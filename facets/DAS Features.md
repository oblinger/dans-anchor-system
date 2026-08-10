---
description: "specification for F-numbered per-feature design docs and their index page"
---

| -[[DAS Features]]- | → [[DAS]] → [[FCT]] → [DAS Features](hook://p/DAS%20Features)  |
| --- | --- |
| Related | [[DAS Roadmap]],  [[DAS Backlog]],  [[DAS Status]],  [[DAS Facet]],   |
| Rules | [[R-fct-features]],   |
| Examples | [[HBR Features\|minimal]],  [[HBR Features\|fuller]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Features
Specification for the **Features** facet — F-numbered per-feature design docs that live under `{slug} Design/{slug} Features/`, with their index page and first-H2 Open-Questions block.

**Location:** `{slug} Design/{slug} Features/` (folder; one file per feature, `F<NNN> — <Title>.md`).

**Relocated to Design 2026-06-10** — previously lived at `{slug} Track/{slug} Features/` (per F094) and `{slug} Docs/{slug} Plan/{slug} Features/` (pre-F094). Moved into Design alongside [[DAS Roadmap]] because feature docs are themselves design artifacts — each carries a Summary, Success Criteria, and Design section that the PRD / Architecture / Testing facets refer to. Track now holds only [[DAS Backlog]], [[DAS Status]], and tracking metadata. Lazy migration: existing anchors stay at the old location until next `/feature` or `/design` touch repositions them (F142).

**Cardinality: many** — each anchor holds any number of feature docs (one F-numbered file per feature).

**Worked examples:** `examples/HBR/HBR Design/HBR Features/` (in this repo) — three rendered feature docs (`F001 — Content-Hash Dedup.md`, `F002 — On-the-Fly Transcode Session.md`, `F003 — Scheduled Catalog Checkpoint.md`) plus their `HBR Features.md` index, demonstrating the Open-Questions-first-H2-below-H1 convention, the `F<NNN> — <Title>.md` filename pattern, and a clean/empty vs. populated Open-Questions zone. Open them for rendered instances; the structure is specified in prose in the sections below.

## Features Folder Structure

Features are documented in their own subfolder within `{slug} Design/`. Filenames are `F<NNN> — <Title>.md` (zero-padded triple-digit F-number per anchor):

```
{slug} Design/
└── {slug} Features/
    ├── .anchor                          ← description-only metadata (one line, no frontmatter delimiters)
    ├── {slug} Features.md               ← feature index (reverse chronological)
    ├── F001 — Content-Hash Dedup.md     ← individual feature
    ├── F002 — On-the-Fly Transcode Session.md
    └── F003 — Scheduled Catalog Checkpoint.md
```

The `.anchor` is a single plain-text line — e.g. `description: F-numbered feature specs` — with no `---` frontmatter delimiters.

## Features Index Page

The `{slug} Features.md` page lists all features in reverse chronological order (newest first), one bullet per feature. The index may open with the standard anchor dispatch-table header (breadcrumb row + Anchor / Related rows) for vault navigation; the header is optional but recommended once the anchor is wired.

**Row shape:** `[[F<NNN> — <Title>]]` wiki-link, then the lifecycle status in backtick-brackets, then an em-dash, a one-line description, and (for roadmap-commissioned features) a trailing `→ [[{slug} Roadmap|M<n>]]` milestone link. Example from the worked HBR index:

```
- [[F001 — Content-Hash Dedup]] `[Done]` — skip files already in the catalog by content hash during ingest (US-HBR-1). → [[HBR Roadmap|M1.2]]
```

- **FILE NAME** — Each feature is an F-numbered file using the format `F<NNN> — <Title>.md` (zero-padded triple-digit F-number, unique within the anchor). Dated `YYYY-MM-DD <Title>.md` filenames are the legacy form (pre-F-numbering) — do not author new ones; existing dated docs are left until next touch.
- **FEATURE STATUS** — The lifecycle state (`Designing` / `Agreed` / `Implementing` / `Testing` / `Done`) is the single source of truth in the feature doc's `## Status` section. The index row mirrors it in `` `[<State>]` `` backtick-brackets as a navigation convenience; keep the two aligned.

## Feature Document Format

While pending Qs exist, `## Open Questions` (with its `### Resolved` subsection) is the **first H2 below the H1** — the reader hits blocking decisions the moment they pass the head, while the file stays a normal outline (per [[F241 — Questions block below H1 + state-stamped integrity hash|F241]], 2026-07-15; supersedes the earlier above-the-H1 zone). Once every Q resolves the block is **deleted entirely** (Phase 2) and the decisions migrate to a bottom `## Resolved` H2; the rest of the file is the feature spec proper — Summary, Design, etc.

### Open Questions block — present only while Qs are pending

| Section | Level | Required | Purpose |
|---------|-------|----------|---------|
| `## Open Questions` | first H2, below H1 | While Qs pending | Blocking decisions; feature cannot leave Designing while non-empty |
| `### Resolved` | H3 under Open Questions | Staging until Phase 2 | Answered Qs stage here, then migrate to the bottom `## Resolved` H2 |

The block carries a state-script integrity stamp (`<!-- state:q XX -->`); a hand-edit that breaks it trips the on-write warning (warden R-state-region-03 / audit-q C48) — recover with `state revalidate <anchor> <doc>`.

**Workflow note:** every time an agent edits Open Questions — adds a question, resolves one, moves one to Resolved — it immediately runs `open "<path to this file>"` so the doc surfaces on the user's screen. The `/feature` skill's Runbook step 1a enforces this.

### Document zone — H1 and below

Start with only the mandatory sections; add optional sections as the feature grows in complexity.

**Mandatory:**
- **H1 `# [[{slug}]] · F{n} — {Feature Name}`** — anchor-slug breadcrumb (wiki-link to anchor page) + F-number + title. The leading `[[{slug}]]` lets the reader (a) jump back to the anchor page and (b) immediately see which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them. Filename matches without the `[[]]` brackets: `F{n} — {Feature Name}.md`.
- **Title encodes M-position when feature is commissioned from a roadmap milestone** (per [[DAS Roadmap]] R-roadmap-10). Format: `F<NNN> — M-<Name>.<position>: <Title from Roadmap entry>`. Example: `F118 — M-CLI.3.5: Implement CLI Core Statements.md`. The roadmap entry gets a `[F118]` marker pointing at the feature doc. Bi-directional discoverability without rename-cost. See [[F144 — Completed Roadmap + named milestones]] for the provenance discussion. **Features commissioned NOT from a roadmap stay `F<NNN> — <Title>` form** — absence of M-prefix signals "filed independently."
- **F060 placement.** The feature-doc H1 already carries its own breadcrumb (`[[{slug}]] ·`), so the F060 dispatch-table placeholder is **optional** for feature docs. New feature docs may skip the placeholder; older ones that have it can keep it. Rewire does not insert one if absent.
- **Summary** — What the feature does and why it exists (1-2 paragraphs). On the worked examples this opens the document body directly after the H1.
- **Status** — lifecycle state (Designing / Agreed / Implementing / Testing / Done). The state keyword may be elaborated with date / commit / blocking note, e.g. `Done — shipped in v1; covered by ingest integration tests.` or `Designing — awaiting Q2 (cache eviction) resolution.`

**Recommended (add when the feature has user-visible impact or non-obvious acceptance):**
- **Success Criteria** — acceptance criteria plus how completion is verified. Open with a `**Tier: <Required|...>**` line when the feature is a release blocker, then a bullet list of testable conditions. Present on all three worked examples; include it whenever a feature has an external acceptance contract.

**Optional (add as needed, H2 headings in document order):**
- **TLDR (per `progressive-disclosure`)** — 3-5 one-line bullets, each with a 2-3-word bolded descriptor, placed immediately after the H1 (before Summary). Format: `**TLDR**` heading then a bullet list of `- **<Descriptor>** — <one-line summary>`. Add for substantial feature docs whose gist benefits from up-front compression; short single-concern docs (like the worked HBR examples) may go straight to Summary.
- **Interface** — Description of external interface (API, CLI, config, user, etc.)
- **Requirements** — Specific acceptance criteria or constraints
- **Design** — Technical approach, architecture decisions, trade-offs
- **Dependencies** — What this feature depends on or what it blocks
- **Roadmap** — Execution plan for substantial features. See § Roadmap section below.
- **Notes** — Working notes, research

### `## Roadmap` section — for features substantial enough to spawn sub-work

Large feature docs sometimes need their own sub-roadmap — the feature is a chunk of work that breaks down into multiple independent sub-tasks or sub-features. The `## Roadmap` H2 is the home for this sub-plan; it follows the [[DAS Roadmap]] conventions (multi-level numbering, checkboxes, Status-line, etc.) scoped to *inside this feature*.

**Two patterns within a feature's Roadmap:**

1. **Dotted sub-numbering** — `F<NNN>.1`, `F<NNN>.2`, `F<NNN>.3` for sub-items that stay inside this feature doc. Each sub-item is a chunk of work that gets minted in turn; the parent F-number stays the unit of feature-level tracking. Use when the sub-items are too small to deserve their own feature docs.
2. **Sub-feature spinoffs** — bullets like `[ ] [[F<NNN+k> — <Title>]]` (or bare brackets `[F<NNN+k> — <Title>]` for as-yet-unwritten feature docs) when a sub-item is substantial enough to deserve its own feature doc. The parent's roadmap captures the intent; the child feature doc gets authored when work on that piece begins.

Both patterns can mix in the same Roadmap section — small inline sub-items stay dotted; substantial spinoffs get their own F-numbers.

**Example:**

```markdown
## Roadmap

- [x] **F017.1 — WAL append path** — wrap enqueue/dequeue in `cae.wal` append. Independent.
- [x] **F017.2 — SQLite schema + migrations** — `migrations/0001_init.sql`. Independent of F017.1.
- [ ] **F017.3 — Recovery loader** — depends on F017.1 + F017.2. Will spawn:
    - [ ] [F049 — WAL compaction strategy] — not yet authored; capture when recovery loader's bottleneck surfaces.
- [ ] **F017.4 — Backpressure on durable enqueue** — defer to post-MVP.

**Status:** Core complete — F017.1 + F017.2 merged. F017.3 in progress; F049 deferred.
```

When the Roadmap section drives the feature's tracking, the feature doc's `## Status` field above carries the rollup ("Core complete — 2/4 sub-items done") and the Roadmap section carries the per-sub-item detail. Consistent with the [[DAS Roadmap]] "checkbox + Status-line + per-item-checkbox" three-axis convention applied at smaller scope.

**Referencing as-yet-undesigned sub-features.** Bare-bracket entries `[F<NNN+k> — <Title>]` signal "this sub-feature will exist when authoring catches up." When the agent / user reaches that sub-item and creates the actual feature doc, the bare brackets upgrade to `[[F<NNN+k> — <Title>]]` wiki-links. The roadmap captures intent without requiring all sub-features to be designed up front.

---

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this Features-facet spec. The normative shape is the body above + the extracted [[R-fct-features]] ruleset; skills `/feature`, `/design`, `/groom`, `/crank` cite it and audit/rewire check anchors against it.)*

- **NOT a feature index, NOT a backlog, NOT a roadmap** — don't pile concrete `F<NNN>` entries, status lists, or per-anchor feature catalogs here. Those live in `{slug} Features.md` index pages within each anchor, or in [[DAS Backlog]] / [[DAS Roadmap]] for their respective concerns.
- **Inclusion test for edits** — a change belongs here only if it defines the *shape* of feature docs across all anchors: folder location, filename pattern, the block layout (Open Questions as the first H2 below the H1; spec body follows), mandatory vs optional H2 sections, title-encoding conventions (M-position), or the Roadmap-within-feature sub-pattern. Anchor-local feature conventions go in `{slug} Rules.md` or `{slug} Decisions.md`, not here.
- **No inline reference example — link the real ones.** The feature-doc shape is conveyed by the prose sections (Folder Structure / Index Page / Feature Document Format) plus the `**Worked examples:**` pointer to the `examples/HBR/HBR Design/HBR Features/` docs in this repo. Do NOT paste a sample feature doc back into this spec.
- **Cross-references to maintain** — [[DAS Roadmap]] (M-position title encoding, sub-roadmap pattern), [[DAS Backlog]] (tracking surface), [[DAS Status]] (lifecycle states), `progressive-disclosure` (TLDR rule), and the relocation note (F094 → 2026-06-10 Design move; F142 lazy-migration). Changing any load-bearing convention ripples across every anchor — update the worked examples and downstream skill runbooks in the same pass.
