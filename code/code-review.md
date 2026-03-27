# Review

Review code for correctness, quality, and adherence to the spec. Catches issues before they merge.

## When to Use

After code is written and tests pass. Run before merging a PR or marking a milestone complete. Also invoked by `/code test review` for test-specific quality checks.

## Workflow

### 1. Load Context

Read the implementation spec and relevant module docs. Understand what the code should do.

### 2. Read the Diff

Review all changed files. For each change, check:

- **Correctness** — does it implement the spec accurately?
- **Completeness** — are all acceptance criteria addressed?
- **Edge cases** — are error paths and boundary conditions handled?
- **Style** — does it follow existing codebase conventions?

### 3. Anti-Pattern Check

Scan for common problems:

- **Testing mock behavior instead of real behavior** — tests that verify mock calls rather than actual outcomes
- **Test-only methods in production code** — methods that exist solely for testability
- **Assertions that always pass** — weak assertions like `is not None` that do not catch regressions
- **Incomplete mocks hiding assumptions** — mocks that only return success, hiding real failure modes
- **Dead code** — unreachable branches, unused imports, commented-out blocks
- **Duplicated logic** — same computation in multiple places instead of a shared function
- **Hardcoded values** — magic numbers or strings that should be constants or config
- **Missing error handling** — operations that can fail but have no error path
- **Overly broad catch** — catching all exceptions instead of specific ones

### 4. Architecture Compliance

Verify the code respects the system design:
- Module boundaries are not violated (no reaching into another module's internals)
- Data flows match the System Design doc
- New dependencies are justified and documented

### 5. Report

Produce a review summary:
- **Approve** — code is ready to merge
- **Request changes** — list specific issues with file and line references
- **Questions** — design ambiguities that need resolution before approval
