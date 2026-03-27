# Delegate — Parallel Work Dispatch

Dispatch independent units of work to subagents, optionally in worktrees, with a structured merge-back pattern. Use this whenever the main agent has multiple independent tasks that can run concurrently.

## When to Use

- Fixing multiple rule exceptions across different modules
- Refactoring several files with non-overlapping changes
- Writing tests for multiple modules
- Any batch of work where items don't depend on each other's output

## Decision: Inline vs Delegate

Not everything needs delegation. Use this checklist:

| Condition | Action |
|-----------|--------|
| 1-2 items, same file | Do it inline, no delegation |
| 3+ items, different files | Delegate with subagents |
| Items touch shared code | Group into one subagent |
| Test suite is slow (>30s) | Use worktrees so each agent can test independently |
| Test suite is fast (<30s) | Subagents without worktrees; test sequentially at merge |

## Workflow

### 1. Plan the Work

List all work items. For each item, identify which files it touches.

### 2. Group by File Overlap

Build groups where no two groups touch the same file. Items that share files go in the same group. This prevents merge conflicts.

**Foundation-first ordering within groups:** If item B depends on item A's output (e.g., A creates a type that B uses), they must be in the same group with A before B. No forward dependencies.

Algorithm:
1. Build a file-touch map: item → set of files it modifies
2. Merge items with overlapping file sets into the same group
3. Within each group, order by dependency (foundations first)
4. Verify: no group depends on another group's output

### 3. Decide Worktrees vs Shared Working Tree

**Use worktrees when:**
- 3+ groups
- Test suite takes >30s
- Changes are large enough that you want independent test runs

**Use shared working tree when:**
- 2 groups
- Test suite is fast
- Changes are small and mechanical

### 4. Launch Subagents

For each group, launch a subagent with:

**In its prompt:**
- The full context it needs (rules file, relevant source, etc.)
- Its specific list of work items
- Clear instructions on what to do and what tests to run
- Whether to commit (worktree) or just stage changes (shared)

**Worktree mode:**
- Use `isolation: "worktree"` on the Agent tool
- Each subagent works on an isolated branch
- Each subagent commits its own work with a descriptive message
- Subagent runs tests in its own worktree

**Shared mode:**
- Subagents run in parallel for analysis/planning only
- Edits execute sequentially — one subagent at a time
- Main agent commits after each group's edits are verified

### 5. Review Pattern

The main agent reviews results, not subagents reviewing each other:
- **Subagents execute** — they make changes and run tests
- **Main agent reviews** — it checks each subagent's output inline, with full conversation context
- This separation ensures the reviewer sees the big picture across all groups

### 6. Record the Backlog Item

When using worktrees, the subagents return and their branches exist but aren't merged. Create a backlog entry with:

```markdown
### Merge delegation branches — [date]

Branches to merge:
- `worktree/rule-fix-companion` — fixes EX001, EX002, EX004 in CompanionEngine (tests passed)
- `worktree/rule-fix-textsender` — fixes EX027, EX030, EX031 in TextSender (tests passed)
- `worktree/rule-fix-glow` — fixes EX043, EX044 in GlowOverlay (tests passed)

Merge order: any (no cross-group dependencies)
After merge: rebase if needed, run full test suite, then `/rule sync`
```

### 7. Merge (when picked up from backlog)

For each branch:
1. Rebase onto current main (other work may have landed)
2. Resolve conflicts if any (should be rare given non-overlapping groups)
3. Run tests after rebase
4. Merge to main
5. Delete the worktree branch

After all branches merged:
- Run full test suite
- Run `/rule sync` if this was a rule fix delegation
- Remove the backlog item

## Anti-Patterns

- **Don't delegate trivial work** — if it's faster to just do it, do it
- **Don't create one subagent per item** — group by file overlap, not by item
- **Don't let subagents review each other** — the main agent reviews, because it has full context
- **Don't forget the backlog item** — unmerged worktree branches rot quickly
- **Don't let branches age more than a day or two** — rebase pain grows fast
