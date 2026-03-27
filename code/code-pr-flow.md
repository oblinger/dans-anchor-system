# PR Flow

Iterative PR-based development workflow. The pilot works on a feature branch, PRs batched work for user review, and iterates until the feature is complete. Adapted from the CAB PR Flow pattern.

## When to Use

When the user wants incremental, reviewed delivery of milestones. Invoke with "PR flow" to start or continue the cycle.

## Workflow

### Branch Structure

```
main
 +-- feature/{name}-base
      +-- feature/{name}-work   <- all work happens here
```

### Cycle

1. **User says "PR flow"** — pilot finds next incomplete roadmap item
2. **Pilot works** on `-work` branch, batching until ~300 lines changed (or custom size: "PR flow 500")
3. **PR and surf** — pilot PRs `-work` into `-base`, merges, surfs the Files tab, then STOPS
4. **User reviews** — provides feedback or says "done" / "PR flow"
5. **Iterate** — if fixes needed, go back to step 2
6. **Complete** — pilot PRs `-base` into `main`, user squash-merges

### Key Rules

- **Always stop after surfing a PR** — never continue without user feedback
- **Batch small milestones** — if a milestone is under the line target, continue to the next
- **PR naming**: `-work` into `-base`: "Work on M3.1: description" (incremental). `-base` into `main`: "M3.1: Description" (clean final).

### Bulk Variant

"PR flow bulk" — pilot owns the full cycle with ~4 parallel agents. No user review per PR. Batches by parent milestone. See [[CAB-pr-flow]] for the full spec.

### Git Protocol

Commit after each well-defined piece of activity. Before pausing for any reason:
1. Commit any uncommitted work
2. Push all local commits
3. Merge ready PRs
4. Verify `git status` is clean
