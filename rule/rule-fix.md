# Fix — Execute Exception Fixes

Fix exceptions in the rules file using `/code bugfix` discipline. Scope the work by rule, module, grade, or specific EX number.

**MANDATORY: When done, call `stat add` with results, then add an H2 entry with the outcome table to the Now file. The user watches the Now file — if you don't post, they won't know what happened.**

## When to Use

After triage identifies exceptions worth fixing, or when the user asks to clean up a specific area.

## Scoping

The user specifies what to fix using natural language. Parse the request to determine the scope:

| User says | Means | Grades included |
|-----------|-------|-----------------|
| "fix EX004" or "fix exception 4" | Specific exception | Just that one |
| "fix the sensor rules" or "fix sensors and effectors" | By rule name | All exceptions under that rule |
| "fix CompanionEngine rules" or "fix companion rules" | By module | All exceptions in that module |
| "fix the D rules" or "fix D grade rules" | Bare letter grade | D+, D, D-, and F |
| "fix D- rules" | Specific sub-grade | D- and F only |
| "fix D+ rules" | Specific sub-grade | D+, D, D-, F |
| "make beneficial rule fixes" | Gain >= Loss line | C, C-, D+, D, D-, F |
| "fix the D rules in CompanionEngine" | Combined | Grade + module filter |
| "fix all timing hack rules" | By pattern | Exceptions matching a described pattern |

### Grade scale

Full scale from best to worst: A, B+, B, B-, C+, C, C-, D+, D, D-, F

**Bare letter** ("the D rules") → all +/- variants of that letter and worse.
**Letter with +/-** ("D- rules") → that specific sub-grade and worse.
**"Beneficial"** → C and below. C is the defined line where Gain first equals or exceeds Loss.

**Defaults:** If no grade is specified, the default is **beneficial** (C and below). If no rule is specified, the default is **all rules**. So `/rule fix` with no arguments means "fix all beneficial exceptions across all rules."

## Agent Authority

The coding agent executing fixes is the ultimate authority on how to fix each exception. The Alternative proposed during triage is a *suggestion*, not a mandate. The coding agent:

- **May reject** an exception fix if the Alternative is infeasible, unsafe, or would introduce worse problems
- **May question** an exception fix if it's unclear whether the tradeoff is worth it
- **May fix differently** than the Alternative proposes — it has the compiler, the tests, and the full codebase context that the triage agent lacked
- **Must document** its reasoning when it deviates from, rejects, or questions the proposed Alternative

## Workflow

### 1. Select and Confirm

Read the project's rules file. Apply the user's scope filters to build the list of exceptions to fix. Show the list to the user for confirmation before proceeding.

### 2. Decide Execution Strategy

Based on the number and distribution of exceptions, choose how to execute:

| Situation | Strategy |
|-----------|----------|
| 1-2 exceptions | Fix inline, no delegation |
| 3+ exceptions, non-overlapping files | Delegate via `/code delegate` with worktree subagents |
| 3+ exceptions, heavily overlapping | Delegate, but group overlapping items into one subagent |

When delegating, follow `/code delegate` for grouping, worktree decisions, and the backlog-for-merge pattern.

### 3. For Each Exception (or Group)

The **Alternative** line is the suggested fix. The **Gain** line is the acceptance criterion. But the coding agent decides.

**a. Assess the Alternative** — Is it feasible? Is there a better approach? Decide whether to follow it, modify it, or take a completely different approach.

**b. Apply `/code bugfix` discipline:**
- Checkpoint current state
- Write a red test derived from the **Gain** line — the gain is what the test should verify
- Watch for regressions described in the **Loss** line
- Implement the fix (using the Alternative, a modified version, or your own approach)
- Verify the test goes green
- Verify no regressions

**c. Record the outcome** — one of:
- **Applied** — fixed as proposed or with minor variations
- **Applied differently** — fixed, but using a different approach (document what and why)
- **Rejected** — not fixed, with reasoning (infeasible, worse tradeoff, etc.)
- **Question** — needs user input before proceeding

**d. Update source code:**
- Change `// EX0xx` to `// EX0xx (fixed)` in the source code
- Commit with a message referencing the EX numbers fixed

### 4. Write to Now

Write the results to the project's Now file (found via `cab-config get now`; see `stat` skill for full format spec). The agent's job is done after writing to Now — it does not wait for user approval.

**Determine the queue entry:**

| Situation | When | Action |
|-----------|------|--------|
| All applied, no rejections or questions | — | — (informational) |
| Has rejections or questions | ASAC | Approve |
| Has worktree branches pending merge | ASAC | Merge |

**Now entry format for rule fixes:**

Add a row to the queue table with a date+time block ID link, then add an H2 entry below.

Queue row example:

| Added | When | Action | Entry |
|-------|------|--------|-------|
| [03/20 08:17](#^03200817) | ASAC | Approve | Rule fix results — R22, R23 |

Entry example:

## 03/20 08:17	Rule fix results — R22, R23  ^03200817
**Request:** `/rule fix` D rules on R22, R23
(R22 — Sensors and Effectors Must Be Logic-Free, R23 — No Heuristics, No Fallbacks)
**Results:** 12 exceptions processed — 8 applied, 2 rejected, 1 applied differently, 1 question
**Branches pending merge:** `worktree/rule-fix-companion`, `worktree/rule-fix-textsender`

| EX    | Outcome           | Reason                                                                            |
| ----- | ----------------- | --------------------------------------------------------------------------------- |
| EX011 | Question          | Should indicatorThreshold be time-based instead of tick-based?                    |
| EX012 | Applied Different | Measured actual recovery times. HOW: Used adaptive cooldown instead of fixed 10s  |
| EX006 | Rejected          | No alternative to segment detection heuristic                                     |
| EX014 | Rejected          | AXDialog check is the only way to detect dictation health                         |
|       | APPLIED           | EX003, EX005, EX008, EX015, EX016, EX017, EX018, EX019                           |

**Table rules:**
- Questions, Applied Different, and Rejected get individual rows with EX number and reason
- All cleanly applied exceptions go in one row with no EX number and outcome APPLIED
- Put non-routine outcomes (Question, Applied Different, Rejected) first, APPLIED last

### 6. Update the Rules File

After the user approves (or immediately if no approval needed):

**Move fixed exceptions to a Fixed table** under the same rule section:

```markdown
#### Exceptions
| EX | Grade | Location | Description |
... (remaining active exceptions) ...

#### Fixed
| EX | Grade | Location | Description |
|-----|-------|----------|-------------|
| EX004<br>(fixed) | D | CompanionEngine<br>.restart() | Was: 0.3s delay before restart. Now: completion callback on teardown |
```

The Fixed table keeps the grade for historical record. The EX number gets `(fixed)` on a second line. Description is a short one-liner: what it was, what replaced it.

Run `/rule sync` to finalize.

### 7. Handle Failure

If a fix fails after 3 attempts:
- Do not keep thrashing — escalate to `/code spike`
- Document what was tried and why it failed
- Leave the EX tag in place unchanged
- Move on to the next exception in scope

## Subagent Prompt Design

When delegating to worktree subagents, each subagent's prompt should include:

1. The rules file (or the relevant rule section)
2. The list of EX numbers it's responsible for, with their full descriptions (Purpose, Keep, Alternative, Gain/Loss)
3. Instructions to use `/code bugfix` discipline for each fix
4. Instructions to run tests and commit in the worktree
5. Clear statement that the Alternative is a *suggestion* — the coding agent has authority to reject, question, or fix differently
6. Instructions to produce the summary report format shown above
