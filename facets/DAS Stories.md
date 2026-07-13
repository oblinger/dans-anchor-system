---
description: "facet spec for user stories as first-class siblings of a PRD — inline-bullet form for small PRDs, extracted-folder form for large ones"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Stories](hook://p/DAS%20Stories)
# FCT Stories
**Audited examples:** [[FEX Stories]], [[DAS US-CAE-1 — Schedule a Task]], [[DAS US-CAE-3 — Retry Failed Tasks]], [[Forum Stories]], [[HBR PRD User Stories]]

| Table of Contents |  |
|---|---|
| [[#Two forms — single-file PRD (inline stories) and folder PRD (extracted stories)]] |  |
| [[#Location]] |  |
| [[#`{slug} Stories.md` index shape]] |  |
| [[#Story file shape]] |  |
| [[#Naming convention]] |  |
| [[#Wiki-link conventions]] |  |
| [[#Trait applicability]] |  |
| [[#When to use which form]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

Facet spec for the user-stories surface of a PRD — defines the inline-bullet form for small PRDs and the extracted-folder form (`{slug} PRD/` with per-story files indexed by `{slug} Stories.md`) for PRDs whose stories outgrow a single sentence.

**Related:** [[DAS PRD]],  [[DAS Testing]],  [[DAS Features]],  [[DAS Design Folder]]
**Examples:** [[HBR PRD\|inline-stories (single-file form)]],  [[FEX Stories\|folder-form dispatch index (extracted stories)]]

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
- **`## See also`** — links to `[[{slug} PRD]]` (parent) and `~~[[FCT Stories]]~~` (this facet spec).

See the audited live instance [[FEX Stories]] for the rendered form, and [[Forum Stories]] for the role-grouped variant.

The table is the file's load-bearing content — a reader scanning Stories.md sees every story name and its one-line gist in one screen. The story files themselves carry the full content.

**Row ordering:** by `US-<slug>-N` ascending (monotonic-forever numbering — see § Naming convention). New stories append at the bottom; never re-number, never re-order.

## Story file shape

Each `US-<slug>-N — <Title>.md` file is body-only. Standard structure, top to bottom:

- **H1** — `# US-<slug>-<N> — <Title>` (matches the filename exactly — R-stories-07).
- **`description::` line** — one-line summary identical to the row in `{slug} Stories.md`.
- **NO dispatch table.** A story file is **not an anchor** — per [[DAS Doc Structure]] `R-doc-structure-02` it MUST NOT carry a breadcrumb-masthead dispatch table. Back-links to `[[{slug} PRD]]` (parent), `[[{slug} Stories]]` (sibling index), and `~~[[FCT Stories]]~~` (facet spec) live in the `## Related` section at the bottom, not in a top table.
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

# RULESET R-stories
include::
where:: `file:{anchor}/**/{slug} Stories.md, {anchor}/**/US-*.md`
description:: Structural rules for the {slug} Stories facet — folder shape, story file naming, dispatch table, bidirectional linking.

Embedded ruleset for the Stories facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella. All rules below authored in the new `<H> RULE R-<slug>-NN` sentinel form per CAB Rules.

### RULE R-stories-01 — Folder form lives at `{slug} Design/{slug} PRD/` (checked)

When the PRD uses folder form (extracted stories), it lives at `{slug} Design/{slug} PRD/` — anchor-folder with the PRD anchor file inside. Single-file PRDs stay at `{slug} Design/{slug} PRD.md` and do not use this facet.

**Check pattern:** if `{anchor}/{slug} Design/{slug} PRD/` is a directory, then `{slug} PRD.md` exists inside it AND no `{slug} Design/{slug} PRD.md` file exists in the parent (no dual-form).

**Why:** the form is a load-bearing structural choice; mixing or having both forms simultaneously breaks `/design prd`'s detection logic.

### RULE R-stories-02 — `{slug} Stories.md` is the stories index (checked)

When PRD is in folder form, a `{slug} Stories.md` file exists inside `{slug} PRD/`. Its H1 is `# {slug} Stories`. It is an **index** (a specialized content table), not an anchor — it carries no breadcrumb-masthead dispatch table (see R-stories-12).

**Check pattern:** `ls "{anchor}/{slug} Design/{slug} PRD/{slug} Stories.md"` exists; first non-blank line is `# {slug} Stories`.

**Why:** the stories index is the surface readers reach for to see "what user stories does this product serve?" Without it, story files are an unbrowsable folder listing.

### RULE R-stories-03 — Story files match `US-<slug>-<N> — <Title>.md` (sampled)

Every story file's name matches the pattern `^US-{slug}-\d+\s+—\s+.+\.md$` where `{slug}` is the anchor's slug.

**Check pattern:** enumerate non-dispatch files in `{slug} PRD/`; assert each matches the pattern.

**Why:** the `US-<slug>-<N>` identifier is the load-bearing handle used by features (`Realizes: US-<slug>-<N>`) and tests (`Exercises: US-<slug>-<N>`). Off-pattern names break those references.

### RULE R-stories-04 — `<N>` is monotonic-forever (stated)

Story numbers are monotonic-forever within the anchor — never recycled, never re-ordered. A retired story keeps its number; new stories append at the next unused integer.

**Check pattern:** git history — assert no rename collapses two `US-<slug>-<N>` numbers; assert no story file with number `<N>` is followed by a different story file with the same number after a rename.

**Why:** stable identifiers across feature docs, e2e tests, decision docs, and external references. Recycling a number silently breaks every downstream link.

### RULE R-stories-05 — Stories index table has Story + Description columns (checked)

The `{slug} Stories.md` body contains a markdown table with at least two columns: a Story column (wiki-link to the story file) and a Description column (one-line summary). This index table is a permitted specialized content table (not a dispatch table).

**Check pattern:** parse the first markdown table after the H1; assert two columns; assert the story rows' column-1 entries are wiki-links matching `\[\[US-{slug}-\d+` (ignoring a `Story | Description` header row and any bold group rows).

**Why:** the table IS the index — without it, the index file is just a heading with no machine-readable list of stories.

### RULE R-stories-06 — Each story file links back to its PRD (sampled)

Every story file's body contains a wiki-link to `[[{slug} PRD]]` — in its `## Related` section (NOT in a top-of-doc dispatch table, which story files must not have — see R-stories-12).

**Check pattern:** grep each story file for `\[\[{slug} PRD\]\]`.

**Why:** bidirectional linking is what makes the audit walk feasible (PRD → stories → features → tests and back). One-way links erode discoverability.

### RULE R-stories-07 — Story file's H1 matches its identifier (checked)

The H1 of `US-<slug>-<N> — <Title>.md` is exactly `# US-<slug>-<N> — <Title>` (matching the filename).

**Check pattern:** for each story file, first non-blank line is `# ` + filename basename without `.md`.

**Why:** the H1 is the canonical display form; filename drift relative to H1 produces broken back-references when a tool quotes the H1.

### RULE R-stories-08 — Single-file PRDs do not have a `{slug} Stories.md` (checked)

A `{slug} Stories.md` file exists ONLY when the PRD is in folder form. Single-file PRDs keep stories inline as bullets under `## User Stories`.

**Check pattern:** if `{slug} Design/{slug} PRD.md` is a single file (no `{slug} PRD/` folder), then no `{slug} Stories.md` exists anywhere under `{slug} Design/`.

**Why:** prevents the dual-form failure mode where a stories file lingers after a stories-extraction was rolled back.

### RULE R-stories-09 — Stories index links to its parent PRD (checked)

The `{slug} Stories.md` index page contains a wiki-link to `[[{slug} PRD]]` in its `## See also` section (or equivalent).

**Check pattern:** grep `{slug} Stories.md` for `\[\[{slug} PRD\]\]`.

**Why:** as with story → PRD links — the index is reachable from the PRD, but readers landing on Stories.md from elsewhere need the upward pointer.

### RULE R-stories-10 — Story / index links the facet spec as `~~[[FCT Stories]]~~` (stated)

Where a story file or the `{slug} Stories.md` dispatch references the governing facet spec, it links `~~[[FCT Stories]]~~` — the current facet name. The legacy `[[DAS Stories]]` form is stale and must be rewritten on touch.

**Check pattern:** grep story files + `{slug} Stories.md` for `\[\[CAB Stories\]\]`; any hit is a violation (should be `~~[[FCT Stories]]~~`).

**Why:** the facet was renamed CAB → FCT; dangling `[[DAS Stories]]` links resolve to nothing and break the audit walk from instance back to spec.

### RULE R-stories-11 — Folder-form story files carry the canonical `As a …` sentence (sampled)

Every `US-<slug>-N — <Title>.md` file contains the canonical user-story sentence in the form `As a <role>, I want <goal> so that <reason>` — typically as an H2 (`## As a …`) or the first body line. A story file without it is a stub, not a story.

**Check pattern:** for each story file, grep for `(?i)^#*\s*As an?\s+.+\bI want\b.+\bso that\b`.

**Why:** the `As a/I want/so that` clause is the irreducible content of a user story; everything else (Why, acceptance, edges) is elaboration. A file missing it isn't a valid Stories instance.

### RULE R-stories-12 — Story files and the index carry no dispatch table (checked)
check:: no_dispatch_table

Neither a `US-<slug>-<N> — <Title>.md` story file nor the `{slug} Stories.md` index is an anchor, so per [[DAS Doc Structure]] `R-doc-structure-02` neither may carry a breadcrumb-masthead **dispatch table**. Story files put parent/sibling back-links in `## Related`; the index's story-list table is a permitted specialized content table (a header row plus story rows), not a dispatch table.

**Check pattern:** for each story file and `{slug} Stories.md`, assert NO line matches the dispatch-masthead pattern `^\| -\[\[.+\]\]- \|`.

**Why:** stories are short, non-anchor documents; a breadcrumb masthead falsely implies they root a subtree and pushes the one sentence that matters below the fold. This rule is what makes a `US-<slug>-<N>` file (or a Stories index) with a masthead fail — the failure the cleanup of 2026-06-14 corrected.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec and its Why fields are the body + `RULESET R-stories` above.)*

- **Spec, not a catalog** — keep the body abstract and shape-focused; worked stories belong in per-anchor PRDs ([[HBR PRD]]), never inlined here. Inclusion test: content belongs here only if it governs the *structure* of stories or the `{slug} Stories.md` index across all anchors — trait-specific variations (Paper / Topic / Simple) live with those traits, PRD-wide rules in [[DAS PRD]], and cross-facet integrity (story ↔ feature ↔ test) is *referenced* here but defined in the respective specs.
- **`RULESET R-stories` numbers are externally referenced** — rule numbers (R-stories-01..12) must stay monotonic and stable; never renumber, never recycle a retired number. Its `where::` deliberately selects only the Stories-facet files (`{slug} Stories.md` + `US-*.md`), NOT the PRD (which [[DAS PRD]] governs).
- **Cross-ref coordination:** the inline/folder mutual-exclusivity is load-bearing for `/design prd` detection logic — don't introduce a hybrid form without updating [[DAS PRD]] and [[design-prd]] in the same edit; likewise, any change to the `US-<slug>-<N>` identifier shape (the handle for features `Realizes:` / tests `Exercises:`) must update [[DAS Features]] and [[DAS Testing]] in the same edit.
