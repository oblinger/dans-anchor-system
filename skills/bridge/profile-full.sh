#!/usr/bin/env bash
# profile-full.sh — the `full` capability profile for bridge doctor / install (F027 stage 2).
#
# Sourced by the bridge dispatcher when --profile full is set. Reads ambient
# globals set by `resolve_target` in the bridge script:
#   SSH        — bash array; the ssh command with ControlMaster socket
#   SESSION    — the remote tmux session name (bridge-<host>)
#   TARGET     — resolved hostname (with .local)
#
# Every capability declares:
#   cap_desc_<id>       one-line summary of what it enables
#   cap_probe_<id>      verify it works INSIDE the canonical mux server
#                       returns 0 = PASS, non-zero = FAIL
#   cap_install_<id>    attempt automatic install/repair; returns
#                       0 = auto-fixed (walker re-probes),
#                       1 = printed guidance (user action needed),
#                       2 = informational only (no fix, don't count as FAIL)
#   cap_repair_<id>     one-line hint printed under a FAIL row in doctor mode
#
# Rows covered in stage 2 (7): aqua, screen, playwright, safari-ae, clipboard,
# notification, audio. Added stage 3: agent-window.
#
# The stage-2 header said agent-window "requires shared-browser claim design".
# That was wrong, and it is why the row sat deferred for a month after the
# mechanism it probes had already shipped. The convention landed under T171 --
# `bridge tmux --agent SLUG` refuses without an agent identity, creates
# `agent-SLUG`, and runs an occupancy preflight. The probe asks only whether
# the session carries such a window; the browser lease is a SEPARATE, still-open
# design question about a different shared resource. Bundling an unbuilt design
# with a shipped one kept a working check off the board.
#
# Still deferred to stage 3: utm (Windows VM, user-prompted), the shared-browser
# claim/lease, and two live defects in the shipped convention -- case-sensitive
# slugs (`agent-atticus` and `agent-Atticus` coexist for one agent) and no reaper
# for dead agent windows. Those two need a design call; see the F027 backlog Next.

CAPS_FULL_IDS=(aqua screen playwright safari-ae clipboard notification audio agent-window)

# ---------------------------------------------------------------- helpers

# Run BODY inside the mux server via a detached tmux new-window; write a
# marker file on success; wait; return 0 iff marker present. Used for probes
# that require Aqua/TCC context.
#   $1 id      — used to name the marker file
#   $2 body    — shell body; must include `&& touch <marker>` (helper adds it)
#   $3 wait    — seconds to sleep before checking marker (default 3)
_run_in_mux() {
  local id="$1" body="$2" wait="${3:-3}"
  local marker="/tmp/bridge-cap-$id.ok"
  "${SSH[@]}" "rm -f $marker; tmux new-window -t $SESSION -d $(printf '%q' "$body && touch $marker")" 2>/dev/null
  sleep "$wait"
  "${SSH[@]}" "[ -f $marker ]" 2>/dev/null
}

_clean_marker() {
  "${SSH[@]}" "rm -f /tmp/bridge-cap-$1.ok" 2>/dev/null
}

# ---------------------------------------------------------------- aqua

cap_desc_aqua()   { echo "GUI/Aqua launch context — foundation for every TCC-bearing probe below"; }
cap_repair_aqua() { echo "redo 'bridge tmux <host>' so the server is Terminal-launched, then grant TCC per SKILL.md Step 5b"; }

cap_probe_aqua() {
  _run_in_mux aqua 'osascript -e "tell application \"System Events\" to name of first process" >/dev/null 2>&1' 2
  local rc=$?; _clean_marker aqua; return $rc
}

cap_install_aqua() {
  echo "    guidance: $(cap_repair_aqua)"
  return 1
}

# ---------------------------------------------------------------- screen

cap_desc_screen()   { echo "Screen capture — screencapture, screen.py grab, screen-vision workflows"; }
cap_repair_screen() { echo "grant Screen Recording to Terminal.app in remote's Privacy & Security, then quit+reopen Terminal"; }

cap_probe_screen() {
  _run_in_mux screen 'screencapture -x /tmp/bridge-cap-screen.png 2>/dev/null && [ -s /tmp/bridge-cap-screen.png ] && [ $(stat -f%z /tmp/bridge-cap-screen.png) -gt 20000 ]' 3
  local rc=$?
  "${SSH[@]}" "rm -f /tmp/bridge-cap-screen.png" 2>/dev/null
  _clean_marker screen; return $rc
}

cap_install_screen() {
  echo "    guidance: $(cap_repair_screen)"
  return 1
}

