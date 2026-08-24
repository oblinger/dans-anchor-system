---
name: hud
description: >
  Put a vault document on a HUD — one of the secondary Obsidian instances
  (HUD, HUD3, HUD4) — without touching the user's primary Obsidian.
  Use when the user says "glance X to the HUD", "show X on HUD3", "put this
  on my HUD", or when an agent needs its own display surface to show vault
  docs. Also covers creating more instances and repairing existing ones.
tools: Bash, Read
user_invocable: true
---

# HUD — secondary Obsidian display surfaces
requires:: vault, external:hud-cli

Deep wiring: [[WIRE HUD]] · mechanism detail: [[HUD Architecture]].

## The instances

| Instance | Bundle id | Owner |
|---|---|---|
| `HUD` | `md.obsidian.hud` | **Dan** — his F1/F4 glance surface. Agents may *deliver* docs to it (that is what "glance to the HUD" means) but never rearrange it. |
| `HUD2` | `md.obsidian.hud2` | **ASR2's.** Minted 2026-08-23 so the seat number and the surface match — seat N drives HUD N. |
| `HUD3` | `md.obsidian.hud3` | **Agent-ownable.** A session may claim it as its display surface and drive it freely — open docs, change what is shown — without colliding with Dan's windows or other agents'. |
| `HUD4` | `md.obsidian.hud4` | **Agent-ownable.** Same as HUD3. |

All instances display the SAME vault content (each `~/ob/data/<NAME>` is a plain symlink to `~/ob/kmr`), with isolated app identity, window state, and workspace. Primary Obsidian stays reserved for Dan's deep reading and editing — never drive it.

## Showing a document

```bash
hud <file-or-name>              # → HUD (Dan's), NEW TAB, no focus steal
hud <file-or-name> --on 3      # → HUD3   (also --on 4, --on hud4)
hud <file-or-name> --focus     # bring that HUD to the front
hud <file-or-name> --solo      # open it, then close every other tab
hud --list                      # instances + running state
```

Opening always lands in a **new tab** (`paneType=tab` on the URL) — it never replaces what the surface already shows; `--solo` is the explicit clear-to-one-tab gesture. Bare names resolve via `ha -p`. Delivery is `open -g -b <bundle> "obsidian://open?vault=<NAME>&file=<rel>"` — the explicit bundle target means the event can never land in the user's primary Obsidian. The `obsidian-hud*://` schemes route to the right app but are NOT an open channel (the in-app parser ignores foreign schemes) — always deliver via `-b`.

## Claiming an instance

There is no lease mechanism (deliberately — two agent-ownable instances, low collision odds). Claim by using it, and publish the claim on your status line (`statusline --hud=3`) so other sessions can see it. If both are visibly claimed, ask rather than evict.

## The control channel

Each instance's injected preload watches `~/.config/hud/cmd-<inst>.json` (`hud`, `hud3`, `hud4`); when its mtime advances it runs the named Obsidian command and writes `…json.out` with the resulting markdown-tab count — e.g. `{"cmd": "workspace:close-others"}` is how `--solo` works, and a bogus id like `{"cmd": "hud:noop"}` is a harmless way to read the tab count. Instances installed before 2026-08-24 need `HUD-install.py --name <NAME> --update` + a relaunch to carry the watcher.

## Verifying what a HUD shows

The window title is the reliable channel (workspace.json is lazily written):

```bash
osascript -e 'tell application "System Events" to name of front window of process "HUD3"'
```

## Creating / repairing instances

Installer: `~/ob/grove/commons/wire/HUD-install.py` (idempotent).

```bash
python3 HUD-install.py --name HUD5           # mint another instance
python3 HUD-install.py --name HUD3 --update  # refresh app after an Obsidian auto-update
```

`--name` derives everything: `~/Applications/<NAME>.app`, bundle id `md.obsidian.<lower>`, scheme `obsidian-<lower>://`, userData `~/Library/Application Support/<lower>`, vault symlink `~/ob/data/<NAME>` → kmr, and config dir `.obsidian-<lower>` inside kmr (seeded automatically via a localStorage preload injected into the app — no UI step). After minting a new instance, add it to the `INSTANCES` table in `~/bin/hud` and to the table above. After each Obsidian auto-update, every instance needs its own `--update` run.

Disk cost per instance: ~441 MB app + up to ~1 GB Electron cache over time; vault content costs nothing.
