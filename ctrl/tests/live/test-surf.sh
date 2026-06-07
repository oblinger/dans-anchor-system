#!/bin/bash
# test-surf.sh — `ctrl surf` must ALWAYS open a new Chrome tab that loads the URL,
# without disturbing other tabs. NON-DESTRUCTIVE: only touches tabs it creates.
set -u
PASS=0; FAIL=0
ok(){ echo "  ✓ $1"; PASS=$((PASS+1)); }
no(){ echo "  ✗ $1"; FAIL=$((FAIL+1)); }
SENTINEL="https://example.org/SURFTEST-SENTINEL-DO-NOT-WIPE"

chrome_tabs(){ osascript -e 'tell application "Google Chrome"
  set n to 0
  repeat with w in windows
    set n to n + (count of tabs of w)
  end repeat
  return n
end tell' 2>/dev/null; }
active_url(){ osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' 2>/dev/null; }

# Create our OWN sentinel tab (do NOT clobber whatever the user had active) and focus it.
osascript -e 'tell application "Google Chrome"
  activate
  if (count of windows) = 0 then make new window
  tell front window
    make new tab with properties {URL:"'"$SENTINEL"'"}
    set active tab index to (count of tabs)
  end tell
end tell' >/dev/null 2>&1
sleep 1

before=$(chrome_tabs)   # includes our sentinel tab, which is now active ("current view")
echo "tabs before (sentinel active): $before ; current view: $(active_url)"

for i in 1 2 3; do
  u="https://example.com/surf-$i-$(date +%s)-$RANDOM"
  ctrl surf "$u" >/dev/null 2>&1
  sleep 1
  au=$(active_url)
  [ "$au" = "$u" ] && ok "surf $i -> own new active tab" || no "surf $i: expected [$u] got [$au]"
done

after=$(chrome_tabs)
[ "$after" = "$((before+3))" ] && ok "tab count +3 ($before -> $after)" || no "tab count: got $after expected $((before+3))"

# the sentinel (previously-active tab) must be untouched — surf must not navigate it
if osascript -e 'tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) is "'"$SENTINEL"'" then return "found"
    end repeat
  end repeat
  return "missing"
end tell' 2>/dev/null | grep -q found; then ok "previously-active tab preserved (not wiped)"; else no "previously-active tab WIPED"; fi

# cleanup: close ONLY tabs this test created (exact sentinel + our example.com/surf- urls)
osascript -e 'tell application "Google Chrome"
  repeat with w in windows
    set i to (count of tabs of w)
    repeat while i ≥ 1
      set tURL to URL of tab i of w
      if tURL is "'"$SENTINEL"'" or tURL starts with "https://example.com/surf-" then close tab i of w
      set i to i - 1
    end repeat
  end repeat
end tell' >/dev/null 2>&1

echo "=== PASS=$PASS FAIL=$FAIL ==="
[ "$FAIL" -eq 0 ] && echo "ALL PASS" || { echo "FAILURES"; exit 1; }
