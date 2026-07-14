---
description: Subsystem design for the Code group — the verbs that plan, write, test, and ship code against an anchor's Sparse-Linked repo, keeping design and docs vault-side.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Code Design](hook://p/DAS%20Code%20Design)
# DAS Code Design — the design of the Code subsystem
Code is the code-work subsystem: its verbs carry a change from spec through implementation, testing, and release against the anchor's linked repo (`code:` → `~/ob/proj/…`), while the design artifacts and documentation stay vault-side.

![[DAS Code Design.svg|3000]]

| **Skills**                             |                                                                                                                      |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [[DAS Code Skill\|/code]]                | The umbrella verb — spec, plan, execute, test, ship, plus delegate / spike / bugfix / forge sub-actions.             |
| [[DAS Fix\|/fix]]                      | Fix common environment problems — permissions, auth, session config.                                                 |
| [[DAS PR Flow\|/pr-flow]]              | Iterative PR-based development — each PR a reviewed feature unit.                                                    |
| [[DAS Pilot Flow\|/pilot-flow]]        | Top-down flow — PRD → System Design → Roadmap → implementation.                                                      |
| [[cleanup/SKILL\|/cleanup]]            | Sweep every git worktree, remove the safe ones, certify the current one abandonable.                                 |
| [[module-doc/SKILL\|/module-doc]]      | Author a module documentation page from source, conforming to the Module Doc facet.                                  |
| [[devops/SKILL\|/devops]]              | Long-horizon operational work — remote builds, deployments, test-machine drives — under heartbeat discipline.        |
|                                        |                                                                                                                      |
| **Facets**                             |                                                                                                                      |
| [[DAS Code\|Code]]                     | The code-anchor shape — how an anchor that carries software is laid out.                                             |
| [[DAS Code Repository\|Code Repository]] | The linked repo's required surface — README, tests, CI, release conventions.                                       |
| [[DAS Module Doc\|Module Doc]]         | Per-module documentation page — SECTIONS table, per-class tables, method details.                                    |
| [[DAS CLI\|CLI]]                       | Command-line interface conventions for shipped tools.                                                                |
| [[DAS Changes\|Changes]]               | The OpenSpec-style `changes/` + `specs/` layout (F230) — C-numbered change folders.                                  |
|                                        |                                                                                                                      |
| **Traits**                             |                                                                                                                      |
| [[Code Anchor]]                        | Declares the anchor carries software; activates the `code:` link and this group's verbs.                             |
| [[commit]] · [[push]] · [[pr]] · [[nogit]] | Git-behavior traits — how autonomously the agent commits, pushes, or PRs in this anchor.                         |
|                                        |                                                                                                                      |
| **Library**                            |                                                                                                                      |
| Disciplines                            | [[DAS code-repo]] · [[DAS rust]]                                                                                     |
| Rulesets                               | [[R-code]] · [[R-code-mirror]] · [[R-code-repository]] · [[R-code-surface]] · [[R-git]] · [[R-cli]] · [[R-wrapper-cli]] · [[R-versions]] · [[R-module-doc]] · [[R-all-files]] · [[R-changes]] · [[R-specs]] · [[R-openspec]] · [[R-test]] · [[R-testing]] · [[R-dev-dispatch]] · [[R-mac]] · [[R-ios]] |

## Overview

Code's contract: **code lives in the repo, understanding lives in the vault.** The anchor's `.anchor` `code:` key points at the real git repo (`~/ob/proj/…`, Sparse-Linked per [[SKA Decisions]] D12); `/code` runs the work loop against it — read the spec, plan, execute, test, ship — with its sub-actions covering the specialized moves (parallel delegation, root-cause spikes, red-green bugfixes). `/pr-flow` and `/pilot-flow` are the two collaboration shapes (iterative-reviewed vs. top-down-from-design); `/module-doc` writes the vault-side module pages from source so the documentation tracks the code; `/cleanup` keeps the worktree population safe; `/devops` carries the long operational tail (builds, deploys, test machines) under the heartbeat discipline. The git-behavior traits (`commit`, `push`, `pr`, `nogit`) declare per-anchor how autonomously the agent lands work.

Boundaries: **Design authors what Code builds** — PRDs, architecture, and specs are Design-subsystem artifacts; Code consumes them (the pilot-flow runbook walks Design's pipeline before touching code). **Anchor owns the marker vocabulary** — `code:` and `mirror:` are `.anchor` keys defined by the Anchor group; Code exercises them. **Drive sequences the work** — `/crank` and `/mint` decide *when* a Dev task runs; Code's verbs are what they dispatch into.

## Coordinated examples

Code is illustrated by the live Sparse-Linked anchors themselves — e.g. [[KM]] and [[ob-utils]], each a vault anchor whose `code:` links its working repo.

## Design record

- [[DAS Code Skill Design]] · [[DAS Fix Design]] · [[DAS PR Flow Design]] · [[DAS Pilot Flow Design]] — per-verb design docs.
- **Naming (user, 2026-07-14 — F234 Q2):** the group is **Code**. The `/code` verb's pages take the *Code Skill* suffix ([[DAS Code Skill]] docs, [[DAS Code Skill Design]] design doc), freeing the formula name for this profile; folder renamed `design/dev/` → `design/code/`. (Supersedes the agent's same-day interim "Dev" naming, which existed only to dodge that collision.)
- **Grouping (agent, 2026-07-14):** `/cleanup`, `/module-doc`, and `/devops` — previously ungrouped — assigned here at this profile pass.
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Code Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
