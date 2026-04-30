---
name: backlog-horizons
description: Discipline for organizing a backlog along two independent axes — horizon (when the user wants work to happen) and workflow state (whether work has progressed). Adds three horizon H2s — Now / Next / Later — that replace the legacy `## Upcoming` section. Cited from CAB Backlog, /groom, /roster, /feature, /triage.
user_invocable: false
---

# Backlog Horizons Discipline

Two-axis organization of a backlog. **Horizon** answers *when do we want this to happen?* **Workflow state** answers *how far has it progressed?* The two are orthogonal — an item in `## Later` can be `[Ready]`; an item in `## Now` can be `[Designing]`. Horizon is shown by H2 placement; workflow state is shown by the `[Status]` bracket per the `[[workflow]]` discipline.


## Why this exists — the problem it solves

A binary backlog (visible vs Icebox) gives the user no way to *defer* an item without sending it to cold storage. Pushing not-the-next-thing to Icebox makes it disappear from the default `roster`; leaving it in `## Upcoming` makes it compete visually with the imminent stuff. Without a middle gradient, the user either over-promotes (pushes to Active) or over-demotes (sends to Icebox), and the backlog ceases to reflect actual intent.

This discipline introduces three ordered tiers — **Now / Next / Later** — that capture the gradient between *imminent* and *indefinite*. Items still inside the backlog (visible to roster), but with a clear "when" attached.


## The horizons

| Horizon  | Membership |
|---|---|
| **Now**   | Actively being pulled in or imminent — the next 1–2 cycles. The "we really expect to implement this shortly" zone. |
| **Next**  | Committed but not the next thing up. Visible and ordered, but explicitly deferred. The bucket the user reaches for when they want to push something off Now without sending it to Icebox. |
| **Later** | Known wants — will get to eventually. Lower priority than Next, still feels obligatory. |
| **Icebox** | Outside the backlog file entirely (lives in `[[CAB Icebox]]`). May never happen. |

Three is intentional. Two horizons (Now / Later) collapse to the binary problem; four+ horizons just reintroduce the bucket-shuffling overhead that the discipline tries to bound.


## Two independent axes

- **Horizon** — owned by *this* discipline. Determined by H2 placement. Values: Now, Next, Later (Icebox outside).
- **Workflow state** — owned by `[[workflow]]`. Determined by `[Status]` bracket on the bullet. Values: `[ ]` / `[Designing]` / `[Questions]` / `[Blocked]` / `[Ready]` / `[Active]` / `[Verify]` / `[Done]`.

An item can be:

- `## Later` + `[Ready]` — design is clean, just no plan for when. (Common: low-effort items the agent could start anytime, but the user has bigger fish to fry.)
- `## Now` + `[Designing]` — we want to pull this in soon, but it still has unresolved questions. (Drives `/groom` to surface the questions.)
- `## Now` + `[Questions]` — same, but with the `→ [[Feature Doc]]` link convention pinning where the questions live.

The bracket is **mandatory** for items in horizon H2s (so the workflow state is visible without opening the feature doc). The bracket is **optional/redundant** for items in workflow-state H2s (`## Active`, `## Ready`, `## Verify`, `## Done`) where the H2 already implies the state.


## Relationship to existing CAB Backlog H2 sections

CAB Backlog uses three kinds of H2:

| Kind | H2s | What determines membership |
|---|---|---|
| **Workflow-state** | `## Active`, `## Ready`, `## Verify`, `## Done` | Items currently in that workflow state. State implied by H2; bracket optional. |
| **Horizon** | `## Now`, `## Next`, `## Later` | Items in pre-Active workflow states (Designing / Questions / Blocked / Ready), grouped by *when* the user wants to pull them in. State carried by the bracket. |
| **Category** | `## Legwork` | Cross-cutting tag for autonomous agent work. Not a state and not a horizon. Items in Legwork still have a state (shown in bracket) and may have a horizon implied by adjacency. |

The horizon sections **replace the legacy `## Upcoming` H2**. After migration, an item that used to live in `## Upcoming` lives in `## Now`, `## Next`, or `## Later` — pick the horizon that matches actual intent.

### Where does Ready fit?

