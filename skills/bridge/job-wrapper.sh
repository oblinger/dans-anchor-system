#!/bin/bash
# Remote-side wrapper for `bridge run` (ATT F054). Copied to the remote and
# launched detached inside the bridge tmux session.
#
#   $1  job name        $2  path to the user script on the remote
#
# Everything it writes lives under ~/.bridge-jobs/<name>.* and every field is
# read back by `bridge jobs`:
#
#   .log     the job's own stdout+stderr. Its MTIME is one liveness signal.
#   .pgid    the PROCESS GROUP of the job. `bridge jobs` sums accumulated CPU
#            across every process in it; that is the other liveness signal, and
#            the one that separates "silent but working" from "wedged". A wedged
#            USB read accrues no CPU at all -- measured 2026-08-09, 105 minutes
#            of zero -- while `unzip -tq` on a 157 GB archive printed nothing
#            for 16 minutes and burned CPU the whole way.
#   .status  RUNNING while alive, then `DONE rc=<n>` or `FAILED rc=<n>`.
#            Written by a trap so it is set even when the wrapper is killed -- a
#            job that vanishes without a status is GONE, a distinct and
#            reportable state rather than a silent absence.
#   .meta    start epoch + the command, so a check can report age without
#            asking the agent to remember when anything started.
#
# WHY A PROCESS GROUP AND NOT A PID. Two traps, both of which produce an
# instrument that reads zero for a perfectly healthy job:
#   - `caffeinate -dims bash script &` makes `$!` the pid of CAFFEINATE, which
#     does nothing but hold an assertion and therefore burns no CPU, ever.
#   - even tracking `bash script` is wrong once the script spawns the real work:
#     a shell waiting on `unzip` accrues no CPU either, and macOS does not roll a
#     child's time into `ps -o time` until the child is reaped.
# So `set -m` puts the job in its own process group and the check sums the group.
# Descendants at any depth are covered, which is what "is this job executing?"
# actually means.
#
# There is deliberately NO ticker touching a heartbeat file. A ticker proves the
# ticker is alive and nothing else; the point of F054 is that liveness is derived
# from the job itself.
set -u

NAME="${1:?job name required}"
SCRIPT="${2:?script path required}"
DIR="$HOME/.bridge-jobs"
mkdir -p "$DIR"

LOG="$DIR/$NAME.log"
PGIDF="$DIR/$NAME.pgid"
STATUS="$DIR/$NAME.status"
META="$DIR/$NAME.meta"

printf 'start=%s\ncmd=%s\n' "$(date +%s)" "$SCRIPT" > "$META"
printf 'RUNNING\n' > "$STATUS"

finish() {
  local rc="$1"
  if [ "$rc" = 0 ]; then printf 'DONE rc=0\n' > "$STATUS"
  else printf 'FAILED rc=%s\n' "$rc" > "$STATUS"; fi
  printf 'end=%s\n' "$(date +%s)" >> "$META"
}
# Killed-before-exit still leaves a verdict rather than an ambiguous silence.
trap 'finish 130' INT TERM

# Hold the machine and its disks awake for the WHOLE job, including the parts
# that look like nothing. On 2026-08-09 the assertion covered only the expensive
# command; the disk slept during the idle wait before it and the next stat
# blocked for 105 minutes. `-w $$` ties the assertion to this wrapper's life, so
# it cannot outlive the job or be forgotten.
caffeinate -dims -w $$ &

set -m                      # give the job its own process group
bash "$SCRIPT" > "$LOG" 2>&1 &
JOB=$!
set +m
printf '%s\n' "$JOB" > "$PGIDF"    # with `set -m`, pgid == the job's pid

wait "$JOB"
finish "$?"
