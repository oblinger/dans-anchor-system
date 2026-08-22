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

# ── T577(A): the guard DENIES rather than warning ───────────────────────────
#
# Dan ruled T577 Q1 (A) on 2026-08-21. The guard's output changed shape with
# it: instead of prose on stdout it emits the `permissionDecision: deny`
# envelope — the surface `~/.claude/bash-guard.sh` has blocked `tccutil reset`
# through for months, chosen over a bare `exit 2` because the whole lesson of
# T577 is not to ship a guard down a channel nobody has watched work.
#
# So every assertion below asks about the DECISION, not about a substring of
# prose. `denied` extracts the decision; `reason` extracts the explanation the
# agent actually receives.
denied() { printf '%s' "$1" | python3 -c 'import json,sys
raw=sys.stdin.read().strip()
if not raw: print("allow"); raise SystemExit
try: print(json.loads(raw)["hookSpecificOutput"]["permissionDecision"])
except Exception: print("malformed")'; }
reason() { printf '%s' "$1" | python3 -c 'import json,sys
raw=sys.stdin.read().strip()
if not raw: raise SystemExit
try: print(json.loads(raw)["hookSpecificOutput"]["permissionDecisionReason"])
except Exception: pass'; }

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
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && case "$(reason "$out")" in *"young file.md"*) ok ;; *) bad "guard: cp onto young target should warn (got: '$out')" ;; esac || bad "guard: cp onto young target should warn (got: '$out') (no deny)"

# cp onto an old target — silent.
out=$(payload_bash "cp '$TMP/src.py' '$old'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: cp onto old target must be silent (got: '$out')"

# mv onto a young target — warns.
out=$(payload_bash "mv /tmp/x '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && ok || bad "guard: mv onto young target should warn (got: '$out')"

# Redirect onto a young target — warns.
out=$(payload_bash "echo hi > '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && ok || bad "guard: > onto young target should warn (got: '$out')"

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
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && ok || bad "guard: clobber after && should warn (got: '$out')"

# Relative target resolved against payload cwd — warns.
out=$(payload_bash "cp /tmp/x 'young file.md'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && ok || bad "guard: relative target via cwd should warn (got: '$out')"

# Unbalanced quotes — heuristic fails open, silent, exit 0.
out=$(payload_bash "echo 'unclosed > '$young'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && ok || bad "guard: unparseable command must still exit 0"

# Fast path: plain command with no cp/mv/> — silent (and cheap).
out=$(payload_bash "git status" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: plain command must be silent (got: '$out')"

# Garbage stdin — silent, exit 0.
out=$(printf 'not json' | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: garbage stdin must be silent"

# ── T577: read-provenance, the signal age is a proxy for ────────────────────
#
# THE CASE THIS SECTION EXISTS FOR, measured 2026-08-20. Sonar listed the vault
# root, saw no `CRM/`, spent ~20 MINUTES designing with Dan, then created the
# anchor with `cat > CRM/CRM.md`. Atticus had created and committed the same
# files inside that window. Both were silently replaced — this guard stat'd
# them, found them older than 600s, and said nothing. Sonar: *"a staleness
# check that ran a few minutes ago is not a staleness check."*
#
# No threshold fixes it: the dangerous span is not "written seconds ago" but
# "written while the other agent was thinking", and a design conversation is
# tens of minutes long. So the guard now also asks whether THIS session has
# ever read the target — the compare-and-swap the harness enforces for
# Write/Edit and the Bash path bypasses.

transcript="$TMP/transcript.jsonl"
payload_bash_t() {
    python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]},"cwd":sys.argv[2],"transcript_path":sys.argv[3]}))' \
        "$1" "$TMP" "$2"
}

# A transcript in which this session read something else entirely.
printf '{"tool_name":"Read","tool_input":{"file_path":"%s/unrelated.md"}}\n' "$TMP" > "$transcript"

# Sonar's exact shape: an hour-old file this session has never read.
out=$(payload_bash_t "cp '$young' '$old'" "$transcript" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && case "$(reason "$out")" in *"has not been read by this session"*) ok ;; *) bad "guard: an unread old target must warn — this is the Sonar case (got: '$out')" ;; esac || bad "guard: an unread old target must warn — this is the Sonar case (got: '$out') (no deny)"

# Same file, once the transcript shows this session read it. Quiet: the
# content being written CAN have been derived from what is there, and a guard
# that nags anyway is one that gets muted.
printf '{"tool_name":"Read","tool_input":{"file_path":"%s"}}\n' "$old" >> "$transcript"
out=$(payload_bash_t "cp '$young' '$old'" "$transcript" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: a target this session read must be silent (got: '$out')"

# A bare path mention is NOT a read. The needle is `"file_path":"<path>"`
# deliberately: matching a bare substring would count the agent merely
# discussing the file, which is exactly what Sonar did before clobbering it.
printf '{"tool_name":"Bash","tool_input":{"command":"ls %s"}}\n' "$TMP/mentioned.md" > "$transcript"
printf 'x\n' > "$TMP/mentioned.md"
touch -t "$(date -v-1H '+%Y%m%d%H%M.%S')" "$TMP/mentioned.md"
out=$(payload_bash_t "cp '$young' '$TMP/mentioned.md'" "$transcript" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && case "$(reason "$out")" in *"has not been read by this session"*) ok ;; *) bad "guard: mentioning a path is not reading it (got: '$out')" ;; esac || bad "guard: mentioning a path is not reading it (got: '$out') (no deny)"

# Unknowable is not False. A missing or empty transcript must produce NO
# warning — an absent measurement supports no claim, and a guard that shouts
# out of its own blindness gets muted, which costs more than it saves.
out=$(payload_bash_t "cp '$young' '$old'" "$TMP/no-such-transcript.jsonl" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: an unreadable transcript must not manufacture a warning (got: '$out')"

: > "$TMP/empty.jsonl"
out=$(payload_bash_t "cp '$young' '$old'" "$TMP/empty.jsonl" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: an empty transcript must not warn (mmap of 0 bytes) (got: '$out')"

# A payload with no transcript_path at all — every pre-T577 caller, and every
# case above this section. The guard must behave exactly as it did before.
out=$(payload_bash "cp '$young' '$old'" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: no transcript_path must fall back to pre-T577 behaviour (got: '$out')"

# The age warning still owns the fresh case, and says the age thing rather
# than the provenance thing — two different findings, two different fixes.
out=$(payload_bash_t "cp '$old' '$young'" "$transcript" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ "$(denied "$out")" = deny ] && case "$(reason "$out")" in *"was modified"*"ago"*) ok ;; *) bad "guard: a fresh target must still cite AGE, not provenance (got: '$(reason "$out")')" ;; esac || bad "guard: a fresh target was not denied"

# The two branches must never converge on one message: "modified 30s ago" and
# "has not been read" have DIFFERENT remedies (wait and merge, vs read then
# merge), so a block carrying the wrong one sends the reader to the wrong fix.
# Asserted on the SAME payload as the case above, which is what makes this a
# real check rather than a second look at an empty string — the first cut of
# this case sat before `payload_bash_t` was defined, produced no output, and
# passed vacuously.
case "$(reason "$out")" in
    *"has not been read by this session"*) bad "guard: the AGE branch emitted the PROVENANCE message" ;;
    *"was modified"*) ok ;;
    *) bad "guard: the age branch said neither thing: '$(reason "$out")'" ;;