Two valid placements; both are correct:

1. **`## Ready` H2 (workflow-state)** — for items the agent is most likely to pull next. Surfaces "what could the agent grab right now if cranked." This is the conventional location.
2. **Horizon H2 with `[Ready]` bracket** — for items that are design-clean but explicitly scheduled for later. E.g., a `## Later` item with `[Ready]` is "we know how to do this; we're just not doing it now."

When in doubt, prefer `## Ready` for items the user expects to be picked up imminently and a horizon H2 for items where the *when* matters more than the *can-the-agent-start*.


## Roster integration — single count line

`/roster` prints a single line of per-bucket counts using single-word labels — one count per bucket, no double-counting. The sum equals the number of bullets in the backlog file (Icebox is separate).

```
Active: 2  Ready: 5  Now: 3  Next: 7  Later: 4  Verify: 1  (Icebox: 12)
```

Each item appears in exactly one bucket — its H2. Items under workflow-state H2s count under their state label; items under horizon H2s count under their horizon label. `## Done` is excluded from the active-work line by default.

Single labels (no compound "Ready/Now"), single count per item. Resist any temptation to "double-count" Ready items into both the Ready bucket *and* their horizon bucket — that breaks the "sum = total" invariant and makes the line unreadable.


## /groom integration

`/groom` walks the backlog looking for items with status `Unset / Upcoming` (per `[[CAB Backlog]]` § Item Status). Under this discipline:

- Items in horizon H2s with bracket `[ ]`, `[Designing]`, or absent are candidates for `/groom` to investigate.
- Items in horizon H2s with bracket `[Ready]` are already ready — `/groom` skips them (they're awaiting pull, not promotion).
- When `/groom` promotes a horizon-H2 item to Ready, it has two choices:
  - (a) Move the bullet to `## Ready` H2 (conventional path; surfaces it as next-up).
  - (b) Update the bracket to `[Ready]` and leave the bullet in its horizon H2 (preserves the user's *when* intent).
  - **Default**: (a). Move to `## Ready`. The user can demote back to a horizon H2 if they explicitly want the item readied-but-deferred.

When `/groom` parks an item with questions, it uses the `→ [[Feature Doc]]` link convention from `[[CAB Backlog]]` and updates the bracket to `[Questions]`. The bullet stays in its horizon H2.


## The boredom test — practical guardrail for horizon moves

Before moving an item from `## Now` to `## Next`, or from `## Next` to `## Later`, ask:

> *"Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?"*

If it's the latter — leave it in Now and either schedule it for real or genuinely demote it (out of the active-work picture entirely). The horizon move should reflect a real shift in commitment, not procrastination dressed up as planning.

Without this guardrail, the discipline can become a procrastination tool — bucket-shuffling becomes the work instead of the actual work.


## Anti-patterns

- **Conflating Now with Active.** `## Now` is a *scheduling intent* ("we want to pull this in soon"); `## Active` is a *state* ("we have started"). When work begins, the bullet moves out of `## Now` into `## Active`. They are not interchangeable.
- **Demoting to Later as a substitute for Icebox.** If the item may genuinely never happen, send it to Icebox. `## Later` items are still on the backlog total; the user owes them attention eventually.
- **Skipping the bracket in horizon H2s.** Without `[Status]`, the workflow state is invisible. Always include the bracket on items in `## Now`, `## Next`, `## Later`.
- **Inventing a fourth horizon ("Soon", "Eventually", "Maybe").** Three was a deliberate choice. If you need finer granularity, the answer is usually "use status brackets and the boredom test more aggressively," not "add another H2."
- **Treating horizons as state.** Horizons are *user intent over time*; state is *progress through the work*. Don't merge them — the two-axis property is what makes the discipline useful.


## Triggers — when to apply

Apply this discipline whenever:

- A backlog file is being created, audited, or reorganized.
- An item needs to be deferred without disappearing.
- `/roster` prints its count line.
- `/groom` walks the backlog.
- A new skill or audit needs to talk about "what's coming up" vs "what's deferred."

For backlogs that are short enough that all items fit comfortably in one mental glance (≤ ~10 items), the horizons can be deferred — the discipline is overkill until the backlog earns it.
