# Execution Loop

Always work on the highest-priority item that has actionable work, then re-evaluate.
1. **Unblock Workers** — Review PRs, merge, dispatch new workers on fully-specced items
2. **Legwork** — Autonomous tasks: integrate user feedback, update roadmap, doc fixes, test coverage, backlog items from `{NAME} Backlog.md`
3. **Spec Work** — Write implementation specs for upcoming roadmap items whose dependencies are met, keeping the worker pipeline full
4. **Rescan** — Check design consistency: docs vs code, intended design vs actual behavior, stale content, open questions to surface to user


## Unblock Workers

The highest-value work because it refines system state — all subsequent work benefits from an up-to-date codebase.

1. **Review and merge PRs** — verify tests pass, check consistency with design, merge
2. **Update roadmap** — mark completed milestones
3. **Dispatch new workers** — only on items that are fully specced (no design ambiguity)

Workers are dispatched on items with clear implementation details — module interfaces, key data structures, test expectations — enough that a worker can execute without coming back to ask questions.


## Rescan

Periodically re-read documentation and code to verify internal consistency. Surface conflicts, gaps, or stale content as open questions. Present unresolved design decisions to the user.

Especially important after a batch of features lands. Will eventually have multiple levels of depth; for now, scan what seems most likely to have drifted.


## Execution Rules

- **Keep working while workers run** — dispatching a worker does not mean pause. Reassess the priority list for non-overlapping work.
- **Dispatch before pausing** — if about to pause and there is dispatchable work, dispatch first.
- **Only pause when genuinely nothing is actionable** — not merely because a worker is in flight.


## The `next` Command

When the user types **`next`**, **`'`** (single quote), **`crank`**, or **`end`**:

1. **Assess** — walk the priority loop, identify the highest-priority actionable activity
2. **Execute autonomously** — take that action, keep taking successive steps as long as there is clear forward progress
3. **Report on pause** — tell the user exactly one of:
   - A **question** that needs their answer, or
   - The **next actions** the pilot would take on the next `next`


## Context-Aware Pacing

- **Above 30% remaining** — work normally
- **30%-15% remaining** — finish current thread, dispatch ready workers, document state
- **Below 15%** — stop, dispatch, document, pause


## Git Protocol

Commit after each well-defined piece of activity. Before pausing for any reason:
1. Commit any uncommitted work
2. Push all local commits
3. Merge ready PRs
4. Verify `git status` is clean
