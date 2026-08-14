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
# F269 — the fixture anchor lives in a THROWAWAY VAULT under $TMP, not in the
# real one. `ANCHOR_VAULT_ROOT` points `state` / `backlog-edit.py` /
# `queries-render.py` at it, so the render splices its section into $TMP/Q.md
# and cannot reach the live file. The old shape rendered F241FIX into the REAL
# ~/ob/kmr/Q.md and `cp`-restored a snapshot on exit, which left an orphan
# section on any path that skipped the trap and could revert a concurrent
# agent's Q.md writes.
set -u

STATE=~/.claude/skills/workflow/scripts/state
AUDIT=~/.claude/skills/audit/scripts/audit-q.py
BE=~/.claude/skills/workflow/scripts/backlog-edit.py
TMP=$(mktemp -d)
export ANCHOR_VAULT_ROOT="$TMP/vault"
mkdir -p "$ANCHOR_VAULT_ROOT/Topic/Misc/Test"
printf '# Q\n' > "$ANCHOR_VAULT_ROOT/Q.md"
FIX_ROOT="$ANCHOR_VAULT_ROOT/Topic/Misc/Test/F241 Fixture"
TRACK="$FIX_ROOT/F241FIX Track"
BACKLOG="$TRACK/F241FIX Backlog.md"
DOC="$FIX_ROOT/Fixture Doc.md"
QMD="$ANCHOR_VAULT_ROOT/Q.md"
PASS=0; FAIL=0

cleanup() {
    rm -f ~/.config/anchor-system/triage/F241FIX.json
    rm -rf "$TMP"
}
trap cleanup EXIT

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
# F305 D1 — the writer renames the block to `## Open Items` on touch; the
# legacy spelling is read forever. Accept either.
oq_line()   { grep -n -E '^## Open (Items|Questions)$' "$1" | head -1 | cut -d: -f1; }
h1_line()   { grep -n '^# ' "$1" | head -1 | cut -d: -f1; }
has_stamp() { grep -q '<!-- state:q [0-9a-z][0-9a-z] -->' "$1"; }

# ---------- Case A — define places block below H1 with a valid stamp ----------
fresh_backlog; fresh_doc
printf -- '- **Q1 — Pick a color** — Which color?\n  - **(A)** Red.\n  - **(B)** Blue.\n- **Recommendation:** None\n- **Damage:** taste — fixture color choice\n' \
  | "$STATE" define "$FIX_ROOT" "Fixture Doc" Q1 >/dev/null 2>&1
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
OUT=$("$STATE" revalidate "$FIX_ROOT" "Fixture Doc" 2>&1); RC=$?
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
p.write_text(re.sub(r"- \*\*Recommendation:\*\* None[^\n]*\n", "", s))
PY
OUT=$("$STATE" revalidate "$FIX_ROOT" "Fixture Doc" 2>&1); RC=$?
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
- **Recommendation:** None

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
- **Recommendation:** None

# F241FIX · Fixture Doc
Orientation line.

## Summary

Body.
EOF
"$STATE" revalidate "$FIX_ROOT" "Fixture Doc" >/dev/null 2>&1
OQ=$(oq_line "$DOC"); H1=$(h1_line "$DOC")
if [ -n "$OQ" ] && [ -n "$H1" ] && [ "$OQ" -gt "$H1" ] && has_stamp "$DOC"; then
    ok "E: revalidate relocated the legacy above-H1 block below the H1 + stamped (H1=$H1, OQ=$OQ)"
else
    bad "E: expected relocation below H1 — H1=$H1 OQ=$OQ stamp=$(has_stamp "$DOC" && echo yes || echo no)"
fi

# ---------- Case F (T027) — a section-anchored wiki-link on the Q first line
# survives the define block-anchor strip (regression: the old `\s*\^\S+\s*$`
# strip ate a line-final `[[Doc#^id|alias]]` back to a bare `[[Doc#`). ----------
fresh_backlog; fresh_doc
printf -- '- **Q1 — Section link survives** — See [[F241FIX Backlog#^T001|T001]]\n  - **(A)** Yes.\n  - **(B)** No.\n- **Recommendation:** None\n- **Damage:** taste — fixture link check\n' \
  | "$STATE" define "$FIX_ROOT" "Fixture Doc" Q1 >/dev/null 2>&1
if grep -qF '[[F241FIX Backlog#^T001|T001]]' "$DOC"; then
    ok "F: section-anchored wiki-link survives the define round-trip (T027)"
else
    bad "F: link corrupted by block-anchor strip — got: $(grep -n 'Section link' "$DOC")"
fi

echo "----------------------------------------"
echo "F241 q-stamp test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
