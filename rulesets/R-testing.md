# RULESET R-testing
include::
where:: `file:{anchor}/**/* Testing.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — added 2026-07-13, T014 follow-on.
description:: facet spec this doc instantiates

Embedded ruleset for the Testing facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Pulled in via the `R-facet` umbrella; active for an anchor through its traits ([[Warden Semantics]] § Rulesets).

### RULE R-testing-01 — File name is `{slug} Testing.md` (checked)
check:: testing_filename_correct

The facet doc is named `{slug} Testing.md` — not `{slug} Testing Strategy.md`, `{slug} Tests.md`, or any other variant. The doc covers strategy AND proposed tests; the name reflects the scope.

**Check pattern:** `ls "{anchor}/{slug} Design/{slug} Testing.md"` exists. No file named `{slug} Testing Strategy.md` exists alongside (would be the legacy design-testing scaffold; flag for migration).

**Why:** the older `design-testing` scaffold authored `Testing Strategy.md`; this facet supersedes that shape. The shorter name is canonical going forward.

### RULE R-testing-02 — `## Strategy` H2 present with required subsections (checked)
check:: strategy_subsections_present_ordered

The doc has a `## Strategy` H2 containing four H3 subsections in this order: `### Test Kinds`, `### Completeness Targets`, `### Responsibilities`, `### Tier Mapping`.

**Check pattern:** grep for the four H3 headers under `## Strategy`. All four required; ordering required.

**Why:** the four subsections are the load-bearing strategy components. A doc missing Tier Mapping (the most-often-skipped one) loses the connection to [[DAS verification]] and silently weakens what a passing suite proves.

### RULE R-testing-03 — `## Proposed Tests` H2 present, grouped by kind (checked)
check:: proposed_tests_structure

The doc has a `## Proposed Tests` H2 with H3 sub-sections, one per test kind. Each H3 contains a markdown table.

**Check pattern:** grep for `## Proposed Tests`; verify ≥ 1 H3 child; verify each H3 contains a markdown table.

**Why:** the proposed-tests overview is the half of the facet that connects strategy to ground. A strategy-only doc is the failure mode this facet is designed to prevent.

### RULE R-testing-04 — Every test kind in Proposed Tests is declared in Strategy (checked)
check:: proposed_tests_subset_of_strategy

The set of H3 sub-section names under `## Proposed Tests` is a subset of the kinds listed in `## Strategy § Test Kinds`. No kind appears in Proposed Tests that wasn't declared in Strategy.

**Check pattern:** parse the Test Kinds list and the Proposed Tests H3 names; assert subset.

**Why:** prevents the "tests-without-strategy" drift — proposed tests of a kind the strategy never sanctioned. Symmetric to the next rule.

### RULE R-testing-05 — Every declared test kind has a completeness target (checked)
check:: all_test_kinds_have_targets

For every kind appearing in `## Strategy § Test Kinds`, there is a bullet in `## Strategy § Completeness Targets` whose label matches the kind name.

**Check pattern:** parse both lists; assert one-to-one cover.

**Why:** declaring a kind without a target makes the strategy vague — readers can't tell "is this kind aspirational or load-bearing?" Every kind gets a target (even if the target is "no target — sampled" stated explicitly).

### RULE R-testing-06 — Proposed-tests rows link to a Spec (sampled)
check:: proposed_tests_rows_have_spec

Every row in every `## Proposed Tests` table has a non-empty Spec column. The value is either a `[[wiki-link]]` (spec exists) or `[bare bracket]` (spec proposed but not yet authored).

**Check pattern:** parse each table; assert no row has an empty Spec cell.

**Why:** the Spec column is what enforces the three-altitude split. An empty Spec is "test will exist somewhere, vibes" — the failure mode the proposed-tests overview is designed to prevent.

### RULE R-testing-07 — Low-level test specs are NOT inlined in the facet doc (sampled)
check:: spec_cells_format_valid

Spec column bodies are links or brackets, never inline test code, fixture definitions, or precondition prose. The facet doc carries inventory + provenance; the module doc carries the spec.

**Check pattern:** Spec column value matches the pattern `\[\[.+\]\]` (wiki-link) or `\[[^\]]+\]` (bare bracket). Any longer free-form prose in a Spec cell is a violation.

**Why:** facet doc altitude inversion is the failure mode — when the spec creeps into the inventory, the doc becomes the test file, both altitudes are lost, and the module doc decays.

### RULE R-testing-08 — `status::` field present in frontmatter (checked)
check:: status_field_valid

The top-of-file YAML frontmatter contains a `status::` dataview field with value `drafting`, `in-review`, or `accepted`.

