# CAB Backlog

The backlog file (`{NAME} Backlog.md`) holds ideas, low-priority tasks, and deferred work that don't belong on the active Todo or Roadmap yet. Items graduate to the Roadmap or Todo when they become priorities.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK Backlog


## Upcoming
- **Cron syntax** — Support cron expressions for recurring task schedules
- **Task groups** — Allow grouping related tasks that run as a batch
- **Priority levels** — Add high/medium/low priority beyond just deadline ordering

## Testing
- **Webhook notifications** — Send webhook on task completion (implemented, awaiting user verification)

## Completed
- **Retry config** — Per-task retry limits (done in PR #4, see [[TSK Roadmap#M2]])
- **JSON output** — Machine-readable task status output (done in PR #2)

## Legwork
- **User feedback on retry UX** — User mentioned retry errors are confusing; rework error messages
- **Doc consistency pass** — Module docs reference old API names from pre-M2
- **Test coverage for edge cases** — Add tests for empty task lists and concurrent scheduling

## Deferred
- **GUI dashboard** — Web interface for task monitoring (out of scope for CLI-first phase)
- **Multi-tenant support** — Not needed until enterprise tier

---



# Format Specification

## Format

Each entry is a named-list item: bold name, em-dash, description.

Entries are grouped under H2 sections:
- **Upcoming** — Ideas and deferred work not yet scheduled
- **Testing** — Implemented but awaiting user verification that they work as intended. Once confirmed, move to Completed.
- **Completed** — Items that graduated and were finished (with cross-references to where)
- **Legwork** — Autonomous agent work that should be done proactively. Includes user feedback integration, planning actions, doc consistency fixes, and other tasks the agent can execute without user approval. The `/code execute` priority loop pulls from this section as Tier 2 legwork (after PR merging and worker dispatch).
- **Deferred** — Items explicitly parked. Not forgotten, just not now.

## Location

`{NAME} Backlog.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Relationship to Other Planning Docs

- **Todo** — active, near-term tasks
- **Roadmap** — milestone-based execution plan
- **Backlog** — everything else: ideas, someday/maybe, deferred work

Items graduate from Backlog to Todo or Roadmap when they become priorities.
