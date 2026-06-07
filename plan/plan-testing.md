# Plan Testing — Author the Testing Strategy

Phase 4 of the canonical `/plan` sequence (PRD → UX → API → Architecture → **Testing Strategy** → Roadmap). Authors `{NAME} Design/{NAME} Testing Strategy.md` — the project's **testing strategy**: categories of test, completeness target per category, and authoring responsibilities.

**Critical scope distinction:** this sub-skill authors the *regime*, NOT the tests themselves. Test authoring happens during Drive (`/code test` or per-feature in `/mint`). Plan-testing's product is parallel to plan-architect's product: the *plan* for testing, not the test code.

Gate 2 of `/plan` requires `status:: accepted` on BOTH `{NAME} Architecture.md` AND `{NAME} Testing Strategy.md` before roadmapping begins.

## When to Use

- User invoked `/plan testing` directly.
- `/plan` bare auto-dispatched here (canonical phase 4 — Architecture already at `status:: accepted`, Testing Strategy missing or incomplete).
- User said "let's plan the testing strategy" / "testing discipline".

## File location

`{NAME} Design/{NAME} Testing Strategy.md` — sibling of Architecture, PRD, UX inside the Design folder. The strategy is a design artifact.

Module-level test details belong in `Dev/` module docs, NOT here. This file is the high-level strategy.

## Regime file shape (5 H2 sections)

```markdown
---
description: {NAME} Testing Strategy — kinds of tests, completeness targets, responsibilities.
status:: drafting
---

# {NAME} Testing Strategy

## Test Kinds

The categories of test this project will use. Each is described in detail below; this section is the index.

- **Unit** — pure-function, in-process, no I/O.
- **Integration** — multiple components, real internal dependencies, mocked external ones.
- **End-to-end** — full app exercising at least one user story.
- *(others as needed: property-based, smoke, regression, performance, …)*

## Per-Kind Detail

### Unit
- **Covers:** ...
- **Lives at:** ...
- **Naming convention:** ...
- **Tooling:** ...

### Integration
- ...

## Completeness Targets

- **Unit:** all public functions in `src/` have at least one test.
- **Integration:** every subsystem boundary per Architecture has an integration test.
- **End-to-end:** at least one per user story in PRD.

## Responsibilities

- **Unit tests** — agent on `/mint` (the feature mint includes unit tests).
- **Integration tests** — agent on `/mint` for boundary-touching features.
- **End-to-end tests** — author-curated; agent assists.
- **CI** — runs all kinds on PR open and main push.

## Verification Tier Mapping

Per `[[verification]]`:

- **Tier 1 (agent-immediate)** — satisfied by unit + integration tests that run in CI.
- **Tier 2 (agent-over-time)** — satisfied by soak tests + regression tests.
- **Tier 3 (user-passive)** — satisfied by end-to-end tests covering the user-visible flow.
- **Tier 4 (user-explicit)** — fallback only.
```

The roster of 5 H2s is the canonical shape. Each is optional in any individual file but the shape is documented as the expected scaffold. Refine after seeing 2–3 real files.

## Runbook

### 1. Detect anchor + existing file

- Walk up from `cwd` to nearest `.anchor`. Read `traits:` — v1 supports `Code` trait.
- Check whether `{NAME} Design/{NAME} Testing Strategy.md` exists.

### 2. Branch on file existence

**If file does NOT exist** — proceed to § 3 (initial-regime proposal).

**If file exists** — open it; walk the user through completing any thin / missing H2 sections. Skip § 3.

### 3. Initial-regime proposal (hybrid heuristic)

When no `{NAME} Testing Strategy.md` exists yet, draft an initial regime by combining three signal sources:

1. **Read `{NAME} PRD.md`.** Extract user stories. For each story, propose an end-to-end test in § Completeness Targets.
2. **Read `{NAME} Architecture.md`.** Extract subsystems and integration boundaries. Propose integration tests in § Per-Kind Detail § Integration.
3. **Apply Code-trait default template.** For Code anchors, baseline includes unit tests for all public surfaces, a CI pipeline, and standard tooling for the project's language. Use the canonical 5-H2 shape from § Regime file shape above as the scaffold.

Compose the three into a draft `{NAME} Testing Strategy.md`. Write it. Set `status:: drafting` in the frontmatter. Glance the file so the user can review and edit.

### 4. Walk H2 sections with user

Open the file. For each H2:

- **`## Test Kinds`** — confirm the category list. Add/remove based on project shape (property-based testing for parsers; performance tests for hot-path code; etc.).
- **`## Per-Kind Detail`** — fill in for each category: what it covers, where tests live, naming convention, tooling.
- **`## Completeness Targets`** — set the bar. "All public functions" vs "every story has at least one e2e" vs "100% statement coverage" — be specific.
- **`## Responsibilities`** — name who authors each kind. Agent on /mint? Author-curated? CI?
- **`## Verification Tier Mapping`** — connect to `[[verification]]`'s four tiers; which kinds satisfy which tier.

### 5. Acceptance

Acceptance is signaled by `status:: accepted` in the file's frontmatter. The user can:

- **Say "the testing strategy is accepted"** in natural language → agent updates the field.
- **Edit the field directly** to `status:: accepted`.
- **Run `/plan gate testing`** → shortcut for the same field update.

After updating, glance the file so the user verifies the field landed.

### 6. Hand off to next phase

Once `status:: accepted` is set on this file:

- If `{NAME} Architecture.md` also has `status:: accepted` → Gate 2 passes; bare `/plan` will next auto-dispatch to `/plan roadmap`.
- Otherwise → bare `/plan` returns to Architecture phase to finish that gate.

The agent does NOT proactively invoke roadmapping; the user invokes `/plan` again (or says "let's keep planning") to advance.

## Anti-patterns

- **Don't write actual tests here.** That's Drive. This file is the regime that governs test authoring later.
- **Don't ask "should we test this?"** — Code-trait default says yes, test it. Use Lean recommendations per F068 for the granular decisions.
- **Don't gate by separate ceremony.** `status:: accepted` on this file IS the gate. No separate registry, no Verify row, no parallel state.
- **Don't conflate this with module-level test docs.** Those live in `Dev/`. This is the project-level strategy.

## Related

- Parent orchestrator: [[plan]]
- Sibling sub-skills: [[plan-prd]], [[plan-ux]], [[plan-architect]], [[plan-roadmap]]
- Verification discipline: [[verification]]
- Drive-phase test execution: `code-test` (in [[code]] cluster)
- F120 (parent feature) + F122 (this sub-skill's commission)
