# Workflow Discipline

The **workflow discipline** owns the canonical state graph for any unit of work — what state it's in, what each state means, and what advances it. It is the single source of truth for the Definition of Ready and the state vocabulary used across the backlog, feature lifecycle, roadmap, and PRD.

This is a discipline (`user_invocable: false`) — you don't invoke it directly. Other skills (`/feature`, `/ready`, `/mint`, `/finalize`, `/code release`) cite it when they advance an item between states.

## The state graph

Each unit of work moves through these states. Status appears as a **square-bracket prefix** in the bullet (extending the markdown checkbox idiom).

| Bracket | State | What it means |
|---|---|---|
| `[ ]` | Unset | Idea captured. No progress yet. |
| `[Designing]` | Designing | Being thought through. Design questions in flight. |
| `[Blocked]` | Blocked | Waiting on user input. Paired with `→ [[Feature Doc]]`. |
| `[Ready]` | Ready | Design clean. Agent could complete it without further user involvement. |
| `[In Progress]` | In Progress | Actively being worked on. |
| `[Testing]` | Testing | Implementation done. Awaiting verification. |
| `[Completed]` | Completed | Verified done. |

Two optional extension states for surfaces that need them:

| Bracket | State | What it means |
|---|---|---|
| `[Released]` | Released | Shipped to users (after `/code release`). |
| `[Cancelled]` | Cancelled | Abandoned without completing. |

## The Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

If the task still hides any "wait, what about X?" the user would have to answer, it's not Ready — it's Blocked, and the questions belong in a feature doc.

## How items advance

Every state change is driven by a named skill. There are no silent transitions.

- **`/feature`** creates a feature doc → moves item to `[Designing]`. At the Agreed gate, moves to `[Ready]`.
- **`/ready`** walks the backlog and promotes items autonomously to `[Ready]`. If questions remain, parks the item in a feature doc as `[Blocked]`.
- **`ask-questions` discipline** manages the `[Blocked]` ↔ `[Designing]` cycle while the user answers questions.
- **`/mint`** (or `/code mint`, `/code bugfix`) takes a `[Ready]` item to `[In Progress]` to `[Testing]`.
- **`/code verify`** confirms `[Testing]` is real (tests pass, completion proof).
- **`finalize` discipline** closes `[Testing]` to `[Completed]` (verify, commit, push, merge, docs, cleanup).
- **`/code release`** ships `[Completed]` work to `[Released]`.

## Where workflow shows up

- **Backlog** (`{NAME} Backlog.md`) — items live under H2 sections; status shown via bracket prefix or H2 placement (in horizon sections, brackets show pre-Ready states; in workflow-state H2s like `## In Progress`, the H2 implies the state).
- **Feature docs** — the Status field at the bottom uses these state names. Historical labels (Proposed, Agreed, Done) map to the canonical states.
- **Roadmap milestones** — coarser granularity; a milestone's state is the most-advanced state shared by all its acceptance criteria.
- **PRDs** — light usage; PRD-internal states (Draft, Approved) only.

## Horizons vs workflow states

Two different axes — easy to confuse.

- **Horizon** (`Now` / `Next` / `Later`) — *when* you want the work to happen. Owned by `[[backlog-horizons]]`.
- **Workflow state** (`Ready` / `In Progress` / etc.) — *whether* the work has progressed. Owned by this discipline.

`Now` is a scheduling intent. `[In Progress]` is "we've actually started." An item can sit in `## Now` as `[Ready]` for a while; once work begins, it transitions to `[In Progress]` and typically moves out of the horizon section into `## In Progress`.

## When you'll notice this

- A backlog item's bullet starts with `[Status]` — that's the workflow state.
- A roster line shows per-state counts (e.g., `Ready: 5`, `In Progress: 2`) — those are workflow states.
- A feature doc's Status field changes — that's a workflow transition driven by whichever skill triggered it.
- Someone says "this is Ready" — it means the Definition of Ready is met, anywhere in the system.
