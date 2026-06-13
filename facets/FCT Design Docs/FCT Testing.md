---
description: testing facet — the project's testing strategy (kinds, amounts, responsibilities) followed by an overview of the actual tests proposed, consistent with that strategy. Low-level test specs live in module docs, not here.
---

# FCT Testing

Spec for the `{NAME} Testing.md` design facet — a two-part doc combining the project's testing strategy with a proposed-tests inventory, peer to Architecture and UX Design under Design.

**Location:** `{NAME} Design/{NAME} Testing.md` (or `{NAME} Testing/` if it grows to anchor-folder form, parallel to Architecture).

The Testing facet is the **system-level testing story** — how this project gets tested. It is a peer of [[FCT Architecture|Architecture]] and [[FCT UX Design|UX Design]] under [[FCT Design Dispatch|Design]]: where Architecture says *how the system is structured* and UX Design says *what users see*, Testing says *how we will know it works*.

A `{NAME} Testing.md` has two parts that ship together:

1. **Strategy** — the approach. Kinds of testing this project will use, how much of each is designed for, where each lives, who authors what.
2. **Proposed tests overview** — the test inventory at facet altitude. One row per proposed test, consistent with the strategy. The *spec* of each test (preconditions, fixtures, assertions, expected outputs) lives in the relevant module doc, not here.

**Strategy vs proposed tests vs low-level specs — the three-altitude split.** This facet owns the top two altitudes; module docs ([[FCT Module Doc]]) own the lowest.

| Altitude | Lives at | Carries |
|---|---|---|
| Strategy | `{NAME} Testing.md` § Strategy | Kinds of test, completeness targets, authoring responsibilities, tier mapping. |
| Proposed tests (inventory) | `{NAME} Testing.md` § Proposed Tests | Test name, kind, what it exercises, link to its low-level spec. One row per test. |
| Low-level spec | Module doc (`{NAME} Dev Docs/<Module>.md` or `Test/` block on a module page) | Preconditions, fixtures, assertions, expected outputs, actual test code reference. |

The facet doc reads top-down: a reviewer can answer "is this enough testing?" from § Strategy alone, then drill into § Proposed Tests to verify the strategy actually maps to concrete tests, then follow links into module docs for full detail.

## Standard section order

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc | YAML frontmatter (with `status::` field) + `# {NAME} Testing` H1 + dispatch table + **TLDR** (required per [[DSC progressive-disclosure]] § Per-facet preface requirements). |
| 2 | `## Overview` | One paragraph — what this project's testing posture is in a sentence (e.g., "Heavy unit + integration; minimal e2e because the surface is library-shaped"). The reader leaves knowing the *shape* of the test investment. Often elaborates on what the TLDR has already gestured at. |
| 3 | `## Strategy` | The first part of the facet. Subsections below. |
| 3a | `### Test Kinds` | List of categories used (unit / integration / e2e / property-based / smoke / regression / performance / …). One sentence each: definition + scope. |
| 3b | `### Completeness Targets` | Per kind: the bar. "Every public function in `src/`", "every subsystem boundary", "one per user story", or "no target — sampled". Be specific; targets are auditable. |
| 3c | `### Responsibilities` | Who authors what. Agent on `/mint`? Author-curated? CI? Hand off across kinds is explicit. |
| 3d | `### Tier Mapping` | Connection to [[DSC verification]]'s four tiers. Which kinds satisfy which tier. Establishes what level of confidence a passing suite produces. |
| 4 | `## Proposed Tests` | The second part. Inventory table — one row per proposed test, grouped by kind. See § Proposed-tests table below. |
| 5 | `## See also` (optional) | Links to peer design docs (PRD, Architecture, UX), to `[[DSC verification]]`, to `/mint` and `/code test` for execution context. |

The spine is `Overview → Strategy → Proposed Tests`. § 2–4 are the load-bearing invariant; § 5 is optional.

## Proposed-tests table

`## Proposed Tests` is grouped by kind (H3 per kind matching § Strategy § Test Kinds), with a table of one row per test inside each group:

```markdown
## Proposed Tests

### Unit

| Test                                | Exercises                                   | Spec                          |
| ----------------------------------- | ------------------------------------------- | ----------------------------- |
| `test_scheduler_priority_ordering`  | Scheduler picks highest-priority Ready task | [[CAE-Scheduler#Tests]]       |
| `test_retry_backoff_exponential`    | Retry delays double up to cap               | [[CAE-Retry#Tests]]           |

### Integration

| Test                                 | Exercises                                          | Spec                          |
| ------------------------------------ | -------------------------------------------------- | ----------------------------- |
| `test_schedule_then_drain_end_to_end` | Schedule N tasks, drain blocks until all complete | [[CAE Dev Docs/CAE-Boundary]] |
```

