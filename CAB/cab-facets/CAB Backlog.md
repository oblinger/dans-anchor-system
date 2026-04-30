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


## In Progress
- **B3 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries

## Ready
- **B1 — Cron syntax** — Support cron expressions for recurring task schedules

## Upcoming
- **B2 — Task groups** — Allow grouping related tasks that run as a batch
- **B4 — Priority levels** — Add high/medium/low priority beyond just deadline ordering

## Testing
- **B7 — Webhook notifications** — Send webhook on task completion (implemented, awaiting user verification)

## Completed
- **B5 — Retry config** — Per-task retry limits (done in PR #4, see [[CAE Roadmap#M2]])
- **B6 — JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **B9 — User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **B8 — Doc consistency pass** — Module docs reference old API names from pre-M2
- **B10 — Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

---



# Format Specification

## Format

Each entry is a named-list item with a unique **B-number** prefix:

```
- **B<n> — Item Name** — short description.
```

The B-number lets the user refer unambiguously to a single item ("do B5", "B12 needs more detail"). B-numbers are unique within the file but **don't have to be strictly increasing in display order** — items are added and resolved in arbitrary order. When assigning a new B-number:

- Prefer the **lowest unused integer** in the file (gap-fill).
- If active items cluster at high numbers (e.g., most are B40+), just keep counting upward — don't force gap-fill into a stale cluster.
- Once the high cluster clears, future adds restart at the lowest available low number.

Skipped numbers are fine. Don't renumber existing items just to compact — B-numbers are stable references.

Entries are grouped under H2 sections:
- **In Progress** — Items the Pilot is actively driving forward right now. Used for backlog-tracked work that doesn't warrant its own feature doc; items with full feature docs track in-flight state on the feature doc instead.
- **Ready** — Items whose status is **Ready** (see § Definition of Ready below).
- **Upcoming** — Ideas and deferred work not yet scheduled.
- **Testing** — Implemented but awaiting user verification that they work as intended. Once confirmed, move to Completed.
- **Completed** — Items that graduated and were finished (with cross-references to where).
- **Legwork** — Autonomous agent work that should be done proactively. Includes user feedback integration, planning actions, doc consistency fixes, and other tasks the agent can execute without user approval. The `/code execute` priority loop pulls from this section as Tier 2 legwork (after PR merging and worker dispatch).

Items typically flow `Upcoming → Ready → In Progress → Testing → Completed`. The `roster` skill (`show roster`) renders In Progress / Ready / Backlog (everything else except Testing & Completed) as a state-of-the-work summary plus an Icebox count. The `ready` skill (`make ready`) walks the backlog and tries to promote candidates from Upcoming to Ready (see § Definition of Ready and § Item Status below).

For items that are explicitly parked / out-of-scope-for-now / someday-maybe, use the optional [[CAB Icebox]] file rather than a Deferred section here.

## Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

Sharper than "design questions resolved." If the task still hides any "wait, what about X?" that the user would have to answer, it's **not** Ready — it's blocked on questions, and the work belongs in a feature doc until those questions resolve.

This is the bar `/ready` checks for each candidate.

The canonical home for this definition (and the full state graph it sits within) is the **`workflow` discipline** — see `[[workflow]]`. CAB Backlog cites it from here so this spec stays self-contained for backlog-format readers, but the workflow discipline is the single source of truth across surfaces (backlog, roadmap, feature lifecycle, PRD).

## Item Status

Every backlog item has one of these statuses, derived from where the bullet sits and what (if anything) it links to:

| Status | How to recognize |
| --- | --- |
| **Ready** | Bullet is under `## Ready`. |
| **In Progress** | Bullet is under `## In Progress`. |
| **Blocked on questions** | Bullet text contains a `→ [[Feature Doc]]` or `→ [[Open Questions]]` link to a doc with active pending questions. The item is parked there until the user answers. |
| **Testing** | Bullet is under `## Testing`. |
| **Completed** | Bullet is under `## Completed`. |
| **Unset / Upcoming** | Bullet is under `## Upcoming`, `## Legwork`, or any other non-terminal section, AND has no link to active open questions. This is the "candidate for promotion" status. |

### The `→ [[X]]` link convention

When an item has unresolved questions, the bullet description should be replaced with a pointer to where those questions live:

```
- **B12 — Item Name** — → [[2026-04-29 Item Name]]
```

The `→ [[Feature Doc]]` (or `→ [[Open Questions]]`) link is the marker. As long as the linked doc has pending questions in its `## Open Questions` block, the backlog item's status is **Blocked on questions**. When the user resolves those questions, the item can be re-readied (the description gets rewritten to reflect the resolved design, and the bullet moves to `## Ready`).

## Design Principle — Minimize User Back-and-Forth

Workflow operations that touch the backlog — `/ready`, `/roster`, audits, and similar batch operations — **must process the entire batch autonomously before involving the user**. Never interrupt mid-run to ask a question; route every question that emerges to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end of the run as the user's single next action.

Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N. Inline questions are an anti-pattern in batch operations.

(One concession: a single, genuinely trivial question may be deferred to the very end of a `/ready` run and asked after the roster prints, where it stays pinned to the bottom of the screen. Never more than one such inline question per run.)

## Location

`{NAME} Backlog.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan
- **Backlog** — active deferred-work list: ideas under consideration, low-priority but not abandoned
- **[[CAB Icebox|Icebox]]** — optional cold-storage list for items not under active consideration

Items graduate from Backlog to Todo or Roadmap when they become priorities, or move to Icebox when they cool off.
