#!/bin/bash
# read-age-hook.sh — the T187 read-age signal, registered at tool:post:Read
# through the DAS hook registry (TINK F328).
#
# When an agent reads a file that was modified only moments ago, say so: a
# page written 57 seconds ago is an unstable premise — another of the 15+
# live sessions sharing this filesystem may still be mid-edit on it. The
# harness's own read-ledger protects the Write/Edit tools; this signal is
# the read-side half, and it refuses nothing (T187 Q1, resolved (A)
# 2026-08-15: advisory only, so it can stall no one).
#
# THE GUARD IS THE SAFETY PROPERTY (same doctrine as SYS/BRIEF/inject.sh):
# Read is the highest-frequency hook moment in the system, so every path out
# of this script that is not "a shared file with a young mtime" is `exit 0`
# before anything is printed. Scope is $HOME/ob/ — the vault and the linked
# code repos, the surfaces many sessions share. Scratchpads and system paths
# are session-isolated and never signal.
#
# The shebang is #!/bin/bash deliberately, matching hook-run — see its header.

THRESHOLD="${SYS_READ_AGE_THRESHOLD:-600}"   # seconds; younger than this signals
SCOPE="${SYS_READ_AGE_SCOPE:-$HOME/ob/}"     # only files under here signal

input=$(cat)
[ -n "$input" ] || exit 0

target=$(printf '%s' "$input" |
    sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
[ -n "$target" ] || exit 0

case "$target" in
    "$SCOPE"*) ;;
    *) exit 0 ;;
esac

mtime=$(stat -f %m "$target" 2>/dev/null) || exit 0
[ -n "$mtime" ] || exit 0
now=$(date +%s)
age=$((now - mtime))
[ "$age" -ge 0 ] || exit 0
[ "$age" -lt "$THRESHOLD" ] || exit 0

if [ "$age" -lt 120 ]; then
    when="${age}s ago"
else
    when="$((age / 60))m ago"
fi
printf '[read-age] %s was modified %s — possibly by another live session. Treat its content as an unstable premise: re-read before writing anything back that builds on it (T187).\n' \
    "$target" "$when"
exit 0
