---
description: "`/pilot-flow` is the top-down design-then-implementation workflow."
---
# /pilot-flow
`/pilot-flow` is the top-down design-then-implementation workflow. You start from a PRD, work through Open Questions, UX, system design, file layout, and module descriptions, then a roadmap — and then implementation dispatches in priority order. Reach for it when you say "pilot flow" or "top-down development" — the alternative is `/pr-flow`, which is bottom-up iterative PRs with user review per increment.

| -[[SKL Pilot Flow]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Dev]] → [SKL Pilot Flow](hook://p/SKL%20Pilot%20Flow)<br>: the SKL Pilot Flow doc |
| --- | --- |
| Related | [[skills/pilot-flow/SKILL.md\|SKILL]],   |
| [[SKL Pilot Flow Design\|Design]] |  |

Under the hood it delegates: `/code plan` runs the seven-step planning phase, `/code execute` runs the implementation priority loop (user refinements → worker dispatch → spec next → surface decisions → design rescan), and `/code replan` handles lightweight replanning when requirements shift. The pilot role definition (with its `next` command protocol, git protocol, and context pacing rules) lives at `/role pilot`.
