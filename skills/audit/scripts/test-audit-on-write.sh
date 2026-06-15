#!/bin/bash
# test-audit-on-write.sh — F177 end-to-end integration test.
#
# Drives the audit-on-write hook on two deliberately-broken fixtures and asserts
# both paths fire: a mechanical fault is auto-repaired on disk; a judgment fault
# is left untouched but surfaced as an agent message. Mechanical PASS/FAIL, exit
# code. This proves the plumbing — NOT rule-correctness-in-all-cases (out of scope).

set -u
HOOK="$HOME/.claude/skills/audit/scripts/audit-on-write.sh"
SCRATCH="$HOME/ob/kmr/Topic/Misc/Test/F177/scratch"
mkdir -p "$SCRATCH"
export AUDIT_ON_WRITE_ROOTS="$SCRATCH/.roots"
echo "$SCRATCH" > "$AUDIT_ON_WRITE_ROOTS"
fail=0

drive() {  # $1 = file path → pipe a synthetic PostToolUse payload through the hook
    echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$1\"}}" | bash "$HOOK"
}

# ── Fixture 1 — mechanical fault (table jammed against text) → expect auto-fix ──
FM="$SCRATCH/fix-me.md"
printf '%s\n' '---' 'description: fix me' '---' '# Fix Me' 'A summary.' '' \
    '## Body' 'Text before.' '| a | b |' '| - | - |' '| 1 | 2 |' 'Text after.' > "$FM"
drive "$FM" >/dev/null
if python3 - "$FM" << 'PY'
import sys
t = open(sys.argv[1]).read()
sys.exit(0 if ("Text before.\n\n| a | b |" in t and "| 1 | 2 |\n\nText after." in t) else 1)
PY
then echo "PASS  auto-fix — table now has surrounding blank lines"
else echo "FAIL  auto-fix — table not repaired"; fail=1; fi

# ── Fixture 2 — judgment fault (markdown inside a fence) → expect message, no edit ──
GM="$SCRATCH/flag-me.md"
printf '%s\n' '---' 'description: flag me' '---' '# Flag Me' 'A summary.' '' \
    '## Body' 'Example:' '```' '# [[Some Doc]]' '```' 'Done.' > "$GM"
before=$(shasum "$GM" | cut -d' ' -f1)
msg=$(drive "$GM")
after=$(shasum "$GM" | cut -d' ' -f1)
if [ "$before" = "$after" ]; then echo "PASS  message — file left byte-unchanged"
else echo "FAIL  message — file was mutated"; fail=1; fi
if printf '%s' "$msg" | grep -q "R-markdown-11"; then echo "PASS  message — agent message emitted (R-markdown-11)"
else echo "FAIL  message — no agent message surfaced"; fail=1; fi

echo "---"
[ "$fail" = 0 ] && echo "ALL PASS" || echo "FAILURES ($fail)"
exit "$fail"
