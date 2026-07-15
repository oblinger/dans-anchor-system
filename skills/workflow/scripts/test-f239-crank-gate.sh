#!/bin/bash
# test-f239-crank-gate.sh — three-case test for the F239 crank exit handshake
# (per F239 § Success Criteria): (A) dirty-gate refusal, (B) clean stamp +
# legal stop, (C) CRANK READY rejected on an empty Ready queue.
#
# Uses a throwaway fixture anchor under ~/ob/kmr/Topic/Misc/Test/ (per the
# smoke-tests-live-in-the-vault convention); snapshots + restores Q.md, and
# removes every fixture artifact on exit.
set -u

STATE=~/.claude/skills/workflow/scripts/state
HOOK=~/.claude/skills/workflow/scripts/crank-stop-hook.py
FIX_ROOT=~/ob/kmr/Topic/Misc/Test/"F239 Fixture"
TRACK="$FIX_ROOT/F239FIX Track"
BACKLOG="$TRACK/F239FIX Backlog.md"
QMD=~/ob/kmr/Q.md
TMP=$(mktemp -d)
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/triage/F239FIX.json \
          ~/.config/anchor-system/crank/F239FIX.json
    [ -f "$TMP/Q.md.bak" ] && cp "$TMP/Q.md.bak" "$QMD"
    rm -rf "$TMP"
}
trap cleanup EXIT
cp "$QMD" "$TMP/Q.md.bak"

mkdir -p "$TRACK"
printf 'slug: F239FIX\ntitle: F239 Fixture\n' > "$FIX_ROOT/.anchor"

ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

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
OUT=$("$STATE" --anchor "$FIX_ROOT" triage 2>&1); RC=$?
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
LINE=$("$STATE" --anchor "$FIX_ROOT" triage 2>"$TMP/errB"); RC=$?
if [ "$RC" -eq 0 ] && printf '%s' "$LINE" | grep -q "^TRIAGE — Ready 1"; then
    ok "B: clean gates stamped, canonical line: $LINE"
else
    bad "B: expected stamp + line — rc=$RC, line: $LINE, err: $(cat "$TMP/errB")"
fi
"$STATE" --anchor "$FIX_ROOT" crank start >/dev/null
transcript "$LINE"
BLOCK=$(hook_run "$TRANSCRIPT")
if [ -z "$BLOCK" ] && [ ! -f ~/.config/anchor-system/crank/F239FIX.json ]; then
    ok "B2: stop allowed on fresh stamp + echoed line; sentinel cleared"
else
    bad "B2: expected allow — hook out: $BLOCK"
fi

# B3 — a post-stamp mutation stales the stamp: same line must now block
"$STATE" --anchor "$FIX_ROOT" crank start >/dev/null
printf -- '- **T003 — Post-stamp mutation** [Questions] — staler ^T003\n' >> "$BACKLOG"
BLOCK=$(hook_run "$TRANSCRIPT")
if echo "$BLOCK" | grep -q '"decision": "block"'; then
    ok "B3: post-stamp mutation stales the stamp — stop blocked"
else
    bad "B3: expected block on stale stamp — hook out: $BLOCK"
fi
"$STATE" --anchor "$FIX_ROOT" crank stop >/dev/null

# ---------- Case C — CRANK READY rejected when nothing is Ready ----------
cat > "$BACKLOG" <<'EOF'
# F239FIX Backlog

## Now

- **T001 — Fixture parked on a question** [Questions] — nothing ready here ^T001

## Done
EOF
"$STATE" --anchor "$FIX_ROOT" crank start >/dev/null
transcript "All parked. CRANK READY"
BLOCK=$(hook_run "$TRANSCRIPT")
if echo "$BLOCK" | grep -q '"decision": "block"'; then
    ok "C: CRANK READY with Ready=0 blocked"
else
    bad "C: expected block — hook out: $BLOCK"
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
"$STATE" --anchor "$FIX_ROOT" crank start >/dev/null
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
