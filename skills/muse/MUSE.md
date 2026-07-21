---
aliases: [Muse]
description: Voice-memo ingestion + review-and-do pipeline — watch/phone recordings become inbox items, executed via Claude in a tmux session.
---
# MUSE
The service that turns spoken thought into acted-on knowledge. A ~~[[skills|Claude skill]]~~ with two entry points: **`muse ingest`** runs headlessly when a new voice recording lands (via `launchd`) — transcribes it, writes an item file to the permanent archive at `~/ob/kmr/Log/MUSE/`, and prepends a bullet to the [[Quick]] pane. **`/muse do <path>`** runs in Claude Code when typed with an item path — reads the item and proposes an action for the user to approve.

| -[[MUSE]]- | → [[kmr]] → [[SYS]] → [[symlinks]] → [SKL](hook://SKL) → [MUSE](hook://p/MUSE)<br>: Voice-memo ingestion + review-and-do pipeline |
| --- | --- |
|  | [[Log Muse\|Log]],  [[WIRE Muse\|Wire]],   |
| ~~[[MUSE Design\|Design]]~~ | → [[MUSE Architecture\|Architecture]] — flows, action space, safety, config, build order |
| Shape | Claude skill at `~/.claude/skills/muse/` — two sub-verbs `ingest` (headless) and `do` (in-Claude slash command) |
| Sources (current) | [[MACAPP Just Press Record]] — Apple Watch dictation via iCloud |
| Sources (planned) | Voice Memos, Superwhisper direct capture, ad-hoc `.m4a` drop |
| Archive | `~/ob/kmr/Log/MUSE/` — item files land as `MUSE YYYY-MM-DD X <title>.md`, **never pruned** |
| Log | `~/ob/kmr/Log/MUSE/Log Muse.md` — dated bullet per ingest, newest first; suppressed items appear here too (audit trail) |
| Quick pane | `~/ob/kmr/LST/Quick.md` — MUSE prepends a bullet per ingest (raw text when transcript ≤ `MUSE_INLINE_MAX_CHARS`, default 80; else a Markdown link back to the item file). Suppressed items skip Quick. |
| Review | Type `/muse do <path>` into the SYS Claude session; Claude reads the item, proposes an action, waits for approval. (GUI hotkey binding is designed but deferred — see ~~[[MUSE Design\|Design]]~~ § Do flow.) |
| Status | ✅ **Live** — `muse ingest` running, items land in `~/ob/kmr/Log/MUSE/`, Quick.md bulleted, `/muse do` slash-command available. HUD Cmd+Opt+D binding deferred (invocation is by typing the slash command). Shipped as [[F018 — MUSE — Watch-first voice-memo pipeline (ingest + do)]] on 2026-07-13. |
| ... | [[F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)]],  [[MUSE Backlog\|Backlog]],  [[MUSE Messages\|Messages]],  [[muse/SKILL]],   |


## Overview

MUSE owns the whole path from "voice recording arrives on disk" to "the world reflects what the recording asked for." Split into two entry points so the machine work is fast and unattended, but the *interpretation* work always has a human watching:

- **Machine side** (`muse ingest`) — headless, tool-less. Strips quarantine, transcribes via `_transcribe`, derives a short title via `_askAI`, files the item into the Quick pane + Log Muse index, fires a macOS notification. Safe to leave automatic.
- **Human side** (`/muse do`) — invoked when the user hits a hotkey in [[HUD]]. The wrapper activates the terminal and injects the slash command into the SYS tmux session; Claude Code becomes the review UI, proposing action and asking approval before touching anything.

MUSE is **not** a recording app — that's [[MACAPP Just Press Record]] on the watch/phone/Mac. MUSE is **not** an autonomous agent — every action Claude proposes goes through a normal Claude Code tool-call approval prompt.

Full flows, action space, safety analysis, config surface, and implementation order: **[[MUSE Architecture]]**. Wire-side integration only (iCloud sync, launchd trigger, quarantine handling): **[[WIRE Muse]]**.


## History

- **2026-06-30** — Named MUSE. Emerged from a "did the watch recording sync?" debug session that surfaced two adjacent problems: (a) iCloud sync working end-to-end, (b) Gatekeeper quarantine impeding downstream use of every arriving `.m4a`. Same day: architecture converged from "shell script + custom TUI" through "second-vault review surface" to the current **skill + demon + tmux-inject** design, with the second-vault concept split off into its own anchor [[HUD]]. Design captured in [[MUSE Architecture]].
- **2026-07-15** — Canonical page migrated from `SYS/WIRE/MUSE/MUSE.md` to `~/.claude/skills/muse/MUSE.md`. Wire folder collapsed into a single [[WIRE Muse]] facet doc (iCloud + launchd plumbing only). MUSE stands as its own anchor rather than a sub-anchor of [[WIRE]]. Motivation: MUSE outgrew the "wire integration" framing — it's a full service (transcription pipeline + archive + review skill) that happens to be *triggered* by a wire event, not defined by it. Same pass: MUSE Inbox.md renamed to [[Log Muse]] (avoids two files named `MUSE`).
