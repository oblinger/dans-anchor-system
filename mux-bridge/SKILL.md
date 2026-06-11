---
name: mux-bridge
description: Two-axis bridge between this Mac and a remote host. **Control plane** — set up a terminal-multiplexer bridge so the agent can drive the remote via `ctrl box2` (or boxN) with full TCC inheritance; use when SSH-only sessions can't access TCC-protected paths (/Volumes/*, ~/Desktop, ~/Documents) and the agent needs FDA-as-user. **Data plane** — set up file sync (Syncthing today; NFS-via-symlink and rsync planned) so dev-Mac folders appear at the same canonical path on remote. Slash-only — `/mux-bridge <host>` opens a session; `/mux-bridge sync` / `init-syncthing` / `sync-status` / `sync-teardown` manage the data plane.
---

# MUX Bridge

## Purpose

When the agent needs to drive a remote machine *as if it were a local box* — sustained interactive work, FDA-bearing commands, multiplexer hand-off — set up a tmux-on-this-side ⇄ multiplexer-on-the-other-side bridge. Optionally pair with **file sync** so the same vault / code tree appears at identical paths on both sides.

Key insight (control plane): **the remote multiplexer inherits TCC from whatever launches it.** If the user starts tmux/screen from a Terminal app with Full Disk Access, the multiplexer server has FDA, and every command run in its panes inherits FDA — even when the agent attaches via SSH (which itself has no FDA).

Key insight (data plane): **same-relative-path contract.** The remote path always matches the local path absolutely (`/Users/oblinger/ob/kmr/` on dev Mac ↔ same on remote). Preserves wiki-link resolution, absolute-path references, any tooling that bakes in `~/ob/...` paths.

## Architecture

```
This Mac:                          Remote host:
┌─ ctrl box2 (tmux) ──────────────────────── ssh ─────────────────────────► tmux/screen `work` session
│  agent drives via ctrl box2 "cmd"        FDA inherited from Terminal.app launch
└─ outbox2 reads back stdout            commands run inside have FDA

  CONTROL plane (SSH + tmux)                    │   DATA plane (Syncthing today)
                                                │   ~/ob/kmr/  ←── Syncthing ──→  ~/ob/kmr/
                                                │   (real dir, local copy both sides, eventual convergence)
```

Two axes are independent: drive control without sync, or sync without ever attaching a tmux session.

The agent uses `ctrl box2` (or any free boxN slot — keep `box` for general local work, reserve box2+ for named remotes).

## Setup recipe

### Step 1 — confirm SSH key-auth works

```
ssh -o BatchMode=yes oblinger@<host>.local 'hostname'
```

If "Permission denied", run `ssh-copy-id oblinger@<host>.local` via box (interactive password prompt; user types into tmux pane).

### Step 2 — confirm Remote Login is enabled on the remote

If `ssh: connect to host: Connection refused`, Remote Login is off. **Tell the user**: System Settings → General → Sharing → toggle Remote Login ON. CLI route (`sudo systemsetup -setremotelogin on`) needs Full Disk Access on the calling Terminal — flaky on Tahoe. GUI is reliable.

### Step 3 — detect platform and locate the multiplexer

```
ssh user@host 'uname -s ; zsh -lc "which tmux ; which screen ; which brew"'
```

- **macOS (`Darwin`)**: prefer tmux, fall back to screen (built-in).
- **Linux**: prefer tmux. If absent, `which apt-get yum dnf pacman zypper` to detect distro.

### Step 4 — install tmux if missing

**macOS (Apple Silicon)**: `brew install tmux` at `/opt/homebrew/bin/brew`.
**macOS (Intel)**: `brew install tmux` at `/usr/local/bin/brew`. **Bottle may be missing on older macOS — brew will try to compile, which needs an accepted Xcode license**. If you hit `Error: You have not agreed to the Xcode license`, run `sudo xcodebuild -license accept` via interactive box. **If sudo over SSH closes the connection mysteriously**, the SSH-driven sudo may be silently failing on Touch-ID-only Macs — fall back to **`screen`** (always available; same FDA inheritance) instead of fighting tmux install.

**Linux**: `sudo apt-get install -y tmux` (Debian/Ubuntu), `sudo dnf install -y tmux` (Fedora/RHEL), `sudo pacman -S tmux` (Arch).

**Ask the user** before installing if brew/package-manager isn't already present. Don't bootstrap homebrew without consent.

