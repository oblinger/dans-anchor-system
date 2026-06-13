---
name: pr-flow
description: Iterative PR-based development with user review — Each PR is a feature unit reviewed before merge. Use when user says: "pr flow", "iterative development".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# PR Flow — Iterative PR-based development

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


## PR-mode integration (per [[F077]] Q4)

`/pr-flow` is the underlying mechanism for **PR mode** (the Git-aspect Trait per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] + [[PR]] trait spec). The relationship:

- **`/pr-flow` user-invoked** — the legacy use. User types "PR flow" / `/pr-flow`; the cycle above runs once. Composes with any Git-aspect mode the anchor declares (the explicit `/pr-flow` invocation temporarily overrides whatever mode is normally active, per [[DSC mode]] § Git Commit *"Inside `/pr-flow` → defer to PR-mode rules until /pr-flow exits"*).
- **`/pr-flow` auto-deferred-to from PR-mode** — anchors that declare `PR` in their `.anchor` `traits:` list use `/pr-flow` semantics for *every* state-touching commit, not just on explicit invocation. The agent treats every commit boundary in such an anchor as a `/pr-flow` cycle:
  1. Branch named `F<n>-<slug>` (or `B<id>-<slug>` for B-rows).
  2. Commits to that branch.
  3. PR opened via `gh pr create`.
  4. **Hard pause** for user review.
- **Inversion vs Commit mode**: in Commit-mode anchors, the agent commits directly to the working branch (typically `main` / `master`); `/pr-flow` is opt-in per invocation. In PR-mode anchors, the agent NEVER commits to the working branch; `/pr-flow` is the default mechanism.

**When PR mode v1 fully ships** (the per-anchor `traits:` walk-up + override logic per [[F077]] § 5), this section's behavior becomes the default for any anchor declaring `PR`. Until then (2026-06-01), PR mode behavior is invoked only via explicit `/pr-flow` calls.
