---
description: "Plan — federated orchestrator for a project anchor's planning artifacts. The Track-cluster sibling of /crank."
---
# DAS Plan
The `/design` skill walks a project anchor through its planning artifacts in canonical order, detecting which exist, what's missing, and dispatching to per-artifact sub-skills.

| -[[DAS Plan]]- | : Plan — federated orchestrator for a project anchor's planning artifacts. The Track-cluster sibling of /crank.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Plan](hook://p/DAS%20Plan)  |
| --- | --- |
| Related | [[skills/design/SKILL.md\|SKILL]] (runtime),  [[DAS Crank]] (Drive-cluster sibling), |
| ... |  |

Plan is to **Track** what **crank** is to **Drive** — the outer-loop orchestrator at the center of the cluster. Where crank runs thousands of times executing Ready work, plan runs once-per-project (and on major reorgs) driving anchor-level planning artifacts to completeness.

## Canonical phase order

| # | Phase | Sub-skill | Primary artifact |
|---|---|---|---|
| 1 | PRD | `/design prd` | `{slug} PRD.md` — satellite: Stories |
| 2 | Architecture | `/design architect` | `{slug} Architecture.md` — satellites (when applicable): UX, System Design, API |
| 3 | Milestones | `/design milestones` | `{slug} Roadmap.md` — pin the testable increments (initial pass) |
| 4 | Testing | `/design testing` | `{slug} Testing.md` — strategy covering the pinned milestones |
| — | **Gate: design accepted** | — | *"the design is accepted"* → agent stamps `status:: accepted` on Architecture + Testing |
| 5 | Roadmap | `/design roadmap` | `{slug} Roadmap.md` — full post-gate elaboration |
| 6 | Features | `/design features` | `{slug} Features/` folder |
| 7 | Plan complete | — | Transition to Drive (`/crank`) |

Each phase produces one primary artifact (a file). One acceptance gate sits between Testing and Roadmap; it is sticky — once `accepted`, no re-prompt unless the user explicitly resets. (Pipeline per [[DAS Design Design]], ruled 2026-07-14; supersedes the earlier two-gate order.)

## How `/design` knows where the user is

Per-artifact `status::` field at the top of each planning doc. Valid values for the gate-record artifacts (Architecture, Testing): `drafting | in-review | accepted`.

When `status::` is absent, the skill infers state from content guidelines:
- PRD with at least one user story → past PRD-drafting
- Architecture with at least one named subsystem → architecting in progress
- Roadmap with pinned milestones → past the Milestones pass
- Architecture AND Testing both `accepted` → the design-accepted gate has passed
- Roadmap elaborated beyond the pinned milestones → roadmapping in progress

## Invocation forms

| Form | What happens |
|---|---|
| `/design` (bare) | Inspect anchor's planning artifacts, print compact gap table, auto-dispatch to the first incomplete phase. |
| `/design <phase>` | Direct invocation: `/design prd`, `/design ux`, `/design architect`, `/design testing`, `/design roadmap`. |
| `/design gate` | Shortcut for the design-accepted gate: set `status:: accepted` on `{slug} Architecture.md` AND `{slug} Testing.md`. |

The skill also watches for the natural-language acceptance phrase in conversation:
- *"the design is accepted"* → stamps `status:: accepted` on Architecture + Testing (the gate's record)

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
