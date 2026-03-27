# Test Plan

Create the test design document for the project. This is the planning side of testing — deciding what to test, what scaffolds are needed, and how tests are organized. Actual test implementation happens in `/code test`.

## When to Use

During the architecture phase, after System Design and Module Docs exist. Run to establish the test strategy before implementation begins.

## Workflow

### 1. Review Architecture

Read the System Design and Module Docs to understand the components, interfaces, and data flows that need testing.

### 2. Create Test Design Document

Create or open `{NAME} Docs/{NAME} Dev/{NAME} Test Design.md`:

```markdown
# {NAME} Test Design

## Open Questions

## Test Design

| SCAFFOLDS            | Description                                    |
| -------------------- | ---------------------------------------------- |
| [[#KitchenSink]]     | Full system with realistic data                |

| TEST AREAS                    | Category | Level | Description                    |
| ----------------------------- | -------- | ----- | ------------------------------ |
```

### 3. Identify Test Areas

For each module and interface in the architecture:
- What is the critical path that must always work?
- What are the boundary conditions and error cases?
- What external dependencies need isolation or mocking?

Add each test area to the Test Design doc with its category (snap/pr/demand/witness) and level (1-9).

### 4. Plan Scaffolds

Design the kitchen sink scaffold first — one big realistic scaffold that all tests run against. Plan focused scaffolds only for: clean/empty state, debugging isolation, performance testing.

### 5. Define Test Organization

Specify where test files live, what framework is used, and how categories map to test runners. Follow the conventions in [[code-test]] for the project's language.

### 6. Link from Architecture

Reference the Test Design doc from the Files doc and ensure it is reachable from the dispatch tree.
