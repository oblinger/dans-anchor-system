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

### RULE R-stories-10 — Story / index links the facet spec as `~~[[DAS Stories]]~~` (stated)

Where a story file or the `{slug} Stories.md` dispatch references the governing facet spec, it links `~~[[DAS Stories]]~~` — the current facet name. The legacy `[[DAS Stories]]` form is stale and must be rewritten on touch.

**Check pattern:** grep story files + `{slug} Stories.md` for `\[\[CAB Stories\]\]`; any hit is a violation (should be `~~[[DAS Stories]]~~`).

**Why:** the facet spec was renamed (CAB → FCT → DAS); dangling `[[DAS Stories]]` links resolve to nothing and break the audit walk from instance back to spec.

### RULE R-stories-11 — Folder-form story files carry the canonical `As a …` sentence (sampled)

Every `US-<slug>-N — <Title>.md` file contains the canonical user-story sentence in the form `As a <role>, I want <goal> so that <reason>` — typically as an H2 (`## As a …`) or the first body line. A story file without it is a stub, not a story.

**Check pattern:** for each story file, grep for `(?i)^#*\s*As an?\s+.+\bI want\b.+\bso that\b`.

**Why:** the `As a/I want/so that` clause is the irreducible content of a user story; everything else (Why, acceptance, edges) is elaboration. A file missing it isn't a valid Stories instance.

### RULE R-stories-12 — Story files and the index carry no dispatch table (checked)
check:: no_dispatch_table

Neither a `US-<slug>-<N> — <Title>.md` story file nor the `{slug} Stories.md` index is an anchor, so per [[DAS Doc Structure]] `R-doc-structure-02` neither may carry a breadcrumb-masthead **dispatch table**. Story files put parent/sibling back-links in `## Related`; the index's story-list table is a permitted specialized content table (a header row plus story rows), not a dispatch table.

**Check pattern:** for each story file and `{slug} Stories.md`, assert NO line matches the dispatch-masthead pattern `^\| -\[\[.+\]\]- \|`.

**Why:** stories are short, non-anchor documents; a breadcrumb masthead falsely implies they root a subtree and pushes the one sentence that matters below the fold. This rule is what makes a `US-<slug>-<N>` file (or a Stories index) with a masthead fail — the failure the cleanup of 2026-06-14 corrected.

## Adoption

Adopted transitively via [[R-facet]].

## See also

- [[DAS Stories]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
