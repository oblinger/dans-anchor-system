---
description: "facet spec for {NAME} PRD.md — the anchor's product requirements document"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT PRD](hook://p/FCT%20PRD)
# FCT PRD
**Audited examples:** [[HBR PRD]], [[Mini PRD]], [[HBR PRD]], [[DMUX PRD]], [[OBU PRD]]

| Table of Contents |  |
|---|---|
| [[#Location]] |  |
| [[#Two forms — single-file (default) and folder (when stories extract)]] |  |
| [[#Standard section order]] |  |
| [[#Preface zone requirements]] |  |
| [[#User stories — naming and lifecycle]] |  |
| [[#Open questions — handled by `/ask`]] |  |
| [[#Status tracking]] |  |
| [[#Cardinality]] |  |
| [[#Common deviations in real instances]] |  |
| [[#Trait applicability]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

Facet spec for `{NAME} PRD.md` — the first doc in an anchor's Design folder, defining what the product does (goals, non-goals, user stories) for every downstream design phase to consume.

**Related:** [[FCT Architecture]],  [[FCT Testing]],  [[FCT Decisions]],  [[FCT Stories]]
**Examples:** [[HBR PRD\|single-file form]],  [[HBR PRD\|folder form (stories extracted)]]

The PRD (`{NAME} PRD.md`) is the **what** of the product — what it does, who it serves, what's in and out of scope, and the user stories that downstream work realizes. It is the first document written during `/design`, and every downstream phase (UX, Architecture, Testing, Roadmap, Features) reads it as authoritative input.

PRDs are deliberately not the place for technical decisions, principles, rules, or implementation detail — those live in [[FCT Decisions]], [[FCT Ruleset]], [[FCT Architecture]], and per-module docs respectively. The PRD's job is to define the contract that lets everything downstream argue from the same shared understanding of what the product is.

## Location

`{NAME} Design/{NAME} PRD.md` (single-file form) **or** `{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form, when user stories migrate to the [[FCT Stories|Stories sub-facet]]).

**File location moved 2026-06-01 per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]]** — legacy path `{NAME} Docs/{NAME} Plan/{NAME} PRD.md` is superseded. Existing legacy locations migrate during normal anchor work.

## Two forms — single-file (default) and folder (when stories extract)

### Single-file form (default)

```
{NAME} Design/{NAME} PRD.md
```

User stories live inline under `## User Stories` as bullets. Right for most PRDs.

### Folder form (when stories grow to need their own pages)

```
{NAME} Design/{NAME} PRD/
├── {NAME} PRD.md           ← this file, anchor file (matches folder name)
├── {NAME} Stories.md       ← stories dispatch index
├── US-<SLUG>-1 — <Title>.md ← individual story files
└── ...
```

Per [[FCT Stories]]. The PRD's `## User Stories` section then links to `[[{NAME} Stories]]` instead of carrying inline bullets. Migration is one-way; mixing inline and extracted stories in the same PRD is forbidden.

## Standard section order

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc | YAML frontmatter (`description:`) → `:>>` breadcrumb glued directly above the H1 → `# {NAME} PRD` → one-sentence summary. Single-file PRD carries the breadcrumb (no dispatch table); folder-form PRD is an anchor and carries a dispatch table instead (per R-prd-03 / [[FCT Doc Structure|R-doc-structure]]). |
| 2 | `## Overview` | One to two paragraphs — what the product *is*, who it's for, why it needs to exist. Reader leaves knowing the shape of the thing. |
| 3 | `## Design Workflow` | Table listing the design phases downstream of this PRD with wiki-links: PRD → Architecture → Testing → Decisions → Track (Roadmap + Features). The sequence may be revisited iteratively as questions surface. |
| 4 | `## Goals` | Concrete, verifiable outcomes — what the product will accomplish. Bulleted; outcome-shaped (not feature-shaped). |
| 5 | `## Non-Goals` | What the product explicitly will NOT do. Each non-goal is one of: (a) deferred to a future version, (b) out of scope by design, (c) constraint from the environment. Keeps scope conversation honest. |
| 6 | `## User Stories` | Either inline bullets (`US-<SLUG>-<N>` per [[FCT Stories]]) or a wiki-link to `[[{NAME} Stories]]` if folder form. Each story is "As a `<role>`, I want `<capability>` so that `<reason>`." |
| 7 | `## Open Questions` (optional) | Pending decisions surfaced via [[DSC ask-format]]. Lives below the H1 only while pending Qs exist; deletes entirely once all resolve. |
| 8 | `## Resolved` (optional) | Bottom-of-doc archive of resolved questions and decisions, H3 per resolution. Populated as questions resolve; never deleted. |
| 9 | `## See also` (optional) | Links to peer Design facets (Architecture, Testing, Decisions). |

The spine is `Overview → Design Workflow → Goals → Non-Goals → User Stories`. Sections 7-9 appear as needed.

Real instances vary in section *naming* around this spine (e.g. `## Purpose` for Overview, `## Primary Goals`/`## Core Capabilities` for Goals) and some predate the `## Design Workflow` row entirely. The conformant target is the canonical names and order above; older PRDs migrate toward it during normal anchor work rather than being rewritten wholesale.

**Working example:** [[HBR PRD]] — single-file form; three inline stories.

## Preface zone requirements

Per [[DSC progressive-disclosure]] § Per-facet preface requirements:

- **Dispatch table** — **Required**.
- **TLDR** — **Explicitly NOT required**. PRDs are too heterogeneous to compress meaningfully into 3-8 bullets without filler; forcing one degrades the doc. The `## Overview` section serves the grazer-altitude need.
- **Figure** — Optional. A product-shape mockup or context diagram can help on visual products; skip for CLI / library / pure-data projects.

## User stories — naming and lifecycle

- **Identifier:** `US-<SLUG>-<N>` per [[FCT Stories]] § Naming convention. Monotonic-forever within the anchor; never recycled.
- **Inline shape:** H3 heading `### US-<SLUG>-<N>: <Title>` followed by the canonical "As a `<role>`, I want `<goal>` so that `<reason>`" sentence on the next line.
- **When stories grow:** migrate to [[FCT Stories]] folder form. The PRD's `## User Stories` section then reads "See [[{NAME} Stories]] for the story index" + (optionally) a wiki-list of the top-level stories.

### Dispatch-row pointer to stories — required in both forms

The PRD's top-of-doc dispatch table carries a row pointing at stories. The link target depends on the form, but the **display alias is always `{NAME} Stories`** (the proper anchor-prefixed name, matching the convention used by sibling rows like `[[{NAME} Architecture]]`, `[[{NAME} Testing]]`):

- **Single-file PRD (inline stories):** `[[{NAME} PRD#User Stories\|{NAME} Stories]]` — section-deep wiki-link into this same doc's `## User Stories` H2, displayed as `{NAME} Stories`. The description names the story count: *"three user stories (inline-bullet form per [[FCT Stories]]; US-{SLUG}-1..N)"*.
- **Folder-form PRD (extracted stories):** `[[{NAME} Stories]]` — wiki-link to the sibling dispatch index; display defaults to the page name (`{NAME} Stories`). The description names the count: *"N user stories — index at [[{NAME} Stories]]"*.

The row is required in both forms so a reader landing on the PRD has a one-click jump to "what does this product DO for users" without scrolling. The proper-name display keeps the row consistent with its peers in the dispatch table. Worked example: [[HBR PRD]] § dispatch table.

## Open questions — handled by `/ask`

PRD discussions surface questions throughout. The PRD does NOT carry a separate `{NAME} Open Questions.md` file (legacy pattern, deprecated). Instead:

- **Active questions** live as `## Open Questions` H2 directly below the H1, per [[DSC ask-format]].
- **Resolved questions** move to `## Resolved` at the bottom of the doc when answered. Never deleted.
- **The `/ask --doc` workflow** is the way to add or resolve questions on a PRD; it handles the formatting, the lifecycle transitions, and the Q.md update.

## Status tracking

Design-phase completeness for the PRD is tracked in `{NAME} Track/{NAME} Status.md` per [[FCT Status]], on the `prd::` line. The PRD file itself does NOT carry a `status::` dataview field — the centralized Status facet is the single source of truth. Legacy per-doc `status::` is acceptable as a fallback when the Status file doesn't exist yet.

## Cardinality

**One per anchor.** An anchor has at most one PRD — the single authoritative statement of what the product is. When user stories grow large enough to extract, they move to [[FCT Stories]] (folder form), but the PRD itself remains one file per anchor.

## Common deviations in real instances

Surveying live PRDs across the vault, these are the recurring drifts from the canonical shape — each maps to a rule below and is a migration target, not an accepted variant:

- **Legacy header form** — `desc::`/`description::` inline instead of YAML frontmatter (`R-prd-02`), or no metadata line at all (e.g. `[[HA Track]] > [[HA PRD]]` breadcrumb-only). *(The `:>>` breadcrumb itself is now required directly above the H1 per `R-prd-03`; the deviation is the missing YAML frontmatter, not the breadcrumb.)*
- **`US-<N>` without the slug** — inline stories numbered `US-1`, `US-2` rather than `US-<SLUG>-<N>` (`R-prd-05`); collides across anchors.
- **`## Design Constraints` (DC-N)** — architectural/technical constraints living in the PRD instead of [[FCT Decisions]] / [[FCT Ruleset]] (`R-prd-09`).
- **Missing `## Design Workflow`** — older PRDs jump from Overview straight to Goals (`R-prd-04`).
- **No `## User Stories` at all** — stub or library PRDs (e.g. consumer-table-only) that never grew a story section (`R-prd-04`/`R-prd-05`); the Goals serve as a stand-in until stories are authored.

## Trait applicability

Any anchor that has a `{NAME} Design/` folder per [[FCT Design]]. Initially supports anchors with code-shaped artifacts; broader applicability (Paper / Topic / Simple traits) covered as those traits land.

## Audit

`/audit prd` (future) would flag the rules captured in `R-prd` below — body-only shape, required-section presence, `US-<SLUG>-<N>` story numbering, no legacy Open Questions file, etc.

## See also

- [[FCT Stories]] — sub-facet activated when user stories grow beyond inline-bullet form
- [[FCT Architecture]] — peer Design facet (system-architecture story)
- [[FCT Testing]] — peer Design facet (testing strategy + proposed-tests overview)
- [[FCT Decisions]] — peer Design facet (load-bearing decisions citing rules)
- [[FCT Status]] — `{NAME} Status.md` carries the PRD's design-phase tier
- [[DSC ask-format]] — open-questions formatting discipline
- [[DSC progressive-disclosure]] — preface-zone requirements
- [[design-prd]] — authoring sub-skill for `/design prd`
- [[HBR PRD]] — worked example (single-file form, three inline stories)

# RULESET R-prd
include::
where:: `file:{ANCHOR}/**/* PRD.md`
description:: facet spec this doc follows

Embedded ruleset for the PRD facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-prd-01 — Location is `{NAME} Design/{NAME} PRD.md` or folder form (checked)
check:: file_path_matches_prd_locations

The PRD lives at `{NAME} Design/{NAME} PRD.md` (single-file form) or `{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form). Not under `{NAME} Docs/`, not under `{NAME} Plan/`, not at the anchor root.

**Check pattern:** path matches one of the two canonical locations.

**Why:** F094 moved Design docs out of the legacy `{NAME} Plan/` folder; surfacing stale paths breaks `/design`'s anchor-detection.

### RULE R-prd-02 — Opens with YAML frontmatter carrying `description:` (checked)
check:: frontmatter_has description

`{NAME} PRD.md` opens with a `---` YAML frontmatter block carrying a one-line `description:` (the doc metadata — the only thing in the frontmatter).

**Check pattern:** the file begins with a `--- … ---` block; `description:` key present and non-empty.

**Why:** YAML frontmatter is the canonical metadata form across the vault (anchor pages, design docs); the inline `desc::`/`description::` form is deprecated.

### RULE R-prd-03 — Top-matter follows R-doc-structure (breadcrumb-above-H1 for the single-file PRD) (checked)
check:: h1_after_frontmatter

The PRD's top-matter follows [[FCT Doc Structure|R-doc-structure]]-01/-02, which turns on whether the PRD is an anchor:

- **Single-file PRD (the default — a non-anchor member file inside `{NAME} Design/`)** carries a `:>>` breadcrumb line **directly above** the H1, with **no blank line** between the breadcrumb and `# {NAME} PRD` (per R-doc-structure-01). It carries **no** dispatch table (R-doc-structure-02 — a masthead is only for anchors). The breadcrumb's parent is the `{NAME} Design` anchor: `:>> … → [[{NAME}]] → [[{NAME} Design]]`.
- **Folder-form PRD (`{NAME} Design/{NAME} PRD/{NAME} PRD.md`)** is the anchor file of its own folder, so it carries a **dispatch table** (breadcrumb in the first cell), not a `:>>` line.

Frontmatter (`--- … ---`, metadata only) precedes either form.

**Check pattern:** skip the leading `--- … ---` block; for a single-file PRD the next non-blank line is a `:>>` breadcrumb and the line **immediately** below it is the `# {NAME} PRD` H1 (no blank between); for a folder-form PRD the next table is a dispatch masthead. Delegates the breadcrumb-vs-dispatch choice to R-doc-structure.

**Why:** a PRD is a member document inside its anchor, and every non-anchor member document carries its parent up-edge as a `:>>` breadcrumb glued to the H1 (R-doc-structure-01) — the earlier "H1-first, no breadcrumb" form dropped the up-edge. Anchor-ness (single-file vs folder-form), not the doc kind, decides breadcrumb-vs-dispatch, so this rule defers to R-doc-structure rather than restating it.

### RULE R-prd-04 — Required sections present in order (checked)
check:: required_sections_in_order

The PRD contains H2s `## Overview`, `## Design Workflow`, `## Goals`, `## Non-Goals`, `## User Stories` (in that order). Optional H2s (`## Open Questions`, `## Resolved`, `## See also`) may follow.

**Check pattern:** parse H2 headers; assert the five required ones appear in declared order.

**Why:** downstream design phases read the PRD assuming this section spine. Missing sections force the reader to hunt for what they expect to find in a known location.

### RULE R-prd-05 — User stories use `US-<SLUG>-<N>` numbering (checked)
check:: user_stories_use_rid_numbering

Every user-story H3 (inline form) matches `^### US-{SLUG}-\d+: .+` where `{SLUG}` is the anchor's slug. Folder-form PRDs link to `[[{NAME} Stories]]` instead of inline H3s and this rule defers to [[FCT Stories#RULESET R-stories|R-stories]].

**Check pattern:** for inline-form PRDs, enumerate H3s under `## User Stories`; assert each matches the pattern.

**Why:** `US-<SLUG>-<N>` is the load-bearing identifier referenced by feature docs (`Realizes: US-<SLUG>-<N>`), e2e tests (`Exercises: US-<SLUG>-<N>`), and Stories sub-facet files. Old `US-<N>` form (no slug) collides across anchors and breaks cross-anchor references.

### RULE R-prd-06 — No legacy `{NAME} Open Questions.md` file (checked)
check:: no_legacy_open_questions_file

No file named `{NAME} Open Questions.md` exists alongside the PRD. Open questions live as `## Open Questions` H2 directly inside the PRD per [[DSC ask-format]].

**Check pattern:** `ls "{NAME} Design/{NAME} Open Questions.md"` returns no-such-file.

**Why:** the file-based Open Questions pattern was deprecated when `/ask` became the universal asking surface. Linger of the old file produces ambiguity about where to look.

### RULE R-prd-07 — Design Workflow references modern phase names (checked)

The `## Design Workflow` table references `[[{NAME} Architecture]]` (not "System Design"), `[[{NAME} Testing]]` (not "Testing Strategy"), and `[[{NAME} Decisions]]` (not "Principles").

**Check pattern:** parse the Design Workflow table; assert the wiki-link targets are in the modern naming set.

**Why:** F094 (Architecture vs System Design), F113 (Decisions vs Principles), and the 2026-06-10 CAB Testing facet rename (`Testing.md`, not `Testing Strategy.md`) all renamed canonical phase names. References to old names produce broken wiki-links.

### RULE R-prd-08 — Status tracked centrally, not per-doc (stated)

The PRD file does NOT carry a top-of-doc `status::` dataview field. PRD design-phase completeness is tracked in `{NAME} Track/{NAME} Status.md` per [[FCT Status]] on the `prd::` line.

**Check pattern:** grep `{NAME} PRD.md` for `^status::`; expect zero matches when `{NAME} Track/{NAME} Status.md` exists.

**Why:** dual-source-of-truth is the failure mode. F130 made `{NAME} Status.md` authoritative; per-doc `status::` is a legacy fallback that should fade as anchors land Status.md files.

### RULE R-prd-09 — No `## Design Constraints` (DC-N) section (stated)

The PRD does NOT contain a `## Design Constraints` H2 with DC-numbered entries. Architectural / technical constraints belong in [[FCT Decisions]] (`D<N>`) and [[FCT Ruleset]] (`R-<slug>-<NN>`); business / environmental constraints live in `## Non-Goals` or `## Overview`.

**Check pattern:** grep for `^## Design Constraints` or `^### DC-\d+`; expect zero matches.

**Why:** the pre-F113 DC-N pattern conflated business and architectural constraints, and downstream readers couldn't tell which discipline owned which constraint. Splitting Decisions / Rules / Non-Goals gives each constraint a clear home.

### RULE R-prd-10 — Dispatch table carries a Stories row with proper-name display (checked)

The PRD's top-of-doc dispatch table contains a row whose wiki-link target points at the stories — either `[[{NAME} PRD#User Stories\|{NAME} Stories]]` (single-file form) or `[[{NAME} Stories]]` (folder form). The displayed text is always the proper anchor-prefixed name `{NAME} Stories`, matching the display convention used by sibling dispatch rows (`{NAME} Architecture`, `{NAME} Testing`, etc.).

**Check pattern:** parse the PRD's dispatch table; assert at least one row's link target matches one of the two canonical forms AND the row's displayed text is `{NAME} Stories`.

**Why:** Stories are the "what does this product DO for users" of the PRD — readers landing on the PRD need a one-click jump to them without scrolling through Overview / Design Workflow / Goals first. Proper-name display keeps the dispatch table internally consistent; bare "Stories" loses the anchor prefix that every other row carries.

# BRIEF

*(Maintainer note — what belongs in this spec and what doesn't.)*

- **Inclusion test + boundary:** content belongs only if it specifies the SHAPE of `{NAME} PRD.md` (location, required sections it must carry, fields it must declare, how stories are surfaced from sibling docs, how its lifecycle interacts with `/ask` and `{NAME} Status.md`). Technical decisions, principles, and implementation route to [[FCT Decisions]] / [[FCT Ruleset]] / [[FCT Architecture]] — the body already says PRDs are not that. This is not a PRD instance or a product-management essay: worked examples are cited by wiki-link ([[HBR PRD]]); one-off rationale lives in a rule's **Why** block, not in narrative.
- **Two co-located zones — keep aligned:** the facet-spec prose and the embedded `# RULESET R-prd` must agree; when a section-order rule, naming convention, or location prescription changes above, update the matching `### RULE R-prd-NN` (and its **Check pattern** / **Why**) in the same edit. Rule numbering is monotonic-forever — `R-prd-NN` IDs are never recycled; renumbering silently re-points every existing `R-prd-NN` cross-reference (including rule-side `implements D<N>` back-links and docs citing a rule by id).
- **The `## Standard section order` table is the spine** — its row order is what `R-prd-04` enforces; don't reorder rows for stylistic reasons (downstream readers and the audit script both depend on the declared sequence).
- **Cross-refs to keep live on edit:** [[FCT Stories]], [[FCT Decisions]], [[FCT Architecture]], [[FCT Testing]], [[FCT Status]], [[DSC ask-format]], [[DSC progressive-disclosure]], [[HBR PRD]] — if any is renamed, propagate here the same commit.
