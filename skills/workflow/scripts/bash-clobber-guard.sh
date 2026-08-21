#!/bin/bash
# bash-clobber-guard.sh — the T187 Bash-path clobber guard, registered at
# tool:pre:Bash through the DAS hook registry (TINK F328).
#
# The harness's read-ledger protects Write/Edit, but a Bash `cp`/`mv`/`>`
# writes a whole file with no staleness check at all — the exact hole the
# T187 incident went through (a scratchpad copy clobbering a newer committed
# file, with a green 14/14 suite vouching for the loss). This guard watches
# only whole-file-overwrite commands whose TARGET is a shared file another
# session touched moments ago, and it is advisory by design (T187 Q1,
# resolved (A) 2026-08-15): a registry child cannot refuse, and a refusing
# version would stall sessions that cannot see why.
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

now = time.time()
warned = set()
for t in targets:
    path = os.path.expanduser(t)
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(cwd, path))
    if not path.startswith(SCOPE) or path in warned:
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
        warned.add(path)
        when = f"{int(age)}s" if age < 120 else f"{int(age // 60)}m"
        print(f"⚠ [clobber-guard] this command overwrites {path}, which was "
              f"modified {when} ago — possibly by another live session. If "
              f"the content you are writing was read or copied earlier, "
              f"re-read the current file and merge rather than overwrite "
              f"(T187: a stale whole-file copy silently reverts newer work "
              f"and its tests keep passing).")
    elif seen_by_this_session(path, transcript) is False:
        warned.add(path)
        print(f"⚠ [clobber-guard] this command overwrites {path}, and this "
              f"session has never read it. Age says nothing here — whatever "
              f"you are about to write was not derived from what is currently "
              f"in that file, so anything another session put there is lost "
              f"without a diff. Read it first, then merge (T577).")
sys.exit(0)
PYEOF
