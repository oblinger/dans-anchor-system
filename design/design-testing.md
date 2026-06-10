# Design Testing — Author the {NAME} Testing.md facet doc

Phase 5 of the canonical `/design` sequence (PRD → UX → API → Architecture → **Testing** → Roadmap). Authors `{NAME} Design/{NAME} Testing.md` per the [[CAB Testing]] facet — the project's **testing strategy + proposed-tests overview**. The doc has two parts that ship together: § Strategy (kinds, completeness targets, responsibilities, tier mapping) followed by § Proposed Tests (one row per proposed test, grouped by kind, linking to low-level specs in module docs).

**Renamed from `plan-testing` 2026-06-10 per [[F136 — Plan→Design skill rename]]. Authored shape updated 2026-06-10 to match [[CAB Testing]]** — the legacy `{NAME} Testing Strategy.md` 5-H2 strategy-only scaffold is superseded by the new `{NAME} Testing.md` two-part shape. Worked example: [[CAE Testing]].

**Critical scope distinction:** this sub-skill authors the *strategy + proposed-tests overview*, NOT test code. Test code authoring happens during Drive (`/code test` or per-feature in `/mint`); low-level test specs (preconditions, fixtures, assertions) live in module docs. This sub-skill produces the design-altitude doc that drives all three downstream surfaces.

Gate 2 of `/design` requires `status:: accepted` on BOTH `{NAME} Architecture.md` AND `{NAME} Testing.md` before roadmapping begins.

## When to Use

- User invoked `/design testing` directly.
- `/design` bare auto-dispatched here (canonical phase 5 — Architecture already at `status:: accepted`, Testing missing or incomplete).
- User said "let's design the testing strategy" / "testing discipline" / "design tests for X".

## File location

`{NAME} Design/{NAME} Testing.md` — sibling of Architecture, PRD, UX inside the Design folder. The strategy + proposed-tests overview is a design artifact.

Module-level test details belong in module docs under `{NAME} Dev Docs/` or `{NAME} Architecture/` (per the spec section the module ships under), NOT here. This file is the design-altitude inventory; module docs are the low-level specs.

## File shape (per CAB Testing facet)

```markdown
---
description: {NAME} Testing — strategy + proposed-tests overview.
status:: drafting
---

# {NAME} Testing

## Overview

One paragraph — the testing posture in a sentence. ("Heavy unit + integration, modest e2e because the surface is library-shaped" / "E2E-first because UI flows are the value" / etc.) The reader leaves knowing the *shape* of the test investment.

## Strategy

### Test Kinds

- **Unit** — pure-function, in-process, no I/O.
- **Integration** — multiple components, real internal dependencies.
- **End-to-end** — full app exercising at least one user story.
- *(add others as needed: property-based, smoke, regression, performance, …)*

### Completeness Targets

- **Unit:** all public functions in `src/` have at least one test.
- **Integration:** every subsystem boundary per Architecture has at least one integration test.
- **End-to-end:** at least one per user story in PRD.
- *(target per kind declared in § Test Kinds — kind-target symmetry per R-testing-05)*

### Responsibilities

- **Unit tests** — agent on `/mint` for the feature that introduces the function.
- **Integration tests** — agent on `/mint` for boundary-touching features.
- **End-to-end tests** — author-curated; agent assists by drafting.
- **CI** — runs all kinds on PR open and main push.

### Tier Mapping

Per [[verification]]:

- **Tier 1 (agent-immediate)** — satisfied by unit + integration tests that run in CI.
- **Tier 2 (agent-over-time)** — satisfied by soak / regression tests.
- **Tier 3 (user-passive)** — satisfied by end-to-end tests on user-visible flows.
- **Tier 4 (user-explicit)** — fallback only.

## Proposed Tests

### Unit

| Test                              | Exercises                                  | Spec                       |
| --------------------------------- | ------------------------------------------ | -------------------------- |
| `test_<thing>_<condition>`        | <one-line behavior>                        | [[<Module doc>]] § Tests   |

### Integration

| Test                              | Exercises                                  | Spec                       |
| --------------------------------- | ------------------------------------------ | -------------------------- |
| `test_<boundary>_<scenario>`      | <one-line boundary behavior>               | [[<Module doc>]] § Tests   |

### End-to-end

| Test                              | Exercises (User Story)                     | Spec                       |
| --------------------------------- | ------------------------------------------ | -------------------------- |
| `e2e_<flow>`                      | US-<n>: <user-story title>                 | [<E2E spec page>]          |
```

