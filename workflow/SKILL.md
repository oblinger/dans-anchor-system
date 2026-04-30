---
name: workflow
description: Discipline that owns the canonical state graph for a unit of work — state names, transitions, Definition of Ready, and per-surface mappings (Backlog, Roadmap, Feature lifecycle, PRD). Cited from CAB Backlog, feature/SKILL.md, /ready, /mint, /finalize, and other skills that advance work through states.
user_invocable: false
---

# Workflow Discipline

The single source of truth for **what state a unit of work is in**, **what it means**, and **what advances it to the next state**. Every skill that touches the state of work — `/ready`, `/feature`, `/mint`, `/finalize`, `/code release`, `/roster`, audits — cites this discipline.

## Why this exists — the problem it solves

The same vocabulary appears across many surfaces: backlog items have a status, feature docs have a Status field, roadmap milestones have progress, PRDs have a draft/approved cycle. **The labels diverge subtly** — "Agreed" in feature lifecycle is roughly "Ready" in backlog; "Done" in features is "Completed" in backlog; "In Progress" appears in both but with slightly different gates. Skills that touch state pick whichever label was nearest at hand.

The drift compounds: a new skill writes its own state names; the user can't tell at a glance whether `Designing` and `Proposed` are the same thing or different; the Definition of Ready lives in CAB Backlog but is implicitly assumed by skills that don't cite it.

This discipline collapses that to **one state graph** with **one Definition of Ready** that every surface and every skill references. Surfaces (backlog, roadmap, feature, PRD) get a short mapping section saying "here's how the canonical states appear here" — they don't redefine the graph.

## The canonical state graph

A unit of work moves through these states. Each state has a **square-bracket label** that appears in bullet form (extending the markdown checkbox idiom) and a **canonical name**.

| Label | Canonical name | Meaning |
|---|---|---|
| `[ ]` | **Unset** | Idea captured, no progress yet. Default for new items. |
| `[Designing]` | **Designing** | Being thought through. Design questions in flight; spec not yet locked. |
| `[Blocked]` | **Blocked** | Pending user input on questions. Paired with a `→ [[Feature Doc]]` link to where the questions live. |
| `[Ready]` | **Ready** | Design clean. Agent knows how to do the task without further user involvement. (See § Definition of Ready.) |
| `[In Progress]` | **In Progress** | Actively being worked on. |
| `[Testing]` | **Testing** | Implementation done, awaiting verification (tests passing, user confirmation, or both per surface). |
| `[Completed]` | **Completed** | Verified done. Terminal state for most work. |

Two **optional extension states** that not every surface uses:

| Label | Canonical name | Meaning |
|---|---|---|
| `[Released]` | **Released** | Shipped to users (post-`/code release`). Used when the surface tracks shipped state distinctly from completed. |
| `[Cancelled]` | **Cancelled** | Work was abandoned without completion. Terminal but not a success. |

### State graph

```
        ┌─────┐
        │ [ ] │  Unset
        └──┬──┘
           │  someone starts thinking
           ↓
   ┌──────────────┐
   │ [Designing]  │
   └──┬────────┬──┘
      │        │
      │ design │ user input needed
      │ clean  ↓
      │  ┌───────────┐
      │  │ [Blocked] │ ◄─── ask-questions discipline
      │  └─────┬─────┘
      │        │ user resolves
      ↓        ↓
   ┌────────────┐
   │  [Ready]   │  ◄─── /ready promotes here
   └─────┬──────┘
         │  /mint, /code mint, /code bugfix
         ↓
   ┌────────────────┐
   │ [In Progress]  │
   └─────┬──────────┘
         │  implementation complete
         ↓
   ┌─────────────┐
   │  [Testing]  │
   └─────┬───────┘
         │  /finalize discipline
         ↓
   ┌──────────────┐
   │ [Completed]  │  (optional: → [Released] via /code release)
   └──────────────┘
```

### Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

