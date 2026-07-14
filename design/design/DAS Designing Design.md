---
description: Subsystem design for the Designing group — the artifact pipeline, gates, and verbs that turn an idea into an agreed, buildable specification before execution starts.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Designing Design](hook://p/DAS%20Designing%20Design)
# DAS Designing Design
Designing is the subsystem that turns an idea into an agreed, buildable specification: a canonical pipeline of design artifacts (PRD → UX → API → Architecture → Testing → Roadmap → Features) authored jointly by human and agent, with sticky acceptance gates guarding the transition to execution.

![[DAS Designing Design.svg|3000]]

| **Skills**                              |                             |                                                                                                                                                                                     |
| --------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[DAS Plan\|/design]]                   |                             | Federated design orchestrator — detects which artifacts are complete vs. missing, dispatches per-artifact sub-skills (`design-prd` / `design-ux` / `design-architect` / `design-testing` / `design-roadmap`), enforces the two gates. |
| [[DAS Architect\|/architect]]           |                             | Creates + maintains `{slug} Architecture.md` — subsystem decomposition, `module ↔ arch` bidirectional links, single-file → folder-doc upgrade when it grows.                          |
|                                         |                             |                                                                                                                                                                                     |
| **Facets**                              |                             |                                                                                                                                                                                     |
| [[DAS Design Folder\|Design Folder]]    | [[DAS Design Folder\|docs]] | The `{slug} Design/` folder shape that houses every artifact below. Its **presence is the activation**: the folder exists IFF real maintained design content exists (R-design-08); `/design` gates on it. |
| [[templates/prd.md\|PRD]]               | [[DAS PRD\|docs]]           | The *what and why* — overview, goals, non-goals, user stories. First phase, always.                                                                                                 |
| [[DAS UX Design\|UX]]                   | [[DAS UX Design\|docs]]     | User-facing behavior and flows. Phase 2, when the project has a user surface.                                                                                                       |
| [[DAS API Design\|API]]                 | [[DAS API Design\|docs]]    | The public interface contract. Phase 3, when the project exposes one.                                                                                                              |
| [[DAS Architecture\|Architecture]]      | [[DAS Architecture\|docs]]  | The *how* — subsystems, modules, trade-offs. **Gate 1** sits at its end: `status:: accepted`.                                                                                       |
| [[templates/testing.md\|Testing]]       | [[DAS Testing\|docs]]       | Verification strategy sized to the design. **Gate 2**: Architecture AND Testing both `accepted` before roadmapping.                                                                 |
| [[DAS System Design\|System Design]]    | [[DAS System Design\|docs]] | The consolidated single-doc design for anchors small enough not to split PRD / Architecture apart.                                                                                  |
| [[templates/decisions.md\|Decisions]]   | [[DAS Decisions\|docs]]     | The durable rulings record (D-numbered) — decisions that outlive the docs that prompted them.                                                                                       |
| [[DAS Discussion\|Discussion]]          | [[DAS Discussion\|docs]]    | Free-form design discussions — the thinking that feeds the artifacts without living in them.                                                                                       |
| [[DAS Stories\|Stories]]                | [[DAS Stories\|docs]]       | User-story records backing the PRD's stories section.                                                                                                                              |
| [[DAS Features\|Features]]              | [[DAS Features\|docs]]      | `{slug} Design/{slug} Features/` — F-numbered feature docs. **Authored here, executed by Drive** (the feature lifecycle verb lives in that cluster).                                |
|                                         |                             |                                                                                                                                                                                     |
| **Traits**                              |                             |                                                                                                                                                                                     |
| *(folder-presence)*                     | —                           | No explicit trait key — the existing `{slug} Design/` folder is the declaration (R-design-08). Scaffold-on-offer when absent.                                                       |
|                                         |                             |                                                                                                                                                                                     |
| **Library**                             |                             |                                                                                                                                                                                     |
| **`status::` gate fields**              | [[DAS Status\|docs]]        | Per-artifact planning status via the monotonic tier ladder (owned by Tracking); `accepted` on Architecture / Testing is what the gates read. Sticky — once accepted, no re-prompt.  |
| **Rulesets**                            | —                           | [[R-design]] · [[R-prd]] · [[R-architecture]] · [[R-decisions]] · [[R-discussion]] · [[R-stories]] · [[R-ux]] · [[R-design-gate]] · [[R-fct-system-design]] · [[R-design-dispatch]] · [[R-design-docs-group]] — per-facet constraints, checked by Warden / `/audit`. |

## Overview

Designing's contract: **no execution before agreement, and no agreement on missing artifacts.** `/design` walks the anchor through the phases in canonical order — PRD → UX *(if applicable)* → API *(if applicable)* → Architecture → Testing → Roadmap → Features — detecting state rather than assuming it, so the skill is safe to invoke at any point mid-pipeline. Two sticky gates protect the expensive transitions: **Gate 1** (`status:: accepted` on Architecture) guards Testing authoring; **Gate 2** (Architecture *and* Testing accepted) guards Roadmapping. The user passes a gate conversationally ("the architecture is accepted") and the agent stamps the field.

The subsystem's boundaries: **Features are authored here but driven elsewhere** — the `{slug} Design/{slug} Features/` folder is a Designing artifact (F142), while `/feature`, `/crank`, and `/mint` (the Drive cluster) consume it. **Roadmap bridges to Tracking** — `/design roadmap` authors it as the last design phase; the Tracking surfaces carry it from there. **The status ladder is Tracking's engine** — Designing only reads/writes the `accepted` tier at its gates. `/viz` (Doc group) supplies the figures design docs embed.

## Coordinated examples

Designing is illustrated inside the coherent worked worlds at [[DAS Examples]] (HBR, FEX Repo) — each world carries a real `{slug} Design/` tree rather than standalone per-facet samples.

## Design record

- [[DAS Architect Design]] — the `/architect` verb's own design doc.
- [[DAS Design]] — the design-pipeline index (per-skill design docs + PRDs across all groups); distinct from this subsystem profile.
- Shape follows the ratified paradigm [[DAS Tracking Design]] (R-progressive-03 head; merged Skills / Facets / Traits / Library table; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Designing Design.excalidraw` beside the SVG (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
