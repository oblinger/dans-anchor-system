---
description: Subsystem design for the Tracking group — the surfaces, verbs, and rules that let a human and an agent share one picture of work state. Paradigm doc for per-group subsystem design.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Tracking Design](hook://p/DAS%20Tracking%20Design)
# DAS Tracking Design

Tracking is the subsystem that keeps one shared picture of work state between the human and the agent: what is ready, what is blocked, what question is waiting on whom. Its contract: **the agent never asks piecemeal and the user never hunts for state** — questions consolidate into one pile, status renders into one glanceable banner, and every state change flows through one write path. Work state lives in **facet-shaped files** (the surfaces), is mutated only through the **`state` CLI** (the engine), and is operated by a small set of **verbs** (the skills). Two axes organize every work item: *horizon* (Now / Next / Later — when the user wants it) and *workflow state* (the bracket — whether it can proceed). The drive cluster (`/crank`, `/mint`, `/land`) consumes what tracking surfaces as Ready; tracking itself never executes work.

![[DAS Tracking Design.svg|3000]]
*Figure source: `DAS Tracking Design.excalidraw` (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py "DAS Tracking Design.excalidraw"`).*

| Skills | | |
| --- | --- | --- |
| **/ask** | Eliminate every question the agent can, consolidate the residue into `{slug} queries.md`, render Q.md. | [[DAS Ask\|user doc]] · [[DAS ask-inline\|inline form]] |
| **/groom** | Frontier planning: get every could-be-next item fully Ready or parked with its blocking question. | [[DAS Groom\|user doc]] |
| **`state` CLI** | The single write path for rows, questions, statuses, roadmaps; every mutation triggers the Q.md render. | [[SKL State\|doc]] |
| **planning surface** | How the pieces compose per anchor. | [[DAS Plan\|user doc]] |

| Facets | | | |
| --- | --- | --- | --- |
| **[[DAS Backlog]]** | The work queue: rows carrying bracket × horizon, F/T-numbered, block-anchored. | [[templates/backlog\|template]] | rules in spec |
| **[[DAS Query]]** | The consolidated question pile (`{slug} queries.md`): Agent Resolutions / Verifications / Immediate Questions / Questions. | — | rules in spec |
| **[[DAS Status]]** | Per-facet planning status. | [[templates/status\|template]] | [[DAS Status#RULESET R-status\|R-status]] |
| **[[DAS Roadmap]]** | Milestone state; pairs with [[DAS Completed Roadmap]] for the done half. | [[templates/roadmap\|template]] | [[DAS Roadmap#RULESET R-roadmap\|R-roadmap]] · [[DAS Completed Roadmap#RULESET R-completed-roadmap\|R-completed-roadmap]] |
| **[[DAS Track]]** | The `{slug} Track/` folder shape that houses backlog, features, and reports. | — | rules in spec |
| **[[DAS Log]]** | Append-only dated history stream. | — | [[DAS Log#RULESET R-log\|R-log]] · [[DAS dated-entry-stream#RULESET R-dated-entry-stream\|R-dated-entry-stream]] |
| **[[DAS Messages]]** | Inter-agent background notes (vs. user-dropped Inbox input). | — | [[DAS Messages#RULESET R-messages\|R-messages]] |

| Traits | |
| --- | --- |
| **[[Track]]** | Declares the anchor is actively driven through the planning + backlog lifecycle (the "drive loop") — turns on the `{slug} Track/` tree and the verbs above; co-requires the Backlog facet. |

*(Ruleset links go straight to the embedded `# RULESET` block inside each facet spec — per the F133 convention the rules are co-located with the spec that motivates them; the catalog-side `[[R-status]]`-style pages are wiring stubs.)*

## Coordinated examples

Tracking is illustrated inside the coherent worked worlds at [[DAS Examples]] (HBR, FEX Repo) — one real backlog + queries + status set per world, rather than a standalone example per facet.

## Design record

- [[Query PRD]] — the shared resolution-layer design behind /ask and /groom.
- [[DAS Ask Design]] · [[DAS Groom Design]] · [[DAS Groom PRD]] — per-verb design docs.
- [[T009 Phoenix Tracking Survey 2026-07-12]] — demolition survey feeding the Phoenix boil-down of this group.
- This doc is the **paradigm subsystem design**: each skill/facet group gets one of these — architecture figure, then the Skills / Facets / Traits tables (each row linking its template, user doc, and rules), coordinated examples, design record — linked off [[DAS]].
