#!/usr/bin/env bash
# test-route-e2e.sh — the sleep-log route through the REAL pipeline: synthesize
# "Sleep log. I took a quarter Ambien." with `say`, drop it into today's JPR
# folder as a watch recording captured at 03:33:33, run `muse ingest` on it,
# and confirm the words land on tonight's line of MED Sleep Log.md as
# `pill 03:33 I took a quarter Ambien`, while Quick.md's top line is unchanged.
# Cleans every artifact on PASS (audio, item file, hash line, Log Muse bullet,
# the sleep-log part); leaves them for post-mortem on FAIL.
#
# Assumes: whisper via ~/bin/_transcribe, Homebrew ffmpeg, `say` producing real
# audio (it does since 2026-09-04 — the e2e-test.sh note about empty output is
# stale on this machine).

set -uo pipefail

TODAY="$(date +%Y-%m-%d)"
JPR_DIR="$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/$TODAY"
ITEMS_DIR="$HOME/ob/kmr/Log/MUSE"
HASHFILE="$ITEMS_DIR/.muse.hashes"
LOG_MUSE="$ITEMS_DIR/Log Muse.md"
QUICK="$HOME/ob/kmr/LST/Quick.md"
SLEEP_LOG="$HOME/ob/kmr/Topic/MED/MED Sleep/MED Sleep Log.md"
AUDIO="$JPR_DIR/03-33-33.m4a"          # captured 03:33:33 → tonight's line, `pill 03:33 …`
PART="pill 03:33 I took a quarter Ambien"
MUSE="$(cd "$(dirname "$0")" && pwd)/muse"

log() { printf '[route-e2e %s] %s\n' "$(date +%H:%M:%S)" "$*"; }
fail() { log "FAIL: $*"; log "artifacts left in place: $AUDIO, item under $ITEMS_DIR, line in $SLEEP_LOG"; exit 1; }

[[ -x /usr/bin/say ]] || fail "say missing"
[[ -x /opt/homebrew/bin/ffmpeg ]] || fail "ffmpeg missing"
[[ -x "$HOME/bin/_transcribe" ]] || fail "_transcribe missing"
[[ ! -e "$AUDIO" ]] || fail "$AUDIO already exists — a real recording at that second? refusing"
grep -qF -- "$PART" "$SLEEP_LOG" && fail "sleep log already carries '$PART' — clean up first"
mkdir -p "$JPR_DIR"

TMP="$(mktemp -d)"
say -v Samantha -o "$TMP/say.aiff" "Sleep log, I took a quarter Ambien" || fail "say failed"
/opt/homebrew/bin/ffmpeg -y -loglevel error -i "$TMP/say.aiff" -c:a aac "$AUDIO" || fail "ffmpeg failed"
rm -rf "$TMP"
log "audio at $AUDIO ($(wc -c < "$AUDIO") bytes)"

QUICK_TOP_BEFORE="$(head -1 "$QUICK")"
log "running muse ingest (the launchd sweep may beat us to it; either way one ingest happens)"
"$MUSE" ingest "$AUDIO" >/dev/null 2>&1 || true

log "polling up to 90s for the sleep-log line"
DEADLINE=$(( $(date +%s) + 90 ))
while (( $(date +%s) < DEADLINE )); do
    grep -qF -- "$PART" "$SLEEP_LOG" && break
    sleep 3
done
grep -qF -- "$PART" "$SLEEP_LOG" || fail "'$PART' never appeared in $SLEEP_LOG"
LINE="$(grep -F -- "$PART" "$SLEEP_LOG")"
# 03:33 is before noon, so the night is labelled by the evening before it — yesterday
NIGHT="$(date -v-1d +%Y-%m-%d)"
[[ "$LINE" == "- $NIGHT · "* ]] && log "sleep log: $LINE ✓" || fail "landed on the wrong night (want $NIGHT): $LINE"

ITEM="$(grep -l --binary-files=text -F -- "source_audio: $AUDIO" "$ITEMS_DIR"/MUSE\ "$TODAY"\ *.md 2>/dev/null | head -1)"
[[ -n "$ITEM" ]] || fail "no item file references $AUDIO"
grep -q '^state: routed$' "$ITEM" && grep -q '^routed_to: sleep-diary$' "$ITEM" \
    && log "item $(basename "$ITEM"): state routed → sleep-diary ✓" \
    || fail "item frontmatter not routed: $(head -6 "$ITEM")"
[[ "$(head -1 "$QUICK")" == "$QUICK_TOP_BEFORE" ]] && log "Quick.md top line unchanged ✓" || fail "Quick.md changed: $(head -1 "$QUICK")"
grep -qF -- "$(basename "$ITEM" .md | sed 's/ /%20/g').md) → sleep-diary" "$LOG_MUSE" \
    && log "Log Muse bullet carries → sleep-diary ✓" || fail "Log Muse bullet missing the arrow"

log "cleaning up"
rm -f "$AUDIO" "$ITEM"
sed -i '' -e "\|$AUDIO|d" "$HASHFILE"
python3 - "$LOG_MUSE" "$(basename "$ITEM" .md | sed 's/ /%20/g').md" "$SLEEP_LOG" "$PART" <<'EOF'
import sys, re
from pathlib import Path
log_muse, href, sleep_log, part = sys.argv[1:]
p = Path(log_muse)
p.write_text("".join(l for l in p.read_text().splitlines(keepends=True) if href not in l))
p = Path(sleep_log)
out = []
for l in p.read_text().splitlines(keepends=True):
    if part in l:
        parts = [x for x in re.split(r"\s+·\s+", l.rstrip("\n")) if x != part]
        if len(parts) <= 1:          # `- YYYY-MM-DD` alone → the line was only the test
            continue
        l = " · ".join(parts) + "\n"
    out.append(l)
p.write_text("".join(out).rstrip("\n") + "\n")
EOF
grep -qF -- "$PART" "$SLEEP_LOG" && fail "cleanup left the part behind"
log "PASS — a watch memo addressed to the sleep log lands on tonight's line at its capture time"
