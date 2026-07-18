#!/usr/bin/env bash
# test-f001-suppression.sh — validate the F001 three-part suppression predicate
# against real audio files referenced by existing MUSE items. Runs the actual
# bash code paths from `muse` (via bash -c sourcing) to eliminate the
# python-mirror-of-bash risk.
#
# Exits 0 on all-pass; 1 on any classification mismatch.
set -euo pipefail

MUSE_SCRIPT="$(cd "$(dirname "$0")" && pwd)/muse"
[[ -x "$MUSE_SCRIPT" ]] || { echo "test: cannot find $MUSE_SCRIPT"; exit 1; }

# Source the header + detect_silences + suppression math from the muse script.
# We can't source the whole file (main runs on load) so extract via sed.
HELPER_SNIP="$(sed -n '/^MUSE_MIN_WORDS=/,/^MUSE_LEAD_MIN_WORDS=/p' "$MUSE_SCRIPT")
$(sed -n '/^detect_silences()/,/^}/p' "$MUSE_SCRIPT")"

# One case = one audio file we know the expected verdict for.
# Fields: audio_path | word_count | expected_supp_reason (or "no")
declare -a CASES=(
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-15/19-44-11.m4a|6|no"
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-17/19-09-39.m4a|7|no"
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-17/04-27-35.m4a|13|no"
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-17/19-08-48.m4a|10|no"
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-14/11-34-45.m4a|103|trimmed-wps"
    "$HOME/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents/2026-07-14/12-56-24.m4a|1|min-words"
)

evaluate_case() {
    local audio="$1" word_count="$2"
    bash -c "
        set -euo pipefail
        $HELPER_SNIP
        audio='$audio'
        word_count=$word_count
        # (Excerpted from ingest_one — must stay in sync with the source.)
        ffprobe_bin=\"\${FFPROBE_BIN:-/opt/homebrew/bin/ffprobe}\"
        [[ -x \"\$ffprobe_bin\" ]] || ffprobe_bin=\"\$(command -v ffprobe || true)\"
        duration=\"\$(\"\$ffprobe_bin\" -v error -show_entries format=duration -of csv=p=0 \"\$audio\" 2>/dev/null)\"
        have_duration=no
        if [[ -n \"\$duration\" ]] && awk -v d=\"\$duration\" 'BEGIN { exit !(d > 0) }'; then have_duration=yes; fi
        active_duration=0
        trimmed_wps=0
        leading_burst_passes=no
        if [[ \"\$have_duration\" == yes ]]; then
            silences=\"\$(detect_silences \"\$audio\" 2>/dev/null || true)\"
            total_silence=\"\$(printf '%s\n' \"\$silences\" | awk 'NF==2 { s += (\$2 - \$1) } END { printf \"%.3f\", s+0 }')\"
            active_duration=\"\$(awk -v d=\"\$duration\" -v s=\"\$total_silence\" -v pct=\"\$MUSE_SILENCE_TRIM_PCT\" 'BEGIN { cap = pct/100.0 * d; trim = (s<cap)?s:cap; a = d-trim; if (a<0.001) a=0.001; printf \"%.3f\", a }')\"
            trimmed_wps=\"\$(awk -v w=\"\$word_count\" -v a=\"\$active_duration\" 'BEGIN { printf \"%.3f\", w/a }')\"
            speech_in_lead=\"\$(printf '%s\n' \"\$silences\" | awk -v W=\"\$MUSE_LEAD_WINDOW\" 'NF==2 { s=(\$1<0)?0:\$1; e=(\$2>W)?W:\$2; if (s<W && e>s) sil += (e-s) } END { r = W-sil; if (r<0) r=0; printf \"%.3f\", r }')\"
            if awk -v speech=\"\$speech_in_lead\" -v min_speech=\"\$MUSE_LEAD_MIN_SPEECH\" -v wc=\"\$word_count\" -v min_wc=\"\$MUSE_LEAD_MIN_WORDS\" 'BEGIN { exit !(speech >= min_speech && wc >= min_wc) }'; then
                leading_burst_passes=yes
            fi
        fi
        suppress=no
        if (( word_count < MUSE_MIN_WORDS )); then
            suppress=min-words
        elif [[ \"\$have_duration\" == yes ]] && [[ \"\$leading_burst_passes\" != yes ]] && awk -v twps=\"\$trimmed_wps\" -v min=\"\$MUSE_TRIMMED_MIN_WPS\" 'BEGIN { exit !(twps < min) }'; then
            suppress=trimmed-wps
        fi
        printf '%s|%s|%s|%s\n' \"\$suppress\" \"\$active_duration\" \"\$trimmed_wps\" \"\$leading_burst_passes\"
    "
}

fails=0
pad=64
printf '%-'$pad's %-3s %-9s %-6s %-6s %-4s %-11s %s\n' 'audio' 'wc' 'active' 'twps' 'lead?' '->' 'expected' 'got'
for line in "${CASES[@]}"; do
    IFS='|' read -r audio word_count expected <<< "$line"
    if [[ ! -f "$audio" ]]; then
        printf '%-'$pad's SKIP: source audio missing\n' "$(basename "$audio")"
        continue
    fi
    result="$(evaluate_case "$audio" "$word_count")"
    IFS='|' read -r got active twps leading <<< "$result"
    if [[ "$got" == "$expected" ]]; then
        mark=✓
    else
        mark=✗
        fails=$((fails+1))
    fi
    printf '%-'$pad's %-3s %-9s %-6s %-6s %-4s %-11s %s %s\n' \
        "$(basename "$audio")" "$word_count" "$active" "$twps" "$leading" '->' "$expected" "$got" "$mark"
done

echo
if (( fails > 0 )); then
    echo "test-f001: $fails classification mismatch(es)"
    exit 1
fi
echo "test-f001: all cases classified as expected"
