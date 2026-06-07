---
description: "F005 — Backlog"
---

# [[Backlog]] · F005 — Backlog

A discipline for how to organize a backlog so the user can push items off the front without sending them all the way to the Icebox. Adds three horizon sections (Now / Next / Later) inside the backlog, treats them as orthogonal to per-item status (Ready / Questions / Active / etc.), and is documented as a reusable discipline that multiple skills reference (`/groom`, `/roster`, `/feature`, …) — same shape as `ask-questions`.

## Summary

Today's backlog has a binary feel: items are either "in the backlog" (visible) or "in the Icebox" (invisible from the default `roster`). When the user wants to *defer* an item — push it off the front because it's not the next thing up — there's no good place for it. Pushing it into Icebox makes it disappear; leaving it in Upcoming keeps it competing with the imminent stuff.

The fix is **horizon sections within the backlog**: three ordered tiers (Now / Next / Later) that capture the gradient between "doing this soon" and "indefinite." Combined with the orthogonal "ready" status (which means *the agent could start this without further user input*, regardless of when it's scheduled), this gives the user a clean two-axis system.

## Design

### Definition of horizon

| Horizon | Membership |
|---|---|
| **Now** | Actively being pulled in or imminent — the next 1–2 cycles. The "we really expect to implement this shortly" zone. |
| **Next** | Committed but not the next thing up. Visible and ordered, but explicitly deferred. The bucket the user reaches for when they want to push something off Now without sending it to Icebox. |
| **Later** | Known wants — will get to eventually. Lower priority than Next, still feels obligatory. |
| **Icebox** | Outside the backlog. May never happen. (Already exists as a separate file `[[CAB Icebox]]`.) |

### "Ready" is orthogonal to horizon

Ready = *the agent believes it knows how to do this task without further involvement of the user*. It's a refinement check, not a scheduling check. Consequences:

- An item in **Later** can still be Ready (just no plan for when).
- An item in **Now** can be *not* Ready (we want to do it imminently but still have open questions to resolve).
- An item in **Icebox** can be Ready.

This is the core insight that lets the two-axis system work: status (Ready / Questions / Active / etc.) tells you *can the agent start this?*; horizon tells you *when does the user want it to happen?*. The two axes are represented separately in the bullet — see § Item bullet format below.

### Relationship to existing CAB Backlog structure

CAB Backlog currently uses these H2 sections: Active, Ready, Upcoming, Verify, Done, Legwork. Per Q2 resolution: **horizons replace `Upcoming`**. The three H2s `## Now`, `## Next`, `## Later` substitute for `## Upcoming`. The other H2s — `## Active`, `## Ready`, `## Verify`, `## Done`, `## Legwork` — stay. The precise semantics of how horizon H2s relate to workflow-state H2s (e.g., is `Now` ≈ `Active`, or distinct?) is owned by the **`workflow` discipline (B11)**, which factors out the canonical state graph and per-surface mappings.

### Item bullet format

Per Q5 resolution: each backlog item carries its workflow status as a **square-bracket prefix in the bullet**, generalizing the markdown checkbox idiom. Horizon is determined by H2 placement; status is determined by the bracket.

```
- **F{n} — Item Name** [ ] — fresh / no progress yet.
- **F{n} — Item Name** [Designing] — design open questions in flight.
- **F{n} — Item Name** [Questions] — blocked on user questions (paired with mandatory `→ [[Feature Doc]]`).
- **F{n} — Item Name** [Blocked] — blocked on something else (dependency, external review, CI). Note or link describing the blocker is best-practice.
- **F{n} — Item Name** [Ready] — ready in a horizon section, awaiting pull.
- **F{n} — Item Name** [Active] — actively being worked.
- **F{n} — Item Name** [Verify] — implementation done, awaiting verification.
- **F{n} — Item Name** [Done] — done. (Typically lives under `## Done` H2.)
```

The exact set of status tokens and their semantics is owned by the **`workflow` discipline (B11)**. This feature treats the bracket notation as the syntactic convention; the workflow discipline owns the semantics.

### Where the discipline lives

Per Q3 resolution: a **standalone discipline doc** in the `skills/` tree, parallel to `skills/ask-questions/SKILL.md`, with `user_invocable: false`. Per the parallel-docs rule (B12), the discipline ships with two docs:

- `skills/backlog-horizons/SKILL.md` — agent-facing discipline doc.
- `skills/SKL User Docs/SKL Skills/SKL Backlog.md` — user-facing.

CAB Backlog file-format spec stays focused on file format; this discipline addresses *behavior over time* and cites CAB Backlog for layout, the `workflow` discipline for state semantics, and is cited from `/groom`, `/roster`, `/feature`, future `/code` priorities.

### Practical test for Now → Next → Later moves

Per Q6 resolution: enshrine the **boredom test** as a discipline rule.

> Before moving an item from Now to Next, or Next to Later, ask: *"Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?"* If the latter — leave it in Now and either schedule it or genuinely demote it. The horizon move should reflect a real shift in commitment, not procrastination dressed up as planning.

Without this guardrail, the discipline can easily become a procrastination tool — the bucket-shuffling becomes the work instead of the actual work.

### `/roster` changes

Per Q4 resolution: roster prints a single line of per-bucket counts using single-word labels — one count per bucket, **no double-counting**. The sum across the line equals the total number of items in the backlog file (Icebox is separate, outside the backlog).

Format roughly:

```
Active: 2  Ready: 5  Now: 3  Next: 7  Later: 4  Verify: 1  (Icebox: 12)
```

Each item appears in exactly one bucket. Items in the workflow-state H2s (`## Active`, `## Ready`, `## Verify`) count under those labels regardless of horizon. Items in horizon sections (`## Now`, `## Next`, `## Later`) count under the horizon. The `## Done` H2 is excluded from the active-work line by default.

## Prior Discussion (captured verbatim)

> What you're describing is a real pattern — the gap between "imminent" and "indefinite" — and the conventional fix is exactly what you're circling: horizon sections inside the backlog, not a separate document.
>
> Here's what I'd suggest, and why:
>
> **Keep ready orthogonal.** Your instinct is right — ready is a refinement check ("could we start this if we wanted to?") and has nothing to do with when. An icebox item can absolutely be ready. Don't conflate them. This already gives you a clean two-axis system.
>
> **Use horizon sections within the backlog.** Three tiers, in one ordered document:
>
> - **Now** — actively being pulled in or imminent (next 1–2 cycles). The "really expecting to implement shortly" zone you described.
> - **Next** — committed, but not the next thing up. This is the bucket you keep wanting and don't have. Visible, ordered, but explicitly deferred.
> - **Later** — known wants, will get to eventually. Lower priority than Next but you still feel the obligation.
>
> Then **Icebox** sits *outside* the backlog as the "may never happen" parking lot.
>
> This solves your specific problem: when you want to push something off the front of the backlog, you move it from Now → Next (or Next → Later). Still visible when you ask "what's on the backlog?" — just below the imminent stuff. Icebox stays for things you genuinely don't expect to do.
>
> **On grouping vs. separate documents:** keep it one document. The whole point is that "show me status" returns everything — separating documents recreates the icebox-invisibility problem. If the document gets long, fold the lower sections by default in your viewer rather than splitting the file.
>
> **On naming:** Now/Next/Later is the most common convention (ProdPad, Cagan, Basecamp-adjacent teams), but if you already have "Soon," "Upcoming," "Planned," pick three and kill the rest. The names matter less than having exactly three horizons with sharp tests for membership.
>
> **Practical test for the Now → Next move:** "Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?" If the latter — leave it in Now and force yourself to either schedule it or genuinely demote it. The horizon move should reflect a real shift in commitment, not procrastination dressed up as planning.

(Source: a separate-agent discussion the user had on 2026-04-29, retained here so the design conversation has the original framing.)

## Status

Done — 2026-04-30 (commit `b7a7e5e`). User accepted the discipline as a good first version (open to future edits).

## Resolved

- **Q1 — Horizon names: Now / Next / Later, or something else?** — **Resolution:** **Now / Next / Later**. Confirmed 2026-04-30. Short, sharp, conventional. Incorporated into Design § Definition of horizon.

- **Q2 — How do horizons coexist with existing CAB Backlog H2 sections?** — **Resolution:** Replace `## Upcoming` with three horizon H2s `## Now`, `## Next`, `## Later`. Keep `## Active`, `## Ready`, `## Verify`, `## Done` as workflow-state H2s. The precise semantics of how horizon H2s relate to workflow-state H2s (e.g., "is `Now` ≈ `Active`, or distinct?") is **deferred to the new `workflow` discipline (B11)** — that doc owns the canonical state graph and per-surface mappings. Incorporated into Design § Relationship to existing CAB Backlog structure.

- **Q3 — Where does this discipline live?** — **Resolution:** Separate discipline doc, parallel to `ask-questions`. `skills/backlog-horizons/SKILL.md` (agent-facing) + `skills/SKL User Docs/SKL Skills/SKL Backlog.md` (user-facing) per the parallel-docs rule (B12). CAB Backlog file-format spec stays focused on file format and cites this discipline. Incorporated into Design § Where the discipline lives.

- **Q4 — How does `/roster` change to reflect horizons?** — **Resolution:** Roster prints a single line of per-bucket counts using single-word labels — one count per bucket, no double-counting. The sum across the line equals total backlog items. Format roughly: `Active: N | Ready: N | Now: N | Next: N | Later: N | Verify: N`. Each item appears in exactly one bucket. Icebox count stays separate (outside the backlog total). Incorporated into Design § /roster changes.

- **Q5 — Status × horizon as two independent axes — how to represent on a bullet?** — **Resolution:** Status uses square-bracket notation in the bullet text — a generalization of the markdown checkbox (`[ ]`, `[x]`). Examples: `[ ]` (fresh / no progress), `[Designing]`, `[Questions]`, `[Blocked]`, `[Ready]`, `[Active]`, `[Verify]`, `[Done]`. Horizon is determined by H2 placement; status is determined by the bracket. The exact set of status tokens and their semantics is owned by the **`workflow` discipline (B11)**. Incorporated into Design § Item bullet format.

- **Q6 — Should the "boredom test" be part of the discipline?** — **Resolution:** **Yes — enshrine it.** "Am I avoiding this because there's a real reason it should wait, or because I'm bored of it?" The discipline can easily become a procrastination tool without this guardrail. Incorporated into Design § Practical test for Now → Next → Later moves.
