---
description: "facet spec this doc instantiates"
---

| -[[DAS Testing]]- | → [[DAS]] → [[FCT]] → [DAS Testing](hook://p/DAS%20Testing)  |
| --- | --- |
| Related | [[DAS Architecture]],  [[DAS UX Design]],  [[DAS PRD]],  [[DAS Design Docs]],  [[DAS Common Testing Types]],  [[templates/testing.md\|testing template]],   |
| Examples | [[Mini Testing\|minimal worked example]],  [[HBR Testing\|maximal worked example]],   |
| Rules | [[R-testing]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Testing
Spec for the `{slug} Testing.md` design facet — a two-part doc combining the project's testing strategy with a proposed-tests inventory, peer to Architecture and UX Design under Design.

**Location:** `{slug} Design/{slug} Testing.md` (or `{slug} Testing/` if it grows to anchor-folder form, parallel to Architecture).

**Cardinality:** one per anchor — a project has exactly one testing facet doc.

**Two forms in the wild.** Real instances span a range:

- **Single-file, lean** — the common case (e.g. [[Mini Testing]], [[HBR Testing]]): one `{slug} Testing.md` with the standard sections below.
- **Single-file, grown** — a large project keeps the single file but adds project-specific strategy sections between Strategy and Proposed Tests (relevance-gating rules, subjective-review notes), and may carry extra **Scope** / **Recipe** columns on its tables. These additions are allowed — the load-bearing invariant is the `Overview → Strategy → Proposed Tests` spine, not the absence of extra sections or columns.

**Anti-pattern — inlined specs.** Some legacy instances skip the `## Proposed Tests` inventory and instead inline each test's Precondition / Steps / Pass directly under per-test H3s. That is the **altitude inversion** R-testing-07 exists to prevent: the facet doc becomes the test file and the three-altitude split collapses. The fix is to lift those low-level specs into module docs and replace the H3 blocks with one inventory row each, the spec body moving behind the Spec-column link.

The Testing facet is the **system-level testing story** — how this project gets tested. It is a peer of [[DAS Architecture|Architecture]] and [[DAS UX Design|UX Design]] under [[DAS Design Dispatch|Design]]: where Architecture says *how the system is structured* and UX Design says *what users see*, Testing says *how we will know it works*.

A `{slug} Testing.md` has two parts that ship together:

1. **Strategy** — the approach. Kinds of testing this project will use, how much of each is designed for, where each lives, who authors what.
2. **Proposed tests overview** — the test inventory at facet altitude. One row per proposed test, consistent with the strategy. The *spec* of each test (preconditions, fixtures, assertions, expected outputs) lives in the relevant module doc, not here.

**Strategy vs proposed tests vs low-level specs — the three-altitude split.** This facet owns the top two altitudes; module docs ([[DAS Module Doc]]) own the lowest.

| Altitude | Lives at | Carries |
|---|---|---|
| Strategy | `{slug} Testing.md` § Strategy | Kinds of test, completeness targets, authoring responsibilities, tier mapping. |
| Proposed tests (inventory) | `{slug} Testing.md` § Proposed Tests | Test name, kind, what it exercises, link to its low-level spec. One row per test. |
| Low-level spec | Module doc (`{slug} Dev Docs/<Module>.md` or `Test/` block on a module page) | Preconditions, fixtures, assertions, expected outputs, actual test code reference. |

The facet doc reads top-down: a reviewer can answer "is this enough testing?" from § Strategy alone, then drill into § Proposed Tests to verify the strategy actually maps to concrete tests, then follow links into module docs for full detail.

## Standard section order

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc | YAML frontmatter (with `status::` field) + `# {slug} Testing` H1 + dispatch table + **TLDR** (required per [[DAS progressive-disclosure]] § Per-facet preface requirements). |
| 1b | `## Tests` | **REQUIRED coverage table** directly below the preface (after TLDR, before Overview). One row per test kind: **Kind** (a link — see § The tests-table) · **In system** (current test count) · **Expected** (target count and/or qualitative coverage). The grazer-altitude coverage map. |
| 2 | `## Overview` | One paragraph — what this project's testing posture is in a sentence (e.g., "Heavy unit + integration; minimal e2e because the surface is library-shaped"). The reader leaves knowing the *shape* of the test investment. Often elaborates on what the TLDR has already gestured at. |
| 3 | `## Strategy` | The first part of the facet. Subsections below. |
| 3a | `### Test Kinds` | List of categories used (unit / integration / e2e / property-based / smoke / regression / performance / …). One sentence each: definition + scope. |
| 3b | `### Completeness Targets` | Per kind: the bar. "Every public function in `src/`", "every subsystem boundary", "one per user story", or "no target — sampled". Be specific; targets are auditable. |
| 3c | `### Responsibilities` | Who authors what. Agent on `/mint`? Author-curated? CI? Hand off across kinds is explicit. |
| 3d | `### Tier Mapping` | Connection to [[DAS verification]]'s four tiers. Which kinds satisfy which tier. Establishes what level of confidence a passing suite produces. |
| 4 | `## Proposed Tests` | The second part. Inventory table — one row per proposed test, grouped by kind. See § Proposed-tests table below. |
| 5 | `## See also` (optional) | Links to peer design docs (PRD, Architecture, UX), to `~~[[DAS verification]]~~`, to `/mint` and `/code test` for execution context. |

The spine is `Overview → Strategy → Proposed Tests`. § 2–4 are the load-bearing invariant; § 5 is optional. The `## Tests` coverage table (§ 1b) sits in the preface, above the spine.

## The tests-table (required)

Directly below the preface (after the **TLDR**, before `## Overview`), every `{slug} Testing.md` carries a **`## Tests`** table — the at-a-glance coverage map. **One row per test kind** the project uses, in the same kind set as `## Strategy § Test Kinds`. Columns:

| Column | Contents |
|---|---|
| **Kind** | the test kind, as a **link** (target rule below). |
| **In system** | how many tests of this kind exist *today* — a count (`0` if none yet). |
| **Expected** | the coverage bar: an estimated count and/or a qualitative statement (e.g. "~25 — one per invariant", "exhaustive on the pure core", "sampled — no fixed target"). |

**The Kind cell is always a link**, and the target depends on whether the project's use of that kind is ordinary:

- **Vanilla** — the project uses the kind the standard way → link to the matching H2 in [[DAS Common Testing Types]] (e.g. `~~[[Common Testing Types#Property\|Property]]~~`).
- **Special** — the project does something noteworthy with the kind → link to a section **within this same `{slug} Testing.md`** explaining the twist (e.g. `[[#Wire-contract goldens\|Golden]]`). That in-doc section carries only what is *different* from the generic, and may itself cite the Common Testing Types H2.

A reviewer reads `## Tests` to answer "what kinds, how much now, how much intended?" in one glance, then drops into `## Strategy` for the why and `## Proposed Tests` for the individual rows. The kind set here must equal the kinds in `## Strategy § Test Kinds` (and thus the H3 groups in `## Proposed Tests`).

## Proposed-tests table

`## Proposed Tests` is grouped by kind (H3 per kind matching § Strategy § Test Kinds), with a table of one row per test inside each group:

```markdown
## Proposed Tests

### Unit

| Test                                | Exercises                                   | Spec                          |
| ----------------------------------- | ------------------------------------------- | ----------------------------- |
| `test_scheduler_priority_ordering`  | Scheduler picks highest-priority Ready task | [[FEX Scheduler#Tests]]       |
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
description: {slug} Testing — strategy + proposed-tests overview.
status:: drafting
---
```

Valid values: `drafting | in-review | accepted`. Acceptance is half of the design-accepted gate's record for `/design` (Architecture AND Testing both `accepted` → the one gate has passed and roadmap elaboration unblocks, per [[DAS Design Design]]). The user passes the gate in natural language ("the design is accepted"); the agent stamps both fields in the same pass.

## Naming convention

- **Facet file:** `{slug} Testing.md` — just `Testing`, not `Testing Strategy`. The doc covers more than strategy (strategy + proposed tests); the shorter name reflects that.
- **Proposed-test names:** project's native test-runner convention. For Python pytest: `test_<thing>_<condition>`. For Rust: `<mod>::<test_fn>`. The Test column shows the runner-native name verbatim so it greps against the test file.

## Trait applicability

Available to any anchor that ships testable behavior — primarily `code` trait but `skill` and `Publishable` anchors with verifiable outputs may use it too. Most anchors with no shipping code (e.g., pure `topic` anchors) won't carry this facet.

## Relationship to existing infrastructure

- **`/design testing` sub-skill** ([[skills/design/design-testing|design-testing.md]]) is the authoring skill for this facet. The sub-skill was rewritten 2026-06-10 (F136) to author the two-part `{slug} Testing.md` shape per this facet; the legacy 5-H2 `{slug} Testing Strategy.md` scaffold it previously produced is superseded. Migration of any existing `{slug} Testing Strategy.md` files happens lazily — design-testing's runbook detects the legacy file and migrates on first invocation.
- **`~~[[DAS verification]]~~`** is the four-tier discipline this facet's Tier Mapping cites. Testing kinds map to verification tiers — they are not the same vocabulary.
- **`~~[[DAS Architecture]]~~`** is the peer facet whose subsystem boundaries drive integration-test coverage. Re-read Architecture before drafting § Proposed Tests § Integration.

## Audit

`/audit testing` (future) would flag:

- **strategy-without-tests** — § Strategy declares a kind with a non-zero completeness target, but § Proposed Tests has no rows of that kind.
- **tests-without-strategy** — § Proposed Tests includes a kind not declared in § Strategy § Test Kinds.
- **orphan-test-row** — a proposed-test row's Spec column is bracketed (unwritten) for more than one Roadmap milestone past its commission. (The intent is to write specs as you write tests; bracketed entries that linger become silent omissions.)
- **target-miss** — a completeness target is declared (e.g., "every subsystem boundary") and § Proposed Tests doesn't cover the bar set by Architecture.

## See also

- [[DAS Architecture]] — peer facet under Design.
- [[DAS UX Design]] — peer facet under Design.
- [[DAS PRD]] — user stories drive e2e test inventory in § Proposed Tests.
- [[DAS verification]] — four-tier verification discipline that § Tier Mapping cites.
- [[DAS Common Testing Types]] — the standard test-kind catalogue (one H2 per kind) that the required `## Tests` table's Kind cells link to for vanilla kinds.
- [[HBR Testing]] — worked example for CAE Example CLI.
- [[skills/design/design-testing|design-testing]] — authoring sub-skill for `/design testing`.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the embedded `R-testing` ruleset is its auditable form.)*

- **Inclusion test** — a change belongs here only if it applies to every `{slug} Testing.md` across anchors. Per-project content and worked examples ([[HBR Testing]], [[Mini Testing]], [[MUX Testing]]) live in their own anchors, linked from § See also; never inline them here.
- **Keep spec ↔ ruleset in sync** — when the section order, table contract, or `status::` value set changes above, audit each `RULE R-testing-NN` block for matching wording, check-pattern accuracy, and any rule that should be added; the numbered rules are the auditable form of this prose.
- **Sync downstream in lockstep** — the [[skills/design/design-testing|design-testing]] sub-skill is the canonical authoring path (update its runbook when the facet shape evolves — the 2026-06-10 F136 rewrite is the precedent), and the `## Tests` coverage table's Kind cells track [[DAS Common Testing Types]] (keep in sync when either changes).
- **Cross-references that must stay live** — [[DAS Architecture]], [[DAS verification]], [[DAS progressive-disclosure]], [[DAS Common Testing Types]], [[HBR Testing]], [[F133 — Rulesets folder convention + facet embedding|F133]]; renaming or moving any requires updating the wiki-links here.
