---
description: "facet spec this doc follows"
---

| -[[DAS PRD]]- | → [[DAS]] → [[FCT]] → [DAS PRD](hook://p/DAS%20PRD)  |
| --- | --- |
| Related | [[DAS Architecture]],  [[DAS Testing]],  [[DAS Decisions]],  [[DAS Stories]],  [[templates/prd.md\|PRD template]],   |
| Examples | [[HBR PRD\|single-file form]],  [[HBR PRD\|folder form (stories extracted)]],  [[Mini PRD]],   |
| Rules | [[R-prd]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS PRD
Facet spec for `{slug} PRD.md` — the first doc in an anchor's Design folder, defining what the product does (goals, non-goals, user stories) for every downstream design phase to consume.

The PRD (`{slug} PRD.md`) is the **what** of the product — what it does, who it serves, what's in and out of scope, and the user stories that downstream work realizes. It is the first document written during `/design`, and every downstream phase (UX, Architecture, Testing, Roadmap, Features) reads it as authoritative input.

PRDs are deliberately not the place for technical decisions, principles, rules, or implementation detail — those live in [[DAS Decisions]], [[DAS Ruleset]], [[DAS Architecture]], and per-module docs respectively. The PRD's job is to define the contract that lets everything downstream argue from the same shared understanding of what the product is.

## Location

`{slug} Design/{slug} PRD.md` (single-file form) **or** `{slug} Design/{slug} PRD/{slug} PRD.md` (folder form, when user stories migrate to the [[DAS Stories|Stories sub-facet]]).

**File location moved 2026-06-01 per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]]** — legacy path `{slug} Docs/{slug} Plan/{slug} PRD.md` is superseded. Existing legacy locations migrate during normal anchor work.

## Two forms — single-file (default) and folder (when stories extract)

### Single-file form (default)

```
{slug} Design/{slug} PRD.md
```

User stories live inline under `## User Stories` as bullets. Right for most PRDs.

### Folder form (when stories grow to need their own pages)

```
{slug} Design/{slug} PRD/
├── {slug} PRD.md           ← this file, anchor file (matches folder name)
├── {slug} Stories.md       ← stories dispatch index
├── US-<slug>-1 — <Title>.md ← individual story files
└── ...
```

Per [[DAS Stories]]. The PRD's `## User Stories` section then links to `[[{slug} Stories]]` instead of carrying inline bullets. Migration is one-way; mixing inline and extracted stories in the same PRD is forbidden.

## Standard section order

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc | YAML frontmatter (`description:`) → `:>>` breadcrumb glued directly above the H1 → `# {slug} PRD` → one-sentence summary. Single-file PRD carries the breadcrumb (no dispatch table); folder-form PRD is an anchor and carries a dispatch table instead (per R-prd-03 / [[DAS Doc Structure\|R-doc-structure]]). |
| 2 | `## Overview` | One to two paragraphs — what the product *is*, who it's for, why it needs to exist. Reader leaves knowing the shape of the thing. |
| 3 | `## Design Workflow` | Table listing the design phases downstream of this PRD with wiki-links: PRD → Architecture → Testing → Decisions → Track (Roadmap + Features). The sequence may be revisited iteratively as questions surface. |
| 4 | `## Goals` | Concrete, verifiable outcomes — what the product will accomplish. Bulleted; outcome-shaped (not feature-shaped). |
| 5 | `## Non-Goals` | What the product explicitly will NOT do. Each non-goal is one of: (a) deferred to a future version, (b) out of scope by design, (c) constraint from the environment. Keeps scope conversation honest. |
| 6 | `## User Stories` | Either inline bullets (`US-<slug>-<N>` per [[DAS Stories]]) or a wiki-link to `[[{slug} Stories]]` if folder form. Each story is "As a `<role>`, I want `<capability>` so that `<reason>`." |
| 7 | `## Open Questions` (optional) | Pending decisions surfaced via [[DAS ask-format]]. Lives immediately below the H1 as the first H2 (per [[F241 — Questions block below H1 + state-stamped integrity hash\|F241]]) only while pending Qs exist; deletes entirely once all resolve. |
| 8 | `## Resolved` (optional) | Bottom-of-doc archive of resolved questions and decisions, H3 per resolution. Populated as questions resolve; never deleted. |
| 9 | `## See also` (optional) | Links to peer Design facets (Architecture, Testing, Decisions). |

