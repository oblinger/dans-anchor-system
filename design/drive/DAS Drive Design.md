---
description: Subsystem design for the Drive group — the autonomous-execution loop that consumes Ready work (crank → mint → finalize), the feeders that mint new work, and the bounded stop.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Drive Design](hook://p/DAS%20Drive%20Design)
# DAS Drive Design — the design of the Drive subsystem
Drive is the execution subsystem: it consumes what Tracking surfaces as Ready and turns it into shipped, committed work — `/crank` loops for maximum progress, `/mint` executes one item, `/finalize` closes it out — with `/feature` and `/change` minting new work in, `/fortify` for when iteration stops converging, and `/land` as the bounded stop.

![[DAS Drive Design.svg|3000]]

| **Skills**                         |                                                                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [[DAS Crank\|/crank]]              | The outer loop — maximum progress through Ready work; quality drop is the only stop. Trigger: `'`.                  |
| [[DAS Mint\|/mint]]                | Execute one ready item — read the spec, build, test, verify, commit.                                                |
| [[DAS Finalize\|/finalize]]        | Close out a unit of work — verify, commit, docs, status, cleanup. Consumed by /land and /crank.                     |
| [[DAS Land\|/land]]                | Bounded crank — finish everything in flight, commit, stop; start nothing new. Trigger: `.`.                         |
| [[DAS Fortify\|/fortify]]          | Skeptical counterpart to crank — when fixes don't stick, distrust everything and verify from ground truth.          |
| [[DAS Feature\|/feature]]          | Feature lifecycle — mint an F-row + feature doc, drive Designing → Agreed → Done through the user gate.             |
| [[change/SKILL\|/change]]          | OpenSpec-style sibling of /feature — mint a C-row + `changes/C###-slug/` folder (F230).                             |
|                                    |                                                                                                                  |
| **Facets**                         |                                                                                                                  |
| *(consumed, not owned)*            | Drive executes against Design's [[DAS Features\|Features]] docs and Tracking's [[DAS Backlog\|Backlog]] rows — it owns no document shape of its own. |
|                                    |                                                                                                                  |
| **Traits**                         |                                                                                                                  |
| [[drive]] · [[lean]]               | The autonomy modes — how aggressively the agent auto-decides (assume-and-announce per [[F068 — Assume-and-announce discipline (Drive mode)\|F068]]) vs. asks. |
|                                    |                                                                                                                  |
| **Library**                        |                                                                                                                  |
| **Punctuation triggers**           | `'` = /crank, `.` = /land, `"` = /ask — single-keystroke go/stop/consolidate, wired in the global CLAUDE.md.        |

## Overview

Drive's contract: **stopping is the costly action, not continuing.** `/crank` is the go button: it sequences as many Ready items as it can — parallelizing independent ones — and may stop only when the next mint would drop quality; its hard continuation rule requires an explicit, specific risk-of-continuing argument before any stop, and its exit cascade routes through `/groom` then `/ask` so a stop always leaves the user a current queue file, never a dangling chat question. `/mint` is one turn of the crank; `/finalize` is the close-out discipline both ride; `/land` inverts the posture — finish what's in flight, commit, start nothing. `/fortify` handles the pathological case where normal iteration loops without converging. New work enters through `/feature` (F-rows with feature docs and the user-agreement gate) and `/change` (C-rows in the OpenSpec layout). The `drive` and `lean` traits set the autonomy mode: visible + low-recoverability decisions are auto-decided and announced, everything else becomes a parked question.

Boundaries: **Tracking supplies the queue and takes the questions** — Ready rows come from Tracking's surfaces, every mutation goes through its `state` CLI, and Drive's stops hand residual questions to `/ask`'s pile. **Design supplies the specs** — feature docs are Design artifacts; Drive executes them and stamps their status. **Code supplies the craft** — when the ready item is code, `/mint` dispatches into the Code verbs.

## Coordinated examples

Drive is illustrated by any anchor's live backlog history — the [[SKA Backlog]] itself is a long record of crank/mint/land cycles over F- and T-rows.

## Design record

- [[DAS Crank Design]] · [[DAS Crank PRD]] · [[DAS Mint Design]] · [[DAS Mint PRD]] · [[DAS Finalize Design]] · [[DAS Finalize PRD]] · [[DAS Land Design]] · [[DAS Land PRD]] · [[DAS Fortify Design]] · [[DAS Fortify PRD]] · [[DAS Feature Design]] · [[DAS Feature PRD]] — per-verb design docs.
- **Grouping (agent, 2026-07-14):** `/change` — previously ungrouped — assigned here as `/feature`'s sibling at this profile pass.
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Drive Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
