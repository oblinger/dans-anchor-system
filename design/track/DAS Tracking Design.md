---
description: Subsystem design for the Tracking group — the surfaces, verbs, and rules that let a human and an agent share one picture of work state. Paradigm doc for per-group subsystem design.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Tracking Design](hook://p/DAS%20Tracking%20Design)
# DAS Tracking Design

Tracking is the subsystem that keeps one shared picture of work state between the human and the agent: what is ready, what is blocked, what question is waiting on whom. Its contract: **the agent never asks piecemeal and the user never hunts for state** — questions consolidate into one pile, status renders into one glanceable banner, and every state change flows through one write path.

![[DAS Tracking Design.svg|3000]]
*Figure source: `DAS Tracking Design.d2` — regenerate with `d2 "DAS Tracking Design.d2" "DAS Tracking Design.svg"`.*

## The idea

Work state lives in **facet-shaped files** (the surfaces), is mutated only through the **`state` CLI** (the engine), and is operated by a small set of **verbs** (the skills). Two axes organize every work item: *horizon* (Now / Next / Later — when the user wants it) and *workflow state* (the bracket — whether it can proceed). The drive cluster (`/crank`, `/mint`, `/land`) consumes what tracking surfaces as Ready; tracking itself never executes work.

## Key facets

Each facet is a per-document structural spec; where a template exists it is the fastest way to instantiate one.

- **[[DAS Backlog]]** — the work queue: rows carrying bracket × horizon, F/T-numbered, block-anchored. Template: [[templates/backlog|backlog]].
- **[[DAS Query]]** — the consolidated question pile (`{slug} queries.md`): Agent Resolutions / Verifications / Immediate Questions / Questions. Design record: [[Query PRD]].
- **[[DAS Status]]** — per-facet planning status. Template: [[templates/status|status]].
- **[[DAS Roadmap]]** — milestone state; pairs with [[DAS Completed Roadmap]] for the done half. Template: [[templates/roadmap|roadmap]].
- **[[DAS Track]]** — the `{slug} Track/` folder shape that houses backlog, features, and reports.
- **[[DAS Log]]** / **[[DAS Messages]]** — dated entry streams (append-only history, inter-agent messages).

## Key skills

Each verb has a user doc at the group's docs surface (`docs/track/`).

- **/ask** — eliminate every question the agent can, consolidate the residue into `{slug} queries.md`, render Q.md. User doc: [[DAS Ask]] (inline form: [[DAS ask-inline]]).
- **/groom** — frontier planning: get every could-be-next item fully Ready or parked with its blocking question. User doc: [[DAS Groom]].
- **`state` CLI** — the single write path for rows, questions, statuses, roadmaps; every mutation triggers the Q.md render. Doc: [[SKL State]].
- **Planning surface** — how the pieces compose per anchor: [[DAS Plan]].

## Rules

Checkable constraints adopted by tracking surfaces: [[R-status]], [[R-roadmap]], [[R-completed-roadmap]], [[R-log]], [[R-messages]], [[R-dated-entry-stream]].

## Coordinated examples

Tracking is illustrated inside the coherent worked worlds at [[DAS Examples]] (HBR, FEX Repo) — one real backlog + queries + status set per world, rather than a standalone example per facet.

## Design record

- [[Query PRD]] — the shared resolution-layer design behind /ask and /groom.
- [[DAS Ask Design]] · [[DAS Groom Design]] · [[DAS Groom PRD]] — per-verb design docs.
- This doc is the **paradigm subsystem design**: each skill/facet group gets one of these — architecture picture, key facets (→ templates), key skills (→ user docs), rules, coordinated examples — linked off [[DAS]].
