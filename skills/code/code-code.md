# Code

Implement code according to a spec. Follow the spec precisely, write clean code, and self-check before declaring done.

## When to Use

After a spec exists for the current milestone. This is the core implementation step.

## Workflow

### 1. Load the Spec

Read the implementation spec for the current milestone. Understand the goal, files to modify, interfaces, behavior, and acceptance criteria.

### 2. Implement

Write the code as specified:
- Follow existing code style and patterns in the codebase
- Implement interfaces exactly as specified in the module docs
- Handle edge cases and errors described in the spec
- Keep changes focused — do not refactor unrelated code

### 3. Self-Check

Before declaring done:
- Re-read the spec. Does the code match every requirement?
- Run the project's lint/format tools
- Run existing tests to ensure nothing broke
- Write new tests as specified in the test expectations
- Check that acceptance criteria are met

### 4. Update Docs

- Remove **(proposed)** from any module doc items that now match the code
- Update the Files doc if new files were created
- Mark the roadmap milestone as complete

### 5. Commit

Commit with a clear message referencing the milestone. If working in a PR flow, push to the work branch.
