#!/bin/bash
# test-f242-groom-gate.sh — the F242 mechanical groom gate (per F242 §
# Success Criteria): the agent cannot record, stamp, or pass audit on a
# punted Next/question. Five cases:
#   (A) `set --status Ready --next "<sentinel>"` is REFUSED at write time
#       (empty / ⚠ / TBD / N/A / none / -), so a punt can't be recorded;
#   (B) a concrete Next ("run the sweep across all anchors") is ACCEPTED;
#   (C) `state triage` REFUSES to stamp when a Ready row's Next was
#       hand-edited to a sentinel past the write gate;
#   (D) audit-q C49 flags a pre-seeded Ready row with a sentinel Next;
#   (E) audit-q C49 flags a [Questions] row whose inline question is a
#       placeholder sentinel.
#
# Uses a throwaway fixture anchor under ~/ob/kmr/Topic/Misc/Test/ (per the
# smoke-tests-live-in-the-vault convention); snapshots + restores Q.md, and
# removes every fixture artifact on exit.
set -u

STATE=~/.claude/skills/workflow/scripts/state
AUDIT=~/.claude/skills/audit/scripts/audit-q.py
FIX_ROOT=~/ob/kmr/Topic/Misc/Test/"F242 Fixture"
TRACK="$FIX_ROOT/F242FIX Track"
BACKLOG="$TRACK/F242FIX Backlog.md"
QMD=~/ob/kmr/Q.md
TMP=$(mktemp -d)
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/triage/F242FIX.json
    [ -f "$TMP/Q.md.bak" ] && cp "$TMP/Q.md.bak" "$QMD"
    rm -rf "$TMP"
}
trap cleanup EXIT
cp "$QMD" "$TMP/Q.md.bak"

mkdir -p "$TRACK"
printf 'slug: F242FIX\ntitle: F242 Fixture\n' > "$FIX_ROOT/.anchor"

ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

fresh_backlog() {
    cat > "$BACKLOG" <<'EOF'
# F242FIX Backlog

## Now

- **T001 — Fixture task** [Questions] — fixture ^T001

## Done
EOF
}

# ---------- Case A — sentinel Next refused at write time ----------
for sentinel in "TBD" "N/A" "none" "-" "⚠"; do
    fresh_backlog
    OUT=$("$STATE" --anchor "$FIX_ROOT" Backlog T001 set --status Ready \
          --next "$sentinel" 2>&1); RC=$?
    if [ "$RC" -ne 0 ] && echo "$OUT" | grep -qi "non-answer"; then
        ok "A[$sentinel]: sentinel Next refused at write (rc=$RC)"
    else
        bad "A[$sentinel]: expected non-answer refusal — rc=$RC, out: $OUT"
    fi
    if grep -q "\[Ready\]" "$BACKLOG"; then
        bad "A[$sentinel]2: refused write must not land"
    fi
done

# ---------- Case B — a concrete Next is accepted ----------
fresh_backlog
OUT=$("$STATE" --anchor "$FIX_ROOT" Backlog T001 set --status Ready --horizon Ready \
      --next "run the sweep across all anchors and diff the output" 2>&1); RC=$?
if [ "$RC" -eq 0 ] && grep -q "\[Ready\]" "$BACKLOG"; then
    ok "B: concrete Next accepted (rc=$RC)"
else
    bad "B: expected accept — rc=$RC, out: $OUT"
fi

# ---------- Case C — triage gate refuses a hand-edited sentinel Next ----------
# Seed a well-formed Ready row, then hand-edit its Next to a sentinel past the
# write gate; `state triage` must refuse and name the non-answer.
cat > "$BACKLOG" <<'EOF'
# F242FIX Backlog

## Ready

- **T003 — Hand-edited past the write gate** [Ready] — seeded ^T003
  - **Next:** TBD

## Done
EOF
OUT=$("$STATE" --anchor "$FIX_ROOT" triage 2>&1); RC=$?
if [ "$RC" -ne 0 ] && echo "$OUT" | grep -qi "non-answer"; then
    ok "C: triage refused the hand-edited sentinel Next (rc=$RC)"
else
    bad "C: expected triage refusal — rc=$RC, out: $OUT"
fi

# ---------- Case D — audit-q C49 flags a seeded sentinel Next ----------
cat > "$BACKLOG" <<'EOF'
# F242FIX Backlog

## Ready

- **T004 — Legacy row minted before the gate** [Ready] — seeded ^T004
  - **Next:** none declared

## Done
EOF
OUT=$(python3 "$AUDIT" --scope backlog --anchor F242FIX --dry 2>&1)
if echo "$OUT" | grep -q "C49"; then
    ok "D: audit-q C49 flagged the seeded sentinel Next"
else
    bad "D: expected a C49 finding — out: $OUT"
fi

# ---------- Case E — audit-q C49 flags a placeholder inline question ----------
cat > "$BACKLOG" <<'EOF'
# F242FIX Backlog

## Now

- **T005 — Question row with a punted inline question** [Questions] — seeded ^T005
  - **Q1 — Which approach** — TBD
    - **(A)** one.
    - **(B)** two.
  - **Recommendation:** None

## Done
EOF
OUT=$(python3 "$AUDIT" --scope backlog --anchor F242FIX --dry 2>&1)
if echo "$OUT" | grep -q "C49"; then
    ok "E: audit-q C49 flagged the placeholder inline question"
else
    bad "E: expected a C49 finding — out: $OUT"
fi

echo "----------------------------------------"
echo "F242 groom-gate test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
