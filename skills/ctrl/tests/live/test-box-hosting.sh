#!/usr/bin/env bash
# test-box-hosting.sh — `ctrl box` hosting: --in / --standalone / the
# primary_session default (MUX T323).
#
# Every case is a REAL round trip through tmux: create the box, run a command
# with a nonce in it, and read the nonce back out with `ctrl outbox`. A box
# that is created but never actually written to would pass a "does the window
# exist" check and fail this one.
#
# Uses scratch host sessions only — never the user's live primary_session.
# Exit 0 PASS / 1 FAIL.

set -uo pipefail
CTRL="${CTRL:-$HOME/bin/ctrl}"
HOST="ctrlboxtest-host-$$"
DEAD="ctrlboxtest-dead-$$"
BOX="ctrlboxtest-box-$$"
fails=0

cleanup() {
    tmux kill-session -t "=$HOST" 2>/dev/null
    tmux kill-session -t "=$BOX"  2>/dev/null
    tmux kill-session -t "=${HOST}extra" 2>/dev/null
}
trap cleanup EXIT

ok()   { echo "  PASS  $1"; }
bad()  { echo "  FAIL  $1"; fails=$((fails+1)); }
nonce(){ echo "NONCE${RANDOM}${RANDOM}"; }

echo "== 1. --standalone creates a session, not a window =="
n=$(nonce)
"$CTRL" box --session "$BOX" --standalone "echo $n" >/dev/null 2>&1
sleep 1
if tmux has-session -t "=$BOX" 2>/dev/null; then ok "standalone session exists"
else bad "standalone session missing"; fi
if "$CTRL" outbox --session "$BOX" --standalone 40 2>/dev/null | grep -q "^$n$"; then
    ok "standalone round trip"
else bad "standalone round trip — nonce $n never came back"; fi

echo "== 2. --in hosts the box as a WINDOW in the named session =="
tmux new-session -d -s "$HOST"
# The host's own original window — NOT another ctrl box, which would legitimately
# carry the declaration and make the no-leak check below vacuously fail.
ORIGWIN=$(tmux list-windows -t "=$HOST" -F '#{window_id}' | head -1)
n=$(nonce)
"$CTRL" box --session "$BOX" --in "$HOST" "echo $n" >/dev/null 2>&1
sleep 1
if tmux list-windows -t "=$HOST" -F '#{window_name}' | grep -qx "$BOX"; then
    ok "hosted window exists in $HOST"
else bad "hosted window missing from $HOST"; fi
if "$CTRL" outbox --session "$BOX" --in "$HOST" 40 2>/dev/null | grep -q "^$n$"; then
    ok "hosted round trip"
else bad "hosted round trip — nonce $n never came back"; fi

echo "== 3. the hosted window KEEPS its name while a command runs =="
# automatic-rename is on globally; without the explicit pin the shell renames
# the window to whatever it is running and the =host:=name target dies.
"$CTRL" box --session "$BOX" --in "$HOST" "sleep 8" >/dev/null 2>&1
sleep 1.5
if tmux list-windows -t "=$HOST" -F '#{window_name}' | grep -qx "$BOX"; then
    ok "name pinned under a running command"
else bad "window was auto-renamed — target =$HOST:=$BOX no longer resolves"; fi

echo "== 4. the T586 occupant guard fires on the HOSTED target =="
# `sleep` from case 3 is still the foreground command.
if "$CTRL" box --session "$BOX" --in "$HOST" "echo should-not-run" >/dev/null 2>&1; then
    bad "occupant guard did not refuse a busy hosted pane"
else ok "occupant guard refused a busy hosted pane"; fi
sleep 8

echo "== 5. an explicit --in naming a dead session FAILS, never falls back =="
tmux kill-session -t "=$DEAD" 2>/dev/null
n=$(nonce)
if "$CTRL" box --session "$BOX" --in "$DEAD" "echo $n" >/dev/null 2>&1; then
    bad "--in on a dead session succeeded (should exit non-zero)"
else ok "--in on a dead session refused"; fi
if tmux has-session -t "=$DEAD" 2>/dev/null; then
    bad "--in on a dead session CREATED it"
else ok "--in on a dead session created nothing"; fi

echo "== 6. targets are exact-matched, not prefix-matched =="
# A bare tmux target prefix-matches, so a box named for a prefix of a live
# session would silently hijack it.
tmux new-session -d -s "${HOST}extra" 2>/dev/null
if tmux has-session -t "=${HOST}" 2>/dev/null && \
   ! tmux has-session -t "=${HOST}ex" 2>/dev/null; then
    ok "= prefix gives exact session matching"
else bad "exact matching broken"; fi

echo "== 7. the primary_session DEFAULT hosts the box, with no --in =="
# Drives the whole default path through the `~/bin/ctrl` SYMLINK, which is how
# it is actually invoked. That matters: the accessor is located relative to the
# script, and `abspath(__file__)` does not follow symlinks — it resolved to
# `~/anchor-system/scripts/` and the fail-soft reported "no primary_session" on
# a machine that had one. A unit test run from the source dir cannot see this.
ENVDOC="${TMPDIR:-/tmp}/ctrlboxtest-userenv-$$.md"
printf '# User Environment\n\n## tmux\n\n```yaml\nprimary_session: %s\n```\n' "$HOST" > "$ENVDOC"
export ANCHOR_SYSTEM_USER_ENV_DOC="$ENVDOC"
BOX2="${BOX}-dflt"
n=$(nonce)
"$CTRL" box --session "$BOX2" "echo $n" >/dev/null 2>&1
sleep 1
if tmux list-windows -t "=$HOST" -F '#{window_name}' | grep -qx "$BOX2"; then
    ok "default hosted the box in primary_session"
