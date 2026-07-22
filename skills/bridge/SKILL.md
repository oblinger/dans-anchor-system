---
name: bridge
description: Connect this Mac to another machine — via the packaged dispatcher `~/.claude/skills/bridge/bridge` (F279); never improvise raw ssh. **Control** (`bridge tmux <host>`) — symmetric `bridge-<host>` tmux sessions both sides, a live viewer Terminal window on the REMOTE's own screen, TCC inheritance (FDA/Screen Recording/Accessibility) so the agent drives the remote as a local box. **Converge** (`bridge install <host>`, alias `refresh`) — idempotent env-twin provisioning: skills + CLAUDE.md + ctrl + launchd-durable Syncthing + provision stamp. **Diagnose** (`bridge doctor <host>`) — read-only deep check; a sub-second preflight also rides every verb automatically. **Sync** (`bridge sync`) — Syncthing status/revive. **Agent** (`bridge agent`) — deploy a briefed Claude agent. Slash-only. Per-user recipe in ~/.config/bridge/config.yaml.
---

# Bridge
requires:: vault, external:homebrew, external:syncthing, external:tmux
subsystem:: [[DAS Utility Design]] — the Utility group's subsystem profile

| Table of Contents |  |
|---|---|
| **[[#Heartbeat discipline — MANDATORY whenever a bridge is active]]** |  |
| **[[#The dispatcher — every verb is a packaged command (F279)]]** |  |
|    [[#Config files]] |  |
|    [[#Setup recipe (manual background — the dispatcher automates this)]] |  |
|    [[#Control gotchas (2026-06-06, COPPER → 10T verification)]] |  |
|    [[#The "disk station" pattern]] |  |
|    [[#Subcommand surface]] |  |
|    [[#Resolution flow for `bridge sync`]] |  |
|    [[#Init recipe (Syncthing)]] |  |
|    [[#Tar-seed accelerator (initial seed — strongly preferred for big/small-file vaults)]] |  |
|    [[#Fast-link discovery (Thunderbolt / USB-C bridge)]] |  |
|    [[#`sync-status` / `sync-teardown`]] |  |
|    [[#Per-session auto-resume]] |  |
|    [[#rsync mode (F175 Phase 3 — explicit push/pull, the hard gate)]] |  |
|    [[#NFS-via-symlink mode (F175 Phase 2 — live mount, zero lag)]] |  |
|    [[#Sync gotchas]] |  |
|    [[#Environment parity ≠ session portability]] |  |
|    [[#Memory IS shared (F159)]] |  |
|    [[#Recipe — `claude-provision.py`]] |  |
|    [[#Refresh — `bridge refresh <host>` (reconverge an existing twin)]] |  |
|    [[#When to use]] |  |
|    [[#Subcommand surface]] |  |
|    [[#Standard tmux session — `agent`, one per host]] |  |
|    [[#Setup recipe — composition with `bridge claude` + tmux launch + windows]] |  |
|    [[#Brief format — YAML frontmatter + redundant body-top table]] |  |
|    [[#Status doc — one canonical doc per host at a computed path]] |  |
|    [[#Status doc transport — SSH-pull on demand; NOT Syncthing; NOT git]] |  |
|    [[#Heartbeat — hard convention while there's active work]] |  |
|    [[#Idempotency]] |  |
|    [[#Gotchas (live, from the 2026-06-23 hand-run)]] |  |
| **[[#When NOT to use bridge]]** |  |
| **[[#Status]]** |  |

**Bridge** is the umbrella for "connect this machine to another machine." Renamed from `mux-bridge` (F150) once it grew past the original SSH+tmux control plane.

**Anti-pattern — one-shot SSH remote-control.** `ssh <host> '<cmd>'` to drive remote work is the wrong tool (no state, no TCC inheritance, no observability, nohup hacks for anything long) — this skill's persistent tmux is the sanctioned control plane. A live Warden rule ([[R-ob-remote-ops]]-01, F183) denies one-shot SSH at `tool:pre:Bash` and redirects here; bare attaches, `scp`/`rsync`, and in-bridge `tmux` commands pass.

## Heartbeat discipline — MANDATORY whenever a bridge is active

**Rule (user, 2026-06-12): while ANY bridge is active — a control session, a sync, a remote agent, or a background workflow driving the remote — you MUST keep a running heartbeat that verifies *actual progress*, not just "still waiting."**

- **Arm a timer.** Schedule a wake-up (default **120 s**; never longer than the 300 s cache window while actively watching) via `ScheduleWakeup`. Re-arm it every heartbeat until the remote work is genuinely done. Do NOT rely solely on "I'll be auto-notified when it finishes" — the failure mode this rule defeats is a remote agent / workflow that **hangs silently** (it never finishes, so the completion notification never fires, and the user sits staring at a dead screen). The earlier Fable-agent hangs and the silent workflow stalls are exactly why this rule exists.
- **Verify ground-truth progress, not pane text.** Each heartbeat, check that something concrete advanced since last time: workflow agent transcripts growing / `journal.jsonl` mtime moving, new commits, files changing, the target metric dropping. If **nothing advanced** between two heartbeats, treat it as STALLED — investigate the stuck agent/process (capture state, then unstick/restart) rather than waiting another cycle.
- **Always end a heartbeat with the ALL-CAPS state banner** (per the `devops` skill): `WORKING — {what}` / `WAITING ON COMPLETION — {what, ETA}` / `WAITING ON USER — {action}`. The banner is the last line, every time.
- **Never go dark.** Silence while a bridge is active is a spec violation — the user must always be able to see, at the cadence of the heartbeat, that progress is real.

See the `devops` skill for the general heartbeat/watcher discipline; this section makes it **non-optional** the moment a bridge is in play.

## The dispatcher — every verb is a packaged command (F279)

**All bridge operations run through `~/.claude/skills/bridge/bridge`** — agents invoke it by full path (it rides the skills repo, so it exists on any provisioned machine, with no `~/bin` or PATH dependency). Raw ssh improvisation is the anti-pattern this dispatcher retires. A **sub-second preflight** runs automatically in front of every verb: local checks always (config sanity, provision-stamp age, local session liveness), one remote ping only over a warm SSH ControlMaster socket (the dispatcher sets `ControlPersist` on all its ssh, keeping sockets warm). On failure the preflight names the fix (`run: bridge install <host>`).

| Verb | Kind | What it does |
|---|---|---|
| `bridge tmux <host> [--session S] [--force] [--viewer]` | mechanism — **control** | **Flagship connect.** Ensures a tmux session on the remote launched in a Terminal window **on the remote's own screen** (the glanceable viewer + the TCC-blessed context), and a **local tmux session `bridge-<host>`** ssh-attached to it. Session named `bridge-<host>` on both sides. Drive: `tmux send-keys -t bridge-<host> "<cmd>" Enter`; read: `tmux capture-pane -t bridge-<host> -p`. Renamed from `bridge mux` (F279 — tmux is what's being bridged). |
| `bridge install <host>` (alias `refresh`) | **goal — converge** | **Idempotent "make it so."** Env files via claude-provision (`~/.claude`, `~/.config` includes, `bin` utilities like ctrl), skills-repo wiring, launchd-durable Syncthing on the remote, provision stamp (remote + local cache). First run installs; re-run reconverges (subsumes F262's refresh). |
| `bridge sync [host]` | mechanism — **data** | Syncthing status/revive. Full share creation stays in `syncthing-helper.py` (move-aside confirmation gate). |
| `bridge skills <host>` | **goal** | Ensure the remote's `~/.claude/skills` tracks the skills repo named in config (`skills_repo`) — symlink into the vault-synced copy when present; clone from `url` only for non-twin machines (never alongside a sync-covered path). Bridge stays generic; only the user's config names the repo (F279 D1). |
| `bridge doctor <host>` | **diagnose** | **Read-only deep check** — reach / Aqua launch-context / TCC caps / sync daemon / launchd / stamp / ctrl / local session. Never mutates (that's install's job). The slow, careful backup to the automatic preflight. |
| `bridge claude [host]` | **goal** | Make the remote a Claude environment-twin. *Composes* `sync` (content) + `~/.claude` provisioning. Now the provisioning core that `install` wraps. |
| `bridge agent <host>` | **goal** | Deploy a working Claude *agent* on the remote with a brief. *Composes* `claude` (env-twin) + tmux launch + status-doc + heartbeat. See F007. |

**Two design contracts that run through everything:**
- **Same-relative-path:** the remote path always matches the local path absolutely (`/Users/oblinger/ob/kmr/` ↔ same on remote). Preserves wiki-links, absolute-path references, `~/ob/...`-baked tooling, and Claude's path-keyed session lookup.
- **Per-user recipe in config, abstract goal in skill:** the skill knows the *shape* of a bridge; `~/.config/bridge/config.yaml` holds *this user's* concrete paths/hosts. **Nothing is baked into the skill or its helpers** (F262): the remote ssh/rsync login is derived from the environment (`$USER`, `getpass.getuser()` fallback) — the twin is same-user by design — never a hard-coded name. Example commands below show a concrete login (`oblinger@…`) and home path (`/Users/oblinger/…`) only for readability; substitute your own — the operative helpers already derive both. A different-username twin is an edge case handled at the user/config layer (a future `remote_user` config override), not by editing the skill.

### Config files

```
~/.config/bridge/config.yaml   # defaults + claude_environment manifest (F146/F150)
~/.config/bridge/hosts.yaml     # per-host sync state (device IDs, folders, move-aside)
```

`config.yaml`:
```yaml
version: 1
defaults: { remote: haorui.local, sync_mode: syncthing }
claude_environment:
  sync: []                                    # ADDITIONAL paths only — the vault comes from
                                              # dans-anchor-system global.yaml vault_root (F159)
  memory: shared                              # bidirectional memory share (F159); "off" disables
  claude_home:                                # ~/.claude provisioning (rsync include − exclude)
    include: [ skills, CLAUDE.md, settings.json, commands, agents, keybindings.json,
               bash-guard.sh, load-role-hook.sh, messages-stop-hook.sh, statusline-command.sh ]
    # ^ loose hook scripts referenced by settings.json MUST travel with it, or every
    #   session on the twin logs hook errors (found live 2026-06-12)
    exclude: [ projects, todos, worktrees, shell-snapshots, statsig, .DS_Store ]
  config_home:                                # ~/.config provisioning, one-way (F159)
    include: [ anchor-system ]                 # the ~/.config subdir name (plumbing), NOT the
                                               # repo identity name dans-anchor-system (F229)
    exclude: [ cache, __pycache__, .DS_Store ]
```

**The vault path is NOT duplicated in bridge config** — `claude-provision.py` reads `vault_root` from `~/.config/anchor-system/global.yaml`, the same parameter every cross-cutting skill script scopes by. Missing `vault_root` fails loudly (F159).

The helpers live at `~/.claude/skills/bridge/`: `syncthing-helper.py` (sync mechanism) and `claude-provision.py` (claude goal).

---

# Control bridge — `bridge tmux <host>`

**One command does all of this:** `~/.claude/skills/bridge/bridge tmux <host>` (F279 — renamed from `bridge mux`). It automates the whole setup below — Aqua-launched server, the on-screen viewer window, the symmetric `bridge-<host>` sessions, the capability check — and refuses to restart a server with busy panes (`--force` overrides; `--viewer` only re-throws the viewer window). The manual recipe is kept for background and troubleshooting; do **not** hand-run it when the dispatcher works.

Drive a remote machine *as if it were a local box* — sustained interactive work, FDA-bearing commands, multiplexer hand-off — via a tmux-on-this-side ⇄ tmux-on-the-other-side bridge.

Key insight: **the remote multiplexer inherits TCC from whatever launches it.** If tmux starts from a Terminal app with Full Disk Access, the tmux server has FDA, and every command in its panes inherits FDA — even when the agent attaches via SSH (which itself has no FDA). The dispatcher achieves this headlessly: it writes a `.command` to the remote and `open`s it over ssh, which launches Terminal **in the remote's Aqua session** — that window doubles as the user-glanceable viewer of everything the agent runs.

```
This Mac:                                   Remote host:
┌─ tmux session bridge-<host> ──── ssh ────► tmux session bridge-<host>
│  drive: tmux send-keys -t bridge-<host>     server launched by Terminal.app (Aqua)
└─ read:  tmux capture-pane -t bridge-<host>  → panes have FDA; window visible on remote screen
```

Legacy note: the pre-F279 pattern (`ctrl box2` + remote session `work`) is retired — the dedicated `bridge-<host>` local session replaces boxN slots for remote driving.

### Setup recipe (manual background — the dispatcher automates this)

**Step 1 — confirm SSH key-auth works.**
```
ssh -o BatchMode=yes oblinger@<host>.local 'hostname'
```
If "Permission denied", run `ssh-copy-id oblinger@<host>.local` via box (interactive password prompt; user types into tmux pane).

**Step 2 — confirm Remote Login is enabled on the remote.** If `ssh: connect to host: Connection refused`, Remote Login is off. **Tell the user**: System Settings → General → Sharing → toggle Remote Login ON. CLI route (`sudo systemsetup -setremotelogin on`) needs FDA on the calling Terminal — flaky on Tahoe. GUI is reliable.

**Step 3 — detect platform and locate the multiplexer.**
```
ssh user@host 'uname -s ; zsh -lc "which tmux ; which screen ; which brew"'
```
- **macOS (`Darwin`)**: prefer tmux, fall back to screen (built-in).
- **Linux**: prefer tmux; if absent, `which apt-get yum dnf pacman zypper` to detect distro.

**Step 4 — install tmux if missing.**
- **macOS (Apple Silicon)**: `brew install tmux` at `/opt/homebrew/bin/brew`.
- **macOS (Intel)**: `brew install tmux` at `/usr/local/bin/brew`. **Bottle may be missing on newer macOS — brew tries to compile, which needs an accepted Xcode license.** If you hit `Error: You have not agreed to the Xcode license`, either `sudo xcodebuild -license accept` via interactive box, OR sidestep brew entirely with a prebuilt binary (see § Intel/Xcode bypass under Sync gotchas — the cleaner path for packaged tools). **If sudo over SSH closes the connection**, it's silently failing on Touch-ID-only Macs — fall back to **`screen`** (always available; same FDA inheritance).
- **Linux**: `sudo apt-get install -y tmux` / `dnf install -y tmux` / `pacman -S tmux`.

**Ask the user** before installing if brew/package-manager isn't present. Don't bootstrap homebrew without consent.

**Step 5 — start the multiplexer on the remote *from a TCC-blessed Terminal*.**

> 🚨 **THE ONE CHOICE THAT DETERMINES WHAT THE BRIDGE CAN DO — get it right at setup.** Start the canonical mux session **from Terminal.app on the remote's own screen — NEVER over SSH.** This single decision is load-bearing:
> - **Terminal-launched** server lives inside the GUI/Aqua session → its panes inherit **Full Disk Access** *and* **window-server access** *and* can drive **GUI apps** (`utmctl`, AppleScript, `screencapture`/`screen.py`). This is the *full-capability* bridge.
> - **SSH-launched** server has **none** of that → `screencapture` → *"could not create image from display"*, `utmctl` → `OSStatus -1743`, `/Volumes/*` → "Operation not permitted." This trap cost a whole debugging session on haorui (2026-06-29) trying to drive a UTM VM + grab the screen over an SSH-launched bridge.
> **Do NOT** spin up a *second* server later to "add" GUI capability — make the **one** canonical server Terminal-launched from the start, so file-control, screen-vision, and GUI-app control all come from the same place.

```
tmux new -s work      # run THIS from Terminal.app ON THE REMOTE, not over ssh
```
Persists on detach (`Ctrl-B D` tmux, `Ctrl-A D` screen).

**Step 5b — grant TCC to that Terminal** (one-time, remote's System Settings → Privacy & Security): **Full Disk Access**, **Screen Recording** (for `screen.py grab`), and **Accessibility** (for `screen.py` click/type). Quit & reopen Terminal after granting so the server inherits them. Skip these and the bridge silently degrades to file-only.

**Step 6 — attach from the local side.**
```
tmux new-session -d -s bridge-<host> "ssh -t oblinger@<host>.local 'tmux attach -t bridge-<host>'"
```
From here `tmux send-keys -t bridge-<host> "<cmd>" Enter` runs inside the remote pane with full FDA; `tmux capture-pane -t bridge-<host> -p` reads back.

**Step 7 — VERIFY the bridge has the capabilities you expect — at setup AND cheaply at each (re)connect.** A bridge that *looks* up but silently lacks GUI context is the exact failure this section exists to prevent, so **test, don't assume**:
```
~/.claude/skills/bridge/screen-check.sh <host> [session]     # session default: work
```
`screen-check.sh` runs an **FDA probe** (TCC-dir read) and a **test grab** (`screencapture`) *inside the canonical mux server* — bare-SSH probes prove nothing about the server's GUI context — and reports PASS/FAIL per capability with the exact remediation (redo Step 5 Terminal-launch, or grant the Step 5b TCC permissions). `bridge-test.sh` runs it automatically as `T-ctl-screen`, so any connect-time test pass covers this. The ~3-second self-test on every connect catches a degraded bridge *before* you build work on top of it.

### Control gotchas (2026-06-06, COPPER → 10T verification)

1. **`du: /Volumes/X: Operation not permitted` over SSH** — TCC blocks SSH-launched processes from /Volumes. This bridge exists *because of* this.
2. **Granting FDA to `/usr/libexec/sshd-keygen-wrapper`** is Apple's documented fix but the Tahoe FDA pane silently failed to register it. Don't burn time there — pivot to the control bridge.
3. **macOS OpenSSH 9.8+** uses split binaries: `sshd` + `sshd-session` + `sshd-auth`. FDA may need to apply to `sshd-session`.
4. **`/usr/local/bin/brew` on Intel is NOT in the SSH non-interactive PATH.** Use the full path or `zsh -lc`.
5. **Xcode license must be accepted before brew compiles from source.** Intel + newer-macOS + missing bottles = compile required.
6. **`sudo` over SSH on Touch-ID-only Macs can silently fail** — prompt accepts password, command exits without effect. Workaround: user runs it in Terminal on the remote.
7. **macOS Tahoe (26) split `Siri & Spotlight`** into separate panes. Old guides no longer apply.

### The "disk station" pattern

Pin slow/noisy bulk ops to a dedicated remote so the user's primary surface stays responsive. **Primary Mac** stays quiet; **disk station** (older laptop with the drives attached) runs the bulk reads/writes/verifies; the control bridge drives it. Do NOT default to "move the drives to the primary machine" — confirm a quieter remote exists and propose the bridge first.

---

# Sync bridge — `bridge sync`

Per-host mode; a host has at most one sync mode at a time. Phase 1 ships **Syncthing** (eventual-convergence bidirectional, both sides keep a local copy). Phase 2 (NFS-via-symlink) and Phase 3 (rsync push/pull) deferred. Spec: `[[F122 — mux-bridge file-sync extension (Syncthing + NFS-via-symlink + rsync future)]]`.

### Subcommand surface

```
bridge sync                          # all defaults from config.yaml
bridge sync <folder>                 # override folder; default remote + mode
bridge sync --remote <host>          # override remote; default folder + mode
bridge sync-add <host> <folder>      # add another folder under host's existing mode
bridge sync-status <host>            # mode, folders, freshness, errors
bridge sync-teardown <host>          # stop syncing this host (files preserved)
```

**Three sync modes, one per host** (switching = teardown + re-init): **syncthing** (live bidirectional convergence — the default; recipe below), **nfs** (live mount, zero lag — § NFS-via-symlink mode), **rsync** (explicit push/pull batch, the hard-gate mode — § rsync mode). All three record state in `~/.config/bridge/hosts.yaml` and share the same-absolute-path contract.

### Resolution flow for `bridge sync`

1. **Read config.yaml `defaults`** — for each field not on CLI, use the default; for each missing field, prompt once and write back atomically.
2. **Read hosts.yaml** — if `<host>` already has a sync mode: probe daemons, print status. Mismatch (asked Syncthing, host is on NFS) → refuse: "run `bridge sync-teardown <host>` first." No entry → run the init recipe below.

### Init recipe (Syncthing)

The helper `~/.claude/skills/bridge/syncthing-helper.py` does the REST operations (idempotent, JSON output).

**1 — SSH reachability.** `ssh -o BatchMode=yes -o ConnectTimeout=5 oblinger@<host> hostname` (set up the control bridge first if this fails).

**2 — Syncthing on dev Mac.** `command -v syncthing || brew install syncthing; brew services start syncthing`.

**3 — Syncthing on remote.** `command -v syncthing || brew install syncthing` — **but on Intel/newer-macOS brew may hit the Xcode-license wall; use the prebuilt-binary bypass** (§ Sync gotchas). Start it: `nohup syncthing serve --no-browser &` (or `brew services start` if brew-installed).

**4 — Wait for both daemons.** Poll `http://127.0.0.1:8384/rest/system/ping` (with `X-API-Key`) on both sides until pong.

**5 — Pair devices.**
```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py pair --host "<host>"
```
Fetches API keys from `~/Library/Application Support/Syncthing/config.xml` on both sides (remote via grep+sed — **avoid `python3` on a fresh remote**, it trips the Xcode-license shim), fetches device IDs, cross-registers them. Returns `(local_id, remote_id)`.

**6 — Warn + move-aside on remote** (per F122 § Move-aside semantics — the safe default for seeding onto a machine with a *prior* copy):
```
⚠️  About to sync <folder>/ to <host>. Existing remote content moves aside to
    <folder>.old.<YYYY-MM-DD>/ ; the new empty <folder>/ receives the synced version. Proceed? [y/N]
```
```bash
ssh oblinger@<host> 'if [ -e <folder> ] && [ ! -L <folder> ]; then mv <folder> <folder>.old.$(date +%F); fi; mkdir -p <folder>'
```

**7 — Drop `.stignore`** at `<folder>/` on the dev Mac (don't overwrite an existing one):
```
.DS_Store
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
*.swp
node_modules/
.git/
.claude/
.claude.json
```
**`.claude/` and `.git/` are load-bearing excludes** — `.claude/worktrees/` alone was ~52k files / 381 MB of ephemeral runtime cruft on the test vault. **`.stignore` is per-device** — Syncthing does NOT auto-propagate it; `scp` the same file to the remote so both sides agree.

**8 — Create share** (Send-Only local / Receive-Only remote initially — directional safety on top of the move-aside):
```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py share --host "<host>" --folder "<folder>" \
  --folder-id "<id>" --local-mode sendonly --remote-mode receiveonly
```

**9 — Initial convergence.** For many small files Syncthing's block protocol crawls (~2 MB/s on a 119k-file vault — metadata-bound, not bandwidth). **Prefer the tar-seed accelerator** (§ below) over `wait-converge` for the first seed; it's ~40× faster. If using Syncthing's own path:
```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py wait-converge --host "<host>" --folder-id "<id>" --timeout 1800
```

**10 — Flip to bidirectional** (only if the user wants two-way; default-safe is to leave one-way mirror):
```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py flip-bidirectional --host "<host>" --folder-id "<id>"
```

**11 — Record + report.**
```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py record --host "<host>" --folder "<folder>" \
  --folder-id "<id>" --local-id "$L" --remote-id "$R" --move-aside "<folder>.old.<date>"
```

### Tar-seed accelerator (initial seed — strongly preferred for big/small-file vaults)

Syncthing's per-file protocol is slow for the initial seed of a many-small-files tree. When a fast link exists, seed with a single tar stream, then let Syncthing verify-and-converge:

```bash
# pause folder both sides (REST: set folder paused=true) — see helper/inline curl
tar -C ~/ob -cf - --exclude='.git' --exclude='node_modules' --exclude='.claude' \
  --exclude='.DS_Store' --exclude='.obsidian/workspace*.json' --exclude='.trash' kmr \
  | ssh -o Compression=no oblinger@<fast-link-ip> 'tar -C ~/ob -xf -'
# unpause both sides + rescan → Syncthing hashes the present files, converges near-instantly
```
Measured: **14.3 GB in ~146 s (~98 MB/s)** vs ~90 min for Syncthing's crawl. Excludes must mirror `.stignore` so the seeded set matches what Syncthing expects. Harmless tar warnings: unpackable xattrs, un-archivable sockets (e.g. `*.sock`).

### Fast-link discovery (Thunderbolt / USB-C bridge)

A **Thunderbolt** cable between two TB-capable Macs auto-creates a `Thunderbolt Bridge` (`bridge0`) interface with link-local IPs (169.254.x.x) — full TCP/IP, ~10 Gbps, no config. (A plain USB-C *charging* cable does nothing network-wise.) Verify and prefer it:
```bash
ifconfig bridge0 | grep -E 'inet |status'          # both sides; status: active
ping -c3 <remote-bridge0-ip>                        # sub-ms RTT confirms the fast link
```
Syncthing's local discovery usually picks up the bridge IP automatically — confirm via `/rest/system/connections` (`address` should be the 169.254.x.x:22000, not the wifi IP). If it doesn't, add the bridge IP as an explicit device address in Syncthing.

### `sync-status` / `sync-teardown`

```bash
python3 ~/.claude/skills/bridge/syncthing-helper.py status   --host "<host>"
python3 ~/.claude/skills/bridge/syncthing-helper.py teardown --host "<host>"   # removes shares both sides; files kept
```
Teardown also offers to remove the recorded `move_aside` directory on the remote.

### Per-session auto-resume

When `bridge <host>` runs and hosts.yaml has a sync entry: probe both daemons; restart a down one (`brew services restart syncthing` or re-`nohup`); if the remote is unreachable, warn but continue with the control session (data plane is best-effort).

### rsync mode (F175 Phase 3 — explicit push/pull, the hard gate)

**Use when** explicit batch transfers fit better than live sync — experiment dispatch, no-overhead-when-idle, or a deliberate gate between "what's on this Mac" and "what's on the remote." No daemon; nothing moves until you say so. Helper: `~/.claude/skills/bridge/rsync-helper.py`.

```
rsync-helper.py init <host> <folder> [--remote-path P]   # record mode+mapping (refuses if host has another mode)
rsync-helper.py push <host> [<folder>] [--mirror] [--dry-run]   # local → remote
rsync-helper.py pull <host> [<folder>] [--mirror] [--dry-run]   # remote → local
rsync-helper.py status <host>                            # mode + folders + last push/pull stamps
rsync-helper.py remove <host> <folder> | teardown <host> # config-only unwire; files never deleted
```

- **Never deletes unless `--mirror`** (adds `--delete`). Default push/pull is additive-overwrite (`rsync -a`), excludes `.DS_Store`/`.Trashes`/`__pycache__` plus any `--exclude`.
- Bare `push <host>` / `pull <host>` moves **all** configured folders for that host.
- Verified live 2026-07-01 against haorui (push → edit-on-remote → pull round-trip); `bridge-test.sh` runs it as `T-syn-rsync`.

### NFS-via-symlink mode (F175 Phase 2 — live mount, zero lag)

**Use when** the remote needs an instant view of this Mac's edits and both machines are on a **private network** (Tailscale / RFC1918 / .local). The remote mounts the export under `/Volumes/mb-<host>-<slug>/` and a symlink at the canonical path covers it. Helper: `~/.claude/skills/bridge/nfs-helper.py` — it **never runs sudo**; the live steps need sudo on BOTH sides, so the agent drives the emitted plan through an interactive box session where the user types passwords.

```
nfs-helper.py probe <host>                       # network class; EXIT 1 + refusal if public (NFS is unencrypted)
nfs-helper.py plan <host> <folder>               # emit the exact /etc/exports + nfsd + mount + move-aside + symlink sequence
nfs-helper.py record <host> <folder> --mount-point M   # write hosts.yaml after the plan is applied
nfs-helper.py status <host>                      # live mount probe over ssh
nfs-helper.py teardown-plan <host>               # emit the unwind sequence (files never deleted)
```

- **Public-IP remotes are refused** — probe first; the plan command refuses too.
- **Move-aside, never replace**: pre-existing remote content goes to `<path>.old.<date>/` before the symlink lands (the recovery copy).
- **Per-session auto-resume**: with nfs mode configured, `bridge <host>` should `status`-probe the mount and re-run the mount step if stale; if this Mac is unreachable within ~3s, warn and continue control-only — don't hang.

### Sync gotchas

1. **Syncthing config.xml** — `~/Library/Application Support/Syncthing/config.xml` (space in path; quote it). API key + GUI password live here. Read the apikey with `grep -E '<apikey>[^<]+</apikey>' | sed ...` — **not** `python3` on a fresh remote.
2. **REST API binds 127.0.0.1** — query the remote via SSH-wrapped curl (`ssh host 'curl -H "X-API-Key: K" http://127.0.0.1:8384/...'`). The helper uses this pattern.
3. **Intel/Xcode bypass** — `brew install syncthing` on Intel + newer-macOS tries to compile (no bottle) → `Error: You have not agreed to the Xcode license`. Even `python3` and `xcrun` trip the same one-time Command-Line-Tools license gate. **Bypass:** install Syncthing's **prebuilt binary** (no compiler): download `syncthing-macos-amd64-vX.Y.Z.zip` from GitHub releases, unzip, drop `syncthing` in `~/bin`. Cleaner than `sudo xcodebuild -license accept` for a packaged tool. (The license isn't an Intel limit per se — it's "needing the compiler"; Intel+new-macOS just lacks bottles, so it needs it.)
4. **`.stignore` is per-device, not synced** — edit it on the dev Mac AND `scp` to the remote, or each side filters differently and the global file count never reconciles. Verify a pattern took via `/rest/db/ignores` + `/rest/db/file?file=<path>` (`local.ignored` should be true) and a count drop in `/rest/db/status` `globalFiles`.
5. **Conflict files** (`*.sync-conflict-<date>-<id>.<ext>`) appear if both sides edit the same file pre-convergence. Move-aside prevents them on init; watch post-flip under bidirectional.
6. **First convergence over LAN** on a large vault: 10-30 min via Syncthing's own protocol — use the tar-seed accelerator instead.

---

# Claude bridge — `bridge claude`

**Goal:** make `<host>` able to run a Claude instance as a **twin** of this machine. It *composes* the mechanisms — `bridge sync` carries the content; an rsync provisions `~/.claude`.

A "Claude environment" = **synced content** (vault, code — rooted at dans-anchor-system `vault_root`) + **`~/.claude` minus transcripts** (skills, CLAUDE.md, settings, commands) + **shared memory** (F159) + **anchor-system config** (F159). The abstract shape is here; the concrete paths are in `config.yaml` `claude_environment`.

### Environment parity ≠ session portability

`bridge claude` provisions for **fresh** sessions on the twin. It **never** carries `~/.claude/projects/*.jsonl` transcripts. Transcripts are path-keyed (would technically `--resume` since paths are identical) but are append-heavy `.sync-conflict` generators under bidirectional sync and reference machine-local state (PIDs, tmux, background tasks) absent on the twin. **Excluded by design.** Start fresh sessions over there; the environment is what travels.

### Memory IS shared (F159)

Auto-memory lives at the harness-standard path `~/.claude/projects/<project-key>/memory/` — inside the excluded transcripts tree, so pre-F159 twins woke up without their lore. With `memory: shared`, `apply` creates a **second Syncthing folder** (`claude-memory`, path `~/.claude/projects/`, sendreceive both sides) whose `.stignore` admits ONLY memory dirs:

```
!/*/memory
!/*/memory/**
*
```

The transcripts-never-travel invariant moves from the folder boundary to the **ignore layer**: each machine's own transcripts sit in the ignored zone and never enter the shared index (verify checks the global index for `.jsonl`, not the remote disk — the twin legitimately writes its own transcripts once it runs `claude`). `.stignore` is per-device; `apply` writes it on BOTH sides before creating the share so the first scan never offers transcripts. Memory's one-fact-per-file design keeps conflict risk low; the only contested file is `MEMORY.md`, where a rare `.sync-conflict` is visible and cheap to heal. Remote learnings sync home — the twin contributes to the same lore it inherits.

### Recipe — `claude-provision.py`

```bash
# 1. See what would happen (sync coverage + include/exclude)
python3 ~/.claude/skills/bridge/claude-provision.py plan   --host <host>

# 2. Apply — rsync ~/.claude include−exclude (over the fast link if present)
python3 ~/.claude/skills/bridge/claude-provision.py apply  --host <host> [--bridge-ip <169.254.x.x>]

# 3. Verify — skills landed, projects/ did NOT
python3 ~/.claude/skills/bridge/claude-provision.py verify --host <host> [--bridge-ip <169.254.x.x>]
```

- `plan` reports vault_root, sync coverage (vault_root + `sync` extras), memory-share state, and both rsync manifests (it does **not** auto-init sync — that has its own move-aside gate; if a path is uncovered it tells you to run `bridge sync <host>`).
- `apply` rsyncs each `claude_home.include` from `~/.claude/` and each `config_home.include` from `~/.config/`, applying the excludes, over `--bridge-ip` when given; then sets up the memory share if `memory: shared` and not yet recorded (idempotent via hosts.yaml). `--delete` makes the remote a true mirror.
- `verify` confirms skills + CLAUDE.md present, **no `.jsonl` in the shared memory index**, memory share recorded, anchor-system config present → `twin_ready`.

Then `bridge <host>` (control) into the twin and run `claude` there — same skills, same CLAUDE.md, same vault, fresh sessions.

### Refresh — `bridge refresh <host>` (reconverge an existing twin)

**Goal:** pull an already-provisioned twin up to date in one shot — the routine "sync my changes over and re-provision `~/.claude`" verb. It **composes existing mechanisms, adds no first-time setup**: unlike `bridge claude` on a cold host, `refresh` assumes the sync folders and move-aside gates were already cleared, so it never re-runs init.

```bash
# reconverge content, then re-provision ~/.claude + ~/.config, then confirm
bridge refresh <host>
```

Resolution flow (each step is an existing verb — `refresh` only sequences them):

1. **Reconverge content** — `bridge sync-status <host>` to confirm the folders exist and are healthy; for Syncthing that is enough (live bidirectional already converges), for rsync mode run the explicit `bridge sync --remote <host>` push. If `<host>` has **no** sync entry, `refresh` refuses and points at `bridge claude <host>` (cold-start does the move-aside/init that `refresh` deliberately skips).
2. **Re-provision `~/.claude` + `~/.config`** — `claude-provision.py apply --host <host>` (over `--bridge-ip` when a fast link is up): re-rsyncs each `claude_home.include` and `config_home.include` include−exclude, idempotently. This is what carries new/changed skills, CLAUDE.md, settings, and the `anchor-system` config to the twin.
3. **Verify** — `claude-provision.py verify --host <host>`: skills + CLAUDE.md present, no `.jsonl` in the shared memory index, `twin_ready`.

`refresh` is the verb you reach for after editing skills or CLAUDE.md locally and wanting the twin current; `claude` is the one-time cold provision, `refresh` is every time after.

---

---

# Agent bridge — `bridge agent <host>`

Deploy a working Claude **agent** on `<host>` with a task brief. The agent runs end-to-end in a tmux session; the user views status via a vault-resident doc rendered in Obsidian on the remote. Replaces the eight-step manual recipe we ran by hand on 2026-06-23 to stand up the M1+M2 BEAST verification agent on haorui. Spec: `[[F007 — bridge agent]]`.

### When to use

Multi-hour dev-ops work (disk verification, hash sweeps, migration, anything where the laptop coordinator would degenerate into "SSH-probe every 20 minutes and hope"). Latency-to-detection of a stuck script via SSH-probing is minutes-to-hours; a local agent on the remote catches the same stall in 30 seconds — and survives whatever happens to the laptop session. See the `offload-long-devops-to-bridge-agent` memory for full motivation.

### Subcommand surface

```
bridge agent <host> --brief <path>          # standard invocation
bridge agent <host> --brief <path> --restart # tear down existing agent session, start fresh
bridge agent <host> --no-sync               # skip the push-pull step (trusted-fresh vault)
bridge agent <host> --no-layout             # skip window arrangement
bridge agent <host> --session <name>        # override the default session name (rare)
bridge agent <host> --role <path>           # override the agent's cwd (rare; default = invoker's cwd)
bridge agent <host> --model <id>            # override model (default = invoker's model)
```

### Standard tmux session — `agent`, one per host

The skill names the remote tmux session `agent` — one agent per host. Re-invoking when the session exists attaches local windows to the existing session (idempotent); `--restart` forces tear-down + fresh launch. To run a concurrent second agent on the same host (rare), `--session <name>` overrides.

### Setup recipe — composition with `bridge claude` + tmux launch + windows

The skill is the top-of-stack action; internally it calls existing bridge helpers, then does the deploy-specific work.

**Step 1 — env-twin check + provision if missing.** `python3 ~/.claude/skills/bridge/claude-provision.py verify --host <host>` to confirm `twin_ready: true`. If not, run `apply` to provision.

**Step 2 — vault freshness (push-then-pull, always).** Two-layer mechanism: Syncthing rescan-and-wait first (POST `/rest/db/scan` on both sides, poll `/rest/db/status` until convergence, 30s deadline), `rsync -a --delete` fallback if Syncthing daemon is unreachable or doesn't converge. Skill blocks on this step. `--no-sync` opts out.

**Step 3 — ensure `MY/Bridge agents/` exists + is excluded from sync and git.** On first use:
- Append `MY/Bridge agents/**` to `~/ob/kmr/.gitignore` if not present.
- Append the same to `~/ob/kmr/.stignore` on both sides (Syncthing exclude).
- `mkdir -p "~/ob/kmr/MY/Bridge agents/"` on the remote.

**Step 4 — ship the brief.** `scp <brief> oblinger@<host>:/Users/oblinger/agent-brief.md`. The brief is the spec; agent reads it on bootstrap.

**Step 5 — start tmux session + launch claude.** `ssh oblinger@<host>.local "tmux new -ds agent -x 220 -y 50 'cd <cwd> && claude'"`. Cwd defaults to invoker's cwd (path-identity invariant carries the role forward — same `CLAUDE.md` stack loads on the remote).

**Step 6 — handle /login if needed.** Capture the pane (`tmux capture-pane -t agent -p`). If "Not logged in" appears, **pause and instruct the user**: "Attach via `ssh oblinger@<host> tmux attach -t agent`, run `/login`, complete OAuth, detach with Ctrl-B D, re-run `bridge agent` to continue." One-time per host.

**Step 7 — pick model.** If invoker's model differs from the remote's default, send `/model <id>` and confirm.

**Step 8 — bootstrap prompt.** Send the prompt that tells the agent to read `/Users/oblinger/agent-brief.md` and execute. Standard text:

> You are the local SYS agent on `<host>`. Your handoff brief is at `/Users/oblinger/agent-brief.md` — read it in full, then execute end-to-end. Write status to `~/ob/kmr/MY/Bridge agents/<host> agent.md`. Use assume-and-announce (F068) for ambiguity; the user has explicitly stepped out for this task. Arm a `ScheduleWakeup` heartbeat that verifies ground-truth progress. Begin.

**Step 9 — open Terminal on the REMOTE's display + attach + screen-grab (single-shot, MANDATORY).** The agent's tmux session MUST be visible on the remote machine's own monitor so the user can walk up to `<host>` and physically see the agent working. The remote Terminal window is the primary "the agent is alive" signal; the local Terminal (step 9b) is redundant and can be skipped. **A tmux session that is only reachable via SSH — no window on the remote's Aqua display — is a spec violation.**

Use a **single self-verifying `.command` file** that (a) attaches to tmux and (b) forks a delayed screencapture in the background so the capture fires while its own tab is guaranteed to be frontmost. This pattern beats the two-file variant (`bridge-attach-*.command` + `bridge-grab-*.command`) because Terminal.app opens each `open <.command>` as a new tab that becomes frontmost — so a separate grab command reliably captures itself, not the attach tab. The single-shot pattern sidesteps the whole tab-focus race.

Per [[reference_remote_mac_gui_via_open_command]] — SSH lives in launchd Background context; `osascript`-driving Terminal.app or invoking `screencapture` from that context intermittently fails with -1712 or hits TCC prompts. An `open`-ed `.command` file runs in the Aqua session cleanly with no permission dialogs.

```bash
ssh oblinger@<host>.local 'cat > /tmp/bridge-attach-<session>.command <<EOF
#!/bin/bash
# Fork a delayed screencapture — fires while THIS tab is frontmost
(sleep 4 && screencapture -x /tmp/bridge-verify-<session>.png) &
exec tmux attach -t <session>
EOF
chmod +x /tmp/bridge-attach-<session>.command
# Quit Terminal first so this .command opens as a fresh single-tab window
osascript -e "tell application \"Terminal\" to quit" 2>/dev/null
sleep 3
open /tmp/bridge-attach-<session>.command
sleep 7   # 4s screencapture delay + 3s buffer
'
scp oblinger@<host>.local:/tmp/bridge-verify-<session>.png /tmp/bridge-verify-<session>.png
```

**Verify by Reading the screenshot.** Expected: a Terminal window on the remote's screen showing tmux content (claude's prompt banner + working output + tmux status bar naming the session). **If the screenshot does not show the Terminal window OR does not show recognizable tmux content, the bridge is not fully deployed** — halt and surface to the user with the specific failure. Do NOT declare deploy successful without this verification.

**Step 9b — open local Terminal + attach (OPTIONAL — for laptop-side visibility).** `open -a Terminal` on the *laptop* with a fresh window running `ssh oblinger@<host>.local "tmux attach -t <session>"`. Useful when the user works from the laptop most of the time; can be skipped when the primary interaction is walking up to the remote. Skipped by `--no-local-terminal`.

**Step 10 — open Obsidian on the remote** showing the status doc. `ssh oblinger@<host>.local 'open -a Obsidian "~/ob/kmr/MY/Bridge agents/<host> agent.md"'`.

**Step 11 — verification is baked into Step 9.** The screenshot from the embedded delayed screencapture is the deploy-successful gate. Re-invoke Step 9 (which is idempotent — the .command file is rewritten each time) to re-verify at any point during the mission.

Common failure modes the screen-grab catches:

- No active user session on the remote (user is logged out / on the login screen) — screenshot shows the loginwindow or an empty desktop.
- The remote is in a locked state (`screencapture -x` produces a black frame).
- Terminal.app failed to launch (screenshot shows the desktop but no Terminal window).
- Terminal opened on a different Space than the visible one (screenshot shows a desktop other than the one with Terminal on it).

Each of these needs a different remediation (log the user in, unlock, retry the launch, switch Space) — surface the specific case, not a generic "deploy failed."

**Step 12 — arrange windows on the laptop.** `osascript` to position: local Terminal (if opened via 9b) middle column (~33% width × ~60-70% height, centered), local Obsidian right column (~33% width × full height, anchored right). `--no-layout` skips.

**Step 13 — stand down banner.** Print: `WORKING — agent on <host> owns task; tmux visible on <host>'s display; coordinator polling on demand.`

### Brief format — YAML frontmatter + redundant body-top table

YAML for the skill to parse (`mission` required; `status_doc` / `heartbeat` / `role` optional overrides). The body opens with a redundant markdown table mirroring the same fields as wiki-links — the user reads the table in Obsidian (frontmatter isn't visible in rendered mode).

Canonical template at `~/.claude/skills/bridge/templates/brief-template.md` — start there for new briefs. Body content: Mission / Current state snapshot / File inventory / Hard rules / Status protocol / Escalation / First action.

### Status doc — one canonical doc per host at a computed path

`~/ob/kmr/MY/Bridge agents/<host> agent.md`. The skill creates the folder + the gitignore + the stignore entries on first use. One doc per host; subsequent tasks overwrite. Brief's frontmatter MAY override the path via `status_doc:` for unusual cases.

Canonical format (template at `~/.claude/skills/bridge/templates/status-doc-template.md`):

- H1 + dim italic timestamp line
- **Three one-line headlines** at top — one per phase or workstream — each `<emoji> <phase> <verb> — <X/Y> · <key info> · ETA <when>`. Emoji vocabulary: `🟢 progressing` / `🟡 slow` / `⏸ paused` / `🟠 stalled` / `🔴 attention` / `✅ complete`.
- `## ATTENTION` H2 only when user input is needed. Format: `**Recommended action:** … · **Why:** … · **Decision needed from you:** … · **If we wait:** …`.
- `## Now` (one short line — current activity).
- Detail sections below the fold.

### Status doc transport — SSH-pull on demand; NOT Syncthing; NOT git

The status doc churns on every heartbeat. We don't want that in git history or Syncthing's conflict tracking. **The doc is gitignored + stignored + lives only on the remote** (write-side). Primary user-facing surface: the remote's Obsidian, which the layout step also opens.

When the laptop coordinator agent (the SYS agent on the invoking machine) needs the status — typically because the user asked — pull on demand:

```
ssh oblinger@<host>.local 'cat "~/ob/kmr/MY/Bridge agents/<host> agent.md"'
```

The pull populates the coordinator's chat summary. The coordinator never writes a local copy — that would just be stale. Optional follow-up: a periodic `launchd` that `scp`'s every N minutes for laptop-side Obsidian viewing; out of scope for v1.

### Heartbeat — hard convention while there's active work

The remote agent owns its own heartbeat rate via `ScheduleWakeup`. **Whenever there's active work in flight, a heartbeat MUST be armed** — non-optional. Standard ranges (agent picks):

- 60-300s during setup / first targets / OAuth pause
- 1200-1800s during steady-state (20-30 min)
- 30-600s during final wind-down / waiting on a single long target

Every heartbeat verifies *ground-truth* progress (results file row count advancing, log mtime moving, in-progress process alive), regenerates the status doc, and console-prints a one-line `WORKING — ...` banner. No progress between two heartbeats → `🟠 stalled` in the headline + investigate.

### Idempotency

| Re-invoke scenario | Behavior |
|---|---|
| Same host, `agent` session running | Attach local Terminal + Obsidian to existing; print `Reusing existing agent on <host>`. No new launch. |
| Same host, `agent` running + `--restart` | Kill, re-ship brief, fresh launch. |
| Same host, no session | Full setup as if first invocation. Vault sync runs. |
| Different host | Independent — each host has its own `agent` session. |

### Gotchas (live, from the 2026-06-23 hand-run)

- **`tmux capture-pane -p`** sometimes returns empty when the pane is in TUI alternate-screen mode. Use `-S 0 -E -` to capture the visible buffer fresh.
- **OAuth URL line-wrapping** in `capture-pane` output can mangle the `state` parameter if you try to reassemble the URL programmatically. That's why the OAuth UX is "pause + instruct the user to attach and click locally," not "extract URL and open in laptop browser."
- **`zsh` on the remote eats `==`** in pipelines (zsh equal-expansion). Use single-quoted or escaped markers like `--- HEADER ---` instead of `=== HEADER ===` in SSH-wrapped probes.
- **Uninterruptible I/O wait on a bad-sector path** (e.g. BEAST corruption on the M1+M2 run) can leave a bash process unresponsive to SIGTERM. `kill -9` works only sometimes; the cleanest recovery is to kill the tmux session entirely. Briefs should specify per-target timeouts to prevent this from blocking the whole run.

---

## When NOT to use bridge

- One-shot read on a non-TCC path → plain `ssh user@host 'cmd'`.
- One-shot op on a TCC path → have the user run a self-contained script in their Terminal that writes to `/tmp/`, then SSH-read `/tmp/`.
- One-time file push with no ongoing mirror → `rsync`/`scp` directly (sync-bridge is for a *standing* mirror).
- Quick remote command that takes < 30 minutes — overhead of `bridge agent` not worth it; just SSH-probe.

## Status

**Active** (F150, 2026-06-11). Control plane captured 2026-06-06 (COPPER → 10T). Sync (Syncthing) + Claude bridge built and **verified live against haorui.local** 2026-06-11: 14.4 GB vault seeded via tar over a Thunderbolt bridge, `.claude/` excluded both sides, `bridge claude` provisioned 65 skills + CLAUDE.md with `projects/` excluded (`twin_ready: true`). Renamed from `mux-bridge`; helpers at `~/.claude/skills/bridge/`; config at `~/.config/bridge/`. NFS (Phase 2) and rsync (Phase 3) still deferred per F122.

**F159 (2026-06-12)** — Claude bridge grew three layers, all verified live against haorui.local: vault path derived from dans-anchor-system `vault_root` (removed from bridge config); bidirectional **memory sharing** via the `claude-memory` ignore-filtered share (two-way probe converged ~15s each direction; shared index verified `.jsonl`-free while haorui's own transcripts stayed local); one-way **anchor-system config** provisioning. Full F151 harness: 10 pass, 0 fail. Known gap (out of scope): `~/bin` shell tools (`ctrl`, `ha`, `exp`) referenced by the synced CLAUDE.md are machine installs and don't travel.

**F007 (2026-06-23)** — Agent bridge added. The `bridge agent <host>` subcommand composes `bridge claude` (env-twin) with a deploy step: env-check → vault push-pull → ensure `MY/Bridge agents/` git+stignored → ship brief → tmux launch with cwd identity → /login pause-and-instruct if needed → model pick → bootstrap prompt → local Terminal + Obsidian opens → window arrangement → coordinator stands down. Status doc convention: one canonical doc per host at `~/ob/kmr/MY/Bridge agents/<host> agent.md`, gitignored, transported by SSH-pull on demand (never Syncthing, never git). Heartbeat is a hard convention while work is active. Templates at `~/.claude/skills/bridge/templates/`. Hand-run dress rehearsal: M1+M2 BEAST verification on haorui (the recipe was extracted from that experience).
