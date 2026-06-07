---
description: "Plan — federated orchestrator for a project anchor's planning artifacts. The Track-cluster sibling of /crank."
---

# Plan

The `/plan` skill walks a project anchor through its planning artifacts in canonical order, detecting which exist, what's missing, and dispatching to per-artifact sub-skills.

Plan is to **Track** what **crank** is to **Drive** — the outer-loop orchestrator at the center of the cluster. Where crank runs thousands of times executing Ready work, plan runs once-per-project (and on major reorgs) driving anchor-level planning artifacts to completeness.

## Canonical phase order

| # | Phase | Sub-skill | Primary artifact | Gate after |
|---|---|---|---|---|
| 1 | PRD | `/plan prd` | `{NAME} PRD.md` | — |
| 2 | UX | `/plan ux` | `{NAME} UX.md` | — |
| 3 | API | `/plan api` | `{NAME} API.md` | — |
| 4 | Architecture | `/plan architect` | `{NAME} Architecture.md` | **Gate 1** — `status:: accepted` on Architecture |
| 5 | Testing Strategy | `/plan testing` | `{NAME} Testing Strategy.md` | **Gate 2** — `status:: accepted` on BOTH Architecture AND Testing Strategy |
| 6 | Roadmap | `/plan roadmap` | `{NAME} Roadmap.md` + per-milestone feature docs | — |
| 7 | Plan complete | — | — | Transition to Drive (`/crank`) |

Each phase produces one primary artifact (a file). Two phases end with an explicit acceptance gate. Gates are sticky: once `accepted`, no re-prompt unless the user explicitly resets.

## How `/plan` knows where the user is

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
| `/plan` (bare) | Inspect anchor's planning artifacts, print compact gap table, auto-dispatch to the first incomplete phase. |
| `/plan <phase>` | Direct invocation: `/plan prd`, `/plan ux`, `/plan architect`, `/plan testing`, `/plan roadmap`. |
| `/plan gate architecture` | Shortcut: set `status:: accepted` on `{NAME} Architecture.md`. |
| `/plan gate testing` | Shortcut: set `status:: accepted` on `{NAME} Testing Strategy.md`. |

The skill also watches for natural-language acceptance phrases in conversation:
- *"the architecture is accepted"* → sets `status:: accepted` on Architecture
- *"the testing strategy is accepted"* → sets `status:: accepted` on Testing Strategy

## Sub-skills

| Verb | Sub-skill | Authors |
|---|---|---|
| `/plan prd` | [[plan-prd]] | `{NAME} PRD.md` |
| `/plan ux` | [[plan-ux]] | `{NAME} UX.md` |
| `/plan architect` | [[plan-architect]] | `{NAME} Architecture.md` + subsystems |
| `/plan testing` | [[plan-testing]] | `{NAME} Testing Strategy.md` |
| `/plan roadmap` | [[plan-roadmap]] | `{NAME} Roadmap.md` + per-milestone feature docs |

## Scope (v1)

v1 supports `Code` trait anchors only. Per-trait artifact rosters for Paper / Topic / Simple anchors is Phase 2 — generalization decided at that time based on observed authoring patterns.

## Related

- Center-of-Track sibling: [[SKL Workflow]] (canonical state graph)
- Backlog discipline: [[SKL Backlog]]
- Drive-cluster center: [[SKL Crank]]
- Feature lifecycle (post-plan): [[SKL Feature]]
- Verification discipline: [[verification]]
