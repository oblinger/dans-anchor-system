#!/bin/bash
# test-f248-summary-line.sh — the F248 canonical closing/summary-line emitter
# (`state <anchor> summary-line --recommend <directive>`). Asserts the exact
# T034 line character-for-character for every recommendation directive, on a
# fixture anchor whose banner carries known Ready/User/Parked counts:
#   - counts (Ready/User/Parked), ` . ` separators, `Groomed`, and the
#     recommendation slot are all OWNED by state and must match the golden line;
#   - `--recommend` is REQUIRED (never-strand guard) — omitting it errors;
#   - an unknown directive errors;
#   - piped/captured output carries NO ANSI escape (redirect-safe).
#
# F269 — the fixture anchor lives in a THROWAWAY VAULT under $TMP, not in the
# real one. `ANCHOR_VAULT_ROOT` points `state` / `backlog-edit.py` /
# `queries-render.py` at it, so the render splices its section into $TMP/Q.md
# and cannot reach the live file. The old shape rendered F248FIX into the REAL
# ~/ob/kmr/Q.md and `cp`-restored a snapshot on exit, which left an orphan
# section on any path that skipped the trap and could revert a concurrent
# agent's Q.md writes.
set -u

STATE=~/.claude/skills/workflow/scripts/state
TMP=$(mktemp -d)
export ANCHOR_VAULT_ROOT="$TMP/vault"
mkdir -p "$ANCHOR_VAULT_ROOT/Topic/Misc/Test"
printf '# Q\n' > "$ANCHOR_VAULT_ROOT/Q.md"
FIX_ROOT="$ANCHOR_VAULT_ROOT/Topic/Misc/Test/F248 Fixture"
TRACK="$FIX_ROOT/F248FIX Track"
BACKLOG="$TRACK/F248FIX Backlog.md"
QUERIES="$TRACK/F248FIX queries.md"
QMD="$ANCHOR_VAULT_ROOT/Q.md"
PASS=0; FAIL=0

cleanup() {
    rm -rf "$FIX_ROOT"
    # F269 — nothing to restore: the Q.md this test renders into
    # is inside $TMP and goes away with it.
    rm -rf "$TMP"
}
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

# Write a banner with the given counts — summary-line scrapes exactly this H1
# line for its counts (same source as the live queries.md render).
#
# THIS MUST BE THE REAL BANNER FORM. It was not: the fixture used to emit
# `# [U+A] F248FIX — Runnable N . User N . Verify N — Legwork 0`, a shape the
# renderer has never produced, with ` . ` separators and a trailing `Legwork`
# field that exist nowhere in the spec. It passed anyway because the scraping
# regexes were unanchored, so `Runnable\s+(\d+)` matched any spelling. F305
# anchored them on their zone separators — the words `Ready` and `Parked` also
# occur as BRACKET names, so an unanchored match picks the wrong number — and
# the invented form stopped matching, which is the fixture failing honestly for
# the first time. Keep this string identical to `audit_q.format_status_banner`.
set_banner() {  # $1=ready $2=user $3=parked
    cat > "$QUERIES" <<EOF
---
kind: queries
---
# [U+A]  [[F248FIX|F248FIX]]  -  Ready $1    User $2   |   Now 0    Next 0    Later 0   |   Parked $3    Waiting 0    Icebox 0
EOF
}

# assert: directive $2 on the current banner emits exactly the golden line $3
golden() {  # $1=label $2=directive $3=expected-line
    local out
    out=$(NO_COLOR=1 "$STATE" summary-line "$FIX_ROOT" --recommend "$2" 2>/dev/null)
    if [ "$out" = "$3" ]; then ok "$1"; else bad "$1 — got: [$out] want: [$3]"; fi
}

# ---------- Scenario 1 — Ready 3, User 1, Parked 2 (singular phrasing) ----------
set_banner 3 1 2
golden "compact"   compact   "F248FIX: please /compact . Groomed . Ready 3 . User 1 . Parked 2"
golden "clear"     clear     "F248FIX: please /clear . Groomed . Ready 3 . User 1 . Parked 2"
golden "crank"     crank     "F248FIX: crank with ' . Groomed . Ready 3 . User 1 . Parked 2"
golden "nothing"   nothing   "F248FIX: crank with ' . Groomed . Ready 3 . User 1 . Parked 2"
golden "answer/1"  answer    "F248FIX: answer the 1 on your plate . Groomed . Ready 3 . User 1 . Parked 2"
golden "clear-all" clear-all "F248FIX: all clear . Groomed . Ready 3 . User 1 . Parked 2"
golden "done"      done      "F248FIX: all clear . Groomed . Ready 3 . User 1 . Parked 2"

# ---------- Scenario 2 — User 2 (plural) ----------
set_banner 3 2 2
golden "answer/2"  answer    "F248FIX: answer the 2 on your plate . Groomed . Ready 3 . User 2 . Parked 2"

# ---------- Scenario 3 — all-zero banner ----------
set_banner 0 0 0
golden "crank/0"   crank     "F248FIX: crank with ' . Groomed . Ready 0 . User 0 . Parked 0"

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
