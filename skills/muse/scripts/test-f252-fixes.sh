#!/usr/bin/env bash
# test-f252-fixes.sh — F253 Step 4: regression tests for the deferred F252
# Fable-scan MUSE fixes. Sources the muse functions in isolation (the CLI
# dispatch is guarded by BASH_SOURCE==0) with a fake HOME + stub binaries, and
# never touches the real vault / JPR dir.
#
#   F2  manual+sweep share one re-entrant lock (acquire_lock)
#   F3  partial-file recovery via size recorded in the hashfile
#   F5  Log bullets inserted in timestamp order (late arrival → correct slot)
#   F7  hash/transcribe wrapped in a timeout (graceful degradation)
#   F8a hashfile lookup is exact-path (no `x.m4a.m4a` substring match)
#   F8c repeatedly-failing files tracked + skipped, reset on size change
#   F8d Quick/Log rewritten in place (inode + mode preserved)

MUSE="$(cd "$(dirname "$0")" && pwd)/muse"

PASS=0; FAIL=0
ok() { PASS=$((PASS + 1)); printf '  PASS: %s\n' "$*"; }
no() { FAIL=$((FAIL + 1)); printf '  FAIL: %s\n' "$*"; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- fake env + stubs -------------------------------------------------------
export MUSE_ITEMS_DIR="$TMP/items"
export MUSE_QUICK_FILE="$TMP/Quick.md"
export MUSE_LOG_FILE="$TMP/Log Muse.md"
export MUSE_JPR_DIR="$TMP/jpr"
export FFPROBE_BIN="/nonexistent-ffprobe"   # force WPS test to be skipped
mkdir -p "$MUSE_ITEMS_DIR" "$MUSE_JPR_DIR"
cat > "$TMP/_transcribe" <<'EOF'
#!/usr/bin/env bash
echo "this is a test memo with plenty of words to pass"
EOF
cat > "$TMP/_askAI" <<'EOF'
#!/usr/bin/env bash
echo "Test Memo Title"
EOF
chmod +x "$TMP/_transcribe" "$TMP/_askAI"
export TRANSCRIBE_BIN="$TMP/_transcribe"
export ASKAI_BIN="$TMP/_askAI"

# shellcheck disable=SC1090
source "$MUSE"
set +e +o pipefail   # let assertions use || without aborting; keep -u for rigor

# --- F5: insert_log_bullet timestamp ordering -------------------------------
echo "== F5 Log bullets inserted in chronological (newest-first) order =="
LOG="$MUSE_LOG_FILE"
insert_log_bullet "$LOG" "2026-07-16 10:00:00" "- 2026-07-16 10:00:00  [ten](a.md)"
insert_log_bullet "$LOG" "2026-07-16 12:00:00" "- 2026-07-16 12:00:00  [twelve](b.md)"
# late arrival with an OLDER timestamp than 12:00 but NEWER than 10:00
insert_log_bullet "$LOG" "2026-07-16 11:00:00" "- 2026-07-16 11:00:00  [eleven](c.md)"
order="$(grep -oE '\[(ten|eleven|twelve)\]' "$LOG" | tr -d '[]' | tr '\n' ' ')"
if [[ "$order" == "twelve eleven ten " ]]; then
    ok "11:00 arrival spliced between 12:00 and 10:00 (order: $order)"
else
    no "wrong Log order: '$order' (want 'twelve eleven ten ')"
fi
# oldest-ever arrival → bottom
insert_log_bullet "$LOG" "2026-07-16 08:00:00" "- 2026-07-16 08:00:00  [eight](d.md)"
last="$(grep -oE '\[(ten|eight)\]' "$LOG" | tail -1 | tr -d '[]')"
[[ "$last" == "eight" ]] && ok "08:00 arrival lands at the bottom" || no "08:00 not at bottom (last=$last)"

# --- F8d: in-place rewrite preserves inode + mode ---------------------------
echo "== F8d Quick/Log rewritten in place (inode + mode preserved) =="
printf -- '- existing bullet\n' > "$MUSE_QUICK_FILE"
chmod 640 "$MUSE_QUICK_FILE"
ino_before="$(stat -f '%i' "$MUSE_QUICK_FILE")"; mode_before="$(stat -f '%Lp' "$MUSE_QUICK_FILE")"
prepend_line "$MUSE_QUICK_FILE" "- new top bullet"
ino_after="$(stat -f '%i' "$MUSE_QUICK_FILE")"; mode_after="$(stat -f '%Lp' "$MUSE_QUICK_FILE")"
if [[ "$ino_before" == "$ino_after" && "$mode_before" == "$mode_after" ]]; then
    ok "prepend_line kept inode ($ino_after) + mode ($mode_after)"
else
    no "prepend_line changed inode ($ino_before→$ino_after) or mode ($mode_before→$mode_after)"
fi
[[ "$(head -1 "$MUSE_QUICK_FILE")" == "- new top bullet" ]] && ok "new bullet is at the top" || no "new bullet not prepended"

# --- F3 + F8a: _recorded_size exact-path + size extraction ------------------
echo "== F3+F8a hashfile exact-path lookup + size extraction =="
HF="$TMP/hashes"
printf 'abc123 500 /jpr/2026-07-16/10-00-00.m4a\n' >  "$HF"   # new format
printf 'def456 /jpr/2026-07-16/11-00-00.m4a\n'     >> "$HF"   # legacy (no size)
r="$(_recorded_size "$HF" "/jpr/2026-07-16/10-00-00.m4a")" && [[ "$r" == "500" ]] \
    && ok "new-format entry returns its size (500)" || no "size lookup wrong: '$r'"
r="$(_recorded_size "$HF" "/jpr/2026-07-16/11-00-00.m4a")" && [[ "$r" == "LEGACY" ]] \
    && ok "legacy entry returns LEGACY" || no "legacy lookup wrong: '$r'"
if _recorded_size "$HF" "/jpr/2026-07-16/10-00-00.m4a.m4a" >/dev/null; then
    no "F8a: substring path '.m4a.m4a' wrongly matched"
else
    ok "F8a: '.m4a.m4a' does not substring-match a real path"
fi
_recorded_size "$HF" "/jpr/nope.m4a" >/dev/null && no "absent path wrongly found" \
    || ok "absent path returns not-found (exit 1)"

# --- F7: _with_timeout runs the command (guarded or not) --------------------
echo "== F7 _with_timeout wraps a command and returns its output/status =="
out="$(_with_timeout 5 echo hello)"
[[ "$out" == "hello" ]] && ok "_with_timeout passes through stdout" || no "_with_timeout output wrong: '$out'"
TIMEOUT_BIN="" out2="$(_with_timeout 5 printf 'plain')"
[[ "$out2" == "plain" ]] && ok "runs unguarded when no timeout binary present" || no "unguarded path wrong: '$out2'"

# --- F8c: failure tracking (increment / size-reset / clear) -----------------
echo "== F8c consecutive-failure tracking =="
FF="$TMP/failures"; P="/jpr/x.m4a"
_failure_bump "$FF" "$P" 100
_failure_bump "$FF" "$P" 100
read -r c s <<< "$(_failure_get "$FF" "$P")"
[[ "$c" == "2" && "$s" == "100" ]] && ok "two failures at same size → count 2" || no "count wrong: c=$c s=$s"
_failure_bump "$FF" "$P" 250   # size changed → reset to 1
read -r c s <<< "$(_failure_get "$FF" "$P")"
[[ "$c" == "1" && "$s" == "250" ]] && ok "size change resets the counter to 1" || no "reset wrong: c=$c s=$s"
_failure_clear "$FF" "$P"
read -r c s <<< "$(_failure_get "$FF" "$P")"
[[ "$c" == "0" ]] && ok "clear removes the failure row" || no "clear failed: c=$c"

# --- F2: acquire_lock re-entrancy + stale reclaim + release -----------------
echo "== F2 shared lock: re-entrant, stale-reclaim, release =="
MUSE_LOCK_OWNED_BY_ME="no"; rm -rf "$(_lock_dir)"
acquire_lock wait && [[ "$MUSE_LOCK_OWNED_BY_ME" == "yes" ]] \
    && ok "acquire_lock takes the lock" || no "acquire_lock failed to take the lock"
acquire_lock wait && ok "second acquire is a re-entrant no-op (same process)" || no "re-entrant acquire failed"
release_lock
[[ ! -d "$(_lock_dir)" && "$MUSE_LOCK_OWNED_BY_ME" == "no" ]] \
    && ok "release_lock removes the lockdir + clears ownership" || no "release_lock did not clean up"
# stale reclaim: plant a lockdir owned by a dead pid
mkdir -p "$(_lock_dir)"; echo 999999 > "$(_lock_dir)/pid"
MUSE_LOCK_OWNED_BY_ME="no"
acquire_lock wait && ok "reclaims a lock whose recorded pid is dead" || no "failed to reclaim a dead-pid lock"
release_lock; MUSE_LOCK_OWNED_BY_ME="no"; rm -rf "$(_lock_dir)"

# --- integration: ingest_one dedup + F3 partial-file recovery ---------------
echo "== integration: ingest_one dedup + F3 partial-file re-ingest =="
AUDIO="$MUSE_JPR_DIR/2026-07-16/10-00-00.m4a"
mkdir -p "$(dirname "$AUDIO")"
printf 'AAAA' > "$AUDIO"                       # 4-byte "partial"
ingest_one "$AUDIO" >/dev/null 2>&1; release_lock; MUSE_LOCK_OWNED_BY_ME="no"
n1="$(find "$MUSE_ITEMS_DIR" -maxdepth 1 -name 'MUSE 2026-07-16 *.md' | wc -l | tr -d ' ')"
[[ "$n1" == "1" ]] && ok "first ingest creates one item file" || no "first ingest item count=$n1"
grep -q ' 4 .*10-00-00.m4a$' "$MUSE_ITEMS_DIR/.muse.hashes" \
    && ok "hashfile records the size (4) for the ingested path" || no "hashfile missing size field: $(cat "$MUSE_ITEMS_DIR/.muse.hashes")"
# same file, same size → skipped
ingest_one "$AUDIO" >/dev/null 2>&1; release_lock; MUSE_LOCK_OWNED_BY_ME="no"
n2="$(find "$MUSE_ITEMS_DIR" -maxdepth 1 -name 'MUSE 2026-07-16 *.md' | wc -l | tr -d ' ')"
[[ "$n2" == "1" ]] && ok "re-ingest of the identical file is skipped (still 1 item)" || no "dedup failed: item count=$n2"
# file grows (partial → complete) → re-ingested
printf 'AAAABBBBBBBB' > "$AUDIO"               # size 4 → 12
ingest_one "$AUDIO" >/dev/null 2>&1; release_lock; MUSE_LOCK_OWNED_BY_ME="no"
n3="$(find "$MUSE_ITEMS_DIR" -maxdepth 1 -name 'MUSE 2026-07-16 *.md' | wc -l | tr -d ' ')"
[[ "$n3" == "2" ]] && ok "size change triggers partial-file re-ingest (2 items)" || no "F3 re-ingest failed: item count=$n3"

echo
echo "$PASS passed, $FAIL failed"
[[ "$FAIL" == "0" ]]
