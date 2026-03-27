# Bugfix — Disciplined Bug Response

The standard flow for fixing a bug. Red-green discipline, clean commits, and contrarian verification.

**Not the same as spike.** Bugfix is the standard disciplined flow. If bugfix doesn't work after a reasonable effort, THEN escalate to `/code spike`.

## When to Use

- Tests were passing but something isn't working correctly
- User reports a bug
- You discover unexpected behavior during implementation

## Workflow

### 1. Checkpoint
Commit the current clean state before touching anything:
```bash
git add -A && git commit -m "checkpoint: before fixing {bug description}"
```

### 2. Confirm the Bug
Reproduce the issue. Describe in one sentence: "X happens when it should Y."

### 3. Write a Red Test (MANDATORY)
**Before diagnosing or fixing anything**, write a test that reproduces the bug.

- The test must FAIL (red) right now — if it passes, your test doesn't capture the bug
- Run the test, confirm it fails
- This test becomes the regression test

If you can't write a test that reproduces the bug, note this in Open Questions and discuss with the user.

### 4. Diagnose and Fix
- Read the code in the failure path
- Identify the root cause: "The bug is caused by X because Y"
- Apply the minimal fix — just the root cause, nothing more
- Do NOT fix adjacent issues, refactor, or improve code

### 5. Verify Green
- Run the red test — it must now PASS (green)
- Run the full test suite — nothing else broke
- If the test still fails, go back to step 4
- After 3 failed fix attempts, escalate to `/code spike` — or the user may escalate earlier by saying "spike it"

### 6. Revert and Reapply (clean commit)
Now that you know the fix works, make it clean:

```bash
git checkout .    # revert to checkpoint
```

- Apply ONLY the fix and the new test — nothing else
- No leftover logging, no experimental changes, no adjacent improvements
- The diff should be small and obvious: "here's the test, here's the fix"

### 7. Verify Again (clean base)
- Run the red test on the clean base — must PASS
- Run the full test suite — nothing broke
- If it fails on clean base but worked before, you missed a dependency in the fix

### 8. Verify the Original Bug is Gone (MANDATORY)

**Assume the bug is NOT fixed until you prove otherwise.**

- Go back to the exact scenario that exposed the bug
- Re-run that scenario, observe the result
- Confirm the original symptom is gone — not just that your test passes, but that the actual thing that was broken is now working
- If the original bug is still present despite your test passing, your test doesn't capture the real bug — go back to step 3

### 9. Commit (clean)
```bash
git add -A && git commit -m "fix: {what was broken and why}"
```

Clean history: checkpoint → fix. No debugging mess.

### 10. Document
- If the bug was subtle, add a comment explaining why the fix is correct
- Add the bug to [[DEV Lessons]] if it reveals a pattern worth remembering

## Why This Flow

- **Red test first** — proves the bug is real and the fix actually addresses it
- **Checkpoint + revert** — keeps the commit history clean, no debugging artifacts
- **Contrarian verification** — assume it's NOT fixed, prove it IS
- **Minimal fix** — one change, one purpose, easy to review and revert if needed
