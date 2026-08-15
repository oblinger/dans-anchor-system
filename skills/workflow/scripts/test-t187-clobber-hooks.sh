#!/bin/bash
# test-t187-clobber-hooks.sh — synthetic-payload tests for the two T187
# hooks: read-age-hook.sh (tool:post:Read) and bash-clobber-guard.sh
# (tool:pre:Bash). Every case feeds a hand-built JSON payload on stdin and
# asserts on stdout + exit status; nothing touches the live registry.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
READAGE="$HERE/read-age-hook.sh"
GUARD="$HERE/bash-clobber-guard.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# The hooks scope to $HOME/ob/ by default; tests override scope to $TMP so
# they run hermetically on any machine.
export SYS_READ_AGE_SCOPE="$TMP/"
export SYS_CLOBBER_SCOPE="$TMP/"
export SYS_READ_AGE_THRESHOLD=600
export SYS_CLOBBER_THRESHOLD=600

pass=0 fail=0
ok()  { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }

young="$TMP/young file.md"          # spaces on purpose — vault paths have them
old="$TMP/old file.md"
printf 'young\n' > "$young"
printf 'old\n' > "$old"
# Age the old file well past the threshold.
touch -t "$(date -v-1H '+%Y%m%d%H%M.%S')" "$old"

payload_read() { printf '{"tool_name":"Read","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$1" "$TMP"; }
payload_bash() { python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]},"cwd":sys.argv[2]}))' "$1" "$TMP"; }

# ── read-age-hook ───────────────────────────────────────────────────────────

out=$(payload_read "$young" | "$READAGE"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[read-age]"*"young file.md"*) ok ;; *) bad "read-age: young in-scope file should signal (got: '$out')" ;; esac

out=$(payload_read "$old" | "$READAGE"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "read-age: old file must be silent (got: '$out')"

out=$(payload_read "/etc/hosts" | "$READAGE"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "read-age: out-of-scope file must be silent (got: '$out')"

out=$(payload_read "$TMP/does-not-exist.md" | "$READAGE"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "read-age: missing file must be silent (got: '$out')"

out=$(printf '' | "$READAGE"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "read-age: empty stdin must be silent"

out=$(printf 'not json at all' | "$READAGE"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "read-age: garbage stdin must be silent"

# ── bash-clobber-guard ──────────────────────────────────────────────────────

# cp onto a young target — the T187 incident shape — must warn.
out=$(payload_bash "cp '$TMP/src.py' '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[clobber-guard]"*"young file.md"*) ok ;; *) bad "guard: cp onto young target should warn (got: '$out')" ;; esac

# cp onto an old target — silent.
out=$(payload_bash "cp '$TMP/src.py' '$old'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: cp onto old target must be silent (got: '$out')"

# mv onto a young target — warns.
out=$(payload_bash "mv /tmp/x '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[clobber-guard]"*) ok ;; *) bad "guard: mv onto young target should warn (got: '$out')" ;; esac

# Redirect onto a young target — warns.
out=$(payload_bash "echo hi > '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[clobber-guard]"*) ok ;; *) bad "guard: > onto young target should warn (got: '$out')" ;; esac

# Append redirect — NOT a clobber, silent.
out=$(payload_bash "echo hi >> '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: >> append must be silent (got: '$out')"

# Reading the young file is not overwriting it — silent.
out=$(payload_bash "grep -n foo '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: read-only command must be silent (got: '$out')"

# cp where the young file is the SOURCE, target elsewhere — silent.
out=$(payload_bash "cp '$young' /tmp/elsewhere.md" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: young file as cp SOURCE must be silent (got: '$out')"

# cp onto a directory target — files land inside, not a whole-file clobber; silent.
mkdir -p "$TMP/subdir"
out=$(payload_bash "cp '$TMP/src.py' '$TMP/subdir'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: cp onto directory must be silent (got: '$out')"

# Out-of-scope target — silent.
sysf="$TMP.outside.$$"; printf 'x\n' > "$sysf"
out=$(payload_bash "cp /tmp/x '$sysf'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: out-of-scope young target must be silent (got: '$out')"
rm -f "$sysf"

# Compound command: safe first half, clobber second half — warns.
out=$(payload_bash "ls -la && cp /tmp/x '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[clobber-guard]"*) ok ;; *) bad "guard: clobber after && should warn (got: '$out')" ;; esac

# Relative target resolved against payload cwd — warns.
out=$(payload_bash "cp /tmp/x 'young file.md'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && case "$out" in *"[clobber-guard]"*) ok ;; *) bad "guard: relative target via cwd should warn (got: '$out')" ;; esac

# Unbalanced quotes — heuristic fails open, silent, exit 0.
out=$(payload_bash "echo 'unclosed > '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && ok || bad "guard: unparseable command must still exit 0"

# Fast path: plain command with no cp/mv/> — silent (and cheap).
out=$(payload_bash "git status" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: plain command must be silent (got: '$out')"

# Garbage stdin — silent, exit 0.
out=$(printf 'not json' | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: garbage stdin must be silent"

echo "t187-clobber-hooks: $pass passed, $fail failed"
[ $fail -eq 0 ]
