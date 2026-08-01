#!/bin/bash
# test-f240-verify-gate.sh — four-case test for the F240 verification
# ownership gate (per F240 § Success Criteria): (A) missing --why-user
# refused, (B) mechanical phrasing refused even with --why-user, (C) genuine
# taste check with --why-user passes and the annotation lands in the row,
# (D) audit-q C47 flags a pre-seeded mechanical [Verify] row. Plus (E):
# a same-family re-touch of an existing [Verify] row is grandfathered.
#
# Uses a throwaway fixture anchor under ~/ob/kmr/Topic/Misc/Test/ (per the
# smoke-tests-live-in-the-vault convention); snapshots + restores Q.md, and
# removes every fixture artifact on exit.
set -u

STATE=~/.claude/skills/workflow/scripts/state
AUDIT=~/.claude/skills/audit/scripts/audit-q.py
FIX_ROOT=~/ob/kmr/Topic/Misc/Test/"F240 Fixture"
TRACK="$FIX_ROOT/F240FIX Track"
BACKLOG="$TRACK/F240FIX Backlog.md"
QMD=~/ob/kmr/Q.md
TMP=$(mktemp -d)
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/triage/F240FIX.json
    [ -f "$TMP/Q.md.bak" ] && cp "$TMP/Q.md.bak" "$QMD"
    rm -rf "$TMP"
}
trap cleanup EXIT
cp "$QMD" "$TMP/Q.md.bak"

mkdir -p "$TRACK"
printf 'slug: F240FIX\ntitle: F240 Fixture\n' > "$FIX_ROOT/.anchor"

ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

fresh_backlog() {
    cat > "$BACKLOG" <<'EOF'
# F240FIX Backlog

## Now

- **T001 — Fixture task heading to Verify** [Ready] — fixture ^T001
  - **Next:** run the fixture step end-to-end with zero user involvement

## Done
EOF
}

# ---------- Case A — missing --why-user refused ----------
fresh_backlog
OUT=$("$STATE" set "$FIX_ROOT" Backlog T001 --status Verify \
      --verify "do the groupings read right to you?" 2>&1); RC=$?
if [ "$RC" -ne 0 ] && echo "$OUT" | grep -q -- "--why-user"; then
    ok "A: missing --why-user refused (rc=$RC)"
else
    bad "A: expected why-user refusal — rc=$RC, out: $OUT"
fi
if grep -q "\[Verify\]" "$BACKLOG"; then
    bad "A2: refused write must not land"
else
    ok "A2: backlog unchanged on refusal"
fi

# ---------- Case B — mechanical phrasing refused even WITH --why-user ----------
fresh_backlog
OUT=$("$STATE" set "$FIX_ROOT" Backlog T001 --status Verify \
      --verify "did the render pass on the fixture anchor?" \
      --why-user "I want to see it myself" 2>&1); RC=$?
if [ "$RC" -ne 0 ] && echo "$OUT" | grep -qi "machine event"; then
    ok "B: mechanical phrasing refused despite --why-user (rc=$RC)"
else
    bad "B: expected mechanical refusal — rc=$RC, out: $OUT"
fi

# ---------- Case C — genuine taste check passes; annotation lands ----------
fresh_backlog
OUT=$("$STATE" set "$FIX_ROOT" Backlog T001 --status Verify --horizon Verify \
      --verify "does the fixture layout feel right in daily use?" \
      --why-user "taste call on the layout" 2>&1); RC=$?
if [ "$RC" -eq 0 ] && grep -q "\[Verify\]" "$BACKLOG"; then
    ok "C: taste check with --why-user accepted (rc=$RC)"
else
    bad "C: expected accept — rc=$RC, out: $OUT"
fi
if grep -q "· \*why-user: taste call on the layout\*" "$BACKLOG"; then
    ok "C2: why-user annotation landed on the Verify sub-bullet"
else
    bad "C2: annotation missing — row: $(grep -A1 T001 "$BACKLOG")"
fi

# ---------- Case E — same-family re-touch grandfathered (no --why-user) ----------
OUT=$("$STATE" set "$FIX_ROOT" Backlog T001 --horizon Later 2>&1); RC=$?
if [ "$RC" -eq 0 ]; then
    ok "E: horizon move of an existing [Verify] row needs no --why-user"
else
    bad "E: expected grandfathered accept — rc=$RC, out: $OUT"
fi

# ---------- Case D — audit-q C47 fires on a pre-seeded mechanical row ----------
cat > "$BACKLOG" <<'EOF'
# F240FIX Backlog

## Verify

- **T002 — Legacy row minted before the gate** [Verify] — seeded by hand ^T002
  - **Verify:** did the migration script run on every anchor?

## Done
EOF
OUT=$(python3 "$AUDIT" --scope backlog --anchor F240FIX --dry 2>&1); RC=$?
if echo "$OUT" | grep -q "C47"; then
    ok "D: audit-q C47 flagged the seeded mechanical [Verify] row"
else
    bad "D: expected a C47 finding — rc=$RC, out: $OUT"
fi

echo "----------------------------------------"
echo "F240 verify-gate test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
