# Dev Environment Setup

Set up a repeatable, standardized developer environment for a project. Asks clarifying questions about the project type, then creates the appropriate infrastructure.

## Usage

```
/code setup                    # Start interactive setup for current project
/code setup <anchor-name>      # Set up dev environment for a specific anchor
```

## Component Catalog

Every component below MAY be included depending on the project type. The **Condition** column says when each applies. A `*` means see notes below the table.

| Component                                          | Condition        | Opt | Description                                                    |
|----------------------------------------------------|------------------|-----|----------------------------------------------------------------|
|                                                    |                  |     | **ALL PROJECTS**                                               |
| [justfile](#1-justfile)                            | all              |     | Central build orchestration with named recipes                 |
| [Dev environment check](#3-dev-environment-check)  | all              |     | Fast pre-build gate that verifies symlinks, paths, tools       |
| [Unit test recipes](#8-unit-test-recipes)          | all              |     | `just test` wiring for the project's test framework            |
| [Pre-commit hook](#10-pre-commit-hook)             | all              |     | Fast test subset that gates commits                            |
| [IDE settings](#18-ide-settings)                   | all              |     | .vscode/settings.json, .tmuxp.yaml, editor config             |
|                                                    |                  |     | **COMPILED / NATIVE**                                          |
| [Symlink management](#12-symlink-management)       | compiled         |     | Ensure one copy of binaries, symlinks everywhere else          |
| [Multi-arch build](#13-multi-arch-build)           | native binary    |     | Universal binary support (arm64 + x86_64)                      |
| [Build verification](#2-build-verification)        | compiled         | opt | Embed build metadata, verify at runtime against stale binaries |
|                                                    |                  |     | **MACOS APP**                                                  |
| [Dev app bundle](#4-dev-app-bundle)                | .app packaging*  |     | Symlink-based /Applications/App.app for testing                |
| [Code signing](#5-code-signing)                    | macOS app        |     | Sign and notarize binaries for Gatekeeper                      |
| [Beta channel](#7-beta-channel)                    | GUI app          | opt | Separate app bundle, config dir, and hotkey for side-by-side   |
| [URL scheme handler](#14-url-scheme-handler)       | macOS deep link  |     | Register and handle custom URL schemes (e.g., `myapp://`)      |
|                                                    |                  |     | **SERVER / DAEMON**                                            |
| [Integration/E2E tests](#9-integratione2e-tests)   | server/GUI       |     | Feature-gated tests requiring a running process                |
| [Server restart recipe](#15-server-restart-recipe) | long-running*    |     | `just restart` to kill and relaunch a background server        |
| [Daily backups](#16-daily-backups)                 | stateful*        | opt | Auto-backup of databases or state files with retention policy  |
|                                                    |                  |     | **DISTRIBUTION / INSTALL**                                     |
| [Distribution packaging](#6-distribution-packaging)| distributable*   |     | DMG/installer/archive creation for end users                   |
| [Config management](#11-config-management)         | configurable*    |     | Dist configs, default generation, version compatibility checks |
| [Uninstall script](#17-uninstall-script)           | installable      |     | Clean removal of app, configs, and registrations               |
|                                                    |                  |     | **LANGUAGE / TOOL**                                            |
| [Shell integration](#19-shell-integration)         | CLI tool         |     | Zshrc/bashrc snippet for PATH, completions, aliases            |
| [Rust toolchain pinning](#20-rust-toolchain-pinning)| Rust            |     | rust-toolchain.toml for consistent compiler versions           |

### Condition Notes

- **.app packaging** — The project produces a macOS `.app` bundle (GUI or menubar app)
- **distributable** — End users install the software (not just developer use)
- **configurable** — The app reads config files that ship with a distribution
- **long-running** — A server, daemon, or background process that persists across builds
- **stateful** — The app maintains a database, log, or state file that would be costly to lose

---

## Interactive Workflow

### Phase 1: Discovery

Ask the user these questions to determine which components apply. Present them as a numbered list and let the user answer in bulk.

```
I need to understand your project to set up the right dev environment.
Please answer these (skip any that are obvious from context):

1. Language/framework? (e.g., Rust, Python, TypeScript, Swift, Go)
2. What does it produce? (CLI tool, GUI app, library, web service, daemon)
3. Target platform? (macOS, Linux, cross-platform, web)
4. Is it packaged as a macOS .app bundle? (yes/no)
5. Does it have a config file users edit? (yes/no)
6. Does it run as a long-lived server or daemon? (yes/no)
7. Does it maintain state (database, log files)? (yes/no)
8. Will it be distributed to end users? (yes/no)
9. Does it need a custom URL scheme? (e.g., myapp://) (yes/no)
10. Where is the project root? (path or "here" for cwd)
11. Which anchor should be updated with dev docs? (name or "none")
```

### Phase 2: Component Selection

Based on answers, determine which components from the catalog apply. Present the selected components as a checklist, then list available optional components separately. Optional components (marked `opt` in the catalog) are NOT included by default — only add them if the user explicitly requests them.

```
Based on your answers, here's what I'll set up:

[x] justfile — build recipes
[x] Dev environment check — pre-build verification
[x] Unit test recipes — test wiring
[x] Pre-commit hook — commit gate
[ ] Dev app bundle — (skipped: not a .app)
...

Optional components available for this project (not included unless you request them):
  - Build verification — embed build metadata, detect stale binaries
  - Beta channel — separate app bundle for side-by-side testing
  - Daily backups — auto-backup of state files with retention policy

Want any optional components? Or adjust the list above?
(e.g., "add Beta channel, remove Pre-commit hook", or "looks good")
```

### Phase 3: Implementation

For each selected component, create the files described in the sections below. Adapt templates to the specific language, framework, and project structure.

After all components are created, run the dev environment check to verify everything works.

### Phase 4: Anchor Update

If the user specified an anchor, add a development section to the anchor's CLAUDE.md or project documentation listing:
- How to build (`just build`)
- How to test (`just test`)
- How to deploy/restart
- Key file locations

---

## Component Details

### 1. justfile

Create a `justfile` at the project root. Always include:

```just
# Show available commands
default:
    @just --list

# Build the project
build: check-dev-env
    @echo "Building..."
    # language-specific build command

# Run tests
test:
    # language-specific test command

# Clean build artifacts
clean:
    # language-specific clean
```

**Language-specific patterns:**
- **Rust**: `cargo build --release`, `cargo test --lib`
- **Python**: `python -m pytest`, virtual env activation
- **TypeScript/Node**: `npm run build`, `npm test`
- **Go**: `go build ./...`, `go test ./...`
- **Swift**: `swift build`, `swift test`

### 2. Build Verification (compiled languages)

For compiled languages, embed build metadata so stale binaries are detected.

**Rust pattern** (from HookAnchor):
- `build.rs` reads `JUST=1` env var, embeds timestamp, git commit, branch
- Runtime check in startup path compares embedded metadata
- Shows error dialog if binary wasn't built with `just build`

**General pattern:**
- Build script writes a `.build-stamp` file with timestamp + git hash
- Startup reads stamp, warns if > N days old or missing

### 3. Dev Environment Check

Create `dev-scripts/setup/dev-check.sh` (or equivalent):

```bash
#!/usr/bin/env bash
set -e
# Verify all required tools are installed
# Verify all symlinks/paths are valid
# Verify config files exist
# Exit 0 if all good, exit 1 with clear message if not
```

Wire into justfile: `build: check-dev-env`

**What to check:**
- Required CLI tools exist (`command -v tool`)
- Symlinks point to correct targets
- Config directory exists with required files
- Environment variables are set (if needed)
- No stale lock files or sockets

### 4. Dev App Bundle (macOS .app)

Wire into justfile as `just build_dev_env`. This recipe builds the project and creates `/Applications/MyApp.app` using **symlinks only**:

```bash
#!/usr/bin/env bash
APP="/Applications/MyApp.app"
RELEASE="$(pwd)/target/release"

mkdir -p "$APP/Contents/MacOS"
mkdir -p "$APP/Contents/Resources"

# SYMLINKS, not copies!
ln -sf "$RELEASE/my_binary" "$APP/Contents/MacOS/MyApp"

# Generate Info.plist
cat > "$APP/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>MyApp</string>
  <key>CFBundleExecutable</key><string>MyApp</string>
  ...
</dict></plist>
PLIST

# Register with Launch Services
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
```

Add `DO_NOT_COPY_BINARIES.md` to the app bundle as a safeguard.

### 5. Code Signing (macOS)

Create `dev-scripts/build/sign.sh`:

```bash
#!/usr/bin/env bash
IDENTITY="Developer ID Application: ..."
ENTITLEMENTS="dev-scripts/build/entitlements.plist"

codesign --force --options runtime \
  --sign "$IDENTITY" \
  --entitlements "$ENTITLEMENTS" \
  --timestamp "$1"
```

Create `entitlements.plist` with minimum required entitlements for the app.

Add justfile recipes: `sign`, `sign-app`, `sign-dmg`

### 6. Distribution Packaging

Create `dev-scripts/build/build_dist.sh`:
- Build universal binaries (if native)
- Copy to temporary app bundle (actual copies for distribution)
- Include distribution config files
- Sign and notarize
- Create DMG or archive
- Store in `versions/<version>/`

### 7. Beta Channel

- Separate app bundle name (`MyApp Beta.app`)
- Separate config directory (`~/.config/myapp-beta/`)
- Feature flag in build system (`--features beta`)
- Different hotkey/port to avoid conflicts with production

### 8. Unit Test Recipes

Wire the project's test framework into justfile:

```just
test:
    cargo test --lib          # Rust
    pytest tests/             # Python
    npm test                  # Node
    go test ./...             # Go
```

### 9. Integration/E2E Tests

- Feature-gate behind a flag so they don't run in normal `just test`
- Require a running server/process
- Run single-threaded to avoid conflicts

```just
test-e2e:
    @echo "Server must be running..."
    cargo test --features e2e --test e2e -- --test-threads=1
```

### 10. Pre-commit Hook

Create `dev-scripts/setup/setup-git-hooks.sh`:

```bash
#!/usr/bin/env bash
cat > .git/hooks/pre-commit << 'HOOK'
#!/usr/bin/env bash
just test-commit || exit 1
HOOK
chmod +x .git/hooks/pre-commit
```

Add fast test recipe:

```just
test-commit:
    @echo "Running pre-commit tests..."
    # fastest critical subset only
```

### 11. Config Management

- **Runtime config**: `~/.config/myapp/config.yaml` (symlinked during dev)
- **Distribution config**: `config/dist_config.yaml` (sanitized, no secrets)
- **Default generator**: Script to strip personal data from dev config
- **Version check**: Embed `config_version` field, check at startup

### 12. Symlink Management

Rule: ONE copy of each binary in `target/release/`. Everything else is symlinks:
- `/Applications/MyApp.app/Contents/MacOS/*` → `target/release/`
- `~/bin/myapp` → `target/release/`

Verify in dev-check script. Add `DO_NOT_COPY_BINARIES.md` markers.

### 13. Multi-arch Build

```just
build-universal:
    rustup target add x86_64-apple-darwin aarch64-apple-darwin
    cargo build --release --target aarch64-apple-darwin
    cargo build --release --target x86_64-apple-darwin
    lipo -create -output target/release/mybinary \
      target/aarch64-apple-darwin/release/mybinary \
      target/x86_64-apple-darwin/release/mybinary
```

### 14. URL Scheme Handler

- Register in Info.plist `CFBundleURLTypes`
- Handle via Apple Events (NOT command line args)
- Re-register with `lsregister` after setup

### 15. Server Restart Recipe

```just
restart:
    @echo "Restarting server..."
    ./target/release/myapp --restart
    # OR: kill existing, relaunch
```

Critical after every build for long-running processes.

### 16. Daily Backups

Add to dev-check script:

```bash
BACKUP_DIR="$HOME/.myapp-backups"
TODAY=$(date +%Y%m%d)
DB="$HOME/.config/myapp/data.db"
if [ -f "$DB" ] && [ ! -f "$BACKUP_DIR/data_$TODAY.db" ]; then
    mkdir -p "$BACKUP_DIR"
    cp "$DB" "$BACKUP_DIR/data_$TODAY.db"
    find "$BACKUP_DIR" -name "data_*.db" -mtime +30 -delete
fi
```

### 17. Uninstall Script

Create `dev-scripts/uninstall.sh`:
- Kill running processes
- Remove app bundle
- Remove URL registrations
- Remove shell integration
- Optionally remove config (ask first)

### 18. IDE Settings

Create `.vscode/settings.json` with:
- Language-specific formatter/linter settings
- File watcher exclusions for build artifacts
- Recommended extensions

Create `.tmuxp.yaml` for dev session layout if the user uses tmux.

### 19. Shell Integration

Create `config/shell_integration.zsh`:

```bash
# MyApp shell integration
export PATH="$HOME/bin:$PATH"
# completions, aliases, etc.
```

### 20. Rust Toolchain Pinning

Create `rust-toolchain.toml`:

```toml
[toolchain]
channel = "stable"
```
