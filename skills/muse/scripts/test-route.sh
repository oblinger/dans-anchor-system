#!/usr/bin/env bash
# test-route.sh — step 3.5 address routing (Dan, 2026-09-04). A memo that opens
# by naming its destination ("sleep log, …") is filed by that destination's own
# script at its CAPTURE time and skips the title call, Quick and Sparks; every
# other memo is untouched; a crashing handler never loses a memo; a suppressed
# memo is never offered; an empty handler list is legal under `set -u`.
#
# Sources the muse functions with a fake HOME-less env + stub binaries (the
# f252 harness pattern) — never touches the real vault, JPR dir or Sparks.

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
export MUSE_STATE_CLI="$TMP/state"          # records drops; never reaches Sparks
export FFPROBE_BIN="/nonexistent-ffprobe"
# audio_readable falls back to `command -v ffprobe`; with Homebrew off PATH the
# reading is `unknown` and the fake bytes pass through to the transcriber stub.
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"
mkdir -p "$MUSE_ITEMS_DIR" "$MUSE_JPR_DIR/2026-09-04"
: > "$MUSE_QUICK_FILE"

cat > "$TMP/_transcribe" <<EOF
#!/usr/bin/env bash
cat "$TMP/transcript"
EOF
cat > "$TMP/_askAI" <<EOF
#!/usr/bin/env bash
echo called >> "$TMP/askai-calls"
echo "LLM Title"
EOF
cat > "$TMP/state" <<EOF
#!/usr/bin/env bash
echo "\$*" >> "$TMP/drops"
EOF
# The handler contract: `<handler> voice --captured <stamp> <text>`,
# exit 0 = filed, 3 = not mine, anything else = failed.
cat > "$TMP/handler" <<EOF
#!/usr/bin/env bash
[[ -e "$TMP/handler-crash" ]] && exit 1
printf '%s|%s\n' "\$3" "\$4" >> "$TMP/filed"
shopt -s nocasematch
[[ "\$4" == sleep\ log* ]] && exit 0
exit 3
EOF
chmod +x "$TMP/_transcribe" "$TMP/_askAI" "$TMP/state" "$TMP/handler"
export TRANSCRIBE_BIN="$TMP/_transcribe"
export ASKAI_BIN="$TMP/_askAI"

# shellcheck disable=SC1090
source "$MUSE"
set +e +o pipefail
MUSE_ROUTE_HANDLERS=("$TMP/handler")

mk_audio() {  # <HH-MM-SS> — distinct bytes per file so SHAs differ
    local p="$MUSE_JPR_DIR/2026-09-04/$1.m4a"
    printf 'fake-audio-%s-%s%s' "$1" "$RANDOM" "$RANDOM" > "$p"
    printf '%s' "$p"
}
run_one() { ingest_one "$1" >/dev/null 2>&1; release_lock; MUSE_LOCK_OWNED_BY_ME="no"; }

echo "== routed memo =="
printf 'Sleep log. I took a quarter Ambien.' > "$TMP/transcript"
run_one "$(mk_audio 02-14-33)"
grep -q '^2026-09-04 02:14:33|Sleep log. I took a quarter Ambien.$' "$TMP/filed" 2>/dev/null \
    && ok "handler called with the capture time and the transcript" \
    || no "handler call: $(cat "$TMP/filed" 2>/dev/null)"
item="$(ls "$MUSE_ITEMS_DIR"/MUSE*.md 2>/dev/null | head -1)"
if [[ -n "$item" ]] && grep -q '^state: routed$' "$item" && grep -q '^routed_to: handler$' "$item"; then
    ok "item frontmatter: state routed, routed_to handler"
else
    no "frontmatter: $(head -8 "$item" 2>/dev/null)"
fi
grep -q '^title_source: routed$' "$item" && ok "title is transcript-derived" || no "title_source: $(grep title_source "$item")"
[[ ! -s "$MUSE_QUICK_FILE" ]] && ok "Quick untouched" || no "Quick got: $(cat "$MUSE_QUICK_FILE")"
[[ ! -e "$TMP/drops" ]] && ok "no Sparks drop" || no "Sparks drop: $(cat "$TMP/drops")"
[[ ! -e "$TMP/askai-calls" ]] && ok "no LLM title call" || no "askAI was called"
grep -q ' → handler$' "$MUSE_LOG_FILE" && ok "Log Muse bullet carries → handler" || no "log: $(cat "$MUSE_LOG_FILE")"

echo "== unaddressed memo takes the normal path =="
printf 'Hey Lumen remind me tomorrow to buy a mattress' > "$TMP/transcript"
run_one "$(mk_audio 09-00-00)"
grep -q 'Lumen' "$MUSE_QUICK_FILE" && ok "Quick bullet written" || no "Quick missing the bullet"
grep -q 'drop Sparks' "$TMP/drops" 2>/dev/null && ok "Sparks drop made" || no "no Sparks drop"
item="$(grep -l 'Lumen' "$MUSE_ITEMS_DIR"/MUSE*.md)"
grep -q '^state: unreviewed$' "$item" && ok "state unreviewed" || no "state: $(grep state: "$item")"
[[ -e "$TMP/askai-calls" ]] && ok "LLM title called" || no "no title call"
grep -q '^2026-09-04 09:00:00|Hey Lumen' "$TMP/filed" && ok "handler was offered it and declined (rc 3)" || no "handler not offered"

echo "== crashing handler never loses a memo =="
touch "$TMP/handler-crash"; rm -f "$TMP/drops"
printf 'Sleep log. melatonin at eleven tonight.' > "$TMP/transcript"
run_one "$(mk_audio 23-11-00)"
grep -q 'melatonin' "$MUSE_QUICK_FILE" && ok "fell through to Quick" || no "Quick lacks it"
[[ -e "$TMP/drops" ]] && ok "fell through to Sparks" || no "no Sparks drop"
item="$(grep -l 'melatonin' "$MUSE_ITEMS_DIR"/MUSE*.md)"
grep -q '^state: unreviewed$' "$item" && ok "state unreviewed, not routed" || no "state: $(grep state: "$item")"
rm -f "$TMP/handler-crash"

echo "== suppressed memo is never offered =="
: > "$TMP/filed"
printf 'Sleep log.' > "$TMP/transcript"      # 2 words < MUSE_MIN_WORDS
run_one "$(mk_audio 03-00-00)"
[[ ! -s "$TMP/filed" ]] && ok "handler not called for a suppressed memo" || no "handler called: $(cat "$TMP/filed")"

echo "== empty handler list is legal under set -u =="
MUSE_ROUTE_HANDLERS=()
rm -f "$TMP/drops"
printf 'Sleep log. quarter ambien again tonight' > "$TMP/transcript"
run_one "$(mk_audio 04-00-00)"
grep -q 'ambien again' "$MUSE_QUICK_FILE" && [[ -e "$TMP/drops" ]] \
    && ok "no handlers → normal path" || no "empty handler list broke ingest"

echo
echo "PASS=$PASS FAIL=$FAIL"
[[ $FAIL -eq 0 ]]
