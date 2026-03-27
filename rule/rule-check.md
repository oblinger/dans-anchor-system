# Check — Find and Grade Rule Violations

Scan source files for rule violations, grade them, write the five-part analysis, add them to the rules file, and post results to Now.

**MANDATORY: When done, call `stat add` with results, then add an H2 entry with the findings table to the Now file. The user watches the Now file — if you don't post, they won't know what happened.**

## When to Use

After code changes land, or periodically as a full audit (`--all` flag). Default scope is files changed since the last check.

## Workflow

### 1. Load the Rules

Find the project's rules file using `cab-config get rules`. Read all `RULE:` declarations to build the checklist. Read the rules file fresh each time — do not rely on memory.

### 2. Determine Scope

- If `--all` flag: scan all source files
- Otherwise: run `git diff <last-checked-commit>..HEAD --name-only` to get changed files
- The last-checked commit is stored in `.skl/rule/last-checked`
- If no checkpoint exists, treat as `--all`

### 3. Scan Each File

For each file in scope:
- Read the file
- Check each `RULE:` against the code
- Structural rules first (grep-able patterns): sleep/delay calls, fallback logic, magic numbers, wrong-layer access, direct internal access across module boundaries
- Semantic rules second (judgment calls): naming violations, architectural concerns, design pattern deviations
- For each potential violation, check if it has a `// EX0xx` comment
- If untagged, record: file, line number, which rule it may violate, and why

For large codebases, use subagents — one per file — each with the full rules list in their prompt.

When uncertain whether something is a violation, flag it as "possible" rather than ignoring it.

### 4. Grade and Analyze Each Violation

For each new violation found, write the full five-part exception description (see `/rule triage` format):

1. **Summary** — what the violation is
2. **Purpose:** — what the code is trying to accomplish
3. **Keep:** — why it might need to stay
4. **Alternative:** — concrete spec for what you'd do instead (or "None")
5. **Gain/Loss** or **Loss/Gain** — net assessment, order encodes the judgment

Assign a grade (A through F, with +/-). Add `// EX0xx` comment to the source code. Assign the next available EX number.

### 5. Update the Rules File

Add each new exception to the appropriate rule's exception table in the rules file. Use the R-numbered rule to find the right table.

### 6. Post to Now

Post results to Now using `stat`:

- If ≤5 rule categories with new exceptions: post a lightweight row (Notes column is enough)
- If >5 rule categories: post with an H2 entry containing a summary table

```bash
stat add "Rule check: found 7 new exceptions across R22, R23, R07"
```

Or if there are items needing review:

```bash
stat add --status "Review" --ref "[[DMUX Rules]]" "Rule check: 12 new exceptions need review"
```

### 7. Update Checkpoint

Store current HEAD commit as the new checkpoint in `.skl/rule/last-checked`.