### Step 5 — start the multiplexer on the remote *from a TCC-blessed Terminal*

**CRITICAL**: the user must start the session **from Terminal.app on the remote**, not via SSH. SSH-launched mux has SSH's TCC context (no FDA). Terminal-launched mux has Terminal's FDA.

Tell the user:

```
# tmux
tmux new -s work

# screen
screen -S work
```

The session persists when they detach (`Ctrl-B D` for tmux, `Ctrl-A D` for screen).

### Step 6 — attach from the local box

```
# tmux
ctrl box2 "ssh -t oblinger@<host>.local 'tmux attach -t work'"

# screen
ctrl box2 "ssh -t oblinger@<host>.local 'screen -x work'"
```

From here, every `ctrl box2 "cmd"` runs `cmd` inside the remote multiplexer pane, which has full FDA. `ctrl outbox2` reads back what was printed.

## Gotchas observed in the wild (2026-06-06, COPPER → 10T verification)

1. **`du: /Volumes/X: Operation not permitted` over SSH** — TCC blocks SSH-launched processes from reading /Volumes. This skill exists *because of* this failure mode.
2. **Granting Full Disk Access to `/usr/libexec/sshd-keygen-wrapper`** is the documented Apple solution but the Tahoe FDA pane silently failed to register the addition when tested. Don't burn time on the FDA pane — pivot to mux bridge instead.
3. **macOS shipping OpenSSH 9.8+** uses split binaries: `sshd` (listener) + `sshd-session` (per-connection) + `sshd-auth`. Granting FDA may need to apply to `sshd-session`, not `sshd-keygen-wrapper`.
4. **`/usr/local/bin/brew` on Intel Macs is NOT in the SSH non-interactive PATH** by default. Use the full path or `zsh -lc`.
5. **Xcode license must be accepted before brew can compile from source**. Tahoe + Intel + missing bottles = compile required.
6. **`sudo` over SSH with Touch-ID-only Macs can silently fail** — the sudo prompt accepts the password but the command exits without effect. Workaround: have the user run the privileged command in Terminal on the remote (not via SSH).
7. **macOS Tahoe (26) split `Siri & Spotlight` into separate `Spotlight` and `Siri` panes**. Old guides pointing at "Siri & Spotlight" no longer apply.

## The "disk station" pattern

A powerful use of mux-bridge is to **pin slow / noisy bulk operations to a dedicated remote machine** so the user's primary work surface stays responsive. Pattern:

- **Primary Mac** — user's day-to-day machine, where they're working actively. Stays quiet.
- **Disk station** — a secondary Mac (often an older laptop with the right physical USB / Thunderbolt ports) that has the drives physically attached and runs the bulk reads / writes / verifies.
- **Mux-bridge** lets the agent drive disk-station operations from the primary Mac without intruding on local CPU / fan / disk activity.

Do NOT default to "move the drives to the user's primary machine" when bulk operations are needed — confirm whether they have a quieter remote machine to use, and propose mux-bridge first. Captured 2026-06-06 after the user explicitly noted "this Mac is busy" during the COPPER → 10T verification.

## When NOT to use this skill

For a one-shot read on the remote (`cat /tmp/foo` or similar non-TCC path), plain `ssh user@host 'cmd'` is fine. Mux bridge is for sustained interactive work where you'll be running many commands or watching live output.

For a one-shot operation on a TCC-protected path, an alternative is to have the user run a self-contained script in their Terminal that writes output to `/tmp/` (non-TCC) — agent then SSH-reads `/tmp/` without needing FDA.

## Data plane — file sync (Phase 1: Syncthing)

Per-host mode. A remote host has at most one sync mode at a time. Phase 1 ships Syncthing (eventual-convergence bidirectional with both sides keeping a local copy). Phases 2 (NFS-via-symlink) and 3 (rsync-style explicit push/pull) deferred. Spec: `[[F122 — mux-bridge file-sync extension (Syncthing + NFS-via-symlink + rsync future)]]`.

### Subcommand surface

```
/mux-bridge sync                              # use defaults from ~/.config/mux-bridge/defaults.yaml
/mux-bridge sync <folder>                     # override folder; use default remote + mode
/mux-bridge sync --remote <host>              # override remote; use default folder + mode
/mux-bridge init-syncthing <host> <folder>    # explicit form — no defaults consulted
/mux-bridge sync-add <host> <folder>          # add another folder under host's existing mode
/mux-bridge sync-status <host>                # show mode, folders, freshness, errors
/mux-bridge sync-teardown <host>              # remove all sync for this host (files preserved)
```