esac

# Out of scope stays out of scope on the new path too.
printf 'x\n' > "$TMP/../outside.md" 2>/dev/null || true
out=$(payload_bash_t "cp '$young' /etc/hosts" "$transcript" | "$GUARD"); rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok || bad "guard: out-of-scope target must be silent on the provenance path (got: '$out')"

# ── T577(A): the override, and the shape it must refuse ─────────────────────
#
# A blocking guard with no way past it is a trap. The escape is a REASON, not
# an assent: `CLOBBER_OK=1` is what an override degrades into once it becomes
# reflex, so it is rejected and falls through to the deny that tells you what
# to type. The gate never judges whether the sentence is any good — having to
# compose one is the entire filter.
export SYS_CLOBBER_LOG_DIR="$TMP/clobberlog"

out=$(payload_bash_t "CLOBBER_OK=1 cp '$young' '$old'" "$transcript" | "$GUARD")
[ "$(denied "$out")" = deny ] && ok || bad "guard: a bare CLOBBER_OK=1 must not pass"

out=$(payload_bash_t "CLOBBER_OK=true cp '$young' '$old'" "$transcript" | "$GUARD")
[ "$(denied "$out")" = deny ] && ok || bad "guard: CLOBBER_OK=true must not pass"

out=$(payload_bash_t "CLOBBER_OK='generated artefact, rebuilt wholesale every run' cp '$young' '$old'" "$transcript" | "$GUARD")
[ -z "$out" ] && ok || bad "guard: a reasoned CLOBBER_OK must allow (got: '$out')"

# The record is the half that makes a blocking guard reviewable — T577's whole
# finding was that nobody could tell whether the advisory had ever spoken, and
# shipping a BLOCKING version with the same blind spot repeats it at higher
# cost. Blocks and overrides both land, and the override carries its reason.
log="$TMP/clobberlog/refusals.jsonl"
[ -s "$log" ] && ok || bad "guard: nothing was written to the refusal log"
grep -q '"kind": *"block:' "$log" && ok || bad "guard: no block recorded in the log"
grep -q '"kind": *"override:' "$log" && ok || bad "guard: no override recorded in the log"
grep -q 'rebuilt wholesale every run' "$log" && ok || bad "guard: the override reason was not recorded"

# Logging must never be the thing that blocks a command.
SYS_CLOBBER_LOG_DIR=/dev/null/nope \
  out=$(SYS_CLOBBER_LOG_DIR=/dev/null/nope payload_bash_t "cp '$young' '$old'" "$transcript" | "$GUARD")
[ "$(denied "$out")" = deny ] && ok || bad "guard: an unwritable log changed the verdict"

echo "t187-clobber-hooks: $pass passed, $fail failed"
[ $fail -eq 0 ]
