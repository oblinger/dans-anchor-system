#!/bin/bash
# test-f254-mutation-core.sh — F254 Step A: the backlog-edit.py mutation core.
# Regression tests for the F250 Fable-scan CRITICAL/HIGH cluster — each case
# reproduces a finding that silently corrupted the vault's live write path:
#   #1  cross-file (Backlog<->Icebox) move must preserve title/body/status/subs
#       (a bare `set --horizon Icebox` used to rebuild the row from nothing and
#        write the literal `[same]` bracket);
#   #2  a destination guard that refuses AFTER the source delete used to vanish
#       the row from BOTH files — dest now writes first, source deleted after;
#   #3  the F/T/C mint must count TITLE-LESS rows (`- **T002** [Done]`) so it
#       never re-mints an in-use id and overwrites that row;
#   #4  a row ROW_HEADER_RE recognizes but ROW_FULL_RE can't parse (en-dash,
#       missing bracket) must be REFUSED, not treated as fresh and wiped;
#   #7  `define` on an existing row must REPLACE its sub-bullet span, not append
#       (which duplicated Q<n>/Plan bullets).
# Fully isolated: builds a throwaway fake-HOME vault under mktemp, drives the
# real `state` CLI with HOME pointed at it, never touches the real vault.
set -u

STATE="$HOME/.claude/skills/workflow/scripts/state"
FH="$(mktemp -d)"
A="$FH/ob/kmr/ZZTest"
BL="$A/ZZT Track/ZZT Backlog.md"
IB="$A/ZZT Track/ZZT Icebox.md"
PASS=0; FAIL=0
ok(){ echo "  PASS: $1"; PASS=$((PASS+1)); }
no(){ echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
cleanup(){ rm -rf "$FH"; }
trap cleanup EXIT
run(){ HOME="$FH" "$STATE" --anchor ZZT "$@" 2>&1; }

build(){
  rm -rf "$A"
  mkdir -p "$A/ZZT Track" "$A/ZZT Design/ZZT Features"
  printf 'slug: ZZT\n' > "$A/.anchor"
  cat > "$BL" <<'BL_EOF'
---
description: sandbox backlog
---

# ZZT Backlog

## Now

- **F001 — Alpha feature** [Designing] — important body text → [[F001 — Alpha]] ^F001
  - **Plan:** step one then two

## Later

- **T001 — Real task** [Blocked F001] — real body → waiting on thing ^T001
  - **Q1 — Old question** — old details
- **T002** [Done] ^T002
- **T003 – Endash task** [Blocked] — precious body text ^T003

## Done
BL_EOF
  cat > "$IB" <<'IB_EOF'
---
description: sandbox icebox
---

# ZZT Icebox

## Iced

- **F002 — Parked feature** [Blocked F001] — parked body with rich detail ^F002
  - **Plan:** revive when ready
IB_EOF
}

echo "== #1 cross-file move preserves title/body/status/subs =="
build
run Backlog F002 set --horizon Now >/dev/null 2>&1
if grep -q "F002 — Parked feature" "$BL" && grep -q "parked body with rich detail" "$BL" \
   && grep -q "\[Blocked F001\]" "$BL" && grep -q "revive when ready" "$BL"; then
  ok "F002 landed in Backlog with title/body/status/subs intact"
else no "F002 content not preserved on move"; fi
grep -q "\[same\]" "$BL" && no "literal [same] written" || ok "no literal [same] bracket"
grep -q "F002" "$IB" && no "F002 still in Icebox (not deleted)" || ok "F002 removed from Icebox"

echo "== #2 refused destination leaves source row intact =="
build
run Backlog F002 set --horizon Now --status Ready >/dev/null 2>&1  # [Ready] w/o --next -> F171 refuses dest
grep -q "F002" "$IB" && ok "F002 still in Icebox after refused dest" || no "F002 LOST from Icebox (row destroyed)"
grep -q "F002" "$BL" && no "F002 leaked into Backlog despite refusal" || ok "F002 not in Backlog (dest refused cleanly)"

echo "== #3 mint counts title-less / en-dash rows, no overwrite =="
build
out="$(printf '%s' '- **T+ — New minted task** [Designing]' | HOME="$FH" "$STATE" --anchor ZZT Backlog T+ define 2>&1)"
echo "$out" | grep -q "T004" && ok "minted T004 (not an in-use id)" || no "mint returned wrong id: $out"
grep -q "^- \*\*T002\*\* \[Done\]" "$BL" && ok "T002 untouched" || no "T002 was overwritten"

echo "== #4 malformed (en-dash) row refused, not wiped =="
build
out="$(run Backlog T003 set --status Ready --next "do it" 2>&1)"
echo "$out" | grep -qi "malformed" && ok "en-dash T003 edit refused with 'malformed'" || no "T003 edit not refused: $out"
grep -q "precious body text" "$BL" && ok "T003 body preserved" || no "T003 body WIPED"

echo "== #7 re-define existing row REPLACES subs (no duplication) =="
build
printf '%s\n%s' '- **T001 — Real task** [Blocked F001] — new body' '  - **Plan:** brand new plan' \
  | HOME="$FH" "$STATE" --anchor ZZT Backlog T001 define >/dev/null 2>&1
n_new=$(grep -c "brand new plan" "$BL")
[ "$n_new" -eq 1 ] && ok "new sub-bullet present exactly once" || no "new sub-bullet count=$n_new"
grep -q "old details" "$BL" && no "old sub-bullet survived (duplication)" || ok "old sub-bullet replaced, not duplicated"

echo "== regression: normal same-file move still preserves content =="
build
run Backlog F001 set --horizon Later >/dev/null 2>&1
if grep -q "F001 — Alpha feature" "$BL" && grep -q "important body text" "$BL" && grep -q "step one then two" "$BL"; then
  ok "same-file move preserved title/body/subs"
else no "same-file move regressed"; fi

echo
echo "==== RESULT: $PASS passed, $FAIL failed ===="
[ "$FAIL" -eq 0 ]
