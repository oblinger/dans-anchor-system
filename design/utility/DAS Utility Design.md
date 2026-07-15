---
description: Subsystem design for the Utility group — machine access (local, remote, GPU, GUI), capture pipelines (voice, text), and life utilities; always available, no anchor trait.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [design](hook://design) → [DAS Utility Design](hook://p/DAS%20Utility%20Design)
# DAS Utility Design — the design of the Utility subsystem
Utility is the grab-bag subsystem, organized as three clusters: **Connection** (reach other machines — bridge, exp), **Machine control** (drive this one — ctrl, screen, get-user-auth), and **Productivity** (the little tools — vox, muse, snip, cook, atlas). No anchor trait declares them; they are always available.

![[DAS Utility Design.svg|3000]]

| **Skills**                              |                                                                                                                |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| *Connection*                            |                                                                                                                |
| [[bridge/SKILL\|/bridge]]               | Connect to another machine — control (SSH+tmux+TCC), sync (Syncthing/NFS/rsync), claude (env-twin).             |
| [[DAS Exp\|/exp]]                       | Remote experimentation — ML workloads on ephemeral vast.ai GPU workers; the `zap` dispatch.                     |
| *Machine control*                       |                                                                                                                |
| [[DAS Ctrl\|/ctrl]]                     | Local environment control — persistent `box` tmux session, browser surf, bot-wall-beating `cpage`.              |
| [[screen/SKILL\|/screen]]               | See and drive a Mac's screen — grab + click + type, locally or over the bridge.                                 |
| [[get-user-auth/SKILL\|/get-user-auth]] | Route an auth prompt to the user's GUI session — keychain, sudo, 2FA, trust dialogs — and verify it landed.     |
| *Productivity*                          |                                                                                                                |
| [[vox/SKILL\|/vox]]                     | File voice-memo audio with whisper-transcribed siblings into the VOX folder.                                    |
| [[muse/SKILL\|/muse]]                   | Watch-first dictation pipeline — launchd sweep ingests recordings into `Log/MUSE` for review-and-do.            |
| [[DAS Snip\|/snip]]                     | Capture rough text drops and iteratively refine them — versioned newest-on-top.                                 |
| [[DAS Cook\|/cook]]                     | Recipe-aware shopping/staging list from Paprika.                                                                |
| [[atlas/SKILL\|/atlas]]                 | Maintain the vault-wide glossary/router ([[Atlas]]) — routing, not duplication.                                 |
|                                         |                                                                                                                |
| **Facets**                              |                                                                                                                |
| *(none owned)*                          | Utility's outputs land in existing shapes — `Log/` streams (Tracking), Topic docs, VOX/MUSE folders.            |
|                                         |                                                                                                                |
| **Traits**                              |                                                                                                                |
| *(always on)*                           | Utility verbs operate on the machine and the outside world, not on anchor shape — no trait declares them.       |
|                                         |                                                                                                                |
| **Library**                             |                                                                                                                |
| **`ctrl` / `exp` CLIs**                 | The shell engines under the skills — `ctrl box/surf/cpage`, `exp init/exe/push/pull` (config `~/.config/exp/`). |
| **Bridge config**                       | Per-user machine recipes at `~/.config/bridge/config.yaml`.                                                     |
| Rulesets                                | [[R-mac]] · [[R-ob]] (owner-scoped umbrella: [[R-ob-remote-ops]] · [[R-ob-cmd-proc]] · [[R-ob-observability]] · [[R-ob-state-mgt]]) |

## Overview

Utility's contract: **the agent reaches everything itself — the user is never the remote control.** The **Connection** cluster extends the agent to other machines: `/bridge` at three depths (control, sync, full Claude env-twin), `/exp` to ephemeral GPU workers. The **Machine control** cluster drives whatever machine it's on: `/ctrl` owns the local environment (persistent tmux `box`, real-browser page fetches past bot walls), `/screen` gives the agent eyes and hands on any GUI, and `/get-user-auth` handles the one thing the agent genuinely can't supply — a credential — by raising the prompt on the user's screen and verifying it landed. The **Productivity** cluster is the little tools that pull the user's raw material into the vault and keep it usable: voice (`/vox`, `/muse`), rough text (`/snip`), the vault-wide router (`/atlas`), and `/cook` as the archetypal life utility. Long-running work here rides the heartbeat discipline: status + ETA on every tick, progress-based (never wall-clock) termination.

Boundaries: **Utility is reach, other groups are purpose** — `/buy` (Search) and remote disk work (SYS) *use* `/ctrl` and `/bridge`; the destination subsystem owns the task. **Capture ends at filing** — `/muse` and `/snip` land content in the vault; what the content *spawns* (features, questions) goes through Drive and Tracking. **Machine setup is Anchor's `/install`** — Utility assumes an installed environment.

## Coordinated examples

Utility is illustrated by its own live infrastructure — the standing `box` tmux session, the `~/.config/bridge/` and `~/.config/exp/` machine recipes, and the `Log/MUSE` ingestion stream.

## Design record

- [[DAS Ctrl Design]] · [[DAS Exp Design]] · [[DAS Snip Design]] · [[DAS Cook Design]] · [[DAS Parley Design]] — per-verb design docs.
- **Grouping (agent, 2026-07-14):** `/bridge`, `/screen`, `/get-user-auth`, `/vox`, and `/muse` — previously ungrouped — assigned here at this profile pass. `/devops` went to [[DAS Code Design|Code]] (build/deploy focus).
- **Subgroup revision (user, 2026-07-14):** the group organizes into three clusters — Connection (bridge, exp), Machine control (ctrl, screen, get-user-auth), Productivity (vox, muse, snip, cook, atlas) — rendered as containers in the figure.
- **Membership revisions (user, 2026-07-14):** `/atlas` moved in from Doc (it maintains the vault, it doesn't author documents). `/parley` moved out — its products are Discussion/Decisions artifacts, so it went to [[DAS Design Design|Design]] (agent call; user's first instinct was Drive — one-line move if preferred).
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Utility Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