**Spec column rules:**

- A wiki-link to wherever the low-level test spec lives — typically a `## Tests` block on a module doc, or a dedicated test-spec page when the test crosses module boundaries.
- `[bare brackets]` (no double bracket) for proposed-but-unwritten specs that don't yet have a destination.
- Never inline the spec into this table — that's the altitude inversion this facet is designed to prevent.

## YAML status field

The frontmatter carries a `status::` dataview field tracking facet completeness:

```yaml
---
description: {NAME} Testing — strategy + proposed-tests overview.
status:: drafting
---
```

Valid values: `drafting | in-review | accepted`. Acceptance is the Gate 2 signal for `/design` (Architecture AND Testing both `accepted` → roadmapping unblocks). The user sets `accepted` explicitly in natural language ("the testing strategy is accepted") or by editing the field directly.

## Naming convention

- **Facet file:** `{NAME} Testing.md` — just `Testing`, not `Testing Strategy`. The doc covers more than strategy (strategy + proposed tests); the shorter name reflects that.
- **Proposed-test names:** project's native test-runner convention. For Python pytest: `test_<thing>_<condition>`. For Rust: `<mod>::<test_fn>`. The Test column shows the runner-native name verbatim so it greps against the test file.

## Trait applicability

Available to any anchor that ships testable behavior — primarily `Code` trait but `Skill` and `Publishable` anchors with verifiable outputs may use it too. Most anchors with no shipping code (e.g., pure `Topic` anchors) won't carry this facet.

## Relationship to existing infrastructure

- **`/design testing` sub-skill** ([[skills/design/design-testing|design-testing.md]]) is the authoring skill for this facet. The sub-skill was rewritten 2026-06-10 (F136) to author the two-part `{NAME} Testing.md` shape per this facet; the legacy 5-H2 `{NAME} Testing Strategy.md` scaffold it previously produced is superseded. Migration of any existing `{NAME} Testing Strategy.md` files happens lazily — design-testing's runbook detects the legacy file and migrates on first invocation.
- **`[[DSC verification]]`** is the four-tier discipline this facet's Tier Mapping cites. Testing kinds map to verification tiers — they are not the same vocabulary.
- **`[[FCT Architecture]]`** is the peer facet whose subsystem boundaries drive integration-test coverage. Re-read Architecture before drafting § Proposed Tests § Integration.

## Audit

`/audit testing` (future) would flag:

- **strategy-without-tests** — § Strategy declares a kind with a non-zero completeness target, but § Proposed Tests has no rows of that kind.
- **tests-without-strategy** — § Proposed Tests includes a kind not declared in § Strategy § Test Kinds.
- **orphan-test-row** — a proposed-test row's Spec column is bracketed (unwritten) for more than one Roadmap milestone past its commission. (The intent is to write specs as you write tests; bracketed entries that linger become silent omissions.)
- **target-miss** — a completeness target is declared (e.g., "every subsystem boundary") and § Proposed Tests doesn't cover the bar set by Architecture.

## See also

- [[FCT Architecture]] — peer facet under Design.
- [[FCT UX Design]] — peer facet under Design.
- [[FCT PRD]] — user stories drive e2e test inventory in § Proposed Tests.
- [[DSC verification]] — four-tier verification discipline that § Tier Mapping cites.
- [[CAE Testing]] — worked example for CAE Example CLI.
- [[skills/design/design-testing|design-testing]] — authoring sub-skill for `/design testing`.


# RULESET R-testing
include::
where:: file:{ANCHOR}/**/* Testing.md
description:: facet spec this doc instantiates

Embedded ruleset for the Testing facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Adopted via `R-facet` umbrella; an anchor that wants its `{NAME} Testing.md` audited pulls `R-facet` from its `{NAME} Decisions.md`.

### RULE R-testing-01 — File name is `{NAME} Testing.md` (checked)
check:: testing_filename_correct

The facet doc is named `{NAME} Testing.md` — not `{NAME} Testing Strategy.md`, `{NAME} Tests.md`, or any other variant. The doc covers strategy AND proposed tests; the name reflects the scope.