Sharper than "design questions resolved." If the task still hides any "wait, what about X?" that the user would have to answer, it's **not** Ready — it's `[Blocked]`, and the work belongs in a feature doc until those questions resolve.

This is the canonical definition. CAB Backlog cites it; `/ready` checks it for each candidate; `/feature` gates the Designing → Ready transition on it.

## State transitions

Every transition is driven by an explicit skill or trigger. There are no silent state changes.

| From | To | Triggered by | Notes |
|---|---|---|---|
| `[ ]` | `[Designing]` | `/feature`, manual edit, `/code plan` | A feature doc is created OR planning begins. |
| `[Designing]` | `[Blocked]` | ask-questions discipline | Pending Qs added to `## Open Questions`; bullet description rewritten as `→ [[Feature Doc]]`. |
| `[Blocked]` | `[Designing]` | User answers Qs | When pending Qs are resolved (`### Resolved`), description gets rewritten to reflect the resolved design. |
| `[Designing]` | `[Ready]` | `/ready`, `/feature` (Agreed gate) | Design is locked; Definition of Ready met. |
| `[ ]` | `[Ready]` | `/ready` (autonomous) | Item was clear enough that `/ready` could promote without going through Designing. |
| `[Ready]` | `[In Progress]` | `/mint`, `/code mint`, `/code bugfix`, `/code spike`, manual claim | Work begins. |
| `[In Progress]` | `[Testing]` | `/code mint`, `/code verify`, `/finalize` (verify step) | Implementation done; awaiting verification. |
| `[Testing]` | `[Completed]` | `/finalize` discipline (verify → commit → push → merge → docs → cleanup), user confirmation | Verification passed. |
| `[Completed]` | `[Released]` | `/code release` (optional) | Surfaces that distinguish shipped state. |
| any | `[Cancelled]` | manual decision | Work abandoned. Bullet typically moves to a "Cancelled" or "Icebox" location. |

### Anti-transitions (state changes that should NOT happen silently)

- **`[In Progress]` directly to `[Completed]`.** Always pass through `[Testing]` so verification is explicit (`/finalize` owns this).
- **`[Designing]` to `[In Progress]` skipping `[Ready]`.** Definition of Ready is the gate; without it, you risk implementing on unresolved design.
- **`[Completed]` back to any earlier state.** Once Completed, the work is closed. Reopening means a new B-number for the follow-up.

## Skill cross-references

| Skill | What it advances |
|---|---|
| `/feature` | `[ ]` → `[Designing]` (creates feature doc); `[Designing]` → `[Ready]` at the Agreed gate. |
| `/ready` | `[ ]` or `[Designing]` → `[Ready]` autonomously, or `[Designing]` → `[Blocked]` if questions remain. |
| `/ask-questions` (discipline) | Manages `[Blocked]` ↔ `[Designing]` via question batching and resolution. |
| `/mint`, `/code mint` | `[Ready]` → `[In Progress]` → `[Testing]`. |
| `/code bugfix` | Same as `/mint` but with a red-test gate at the start. |
| `/code spike` | Stays in `[In Progress]` while diagnosing root cause. |
| `/code verify` | `[In Progress]` → `[Testing]` (proof of completion). |
| `/finalize` (discipline) | `[Testing]` → `[Completed]` (verify, commit, push, merge, update docs, cleanup). |
| `/code release` | `[Completed]` → `[Released]` (changelog, version, package, publish, ship). |
| `/roster` | Reads state across all items and prints per-bucket counts. |
| `/audit` | Generates new `[ ]` items from findings (no state advancement). |

## Per-surface mappings

Each surface that uses workflow state cites this discipline and maps the canonical states onto its own structure.

### Backlog (`{NAME} Backlog.md`)

Per `[[CAB Backlog]]` and `[[backlog-horizons]]`:

