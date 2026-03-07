# cab-pr-flow — Iterative PR-Based Development

Efficient flow for user-reviewed incremental PRs. Claude works on a feature branch, PRs batched work for review, and iterates until the feature is complete.

For the full detailed procedure, read `CAB Skills/CAB PR Flow.md` in the CAB folder (`ha -p CAB`).

## Quick Summary

### Branch Structure
```
main
 └── feature/{name}-base
      └── feature/{name}-work   ← all work happens here
```

### Cycle
1. **User says "PR flow"** — Claude finds next incomplete roadmap item
2. **Claude works** on `-work` branch, batching until ~{SIZE} lines (default 300)
3. **PR & surf** — Claude PRs `-work` → `-base`, merges, surfs Files tab, **STOPS**
4. **User reviews** — provides feedback or says "done" / "PR flow"
5. **Iterate** — if fixes needed, go to step 2
6. **Complete** — Claude PRs `-base` → `main`, user squash-merges

### Key Rules
- **Always stop after surfing a PR** — never continue without user feedback
- **If waiting without a PR**, call `alert "Waiting for: <reason>"`
- **Batch small milestones** — if a milestone is < {SIZE} lines, continue to next
- **Custom size**: "PR flow 500" uses 500 lines as target

### PR Naming
- `-work` → `-base`: "Work on M3.1: description" (incremental review)
- `-base` → `main`: "M3.1: Description" (clean final title)

## Bulk Variant

"PR flow bulk" — Claude owns the full cycle with ~4 parallel agents. No user review per PR. Batches by parent milestone. Read the full spec in `CAB Skills/CAB PR Flow.md`.
