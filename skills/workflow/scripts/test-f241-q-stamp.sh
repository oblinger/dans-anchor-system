#!/bin/bash
# test-f241-q-stamp.sh — five-case test for the F241 Open-Questions placement +
# integrity-stamp machinery (per F241 § Success Criteria):
#   (a) `Q+ define` on a fresh doc creates the block as the first H2 BELOW the
#       H1 with a valid `<!-- state:q XX -->` stamp;
#   (b) a hand-edit inside the block breaks the stamp (recompute != stored);
#   (c) `state <doc> revalidate` re-stamps a format-valid hand-edited block, and
#       REFUSES a format-invalid one (missing Recommendation) with rc!=0;
#   (d) a stampless legacy block warns nothing (grandfathered) — audit-q clean;
#   (e) a legacy above-the-H1 block is relocated below the H1 by revalidate.
#
# Uses a throwaway fixture anchor under ~/ob/kmr/Topic/Misc/Test/ (per the
# smoke-tests-live-in-the-vault convention); snapshots + restores Q.md and
# removes every fixture artifact on exit.
set -u

STATE=~/.claude/skills/workflow/scripts/state
AUDIT=~/.claude/skills/audit/scripts/audit-q.py
BE=~/.claude/skills/workflow/scripts/backlog-edit.py
FIX_ROOT=~/ob/kmr/Topic/Misc/Test/"F241 Fixture"
TRACK="$FIX_ROOT/F241FIX Track"
BACKLOG="$TRACK/F241FIX Backlog.md"
DOC="$FIX_ROOT/Fixture Doc.md"
QMD=~/ob/kmr/Q.md
TMP=$(mktemp -d)
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/triage/F241FIX.json
    [ -f "$TMP/Q.md.bak" ] && cp "$TMP/Q.md.bak" "$QMD"
    rm -rf "$TMP"
}
trap cleanup EXIT
cp "$QMD" "$TMP/Q.md.bak"

mkdir -p "$TRACK"
printf 'slug: F241FIX\ntitle: F241 Fixture\n' > "$FIX_ROOT/.anchor"

ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

fresh_backlog() {
    cat > "$BACKLOG" <<'EOF'
# F241FIX Backlog

## Now

- **T001 — Fixture row** [Questions] — → [[Fixture Doc]] ^T001

## Done
EOF
}

fresh_doc() {
    cat > "$DOC" <<'EOF'
---
description: fixture feature doc
---

# F241FIX · Fixture Doc
Orientation line for the fixture.

## Summary

Body prose.

## Status

**Questions** — fixture gate
EOF
}

# stamp helper — first char index of ## Open Questions vs first H1
oq_line()   { grep -n '^## Open Questions$' "$1" | head -1 | cut -d: -f1; }
h1_line()   { grep -n '^# ' "$1" | head -1 | cut -d: -f1; }
has_stamp() { grep -q '<!-- state:q [0-9a-z][0-9a-z] -->' "$1"; }

# ---------- Case A — define places block below H1 with a valid stamp ----------
fresh_backlog; fresh_doc
printf -- '- **Q1 — Pick a color** — Which color?\n  - **(A)** Red.\n  - **(B)** Blue.\n- **Recommendation:** Lean (A)\n' \
  | "$STATE" --anchor "$FIX_ROOT" "Fixture Doc" Q1 define >/dev/null 2>&1
OQ=$(oq_line "$DOC"); H1=$(h1_line "$DOC")
if [ -n "$OQ" ] && [ -n "$H1" ] && [ "$OQ" -gt "$H1" ]; then
    ok "A: Open Questions is below the H1 (H1=$H1, OQ=$OQ)"
else
    bad "A: expected OQ below H1 — H1=$H1 OQ=$OQ"
fi
if has_stamp "$DOC"; then
    ok "A2: block carries an integrity stamp"
else
    bad "A2: no stamp written — $(sed -n "${OQ}p;$((OQ+1))p" "$DOC")"
fi

