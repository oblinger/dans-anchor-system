#!/bin/bash
# test-f248-summary-line.sh — the F248 canonical closing/summary-line emitter
# (`state <anchor> summary-line --recommend <directive>`). Asserts the exact
# T034 line character-for-character for every recommendation directive, on a
# fixture anchor whose banner carries known Runnable/User/Verify counts:
#   - counts (Runnable/User/Verify), ` . ` separators, `Groomed`, and the
#     recommendation slot are all OWNED by state and must match the golden line;
#   - `--recommend` is REQUIRED (never-strand guard) — omitting it errors;
#   - an unknown directive errors;
#   - piped/captured output carries NO ANSI escape (redirect-safe).
#
# Fixture anchor lives under ~/ob/kmr/Topic/Misc/Test/ (smoke-tests-in-vault).
set -u

STATE=~/.claude/skills/workflow/scripts/state
FIX_ROOT=~/ob/kmr/Topic/Misc/Test/"F248 Fixture"
TRACK="$FIX_ROOT/F248FIX Track"
BACKLOG="$TRACK/F248FIX Backlog.md"
QUERIES="$TRACK/F248FIX queries.md"
PASS=0; FAIL=0

cleanup() { rm -rf "$FIX_ROOT"; }
trap cleanup EXIT

mkdir -p "$TRACK"
printf 'slug: F248FIX\ntitle: F248 Fixture\n' > "$FIX_ROOT/.anchor"
cat > "$BACKLOG" <<'EOF'
# F248FIX Backlog

## Now

## Done
EOF

ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# Write a synthetic banner with the given counts — summary-line scrapes exactly
# this H1 line for its counts (same source as the live queries.md render).
set_banner() {  # $1=ready $2=questions $3=verify
    cat > "$QUERIES" <<EOF
---
kind: queries
---
# [U+A] F248FIX — Runnable $1 . User $2 . Verify $3 — Legwork 0
EOF
}

# assert: directive $2 on the current banner emits exactly the golden line $3
golden() {  # $1=label $2=directive $3=expected-line
    local out
    out=$(NO_COLOR=1 "$STATE" summary-line "$FIX_ROOT" --recommend "$2" 2>/dev/null)
    if [ "$out" = "$3" ]; then ok "$1"; else bad "$1 — got: [$out] want: [$3]"; fi
}

# ---------- Scenario 1 — Runnable 3, User 1, Verify 2 (singular phrasing) ----------
set_banner 3 1 2
golden "compact"   compact   "F248FIX: please /compact . Groomed . Runnable 3 . User 1 . Verify 2"
golden "clear"     clear     "F248FIX: please /clear . Groomed . Runnable 3 . User 1 . Verify 2"
golden "crank"     crank     "F248FIX: crank with ' . Groomed . Runnable 3 . User 1 . Verify 2"
golden "nothing"   nothing   "F248FIX: crank with ' . Groomed . Runnable 3 . User 1 . Verify 2"
golden "answer/1"  answer    "F248FIX: answer the 1 on your plate . Groomed . Runnable 3 . User 1 . Verify 2"
golden "clear-all" clear-all "F248FIX: all clear . Groomed . Runnable 3 . User 1 . Verify 2"
golden "done"      done      "F248FIX: all clear . Groomed . Runnable 3 . User 1 . Verify 2"

# ---------- Scenario 2 — User 2 (plural) ----------
set_banner 3 2 2
golden "answer/2"  answer    "F248FIX: answer the 2 on your plate . Groomed . Runnable 3 . User 2 . Verify 2"

# ---------- Scenario 3 — all-zero banner ----------
set_banner 0 0 0
golden "crank/0"   crank     "F248FIX: crank with ' . Groomed . Runnable 0 . User 0 . Verify 0"

# ---------- Guard A — --recommend is required ----------
set_banner 3 1 2
if NO_COLOR=1 "$STATE" summary-line "$FIX_ROOT" >/dev/null 2>&1; then
    bad "guard: missing --recommend must error"
else
    ok "guard: missing --recommend errors (never-strand)"
fi

# ---------- Guard B — unknown directive errors ----------
if NO_COLOR=1 "$STATE" summary-line "$FIX_ROOT" --recommend bogus >/dev/null 2>&1; then
    bad "guard: unknown directive must error"
else
    ok "guard: unknown directive errors"
fi

# ---------- Guard C — piped output carries no ANSI escape (redirect-safe) ----------
raw=$("$STATE" summary-line "$FIX_ROOT" --recommend crank 2>/dev/null)
if printf '%s' "$raw" | grep -q $'\033'; then
    bad "guard: piped output must be plain (no ANSI)"
else
    ok "guard: piped output is plain (no ANSI escape)"
fi

echo "----------------------------------------"
echo "F248 summary-line test: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
