---
description: "Plan — federated orchestrator for a project anchor's planning artifacts. The Track-cluster sibling of /crank."
---
# DAS Plan
The `/design` skill walks a project anchor through its planning artifacts in canonical order, detecting which exist, what's missing, and dispatching to per-artifact sub-skills.

| -[[DAS Plan]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Plan](hook://p/DAS%20Plan)<br>: Plan — federated orchestrator for a project anchor's planning artifacts. The Track-cluster sibling of /crank. |
| --- | --- |
| Related | [[skills/design/SKILL.md\|SKILL]] (runtime),  [[DAS Crank]] (Drive-cluster sibling), |

Plan is to **Track** what **crank** is to **Drive** — the outer-loop orchestrator at the center of the cluster. Where crank runs thousands of times executing Ready work, plan runs once-per-project (and on major reorgs) driving anchor-level planning artifacts to completeness.

## Canonical phase order

| # | Phase | Sub-skill | Primary artifact | Gate after |
|---|---|---|---|---|
| 1 | PRD | `/design prd` | `{slug} PRD.md` | — |
| 2 | UX | `/design ux` | `{slug} UX.md` | — |
| 3 | API | `/design api` | `{slug} API.md` | — |
| 4 | Architecture | `/design architect` | `{slug} Architecture.md` | **Gate 1** — `status:: accepted` on Architecture |
| 5 | Testing Strategy | `/design testing` | `{slug} Testing Strategy.md` | **Gate 2** — `status:: accepted` on BOTH Architecture AND Testing Strategy |
| 6 | Roadmap | `/design roadmap` | `{slug} Roadmap.md` + per-milestone feature docs | — |
| 7 | Plan complete | — | — | Transition to Drive (`/crank`) |

Each phase produces one primary artifact (a file). Two phases end with an explicit acceptance gate. Gates are sticky: once `accepted`, no re-prompt unless the user explicitly resets.

## How `/design` knows where the user is

Per-artifact `status::` field at the top of each planning doc. Valid values for the gate-gating artifacts (Architecture, Testing Strategy): `drafting | in-review | accepted`.

When `status::` is absent, the skill infers state from content guidelines:
- PRD with at least one user story → past PRD-drafting
- Architecture with at least one named subsystem → architecting in progress
- Architecture `status:: accepted` → Gate 1 passed
- Architecture AND Testing Strategy both `accepted` → Gate 2 passed
- Roadmap with at least one milestone → roadmapping in progress

## Invocation forms

| Form | What happens |
|---|---|
| `/design` (bare) | Inspect anchor's planning artifacts, print compact gap table, auto-dispatch to the first incomplete phase. |
| `/design <phase>` | Direct invocation: `/design prd`, `/design ux`, `/design architect`, `/design testing`, `/design roadmap`. |
| `/design gate architecture` | Shortcut: set `status:: accepted` on `{slug} Architecture.md`. |
| `/design gate testing` | Shortcut: set `status:: accepted` on `{slug} Testing Strategy.md`. |

The skill also watches for natural-language acceptance phrases in conversation:
- *"the architecture is accepted"* → sets `status:: accepted` on Architecture
- *"the testing strategy is accepted"* → sets `status:: accepted` on Testing Strategy

## Sub-skills

| Verb | Sub-skill | Authors |
|---|---|---|
| `/design prd` | [[design-prd]] | `{slug} PRD.md` |
| `/design ux` | [[design-ux]] | `{slug} UX.md` |
| `/design architect` | [[design-architect]] | `{slug} Architecture.md` + subsystems |
| `/design testing` | [[design-testing]] | `{slug} Testing Strategy.md` |
| `/design roadmap` | [[design-roadmap]] | `{slug} Roadmap.md` + per-milestone feature docs |

## Scope (v1)

v1 supports `code` trait anchors only. Per-trait artifact rosters for Paper / Topic / Simple anchors is Phase 2 — generalization decided at that time based on observed authoring patterns.

## Related

- Center-of-Track sibling: [[DAS workflow]] (canonical state graph)
- Backlog discipline: [[DAS Backlog]]
- Drive-cluster center: [[DAS Crank]]
- Feature lifecycle (post-plan): [[DAS Feature]]
- Verification discipline: [[DAS verification]]