# ---------- Case B — a hand-edit breaks the stamp ----------
python3 - "$DOC" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
p.write_text(s.replace("Which color?", "Which color, exactly?"))
PY
VERDICT=$(python3 - "$DOC" "$BE" <<'PY'
import sys, importlib.util, pathlib
doc, be_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("be", be_path)
be = importlib.util.module_from_spec(spec); spec.loader.exec_module(be)
lines = pathlib.Path(doc).read_text().splitlines()
rng = be._open_questions_range(lines)
stored = be.read_q_stamp(lines, *rng); computed = be.compute_q_stamp(lines, *rng)
print("MISMATCH" if stored != computed else "MATCH")
PY
)
if [ "$VERDICT" = "MISMATCH" ]; then
    ok "B: hand-edit inside the block breaks the stamp"
else
    bad "B: expected stamp mismatch after hand-edit — got $VERDICT"
fi

# ---------- Case C1 — revalidate re-stamps a format-valid hand-edited block ----------
OUT=$("$STATE" --anchor "$FIX_ROOT" "Fixture Doc" revalidate 2>&1); RC=$?
VERDICT=$(python3 - "$DOC" "$BE" <<'PY'
import sys, importlib.util, pathlib
doc, be_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("be", be_path)
be = importlib.util.module_from_spec(spec); spec.loader.exec_module(be)
lines = pathlib.Path(doc).read_text().splitlines()
rng = be._open_questions_range(lines)
stored = be.read_q_stamp(lines, *rng); computed = be.compute_q_stamp(lines, *rng)
print("MATCH" if stored == computed else "MISMATCH")
PY
)
if [ "$RC" -eq 0 ] && [ "$VERDICT" = "MATCH" ]; then
    ok "C1: revalidate re-stamped the valid block (rc=$RC)"
else
    bad "C1: expected re-stamp — rc=$RC verdict=$VERDICT out=$OUT"
fi

# ---------- Case C2 — revalidate REFUSES a format-invalid block ----------
python3 - "$DOC" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
p.write_text(re.sub(r"- \*\*Recommendation:\*\* Lean \(A\)\n", "", s))
PY
OUT=$("$STATE" --anchor "$FIX_ROOT" "Fixture Doc" revalidate 2>&1); RC=$?
if [ "$RC" -ne 0 ] && echo "$OUT" | grep -qi "ask-format"; then
    ok "C2: revalidate refused a format-invalid block (rc=$RC)"
else
    bad "C2: expected ask-format refusal — rc=$RC out=$OUT"
fi

# ---------- Case D — a stampless legacy block warns nothing ----------
fresh_backlog
cat > "$DOC" <<'EOF'
---
description: fixture feature doc
---

# F241FIX · Fixture Doc
Orientation line.

## Open Questions

- **Q1 — Legacy stampless** — Which one? ^Fixture-Doc-Q1
  - **(A)** This.
  - **(B)** That.
- **Recommendation:** Lean (A)

## Summary

Body.

## Status

**Questions** — fixture gate
EOF
OUT=$(python3 "$AUDIT" --scope backlog --anchor F241FIX --dry 2>&1)
if echo "$OUT" | grep -q "C48"; then
    bad "D: stampless legacy block should be grandfathered — got C48: $OUT"
else
    ok "D: stampless legacy block warns no C48 (grandfathered)"
fi

# ---------- Case E — revalidate relocates a legacy above-H1 block ----------
cat > "$DOC" <<'EOF'
---
description: fixture feature doc
---

## Open Questions

- **Q1 — Above the H1** — Which one? ^Fixture-Doc-Q1
  - **(A)** This.
  - **(B)** That.
- **Recommendation:** Lean (A)

# F241FIX · Fixture Doc
Orientation line.

## Summary

Body.
EOF
"$STATE" --anchor "$FIX_ROOT" "Fixture Doc" revalidate >/dev/null 2>&1
OQ=$(oq_line "$DOC"); H1=$(h1_line "$DOC")
if [ -n "$OQ" ] && [ -n "$H1" ] && [ "$OQ" -gt "$H1" ] && has_stamp "$DOC"; then
    ok "E: revalidate relocated the legacy above-H1 block below the H1 + stamped (H1=$H1, OQ=$OQ)"
else
    bad "E: expected relocation below H1 — H1=$H1 OQ=$OQ stamp=$(has_stamp "$DOC" && echo yes || echo no)"
fi

echo "----------------------------------------"
echo "F241 q-stamp test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
