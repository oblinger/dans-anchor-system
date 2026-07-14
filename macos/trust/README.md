# `_trust` — signed launcher for FDA-gated background pipelines

`_trust` is the machine-local trust anchor that DAS-installed skills route through when they need Full Disk Access from a background/scheduled context (launchd, cron, login items).

Deployed as a compiled Mach-O at `~/bin/_trust`, Developer-ID-signed and Apple-notarized. Granted FDA once in System Settings, it dispatches to trusted target scripts via `execv` — the target scripts inherit `_trust`'s TCC identity and can read protected paths (iCloud FileProvider mounts, `~/Documents`, `~/Library/Mail`, etc.).

## When you need this

- **You do** — if you want any DAS skill's background/scheduled invocation (e.g., MUSE's launchd auto-sweep of Just-Press-Record recordings) to work without you launching it interactively.
- **You don't** — if you're happy running everything interactively via `/skill-name` commands from Claude Code (which inherits FDA from its parent). Skills route through `_trust` **only** when the DAS `install` skill detects `_trust` on `PATH`; without it, they fall back to interactive-only mode and `install` skips their daemon-setup step silently.

Non-macOS hosts don't need this at all (no TCC).

## Why not a shell script

macOS Sequoia's TCC layer **silently no-ops FDA grants on**:

1. SIP-managed shell interpreters (`/bin/bash`, `/bin/zsh`, `/usr/bin/python3`). The Settings UI accepts the grant; the runtime kernel ignores it. Verified against `~/Documents`, `~/Desktop`, and iCloud FileProvider mounts.
2. Adhoc-signed binaries (`codesign -s -`). Same failure mode — silent no-op.
3. Shell scripts inside Developer-ID-signed + notarized + stapled `.app` bundles. The script inherits `/bin/bash`'s SIP identity, not the bundle's identity.

The **only** reliable TCC anchor for launchd-invoked processes is a compiled Mach-O binary that is Developer-ID-signed + Apple-notarized. That's what `_trust` is.

## Prereqs (one-time per machine)

1. **Xcode Command Line Tools** — `xcode-select --install`. Free, ~1 GB, provides `cc`, `codesign`, `xcrun`.
2. **Developer ID Application certificate in the login Keychain** — free with an Apple ID (no paid developer program required for personal machine use):
   - Xcode → Settings → Accounts → add your Apple ID → Manage Certificates → `+` → Developer ID Application. Cert lands in login Keychain automatically.
   - Or via developer.apple.com → Certificates → `+` → Developer ID Application → generate CSR from Keychain Access → download → double-click to install.
3. **`notarytool` Keychain profile** — one-time credential store:
   ```
   xcrun notarytool store-credentials das-notarize \
     --apple-id <your-apple-id@example.com> \
     --team-id <YOUR-TEAM-ID> \
     --password <app-specific-password>
   ```
   Get the app-specific password at appleid.apple.com → Sign-In and Security → App-Specific Passwords.

## Build

```
cd dans-anchor-system/macos/trust
./build
```

The script auto-picks the first Developer ID Application identity from Keychain, compiles + signs + submits for notarization + waits + emits verification output. Takes ~30-60 seconds (mostly waiting on Apple's notarization service).

**After any edit to `_trust.c`:** re-run `./build`. TCC binds the FDA grant to the code-signature identity (Team ID), not to the file hash — rebuilds preserve the grant. No need to re-toggle FDA in System Settings.

## Grant FDA (first time only)

After the first successful build:

1. System Settings → **Privacy & Security** → **Full Disk Access**
2. Click **`+`**
3. In the file picker, press **`Cmd + Shift + G`** and type: `~/bin/_trust` → Return
4. Select `_trust` → **Open**
5. Toggle the row **on**
6. Authenticate if prompted (Touch ID / password)

Subsequent rebuilds do not require re-toggling — the Team-ID-anchored grant persists.

## Adding a new verb

Rebuild-to-extend is the whole design point.

1. Edit `_trust.c` — add a new `if (strcmp(argv[1], "your-verb") == 0) { ... execv(...) ... }` block. Every trusted target script's absolute path lives in this source.
2. Rerun `./build` — recompiles + resigns + re-notarizes.
3. FDA grant persists (same identity).

No config file, no plugin directory, no runtime registry — the audit surface is this source file, reviewed at compile time.

## Verification (what to expect)

After a successful build:

```
codesign -dvv ~/bin/_trust
# Should include: Authority=Developer ID Application: <your name> (...)
#                 TeamIdentifier=<your team ID>

spctl -a -vvvv ~/bin/_trust
# Should report: accepted (source=Notarized Developer ID)
```

If `spctl` says `rejected, source=Unnotarized Developer ID`, the notarization step didn't complete — check `xcrun notarytool history --keychain-profile das-notarize` for the last submission's status.

## Reference

- **F019** (SYS anchor) — full design of the two-track TCC strategy (`_trust` on personal machines; `/muse` interactive fallback for others).
- **[[gotcha-adhoc-code-signing]]** — vault-wide memory of why adhoc signing silently fails for TCC.
