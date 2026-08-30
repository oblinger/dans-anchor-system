#!/bin/bash
# test-t203-slug-disagreement.sh — a declared slug that disagrees with the
# filenames must produce a DIAGNOSIS, not a bare not-found.
#
# `state` resolves an anchor by backlog FILENAME and never reads `.anchor`'s
# `slug:`; `ha -p` reads the declared slug. The two can disagree indefinitely
# with nothing reporting it, and the old error named the missing file rather
# than the disagreement it had actually hit.
#
# Measured by ATT 2026-08-11 mid-rename: `state drop PROS …` failed while
# `.anchor` still said `slug: PROS`, and `state drop BOONE …` worked. An agent
# doing exactly the right thing — read Staff.md, see [[PROS]], drop to PROS —
# got an error that suggested nothing, and only folder-listing found the name
# that worked. Boone's Inbox did not exist until 11:57 that day, consistent
# with never having received a drop.
#
# This asserts the diagnostic ONLY. Which side is authoritative is T203 Q1 and
# is deliberately unresolved — resolution order is unchanged here.
#
# Usage: bash test-t203-slug-disagreement.sh
set -uo pipefail
STATE="$(cd "$(dirname "$0")" && pwd)/state"
PASS=0; FAIL=0
ok(){ if [ "$1" = 0 ]; then PASS=$((PASS+1)); echo "PASS  $2"; else FAIL=$((FAIL+1)); echo "FAIL  $2"; fi; }

TD=$(mktemp -d)
trap 'rm -rf "$TD"' EXIT
mkdir -p "$TD/Boone/BOONE Track"
printf 'slug: PROS\n' > "$TD/Boone/.anchor"
printf '# BOONE Backlog\n\n## Now\n' > "$TD/Boone/Boone Track/Boone Backlog.md"

# 1 — the declared-but-not-operative slug names the disagreement.
out=$(ANCHOR_VAULT_ROOT="$TD" "$STATE" show PROS Backlog T1 2>&1)
echo "$out" | grep -q "DECLARES .slug: PROS"; ok $? "declared slug reports the disagreement"
echo "$out" | grep -q "resolves by filename"; ok $? "...and says which side each tool uses"
echo "$out" | grep -qi "did you mean\|not a directory"; ok $((1-$?)) "...instead of the bare not-found"

# 2 — the operative (filename) slug still resolves. The diagnostic must not
#     have changed resolution, only the message on the failure path.
out=$(ANCHOR_VAULT_ROOT="$TD" "$STATE" show BOONE Backlog T1 2>&1)
echo "$out" | grep -q "Boone Backlog.md"; ok $? "filename slug still resolves normally"
echo "$out" | grep -q "DECLARES"; ok $((1-$?)) "...with no disagreement noise on the success path"

# 3 — a slug nobody declares keeps the original not-found. Without this the fix
#     would trade a bad message for a misleading one on the common typo.
out=$(ANCHOR_VAULT_ROOT="$TD" "$STATE" show NOSUCHSLUG Backlog T1 2>&1)
echo "$out" | grep -q "no 'NOSUCHSLUG Backlog.md' found under"; ok $? "unknown slug keeps the plain not-found"
echo "$out" | grep -q "DECLARES"; ok $((1-$?)) "...and claims no disagreement it did not find"

# 4 — agreement is silent: declared slug == filename prefix resolves with no
#     diagnostic at all. This is the whole corpus's normal state.
mkdir -p "$TD/Ok/OK Track"
printf 'slug: OK\n' > "$TD/Ok/.anchor"
printf '# OK Backlog\n\n## Now\n' > "$TD/Ok/OK Track/OK Backlog.md"
out=$(ANCHOR_VAULT_ROOT="$TD" "$STATE" show OK Backlog T1 2>&1)
echo "$out" | grep -q "DECLARES"; ok $((1-$?)) "matching slug and filename produce no diagnostic"

# 5 — a declared-slug anchor with NO backlog under ANY name (pebble-only,
#     e.g. SVH) is NOT a naming drift: the message must say there is no
#     backlog rather than assert "named otherwise" and offer an unfollowable
#     retry (SV drop 2026-08-13: two probes and a detour to learn what the
#     first message could have said outright).
mkdir -p "$TD/Harness/SVH Track"
printf 'slug: SVH\n' > "$TD/Harness/.anchor"
printf '# SVH Pebble\n' > "$TD/Harness/SVH Track/SVH Pebble.md"
out=$(ANCHOR_VAULT_ROOT="$TD" "$STATE" show SVH Backlog T1 2>&1)
echo "$out" | grep -q "NO backlog under any name"; ok $? "pebble-only anchor: says no backlog exists"
echo "$out" | grep -q "named otherwise"; ok $((1-$?)) "...and does not assert a naming drift"
echo "$out" | grep -q "Retry"; ok $((1-$?)) "...and offers no unfollowable retry"

echo "----------------------------------------"
echo "T203 slug-disagreement: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