The spine is `Overview → Design Workflow → Goals → Non-Goals → User Stories`. Sections 7-9 appear as needed.

Real instances vary in section *naming* around this spine (e.g. `## Purpose` for Overview, `## Primary Goals`/`## Core Capabilities` for Goals) and some predate the `## Design Workflow` row entirely. The conformant target is the canonical names and order above; older PRDs migrate toward it during normal anchor work rather than being rewritten wholesale.

**Working example:** [[HBR PRD]] — single-file form; three inline stories.

## Preface zone requirements

Per [[DAS progressive-disclosure]] § Per-facet preface requirements:

- **Dispatch table** — **Required**.
- **TLDR** — **Explicitly NOT required**. PRDs are too heterogeneous to compress meaningfully into 3-8 bullets without filler; forcing one degrades the doc. The `## Overview` section serves the grazer-altitude need.
- **Figure** — Optional. A product-shape mockup or context diagram can help on visual products; skip for CLI / library / pure-data projects.

## User stories — naming and lifecycle

- **Identifier:** `US-<slug>-<N>` per [[DAS Stories]] § Naming convention. Monotonic-forever within the anchor; never recycled.
- **Inline shape:** H3 heading `### US-<slug>-<N>: <Title>` followed by the canonical "As a `<role>`, I want `<goal>` so that `<reason>`" sentence on the next line.
- **When stories grow:** migrate to [[DAS Stories]] folder form. The PRD's `## User Stories` section then reads "See [[{slug} Stories]] for the story index" + (optionally) a wiki-list of the top-level stories.

### Dispatch-row pointer to stories — required in both forms

The PRD's top-of-doc dispatch table carries a row pointing at stories. The link target depends on the form, but the **display alias is always `{slug} Stories`** (the proper anchor-prefixed name, matching the convention used by sibling rows like `[[{slug} Architecture]]`, `[[{slug} Testing]]`):

- **Single-file PRD (inline stories):** `[[{slug} PRD#User Stories\|{slug} Stories]]` — section-deep wiki-link into this same doc's `## User Stories` H2, displayed as `{slug} Stories`. The description names the story count: *"three user stories (inline-bullet form per [[DAS Stories]]; US-{slug}-1..N)"*.
- **Folder-form PRD (extracted stories):** `[[{slug} Stories]]` — wiki-link to the sibling dispatch index; display defaults to the page name (`{slug} Stories`). The description names the count: *"N user stories — index at [[{slug} Stories]]"*.

The row is required in both forms so a reader landing on the PRD has a one-click jump to "what does this product DO for users" without scrolling. The proper-name display keeps the row consistent with its peers in the dispatch table. Worked example: [[HBR PRD]] § dispatch table.

## Open questions — handled by `/ask`

PRD discussions surface questions throughout. The PRD does NOT carry a separate `{slug} Open Questions.md` file (legacy pattern, deprecated). Instead:

- **Active questions** live as `## Open Questions` H2 directly below the H1 (the first H2), per [[DAS ask-format]].
- **Resolved questions** move to `## Resolved` at the bottom of the doc when answered. Never deleted.
- **The `/ask --doc` workflow** is the way to add or resolve questions on a PRD; it handles the formatting, the lifecycle transitions, and the Q.md update.

## Status tracking

Design-phase completeness for the PRD is tracked in `{slug} Track/{slug} Status.md` per [[DAS Status]], on the `prd::` line. The PRD file itself does NOT carry a `status::` dataview field — the centralized Status facet is the single source of truth. Legacy per-doc `status::` is acceptable as a fallback when the Status file doesn't exist yet.

## Cardinality

**One per anchor.** An anchor has at most one PRD — the single authoritative statement of what the product is. When user stories grow large enough to extract, they move to [[DAS Stories]] (folder form), but the PRD itself remains one file per anchor.

