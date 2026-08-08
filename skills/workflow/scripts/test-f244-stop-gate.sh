#!/bin/bash
# test-f244-stop-gate.sh — the F244 never-strand-the-user Stop gate
# (crank-stop-hook.py). Drives the hook with synthetic Stop payloads against a
# throwaway fixture anchor, asserting the worklist-empty invariant:
#   (A) work-armed (turn used a tool) + dirty worklist  → BLOCK
#   (B) work-armed + clean worklist (empty frontier)    → ALLOW
#   (C) NOT armed (pure-text turn) + dirty worklist      → ALLOW (chat turn)
#   (D) grooming the dirty row (add Next) empties it     → ALLOW
#   (E) block cap: 3 blocks then the 4th ALLOWs (fail-open)
#   (F) the disarm (4th) writes a record to stopgate/disarms.jsonl
#
# F269 — the fixture anchor now lives in a THROWAWAY VAULT, not the real one.
# `ANCHOR_VAULT_ROOT` points `state` / `backlog-edit.py` / `queries-render.py`
# at $TMP, so the render splices its section into $TMP/Q.md and cannot reach
# the live file at all. What this replaces was worse than it looked: the
# fixture rendered into the REAL ~/ob/kmr/Q.md and teardown `cp`-restored a
# snapshot, which (a) left an orphan section behind on any path that skipped
# the trap, and (b) silently reverted whatever a CONCURRENT agent had written
# to Q.md while the test ran.
set -u

HOOK=~/.claude/skills/workflow/scripts/crank-stop-hook.py
STATE=~/.claude/skills/workflow/scripts/state
TMP=$(mktemp -d)
export ANCHOR_VAULT_ROOT="$TMP/vault"
mkdir -p "$ANCHOR_VAULT_ROOT/Topic/Misc/Test"
printf '# Q\n' > "$ANCHOR_VAULT_ROOT/Q.md"
FIX_ROOT="$ANCHOR_VAULT_ROOT/Topic/Misc/Test/F244 Fixture"
BACKLOG="$FIX_ROOT/F244FIX Track/F244FIX Backlog.md"
QMD="$ANCHOR_VAULT_ROOT/Q.md"
PASS=0; FAIL=0

DISARM_LOG=~/.config/anchor-system/stopgate/disarms.jsonl
cleanup() {
    rm -rf "$FIX_ROOT"
    rm -f ~/.config/anchor-system/stopgate/F244FIX.json
    rm -f ~/.config/anchor-system/crank/F244FIX.json
    # strip this fixture's rows from the shared disarm log (no test pollution)
    if [ -f "$DISARM_LOG" ]; then
        grep -v '"anchor": "F244FIX"' "$DISARM_LOG" > "$DISARM_LOG.tmp" 2>/dev/null
        mv "$DISARM_LOG.tmp" "$DISARM_LOG" 2>/dev/null
    fi
    # No Q.md snapshot to restore any more (F269): the Q.md this test renders
    # into lives inside $TMP and goes away with it. A fixture still cannot reap
    # its own section — the reaper needs the backlog cleanup just deleted — but
    # that no longer matters when the orphan and the file holding it are both
    # thrown away.
    rm -rf "$TMP"
}
trap cleanup EXIT

mkdir -p "$FIX_ROOT/F244FIX Track"
printf 'slug: F244FIX\ntitle: F244 Fixture\n' > "$FIX_ROOT/.anchor"
# slug stub: `state` regenerates a queries.md whose banner self-links [[F244FIX]];
# without a page of that basename it dangles (C22) and the finding lands on the
# groom worklist (F258), so a "groomed" fixture never reaches count 0. (F265.)
printf '# F244FIX\n' > "$FIX_ROOT/F244FIX.md"

ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# --- transcripts ---
TOOL_TX="$TMP/tool.jsonl"
cat > "$TOOL_TX" <<'EOF'
{"type":"user","message":{"content":"go do the thing"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{}}]}}
{"type":"user","message":{"content":[{"type":"tool_result","content":"ok"}]}}
{"type":"assistant","message":{"content":[{"type":"text","text":"done"}]}}
EOF
TEXT_TX="$TMP/text.jsonl"
cat > "$TEXT_TX" <<'EOF'
{"type":"user","message":{"content":"what do you think about X?"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"here is my opinion"}]}}
EOF

