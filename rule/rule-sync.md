# Sync — Reconcile Rules File with Code

Bookkeeping pass to keep the rules file in sync with the actual state of the codebase. No judgment calls — just sync state.

## When to Use

After fixes land, after refactors, or periodically to keep the rules file accurate.

## Workflow

### 1. Load the Rules File

Read the project's rules file. Catalog every exception in every table (both Exceptions and Fixed tables): EX number, grade, location, description.

### 2. Check Existing Exceptions Against Code

For each exception in the active Exceptions tables:
- Grep the codebase for `// EX0xx` (using the specific number)
- If the tag says `// EX0xx (fixed)`: move the exception from the Exceptions table to the Fixed table under the same rule
- If the tag is **gone entirely** (code was deleted or refactored): move to Fixed table if the fix is confirmed, otherwise flag for re-triage
- If the code around the tag **changed significantly**: flag for re-triage rather than removing

### 3. Move Fixed Exceptions

When moving an exception to the Fixed table:

**In the Exceptions table:** Remove the row.

**In the Fixed table** (create if it doesn't exist as an H4 `#### Fixed` section after the Exceptions table):

```markdown
#### Fixed

| EX | Grade | Location | Description |
|-----|-------|----------|-------------|
| EX004<br>(fixed) | D | CompanionEngine<br>.restart() | Was: 0.3s delay before restart. Now: completion callback on teardown |
```

- Keep the original grade for historical record
- Add `(fixed)` on a second line under the EX number
- Replace the five-part description with a short one-liner: "Was: X. Now: Y"

### 4. Check Code for New Exception Tags

Grep the entire codebase for `// EX` patterns. For any tag found in code that is not in the rules file:
- Add it to the appropriate rule's exception table
- Mark it as needing triage (no grade yet)

### 5. Update Summary Counts

If the rules file has an exception count summary, update it to reflect the current state (active exceptions and fixed count).

### 6. Update Now

If there are rule-fix entries in the project's Now file that have been fully resolved (approved, merged, synced), clear them from Now as described in the `/now` skill — remove from queue table, prepend to `now-history.md` (same folder as the Now file).

### 7. Preserve Numbering

Do not renumber exceptions or rules. Gaps in the EX and R sequences are fine — they avoid confusing source code comments and cross-references. Even when exceptions are moved to the Fixed table, their numbers are retired, not reused.
