#!/bin/bash
# Maintain hook — runs on every Read tool use
# Phase 1: ~1ms — check if pending maintenance exists
# Phase 2: ~1ms — check if it's time to recheck
# Phase 3: ~0ms — kick off background check, don't block

SKLDIR=".skl/maintain"
PENDING="$SKLDIR/pending.md"
TABLE_FILE=""

# Find the maintenance table — look for *Maintenance.md in Plan folder
# Quick check: does .skl/maintain even exist?
[ -d "$SKLDIR" ] || exit 0

# Phase 1: Is there pending maintenance to report?
if [ -s "$PENDING" ]; then
    cat "$PENDING"
    exit 0
fi

# Phase 2: Is it time to check?
NEXT="$SKLDIR/next-check"
NOW=$(date +%s)
if [ -f "$NEXT" ]; then
    THEN=$(cat "$NEXT" 2>/dev/null)
    [ "$NOW" -lt "${THEN:-0}" ] && exit 0
fi

# Phase 3: Time to check — update timer, kick off background
echo $((NOW + 30)) > "$NEXT"
python3 ~/.claude/skills/cab/maintain-check.py "$(pwd)" > "$PENDING" 2>/dev/null &
exit 0
