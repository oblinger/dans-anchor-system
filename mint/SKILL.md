---
name: mint
description: >
  Execute the agentic action — take what's ready and make it real.
  For code: read the feature/spec, write code, test, verify, commit.
  Use when the user says: "mint it", "mint the feature", "go ahead and build it",
  "implement this", "make it happen", "do it".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Mint

Take what's ready and make it real. Orchestrate the implementation phase — spec, code, test, review, verify, commit.

## Runbook

### 1. Assess

- Read the feature doc or spec that defines what to build
- Confirm the feature is in "Agreed" or "Ready" state — all questions answered, no decisions pending
- If not agreed, stop and tell the user: "This feature hasn't been agreed yet. Run `/feature` to complete the design."

### 2. Pipeline (per milestone)

| Step | Action | What it does |
|------|--------|-------------|
| 1 | Spec | Write implementation spec for the milestone (if not already written) |
| 2 | Code | Implement according to the spec |
| 3 | Test | Write and run tests |
| 4 | Review | Check code quality and spec compliance |
| 5 | Verify | Run full test suite, produce completion proof |
| 6 | Commit | Commit and push |

### 3. Modes

**Solo** — The pilot executes the full pipeline sequentially for each milestone. Simplest flow — one agent, one branch.

**Workers** — The pilot specs milestones and dispatches them to worker agents. The pilot's job becomes: spec upcoming milestones, review completed PRs, unblock workers, merge approved work.

**Parallel** — Multiple workers run simultaneously on independent milestones. The pilot manages the dispatch queue and resolves conflicts.

Default to solo mode unless the user specifies workers or parallel.

### 4. Execution Loop

Always work on the highest-priority item that has actionable work, then re-evaluate:

1. **Unblock Workers** — review PRs, merge, dispatch new workers on fully-specced items
2. **Legwork** — autonomous tasks: integrate user feedback, update roadmap, doc fixes
3. **Spec Work** — write specs for upcoming roadmap items whose dependencies are met
4. **Rescan** — check design consistency: docs vs code, intended vs actual

### 5. Git Protocol

Commit after each well-defined piece of activity. Before pausing:
1. Commit any uncommitted work
2. Push all local commits
3. Merge ready PRs
4. Verify `git status` is clean

### 6. Stat Updates

```bash
skl-stat update <S#> "Implementing" "Starting implementation"
skl-stat update <S#> "Testing" "Implementation complete, running tests"
skl-stat update <S#> "Done" "Feature complete and tested"
```

### 7. On Completion

On `/mint`: assess the roadmap, find the next milestone, and enter the pipeline.