**Spec column convention:** `[[wiki-link]]` for proposed specs whose home doc exists; `[bare brackets]` for proposed-but-unwritten specs that don't yet have a destination. Never inline test code or precondition prose into the table — that's the altitude inversion the facet is designed to prevent. (See [[CAB Testing#RULESET R-testing|R-testing]] rules 6 and 7.)

## Runbook

### 1. Detect anchor + existing file

- Walk up from `cwd` to nearest `.anchor`. Read `traits:` — v1 supports `Code` trait.
- Check whether `{NAME} Design/{NAME} Testing.md` exists.
- **Legacy detection:** if `{NAME} Design/{NAME} Testing Strategy.md` exists instead (legacy plan-testing scaffold), surface it: *"Found legacy `{NAME} Testing Strategy.md` — migrating to `{NAME} Testing.md` per [[CAB Testing]]."* Read it as input for § 3.

### 2. Branch on file existence

**If `{NAME} Testing.md` does NOT exist** — proceed to § 3 (initial-draft proposal).

**If file exists** — open it; walk the user through completing any thin / missing H2 sections. Run [[CAB Testing#RULESET R-testing|R-testing]] rules against it and fix violations. Skip § 3.

### 3. Initial-draft proposal (hybrid heuristic)

When no `{NAME} Testing.md` exists yet, draft both halves by combining three signal sources:

1. **Read `{NAME} PRD.md`.** Extract user stories. For each story, propose an e2e row in § Proposed Tests § End-to-end.
2. **Read `{NAME} Architecture.md`.** Extract subsystems and integration boundaries. For each boundary, propose an integration-test row in § Proposed Tests § Integration. Identify load-bearing pure-logic units (queue invariants, retry schedules, parsing). Propose property-based-test rows when the invariant is universally-quantifiable.
3. **Apply Code-trait default template.** For Code anchors, baseline includes unit tests for all public surfaces of every subsystem (one row per `<subsystem>` × <golden-path test>), a CI pipeline, and standard tooling for the project's language. Use the canonical file shape above as the scaffold.

Compose the three signals into a draft `{NAME} Testing.md`. Set `status:: drafting` in the frontmatter. Use deliberate `[bare brackets]` for Spec columns where the destination module doc doesn't yet exist — these mark intentional roadmap.

Glance the file so the user can review and edit.

### 4. Walk sections with user

Open the file. For each section:

- **`## Overview`** — write the one-sentence testing-posture summary. ("Heavy unit + integration, modest e2e" / etc.)
- **`## Strategy § Test Kinds`** — confirm the category list. Add/remove based on project shape.
- **`## Strategy § Completeness Targets`** — set the bar per kind. Enforce the kind-target one-to-one symmetry (every declared kind has a target).
- **`## Strategy § Responsibilities`** — name who authors each kind.
- **`## Strategy § Tier Mapping`** — connect to [[verification]]'s four tiers; which kinds satisfy which tier.
- **`## Proposed Tests`** — one H3 sub-section per kind matching § Test Kinds. Each H3 has a markdown table with Test / Exercises / Spec columns. Bare-bracket Specs are fine; they're roadmap.

### 5. Acceptance

Acceptance is signaled by `status:: accepted` in the file's frontmatter. The user can:

- **Say "the testing is accepted"** / *"testing looks good"* / *"the testing strategy is accepted"* → agent updates the field.
- **Edit the field directly** to `status:: accepted`.
- **Run `/design gate testing`** → shortcut for the same field update.

After updating, glance the file so the user verifies the field landed.

### 6. Hand off to next phase

Once `status:: accepted` is set on this file:

- If `{NAME} Architecture.md` also has `status:: accepted` → Gate 2 passes; bare `/design` will next auto-dispatch to `/design roadmap`.
- Otherwise → bare `/design` returns to Architecture phase to finish that gate.

The agent does NOT proactively invoke roadmapping; the user invokes `/design` again (or says "let's keep designing") to advance.

## Anti-patterns

- **Don't write actual test code here.** That's Drive (`/mint`, `/code test`). This file is the design-altitude inventory.
- **Don't inline low-level test specs into the Spec column.** Spec is a link or a bracket, never prose. (R-testing-07.)
- **Don't author the legacy `{NAME} Testing Strategy.md`.** The facet name is `{NAME} Testing.md`; the legacy 5-H2 strategy-only shape is superseded. (R-testing-01.)
- **Don't ask "should we test this?"** — Code-trait default says yes, test it. Use Lean recommendations per F068 for granular decisions.
- **Don't declare a kind in Strategy without proposing tests of that kind.** (R-testing-04, R-testing-05.)
- **Don't gate by separate ceremony.** `status:: accepted` on this file IS the gate. No separate registry, no Verify row, no parallel state.

## Related

- Facet spec: [[CAB Testing]]
- Worked example: [[CAE Testing]]
- Embedded rule set: [[CAB Testing#RULESET R-testing|R-testing]] (9 rules)
- Parent orchestrator: [[design]]
- Sibling sub-skills: [[design-prd]], [[design-ux]], [[design-architect]], [[design-roadmap]]
- Verification discipline: [[verification]]
- Drive-phase test execution: `code-test` (in [[code]] cluster)
- F120 (parent feature) + F122 (this sub-skill's commission) + F136 (rename + shape update)
