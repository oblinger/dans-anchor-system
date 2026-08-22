#!/bin/bash
# T588 — `exp exe` must refuse a multi-line command BEFORE contacting any remote.
#
# The defect being guarded: _run.cmd is line 1 nonce, line 2 command, and
# exp-watcher.sh's read loop assigns CMD="$line" once per line — so only the
# LAST line survives. The earlier lines are dropped, the survivor runs, and a
# clean exit writes "Done". Nothing at either end reports the truncation.
#
# Run:  bash test-t588-exp-multiline-refusal.sh

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0

ok() {  # ok <condition-exit-code> <description>
    if [ "$1" -eq 0 ]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL: $2"
    fi
}

# ── Harness ────────────────────────────────────────────────────────────────
# Source the real exp.sh, then replace exactly two things: the config read
# (so no configured remote is needed) and the network primitives (so any
# attempt to reach a remote is recorded rather than performed). Everything
# between them — including the real -r/--remote arg splitting — is the code
# under test.

source "$HERE/exp.sh"

TRIPWIRE="$(mktemp)"
EXP_LOG="$(mktemp)"          # keep the real ~/.config/exp/exp.log untouched

_exp-load-remote() {
    EXP_HOST="test.invalid"
    EXP_PORT="22"
    EXP_LOCAL="$(mktemp -d)"
    EXP_REMOTE_NAME="${1:-t588}"
    return 0
}

# Tripwires. ssh/rsync cover every remote-contacting path; `timeout` is
# overridden too because _exp-ssh-quick runs `timeout 15 ssh …`, and timeout
# execs the binary rather than seeing a shell function.
ssh()     { echo "ssh"     >> "$TRIPWIRE"; return 0; }
rsync()   { echo "rsync"   >> "$TRIPWIRE"; return 0; }
timeout() { shift; "$@"; }

run_exe() {  # run_exe <cmd> ; sets RC, OUT (stdout+stderr)
    : > "$TRIPWIRE"
    OUT="$(exp-exe "$1" 5 -r t588 2>&1)"
    RC=$?
}

echo "T588 — exp exe multi-line refusal"

# ── A. The refusal fires, and fires before any remote is contacted ─────────

MULTI='export FOO=bar
cd gpubench
python run.py'

# NOTE: a bare `RC != 0` proves nothing here — without the guard the call also
# exits non-zero, just later and after contacting the remote. Every refusal
# assertion therefore requires the EMPTY TRIPWIRE as well; that is the half
# that distinguishes "refused" from "tried and failed". Verified by mutation:
# deleting the guard fails 6 of these and leaves a bare RC check passing.
refused() { [ "$RC" -ne 0 ] && [ ! -s "$TRIPWIRE" ]; }

run_exe "$MULTI"
ok "$(refused && echo 0 || echo 1)"                                  "multi-line command is refused, with no remote contacted"
ok "$([ ! -s "$TRIPWIRE" ] && echo 0 || echo 1)"                     "refusal happens BEFORE any ssh/rsync — tripwire is empty"
ok "$(echo "$OUT" | grep -q 'single line' && echo 0 || echo 1)"      "message says the command must be a single line"
ok "$(echo "$OUT" | grep -q 'LAST line' && echo 0 || echo 1)"        "message names the mechanism (only the LAST line survives)"
ok "$(echo "$OUT" | grep -q "report" && echo 0 || echo 1)"           "message says the truncated run would report success"
ok "$(grep -q 'refused-multiline' "$EXP_LOG" && echo 0 || echo 1)"   "the refusal is logged"

# Two lines is enough — the bug does not need three.
run_exe 'cd gpubench
python run.py'
ok "$(refused && echo 0 || echo 1)"                                  "two-line command is refused"
ok "$([ ! -s "$TRIPWIRE" ] && echo 0 || echo 1)"                     "two-line refusal also precedes any remote contact"

# A blank interior line still truncates — the watcher keeps the last line
# regardless of what the dropped ones contained.
run_exe 'echo one

echo two'
ok "$(refused && echo 0 || echo 1)"                                  "command with a blank interior line is refused"

# ── B. The guard does not over-fire ────────────────────────────────────────
# A single-line command must reach the remote-contacting code. This is the
# assertion that would catch a guard written to refuse everything.

run_exe 'cd gpubench && /venv/main/bin/python run.py'
ok "$([ -s "$TRIPWIRE" ] && echo 0 || echo 1)"                       "single-line command PROCEEDS to contact the remote"
ok "$(echo "$OUT" | grep -q 'must be a single line' && echo 1 || echo 0)" "single-line command is not refused"

# printf adds a trailing newline on the wire anyway, so a trailing newline in
# the caller's string is not a second line.
run_exe 'echo hello
'
ok "$([ -s "$TRIPWIRE" ] && echo 0 || echo 1)"                       "trailing newline alone is NOT treated as multi-line"

# Semicolons and && are the sanctioned way to write a compound command.
run_exe 'set -e; cd gpubench; python run.py'
ok "$([ -s "$TRIPWIRE" ] && echo 0 || echo 1)"                       "';'-joined compound command is allowed"

# A newline inside single quotes is still a newline on the wire — the watcher
# reads the file line by line and cannot see the quoting. Refusing is correct.
run_exe "python -c 'print(1)
print(2)'"
ok "$(refused && echo 0 || echo 1)"                                  "newline inside quotes is refused too (the wire cannot see quoting)"

# ── C. The defect the refusal exists for is still in the watcher ───────────
# If someone teaches exp-watcher.sh to accumulate lines, these two assertions
# fail — which is the signal to revisit the refusal rather than leave it
# guarding a bug that no longer exists.

WATCHER="$HERE/exp-watcher.sh"
ok "$(grep -q 'CMD="\$line"' "$WATCHER" && echo 0 || echo 1)"        "exp-watcher.sh still assigns CMD=\$line (last line wins)"
ok "$(grep -q 'CMD="\$CMD' "$WATCHER" && echo 1 || echo 0)"          "exp-watcher.sh does NOT accumulate lines into CMD"

# Reproduce the truncation itself, so the test records the actual behaviour
# rather than only the shape of the source.
FIXTURE="$(mktemp)"
printf 'EXP-1-2\nexport FOO=bar\ncd gpubench\npython run.py\n' > "$FIXTURE"
_nonce=""; _cmd=""; _n=0
while IFS= read -r line; do
    if [ "$_n" -eq 0 ] && [[ "$line" == EXP-* ]]; then _nonce="$line"
    elif [ "$_n" -eq 0 ]; then _cmd="$line"
    else _cmd="$line"
    fi
    _n=$((_n + 1))
done < "$FIXTURE"
ok "$([ "$_cmd" = "python run.py" ] && echo 0 || echo 1)"            "the read loop yields ONLY the last line ('$_cmd')"
ok "$([ "$_nonce" = "EXP-1-2" ] && echo 0 || echo 1)"                "the nonce is still parsed correctly"

rm -f "$TRIPWIRE" "$EXP_LOG" "$FIXTURE"

echo
echo "T588: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
