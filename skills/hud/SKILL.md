---
name: hud
description: >
  Put a vault document on a HUD — one of the secondary Obsidian instances
  (HUD, HUD2, HUD3, HUD4) — without touching the user's primary Obsidian.
  HUD2/3/4 belong to the ASR2/ASR3/ASR4 seats; every other agent uses
  plain `glance` and only touches a HUD when the user names one.
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
| `HUD2` | `md.obsidian.hud2` | **[[ASR2]]'s.** Seat N drives HUD N — the one standing assignment in the vault. |
| `HUD3` | `md.obsidian.hud3` | **[[ASR3]]'s.** Same scheme. |
| `HUD4` | `md.obsidian.hud4` | **[[ASR4]]'s.** Same scheme. |

> 🚦 **The ASR seats are the ONLY standing assignment. Every other agent just uses `glance` and never touches a HUD unless Dan names one in the session.**
> Reaffirmed by Dan 2026-08-28, narrowing the 2026-08-25 correction rather than reversing it. The 2026-08-25 problem was never that the seats had HUDs — it was everyone *else* drifting onto them: *"a lot of agents are writing to HUD2… agents that weren't even around when we created these things."* So the rule is not "no reserved instances," it is **these three anchors, by seat number, and nobody else.** If you are not a session whose working directory is `LRN ASR/ASR2`, `ASR3`, or `ASR4`, do not pick a HUD for yourself — Dan will tell you.

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
