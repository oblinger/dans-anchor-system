#!/usr/bin/env bash
# screen-check.sh — bridge screen-vision + FDA self-test (F224).
#
# Verifies the remote's canonical tmux server carries GUI-session context by
# running probes INSIDE that server (not over bare SSH — bare SSH always
# lacks the window server, so probing there proves nothing):
#   fda    — read the TCC dir (Full Disk Access)
#   screen — a real screencapture grab (window-server + Screen Recording)
# PASS/FAIL per capability with remediation. Cheap (~3s) — run at setup and
# at each (re)connect (bridge-test.sh invokes it as T-ctl-screen).
#
# Usage: screen-check.sh <host> [session]   (session default: work)

set -u
HOST="${1:-}"
SESSION="${2:-work}"
USER_R="oblinger"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
[ -z "$HOST" ] && { echo "usage: screen-check.sh <host> [session]"; exit 2; }

FAILED=0
rec() { printf '  %-5s %-7s %s\n' "$1" "$2" "$3"; [ "$1" = FAIL ] && FAILED=1; }

echo "== bridge screen-check against $HOST (session: $SESSION) =="

# reach
if ! $SSH "$USER_R@$HOST" hostname >/dev/null 2>&1; then
  rec FAIL reach "remote $HOST unreachable over ssh"
  echo "== screen-check: FAIL =="
  exit 2
fi
rec PASS reach "ssh key-auth OK"

# macOS only — the GUI/TCC model this tests is Darwin's
OS=$($SSH "$USER_R@$HOST" uname 2>/dev/null)
if [ "$OS" != "Darwin" ]; then
  rec SKIP screen "remote is $OS — macOS GUI/TCC checks don't apply"
  echo "== screen-check: PASS (non-macOS) =="
  exit 0
fi

# canonical mux session present
if ! $SSH "$USER_R@$HOST" "tmux has-session -t $SESSION" >/dev/null 2>&1; then
  rec FAIL mux "no tmux session '$SESSION' — start it from Terminal.app ON THE REMOTE (bridge Step 5; never over ssh)"
  echo "== screen-check: FAIL =="
  exit 1
fi
rec PASS mux "canonical session '$SESSION' present"

# probes run inside the mux server; results land as marker files
$SSH "$USER_R@$HOST" "rm -f /tmp/bsc.png /tmp/bsc.err /tmp/bsc.fda; \
  tmux new-window -t $SESSION -d 'ls \"/Library/Application Support/com.apple.TCC\" >/dev/null 2>&1 && touch /tmp/bsc.fda; \
  screencapture -x /tmp/bsc.png 2>/tmp/bsc.err'" 2>/dev/null
sleep 3

# fda — TCC dir is unreadable without Full Disk Access
if $SSH "$USER_R@$HOST" "[ -f /tmp/bsc.fda ]" 2>/dev/null; then
  rec PASS fda "TCC dir readable from mux server (Full Disk Access)"
else
  rec FAIL fda "no FDA in the mux server — grant Full Disk Access to Terminal (Step 5b), or the server was SSH-launched (redo Step 5), then quit & reopen Terminal"
fi

# screen — a real grab is >20KB; failure writes nothing (or an error)
SIZE=$($SSH "$USER_R@$HOST" "stat -f%z /tmp/bsc.png 2>/dev/null" 2>/dev/null)
if [ -n "${SIZE:-}" ] && [ "$SIZE" -gt 20000 ] 2>/dev/null; then
  rec PASS screen "grab OK (${SIZE} bytes) — window-server + Screen Recording present"
else
  ERR=$($SSH "$USER_R@$HOST" "cat /tmp/bsc.err 2>/dev/null" 2>/dev/null | head -1)
  rec FAIL screen "grab failed${ERR:+ ($ERR)} — SSH-launched server or Screen Recording not granted: redo Step 5 (Terminal-launch) + Step 5b (grant Screen Recording to Terminal), then quit & reopen Terminal"
fi

$SSH "$USER_R@$HOST" "rm -f /tmp/bsc.png /tmp/bsc.err /tmp/bsc.fda" 2>/dev/null

if [ "$FAILED" -eq 0 ]; then echo "== screen-check: PASS =="; exit 0
else echo "== screen-check: FAIL =="; exit 1; fi
