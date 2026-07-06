---
description: "the /query skill — concept dossier: user guide, PRD, design, runtime, examples"
---
# SKL Query
The concept dossier for **`/query`** — everything published about the asking skill: the user guide, the shared resolution-layer PRD, the design, and the runtime spec.

| -[[SKL Query]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[skill-docs]] → [[SKL Drive]] → [SKL Query](hook://p/SKL%20Query)<br>: the /query concept dossier |
| --- | --- |
| Related | [[ASG Query\|User Guide]],  [[skills/query/SKILL.md\|SKILL]] (runtime) |
| Design | [[Query PRD\|PRD]] (shared resolution-layer PRD) |
| Facet | [[FCT Query]] (the `"{SLUG} queries.md"` file format) |

## What this is

`/query` is the universal asking subroutine — it routes a decision the agent can't make alone into a question you can answer from what's written, and eliminates every question it can before that. It is the **query half of the resolution layer** (with [[SKL Groom]] as the backlog half).

- **Use it** → [[ASG Query]] (the user guide).
- **Understand / adapt it** → [[Query PRD]] (design + goals + the determination ladder), [[FCT Query]] (the file-format rules the queries doc must satisfy).
- **Run it** → the runtime spec at [[skills/query/SKILL.md\|SKILL.md]] (loaded by Claude; the agent-facing runbook).

Tracking (feature docs, backlog) lives dev-side under the SKA agent, not in this published dossier.
