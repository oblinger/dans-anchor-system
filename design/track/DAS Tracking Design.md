---
description: Subsystem design for the Tracking group — the surfaces, verbs, and rules that let a human and an agent share one picture of work state. Paradigm doc for per-group subsystem design.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Tracking Design](hook://p/DAS%20Tracking%20Design)
# DAS Tracking Design
Tracking is the subsystem that keeps one shared picture of work state between the human and the agent: what is ready, what is blocked, what question is waiting on whom.

![[DAS Tracking Design.svg|3000]]

| **Skills**                              |                                                                                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[DAS Ask\|/ask]]                       | Eliminate every question the agent can; consolidate the residue into `{slug} queries.md`; render Q.md.                                                                  |
| [[DAS Groom\|/groom]]                   | Frontier planning: get every could-be-next item fully Ready or parked with its blocking question.                                                                       |
| [[DAS Plan\|/design]]                   | Once-per-project planning orchestrator — drives the anchor's planning artifacts to completeness.                                                                        |
|                                         |                                                                                                                                                                         |
| **Facets**                              |                                                                                                                                                                         |
| [[DAS Backlog\|Backlog]]                | The work queue: rows carrying bracket × horizon, F/T-numbered, block-anchored.                                                                                          |
| [[DAS Query\|Query]]                    | The consolidated question pile (`{slug} queries.md`) — banner + body copied verbatim into Q.md.                                                                         |
| [[DAS Status\|Status]]                  | Per-facet planning status via the monotonic tier ladder.                                                                                                                |
| [[DAS Roadmap\|Roadmap]]                | Forward-looking milestone state, named `M-<Name>` entries.                                                                                                              |
| [[DAS Completed Roadmap\|Completed Roadmap]] | Migration target for shipped milestones, newest at top.                                                                                                            |
| [[DAS Log\|Log]]                        | Append-only dated history stream — what happened on what day.                                                                                                           |
| [[DAS Messages\|Messages]]              | Inter-agent background notes (vs. user-dropped Inbox input).                                                                                                            |
| [[DAS Inbox\|Inbox]]                    | User-dropped input awaiting agent triage.                                                                                                               |
| [[DAS Icebox\|Icebox]]                  | Cold storage for parked rows — outside every default groom scope.                                                                                       |
| [[DAS Track\|Track]]                    | The `{slug} Track/` folder shape that houses the surfaces above.                                                                                                        |
|                                         |                                                                                                                                                                         |
| **Traits**                              |                                                                                                                                                                         |
| [[Track]]                               | Declares the anchor is actively driven through the planning + backlog lifecycle — turns on the `{slug} Track/` tree and the verbs above; co-requires the Backlog facet. |
|                                         |                                                                                                                                                                         |
| **Library**                             |                                                                                                                                                                         |
| [[DAS State\|`state` CLI]]              | The single write path for rows, questions, statuses, roadmaps; every mutation triggers the Q.md render.                                                                 |
| **`queries-render.py`**                 | Mechanical renderer — rebuilds `{slug} queries.md` and copies it into Q.md after every mutation.                                                                        |
| Disciplines                             | [[DAS workflow]] · [[DAS ask-format]] · [[DAS verification]] · [[DAS granularity]]                                                                                      |
| Rulesets                                | [[R-backlog]] · [[R-query]] · [[R-status]] · [[R-log]] · [[R-messages]] · [[R-roadmap]] · [[R-completed-roadmap]] · [[R-track-group]] · [[R-track-dispatch]] · [[R-fct-icebox]] · [[R-fct-inbox]] · [[R-fct-plan-dispatch]] · [[R-state-region]]                        |

## Overview

Tracking's contract: **the agent never asks piecemeal and the user never hunts for state** — questions consolidate into one pile, status renders into one glanceable banner, and every state change flows through one write path. Work state lives in **facet-shaped files** (the surfaces), is mutated only through the **`state` CLI** (the engine), and is operated by a small set of **verbs** (the skills). Two axes organize every work item: *horizon* (Now / Next / Later — when the user wants it) and *workflow state* (the bracket — whether it can proceed). The drive cluster (`/crank`, `/mint`, `/land`) consumes what tracking surfaces as Ready; tracking itself never executes work.

In the table above, every item's name links its docs page directly — the skill dossier (whose masthead links the runbook) or the facet spec (whose masthead leads with breadcrumb · Related · Examples · Rules · ToC and links the template) — so one column of links routes everywhere. Rules live in `rulesets/R-<name>.md` (whole tracking group extracted 2026-07-12; other groups follow at their profile pass). *(Table reduced to two columns per the shape revision of 2026-07-14 — see design record.)*

## Coordinated examples

Tracking is illustrated inside the coherent worked worlds at [[DAS Examples]] (HBR, FEX Repo) — one real backlog + queries + status set per world, rather than a standalone example per facet.

## Design record

- [[Query PRD]] — the shared resolution-layer design behind /ask and /groom.
- [[DAS Ask Design]] · [[DAS Groom Design]] · [[DAS Groom PRD]] — per-verb design docs; [[DAS ask-inline]] is the inline form of /ask.
- [[T009 Phoenix Tracking Survey 2026-07-12]] — demolition survey feeding the Phoenix boil-down of this group.
- This doc is the **paradigm subsystem design** (shape ratified 2026-07-12, encoded as `R-progressive-03`): breadcrumb → H1 → orientation line, overview figure, one merged Skills / Facets / Traits / Library table, `## Overview`, coordinated examples, design record — each group gets one of these, linked off [[DAS]]. **Shape revision (user, 2026-07-14, Design session):** the table is **two columns** — the item's name links its docs page directly (which routes on to runbook / template / rules); the separate docs column is retired; descriptions stay to one line. Profile filenames follow the literal formula `DAS <Group> Design.md` (so the Design group's is [[DAS Design Design]], repeat accepted; a gerund or subtitle may soften the H1 title text, never the filename).
- Figure source: same-basename `DAS Tracking Design.excalidraw` beside the SVG (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
