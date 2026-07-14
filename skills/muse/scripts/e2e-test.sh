#!/bin/bash
# muse-e2e-test.sh — end-to-end verification of the MUSE pipeline.
#
# 1. Generates deterministic test audio (`say` → aiff → m4a) with an
#    embedded marker phrase.
# 2. Drops it into the real JPR dir with today's date subfolder.
# 3. Kicks the launchd agent (or invokes muse ingest --sweep directly if
#    --no-launchd is passed).
# 4. Polls (up to 90s) for a MUSE item file whose frontmatter references
#    the test audio path.
# 5. Verifies Quick.md has a new bullet that references the item or marker.
# 6. SOAK (30s): re-verifies the bullet is STILL at the top — catches the
#    "HUD/Obsidian cache write-back nuker" failure mode where an editor's
#    stale in-memory version overwrites muse's prepend.
# 7. On PASS: removes the test audio, item file, hashfile entry, and
#    Quick.md bullet — leaves the vault clean.
# 8. On FAIL: leaves artifacts in place, prints diagnostic dump.
#
# Assumes: `_trust` built + FDA granted; launchd agent installed; _transcribe
# and _askAI in ~/bin/; Homebrew ffmpeg at /opt/homebrew/bin/ffmpeg.

set -euo pipefail

MODE="launchd"        # or "direct"
[[ "${1:-}" == "--no-launchd" ]] && MODE="direct"

STAMP="$(date +%s)"
MARKER="e2etest${STAMP}"
LOG="/tmp/muse-e2e-${STAMP}.log"

TODAY="$(date +%Y-%m-%d)"
JPR_DIR="$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/${TODAY}"
QUICK="$HOME/ob/kmr/LST/Quick.md"
ITEMS_DIR="$HOME/ob/kmr/Log/MUSE"
HASHFILE="$ITEMS_DIR/.muse.hashes"
AGENT="gui/501/com.oblinger.muse-ingest"

exec > >(tee -a "$LOG") 2>&1

log() { printf '[e2e %s] %s\n' "$(date +%H:%M:%S)" "$*"; }
fail() {
    log "FAIL: $*"
    log "--- muse log tail ---"
    tail -25 ~/Library/Logs/muse-ingest.log 2>/dev/null || true
    log "--- Quick.md top 3 ---"
    head -3 "$QUICK" 2>/dev/null || true
    log "--- test artifacts left in place for post-mortem ---"
    log "  test audio:  ${AUDIO_PATH:-(not created)}"
    log "  item file:   ${NEW_ITEM:-(not created)}"
    log "  test log:    $LOG"
    exit 1
}

log "MODE=$MODE MARKER=$MARKER"

# --- prereqs ---
[[ -x /usr/bin/say ]]              || fail "/usr/bin/say missing"
[[ -x /opt/homebrew/bin/ffmpeg ]]  || fail "ffmpeg missing at /opt/homebrew/bin/ffmpeg"
[[ -x "$HOME/bin/_transcribe" ]]   || fail "_transcribe missing"
[[ -x "$HOME/bin/_askAI" ]]        || fail "_askAI missing"
[[ -d "$JPR_DIR" ]] || mkdir -p "$JPR_DIR"

if [[ "$MODE" == "launchd" ]]; then
    [[ -x "$HOME/bin/_trust" ]]    || fail "_trust missing at $HOME/bin/_trust"
    # Verify agent is loaded
    launchctl print "$AGENT" >/dev/null 2>&1 || fail "launchd agent $AGENT not bootstrapped — run install-launchd.sh first"
fi

# --- 1. source test audio ---
# Rather than synthesizing (macOS `say` produces near-empty audio on this
# machine — 0.01s duration regardless of text — probably missing TTS voice
# resources), reuse an already-known-good m4a. Copy an existing JPR file
# whose transcript we've verified into a fresh test path, so muse's
# path-based dedup treats it as a new file.
AUDIO_PATH="${JPR_DIR}/${MARKER}.m4a"
# Pick the smallest already-processed m4a from ANY JPR date subdir as the source.
# (Today's subdir may be empty after midnight rollover; source doesn't need to
# be from today.)
JPR_PARENT="$(dirname "$JPR_DIR")"
SOURCE_AUDIO="$(find "$JPR_PARENT" -maxdepth 2 -type f -iname '*.m4a' ! -name 'e2etest*' -exec stat -f '%z %N' {} \; \
    | grep -v e2etest | sort -n | head -1 | cut -d' ' -f2-)"
[[ -n "$SOURCE_AUDIO" ]] || fail "no source m4a found under $JPR_PARENT — dictate one first"
log "cloning $(basename "$SOURCE_AUDIO") → ${MARKER}.m4a (via ffmpeg with unique metadata to defeat SHA dedup)"
# Re-mux with a unique metadata title. Audio stream is copied (bit-identical
# demux) so whisper still transcribes the same content; container metadata
# differs → SHA differs → muse's SHA dedup treats it as a new file.
/opt/homebrew/bin/ffmpeg -y -i "$SOURCE_AUDIO" -c:a copy -metadata title="e2e-${MARKER}" "$AUDIO_PATH" \
    >/dev/null 2>&1 \
    || fail "ffmpeg metadata-remux failed"