dirty_backlog() {
    cat > "$BACKLOG" <<'EOF'
# F244FIX Backlog

## Now

- **T001 — Ungroomed row** [Ready] — no Next, so it is on the worklist ^T001

## Done
EOF
}
clean_backlog() {
    cat > "$BACKLOG" <<'EOF'
# F244FIX Backlog

## Now

## Done
EOF
}

payload() { printf '{"cwd":"%s","transcript_path":"%s"}' "$FIX_ROOT" "$1"; }
blocked() { echo "$1" | grep -q '"decision": *"block"'; }

# ---------- A — work-armed + dirty → BLOCK ----------
rm -f ~/.config/anchor-system/stopgate/F244FIX.json
dirty_backlog
OUT=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
if blocked "$OUT"; then ok "A: work-armed + dirty worklist blocks"; else bad "A: expected block — out: $OUT"; fi

# ---------- B — work-armed + clean → ALLOW ----------
rm -f ~/.config/anchor-system/stopgate/F244FIX.json
clean_backlog
OUT=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
if blocked "$OUT"; then bad "B: expected allow on clean worklist — out: $OUT"; else ok "B: work-armed + empty worklist allows"; fi

# ---------- C — NOT armed (pure text) + dirty → ALLOW ----------
rm -f ~/.config/anchor-system/stopgate/F244FIX.json
dirty_backlog
OUT=$(payload "$TEXT_TX" | python3 "$HOOK" 2>/dev/null)
if blocked "$OUT"; then bad "C: pure-chat turn must not be gated — out: $OUT"; else ok "C: un-armed (pure-text) turn allows despite dirty worklist"; fi

# ---------- D — grooming the row (add Next) empties worklist → ALLOW ----------
rm -f ~/.config/anchor-system/stopgate/F244FIX.json
dirty_backlog
"$STATE" set "$FIX_ROOT" Backlog T001 --status Ready --next "run the concrete first step with zero user involvement" >/dev/null 2>&1
CNT=$("$STATE" groom-list "$FIX_ROOT" --count 2>/dev/null | tail -1)
OUT=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
if [ "$CNT" = "0" ] && ! blocked "$OUT"; then ok "D: adding a Next empties the worklist and allows the stop"; else bad "D: expected count=0 + allow — count=$CNT out: $OUT"; fi

# ---------- E — block cap: 3 blocks then allow ----------
rm -f ~/.config/anchor-system/stopgate/F244FIX.json
grep -v '"anchor": "F244FIX"' "$DISARM_LOG" > "$DISARM_LOG.tmp" 2>/dev/null && mv "$DISARM_LOG.tmp" "$DISARM_LOG" 2>/dev/null
dirty_backlog
b1=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
b2=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
b3=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
b4=$(payload "$TOOL_TX" | python3 "$HOOK" 2>/dev/null)
if blocked "$b1" && blocked "$b2" && blocked "$b3" && ! blocked "$b4"; then
    ok "E: block cap fails open on the 4th consecutive block"
else
    bad "E: expected block×3 then allow — $(blocked "$b1" && echo B||echo A)$(blocked "$b2" && echo B||echo A)$(blocked "$b3" && echo B||echo A)$(blocked "$b4" && echo B||echo A)"
fi

# ---------- F — the disarm (4th block) was recorded to disarms.jsonl ----------
if [ -f "$DISARM_LOG" ] && grep '"anchor": "F244FIX"' "$DISARM_LOG" | grep -q '"blocks": 4'; then
    ok "F: disarm recorded to disarms.jsonl (anchor + blocks=4)"
else
    bad "F: expected a F244FIX disarm row with blocks=4 in $DISARM_LOG"
fi

echo "----------------------------------------"
echo "F244 stop-gate test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
