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

# --- T569: the AUDIO decides whether to stop retrying, never a failure count -
# The 38-day MUSE outage was invisible because every run logged `ingested 0 new`
# while 20+ real recordings sat blacklisted by a dead API key. Two separate
# defects produced that, and the second is what these guard.
#
# Reporting (fixed first): a zero with files still failing is a claim about the
# instrument, not the corpus, and the two used to read identically.
#
# Policy (Dan's ruling, 2026-08-20): "We should have a positive way of
# understanding whether or not it's possible to transcribe the audio. And if
# not, we can fail it the first time. And if so, then we just keep trying until
# we can get it." The three-strike blacklist is GONE — not retuned. It counted
# failures, and a failure count is an open-ended reading of the ENVIRONMENT;
# every one of the 20+ lost recordings failed on a cosmetic LLM title call
# AFTER Whisper had already transcribed it, so not one of them was ever a
# failure to transcribe audio. `audio_readable` replaces it with a closed
# reading of the FILE.
echo "== T569 the audio decides — positive readability, not a failure count =="

# 1. The probe reads audio, and BOTH conditions are required. Real fixtures
#    beat synthetic ones here: these two shapes are what the live corpus held.
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
    REAL_FFPROBE="$(command -v ffprobe)"
    GOOD="$TMP/good.m4a"; STUB="$TMP/stub.m4a"; TRUNC="$TMP/trunc.m4a"
    ffmpeg -v error -f lavfi -i "sine=frequency=440:duration=2" -c:a aac "$GOOD" -y 2>/dev/null
    # A container that DECLARES an audio stream but holds no samples — the
    # 646-byte stub in the live corpus, which reports codec_type=audio with
    # duration=N/A. A stream declaration is not audio.
    # Built by REMUXING rather than truncating. A `head -c 646` of a valid file
    # produces something ffprobe rejects outright, which is the easy case and is
    # NOT what the live corpus held: the real 646-byte stub announced
    # `codec_type=audio` with `duration=N/A`, and that shape walked straight
    # past the first version of this probe. The synthetic fixture passed while
    # the real file failed — so the fixture now imitates the file, not the idea.
    ffmpeg -v error -i "$GOOD" -t 0 -c copy "$STUB" -y 2>/dev/null || head -c 646 "$GOOD" > "$STUB"
    # A recording whose moov atom never got flushed (JPR crashed mid-write) —
    # the 76 MB file in the live corpus.
    head -c 4096 "$GOOD" > "$TRUNC"
    FFPROBE_BIN="$REAL_FFPROBE"
    [[ "$(audio_readable "$GOOD")" == readable ]] \
        && ok "real audio with a duration reads READABLE" \
        || no "a valid recording did not read readable — this would be data loss"
    # This is the assertion that failed on the live corpus while its synthetic
    # predecessor passed. `duration=N/A` with a declared audio stream.
    [[ "$(/opt/homebrew/bin/ffprobe -v error -show_entries format=duration -of csv=p=0 "$STUB" 2>/dev/null)" == "N/A" ]] \
        && ok "the stub fixture really does report duration=N/A (it imitates the live file)" \
        || no "the stub fixture is not the shape it is supposed to test"
    [[ "$(audio_readable "$STUB")" == unreadable ]] \
        && ok "a stream declaration with duration=N/A reads UNREADABLE" \
        || no "a sample-less container passed as readable (awk string-compare trap?)"
    [[ "$(audio_readable "$TRUNC")" == unreadable ]] \
        && ok "a truncated capture (no moov atom) reads UNREADABLE" \
        || no "a truncated capture passed as readable"
    # An iCloud placeholder and a truncated capture are INDISTINGUISHABLE to
    # ffprobe — both are "Invalid data found". So a negative reading is only
    # trusted once the bytes are local. Without this guard, every recording that
    # synced slowly would be permanently rejected.
    SPARSE="$TMP/sparse.m4a"
    dd if=/dev/zero of="$SPARSE" bs=1 count=0 seek=10000000 2>/dev/null
    [[ "$(audio_readable "$SPARSE")" == unknown ]] \
        && ok "an unmaterialized (dataless) file reads UNKNOWN, not unreadable" \
        || no "a dataless file was rejected — slow iCloud sync would lose recordings"
    FFPROBE_BIN="/nonexistent-ffprobe"
