---
description: "facet spec for user stories as first-class siblings of a PRD — inline-bullet form for small PRDs, extracted-folder form for large ones"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Stories](hook://p/FCT%20Stories)

# FCT Stories
**Audited examples:** [[CAE Stories]], [[US-CAE-1 — Schedule a Task]], [[US-CAE-3 — Retry Failed Tasks]], [[Forum Stories]], [[HBR PRD User Stories]]

Facet spec for the user-stories surface of a PRD — defines the inline-bullet form for small PRDs and the extracted-folder form (`{NAME} PRD/` with per-story files indexed by `{NAME} Stories.md`) for PRDs whose stories outgrow a single sentence.

**Related:** [[FCT PRD]],  [[FCT Testing]],  [[FCT Features]],  [[FCT Design]]
**Examples:** [[HBR PRD\|inline-stories (single-file form)]],  [[CAE Stories\|folder-form dispatch index (extracted stories)]]

**TLDR** — Stories are part of the PRD. Small PRDs keep stories inline as bullets under `## User Stories`; large PRDs extract them to `{NAME} PRD/` folder form with a `{NAME} Stories.md` dispatch index and per-story `US-<RID>-<N> — <Title>.md` files. The two forms are mutually exclusive. **Cardinality: many** — a PRD in folder form can have any number of story files. The embedded `R-stories` ruleset enforces folder shape, naming, dispatch table structure, and bidirectional linking.

The Stories facet specifies the format for **user stories as first-class siblings** of the PRD. When a PRD grows enough that its user stories warrant their own scrollable pages (multi-paragraph rationale, acceptance criteria, mockups, decision history), the PRD migrates from single-file form to **folder form** — `{NAME} PRD/` — and stories live as siblings indexed by `{NAME} Stories.md`. Small PRDs whose stories compress to a single bullet each keep the inline `## User Stories` H2 inside `{NAME} PRD.md` and never need this facet.

Stories are **part of the PRD**, not a separate design phase. Capturing them is an explicit step in `/design prd` (per the design sub-skill), and every story carries a wiki-link back to the PRD it serves. The Stories facet exists so the user-story shape, naming, and index format are unambiguous and auditable.

## Two forms — single-file PRD (inline stories) and folder PRD (extracted stories)

### Single-file form (default for small PRDs)

```
{NAME} Design/{NAME} PRD.md         ← PRD with `## User Stories` H2 listing stories inline
```

Stories live under `## User Stories` inside the PRD. Two inline shapes are valid, smallest first:

- **Compact bullets** — one bullet per story, one sentence each. Right when a one-line description conveys everything a downstream reader needs.
- **Inline `### US-<RID>-N` subsections** — each story gets a short `### US-<RID>-N — <Title>` H3 carrying the canonical `As a … I want … so that …` sentence plus a single `**Acceptance:**` line. Optionally fronted by a compact index table grouping the stories (e.g. by pipeline stage). This is the right inline shape once stories deserve an explicit identifier and acceptance line but still don't warrant their own scrollable pages. The maximal worked example ([[HBR PRD]]) uses exactly this shape — US-HBR-1..5 grouped Ingest / Serve / Operate.

Either way the stories stay **inside `{NAME} PRD.md`** — no separate Stories facet file is created. This is the right shape for most PRDs.

### Folder form (when stories grow)

```
{NAME} Design/{NAME} PRD/                          ← PRD becomes an anchor-folder
├── .anchor                                        ← marker (optional)
├── {NAME} PRD.md                                  ← main PRD content (anchor file)
├── {NAME} Stories.md                              ← stories dispatch index (NOT an anchor file)
├── US-<RID>-1 — <Story Title>.md                  ← individual story files
├── US-<RID>-2 — <Story Title>.md
└── ...
```

**Why folder form:** when a story needs multi-paragraph rationale, acceptance criteria spelled out, a mockup, a decision history, or its own embedded RULES — the inline-bullet form constrains the story to a single sentence, and the PRD becomes either thin (story compressed unfairly) or bloated (story unfolded inline, drowning the PRD's other sections).

**Migration is one-way:** once stories are extracted to folder form, they stay extracted. Mixing inline-bullet stories with extracted-file stories in the same PRD is forbidden — pick one shape and use it consistently.

**On `{NAME} Stories.md` not being an anchor file:** its filename is `{NAME} Stories` but the parent folder is `{NAME} PRD/`. Per anchor-file convention, the anchor file's basename must match its folder's basename — only `{NAME} PRD.md` qualifies. `{NAME} Stories.md` is a regular dispatch page that happens to live in the PRD folder.

## Location

`{NAME} Design/{NAME} PRD/{NAME} Stories.md` — directly inside the PRD's anchor folder, alongside the PRD anchor file and the story files.

## `{NAME} Stories.md` index shape

Body-only — no YAML frontmatter. The Stories index is **not an anchor** (the PRD anchor file `{NAME} PRD.md` roots the folder), so per [[FCT Doc Structure]] `R-doc-structure-02` it carries **no breadcrumb-masthead dispatch table** — its story-list table is a permitted **specialized content table** (an index), not a dispatch table. Required elements, top to bottom:

- **H1** — `# {NAME} Stories`.
- **Summary line** — one-line gist of the stories surface, directly under the H1.
- **Stories index table** — a header row (`Story | Description`), then one row per story: column 1 is the `[[US-{RID}-N — <Title>]]` wiki-link, column 2 is the one-line summary. Optionally interleave bold role/pipeline group rows (e.g. `**Ingest**`). No breadcrumb row.
- **`## See also`** — links to `[[{NAME} PRD]]` (parent) and `[[FCT Stories]]` (this facet spec).

See the audited live instance [[CAE Stories]] for the rendered form, and [[Forum Stories]] for the role-grouped variant.

The table is the file's load-bearing content — a reader scanning Stories.md sees every story name and its one-line gist in one screen. The story files themselves carry the full content.

**Row ordering:** by `US-<RID>-N` ascending (monotonic-forever numbering — see § Naming convention). New stories append at the bottom; never re-number, never re-order.

## Story file shape

Each `US-<RID>-N — <Title>.md` file is body-only. Standard structure, top to bottom:

- **H1** — `# US-<RID>-<N> — <Title>` (matches the filename exactly — R-stories-07).
- **`description::` line** — one-line summary identical to the row in `{NAME} Stories.md`.
- **NO dispatch table.** A story file is **not an anchor** — per [[FCT Doc Structure]] `R-doc-structure-02` it MUST NOT carry a breadcrumb-masthead dispatch table. Back-links to `[[{NAME} PRD]]` (parent), `[[{NAME} Stories]]` (sibling index), and `[[FCT Stories]]` (facet spec) live in the `## Related` section at the bottom, not in a top table.
- **`## As a <role>, I want <goal> so that <reason>`** — the canonical user-story sentence (required — R-stories-11). One line. Everything below is recommended but optional.
- **`## Why`** — 2-4 paragraphs: what the user is trying to accomplish, why it matters, what's broken without this.
- **`## Acceptance criteria`** — specific observable outcomes.
- **`## Edge cases`** — unusual conditions and failure modes.
- **`## Related`** — peer stories, implementing feature docs, architecture docs this story exercises.

See the audited live instances [[US-CAE-1 — Schedule a Task]] and [[US-CAE-3 — Retry Failed Tasks]] for the rendered form.

**Required sections:** H1 + `## As a ...` (the canonical story sentence). Everything else is recommended but optional — a thin story file with just the canonical sentence is valid for a story that doesn't yet have unfolded rationale. (No dispatch table — see R-stories-12 / [[FCT Doc Structure]] R-doc-structure-02.)

## Naming convention

- **Story identifier:** `US-<RID>-<N>` — where `<RID>` is the anchor's RID (e.g., `MUX`, `CAE`, `DKT`) and `<N>` is a monotonic-forever integer, never recycled. Zero-padding optional but encouraged once the count crosses 10 (`US-MUX-01` ... `US-MUX-99`).
- **Story file:** `US-<RID>-<N> — <Title>.md` — identifier + em-dash + short title. Title is 3-7 words capturing the story's gist; reads as a noun phrase.
- **Title may evolve** without renaming the file — the file's load-bearing identifier is `US-<RID>-<N>`. If the title needs a big change, rename the file but keep the same `<N>`.

## Wiki-link conventions

- **From PRD body to stories:** `[[US-{RID}-{N}|<Title>]]` — explicit deep-link in PRD prose.
- **From features to stories:** every feature doc that implements a story carries a `Realizes:` line pointing at one or more `[[US-{RID}-{N}]]` identifiers.
- **From tests to stories:** e2e tests in `{NAME} Testing.md` reference the user story they exercise — `Exercises (User Story): US-{RID}-{N}: <Title>`. (Already specified in [[FCT Testing]].)

This bidirectional linking is what makes `/audit stories` (future) useful: walking from stories → features → tests catches stories with no implementing feature, features with no story rationale, e2e tests for missing stories, etc.

## Trait applicability

Any anchor with a PRD. Activated via [[FCT Design]] facet (the `{NAME} Design/` folder). Trait-specific story-form variations (Paper / Topic / Simple) land alongside those traits.

## When to use which form

A progression of increasing weight — adopt the lightest form that fits:

- **Compact bullets (default).** One-sentence bullets under `## User Stories` in `{NAME} PRD.md`. The right shape for most PRDs.
- **Inline `### US-<RID>-N` subsections** when stories deserve a stable identifier and an explicit acceptance line but still fit comfortably inside the PRD. Each story is a short H3 with the canonical sentence + one `**Acceptance:**` line, optionally fronted by a grouping index table (see [[HBR PRD]]).
- **Folder form (extracted stories) when ≥ 1 story qualifies as "needs its own page":** acceptance criteria more than 3 bullets, multi-paragraph rationale, mockups embedded, decision-history needed, story spawns embedded RULES. Migration extracts ALL stories — not just the heavy ones — for consistency.
- **Never mix inline stories and an extracted `{NAME} Stories.md` in the same PRD.** Inline (either inline shape) and folder form are mutually exclusive — pick one per PRD.

## Audit

`/audit stories` (future) would flag the rules in `R-stories` below — folder shape, naming, bidirectional links, etc. — plus cross-facet integrity (story without implementing feature, e2e test for missing story, etc.).

## See also

- [[FCT PRD]] — parent facet; references this one as the "stories sub-facet" when folder form is used
- [[FCT Testing]] — sibling Design facet; e2e tests reference user stories by `US-<RID>-<N>`
- [[FCT Features]] — feature docs carry a `Realizes:` line linking back to the stories they implement
- [[design-prd]] — authoring sub-skill; capturing user stories is an explicit step in PRD design
- [[CAE PRD]] — worked example (currently single-file form; will migrate to folder form when CAE stories grow)

# RULESET R-stories
include::
where:: file:{ANCHOR}/**/{NAME} Stories.md, {ANCHOR}/**/US-*.md
description:: Structural rules for the {NAME} Stories facet — folder shape, story file naming, dispatch table, bidirectional linking.

Embedded ruleset for the Stories facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella. All rules below authored in the new `<H> RULE R-<slug>-NN` sentinel form per CAB Rules.

### RULE R-stories-01 — Folder form lives at `{NAME} Design/{NAME} PRD/` (checked)

When the PRD uses folder form (extracted stories), it lives at `{NAME} Design/{NAME} PRD/` — anchor-folder with the PRD anchor file inside. Single-file PRDs stay at `{NAME} Design/{NAME} PRD.md` and do not use this facet.

**Check pattern:** if `{anchor}/{NAME} Design/{NAME} PRD/` is a directory, then `{NAME} PRD.md` exists inside it AND no `{NAME} Design/{NAME} PRD.md` file exists in the parent (no dual-form).

**Why:** the form is a load-bearing structural choice; mixing or having both forms simultaneously breaks `/design prd`'s detection logic.

### RULE R-stories-02 — `{NAME} Stories.md` is the stories index (checked)

When PRD is in folder form, a `{NAME} Stories.md` file exists inside `{NAME} PRD/`. Its H1 is `# {NAME} Stories`. It is an **index** (a specialized content table), not an anchor — it carries no breadcrumb-masthead dispatch table (see R-stories-12).

**Check pattern:** `ls "{anchor}/{NAME} Design/{NAME} PRD/{NAME} Stories.md"` exists; first non-blank line is `# {NAME} Stories`.

**Why:** the stories index is the surface readers reach for to see "what user stories does this product serve?" Without it, story files are an unbrowsable folder listing.

### RULE R-stories-03 — Story files match `US-<RID>-<N> — <Title>.md` (sampled)

Every story file's name matches the pattern `^US-{RID}-\d+\s+—\s+.+\.md$` where `{RID}` is the anchor's RID.

**Check pattern:** enumerate non-dispatch files in `{NAME} PRD/`; assert each matches the pattern.

**Why:** the `US-<RID>-<N>` identifier is the load-bearing handle used by features (`Realizes: US-<RID>-<N>`) and tests (`Exercises: US-<RID>-<N>`). Off-pattern names break those references.

### RULE R-stories-04 — `<N>` is monotonic-forever (stated)

Story numbers are monotonic-forever within the anchor — never recycled, never re-ordered. A retired story keeps its number; new stories append at the next unused integer.

**Check pattern:** git history — assert no rename collapses two `US-<RID>-<N>` numbers; assert no story file with number `<N>` is followed by a different story file with the same number after a rename.

**Why:** stable identifiers across feature docs, e2e tests, decision docs, and external references. Recycling a number silently breaks every downstream link.

### RULE R-stories-05 — Stories index table has Story + Description columns (checked)

The `{NAME} Stories.md` body contains a markdown table with at least two columns: a Story column (wiki-link to the story file) and a Description column (one-line summary). This index table is a permitted specialized content table (not a dispatch table).

**Check pattern:** parse the first markdown table after the H1; assert two columns; assert the story rows' column-1 entries are wiki-links matching `\[\[US-{RID}-\d+` (ignoring a `Story | Description` header row and any bold group rows).

**Why:** the table IS the index — without it, the index file is just a heading with no machine-readable list of stories.

### RULE R-stories-06 — Each story file links back to its PRD (sampled)

Every story file's body contains a wiki-link to `[[{NAME} PRD]]` — in its `## Related` section (NOT in a top-of-doc dispatch table, which story files must not have — see R-stories-12).

**Check pattern:** grep each story file for `\[\[{NAME} PRD\]\]`.

**Why:** bidirectional linking is what makes the audit walk feasible (PRD → stories → features → tests and back). One-way links erode discoverability.

### RULE R-stories-07 — Story file's H1 matches its identifier (checked)

The H1 of `US-<RID>-<N> — <Title>.md` is exactly `# US-<RID>-<N> — <Title>` (matching the filename).

**Check pattern:** for each story file, first non-blank line is `# ` + filename basename without `.md`.

**Why:** the H1 is the canonical display form; filename drift relative to H1 produces broken back-references when a tool quotes the H1.

### RULE R-stories-08 — Single-file PRDs do not have a `{NAME} Stories.md` (checked)

A `{NAME} Stories.md` file exists ONLY when the PRD is in folder form. Single-file PRDs keep stories inline as bullets under `## User Stories`.

**Check pattern:** if `{NAME} Design/{NAME} PRD.md` is a single file (no `{NAME} PRD/` folder), then no `{NAME} Stories.md` exists anywhere under `{NAME} Design/`.

**Why:** prevents the dual-form failure mode where a stories file lingers after a stories-extraction was rolled back.

### RULE R-stories-09 — Stories index links to its parent PRD (checked)

The `{NAME} Stories.md` index page contains a wiki-link to `[[{NAME} PRD]]` in its `## See also` section (or equivalent).

**Check pattern:** grep `{NAME} Stories.md` for `\[\[{NAME} PRD\]\]`.

**Why:** as with story → PRD links — the index is reachable from the PRD, but readers landing on Stories.md from elsewhere need the upward pointer.

### RULE R-stories-10 — Story / index links the facet spec as `[[FCT Stories]]` (stated)

Where a story file or the `{NAME} Stories.md` dispatch references the governing facet spec, it links `[[FCT Stories]]` — the current facet name. The legacy `[[CAB Stories]]` form is stale and must be rewritten on touch.

**Check pattern:** grep story files + `{NAME} Stories.md` for `\[\[CAB Stories\]\]`; any hit is a violation (should be `[[FCT Stories]]`).

**Why:** the facet was renamed CAB → FCT; dangling `[[CAB Stories]]` links resolve to nothing and break the audit walk from instance back to spec.

### RULE R-stories-11 — Folder-form story files carry the canonical `As a …` sentence (sampled)

Every `US-<RID>-N — <Title>.md` file contains the canonical user-story sentence in the form `As a <role>, I want <goal> so that <reason>` — typically as an H2 (`## As a …`) or the first body line. A story file without it is a stub, not a story.

**Check pattern:** for each story file, grep for `(?i)^#*\s*As an?\s+.+\bI want\b.+\bso that\b`.

**Why:** the `As a/I want/so that` clause is the irreducible content of a user story; everything else (Why, acceptance, edges) is elaboration. A file missing it isn't a valid Stories instance.

### RULE R-stories-12 — Story files and the index carry no dispatch table (checked)
check:: no_dispatch_table

Neither a `US-<RID>-<N> — <Title>.md` story file nor the `{NAME} Stories.md` index is an anchor, so per [[FCT Doc Structure]] `R-doc-structure-02` neither may carry a breadcrumb-masthead **dispatch table**. Story files put parent/sibling back-links in `## Related`; the index's story-list table is a permitted specialized content table (a header row plus story rows), not a dispatch table.

**Check pattern:** for each story file and `{NAME} Stories.md`, assert NO line matches the dispatch-masthead pattern `^\| -\[\[.+\]\]- \|`.

**Why:** stories are short, non-anchor documents; a breadcrumb masthead falsely implies they root a subtree and pushes the one sentence that matters below the fold. This rule is what makes a `US-<RID>-<N>` file (or a Stories index) with a masthead fail — the failure the cleanup of 2026-06-14 corrected.

# BRIEF

- **This file is the facet spec for user stories under a PRD** — authoritative for both the inline-bullet shape (small PRDs) and the extracted folder shape (`{NAME} PRD/` + `{NAME} Stories.md` + per-story files). Cited by [[FCT PRD]], [[FCT Testing]], [[FCT Features]], and [[design-prd]].
- **NOT a catalog of actual stories** and NOT a place to inline anchor-specific story content — worked examples belong in `[[CAE PRD]]`-style anchors, not here. Keep the body abstract and shape-focused.
- **Inclusion test for new content:** a rule, shape, or convention belongs here only if it governs the *structure* of stories or the `{NAME} Stories.md` dispatch across all anchors. Trait-specific variations (Paper / Topic / Simple) live with those traits; PRD-wide rules live in [[FCT PRD]]; cross-facet integrity (story ↔ feature ↔ test) gets *referenced* here but defined in the respective facet specs.
- **The embedded `RULESET R-stories`** is the load-bearing audit surface — rule numbers (R-stories-01..12) are referenced externally and must remain monotonic and stable; never renumber, never recycle a retired rule's number. Its `where::` selects the Stories-facet files only — `{NAME} Stories.md` + `US-*.md` — NOT the PRD (the PRD is governed by [[FCT PRD]]).
- **Inline form has two shapes** — compact one-sentence bullets, or `### US-<RID>-N` subsections with an `**Acceptance:**` line ([[HBR PRD]] uses the latter). Both stay inside `{NAME} PRD.md`. Folder form is the third, heaviest shape.
- **Inline and folder form are mutually exclusive** — the "never mix inline stories with an extracted `{NAME} Stories.md`" constraint (and R-stories-01 / R-stories-08 that enforce it) is structurally load-bearing for `/design prd` detection logic; do NOT introduce a hybrid form without coordinating updates across [[FCT PRD]] and [[design-prd]].
- **`US-<RID>-<N>` is the load-bearing handle** for cross-facet linking (features `Realizes:`, tests `Exercises:`) — any change to the identifier shape ripples through [[FCT Features]] and [[FCT Testing]] and must update those specs in the same edit.
- **Don't pad the body with rationale** that belongs in the ruleset Why fields — each R-stories-NN already carries its own Why; restating it in the prose duplicates content and creates drift.
