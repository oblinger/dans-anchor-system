# Spec

Write an implementation spec for a roadmap milestone. The spec provides enough detail that a worker (or the pilot in solo mode) can implement without design ambiguity.

## When to Use

Before implementing a roadmap milestone. Run to produce the spec that drives `/code code`. In the execution loop, this is the "Spec Work" priority — keeping the worker pipeline full.

## Workflow

### 1. Select the Milestone

Pick the next roadmap item whose dependencies are met. If multiple items are ready, prefer the one that unblocks the most downstream work.

### 2. Read the Design

Load the relevant Module Docs, System Design sections, and any prior Discussion entries for context. Understand the interfaces, data flow, and constraints.

### 3. Write the Spec

Create a spec document (in the project's planning area or as a PR description) with:

- **Goal** — one sentence: what this milestone delivers
- **Files to create or modify** — list with expected changes
- **Interfaces** — function signatures, data structures, protocols the code must implement
- **Behavior** — what the code does, including edge cases and error handling
- **Test expectations** — what tests should verify, referencing the Test Design doc
- **Acceptance criteria** — concrete conditions that prove the milestone is done

### 4. Verify Spec Completeness

Could a worker implement this without coming back to ask questions? If not, add more detail or flag blocking questions.

### 5. Dispatch or Execute

- In **solo mode**: proceed directly to `/code code`
- In **worker mode**: dispatch the spec to a worker via worktree or PR flow
- In **parallel mode**: dispatch and immediately begin speccing the next milestone
