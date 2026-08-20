#!/bin/bash
# test-f239-crank-gate.sh — three-case test for the F239 crank exit handshake
# (per F239 § Success Criteria): (A) dirty-gate refusal, (B) clean stamp +
# legal stop, (C) CRANK READY rejected on an empty Ready queue.
#
# F269 — the fixture anchor lives in a THROWAWAY VAULT under $TMP, not in the
# real one. `ANCHOR_VAULT_ROOT` points `state` / `backlog-edit.py` /
# `queries-render.py` at it, so the render splices its section into $TMP/Q.md
# and cannot reach the live file. The old shape rendered F239FIX into the REAL
# ~/ob/kmr/Q.md and `cp`-restored a snapshot on exit, which left an orphan
# section on any path that skipped the trap and could revert a concurrent
# agent's Q.md writes.
set -u

STATE=~/.claude/skills/workflow/scripts/state
HOOK=~/.claude/skills/workflow/scripts/crank-stop-hook.py
TMP=$(mktemp -d)
export ANCHOR_VAULT_ROOT="$TMP/vault"
mkdir -p "$ANCHOR_VAULT_ROOT/Topic/Misc/Test"
printf '# Q\n' > "$ANCHOR_VAULT_ROOT/Q.md"
FIX_ROOT="$ANCHOR_VAULT_ROOT/Topic/Misc/Test/F239 Fixture"
TRACK="$FIX_ROOT/F239FIX Track"
BACKLOG="$TRACK/F239FIX Backlog.md"
QMD="$ANCHOR_VAULT_ROOT/Q.md"
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/triage/F239FIX.json \
          ~/.config/anchor-system/crank/F239FIX.json
    # F269 — nothing to restore: the Q.md this test renders into
    # is inside $TMP and goes away with it.
    rm -rf "$TMP"
}
trap cleanup EXIT

mkdir -p "$TRACK"
printf 'slug: F239FIX\ntitle: F239 Fixture\n' > "$FIX_ROOT/.anchor"

ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# fixture_doc [row-id] [doc-basename] — mint the doc a parked row points at.
# Post-F329 a [Questions] row is groomed by POINTING at its question, not by
# carrying it: an inline `- **Q<n>` sub-bullet is a C57 finding and the worklist
# counts findings (F258), so a row that hosts its own question is not groomed.
fixture_doc() {
    local rid="${1:-T001}"
    local base="${2:-F239FIX001 - Fixture parked on a question}"
    cat > "$TRACK/$base.md" <<EOF
---
description: Fixture doc hosting the parked question for the F239 crank-gate test.
---

# [[F239FIX]] · $rid — ${base#* - }
A fixture row parked on a question the user must answer.

## Open Items

- **Q1 — Which approach?** — pick one. ^$rid-Q1
  - **(A)** one.
  - **(B)** two.
- **Recommendation:** None

## Status

**Questions** — parked on Q1.
EOF
}

hook_run() {  # $1 = transcript path → hook stdout; hook rc in $HOOK_RC
    python3 - "$FIX_ROOT" "$1" <<'PY' | python3 "$HOOK"
import json, sys
print(json.dumps({"cwd": sys.argv[1], "transcript_path": sys.argv[2],
                  "stop_hook_active": False, "hook_event_name": "Stop"}))
PY
    HOOK_RC=$?
}

transcript() {  # $1 = final assistant text → path in $TRANSCRIPT
    TRANSCRIPT="$TMP/transcript.jsonl"
    python3 - "$1" > "$TRANSCRIPT" <<'PY'
import json, sys
print(json.dumps({"type": "user", "message": {"content": [
    {"type": "text", "text": "'"}]}}))
print(json.dumps({"type": "assistant", "message": {"content": [
    {"type": "text", "text": "Work done.\n\n" + sys.argv[1]}]}}))
PY
}

# ---------- Case A — dirty gates refuse, refusal is the worklist ----------
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

- **T001 — Fixture task with no next step** [Ready] — dirty on purpose ^T001
- **T002 — Fixture task with event-gated next** [Ready] — dirty on purpose ^T002
  - **Next:** re-run when the pile grows past ten items

## Done
EOF
OUT=$("$STATE" triage "$FIX_ROOT" 2>&1); RC=$?
if [ "$RC" -ne 0 ] \
   && echo "$OUT" | grep -q "not actually executable" \
   && echo "$OUT" | grep -q "event-gated"; then
    ok "A: dirty gate refused (rc=$RC, both findings printed)"
else
    bad "A: expected refusal with both findings — rc=$RC, out: $OUT"
fi
if [ -f ~/.config/anchor-system/triage/F239FIX.json ]; then
    bad "A2: refusal must not stamp"
else
    ok "A2: no stamp written on refusal"
fi

# ---------- Case B — clean gates stamp; stamp+line is a legal stop ----------
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

- **T001 — Fixture task, genuinely executable** [Ready] — clean fixture ^T001
  - **Next:** run the fixture step end-to-end with zero user involvement

