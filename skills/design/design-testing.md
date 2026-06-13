# Design Testing — Author the {NAME} Testing.md facet doc

Phase 5 of the canonical `/design` sequence (PRD → UX → API → Architecture → **Testing** → Roadmap). Authors `{NAME} Design/{NAME} Testing.md` per the [[FCT Testing]] facet — the project's **testing strategy + proposed-tests overview**. The doc has two parts that ship together: § Strategy (kinds, completeness targets, responsibilities, tier mapping) followed by § Proposed Tests (one row per proposed test, grouped by kind, linking to low-level specs in module docs).

**Renamed from `plan-testing` 2026-06-10 per [[F136 — Plan→Design skill rename]]. Authored shape updated 2026-06-10 to match [[FCT Testing]]** — the legacy `{NAME} Testing Strategy.md` 5-H2 strategy-only scaffold is superseded by the new `{NAME} Testing.md` two-part shape. Worked example: [[CAE Testing]].

**Critical scope distinction:** this sub-skill authors the *strategy + proposed-tests overview*, NOT test code. Test code authoring happens during Drive (`/code test` or per-feature in `/mint`); low-level test specs (preconditions, fixtures, assertions) live in module docs. This sub-skill produces the design-altitude doc that drives all three downstream surfaces.

Gate 2 of `/design` requires `status:: accepted` on BOTH `{NAME} Architecture.md` AND `{NAME} Testing.md` before roadmapping begins.

## When to Use

- User invoked `/design testing` directly.
- `/design` bare auto-dispatched here (canonical phase 5 — Architecture already at `status:: accepted`, Testing missing or incomplete).
- User said "let's design the testing strategy" / "testing discipline" / "design tests for X".

## File location

`{NAME} Design/{NAME} Testing.md` — sibling of Architecture, PRD, UX inside the Design folder. The strategy + proposed-tests overview is a design artifact.

Module-level test details belong in module docs under `{NAME} Dev Docs/` or `{NAME} Architecture/` (per the spec section the module ships under), NOT here. This file is the design-altitude inventory; module docs are the low-level specs.

## File shape

**Read [[FCT Testing]] before authoring.** The facet spec is the canonical recipe — required sections, dataview fields, the three-altitude split, the Spec-column convention. This sub-skill owns the *process*; the facet owns the *shape*. If anything below conflicts with the facet, the facet wins.

Worked example to crib from: [[CAE Testing]].
Audit rules to honor: [[FCT Testing#RULESET R-testing|R-testing]] (9 rules).

## Runbook

### 1. Detect anchor + existing file

- Walk up from `cwd` to nearest `.anchor`. Assume `{NAME} Design/` exists (the gate per [[FCT Design]]; `/design` orchestrator handles scaffolding before dispatch to this sub-skill).
- Check whether `{NAME} Design/{NAME} Testing.md` exists.
- **Legacy detection:** if `{NAME} Design/{NAME} Testing Strategy.md` exists instead (legacy plan-testing scaffold), surface it: *"Found legacy `{NAME} Testing Strategy.md` — migrating to `{NAME} Testing.md` per [[FCT Testing]]."* Read it as input for § 3.

### 2. Branch on file existence

**If `{NAME} Testing.md` does NOT exist** — proceed to § 3 (initial-draft proposal).

**If file exists** — open it; walk the user through completing any thin / missing H2 sections. Run [[FCT Testing#RULESET R-testing|R-testing]] rules against it and fix violations. Skip § 3.

### 3. Initial-draft proposal (hybrid heuristic)

When no `{NAME} Testing.md` exists yet, draft both halves by combining three signal sources:

1. **Read `{NAME} PRD.md`.** Extract user stories. For each story, propose an e2e row in § Proposed Tests § End-to-end.
2. **Read `{NAME} Architecture.md`.** Extract subsystems and integration boundaries. For each boundary, propose an integration-test row in § Proposed Tests § Integration. Identify load-bearing pure-logic units (queue invariants, retry schedules, parsing). Propose property-based-test rows when the invariant is universally-quantifiable.
3. **Apply default template for code-shaped projects.** When the anchor produces code, baseline includes unit tests for all public surfaces of every subsystem (one row per `<subsystem>` × <golden-path test>), a CI pipeline, and standard tooling for the project's language. Use the canonical file shape above as the scaffold. (For non-code-shaped designed anchors, adapt the kinds to match the artifact — e.g., review-rubrics for written content, smoke checks for methodology.)

Compose the three signals into a draft `{NAME} Testing.md`. Set `status:: drafting` in the frontmatter. Use deliberate `[bare brackets]` for Spec columns where the destination module doc doesn't yet exist — these mark intentional roadmap.

Glance the file so the user can review and edit.

### 4. Walk sections with user

Open the file. For each section:

- **`## Overview`** — write the one-sentence testing-posture summary. ("Heavy unit + integration, modest e2e" / etc.)
- **`## Strategy § Test Kinds`** — confirm the category list. Add/remove based on project shape.
- **`## Strategy § Completeness Targets`** — set the bar per kind. Enforce the kind-target one-to-one symmetry (every declared kind has a target).
- **`## Strategy § Responsibilities`** — name who authors each kind.
- **`## Strategy § Tier Mapping`** — connect to [[DSC verification]]'s four tiers; which kinds satisfy which tier.
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
- **Don't ask "should we test this?"** — designed-lifecycle default says yes, test it. Use Lean recommendations per F068 for granular decisions.
- **Don't declare a kind in Strategy without proposing tests of that kind.** (R-testing-04, R-testing-05.)
- **Don't gate by separate ceremony.** `status:: accepted` on this file IS the gate. No separate registry, no Verify row, no parallel state.

## Related

- Facet spec: [[FCT Testing]]
- Worked example: [[CAE Testing]]
- Embedded rule set: [[FCT Testing#RULESET R-testing|R-testing]] (9 rules)
- Parent orchestrator: [[design]]
- Sibling sub-skills: [[design-prd]], [[design-ux]], [[design-architect]], [[design-roadmap]]
- Verification discipline: [[DSC verification]]
- Drive-phase test execution: `code-test` (in [[code]] cluster)
- F120 (parent feature) + F122 (this sub-skill's commission) + F136 (rename + shape update)