## Common deviations in real instances

Surveying live PRDs across the vault, these are the recurring drifts from the canonical shape — each maps to a rule below and is a migration target, not an accepted variant:

- **Legacy header form** — `desc::`/`description::` inline instead of YAML frontmatter (`R-prd-02`), or no metadata line at all (e.g. `[[HA Track]] > [[HA PRD]]` breadcrumb-only). *(The `:>>` breadcrumb itself is now required directly above the H1 per `R-prd-03`; the deviation is the missing YAML frontmatter, not the breadcrumb.)*
- **`US-<N>` without the slug** — inline stories numbered `US-1`, `US-2` rather than `US-<slug>-<N>` (`R-prd-05`); collides across anchors.
- **`## Design Constraints` (DC-N)** — architectural/technical constraints living in the PRD instead of [[DAS Decisions]] / [[DAS Ruleset]] (`R-prd-09`).
- **Missing `## Design Workflow`** — older PRDs jump from Overview straight to Goals (`R-prd-04`).
- **No `## User Stories` at all** — stub or library PRDs (e.g. consumer-table-only) that never grew a story section (`R-prd-04`/`R-prd-05`); the Goals serve as a stand-in until stories are authored.

## Trait applicability

Any anchor that has a `{slug} Design/` folder per [[DAS Design Folder]]. Initially supports anchors with code-shaped artifacts; broader applicability (Paper / Topic / Simple traits) covered as those traits land.

## Audit

`/audit prd` (future) would flag the rules captured in `R-prd` below — body-only shape, required-section presence, `US-<slug>-<N>` story numbering, no legacy Open Questions file, etc.

## See also

- [[DAS Stories]] — sub-facet activated when user stories grow beyond inline-bullet form
- [[DAS Architecture]] — peer Design facet (system-architecture story)
- [[DAS Testing]] — peer Design facet (testing strategy + proposed-tests overview)
- [[DAS Decisions]] — peer Design facet (load-bearing decisions citing rules)
- [[DAS Status]] — `{slug} Status.md` carries the PRD's design-phase tier
- [[DAS ask-format]] — open-questions formatting discipline
- [[DAS progressive-disclosure]] — preface-zone requirements
- [[design-prd]] — authoring sub-skill for `/design prd`
- [[HBR PRD]] — worked example (single-file form, three inline stories)

# BRIEF

*(Maintainer note — what belongs in this spec and what doesn't.)*

- **Inclusion test + boundary:** content belongs only if it specifies the SHAPE of `{slug} PRD.md` (location, required sections it must carry, fields it must declare, how stories are surfaced from sibling docs, how its lifecycle interacts with `/ask` and `{slug} Status.md`). Technical decisions, principles, and implementation route to [[DAS Decisions]] / [[DAS Ruleset]] / [[DAS Architecture]] — the body already says PRDs are not that. This is not a PRD instance or a product-management essay: worked examples are cited by wiki-link ([[HBR PRD]]); one-off rationale lives in a rule's **Why** block, not in narrative.
- **Two co-located zones — keep aligned:** the facet-spec prose and the embedded `# RULESET R-prd` must agree; when a section-order rule, naming convention, or location prescription changes above, update the matching `### RULE R-prd-NN` (and its **Check pattern** / **Why**) in the same edit. Rule numbering is monotonic-forever — `R-prd-NN` IDs are never recycled; renumbering silently re-points every existing `R-prd-NN` cross-reference (including rule-side `implements D<N>` back-links and docs citing a rule by id).
- **The `## Standard section order` table is the spine** — its row order is what `R-prd-04` enforces; don't reorder rows for stylistic reasons (downstream readers and the audit script both depend on the declared sequence).
- **Cross-refs to keep live on edit:** [[DAS Stories]], [[DAS Decisions]], [[DAS Architecture]], [[DAS Testing]], [[DAS Status]], [[DAS ask-format]], [[DAS progressive-disclosure]], [[HBR PRD]] — if any is renamed, propagate here the same commit.
