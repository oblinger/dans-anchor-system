# Workers

Dispatch and manage worker agents for parallel implementation. Workers are dispatched on fully-specced roadmap items and return completed code via PRs.

## When to Use

When the pilot has specced milestones ready for implementation and wants to parallelize by dispatching to worker agents.

## Workflow

### Dispatching Workers

Workers are dispatched only on items with clear implementation details — module interfaces, key data structures, test expectations — enough that a worker can execute without coming back to ask questions.

1. **Verify spec completeness** — re-read the spec. Could a worker implement this without blocking questions?
2. **Set up the workspace** — create a worktree or branch for the worker (see [[code-worktrees]])
3. **Dispatch** — provide the worker with: the spec, relevant module docs, test expectations, and the branch to work on
4. **Record** — note the dispatch in the roadmap (who is working on what)

### Unblocking Workers

The highest-value work because it refines system state — all subsequent work benefits from an up-to-date codebase.

1. **Review and merge PRs** — verify tests pass, check consistency with design, merge
2. **Update roadmap** — mark completed milestones
3. **Dispatch new workers** — only on items that are fully specced

### Execution Rules

- **Keep working while workers run** — dispatching a worker does not mean pause. Reassess the priority list for non-overlapping work.
- **Dispatch before pausing** — if about to pause and there is dispatchable work, dispatch first.
- **Only pause when genuinely nothing is actionable** — not merely because a worker is in flight.

### Context-Aware Pacing

- **Above 30% context remaining** — work normally
- **30%-15% remaining** — finish current thread, dispatch ready workers, document state
- **Below 15%** — stop, dispatch, document, pause
