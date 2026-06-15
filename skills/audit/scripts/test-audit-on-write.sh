#!/bin/bash
# test-audit-on-write.sh — F177/F179 end-to-end integration test.
#
# Drives the audit-on-write hook on deliberately-broken fixtures and asserts both
# paths fire correctly: auto-fix rules repair the file in place; flag rules emit an
# agent message and leave the offending content untouched. Also asserts the F179
# safety properties — alphanumeric content is preserved (never deleted) and the hook
# is idempotent. Mechanical PASS/FAIL, exit code. Proves plumbing — not rule
# correctness in all cases (that's the agent-verification workflow's job).

set -u
HOOK="$HOME/.claude/skills/audit/scripts/audit-on-write.sh"
SCRATCH="$HOME/ob/kmr/Topic/Misc/Test/F177/scratch"
mkdir -p "$SCRATCH"
export AUDIT_ON_WRITE_ROOTS="$SCRATCH/.roots"
echo "$SCRATCH" > "$AUDIT_ON_WRITE_ROOTS"
fail=0
ok()   { echo "PASS  $1"; }
bad()  { echo "FAIL  $1"; fail=1; }
drive() { echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$1\"}}" | bash "$HOOK"; }

# ── 1. Auto-fix — table jammed against text ──────────────────────────────────
FM="$SCRATCH/fix-me.md"
printf '%s\n' '---' 'description: fix me' '---' '# Fix Me' 'A summary.' '' \
    '## Body' 'Before.' '| a | b |' '| - | - |' '| 1 | 2 |' 'After.' > "$FM"
drive "$FM" >/dev/null
grep -qz $'Before.\n\n| a | b |' "$FM" 2>/dev/null && ok "auto-fix table-blank" || \
  python3 -c "import sys;t=open('$FM').read();sys.exit(0 if 'Before.\n\n| a | b |' in t else 1)" \
    && ok "auto-fix table-blank" || bad "auto-fix table-blank"

# ── 2. Flag — markdown inside a fence (file unchanged, message emitted) ───────
GM="$SCRATCH/flag-me.md"
printf '%s\n' '---' 'description: flag me' '---' '# Flag Me' 'A summary.' '' \
    '## Body' 'Ex:' '```' '# [[Some Doc]]' '```' 'Done.' > "$GM"
b=$(shasum "$GM"|cut -d' ' -f1); msg=$(drive "$GM"); a=$(shasum "$GM"|cut -d' ' -f1)
[ "$b" = "$a" ] && ok "flag fence — file unchanged" || bad "flag fence — file mutated"
printf '%s' "$msg" | grep -q "R-markdown-11" && ok "flag fence — message emitted" || bad "flag fence — no message"

# ── 3. Multi-rule auto-fix (pipe / em-dash / trailing) + angle-bracket flag ───
MM="$SCRATCH/multi.md"
printf '%s\n' '---' 'description: m' '---' '# M' 'Sum.' '' '## B' \
    'Prose with -- dash and trailing   ' 'Lead.' '| [[a|b]] | c |' '| - | - |' \
    'After with <ngle> bracket.' > "$MM"
orig_alnum=$(python3 -c "import sys;print(''.join(c for c in open('$MM').read() if c.isalnum()))")
msg=$(drive "$MM")
python3 - "$MM" << PY && ok "multi auto-fix — pipe+em-dash+trailing repaired" || bad "multi auto-fix"
import sys
t = open("$MM").read()
need = ['[[a\\\\|b]]', ' — dash', 'trailing\n']            # pipe escaped, em-dash, trailing stripped
sys.exit(0 if all(n in t for n in need) else 1)
PY
printf '%s' "$msg" | grep -q "R-markdown-13" && ok "angle-bracket flagged" || bad "angle-bracket not flagged"
python3 -c "import sys;sys.exit(0 if '<ngle>' in open('$MM').read() else 1)" \
  && ok "angle-bracket left for agent (not auto-edited)" || bad "angle-bracket was auto-edited"

# ── 4. Safety — alphanumeric content preserved (never deleted) ────────────────
new_alnum=$(python3 -c "import sys;print(''.join(c for c in open('$MM').read() if c.isalnum()))")
python3 -c "import sys;o='$orig_alnum';n='$new_alnum';it=iter(n);sys.exit(0 if all(c in it for c in o) else 1)" \
  && ok "safety — alphanumeric content preserved (no deletion)" || bad "safety — content deleted"

# ── 5. Idempotence — a second hook run makes no further change ────────────────
s1=$(shasum "$MM"|cut -d' ' -f1); drive "$MM" >/dev/null; s2=$(shasum "$MM"|cut -d' ' -f1)
[ "$s1" = "$s2" ] && ok "idempotent — second run is a no-op" || bad "idempotent — second run changed the file"

echo "---"
[ "$fail" = 0 ] && echo "ALL PASS" || echo "FAILURES ($fail)"
exit "$fail"
