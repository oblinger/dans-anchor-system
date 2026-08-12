---
name: workflow
description: "The canonical state graph for any unit of work — what state it's in, what each state means, and what advances it."
user_invocable: false
group: discipline
---

:>> [[DAS]] → [[disciplines]] → [DAS workflow](hook://p/DAS%20workflow)
# Workflow Discipline
The **workflow discipline** owns the canonical state graph for any unit of work — what state it's in, what each state means, and what advances it. It is the single source of truth for the Definition of Ready and the state vocabulary used across the backlog, feature lifecycle, roadmap, and PRD.

**Related:** [[DAS Disciplines]],  [[DAS verification]],  [[DAS Backlog]]

This is the user-voice concept page. The full mechanics — transitions, anti-transitions, the `state` mutation API, per-surface mappings, and the Blocked/Waiting/Watching semantics — live in the agent-loaded runbook at [[workflow/SKILL|workflow/SKILL.md]], which is the canonical spec. This is a discipline (`user_invocable: false`): you don't invoke it directly; other skills (`/feature`, `/groom`, `/mint`, `/finalize`, `/code release`) cite it when they advance an item between states.

## The state graph — the bracket vocabulary

Each unit of work moves through these states. Status appears as a **square-bracket prefix** in the bullet (extending the markdown checkbox idiom).

| Bracket       | State     | What it means                                                                                       |
| ------------- | --------- | --------------------------------------------------------------------------------------------------- |
| `[ ]`         | Unset     | Idea captured. No progress yet.                                                                     |
| `[Designing]` | Designing | Being thought through. Design work in flight; no questions raised yet.                              |
| `[Questions]` | Questions | Waiting on user input. **Mandatory** `→ [[Feature Doc]]` link to the doc where the questions live.  |
| `[Blocked]`   | Blocked   | Blocked on a non-question item — dependency, external review, CI, infrastructure. Note the blocker. |
| `[Ready]`     | Ready     | Design clean. Agent could complete it without further user involvement.                             |
| `[Active]`    | Active    | Actively being worked on.                                                                          |
| `[Verify]`    | Verify    | Implementation done. Awaiting verification.                                                         |
| `[Done]`      | Done      | Verified done.                                                                                      |

Two optional extension states for surfaces that need them: `[Released]` (shipped after `/code release`) and `[Cancelled]` (abandoned without completing).

## The Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

If the task still hides any "wait, what about X?" the user would have to answer, it's not Ready — it's `[Questions]`, and the questions belong in a feature doc (with the bullet linking to it).

## Horizons vs workflow states

Two different axes — easy to confuse.

- **Horizon** (`Now` / `Next` / `Later`) — *when* you want the work to happen. Owned by [[DAS Backlog]].
- **Workflow state** (`Ready` / `Active` / etc.) — *whether* the work has progressed. Owned by this discipline.

`Now` is a scheduling intent; `[Active]` is "we've actually started." An item can sit in `## Now` as `[Ready]` for a while; once work begins it transitions to `[Active]`. How items advance between states (which skill drives each transition) is spelled out in [[workflow/SKILL|workflow/SKILL.md]] § State transitions.
