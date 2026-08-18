---
description: Subsystem design for the Design group — the artifact pipeline, gates, and verbs that turn an idea into an agreed, buildable specification before execution starts.
---

:>> [[DAS]] → [design](hook://design) → [DAS Design Design](hook://p/DAS%20Design%20Design)
# DAS Design Design — the design of the Design subsystem
Design is the subsystem that turns an idea into an agreed, buildable specification: a canonical pipeline of design artifacts (PRD → Architecture → Milestones → Testing → **design accepted** → Roadmap → Features) authored jointly by human and agent, with one sticky acceptance gate guarding the transition to execution.

![[DAS Design Design.svg|3000]]

| **Skills**                           |                                                                                                                                                                                                               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[DAS Plan\|/design]]                | Walks the pipeline in order, dispatches the per-artifact sub-skills, enforces the design-accepted gate.                                                                                                       |
| [[DAS Architect\|/architect]]        | Builds + maintains `{slug} Architecture.md` — subsystem decomposition, `module ↔ arch` links.                                                                                                                 |
| [[DAS Parley\|/parley]]              | Structured discussion — talk a topic through; its captured decisions and next steps feed the Discussion / Decisions artifacts.                                                                                |
|                                      |                                                                                                                                                                                                               |
| **Facets**                           |                                                                                                                                                                                                               |
| [[DAS Design Folder\|Design Folder]] | The `{slug} Design/` folder itself — its presence activates the subsystem (R-design-08).                                                                                                                      |
| [[DAS PRD\|PRD]]                     | The what and why — overview, goals, user stories.                                                                                                                                                             |
| [[DAS UX Design\|UX]]                | User-facing behavior (when applicable).                                                                                                                                                                       |
| [[DAS API Design\|API]]              | The public interface (when applicable).                                                                                                                                                                       |
| [[DAS Architecture\|Architecture]]   | The how — subsystems, modules, trade-offs. Satellites: UX, System Design, API.                                                                                                                                |
| [[DAS Testing\|Testing]]             | Verification strategy, covering the pinned milestones. Feeds the design-accepted gate.                                                                                                                        |
| [[DAS System Design\|System Design]] | Consolidated single-doc design for small anchors.                                                                                                                                                             |
| [[DAS Decisions\|Decisions]]         | Durable D-numbered rulings.                                                                                                                                                                                   |
| [[DAS Discussion\|Discussion]]       | Free-form design discussion feeding the artifacts.                                                                                                                                                            |
| [[DAS Stories\|Stories]]             | User-story records — the PRD's satellite.                                                                                                                                                                     |
| [[DAS Features\|Features]]           | F-numbered feature docs — authored here, driven by Drive.                                                                                                                                                     |
|                                      |                                                                                                                                                                                                               |
| **Traits**                           |                                                                                                                                                                                                               |
| *(folder-presence)*                  | No trait key — the `{slug} Design/` folder is the declaration.                                                                                                                                                |
|                                      |                                                                                                                                                                                                               |
| **Library**                          |                                                                                                                                                                                                               |
| [[DAS Status\|status:: gate]]        | The `accepted` tier (Tracking's ladder) — what the design-accepted gate reads. Sticky once accepted.                                                                                                          |
| Rulesets                             | [[R-design]] · [[R-prd]] · [[R-architecture]] · [[R-files-architecture]] · [[R-decisions]] · [[R-discussion]] · [[R-stories]] · [[R-ux]] · [[R-api]] · [[R-design-gate]] · [[R-fct-system-design]] · [[R-fct-features]] · [[R-design-dispatch]] · [[R-design-docs-group]] · [[R-layering]] · [[R-arch]] (umbrella: single-source-of-truth · one-path · interfaces-folder · factory-pegboard · ownership) · [[R-process]] (umbrella: design-gate · stable-ids · exception-discipline · wrapper-cli) |

## Overview

Design's contract: **no execution before agreement, and no agreement on missing artifacts.** `/design` walks the phases in canonical order — **PRD** (with its Stories satellite) → **Architecture** (with its UX / System Design / API satellites) → **Milestones** (pin the testable increments — the initial roadmap) → **Testing** (a strategy that covers those milestones) → the **one gate: design accepted** → **Roadmap** (fleshed out after acceptance, as designing each feature spawns its subtasks and sub-features) → **Features** — detecting state rather than assuming it, so it is safe to invoke at any point mid-pipeline. Everything before the gate iterates until the design set is accepted; the user passes it conversationally ("the design is accepted") and the agent stamps the `status::` field. *(Pipeline revised in this session, 2026-07-14 — supersedes the earlier two-gate PRD → UX → API → Architecture → Testing order; UX / System Design / API now ride as Architecture satellites, Stories as the PRD's, and milestone-pinning precedes testing so the tests have concrete increments to cover.)*

Boundaries: **Features are authored here but driven by Drive** — the `{slug} Design/{slug} Features/` folder is a Design artifact (F142); `/feature`, `/crank`, and `/mint` consume it. **Roadmap bridges to Tracking** — `/design roadmap` authors it as the last phase; the Tracking surfaces carry it from there. **The status ladder is Tracking's engine** — Design only reads/writes the `accepted` tier at its gate.

## Coordinated examples

Design is illustrated inside the coherent worked worlds at [[FEX]] (HBR, FEX Repo) — each world carries a real `{slug} Design/` tree rather than standalone per-facet samples.

## Design record

- [[DAS Architect Design]] — the `/architect` verb's own design doc.
- [[DAS Design]] — the design-pipeline index (per-skill design docs + PRDs across all groups); distinct from this subsystem profile.
- Shape follows the paradigm [[DAS Tracking Design]] (R-spine-02 head; merged Skills / Facets / Traits / Library table; one profile per group, linked off [[DAS]]). **Shape revision (user, 2026-07-14, this session):** the table is two columns — the item's name links its docs dossier directly (the dossier routes onward to runbook / template), descriptions stay to one line.
- **Pipeline ruling (user, 2026-07-14):** one gate, not two — *design accepted*, after Testing; Milestones sits between Architecture and Testing (initial roadmap; the full Roadmap elaboration is post-gate). Rendered in the figure as the loop-on-arrow glyph. Runbook conformance landed 2026-07-14 ([[TINK Backlog#^T019|T019]]): `/design` SKILL + design-prd/design-testing sub-skills, [[DAS Plan]] user doc, [[DAS Testing]] facet, and R-testing all carry the one-gate order.
- **Gate record (agent, 2026-07-14, T019):** the one gate is a single conversational event (*"the design is accepted"*, or `/design gate`) recorded by stamping `status:: accepted` on `{slug} Architecture.md` AND `{slug} Testing.md` in the same pass — the old G2 condition becomes the single gate's check, no new field vocabulary, existing anchors' fields stay valid. Chosen over inventing a `design::` line in `{slug} Status.md` (the state CLI hardcodes its five facets; extending it is a separate approved-code task if ever wanted).
- **Membership (agent, 2026-07-14):** `/parley` moved here from Utility — its products are this group's Discussion/Decisions artifacts. (User's first instinct was Drive; one-line move if preferred.)
- Figure source: same-basename `DAS Design Design.excalidraw` beside the SVG (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