### Config files

```
~/.config/mux-bridge/defaults.yaml            # user-environment defaults (F146)
~/.config/mux-bridge/hosts.yaml               # per-host sync state
```

`defaults.yaml` schema:
```yaml
version: 1
default_folder: /Users/oblinger/ob/kmr
default_remote: haouri.local
default_mode: syncthing
```

`hosts.yaml` schema:
```yaml
version: 1
hosts:
  haouri.local:
    mode: syncthing
    syncthing:
      device_id_local: <ABC-XYZ-...>
      device_id_remote: <DEF-UVW-...>
      folders:
        - folder_id: kmr-vault
          local: /Users/oblinger/ob/kmr
          remote: /Users/oblinger/ob/kmr
          move_aside: /Users/oblinger/ob/kmr.old.2026-06-11
          initialized: 2026-06-11
```

### Resolution flow for `/mux-bridge sync`

1. **Read defaults.yaml** — for each field not given on CLI, use the default. For each field MISSING from defaults.yaml AND not on CLI, prompt user once, write answer back atomically.
2. **Read hosts.yaml** — check if resolved `<host>` already has a sync mode configured.
   - **Match** (same mode, same folder): probe daemons; if healthy, print status; done.
   - **Mismatch** (e.g., user requests Syncthing but host is on NFS): refuse — `"<host> is currently on <existing-mode>. Run 'sync-teardown <host>' first, then re-init."`
   - **No entry**: dispatch to `init-syncthing <host> <folder>`.

### `init-syncthing <host> <folder>` recipe

Required: `<host>` (e.g., `haouri.local`), `<folder>` (e.g., `/Users/oblinger/ob/kmr`).

The agent uses the helper script `~/.claude/skills/mux-bridge/syncthing-helper.py` for the REST API operations (pair, share, poll, flip). The helper is idempotent and reports JSON status.

**Step 1 — Verify SSH reachability.**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 oblinger@<host> 'hostname' || \
  { echo "ERROR: SSH to <host> failed. Set up control plane first (see § Setup recipe)."; exit 1; }
```

**Step 2 — Install + start Syncthing on dev Mac if missing.**
```bash
command -v syncthing >/dev/null || brew install syncthing
brew services list | grep -q '^syncthing.*started' || brew services start syncthing
```

**Step 3 — Install + start Syncthing on remote if missing.**
```bash
ssh oblinger@<host> 'command -v syncthing >/dev/null || brew install syncthing; brew services list | grep -q "^syncthing.*started" || brew services start syncthing'
```
Tahoe-on-Intel: brew may need to compile from source — see § Gotchas #4-5.

**Step 4 — Wait for both daemons to be reachable.**
```bash
# Local
for i in $(seq 1 15); do curl -sf http://127.0.0.1:8384/rest/system/ping >/dev/null 2>&1 && break; sleep 2; done
# Remote
ssh oblinger@<host> 'for i in $(seq 1 15); do curl -sf http://127.0.0.1:8384/rest/system/ping >/dev/null 2>&1 && break; sleep 2; done'
```

**Step 5 — Pair devices + create folder share** via helper:
```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py pair \
  --host "<host>" --folder "<folder>" --folder-id "$(basename "<folder>" | tr '[:upper:]' '[:lower:]')-share"
```
This step does:
- Fetches API keys from `~/Library/Application Support/Syncthing/config.xml` on both sides.
- Fetches device IDs via REST API on both sides.
- POSTs each device's ID to the other's `/rest/config/devices`.
- Returns the paired (LOCAL_ID, REMOTE_ID) tuple as JSON.

**Step 6 — Warn user + move-aside on remote.** Per F122 § Move-aside semantics:
```
⚠️  About to sync <folder>/ from this Mac to <host>.
    Remote's existing content at <folder>/ will be moved aside to:
      <folder>.old.<YYYY-MM-DD>/
    The new empty <folder>/ will receive the synced version.
    Proceed? [y/N]
```
On confirm:
```bash
TODAY=$(date +%Y-%m-%d)
ssh oblinger@<host> "
  MOVE_ASIDE='<folder>.old.${TODAY}'
  if [ -e '<folder>' ] && [ ! -L '<folder>' ]; then
    mv '<folder>' \"\$MOVE_ASIDE\"
    echo \"Moved <folder> → \$MOVE_ASIDE\"
  fi
  mkdir -p '<folder>'
