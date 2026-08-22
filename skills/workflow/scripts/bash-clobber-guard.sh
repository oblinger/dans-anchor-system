#!/bin/bash
# bash-clobber-guard.sh — the T187 Bash-path clobber guard, registered at
# tool:pre:Bash through the DAS hook registry (TINK F328).
#
# The harness's read-ledger protects Write/Edit, but a Bash `cp`/`mv`/`>`
# writes a whole file with no staleness check at all — the exact hole the
# T187 incident went through (a scratchpad copy clobbering a newer committed
# file, with a green 14/14 suite vouching for the loss). This guard watches
# only whole-file-overwrite commands whose TARGET is a shared file another
# session touched moments ago, or that this session has never read.
#
# IT BLOCKS. Dan ruled T577 Q1 (A) on 2026-08-21, revising his own T542 Q1
# ruling that it be advisory and never refuse — because T577 measured that
# "advisory" is not a thing this hook moment can be: `PreToolUse`
# `additionalContext` never reaches the agent, so the guard computed correctly
# and spoke to nobody for its entire life. The old note here — *"a registry
# child cannot refuse"* — was true and was the problem, not the justification;
# see the deny block at the bottom for where the guard now lives and why.
#
# Measured before shipping, because a blocking guard across 15+ live sessions
# is not something to estimate: replayed over 10 recent transcripts and 49,677
# real Bash calls, it would have denied **97** — 0.195%, about 1 in 500 — and
# that is an OVER-count, since the replay tests whether the target exists today
# and so counts renames and first-writes that clobbered nothing at the time.
#
# Fast path first: nearly every Bash call contains no cp/mv/redirect, and
# this fires on every one of them across 15+ live sessions — so the raw
# payload is substring-scanned in bash and only matching commands pay the
# python parse. The shebang is #!/bin/bash deliberately, matching hook-run.

input=$(cat)
[ -n "$input" ] || exit 0

# Substring fast path over the raw JSON: if the command mentions none of the
# overwrite forms, the parse can never find one. False positives here (e.g.
# "scp ", a ">" inside prose) just fall through to the real parser.
case "$input" in
    *cp\ *|*mv\ *|*\>*) ;;
    *) exit 0 ;;
esac

exec /usr/bin/env python3 - "$input" <<'PYEOF'
# Parse the payload properly (vault paths contain spaces — naive splitting
# is wrong on this filesystem by construction). Advisory: every exit is 0.
import json, mmap, os, shlex, sys, time
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(os.environ.get(
    "SYS_CLOBBER_LOG_DIR",
    str(Path.home() / ".config" / "anchor-system" / "clobber")))
THRESHOLD = int(os.environ.get("SYS_CLOBBER_THRESHOLD", "600"))
WINDOW = int(os.environ.get("SYS_CLOBBER_WINDOW", str(32 * 1024 * 1024)))
SCOPE = os.environ.get("SYS_CLOBBER_SCOPE",
                       os.path.expanduser("~") + "/ob/")

try:
    payload = json.loads(sys.argv[1])
    command = payload.get("tool_input", {}).get("command", "")
    cwd = payload.get("cwd", "") or os.getcwd()
    transcript = payload.get("transcript_path", "")
except Exception:
    sys.exit(0)
if not command:
    sys.exit(0)