## Done
EOF
LINE=$("$STATE" triage "$FIX_ROOT" 2>"$TMP/errB"); RC=$?
if [ "$RC" -eq 0 ] && printf '%s' "$LINE" | grep -q "^TRIAGE — Ready 1"; then
    ok "B: clean gates stamped, canonical line: $LINE"
else
    bad "B: expected stamp + line — rc=$RC, line: $LINE, err: $(cat "$TMP/errB")"
fi
"$STATE" crank "$FIX_ROOT" start >/dev/null
transcript "$LINE"
BLOCK=$(hook_run "$TRANSCRIPT")
if [ -z "$BLOCK" ] && [ ! -f ~/.config/anchor-system/crank/F239FIX.json ]; then
    ok "B2: stop allowed on fresh stamp + echoed line; sentinel cleared"
else
    bad "B2: expected allow — hook out: $BLOCK"
fi

# B3 — adding a groomed [Questions] row keeps the worklist empty → still ALLOW.
# (F244 superseded F239's stamp-freshness ceremony: worklist-empty is the gate;
# a [Questions] row is a groomed state, not a worklist item.)
"$STATE" crank "$FIX_ROOT" start >/dev/null
# A GENUINELY groomed [Questions] row points at the doc that holds its question
# (post-F258 the worklist counts audit-q findings, so a target-less [Questions]
# row is NOT groomed — and post-F329 an INLINE Q is itself one of those findings).
fixture_doc T003 "F239FIX003 - Parked, groomed"
{
  printf -- '- **T003 — Parked, groomed** [Questions] — → [[F239FIX003 - Parked, groomed|T003]] — a groomed row ^T003\n'
  printf -- '  - **User:** Which approach — the fork and the record are in the doc.\n'
} >> "$BACKLOG"
# Plain tail, NOT the canonical TRIAGE line: B2's transcript would let this stop
# through the stamp+echo handshake no matter what the worklist held, so reusing
# it left the assertion untested. This makes worklist-emptiness the only thing
# that can allow the stop.
transcript "Work done."
BLOCK=$(hook_run "$TRANSCRIPT")
if echo "$BLOCK" | grep -q '"decision": "block"'; then
    bad "B3: a groomed [Questions] row must not block (worklist stays empty) — hook out: $BLOCK"
else
    ok "B3: groomed [Questions] row keeps the worklist empty — stop allowed (F244)"
fi
"$STATE" crank "$FIX_ROOT" stop >/dev/null

# ---------- Case C — an all-parked [Questions] frontier is groomed → ALLOW ----------
# (F244: no CRANK-READY ceremony — a fully groomed frontier, even all-parked, is
# a legal stop; the user can answer the parked question.)
#
# The row points at a doc and the question lives there — post-F329 that IS what
# groomed means, and an inline `- **Q<n>` on the row is a C57 finding, which the
# worklist counts (F258). The pre-F329 fixture shape made this case fail while
# looking like a gate bug; it was the fixture that had gone stale.
fixture_doc  # T001's doc, holding the question the row points at
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

- **T001 — Fixture parked on a question** [Questions] — → [[F239FIX001 - Fixture parked on a question|T001]] — groomed, nothing ready ^T001
  - **User:** Which approach — the fork and the record are in the doc.

## Done
EOF
"$STATE" crank "$FIX_ROOT" start >/dev/null
transcript "All parked and groomed."
BLOCK=$(hook_run "$TRANSCRIPT")
if echo "$BLOCK" | grep -q '"decision": "block"'; then
    bad "C: an all-parked groomed frontier must allow the stop — hook out: $BLOCK"
else
    ok "C: all-parked [Questions] frontier is groomed — stop allowed (F244, no ceremony)"
fi

# C2 — with a genuine [Ready] row, the same CRANK READY tail is a legal stop
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

- **T001 — Fixture task, genuinely executable** [Ready] — clean fixture ^T001
  - **Next:** run the fixture step end-to-end with zero user involvement

## Done
EOF
BLOCK=$(hook_run "$TRANSCRIPT")
if [ -z "$BLOCK" ] && [ ! -f ~/.config/anchor-system/crank/F239FIX.json ]; then
    ok "C2: CRANK READY with Ready=1 allowed; sentinel cleared"
else
    bad "C2: expected allow — hook out: $BLOCK"
fi

# C3 — empty frontier is a legal stop with no ritual (state 1)
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

## Done

- **T001 — All done** [Done] — nothing pending ^T001
EOF
"$STATE" crank "$FIX_ROOT" start >/dev/null
transcript "Everything landed."
BLOCK=$(hook_run "$TRANSCRIPT")
if [ -z "$BLOCK" ] && [ ! -f ~/.config/anchor-system/crank/F239FIX.json ]; then
    ok "C3: empty frontier allowed with no token; sentinel cleared"
else
    bad "C3: expected allow — hook out: $BLOCK"
fi

echo "----------------------------------------"
echo "F239 crank-gate test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
