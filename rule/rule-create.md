# Create — Design Project Rules

Collaboratively design rules for a project. This is a heavy user-in-the-loop process — propose, don't dictate.

## When to Use

When starting rule management for a project, or when expanding an existing rules file with new categories.

## Workflow

### 1. Read the Codebase Structure

Survey the project's key modules, languages, architecture patterns, and existing conventions. Look for:
- Module boundaries and how they communicate
- Threading or concurrency model
- State management approach
- Error handling patterns
- Naming conventions already in use

### 2. Propose Rule Categories

Based on what's observed, suggest categories. Common ones include:
- **Threading** — main thread serialization, lock avoidance, async coordination
- **State ownership** — who owns what, mutation boundaries
- **Component boundaries** — module encapsulation, no internal access
- **Data flow** — event stream purity, listener behavior, transforms
- **Error handling** — no silent fallbacks, explicit failure
- **Naming** — conventions for files, functions, types, constants
- **Architecture** — sensor/effector separation, layer discipline

Present the proposed categories to the user for approval before writing any rules.

### 3. Draft Rules per Category

For each approved category, suggest specific rules based on observed patterns:
- Event-driven systems — event stream purity, listener behavior, state ownership
- Multi-threaded — main thread serialization, lock avoidance, async coordination
- Sensor/effector architectures — logic-free sensors, dumb effectors
- API boundaries — module encapsulation, no internal access
- General — no silent fallbacks, no legacy alongside replacement, naming conventions

Frame each rule as a declarative constraint with a clear `RULE:` statement.

### 4. Discuss Each Rule

Walk through each proposed rule with the user:
- Get approval, refinement, or rejection
- Adjust wording to match the project's vocabulary
- Architectural rules are design decisions — frame them as such
- Start small (5–10 rules) rather than trying to be comprehensive upfront

### 5. Write the Rules File

Write the rules file in the project's Plan docs using the standard format:
- H2 sections for categories
- H3 headings for individual rules, each followed by a `RULE:` declaration line
- H4 Exceptions sections (initially empty) under rules that need them
- Reference [[DMUX Rules]] as the format example

### 6. Iterate Over Time

The rules file is a living document. After the initial pass:
- Start with the rules that matter most
- Expand as patterns emerge during development
- Add new categories when the architecture evolves
- Re-examine rules when the codebase changes significantly