else
    echo "  SKIP: ffmpeg/ffprobe absent — probe fixtures not built"
fi

# 2. Fail-open is the load-bearing half. A voice recording is the one artifact
#    with no second copy, so anything that is not a POSITIVE reading of broken
#    audio must keep the file alive.
#
#    Setting FFPROBE_BIN alone does NOT test this: audio_readable deliberately
#    falls back to `command -v ffprobe`, so the real binary gets found and the
#    assertion measures nothing. The PATH has to be emptied too. An instrument
#    test that cannot actually remove the instrument is the precise failure
#    this row is about, and it turned up here on the first run.
touch "$TMP/whatever.m4a"
mkdir -p "$TMP/nobin"
[[ "$(PATH="$TMP/nobin"; FFPROBE_BIN="/nonexistent-ffprobe"; audio_readable "$TMP/whatever.m4a")" == unknown ]] \
    && ok "no ffprobe anywhere → UNKNOWN, never unreadable (a missing tool cannot reject)" \
    || no "a verdict was produced with no instrument to produce it"

SRC="$(cat "$MUSE")"
# 3. Both duration comparisons force numeric conversion. Without `+0`, awk
#    compares the STRING "N/A" against "0" and 'N' sorts high, so a durationless
#    container reads as having a valid duration. Two sites, same trap: the
#    readability probe and the WPS suppression predicate. Pinned by count so a
#    third site cannot be added in the broken form.
[[ "$(grep -c 'exit !(d+0 > 0)' "$MUSE")" == "2" ]] \
    && ok "both duration tests use d+0 (numeric), not the string compare" \
    || no "a duration comparison compares strings — 'N/A' > '0' is TRUE in awk"
[[ "$SRC" != *'exit !(d > 0)'* ]] \
    && ok "no bare string-compare duration test survives anywhere" \
    || no "a bare 'd > 0' duration test is still present"

# 4. The count must never gate again. This is the assertion that would have
#    caught the original design, and it is a NEGATIVE one on purpose.
[[ "$SRC" != *"blacklisted=\$((blacklisted + 1))"* ]] \
    && ok "the three-strike blacklist counter is gone, not retuned" \
    || no "a blacklist counter still exists — the failure count still gates"
[[ "$SRC" == *"MUSE_MAX_FAILURES:-0"* ]] \
    && ok "MUSE_MAX_FAILURES defaults to 0 — never stop retrying readable audio" \
    || no "a nonzero default failure cap survives"
[[ "$SRC" == *"_rejected_add \"\$rejfile\""* && "$SRC" == *"unreadable)"* ]] \
    && ok "only an UNREADABLE verdict may write the permanent list" \
    || no "something other than the audio can permanently reject a recording"

# 5. Fail it the FIRST time. Three sweeps re-confirming that a file with no
#    audio in it still has no audio in it is waste, and it delayed the signal.
[[ "$SRC" == *"will not retry unless the file changes"* ]] \
    && ok "an unplayable file is rejected on the first failure and says so" \
    || no "rejection is not reported at the moment it happens"

# 6. The two counts mean OPPOSITE things and must not be reported as one.
#    `retrying` is a live environment fault to act on; `unplayable` is settled.
[[ "$SRC" == *"RETRYING (readable audio, still failing"* ]] \
    && ok "the summary names retrying files as an ENVIRONMENT fault" \
    || no "summary does not distinguish a broken environment from a broken file"
[[ "$SRC" == *"unplayable (no decodable audio; not retried"* ]] \
    && ok "...and names unplayable files separately, as settled" \
    || no "summary conflates unplayable files with retrying ones"

# 7. A repaired file gets a fresh reading. The size is on the rejection row so
#    that repairing a recording — which changes its bytes — readmits it.
[[ "$SRC" == *"_rejected_drop \"\$rejfile\" \"\$candidate\""* ]] \
    && ok "a size change drops the rejection so a repaired file is re-read" \
    || no "a repaired recording could never get back in"

# 8. Every counter shares one `local` with `count`: under `set -u` an undeclared
#    counter aborts the sweep on the first file that touches it, which would
#    turn a reporting change into an outage. This caught exactly that once.
[[ "$SRC" == *"local candidate count=0 found_count=0 rejected=0 retrying=0"* ]] \
    && ok "all counters declared local beside count (set -u safe)" \
    || no "a counter is undeclared — set -u would abort the sweep"

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