- Workflow state is shown via the `[Status]` square-bracket prefix in each bullet, OR implied by the bullet's H2 placement.
- H2 sections combine **horizon** (`## Now`, `## Next`, `## Later`) and **workflow state** (`## In Progress`, `## Ready`, `## Testing`, `## Completed`).
- Items in horizon H2s use `[Status]` brackets for their pre-Ready or Blocked state.
- Items in workflow-state H2s have their state implied by the H2 — the bracket is optional/redundant.
- The `## Legwork` H2 is a **category tag**, not a workflow state. Items in Legwork still have a state (Ready / In Progress / etc.), shown in their bracket.

### Roadmap (`{NAME} Roadmap.md`)

Milestones use the same canonical states at coarser granularity. A milestone is in the **most-advanced state shared by all its acceptance criteria**:

- All criteria `[Completed]` → milestone `[Completed]`.
- Any criterion `[In Progress]` → milestone `[In Progress]`.
- All criteria `[Ready]` or beyond → milestone `[Ready]`.
- Else → milestone `[Designing]` or `[Blocked]` per most-blocking criterion.

### Feature lifecycle (`feature/SKILL.md`)

The feature doc Status field uses the canonical states. The current feature lifecycle has historical labels that map as follows:

| Feature lifecycle label | Canonical state | Notes |
|---|---|---|
| Proposed | `[Designing]` | Idea captured; design hasn't started. (See § Design choices to validate — may collapse.) |
| Designing | `[Designing]` | Same. |
| Agreed | `[Ready]` | User has approved the design. (See § Design choices to validate — may collapse.) |
| Implementing | `[In Progress]` | Same. |
| Testing | `[Testing]` | Same. |
| Done | `[Completed]` | Same. |

### PRD

Light usage. PRDs are documents, not units of work — they're *artifacts* produced during the Designing phase of a feature or planning cycle. Common PRD-internal states:

- `[Draft]` — being written.
- `[Approved]` — user has signed off; work can proceed against this PRD.

These are PRD-doc-internal; they don't appear in backlog or roster.

## Horizons vs workflow states

These are **two independent axes**:

- **Horizon** — *when* the user wants the work to happen. Owned by `[[backlog-horizons]]`. Values: Now, Next, Later (plus Icebox outside the backlog).
- **Workflow state** — *whether* the work has progressed and how far. Owned by this discipline. Values: Unset, Designing, Blocked, Ready, In Progress, Testing, Completed.

**Common conflation: "Now" vs "In Progress."** They look similar but mean different things.

- `Now` is a **scheduling intent**: "we want to pull this into action soon."
- `[In Progress]` is a **state**: "we have actually started and are working on it."

An item can sit in `## Now` for a while as `[Ready]` (we want to do it soon, haven't started yet). When work begins, it transitions to `[In Progress]` and typically **moves out of the horizon section into `## In Progress`** — because once active, the horizon question is moot.

Same for `[Testing]` and `[Completed]`: those states have their own H2s. Horizon H2s are for **upcoming** work (pre-In-Progress); workflow-state H2s are for **active and finished** work.

## Anti-patterns

- **Inventing a new state name** instead of citing the canonical one. If your skill needs a state that isn't in the canonical graph, propose adding it here — don't fork.
- **Implicit state transitions.** Every state change should be driven by a named skill or trigger; "the agent decided" is not a transition.
- **Treating "Ready" loosely.** Ready means *the agent could complete this without involving the user*. If you're tempted to mark something Ready while still planning to ask the user something, it's `[Designing]` or `[Blocked]`, not `[Ready]`.
- **Skipping `[Testing]`.** Implementations that go straight to Completed bypass the verification gate. `/finalize` enforces this; manual edits should respect it.
- **State drift between surfaces.** If a backlog item is `[In Progress]` but the feature doc Status says "Designing," one of them is wrong — the user shouldn't have to guess which.

## Design choices to validate

This discipline has open questions on a few design choices. See the feature doc:

- → [[2026-04-30 Workflow Discipline]] — pending Qs on feature-lifecycle alias collapse, Released as a standard state, Blocked granularity.