# ---------------------------------------------------------------- playwright

cap_desc_playwright()   { echo "Browser automation (Playwright + Chromium) — ctrl cpage, headless JS-heavy fetches"; }
cap_repair_playwright() { echo "pip install --user playwright && python3 -m playwright install chromium"; }

# Probe Playwright directly, NOT through `ctrl cpage` (corrected 2026-08-08, F027).
# The original probe ran `ctrl cpage --url about:blank`, which could never pass:
# `cpage` takes the url POSITIONALLY (there is no --url flag), and it rejects
# `about:` anyway -- it accepts only http(s) or a tab number. So the row reported
# FAIL on haorui while Playwright and Chromium were installed and working, and the
# repair action reinstalled ~200 MB of Chromium on every run to fix nothing.
# Launching chromium through the Playwright API proves the actual capability and
# needs no network. The command uses double quotes ONLY -- no single quote may
# appear in it, because it is carried inside a single-quoted argument through the
# ssh -> printf %q -> tmux new-window chain, and one apostrophe would end that
# argument early and split the command. Keep it that way when editing.
cap_probe_playwright() {
  _run_in_mux playwright 'python3 -c "import playwright.sync_api as s; p=s.sync_playwright().start(); b=p.chromium.launch(); print(b.version); b.close(); p.stop()" >/dev/null 2>&1' 25
  local rc=$?
  _clean_marker playwright; return $rc
}

cap_install_playwright() {
  echo "    action: pip install playwright + playwright install chromium (~200 MB)"
  "${SSH[@]}" "zsh -lc 'python3 -m pip install --user --quiet playwright' 2>&1 | tail -3" || return 1
  # Chromium download runs inside the mux server so it uses the same GUI-blessed
  # context that ctrl cpage will later; can take a minute or two.
  local marker="/tmp/bridge-cap-pw-install.ok"
  "${SSH[@]}" "rm -f $marker; tmux new-window -t $SESSION -d $(printf '%q' "zsh -lc 'python3 -m playwright install chromium >/tmp/bridge-cap-pw-install.log 2>&1 && touch $marker'")" 2>/dev/null
  local waited=0
  while [ $waited -lt 180 ]; do
    "${SSH[@]}" "[ -f $marker ]" 2>/dev/null && break
    sleep 5; waited=$((waited+5))
  done
  "${SSH[@]}" "[ -f $marker ]" 2>/dev/null
  local rc=$?
  "${SSH[@]}" "rm -f $marker" 2>/dev/null
  return $rc
}

# ---------------------------------------------------------------- safari-ae

cap_desc_safari-ae()   { echo "Safari AppleEvents (JS-from-AE + Develop menu) — ctrl jpage, real-Safari fetches"; }
cap_repair_safari-ae() { echo "defaults write com.apple.Safari AllowJavaScriptFromAppleEvents / IncludeDevelopMenu -bool true; relaunch Safari"; }

cap_probe_safari-ae() {
  # defaults read works over bare SSH — no Aqua context required for user prefs
  local ae dev
  ae=$("${SSH[@]}" "defaults read com.apple.Safari AllowJavaScriptFromAppleEvents 2>/dev/null" | tr -d '[:space:]')
  dev=$("${SSH[@]}" "defaults read com.apple.Safari IncludeDevelopMenu 2>/dev/null" | tr -d '[:space:]')
  [ "$ae" = "1" ] && [ "$dev" = "1" ]
}

cap_install_safari-ae() {
  echo "    action: defaults write com.apple.Safari AllowJavaScriptFromAppleEvents / IncludeDevelopMenu"
  "${SSH[@]}" "defaults write com.apple.Safari AllowJavaScriptFromAppleEvents -bool true && defaults write com.apple.Safari IncludeDevelopMenu -bool true" 2>/dev/null
  local rc=$?
  echo "    note: Safari must be relaunched for the changes to take effect"
  return $rc
}

# ---------------------------------------------------------------- clipboard

cap_desc_clipboard()   { echo "Clipboard — pbcopy / pbpaste, cross-agent hand-off"; }
cap_repair_clipboard() { echo "restart pboard: killall pboard (macOS auto-relaunches)"; }

cap_probe_clipboard() {
  local tag="bridge-probe-$$"
  _run_in_mux clipboard "echo $tag | pbcopy && [ \"\$(pbpaste)\" = \"$tag\" ]" 2
  local rc=$?; _clean_marker clipboard; return $rc
}

cap_install_clipboard() {
  echo "    action: killall pboard (auto-relaunches)"
  "${SSH[@]}" "killall pboard 2>/dev/null; sleep 1"
  return 0
}

