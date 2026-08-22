#!/bin/bash
# T589 — exp-watcher.sh must not call `setsid` unguarded.
#
# `setsid` is util-linux: absent on macOS entirely and on minimal containers.
# Called unguarded, every command on such a host returns `setsid: command not
# found` and exit 127, and the watcher reports that as the COMMAND's exit
# code — so the experiment takes the blame for the watcher.
#
# Run:  bash test-t589-exp-watcher-pgroup.sh

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WATCHER="$HERE/exp-watcher.sh"
PASS=0
FAIL=0

ok() {
    if [ "$1" -eq 0 ]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL: $2"
    fi
}

echo "T589 — exp-watcher.sh process-group guard"

# ── A. The premise, stated rather than assumed ─────────────────────────────
# Every claim below about the fallback only matters if `setsid` can actually
# be missing. On macOS it is. On a Linux box with util-linux this section
# reports the other branch and the behavioural tests still run, because they
# exercise `set -m` directly rather than whatever this host happens to have.

if command -v setsid >/dev/null 2>&1; then
    echo "  (this host HAS setsid — testing the fallback branch directly)"
    HOST_HAS_SETSID=1
else
    echo "  (this host has NO setsid — the exact condition the guard exists for)"
    HOST_HAS_SETSID=0
    setsid true 2>/dev/null
    ok "$([ $? -ne 0 ] && echo 0 || echo 1)"  "bare \`setsid\` fails on this host (the defect's precondition)"
fi

# ── B. The real file is guarded ────────────────────────────────────────────

ok "$(grep -q 'command -v setsid' "$WATCHER" && echo 0 || echo 1)"           "exp-watcher.sh probes for setsid before using it"
ok "$(grep -q 'set -m' "$WATCHER" && echo 0 || echo 1)"                      "exp-watcher.sh carries the set -m fallback"
ok "$(grep -q 'EXP_PGROUP_MODE' "$WATCHER" && echo 0 || echo 1)"             "the chosen mechanism is named in a variable, decided once"
ok "$(grep -q 'process groups via' "$WATCHER" && echo 0 || echo 1)"          "the choice is ANNOUNCED at startup, not made silently"

# No unguarded call: every line that runs setsid must sit under the probe.
UNGUARDED="$(awk '
    /^[[:space:]]*setsid /  { if (prev !~ /EXP_PGROUP_MODE/) printf "%d ", NR }
                            { prev = $0 }
' "$WATCHER")"
ok "$([ -z "$UNGUARDED" ] && echo 0 || echo 1)"                              "no unguarded \`setsid\` call remains (lines: ${UNGUARDED:-none})"

# ── C. The fallback actually does what setsid did ──────────────────────────
# The only property the surrounding `kill -- -$CMD_PID` needs is that the
# child leads its own process group. Prove it, and prove `set -m` is not a
# no-op by showing the same launch WITHOUT it shares the parent's group.

PROBE="$(mktemp)"
cat > "$PROBE" <<'PROBE_EOF'
self_pgid() { ps -o pgid= -p "$1" 2>/dev/null | tr -d ' '; }
MY_PGID="$(self_pgid $$)"

# with job control — the branch exp-watcher.sh takes when setsid is missing
set -m
bash -c 'sleep 30' &
WITH=$!
set +m
sleep 0.3
echo "WITH=$WITH WITH_PGID=$(self_pgid $WITH) MY_PGID=$MY_PGID"

# without job control — the control
bash -c 'sleep 30' &
WITHOUT=$!
sleep 0.3
echo "WITHOUT=$WITHOUT WITHOUT_PGID=$(self_pgid $WITHOUT)"

# the property that matters: killing the GROUP reaches it
kill -- -"$WITH" 2>/dev/null
sleep 0.5
if kill -0 "$WITH" 2>/dev/null; then echo "GROUPKILL=missed"; else echo "GROUPKILL=hit"; fi
kill "$WITHOUT" 2>/dev/null
echo "PARENT=alive"
PROBE_EOF

