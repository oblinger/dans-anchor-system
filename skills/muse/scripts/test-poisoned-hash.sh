#!/usr/bin/env bash
# test-poisoned-hash.sh — regression: MUSE must never write the empty-string
# SHA-256 (e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
# into .muse.hashes.
#
# Root cause of the field failure (2026-07-21): shasum on an iCloud
# FileProvider placeholder returns the empty-string hash because 0 bytes are
# actually readable, but stat still reports the file's final logical size.
# ingest_one then wrote (empty-sha, real-size, path) to the ledger, and every
# subsequent sweep saw the size match and permanently skipped that recording.
# 19 memos silently lost before diagnosis.
#
# This test simulates the failure mode with a 0-byte .m4a: without the fix,
# ingest_one writes the poison entry; with the fix, it refuses and returns 1.

MUSE="$(cd "$(dirname "$0")" && pwd)/muse"

PASS=0; FAIL=0
ok() { PASS=$((PASS + 1)); printf '  PASS: %s\n' "$*"; }
no() { FAIL=$((FAIL + 1)); printf '  FAIL: %s\n' "$*"; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# fake env + stubs (same shape as test-f252-fixes.sh)
export MUSE_ITEMS_DIR="$TMP/items"
export MUSE_QUICK_FILE="$TMP/Quick.md"
export MUSE_LOG_FILE="$TMP/Log Muse.md"
export MUSE_JPR_DIR="$TMP/jpr"
export FFPROBE_BIN="/nonexistent-ffprobe"
mkdir -p "$MUSE_ITEMS_DIR" "$MUSE_JPR_DIR"

# Stubs return non-empty text/title so, WITHOUT the fix, ingest_one runs to
# completion and writes the poisoned hash. The test catches the write, not the
# transcription outcome.
cat > "$TMP/_transcribe" <<'EOF'
#!/usr/bin/env bash
echo "this transcript simulates a race where content materialized after hashing"
EOF
cat > "$TMP/_askAI" <<'EOF'
#!/usr/bin/env bash
echo "Placeholder Race Title"
EOF
chmod +x "$TMP/_transcribe" "$TMP/_askAI"
export TRANSCRIBE_BIN="$TMP/_transcribe"
export ASKAI_BIN="$TMP/_askAI"

# shellcheck disable=SC1090
source "$MUSE"
set +e +o pipefail

EMPTY_SHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

echo "== ingest_one must NOT poison .muse.hashes with the empty-string SHA =="

# Simulate the iCloud placeholder failure mode: a file that hashes to
# EMPTY_SHA (a 0-byte file does this). In production the file appeared with
# its full logical size but readable content was 0 bytes because
# materialization hadn't landed yet.
AUDIO="$MUSE_JPR_DIR/2026-07-21/13-52-41.m4a"
mkdir -p "$(dirname "$AUDIO")"
: > "$AUDIO"   # 0 bytes → shasum returns EMPTY_SHA

# sanity: verify shasum actually returns the empty-string SHA
computed="$(sha256_of "$AUDIO")"
[[ "$computed" == "$EMPTY_SHA" ]] \
    && ok "shasum on 0-byte file returns the empty-string SHA (test fixture is honest)" \
    || no "test fixture broken: sha256_of on 0-byte file returned '$computed', not empty-SHA"

ingest_one "$AUDIO" >/dev/null 2>&1
rc=$?
release_lock 2>/dev/null; MUSE_LOCK_OWNED_BY_ME="no"

HASHFILE="$MUSE_ITEMS_DIR/.muse.hashes"
if [[ -f "$HASHFILE" ]] && grep -q "^$EMPTY_SHA " "$HASHFILE"; then
    no "ingest_one wrote the poison entry to $HASHFILE (this is the bug)"
    echo "    ledger contents:"; sed 's/^/      /' "$HASHFILE"
else
    ok "ingest_one refused to record the empty-string SHA in the ledger"
fi

[[ "$rc" -ne 0 ]] \
    && ok "ingest_one returned non-zero on empty-content input (rc=$rc)" \
    || no "ingest_one returned 0 despite empty-content input — will bump letter, poison ledger"

echo
echo "$PASS passed, $FAIL failed"
[[ "$FAIL" == "0" ]]
