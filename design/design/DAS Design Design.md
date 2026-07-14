---
description: Subsystem design for the Design group — the artifact pipeline, gates, and verbs that turn an idea into an agreed, buildable specification before execution starts.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Design Design](hook://p/DAS%20Design%20Design)
# DAS Design Design — the design of the Design subsystem
Design is the subsystem that turns an idea into an agreed, buildable specification: a canonical pipeline of design artifacts (PRD → UX → API → Architecture → Testing → Roadmap → Features) authored jointly by human and agent, with sticky acceptance gates guarding the transition to execution.

![[DAS Design Design.svg|3000]]

| **Skills**                           |                                                                                                                 |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| [[DAS Plan\|/design]]                | Walks the pipeline in order, dispatches the per-artifact sub-skills, enforces the two gates.                    |
| [[DAS Architect\|/architect]]        | Builds + maintains `{slug} Architecture.md` — subsystem decomposition, `module ↔ arch` links.                   |
|                                      |                                                                                                                 |
| **Facets**                           |                                                                                                                 |
| [[DAS Design Folder\|Design Folder]] | The `{slug} Design/` folder itself — its presence activates the subsystem (R-design-08).                        |
| [[DAS PRD\|PRD]]                     | The what and why — overview, goals, user stories.                                                               |
| [[DAS UX Design\|UX]]                | User-facing behavior (when applicable).                                                                         |
| [[DAS API Design\|API]]              | The public interface (when applicable).                                                                         |
| [[DAS Architecture\|Architecture]]   | The how — subsystems, modules, trade-offs. Gate 1.                                                              |
| [[DAS Testing\|Testing]]             | Verification strategy. Gate 2, jointly with Architecture.                                                       |
| [[DAS System Design\|System Design]] | Consolidated single-doc design for small anchors.                                                               |
| [[DAS Decisions\|Decisions]]         | Durable D-numbered rulings.                                                                                     |
| [[DAS Discussion\|Discussion]]       | Free-form design discussion feeding the artifacts.                                                              |
| [[DAS Stories\|Stories]]             | User-story records behind the PRD.                                                                              |
| [[DAS Features\|Features]]           | F-numbered feature docs — authored here, driven by Drive.                                                       |
|                                      |                                                                                                                 |
| **Traits**                           |                                                                                                                 |
| *(folder-presence)*                  | No trait key — the `{slug} Design/` folder is the declaration.                                                  |
|                                      |                                                                                                                 |
| **Library**                          |                                                                                                                 |
| [[DAS Status\|status:: gates]]       | The `accepted` tier on Architecture / Testing (Tracking's ladder) — what the gates read. Sticky once accepted.  |
| Rulesets                             | [[R-design]] · [[R-prd]] · [[R-architecture]] · [[R-decisions]] · [[R-discussion]] · [[R-stories]] · [[R-ux]] · [[R-design-gate]] · [[R-fct-system-design]] · [[R-design-dispatch]] · [[R-design-docs-group]] |

## Overview

Design's contract: **no execution before agreement, and no agreement on missing artifacts.** `/design` walks the phases in canonical order — PRD → UX *(if applicable)* → API *(if applicable)* → Architecture → Testing → Roadmap → Features — detecting state rather than assuming it, so it is safe to invoke at any point mid-pipeline. Two sticky gates protect the expensive transitions: **Gate 1** (`status:: accepted` on Architecture) guards Testing authoring; **Gate 2** (Architecture *and* Testing accepted) guards Roadmapping. The user passes a gate conversationally ("the architecture is accepted") and the agent stamps the field.

Boundaries: **Features are authored here but driven by Drive** — the `{slug} Design/{slug} Features/` folder is a Design artifact (F142); `/feature`, `/crank`, and `/mint` consume it. **Roadmap bridges to Tracking** — `/design roadmap` authors it as the last phase; the Tracking surfaces carry it from there. **The status ladder is Tracking's engine** — Design only reads/writes the `accepted` tier at its gates.

## Coordinated examples

Design is illustrated inside the coherent worked worlds at [[DAS Examples]] (HBR, FEX Repo) — each world carries a real `{slug} Design/` tree rather than standalone per-facet samples.

## Design record

- [[DAS Architect Design]] — the `/architect` verb's own design doc.
- [[DAS Design]] — the design-pipeline index (per-skill design docs + PRDs across all groups); distinct from this subsystem profile.
- Shape follows the paradigm [[DAS Tracking Design]] (R-progressive-03 head; merged Skills / Facets / Traits / Library table; one profile per group, linked off [[DAS]]). **Shape revision (user, 2026-07-14, this session):** the table is two columns — the item's name links its docs dossier directly (the dossier routes onward to runbook / template), descriptions stay to one line.
- Figure source: same-basename `DAS Design Design.excalidraw` beside the SVG (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