def seen_by_this_session(path, transcript):
    """Has THIS session read `path`? True / False / None when unknowable.

    T577 — why this exists beside the age test. On 2026-08-20 Sonar listed the
    vault root, saw no `CRM/`, spent ~20 MINUTES designing with Dan, then
    created the anchor with `cat > CRM/CRM.md`. Atticus had created and
    committed the same two files inside that window. Both were silently
    replaced; this guard stat'd them, found them older than the 600s threshold,
    and said nothing. Sonar named the failure exactly: *"I had checked the
    directory and it was empty, so I treated a check from several minutes
    earlier as current. A staleness check that ran a few minutes ago is not a
    staleness check."*

    No threshold fixes that, because the dangerous span is not "written seconds
    ago" but "written while the other agent was thinking", and a design
    conversation is tens of minutes long. **Age is a proxy for the question
    that actually matters: have I seen this file's current bytes?** That is the
    compare-and-swap the harness already enforces for `Write`/`Edit` and that
    the Bash path bypasses entirely — so asking it here closes the hole rather
    than moving it.

    Searches for `"file_path":"<path>"`, the shape a Read/Write/Edit tool call
    takes in the transcript, NOT a bare path substring: a bare path also
    matches the agent merely discussing the file, which would suppress the
    warning in precisely Sonar's case. mmap because a long session's transcript
    runs to tens of MB and this must stay cheap.

    Returns None — never False — when the transcript cannot be read. An absent
    measurement supports no claim, and a guard that manufactures a warning out
    of its own blindness gets muted, which costs more than it saves.

    ONLY THE LAST `WINDOW` BYTES ARE SCANNED, and that is a claim rather than a
    shortcut. Measured on a live session 2026-08-21: a 248 MB transcript takes
    **97 ms** to scan end to end, which this cannot spend on every `cp` across
    15 sessions, and which grows without bound as a session runs. Bounding it
    makes the cost O(window) forever. It also sharpens what a False means: not
    *"never read in this session"* but *"not read RECENTLY"* — and a read from
    200 MB of transcript ago is stale knowledge of the file anyway, so warning
    on it is right rather than a concession.
    """
    if not transcript or not os.path.isfile(transcript):
        return None
    try:
        needle = ('"file_path":"' + json.dumps(path)[1:-1] + '"').encode()
        with open(transcript, "rb") as fh:
            size = os.fstat(fh.fileno()).st_size
            if size == 0:
                return None
            start = max(0, size - WINDOW)
            # mmap's offset must be allocation-granularity aligned; round DOWN
            # so the window is never smaller than asked for.
            offset = (start // mmap.ALLOCATIONGRANULARITY) * mmap.ALLOCATIONGRANULARITY
            mm = mmap.mmap(fh.fileno(), size - offset,
                           access=mmap.ACCESS_READ, offset=offset)
            try:
                return mm.find(needle) != -1
            finally:
                mm.close()
    except (OSError, ValueError):
        return None


try:
    tokens = shlex.split(command)
except ValueError:
    sys.exit(0)  # unbalanced quotes — heuristic gives up, fail open

SEPARATORS = {";", "&&", "||", "|", "&"}

# Split the token stream into simple commands, collecting overwrite targets:
# the last path argument of a cp/mv, and any `>`/`&>`/`N>` redirect target
# (`>>` appends — not a clobber).
targets = []
cmd_tokens = []


def flush():
    if not cmd_tokens:
        return
    head = 0
    while head < len(cmd_tokens) and "=" in cmd_tokens[head].split("/")[0]:
        head += 1  # skip leading VAR=val assignments
    if head < len(cmd_tokens):
        prog = os.path.basename(cmd_tokens[head])
        if prog in ("cp", "mv"):
            args = [t for t in cmd_tokens[head + 1:] if not t.startswith("-")]
            if len(args) >= 2:
                targets.append(args[-1])
    cmd_tokens.clear()


expect_redirect_target = False
for tok in tokens:
    if tok in SEPARATORS:
        flush()
        expect_redirect_target = False
        continue
    if expect_redirect_target:
        targets.append(tok)
        expect_redirect_target = False
        continue
    stripped = tok.lstrip("0123456789")
    if stripped in (">", "&>"):
        expect_redirect_target = True
        continue
    if (stripped.startswith((">", "&>")) and not stripped.startswith(">>")
            and stripped not in (">", "&>")):
        rest = stripped.lstrip("&").lstrip(">")
        if rest:
            targets.append(rest)
        continue
    cmd_tokens.append(tok)
flush()

def log_event(kind, path, why=""):
    """Every refusal and every override, on the record.

    T585. This is the half that makes the guard reviewable rather than
    believed. T577's whole finding was that nobody could tell whether an
    advisory had ever spoken; shipping a BLOCKING version with the same blind
    spot would repeat that at higher cost. The log is what a later read
    measures the false-positive rate from — and per T584, a rollout whose
    review has no owner and no trigger sits in its initial mode forever, so
    that read is filed as a dated row rather than left as an intention.
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "kind": kind, "path": path, "cwd": cwd,
               "command": command[:400]}
        if why:
            rec["why"] = why[:300]
        with (LOG_DIR / "refusals.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except OSError:
        pass                      # logging must never be what blocks a command


# THE ESCAPE, and why it is spelled the way it is.
#
# A blocking guard with no way past it is a trap, and the natural way past this
# one is to READ the file — which is the behaviour the guard exists to produce,
# so it needs no flag. What a flag is for is the case where reading is
# genuinely not the answer: a generated artefact, a binary, a file being
# replaced wholesale on purpose.
#
# `CLOBBER_OK` must carry a REASON, and the reason is the entire mechanism.
# Per the structural-gate pattern the gate never judges the justification's
# quality — being made to type why is what kills the reflexive override — and
# the override is logged beside the refusals so it is challengeable later. A
# bare `CLOBBER_OK=1` is refused precisely because it would become reflex.
override = ""
for tok in tokens:
    if tok.startswith("CLOBBER_OK="):
        raw = tok.split("=", 1)[1].strip()
        # A REASON, not an assent. `CLOBBER_OK=1` / `=true` / `=yes` are the
        # shapes an override degrades into once it becomes reflex, so they are
        # rejected and fall through to the deny — where the message says what
        # to type instead. The gate never judges whether the sentence is GOOD;
        # having to compose one is the whole filter.
        if len(raw) >= 12 and raw.lower() not in ("1", "true", "yes", "ok", "y"):
            override = raw
        break

now = time.time()
seen_targets = set()
refusals = []
for t in targets:
    path = os.path.expanduser(t)
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(cwd, path))
    if not path.startswith(SCOPE) or path in seen_targets:
        continue
    # A cp/mv target may be a directory (file lands inside) — the clobber
    # case is an existing FILE target.
    if not os.path.isfile(path):
        continue
    try:
        age = now - os.stat(path).st_mtime
    except OSError:
        continue
    if 0 <= age < THRESHOLD:
        seen_targets.add(path)
        when = f"{int(age)}s" if age < 120 else f"{int(age // 60)}m"
        refusals.append((path, "age",
              f"{path}\n    was modified {when} ago — possibly by another live "
              f"session. If the content you are writing was read or copied "
              f"earlier, re-read the current file and merge rather than "
              f"overwrite (T187: a stale whole-file copy silently reverts newer "
              f"work and its tests keep passing)."))
    elif seen_by_this_session(path, transcript) is False:
        seen_targets.add(path)
        refusals.append((path, "unread",
              f"{path}\n    has not been read by this session. Age says nothing "
              f"here — whatever you are about to write was not derived from "
              f"what is currently in that file, so anything another session put "
              f"there is lost without a diff (T577)."))

if not refusals:
    sys.exit(0)

if override:
    for path, kind, _ in refusals:
        log_event(f"override:{kind}", path, override)
    sys.exit(0)

for path, kind, _ in refusals:
    log_event(f"block:{kind}", path)

# THE DENY, and why it is this shape rather than a non-zero exit.
#
# T577 measured that `PreToolUse` `additionalContext` never reaches the agent —
# which is how this guard computed correctly and said nothing to anyone for its
# whole life. `permissionDecision: deny` on STDOUT is a different surface, and
# it is the one PROVEN live on this machine: `~/.claude/bash-guard.sh` blocks
# `tccutil reset` with exactly this JSON and has been relied on for months. A
# bare `exit 2` is also documented, but it is untested here, and the entire
# lesson of T577 is not to ship a guard down a channel nobody has watched work.
#
# THE OTHER HALF OF (A) IS NOT IN THIS FILE. A registry line cannot deny —
# F328's own contract says so: *"Structured hook-decision JSON from a registry
# child is not interpreted — a hook that needs `permissionDecision` keeps its
# own settings.json entry rather than a registry line."* Both executors
# (Warden's `run_registry`, and `hook-run`, which exits 0 unconditionally so a
# broken hook cannot suppress a session) fold a child's stdout onto the
# `additionalContext` surface and discard its status. So this guard was moved
# OUT of the registry and given its own `settings.json` PreToolUse/Bash entry
# in the same change. Putting the line back in the registry silently restores
# the mute version.
body = "\n\n".join(msg for _, _, msg in refusals)
reason = (
    "BLOCKED by clobber-guard — this command overwrites a shared file "
    "without having seen its current contents.\n\n" + body + "\n\n"
    "Do one of these:\n"
    "  * Read the file, then merge your changes into it. This is almost always "
    "the right answer, and it clears the guard as a side effect.\n"
    "  * Mutate it through its owning script, or with Edit — both are already "
    "staleness-checked by the harness.\n"
    "  * If a whole-file overwrite really is correct (a generated artefact, a "
    "binary, a deliberate wholesale replace), say why and retry:\n"
    "      CLOBBER_OK=\"<one line: why reading it first is not the answer>\" "
    "<your command>\n"
    "    The reason is recorded and reviewable; a bare CLOBBER_OK=1 is refused.")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": reason}}))
sys.exit(0)
PYEOF