else bad "default did NOT host the box — primary_session was not resolved"; fi
if "$CTRL" outbox --session "$BOX2" 40 2>/dev/null | grep -q "^$n$"; then
    ok "default round trip"
else bad "default round trip — nonce $n never came back"; fi

echo "== 8. a primary_session that is not live falls back to standalone =="
printf '# User Environment\n\n## tmux\n\n```yaml\nprimary_session: %s\n```\n' "$DEAD" > "$ENVDOC"
BOX3="${BOX}-fallback"
n=$(nonce)
err=$("$CTRL" box --session "$BOX3" "echo $n" 2>&1 >/dev/null)
sleep 1
if tmux has-session -t "=$BOX3" 2>/dev/null; then ok "fell back to a standalone box"
else bad "no standalone box after fallback"; fi
if echo "$err" | grep -q "not live"; then ok "fallback was announced on stderr"
else bad "fallback was SILENT — stderr said: $err"; fi
tmux kill-session -t "=$BOX3" 2>/dev/null
unset ANCHOR_SYSTEM_USER_ENV_DOC
rm -f "$ENVDOC"

echo "== 9. a NEW hosted box is created even when the host's current window is busy =="
# `display-message` on a not-yet-existing hosted target silently resolves to
# the host session's CURRENT window instead of failing. Probing the occupant
# before creating the box therefore reads an unrelated pane — and in a real
# MuxUX frame that pane is a `claude` agent, so every first box was refused.
BOX4="${BOX}-fresh"
tmux send-keys -t "=$HOST:=$BOX" 'sleep 12' Enter    # make the host's current window busy
tmux select-window -t "=$HOST:=$BOX"
sleep 1
n=$(nonce)
"$CTRL" box --session "$BOX4" --in "$HOST" "echo $n" >/dev/null 2>&1
sleep 1.5
if "$CTRL" outbox --session "$BOX4" --in "$HOST" 40 2>/dev/null | grep -q "^$n$"; then
    ok "fresh hosted box created and written to past a busy sibling window"
else bad "fresh hosted box refused/failed — occupant probed the wrong pane"; fi
sleep 11

echo "== 10. a box DECLARES itself a console via @muxux-kind =="
# MuxUX classifies by sniffing pane_current_command, and claude's argv0 is a
# bare version string — so any pane that has run claude is captured as an
# agent and relaunched as one. A box is a shell; the option says so. Same
# declared-not-sniffed shape as F160's bridge re-stamp.
BOX5="${BOX}-decl"
"$CTRL" box --session "$BOX5" --in "$HOST" "true" >/dev/null 2>&1
sleep 1
if [ "$(tmux show-options -w -v -t "=$HOST:=$BOX5" @muxux-kind 2>/dev/null)" = "console" ]; then
    ok "hosted box declares @muxux-kind=console"
else bad "hosted box carries no @muxux-kind declaration"; fi
# and it must be visible in a -F format, which is how a capture would read it
if [ "$(tmux list-panes -t "=$HOST:=$BOX5" -F '#{@muxux-kind}' 2>/dev/null | head -1)" = "console" ]; then
    ok "declaration is readable from a list-panes format"
else bad "declaration not readable from a format string"; fi
# a sibling window must NOT inherit it
if [ -z "$(tmux list-panes -t "=$HOST:$ORIGWIN" -F '#{@muxux-kind}' 2>/dev/null | head -1)" ]; then
    ok "declaration does not leak to sibling windows"
else bad "declaration leaked to a sibling window"; fi

BOX6="${BOX}-decl-alone"
"$CTRL" box --session "$BOX6" --standalone "true" >/dev/null 2>&1
sleep 1
if [ "$(tmux show-options -v -t "=$BOX6:" @muxux-kind 2>/dev/null)" = "console" ]; then
    ok "standalone box declares @muxux-kind=console at session scope"
else bad "standalone box carries no session-scope declaration"; fi
tmux kill-session -t "=$BOX6" 2>/dev/null

echo "== 11. per-agent derivation: box-<SLUG> from the nearest .anchor (T598) =="
WORK=$(mktemp -d)
printf 'slug: CTRLTEST%s\n' "$$" > "$WORK/.anchor"
DBOX="box-CTRLTEST$$"
n=$(nonce)
( cd "$WORK" && "$CTRL" box --standalone "echo $n" >/dev/null 2>&1 )
sleep 1
if tmux has-session -t "=$DBOX" 2>/dev/null; then ok "derived session $DBOX exists"
else bad "derived session $DBOX missing"; fi
if ( cd "$WORK" && "$CTRL" outbox --standalone 40 2>/dev/null ) | grep -q "^$n$"; then
    ok "derived round trip through the same derivation"
else bad "derived round trip — nonce $n never came back"; fi

echo "== 12. --session still overrides the derivation =="
n=$(nonce)
( cd "$WORK" && "$CTRL" box --session "$BOX" --standalone "echo $n" >/dev/null 2>&1 )
sleep 1
if "$CTRL" outbox --session "$BOX" --standalone 40 2>/dev/null | grep -q "^$n$"; then
    ok "--session override lands in the named box"
else bad "--session override — nonce $n never came back"; fi
if "$CTRL" outbox --session "$DBOX" --standalone 40 2>/dev/null | grep -q "^$n$"; then
    bad "override leaked into the derived box"
else ok "derived box did not receive the overridden command"; fi
tmux kill-session -t "=$DBOX" 2>/dev/null
rm -rf "$WORK"

echo
if [ "$fails" -eq 0 ]; then echo "PASS — box hosting"; exit 0; fi
echo "FAIL — $fails check(s)"; exit 1
