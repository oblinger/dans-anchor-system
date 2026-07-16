---
description: "facet spec for user stories as first-class siblings of a PRD — inline-bullet form for small PRDs, extracted-folder form for large ones"
---

# DAS Stories
Facet spec for the user-stories surface of a PRD — defines the inline-bullet form for small PRDs and the extracted-folder form (`{slug} PRD/` with per-story files indexed by `{slug} Stories.md`) for PRDs whose stories outgrow a single sentence.

| -[[DAS Stories]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Stories](hook://p/DAS%20Stories) |
| --- | --- |
| Related | [[DAS PRD]],  [[DAS Testing]],  [[DAS Features]],  [[DAS Design Folder]],   |
| Examples | [[HBR PRD\|inline-stories (single-file form)]],  [[FEX Stories\|folder-form dispatch index (extracted stories)]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Forum Stories]],  [[HBR PRD User Stories]],   |
| Rules | [[R-stories]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — Stories are part of the PRD. Small PRDs keep stories inline as bullets under `## User Stories`; large PRDs extract them to `{slug} PRD/` folder form with a `{slug} Stories.md` dispatch index and per-story `US-<slug>-<N> — <Title>.md` files. The two forms are mutually exclusive. **Cardinality: many** — a PRD in folder form can have any number of story files. The embedded `R-stories` ruleset enforces folder shape, naming, dispatch table structure, and bidirectional linking.

The Stories facet specifies the format for **user stories as first-class siblings** of the PRD. When a PRD grows enough that its user stories warrant their own scrollable pages (multi-paragraph rationale, acceptance criteria, mockups, decision history), the PRD migrates from single-file form to **folder form** — `{slug} PRD/` — and stories live as siblings indexed by `{slug} Stories.md`. Small PRDs whose stories compress to a single bullet each keep the inline `## User Stories` H2 inside `{slug} PRD.md` and never need this facet.

Stories are **part of the PRD**, not a separate design phase. Capturing them is an explicit step in `/design prd` (per the design sub-skill), and every story carries a wiki-link back to the PRD it serves. The Stories facet exists so the user-story shape, naming, and index format are unambiguous and auditable.

## Two forms — single-file PRD (inline stories) and folder PRD (extracted stories)

### Single-file form (default for small PRDs)

```
{slug} Design/{slug} PRD.md         ← PRD with `## User Stories` H2 listing stories inline
```

Stories live under `## User Stories` inside the PRD. Two inline shapes are valid, smallest first:

- **Compact bullets** — one bullet per story, one sentence each. Right when a one-line description conveys everything a downstream reader needs.
- **Inline `### US-<slug>-N` subsections** — each story gets a short `### US-<slug>-N — <Title>` H3 carrying the canonical `As a … I want … so that …` sentence plus a single `**Acceptance:**` line. Optionally fronted by a compact index table grouping the stories (e.g. by pipeline stage). This is the right inline shape once stories deserve an explicit identifier and acceptance line but still don't warrant their own scrollable pages. The maximal worked example ([[HBR PRD]]) uses exactly this shape — US-HBR-1..5 grouped Ingest / Serve / Operate.

Either way the stories stay **inside `{slug} PRD.md`** — no separate Stories facet file is created. This is the right shape for most PRDs.

### Folder form (when stories grow)

```
{slug} Design/{slug} PRD/                          ← PRD becomes an anchor-folder
├── .anchor                                        ← marker (optional)
├── {slug} PRD.md                                  ← main PRD content (anchor file)
├── {slug} Stories.md                              ← stories dispatch index (NOT an anchor file)
├── US-<slug>-1 — <Story Title>.md                  ← individual story files
├── US-<slug>-2 — <Story Title>.md
└── ...
```

**Why folder form:** when a story needs multi-paragraph rationale, acceptance criteria spelled out, a mockup, a decision history, or its own embedded RULES — the inline-bullet form constrains the story to a single sentence, and the PRD becomes either thin (story compressed unfairly) or bloated (story unfolded inline, drowning the PRD's other sections).

**Migration is one-way:** once stories are extracted to folder form, they stay extracted. Mixing inline-bullet stories with extracted-file stories in the same PRD is forbidden — pick one shape and use it consistently.

**On `{slug} Stories.md` not being an anchor file:** its filename is `{slug} Stories` but the parent folder is `{slug} PRD/`. Per anchor-file convention, the anchor file's basename must match its folder's basename — only `{slug} PRD.md` qualifies. `{slug} Stories.md` is a regular dispatch page that happens to live in the PRD folder.

## Location

`{slug} Design/{slug} PRD/{slug} Stories.md` — directly inside the PRD's anchor folder, alongside the PRD anchor file and the story files.

## `{slug} Stories.md` index shape

Body-only — no YAML frontmatter. The Stories index is **not an anchor** (the PRD anchor file `{slug} PRD.md` roots the folder), so per [[DAS Doc Structure]] `R-doc-structure-02` it carries **no breadcrumb-masthead dispatch table** — its story-list table is a permitted **specialized content table** (an index), not a dispatch table. Required elements, top to bottom:

- **H1** — `# {slug} Stories`.
- **Summary line** — one-line gist of the stories surface, directly under the H1.
- **Stories index table** — a header row (`Story | Description`), then one row per story: column 1 is the `[[US-{slug}-N — <Title>]]` wiki-link, column 2 is the one-line summary. Optionally interleave bold role/pipeline group rows (e.g. `**Ingest**`). No breadcrumb row.
- **`## See also`** — links to `[[{slug} PRD]]` (parent) and `~~[[DAS Stories]]~~` (this facet spec).

See the audited live instance [[FEX Stories]] for the rendered form, and [[Forum Stories]] for the role-grouped variant.

The table is the file's load-bearing content — a reader scanning Stories.md sees every story name and its one-line gist in one screen. The story files themselves carry the full content.

**Row ordering:** by `US-<slug>-N` ascending (monotonic-forever numbering — see § Naming convention). New stories append at the bottom; never re-number, never re-order.

## Story file shape

Each `US-<slug>-N — <Title>.md` file is body-only. Standard structure, top to bottom:

- **H1** — `# US-<slug>-<N> — <Title>` (matches the filename exactly — R-stories-07).
- **`description::` line** — one-line summary identical to the row in `{slug} Stories.md`.
- **NO dispatch table.** A story file is **not an anchor** — per [[DAS Doc Structure]] `R-doc-structure-02` it MUST NOT carry a breadcrumb-masthead dispatch table. Back-links to `[[{slug} PRD]]` (parent), `[[{slug} Stories]]` (sibling index), and `~~[[DAS Stories]]~~` (facet spec) live in the `## Related` section at the bottom, not in a top table.
- **`## As a <role>, I want <goal> so that <reason>`** — the canonical user-story sentence (required — R-stories-11). One line. Everything below is recommended but optional.
- **`## Why`** — 2-4 paragraphs: what the user is trying to accomplish, why it matters, what's broken without this.
- **`## Acceptance criteria`** — specific observable outcomes.
- **`## Edge cases`** — unusual conditions and failure modes.
- **`## Related`** — peer stories, implementing feature docs, architecture docs this story exercises.

See the audited live instances [[DAS US-CAE-1 — Schedule a Task]] and [[DAS US-CAE-3 — Retry Failed Tasks]] for the rendered form.

**Required sections:** H1 + `## As a ...` (the canonical story sentence). Everything else is recommended but optional — a thin story file with just the canonical sentence is valid for a story that doesn't yet have unfolded rationale. (No dispatch table — see R-stories-12 / [[DAS Doc Structure]] R-doc-structure-02.)

## Naming convention

- **Story identifier:** `US-<slug>-<N>` — where `<slug>` is the anchor's slug (e.g., `MUX`, `CAE`, `DKT`) and `<N>` is a monotonic-forever integer, never recycled. Zero-padding optional but encouraged once the count crosses 10 (`US-MUX-01` ... `US-MUX-99`).
- **Story file:** `US-<slug>-<N> — <Title>.md` — identifier + em-dash + short title. Title is 3-7 words capturing the story's gist; reads as a noun phrase.
- **Title may evolve** without renaming the file — the file's load-bearing identifier is `US-<slug>-<N>`. If the title needs a big change, rename the file but keep the same `<N>`.

## Wiki-link conventions

- **From PRD body to stories:** `[[US-{slug}-{N}|<Title>]]` — explicit deep-link in PRD prose.
- **From features to stories:** every feature doc that implements a story carries a `Realizes:` line pointing at one or more `[[US-{slug}-{N}]]` identifiers.
- **From tests to stories:** e2e tests in `{slug} Testing.md` reference the user story they exercise — `Exercises (User Story): US-{slug}-{N}: <Title>`. (Already specified in [[DAS Testing]].)

This bidirectional linking is what makes `/audit stories` (future) useful: walking from stories → features → tests catches stories with no implementing feature, features with no story rationale, e2e tests for missing stories, etc.

## Trait applicability

Any anchor with a PRD. Activated via [[DAS Design Folder]] facet (the `{slug} Design/` folder). Trait-specific story-form variations (Paper / Topic / Simple) land alongside those traits.

## When to use which form

A progression of increasing weight — adopt the lightest form that fits:

- **Compact bullets (default).** One-sentence bullets under `## User Stories` in `{slug} PRD.md`. The right shape for most PRDs.
- **Inline `### US-<slug>-N` subsections** when stories deserve a stable identifier and an explicit acceptance line but still fit comfortably inside the PRD. Each story is a short H3 with the canonical sentence + one `**Acceptance:**` line, optionally fronted by a grouping index table (see [[HBR PRD]]).
- **Folder form (extracted stories) when ≥ 1 story qualifies as "needs its own page":** acceptance criteria more than 3 bullets, multi-paragraph rationale, mockups embedded, decision-history needed, story spawns embedded RULES. Migration extracts ALL stories — not just the heavy ones — for consistency.
- **Never mix inline stories and an extracted `{slug} Stories.md` in the same PRD.** Inline (either inline shape) and folder form are mutually exclusive — pick one per PRD.

## Audit

`/audit stories` (future) would flag the rules in `R-stories` below — folder shape, naming, bidirectional links, etc. — plus cross-facet integrity (story without implementing feature, e2e test for missing story, etc.).

## See also

- [[DAS PRD]] — parent facet; references this one as the "stories sub-facet" when folder form is used
- [[DAS Testing]] — sibling Design facet; e2e tests reference user stories by `US-<slug>-<N>`
- [[DAS Features]] — feature docs carry a `Realizes:` line linking back to the stories they implement
- [[design-prd]] — authoring sub-skill; capturing user stories is an explicit step in PRD design
- [[HBR PRD]] — worked example (currently single-file form; will migrate to folder form when CAE stories grow)

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec and its Why fields are the body + `RULESET R-stories` above.)*

- **Spec, not a catalog** — keep the body abstract and shape-focused; worked stories belong in per-anchor PRDs ([[HBR PRD]]), never inlined here. Inclusion test: content belongs here only if it governs the *structure* of stories or the `{slug} Stories.md` index across all anchors — trait-specific variations (Paper / Topic / Simple) live with those traits, PRD-wide rules in [[DAS PRD]], and cross-facet integrity (story ↔ feature ↔ test) is *referenced* here but defined in the respective specs.
- **`RULESET R-stories` numbers are externally referenced** — rule numbers (R-stories-01..12) must stay monotonic and stable; never renumber, never recycle a retired number. Its `where::` deliberately selects only the Stories-facet files (`{slug} Stories.md` + `US-*.md`), NOT the PRD (which [[DAS PRD]] governs).
- **Cross-ref coordination:** the inline/folder mutual-exclusivity is load-bearing for `/design prd` detection logic — don't introduce a hybrid form without updating [[DAS PRD]] and [[design-prd]] in the same edit; likewise, any change to the `US-<slug>-<N>` identifier shape (the handle for features `Realizes:` / tests `Exercises:`) must update [[DAS Features]] and [[DAS Testing]] in the same edit.
