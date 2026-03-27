# Plan

Orchestrate the full planning phase from idea to architecture-ready design. Dispatches to individual planning steps in order.

## Capture Everything, File It Where It Belongs

During any planning step, the user may raise ideas that belong to a DIFFERENT step's document. **Always capture these immediately in the right document**, even if you're not on that step yet. For example:
- During PRD discussion, user mentions an architecture idea → write it in System Design
- During UX discussion, user identifies a test scenario → add to Test Plan or Discussion
- During System conversation, user states a requirement → add to PRD
- At any point, user raises an unresolved question → add to Open Questions

Never lose information because "we're not on that step yet." The planning steps are a suggested ORDER, not walls between documents.

## Pipeline

| Step | Action | File | What it produces |
|------|--------|------|-----------------|
| 1 | Anchor | [[code-anchor]] | Project folder, doc skeleton, dispatch tables |
| 2 | PRD | [[code-prd]] | Requirements: goals, user stories, constraints |
| 3 | Research | [[code-research]] | Landscape: tools, prior art, approaches |
| 4 | UX | [[code-ux]] | User experience: screens, commands, concepts |
| 5 | System | [[code-system]] | Technical foundation: language, components, state, deps |
| 6 | Audit | [[code-plan-audit]] | Completeness check before architecture |

## Open Questions

Questions are captured throughout the pipeline in `{NAME} Open Questions.md`. See [[code-open-questions]] for the capture, resolution, and cascade process.

## Planning Levels

Three levels control depth. Standard is the default; the user can request light or deep.

- **Light** — abbreviated pass, enough to establish direction. PRD: overview + goals only. UX: key screens only. System: component list only.
- **Standard** — full pass through each step. Every document complete enough for a worker to build from.
- **Deep** — full pass plus explicit verification of completeness and cross-document consistency after each step. No placeholders or TBDs left.

## Planning Modes

- **Interactive** (default) — step by step with user collaboration, raising urgent questions immediately
- **Complete** — maximum autonomous progress. Tag all questions as Deferred. Work through every step and the backlog. Stop only when no further progress is possible.
- **Exhaustive** — complete mode plus legacy scan, re-document, worker spec pass, and final consistency sweep

## Planning Backlog

Autonomous tasks live in the Legwork section of `{NAME} Backlog.md`. Worked after pipeline steps complete. See the original planning backlog rules for what qualifies.

## Completion

Planning is complete when:
1. All 5 pipeline steps pass
2. Open questions are resolved or deferred
3. User has approved the design
4. Ready to transition to `/code architect`

## Dispatch

On `/code plan`: read each step file in order and execute its workflow. Skip steps whose output already exists and is current, unless the user requests a re-run.