# ---------------------------------------------------------------- notification

cap_desc_notification()   { echo "Notification Center — osascript display notification"; }
cap_repair_notification() { echo "grant Terminal.app 'Automation → System Events' TCC on the remote"; }

cap_probe_notification() {
  _run_in_mux notification 'osascript -e "display notification \"bridge probe\" with title \"Bridge\"" >/dev/null 2>&1' 2
  local rc=$?; _clean_marker notification; return $rc
}

cap_install_notification() {
  echo "    guidance: $(cap_repair_notification)"
  return 1
}

# ---------------------------------------------------------------- audio

cap_desc_audio()   { echo "Audio (afplay + say) — voice output, alert tones"; }
cap_repair_audio() { echo "connect a default audio output device on the remote (system-side, not fixable from here)"; }

cap_probe_audio() {
  _run_in_mux audio 'afplay /System/Library/Sounds/Ping.aiff -t 0.05 2>/tmp/bridge-cap-audio.err; ! grep -qi error /tmp/bridge-cap-audio.err 2>/dev/null' 2
  local rc=$?
  "${SSH[@]}" "rm -f /tmp/bridge-cap-audio.err" 2>/dev/null
  _clean_marker audio; return $rc
}

cap_install_audio() {
  echo "    informational: no install action; audio requires a physical default output device"
  return 2
}

# ---------------------------------------------------------------- agent-window

cap_desc_agent-window()   { echo "Concurrent-agent window convention — agents share a session without colliding"; }
cap_repair_agent-window() { echo "open an identified window: bridge tmux <host> --agent <slug>"; }

# Four agents shared bridge-haorui on 2026-07-26 and collided badly — stolen
# `ctrl jpage` navigations, killed background jobs, a base64 script pasted into
# the middle of another agent's command line — because `tmux send-keys -t
# bridge-<host>` with no window target lands on whichever window happens to be
# ACTIVE. The convention that fixes it is a per-agent named window; this probe
# asks whether the session is actually using it.
#
# Deliberately does NOT run inside _run_in_mux: the helper creates an unnamed
# window to run its body, and every other probe in this file does the same, so a
# probe executing there would see tmux's default numeric names and could not tell
# a conforming session from a bare one. Ask the server directly instead.
cap_probe_agent-window() {
  "${SSH[@]}" "tmux list-windows -t $SESSION -F '#{window_name}' 2>/dev/null" \
    | grep -Eq '^agent-'
}

cap_install_agent-window() {
  echo "    guidance: $(cap_repair_agent-window)"
  echo "    note: the slug is the agent's identity — it appears in tmux list-windows"
  echo "          and in the occupancy refusal any other agent gets"
  return 1
}

# ---------------------------------------------------------------- walker

# profile_full_walk MODE
#   MODE: probe   — doctor-style read-only; prints PASS/FAIL + repair hint on FAIL
#         install — probe first; on FAIL, run install action; re-probe once
#         dry-run — probe first; on FAIL, print what install WOULD do
# Uses ambient SSH / SESSION / TARGET set by resolve_target.
# Returns 0 iff every countable row is PASS at the end of the walk.
profile_full_walk() {
  local mode="$1"
  local pass=0 fail=0 fixed=0 info=0
  local id desc irc
  say "-- full profile walk (${#CAPS_FULL_IDS[@]} rows) --"
  for id in "${CAPS_FULL_IDS[@]}"; do
    desc=$("cap_desc_$id")
    if "cap_probe_$id"; then
      say "  PASS  $id  $desc"
      pass=$((pass+1))
      continue
    fi
    case "$mode" in
      probe)
        say "  FAIL  $id  $desc"
        say "        → $(cap_repair_$id)"
        fail=$((fail+1))
        ;;
      dry-run)
        say "  FAIL  $id  $desc"
        say "        would: $(cap_repair_$id)"
        fail=$((fail+1))
        ;;
      install)
        say "  FAIL  $id  $desc — attempting install"
        "cap_install_$id"; irc=$?
        if [ "$irc" = 0 ]; then
          if "cap_probe_$id"; then
            say "    PASS  $id  fixed"
            fixed=$((fixed+1))
          else
            say "    FAIL  $id  install ran but probe still fails"
            say "        → $(cap_repair_$id)"
            fail=$((fail+1))
          fi
        elif [ "$irc" = 2 ]; then
          info=$((info+1))
        else
          fail=$((fail+1))
        fi
        ;;
    esac
  done
  say "-- profile walk: $pass pass, $fixed fixed, $fail fail, $info info --"
  [ "$fail" = 0 ]
}
