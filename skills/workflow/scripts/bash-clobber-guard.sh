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
import json, os, shlex, sys, time

THRESHOLD = int(os.environ.get("SYS_CLOBBER_THRESHOLD", "600"))
SCOPE = os.environ.get("SYS_CLOBBER_SCOPE",
                       os.path.expanduser("~") + "/ob/")

try:
    payload = json.loads(sys.argv[1])
    command = payload.get("tool_input", {}).get("command", "")
    cwd = payload.get("cwd", "") or os.getcwd()
except Exception:
    sys.exit(0)
if not command:
    sys.exit(0)

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
sys.exit(0)
PYEOF