**Check pattern:** parse YAML; assert `status::` key exists with one of the three values.

**Why:** the `status::` field is the gate signal for `/design roadmap` (formerly `/design roadmap`). Without it, Gate 2 has no input.

### RULE R-testing-09 — Tier Mapping cites the verification discipline (stated)

The `## Strategy § Tier Mapping` sub-section references `~~[[DAS verification]]~~` and maps at least three of the four tiers to test kinds.

**Check pattern:** grep for `~~[[DAS verification]]~~` link in the Tier Mapping body; count tier-1/-2/-3/-4 mentions.

**Why:** the vocabulary connection matters. A Tier Mapping that doesn't cite [[DAS verification]] is freelancing terms that won't match what the verification discipline expects.

### RULE R-testing-10 — TLDR present in preface zone (checked)

The doc carries a `**TLDR**` block in the preface zone (after the dispatch table, before the first body H2), formatted per [[DAS progressive-disclosure]] § TLDR formatting: 3-5 one-line bullets, each with a 2-3-word bolded descriptor. Topical content typically covers the posture (e.g., "heavy unit + integration") and the per-kind bar.

**Check pattern:** the file contains a line `^\*\*TLDR\*\*$` (or `^# TLDR$` style heading) preceding the first `## ` body heading; the immediately-following bullets follow the formatting spec.

**Why:** Testing docs reduce cleanly to a short posture statement that lets a reader graze in 5 seconds — "this project's testing is X-shaped, with bar Y." Requiring the TLDR makes the grazer-altitude unmissable and prevents the Overview paragraph from carrying the whole burden of high-altitude reading. Worked example: [[HBR Testing]] § preface zone.

### RULE R-testing-11 — `## Overview` H2 present, single-paragraph posture (checked)
check:: overview_section_present

The doc has a `## Overview` H2 between the preface zone and `## Strategy`, carrying a short prose statement (typically one paragraph) of the project's testing posture in plain English — the *shape* of the test investment, not the inventory.

**Check pattern:** grep for `^## Overview$` appearing before the first `^## Strategy$`. The section body is non-empty prose (not a table, not a bare bullet list).

**Why:** the Overview is the bridge between the grazer-altitude TLDR and the load-bearing Strategy. A reviewer answers "what is this project's testing posture in a sentence?" from here before drilling in. Skipping it forces the TLDR or the Strategy intro to carry that burden and the reader loses the one-paragraph framing every real instance (HBR, CAE, MUX) provides.

### RULE R-testing-12 — `## Tests` coverage table present below the preface (checked)
check:: tests_table_present

Directly after the preface (TLDR), before `## Overview`, the doc has a `## Tests` H2 containing a table with one row per test kind. Each row's first cell is a wiki-link — to a [[DAS Common Testing Types]] H2 for a vanilla kind, or to a section within this same doc for a project-special kind — and the table carries an "in system" (current count) column and an "expected coverage" column.

**Check pattern:** grep for `^## Tests$` appearing before the first `^## Overview$`; verify it contains a markdown table; verify the kind set equals `## Strategy § Test Kinds`; verify each kind cell is a `[[wiki-link]]`.

**Why:** the tests-table is the coverage map a reviewer reads first — current vs. expected per kind, each kind linked to its strategy (generic in [[DAS Common Testing Types]] or project-special in-doc). Without it the only coverage signal is buried in prose, and the link discipline (vanilla → shared catalogue, special → in-doc section) decays.

(R-testing-01..10 authored 2026-06-10; R-testing-11 added 2026-06-14 in the F178 Testing-facet pilot lane; R-testing-12 added 2026-06-26 — the required `## Tests` coverage table + [[DAS Common Testing Types]] linking. The sentinel form `### RULE R-<slug>-NN — <title> (tier)` is canonical; rule IDs are monotonic-forever and never renumbered.)

## Adoption

Adopted transitively via [[R-facet]] — `include:: [[R-facet]]` in an anchor's `{slug} Decisions.md` pulls every materialized per-facet ruleset including this one.

Direct adoption (if an anchor wants only the Testing rules without the rest of R-facet):

```markdown
# {slug} Decisions
include:: [[R-testing]]
```

## See also

- [[DAS Testing]] — facet spec this ruleset enforces.
- [[HBR Testing]] — worked example that conforms to R-testing.
- [[R-facet]] — parent umbrella; pulls R-testing alongside future per-facet sets.
- [[DAS Rulesets]] — top-level catalog.
- [[F133 — Rulesets folder convention + facet embedding]] — the convention this file follows.
