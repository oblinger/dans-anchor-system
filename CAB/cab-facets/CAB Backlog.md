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
- **Q3 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries

## Ready
- **Q1 — Cron syntax** — Support cron expressions for recurring task schedules

## Upcoming
- **Q2 — Task groups** — Allow grouping related tasks that run as a batch
- **Q4 — Priority levels** — Add high/medium/low priority beyond just deadline ordering

## Testing
- **Q7 — Webhook notifications** — Send webhook on task completion (implemented, awaiting user verification)

## Completed
- **Q5 — Retry config** — Per-task retry limits (done in PR #4, see [[CAE Roadmap#M2]])
- **Q6 — JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **Q9 — User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **Q8 — Doc consistency pass** — Module docs reference old API names from pre-M2
- **Q10 — Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

---



# Format Specification

## Format

Each entry is a named-list item with a unique **Q-number** prefix:

```
- **Q<n> — Item Name** — short description.
```

The Q-number lets the user refer unambiguously to a single item ("do Q5", "Q12 needs more detail"). Q-numbers are unique within the file but **don't have to be strictly increasing in display order** — items are added and resolved in arbitrary order. When assigning a new Q-number:

- Prefer the **lowest unused integer** in the file (gap-fill).
- If active items cluster at high numbers (e.g., most are Q40+), just keep counting upward — don't force gap-fill into a stale cluster.
- Once the high cluster clears, future adds restart at the lowest available low number.

Skipped numbers are fine. Don't renumber existing items just to compact — Q-numbers are stable references.

Entries are grouped under H2 sections:
- **In Progress** — Items the Pilot is actively driving forward right now. Used for backlog-tracked work that doesn't warrant its own feature doc; items with full feature docs track in-flight state on the feature doc instead.
- **Ready** — Items whose design questions are all resolved and that can be started immediately. Same idea as `/feature`'s **Agreed** gate, applied to lighter-weight backlog items.
- **Upcoming** — Ideas and deferred work not yet scheduled
- **Testing** — Implemented but awaiting user verification that they work as intended. Once confirmed, move to Completed.
- **Completed** — Items that graduated and were finished (with cross-references to where)
- **Legwork** — Autonomous agent work that should be done proactively. Includes user feedback integration, planning actions, doc consistency fixes, and other tasks the agent can execute without user approval. The `/code execute` priority loop pulls from this section as Tier 2 legwork (after PR merging and worker dispatch).

Items typically flow `Upcoming → Ready → In Progress → Testing → Completed`. The `roster` skill (`show roster`) renders In Progress / Ready / Backlog (everything else except Testing & Completed) as a state-of-the-work summary plus an Icebox count.

For items that are explicitly parked / out-of-scope-for-now / someday-maybe, use the optional [[CAB Icebox]] file rather than a Deferred section here.

## Location

`{NAME} Backlog.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan
- **Backlog** — active deferred-work list: ideas under consideration, low-priority but not abandoned
- **[[CAB Icebox|Icebox]]** — optional cold-storage list for items not under active consideration

Items graduate from Backlog to Todo or Roadmap when they become priorities, or move to Icebox when they cool off.