**Check pattern:** `ls "{anchor}/{NAME} Design/{NAME} Testing.md"` exists. No file named `{NAME} Testing Strategy.md` exists alongside (would be the legacy design-testing scaffold; flag for migration).

**Why:** the older `design-testing` scaffold authored `Testing Strategy.md`; this facet supersedes that shape. The shorter name is canonical going forward.

### RULE R-testing-02 — `## Strategy` H2 present with required subsections (checked)
check:: strategy_subsections_present_ordered

The doc has a `## Strategy` H2 containing four H3 subsections in this order: `### Test Kinds`, `### Completeness Targets`, `### Responsibilities`, `### Tier Mapping`.

**Check pattern:** grep for the four H3 headers under `## Strategy`. All four required; ordering required.

**Why:** the four subsections are the load-bearing strategy components. A doc missing Tier Mapping (the most-often-skipped one) loses the connection to [[DSC verification]] and silently weakens what a passing suite proves.

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

The `## Strategy § Tier Mapping` sub-section references `[[DSC verification]]` and maps at least three of the four tiers to test kinds.

**Check pattern:** grep for `[[DSC verification]]` link in the Tier Mapping body; count tier-1/-2/-3/-4 mentions.

**Why:** the vocabulary connection matters. A Tier Mapping that doesn't cite [[DSC verification]] is freelancing terms that won't match what the verification discipline expects.

### RULE R-testing-10 — TLDR present in preface zone (checked)

The doc carries a `**TLDR**` block in the preface zone (after the dispatch table, before the first body H2), formatted per [[DSC progressive-disclosure]] § TLDR formatting: 3-5 one-line bullets, each with a 2-3-word bolded descriptor. Topical content typically covers the posture (e.g., "heavy unit + integration") and the per-kind bar.

**Check pattern:** the file contains a line `^\*\*TLDR\*\*$` (or `^# TLDR$` style heading) preceding the first `## ` body heading; the immediately-following bullets follow the formatting spec.

**Why:** Testing docs reduce cleanly to a short posture statement that lets a reader graze in 5 seconds — "this project's testing is X-shaped, with bar Y." Requiring the TLDR makes the grazer-altitude unmissable and prevents the Overview paragraph from carrying the whole burden of high-altitude reading. Worked example: [[CAE Testing]] § preface zone.

(Authored 2026-06-10 in the new `<H> RULE R-<slug>-NN` sentinel form per CAB Rules update. The other 9 rules above are slated for sentinel-form rewrite in F138.)

# BRIEF

- **This is the CAB facet spec for `{NAME} Testing.md`** — it defines the doc shape (Strategy + Proposed Tests, with the four required Strategy subsections), the section order, the proposed-tests table contract, the `status::` gate field, and the embedded `R-testing` ruleset. Edits here ripple to every anchor that adopts the facet.
- **Don't pile per-project content here.** Worked examples (e.g., [[CAE Testing]]) live in their own anchors and are linked from § See also; the spec stays general. Per-source-file editing notes for an actual `{NAME} Testing.md` instance go in that file's own Brief / inline section, not this one.
- **The three-altitude split is load-bearing** — Strategy (this facet) → Proposed Tests inventory (this facet) → low-level test specs (module docs per [[FCT Module Doc]]). Don't blur the boundary by inlining test code, fixtures, or assertions into the Spec column; that's the altitude inversion R-testing-07 exists to prevent.
- **Keep the spec and the `R-testing` RULESET in sync.** When the section order, table contract, or `status::` value set changes in the prose above, audit each `RULE R-testing-NN` block for matching wording, check-pattern accuracy, and any new rule that should be added. The 10 numbered rules are the auditable form of this spec.
- **Authoring authority flows through `/design testing`** — the [[skills/design/design-testing|design-testing]] sub-skill is the canonical authoring path; do not duplicate its runbook here. When the facet shape evolves, update design-testing's runbook in lockstep (the 2026-06-10 F136 rewrite is the precedent).
- **Cross-references that must stay live:** [[FCT Architecture]] (peer facet, drives integration-test bar), [[DSC verification]] (four-tier vocabulary the Tier Mapping cites), [[DSC progressive-disclosure]] (TLDR formatting requirement per R-testing-10), [[CAE Testing]] (worked example), [[F133 — Rulesets folder convention + facet embedding|F133]] (the embedding convention the RULESET below follows).
- **Naming convention is canonical** — `{NAME} Testing.md`, not `Testing Strategy.md` (legacy scaffold). R-testing-01 enforces this; don't reintroduce the longer name when editing examples or migration notes.
