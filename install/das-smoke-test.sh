#!/bin/bash
# Smoke test for das (F225) — hermetic: fake clone + temp $HOME.
set -e
DAS_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/das"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

CLONE="$WORK/clone"
export HOME="$WORK/home"
TARGET="$HOME/.claude/skills"

mkdir -p "$CLONE/install" "$HOME"
cp "$DAS_SRC" "$CLONE/install/das"
chmod +x "$CLONE/install/das"
for s in crank groom triage audit; do          # crank/groom/triage=Drive, audit=Hygiene
    mkdir -p "$CLONE/skills/$s"
    echo "# $s v1" > "$CLONE/skills/$s/SKILL.md"
done
DAS="$CLONE/install/das"

fail() { echo "FAIL: $1"; exit 1; }

# 1. enable a group → all member symlinks exist
"$DAS" enable Drive > /dev/null
for s in crank groom triage; do
    [ -L "$TARGET/$s" ] || fail "enable Drive: $s not symlinked"
done
[ ! -e "$TARGET/audit" ] || fail "enable Drive: audit leaked in"

# 2. disable one → gone; others remain
"$DAS" disable groom > /dev/null
[ ! -e "$TARGET/groom" ] || fail "disable groom: still present"
[ -L "$TARGET/crank" ] && [ -L "$TARGET/triage" ] || fail "disable groom: siblings lost"

# 3. real dir at a skill path → enable preserves it (SKIP), never overwrites
mkdir -p "$TARGET/audit"
echo "my customized audit" > "$TARGET/audit/SKILL.md"
"$DAS" enable audit | grep -q SKIP || fail "enable over real dir: no SKIP"
[ ! -L "$TARGET/audit" ] || fail "enable over real dir: clobbered to symlink"
grep -q "my customized audit" "$TARGET/audit/SKILL.md" || fail "real dir content lost"

# 4. disable never removes a real dir
"$DAS" disable audit | grep -q SKIP || fail "disable real dir: no SKIP"
[ -d "$TARGET/audit" ] || fail "disable real dir: removed it"

# 5. fork a skill, bump the clone → fork unchanged; diff reports the delta
"$DAS" fork crank > /dev/null
[ ! -L "$TARGET/crank" ] && [ -d "$TARGET/crank" ] || fail "fork crank: not a real dir"
echo "# crank v2 (upstream bump)" > "$CLONE/skills/crank/SKILL.md"
grep -q "crank v1" "$TARGET/crank/SKILL.md" || fail "pin bump touched the fork"
"$DAS" diff crank | grep -q "v2" || fail "diff crank: delta not reported"

# 6. diff on a symlinked skill → no divergence, exit 0
"$DAS" diff triage | grep -q "track-live" || fail "diff symlinked: wrong report"

# 7. status runs and shows states
"$DAS" status | grep -q "restart agents" || fail "status: missing session-scope note"

echo "PASS: all das smoke tests"
