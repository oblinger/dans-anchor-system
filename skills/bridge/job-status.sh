#!/bin/bash
# Remote-side reporter for `bridge jobs` (ATT F054). Emits one machine-readable
# line per job; the local side turns it into verdicts.
#
#   name|status|start|end|log_mtime|cpu_seconds|procs|now
#
# cpu_seconds is summed across the job's whole PROCESS GROUP, because the
# process the wrapper can name is rarely the process doing the work -- see
# job-wrapper.sh for why a single pid reads zero on a healthy job.
#
# This script decides NOTHING. It reports raw counters and lets the caller
# compare them against its own previous sample, because a stall is a statement
# about change over time and a single reading cannot express one. A remote-side
# verdict would also have to guess the check interval, which only the caller
# knows.
set -u
DIR="$HOME/.bridge-jobs"
[ -d "$DIR" ] || exit 0
NOW=$(date +%s)

for meta in "$DIR"/*.meta; do
  [ -e "$meta" ] || continue
  name=$(basename "$meta" .meta)
  status=$(head -1 "$DIR/$name.status" 2>/dev/null || echo "NOSTATUS")
  start=$(sed -n 's/^start=//p' "$meta" | head -1)
  end=$(sed -n 's/^end=//p' "$meta" | head -1)
  log="$DIR/$name.log"
  lmt=0
  # `stat -f %m` is BSD-only. On GNU coreutils `-f` means *filesystem* status and
  # takes no format, so `%m` is read as a FILENAME and the real file still gets
  # stat'd -- successfully, exit 0, printing the multi-line default block that
  # opens `File: "..."`. The caller then fed `File:` into $(( )) and died with
  # `File: unbound variable`, on a Linux rig, from a line that reads fine.
  # Both spellings are tried and the answer is required to be digits.
  if [ -f "$log" ]; then
    lmt=$(stat -c %Y "$log" 2>/dev/null || stat -f %m "$log" 2>/dev/null || echo 0)
    case "$lmt" in (*[!0-9]*|'') lmt=0 ;; esac
  fi

  cpu=0; procs=0
  pgid=$(cat "$DIR/$name.pgid" 2>/dev/null || echo "")
  if [ -n "$pgid" ]; then
    # ps TIME is [dd-]hh:mm:ss or mm:ss -- normalise to seconds.
    read -r cpu procs <<EOF
$(ps -axo pgid=,time= 2>/dev/null | awk -v g="$pgid" '
  $1 == g {
    t = $2; d = 0
    if (index(t, "-")) { split(t, a, "-"); d = a[1]; t = a[2] }
    n = split(t, p, ":")
    s = (n == 3) ? p[1]*3600 + p[2]*60 + p[3] : p[1]*60 + p[2]
    tot += s + d*86400; c++
  }
  END { printf "%d %d", tot + 0, c + 0 }')
EOF
  fi
  printf '%s|%s|%s|%s|%s|%s|%s|%s\n' \
    "$name" "$status" "${start:-0}" "${end:-}" "$lmt" "$cpu" "$procs" "$NOW"
done
