---
description: "The **backlog discipline** organizes a backlog along two independent axes — *when* the user wants work to happen (horizon) and *how far* the work has progressed (workflow state) — so items…"
---
# Backlog-Horizons Discipline

The **backlog discipline** organizes a backlog along two independent axes — *when* the user wants work to happen (horizon) and *how far* the work has progressed (workflow state) — so items can be deferred without disappearing into the Icebox.

This is a discipline (`user_invocable: false`) — you don't invoke it directly. It governs how `[[CAB Backlog]]` is structured, how `/roster` prints counts, how `/groom` decides which items to investigate, and how items can be pushed off the front of the backlog without losing them.

## Why this exists — the problem it solves

Without horizons, the backlog has a binary feel: items are either "in" (visible, competing for attention) or "in the Icebox" (effectively invisible). When you want to *defer* an item — push it off the front because it's not the next thing up — there's no good place for it. Pushing to Icebox makes it disappear; leaving it in `## Upcoming` keeps it competing with imminent stuff.

Horizons fix this. The backlog gets three ordered tiers — **Now**, **Next**, **Later** — that capture the gradient between *imminent* and *indefinite* without leaving the backlog entirely.

## The horizons

| Horizon  | What it means |
|---|---|
| **Now**   | Imminent — the next 1–2 cycles. "We really expect to do this shortly." |
| **Next**  | Committed but not the next thing up. Visible and ordered, but explicitly deferred. The bucket you reach for when pushing something off Now without sending it to Icebox. |
| **Later** | Known wants — will get to eventually. Lower priority than Next, still feels obligatory. |
| **Icebox** | Outside the backlog file. May never happen. (Lives in `[[CAB Icebox]]`.) |

## Two axes, not one

A backlog item carries **both** a horizon and a workflow state. They're independent:

- `## Later` + `[Ready]` — design is clean; just no plan for when.
- `## Now` + `[Designing]` — we want this soon, but it still has open questions.
- `## Now` + `[Active]` — would be unusual; once active, the item moves to `## Active` H2.

Horizon comes from H2 placement. State comes from the `[Status]` bracket on the bullet — `[ ]`, `[Designing]`, `[Questions]`, `[Blocked]`, `[Ready]`, `[Active]`, `[Verify]`, `[Done]`. The bracket is mandatory in horizon H2s; optional in workflow-state H2s where the H2 already implies the state.

## What you'll notice

- The backlog has H2 sections `## Now`, `## Next`, `## Later` instead of the legacy `## Upcoming`.
- `/roster` prints a single per-bucket count line: `Active: N  Ready: N  Now: N  Next: N  Later: N  Verify: N  (Icebox: N)`. Each item counts in exactly one bucket.
- `/groom` moves promoted items to `## Ready` by default but respects horizon placement when you explicitly want an item readied-but-deferred.
- When you say "push F12 to next," the agent moves the bullet from `## Now` to `## Next`, preserving its bracket.

## The boredom test

Before moving an item from Now → Next or Next → Later, ask:

> *"Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?"*

If it's the latter — leave it in Now and either schedule it for real or genuinely demote it (to Icebox). The horizon move should reflect a real shift in commitment, not procrastination dressed up as planning.

The discipline can easily become a procrastination tool without this guardrail. The agent applies the test before suggesting a horizon demotion.

## Common confusion: Now vs Active

`## Now` is a **scheduling intent** ("we want to pull this in soon"). `## Active` is a **state** ("we have started"). They are not interchangeable. An item sits in `## Now` until work begins, then moves to `## Active`.
