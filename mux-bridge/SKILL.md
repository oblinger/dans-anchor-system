---
name: mux-bridge
description: Set up a terminal-multiplexer bridge between this machine and a remote host so the agent can drive the remote machine via `ctrl box2` (or boxN) with full TCC inheritance. Use when an SSH-only session can't access TCC-protected paths on the remote (e.g. /Volumes/*, ~/Desktop, ~/Documents) and the agent needs to run commands as the user with that user's Full Disk Access. Slash-only — invoked via `/mux-bridge <host>`.
---

# MUX Bridge

## Purpose

When the agent needs to drive a remote machine *as if it were a local box* — sustained interactive work, FDA-bearing commands, multiplexer hand-off — set up a tmux-on-this-side ⇄ multiplexer-on-the-other-side bridge.

Key insight: **the remote multiplexer inherits TCC from whatever launches it.** If the user starts tmux/screen from a Terminal app with Full Disk Access, the multiplexer server has FDA, and every command run in its panes inherits FDA — even when the agent attaches via SSH (which itself has no FDA).

## Architecture

```
This Mac:                          Remote host:
┌─ ctrl box2 (tmux) ──────────────────────── ssh ─────────────────────────► tmux/screen `work` session
│  agent drives via ctrl box2 "cmd"        FDA inherited from Terminal.app launch
└─ outbox2 reads back stdout            commands run inside have FDA
```

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

## Status

DRAFT — captured 2026-06-06 during live COPPER → 10T backup verification. Pre-existing observations from that session baked in. To refine as more remote-machine work surfaces additional patterns.