OUT="$(bash "$PROBE" 2>&1)"
WITH_PID="$(echo "$OUT"  | sed -n 's/.*WITH=\([0-9]*\) .*/\1/p')"
WITH_PGID="$(echo "$OUT" | sed -n 's/.*WITH_PGID=\([0-9]*\).*/\1/p')"
MY_PGID="$(echo "$OUT"   | sed -n 's/.*MY_PGID=\([0-9]*\).*/\1/p')"
WO_PID="$(echo "$OUT"    | sed -n 's/.*WITHOUT=\([0-9]*\) .*/\1/p')"
WO_PGID="$(echo "$OUT"   | sed -n 's/.*WITHOUT_PGID=\([0-9]*\).*/\1/p')"

ok "$([ -n "$WITH_PGID" ] && [ "$WITH_PGID" = "$WITH_PID" ] && echo 0 || echo 1)"    "with set -m the child LEADS its own group (pgid $WITH_PGID == pid $WITH_PID)"
ok "$([ -n "$MY_PGID" ] && [ "$WITH_PGID" != "$MY_PGID" ] && echo 0 || echo 1)"      "that group is not the watcher's ($WITH_PGID != $MY_PGID)"
ok "$([ -n "$WO_PGID" ] && [ "$WO_PGID" = "$MY_PGID" ] && echo 0 || echo 1)"         "CONTROL: without set -m the child shares the parent's group — so set -m is not a no-op"
ok "$([ -n "$WO_PID" ] && [ "$WO_PGID" != "$WO_PID" ] && echo 0 || echo 1)"          "CONTROL: without set -m the child does not lead a group"
ok "$(echo "$OUT" | grep -q 'GROUPKILL=hit' && echo 0 || echo 1)"                    "\`kill -- -PID\` reaches the group the fallback created"
ok "$(echo "$OUT" | grep -q 'PARENT=alive' && echo 0 || echo 1)"                     "the group kill did NOT take the parent with it"

rm -f "$PROBE"

# ── D. End to end: the real watcher runs a command and writes _done ────────
# Run the shipped file with WATCH_DIR repointed at a scratch dir. On macOS
# this exercises the set -m branch, which is the branch the guard added.

SANDBOX="$(mktemp -d)"
RUNNER="$SANDBOX/watcher.sh"
sed "s#^WATCH_DIR=.*#WATCH_DIR=\"$SANDBOX\"#" "$WATCHER" > "$RUNNER"
ok "$(grep -q "WATCH_DIR=\"$SANDBOX\"" "$RUNNER" && echo 0 || echo 1)"               "sandbox watcher was repointed (WATCH_DIR is a single top-level assignment)"

bash "$RUNNER" > "$SANDBOX/out.log" 2>&1 &
WATCHER_PID=$!
sleep 1

ok "$(grep -q 'process groups via' "$SANDBOX/out.log" && echo 0 || echo 1)"          "the running watcher announces its process-group mechanism"
if [ "$HOST_HAS_SETSID" -eq 0 ]; then
    ok "$(grep -q 'process groups via: set -m' "$SANDBOX/out.log" && echo 0 || echo 1)" "on a host without setsid it announces the fallback"
fi

printf 'EXP-t589-1\ntouch %s/ran.marker\n' "$SANDBOX" > "$SANDBOX/_run.cmd.tmp"
mv "$SANDBOX/_run.cmd.tmp" "$SANDBOX/_run.cmd"

for _ in $(seq 1 60); do [ -f "$SANDBOX/_done" ] && break; sleep 0.25; done

ok "$([ -f "$SANDBOX/_done" ] && echo 0 || echo 1)"                                  "the watcher completed the command and wrote _done"
ok "$([ -f "$SANDBOX/ran.marker" ] && echo 0 || echo 1)"                             "the command ACTUALLY RAN (its side effect exists)"
ok "$([ "$(cat "$SANDBOX/_done" 2>/dev/null)" = "EXP-t589-1 0" ] && echo 0 || echo 1)" "_done carries the nonce and exit 0, not 127 (got: $(cat "$SANDBOX/_done" 2>/dev/null))"
ok "$(kill -0 "$WATCHER_PID" 2>/dev/null && echo 0 || echo 1)"                       "the watcher survived running the command"

kill "$WATCHER_PID" 2>/dev/null
wait "$WATCHER_PID" 2>/dev/null
rm -rf "$SANDBOX"

echo
echo "T589: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
