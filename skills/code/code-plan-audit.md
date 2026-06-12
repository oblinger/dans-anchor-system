# Plan Audit

Completeness check on the planning phase. Verifies that the PRD, UX Design, and System conversation have produced a coherent, sufficient foundation before moving to architecture.

## When to Use

After completing PRD, UX, and System conversation. Run as the final gate before `/code architect`.

## Workflow

### 1. Document Existence Check

Verify these files exist and are non-empty:
- `{NAME} PRD.md`
- `{NAME} UX Design.md`
- `{NAME} Open Questions.md`

### 2. Trace User Stories

For every user story in the PRD:
- Does the UX Design show how the user accomplishes it?
- Has the system conversation addressed the technical approach?

Report any story that lacks UX or technical coverage.

### 3. Terminology Consistency

Scan all three sources for the same concept described with different words. Flag terminology drift.

### 4. Contradiction Check

Look for promises in one document that conflict with constraints or decisions in another. Report conflicts.

### 5. Open Questions Status

Review `{NAME} Open Questions.md`:
- Are all Urgent questions resolved?
- Are Soon questions acceptable to defer?
- Is anything blocking the architecture phase?

### 6. Report

Produce a short pass/fail summary. If issues are found, list them with the affected documents. The user decides whether to fix before proceeding.
