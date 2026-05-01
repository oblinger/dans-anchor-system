---
description: deferred work items
---
# CAB Backlog

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`


The backlog file (`{NAME} Backlog.md`) holds ideas, low-priority tasks, and deferred work that don't belong on the active Todo or Roadmap yet. Items graduate to the Roadmap or Todo when they become priorities.

For items the user wants to remember but is **not** actively considering — distant-future / someday-maybe entries — use the optional [[CAB Icebox]] instead. Backlog is the *active* deferred-work list; Icebox is the *frozen* one.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Backlog.md` — Backlog.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Backlog


## Active
- **F3 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries

## Ready
- **F1 — Cron syntax** — Support cron expressions for recurring task schedules

## Now
- **F2 — Task groups** [Designing] — Allow grouping related tasks that run as a batch
- **F7 — Webhook notifications** [Verify] — Webhook fires on task completion. Verify: trigger a test job and check that the configured webhook URL receives a POST with the documented JSON payload (see [[CAE PRD]] § Webhooks).

## Next
- **F4 — Priority levels** [ ] — Add high/medium/low priority beyond just deadline ordering

## Later
- **F11 — Async task DAGs** [ ] — Long-shot: support directed-acyclic dependencies between tasks

## Done
- **F5 — Retry config** — Per-task retry limits (done in PR #4, see [[CAE Roadmap#M2]])
- **F6 — JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **F9 — User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **F8 — Doc consistency pass** — Module docs reference old API names from pre-M2
- **F10 — Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

---



# Format Specification

## Format

Each entry is a named-list item with a unique **F-number** prefix:

```
- **F{n} — Item Name** [Status] — short description.
```

`F` is for **feature**, in the broad sense of "a thing to be done" — not strictly "feature document." Every backlog item gets an F-number, whether or not it warrants a separate feature doc. If the item has a feature doc, that doc's H1 carries the same F-number; if not, the F-row stands alone in the backlog with the description inline.

The F-number lets the user refer unambiguously to a single item ("do F5", "F12 needs more detail").

### Numbering policy — monotonic, never recycled

F-numbers are **assigned in monotonically increasing order** and **never reused**. When a new item is added, it gets `F{highest-F-in-file + 1}`. When an item reaches Done (or moves to Icebox, or is cancelled), its F-number is **not** released back into the pool. Stable forever.

**F-number namespace is shared across backlog AND icebox** (per `[[workflow]]` § Active-work invariant). When numbering a new feature, take the highest F-number across both `{NAME} Backlog.md` and `{NAME} Icebox.md` and increment. An item moving from backlog to icebox keeps its F-number; thawing back to backlog restores the same F-number. No collisions ever.

**M-numbers are a separate namespace for roadmap milestones** (`{NAME} Roadmap.md`). M-numbers are hierarchical (M1, M1.2, M1.2.3) and are unique only within the roadmap; they don't collide with F-numbers.

This is a change from the legacy B-number policy, which used gap-fill (lowest unused integer). With F-numbers:

- A reference like "F11" means the same thing forever, across all reorganizations.
- Display order in the file may not match numeric order — items are added and resolved in arbitrary order.
- Don't renumber existing items to compact — F-numbers are stable references.

### Transition note: pre-existing B-numbers

Anchors that have historical Done items numbered with the legacy `B<n>` convention preserve those numbers as-is — they cite commit hashes and are part of the historical record. Active items at migration time get renamed `B<n>` → `F<n>` (preserving the number); new items thereafter increment past the highest existing F or B in the file. So a backlog mid-migration may show:

```
## Done
- **B1 — ...** — (historical)
- **B7 — ...** — (historical)

## Ready
- **F11 — ...** — (active, was B11 pre-migration)

## Upcoming
- **F16 — ...** — (new since migration)
```

## Status brackets

Each F-row may carry a workflow-state bracket per the `[[workflow]]` discipline: `[ ]` / `[Designing]` / `[Questions]` / `[Blocked]` / `[Ready]` / `[Active]` / `[Verify]` / `[Done]`. The bracket is mandatory only for items in horizon sections (Now/Next/Later — per `[[backlog-horizons]]`). Items in workflow-state H2s (`## Ready`, `## Active`, `## Verify`, `## Done`) have their state implied by the H2; the bracket is optional/redundant.

## H2 sections

Entries are grouped under H2 sections of three kinds — workflow-state, horizon, and category. The full discipline lives in `[[backlog-horizons]]`; the summary is:

**Workflow-state H2s** (state implied by H2; `[Status]` bracket optional/redundant):

- **Active** — Items the Pilot is actively driving forward right now (state `[Active]`).
- **Ready** — Items whose status is `[Ready]` (see § Definition of Ready below).
- **Done** — Items that graduated and were finished (with cross-references to where).

**Verify is a status, not a section.** Items in `[Verify]` state stay in their horizon H2 (`## Now` is typical, since most verify happens on imminent work) with the `[Verify]` bracket. There is no `## Verify` H2. Rationale: verify is short-lived (waiting on user yes/no) and conceptually keeps the item in its horizon — verifying it doesn't change the *when* intent. The bracket alone carries the state.

**Horizon H2s** (per `[[backlog-horizons]]`; `[Status]` bracket mandatory — workflow state is carried by the bracket since the H2 only conveys *when*):

- **Now** — Imminent — the next 1–2 cycles. The "we really expect to do this shortly" zone.
- **Next** — Committed but not the next thing up. Visible and ordered, but explicitly deferred.
- **Later** — Known wants — will get to eventually. Lower priority than Next.

**Category H2** (cross-cutting; not a state and not a horizon):

- **Legwork** — Autonomous agent work that should be done proactively. Includes user feedback integration, planning actions, doc consistency fixes, and other tasks the agent can execute without user approval. The `/code execute` priority loop pulls from this section as Tier 2 legwork (after PR merging and worker dispatch).

Items typically flow `Now [ ] → Now [Ready] → ## Active → Now [Verify] → ## Done` (or `Next/Later → Now → ...` when scheduling intent shifts). Note: `[Verify]` items stay in their horizon H2 with the bracket; they don't move to a separate H2. The `roster` skill prints a per-bucket count line (one count per H2 plus a Verify count derived from brackets across horizon H2s; sum equals total). The `groom` skill walks horizon H2s looking for items with status `Unset / Designing / Questions / Blocked` and tries to promote candidates to `[Ready]` (see § Definition of Ready and § Item Status below).

**Legacy `## Upcoming`.** Anchors that pre-date the horizons discipline may still have `## Upcoming` as the catch-all pre-ready section. Treat it as a transitional alias for `## Now` until the anchor is migrated. New backlogs use `## Now / ## Next / ## Later` from the start.

For items that are explicitly parked / out-of-scope-for-now / someday-maybe, use the optional [[CAB Icebox]] file rather than a Deferred section here.

## Definition of Ready

The canonical definition lives in the **`workflow` discipline** — see `[[workflow]]` § Definition of Ready. The full state graph (`[Designing]` / `[Questions]` / `[Blocked]` / `[Ready]` / `[Active]` / `[Verify]` / `[Done]`) and the bar for each transition also live there.

For convenience: **An item is Ready when you believe you know how to do this task without further involvement of the user.** This is the bar `/groom` checks for each candidate. If the task still hides any "wait, what about X?" the user would have to answer, it's not Ready — it's `[Questions]`, paired with a `→ [[Feature Doc]]` link to where the questions live.

## Item Status

Every backlog item has one of these statuses, derived from where the bullet sits and what (if anything) it links to:

| Status | How to recognize |
| --- | --- |
| **Ready** | Bullet is under `## Ready`. |
| **Active** | Bullet is under `## Active`. |
| **Questions** | Bullet text contains a `→ [[Feature Doc]]` link to a doc with pending questions; status bracket `[Questions]`. The item is parked there until the user answers. |
| **Blocked** | Bullet has bracket `[Blocked]`; pending non-question blocker (dependency, external review, CI). |
| **Verify** | Bullet has bracket `[Verify]` (lives under its horizon H2; no dedicated `## Verify` H2). |
| **Done** | Bullet is under `## Done`. |
| **Unset / Upcoming** | Bullet is under a horizon H2 (`## Now`, `## Next`, `## Later`) — or the legacy `## Upcoming` — or `## Legwork`, with bracket `[ ]` / `[Designing]` / absent, AND has no link to active open questions. This is the "candidate for promotion" status. |

### The `→ [[X]]` link convention

When an item has unresolved questions, the bullet description should be replaced with a pointer to where those questions live:

```
- **F12 — Item Name** [Questions] — → [[F12 — Item Name]]
```

The `→ [[Feature Doc]]` link is the marker. As long as the linked doc has pending questions in its `## Open Questions` block, the backlog item's status is **Questions**. When the user resolves those questions, the item can be re-readied (the description gets rewritten to reflect the resolved design, and the bullet moves to `## Ready`).

## Design Principle — Minimize User Back-and-Forth

Workflow operations that touch the backlog — `/groom`, `/triage`, `/roster`, audits, and similar batch operations — **must process the entire batch autonomously before involving the user**. Never interrupt mid-run to ask a question; route every question that emerges to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end of the run as the user's single next action.

Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N. Inline questions are an anti-pattern in batch operations.

(One concession: a single, genuinely trivial question may be deferred to the very end of a `/groom` run and asked after the roster prints, where it stays pinned to the bottom of the screen. Never more than one such inline question per run.)

## Location

`{NAME} Backlog.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan (uses `R<n>.<m>` numbering for hierarchical milestone references; planned but deferred)
- **Backlog** — active deferred-work list: ideas under consideration, low-priority but not abandoned
- **[[CAB Icebox|Icebox]]** — optional cold-storage list for items not under active consideration

Items graduate from Backlog to Todo or Roadmap when they become priorities, or move to Icebox when they cool off.
