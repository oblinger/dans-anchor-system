#!/bin/bash
# install-launchd — write + bootstrap the MUSE launchd agent (idempotent).
#
# Called by DAS `install` (or `install muse`) — see F019 for the design.
# Detects `_trust` presence on PATH. If present, writes the plist routing
# through `_trust muse-sweep` and bootstraps the agent. If absent, emits
# an informational note and exits 0 — interactive `/muse` works either way.
#
# Idempotent: safe to run repeatedly. Existing agent is booted out and
# replaced fresh each time.

set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/com.oblinger.muse-ingest.plist"
AGENT="gui/$(id -u)/com.oblinger.muse-ingest"

if ! command -v _trust >/dev/null 2>&1; then
    cat <<'EOF'
muse: _trust not present on PATH — background sweep disabled on this machine.
      Use /muse interactively, or schedule a periodic action from Claude Code
      — see MUSE Architecture § Portable invocation. To enable background
      sweep, build _trust (see F019 § Track A: dans-anchor-system/macos/trust/).
EOF
    exit 0
fi

TRUST_PATH="$(command -v _trust)"

mkdir -p "$(dirname "$PLIST")"

cat > "$PLIST" <<PLIST_END
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.oblinger.muse-ingest</string>

    <!-- Routes through _trust — a Developer-ID-signed + Apple-notarized
         Mach-O launcher granted FDA in System Settings. muse-sweep verb
         execs the muse sweep script with _trust's TCC identity, unlocking
         ~/Library/Mobile Documents/ enumeration. See F019 for the design. -->
    <key>ProgramArguments</key>
    <array>
        <string>${TRUST_PATH}</string>
        <string>muse-sweep</string>
    </array>

    <!-- WatchPaths often misses iCloud FileProvider drops (the OS materializes
         downloaded files without firing FSEvents). StartInterval is the
         backstop — worst-case 5-minute lag from watch dictation to Quick.md. -->
    <key>WatchPaths</key>
    <array>
        <string>${HOME}/Library/Mobile Documents/iCloud~com~openplanetsoftware~Just-Press-Record/Documents</string>
    </array>

    <key>StartInterval</key>
    <integer>300</integer>

    <key>RunAtLoad</key>
    <false/>

    <key>ThrottleInterval</key>
    <integer>10</integer>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${HOME}/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>${HOME}</string>
    </dict>

    <key>StandardOutPath</key>
    <string>${HOME}/Library/Logs/muse-ingest.log</string>

    <key>StandardErrorPath</key>
    <string>${HOME}/Library/Logs/muse-ingest.log</string>
</dict>
</plist>
PLIST_END

# Idempotent: bootout any existing instance before bootstrapping fresh.
launchctl bootout "$AGENT" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "muse install-launchd: wrote $PLIST"
echo "muse install-launchd: bootstrapped $AGENT (routes through $TRUST_PATH muse-sweep)"
echo ""
echo "To force an immediate sweep:  launchctl kickstart -k $AGENT"
echo "To watch the log:             tail -f ~/Library/Logs/muse-ingest.log"