"
```

**Step 7 — Drop `.stignore`** in `<folder>/` on dev Mac (one-time; Syncthing reads it):
```
.DS_Store
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
.claude/
node_modules/
*.swp
```
Don't overwrite an existing `.stignore` — if present, leave alone.

**Step 8 — Create folder share** via helper (Send Only / Receive Only initially):
```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py share \
  --host "<host>" --folder "<folder>" --folder-id "<folder_id>" \
  --local-mode sendonly --remote-mode receiveonly
```

**Step 9 — Wait for initial convergence** via helper:
```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py wait-converge \
  --host "<host>" --folder-id "<folder_id>" --timeout 1800
```
Polls `/rest/db/status?folder=<id>` on remote until `needBytes == 0`. Timeout 30 min default; for large vaults bump higher. Prints `state` + `needBytes` progress every 10s.

**Step 10 — Flip both to Send & Receive** via helper:
```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py flip-bidirectional \
  --host "<host>" --folder-id "<folder_id>"
```
Sets `type: sendreceive` on both sides.

**Step 11 — Record in `hosts.yaml`.** Via helper:
```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py record \
  --host "<host>" --folder "<folder>" --folder-id "<folder_id>" \
  --local-id "$LOCAL_ID" --remote-id "$REMOTE_ID" \
  --move-aside "<folder>.old.${TODAY}"
```

**Step 12 — Report** (chat):
```
✓ mux-bridge sync set up for <host>
  Folder:     <folder>
  Move-aside: <folder>.old.<YYYY-MM-DD>/ on remote (review + delete when ready)
  Status:     `mux-bridge sync-status <host>` to check freshness
```

### `sync-status <host>` recipe

```bash
python3 ~/.claude/skills/mux-bridge/syncthing-helper.py status --host "<host>"
```
Prints per-folder: state (`idle` / `syncing` / `scanning`), last-sync time, byte progress, error count, paused status.

### `sync-teardown <host>` recipe

1. **Confirm:** *"This will stop syncing all folders for `<host>`. Files on both sides will be preserved. Continue? [y/N]"*
2. Helper removes folder shares on both sides:
   ```bash
   python3 ~/.claude/skills/mux-bridge/syncthing-helper.py teardown --host "<host>"
   ```
3. Helper removes the host entry from `hosts.yaml`.
4. If a `move_aside` path is recorded, ask: *"The move-aside directory still exists at `<path>` on `<host>`. Remove it? [y/N]"*
   On yes: `ssh oblinger@<host> "rm -rf '<path>'"`.

### Per-session auto-resume

When `/mux-bridge <host>` is invoked and `hosts.yaml` has a sync entry for that host:
1. Probe both Syncthing daemons (local + remote).
2. If healthy and convergence is current, proceed silently.
3. If a daemon is down: warn, attempt restart (`brew services restart syncthing`), continue.
4. If remote is unreachable (offline / asleep): warn but continue with SSH+tmux session — data plane is best-effort, control plane is the user's primary goal.

### Gotchas observed (Phase 1 Syncthing)

(To be populated as F122 is exercised against real remotes.)

1. **Syncthing config.xml location** — `~/Library/Application Support/Syncthing/config.xml` on macOS (note: space in path; quote it). REST API key + GUI password live here.
2. **API binds to 127.0.0.1 by default** — to query the remote daemon over SSH, either tunnel (`ssh -L 8385:127.0.0.1:8384`) or wrap the curl call in `ssh oblinger@<host> 'curl ...'`. The helper script uses the wrap pattern.
3. **`.stignore` is per-folder**, lives at the folder root on dev Mac side. Syncthing reads it before scanning.
4. **First convergence over LAN** on a large vault can take 10-30 min. Don't kill mid-sync — let `wait-converge` run.
5. **Conflict files** (`*.sync-conflict-<date>-<id>.<ext>`) appear if both sides edited the same file before convergence. With move-aside in step 6, this shouldn't fire on init, but watch for it post-flip.

## Status

DRAFT — control plane captured 2026-06-06 during live COPPER → 10T backup verification. Data-plane Phase 1 (Syncthing) section added 2026-06-11 per F122 design (with move-aside revision); helper script lives at `~/.claude/skills/mux-bridge/syncthing-helper.py`. To refine as live runs against real remotes (starting with haouri.local) surface gotchas.