log "audio at: $AUDIO_PATH ($(wc -c < "$AUDIO_PATH") bytes)"

# --- 2. capture Quick.md state ---
QUICK_TOP_BEFORE="$(head -1 "$QUICK" 2>/dev/null || echo '<empty>')"
log "Quick.md top BEFORE: $QUICK_TOP_BEFORE"

# --- 3. trigger ingest ---
if [[ "$MODE" == "launchd" ]]; then
    log "kickstarting launchd agent (routes through _trust muse-sweep)"
    launchctl kickstart -k "$AGENT"
else
    log "invoking muse ingest --sweep directly"
    ~/.claude/skills/muse/scripts/muse ingest --sweep >/dev/null 2>&1 || true
fi

# --- 4. poll for item file (matches by source_audio in frontmatter) ---
log "polling up to 90s for item file..."
NEW_ITEM=""
DEADLINE=$(( $(date +%s) + 90 ))
while (( $(date +%s) < DEADLINE )); do
    NEW_ITEM="$(grep -l --binary-files=text -F -- "source_audio: ${AUDIO_PATH}" "$ITEMS_DIR"/MUSE\ ${TODAY}\ *.md 2>/dev/null | head -1 || true)"
    [[ -n "$NEW_ITEM" ]] && break
    sleep 3
done
[[ -n "$NEW_ITEM" ]] || fail "no item file appeared within 90s referencing $AUDIO_PATH"
log "item file: $(basename "$NEW_ITEM")"

# --- 5. verify Quick.md top bullet is our item (link form) or matches transcript
# (raw-text form). Don't require the string to change vs BEFORE — two independent
# test runs can legitimately produce identical raw-text bullets when they use
# the same source audio; the semantically-important check is that the item's
# CONTENT is at the top.
QUICK_TOP_AFTER="$(head -1 "$QUICK")"
log "Quick.md top AFTER: $QUICK_TOP_AFTER"
ITEM_BASE="$(basename "$NEW_ITEM" .md)"
ITEM_TRANSCRIPT="$(awk '/^---$/{c++; next} c==2 && NF{print; exit}' "$NEW_ITEM" | tr -d '\r')"
if [[ "$QUICK_TOP_AFTER" == *"$ITEM_BASE"* ]]; then
    log "bullet form: link (references $ITEM_BASE) ✓"
elif [[ -n "$ITEM_TRANSCRIPT" ]] && [[ "$QUICK_TOP_AFTER" == *"$ITEM_TRANSCRIPT"* ]]; then
    log "bullet form: raw text (matches transcript) ✓"
else
    fail "Quick.md top ($QUICK_TOP_AFTER) matches neither item basename ($ITEM_BASE) nor its transcript ($ITEM_TRANSCRIPT)"
fi

# --- 6. SOAK: wait 30s and re-verify ---
log "SOAK: waiting 30s to catch external write-back nukers..."
sleep 30
QUICK_TOP_SOAK="$(head -1 "$QUICK")"
if [[ "$QUICK_TOP_SOAK" != "$QUICK_TOP_AFTER" ]]; then
    log "SOAK FAIL: bullet changed during 30s window"
    log "  was:    $QUICK_TOP_AFTER"
    log "  is now: $QUICK_TOP_SOAK"
    log "  disk vs HEAD Quick.md:"
    (cd ~/ob/kmr && git diff --stat HEAD -- LST/Quick.md 2>&1) || true
    fail "external write-back nuker confirmed — bullet was overwritten after successful prepend"
fi
log "SOAK PASS: bullet stable after 30s ✓"

# --- 7. cleanup ---
log "cleaning up test artifacts..."
rm -f "$AUDIO_PATH"
rm -f "$NEW_ITEM"
# Strip the exact bullet line that we verified was at top.
# Pass QUICK_TOP_AFTER via argv (bash 3.2 lacks @Q transformation).
python3 -c '
import sys
from pathlib import Path
target = sys.argv[1]
p = Path(sys.argv[2])
lines = p.read_text().splitlines(keepends=True)
kept, removed = [], False
for l in lines:
    if not removed and l.rstrip("\n") == target:
        removed = True
        continue
    kept.append(l)
p.write_text("".join(kept))
' "$QUICK_TOP_AFTER" "$QUICK"
# Strip hashfile entry
sed -i '' -e "\|${AUDIO_PATH}|d" "$HASHFILE" 2>/dev/null || true

log "PASS — pipeline works end-to-end (item created, bullet stuck, SOAK survived)"
exit 0
