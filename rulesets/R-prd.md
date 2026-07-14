# RULESET R-prd
include::
where:: `file:{anchor}/**/* PRD.md`
description:: facet spec this doc follows

Embedded ruleset for the PRD facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-prd-01 — Location is `{slug} Design/{slug} PRD.md` or folder form (checked)
check:: file_path_matches_prd_locations

The PRD lives at `{slug} Design/{slug} PRD.md` (single-file form) or `{slug} Design/{slug} PRD/{slug} PRD.md` (folder form). Not under `{slug} Docs/`, not under `{slug} Plan/`, not at the anchor root.

**Check pattern:** path matches one of the two canonical locations.

**Why:** F094 moved Design docs out of the legacy `{slug} Plan/` folder; surfacing stale paths breaks `/design`'s anchor-detection.

### RULE R-prd-02 — Opens with YAML frontmatter carrying `description:` (checked)
check:: frontmatter_has description

`{slug} PRD.md` opens with a `---` YAML frontmatter block carrying a one-line `description:` (the doc metadata — the only thing in the frontmatter).

**Check pattern:** the file begins with a `--- … ---` block; `description:` key present and non-empty.

**Why:** YAML frontmatter is the canonical metadata form across the vault (anchor pages, design docs); the inline `desc::`/`description::` form is deprecated.

### RULE R-prd-03 — Top-matter follows R-doc-structure (breadcrumb-above-H1 for the single-file PRD) (checked)
check:: h1_after_frontmatter

The PRD's top-matter follows [[DAS Doc Structure|R-doc-structure]]-01/-02, which turns on whether the PRD is an anchor:

- **Single-file PRD (the default — a non-anchor member file inside `{slug} Design/`)** carries a `:>>` breadcrumb line **directly above** the H1, with **no blank line** between the breadcrumb and `# {slug} PRD` (per R-doc-structure-01). It carries **no** dispatch table (R-doc-structure-02 — a masthead is only for anchors). The breadcrumb's parent is the `{slug} Design` anchor: `:>> … → [[{slug}]] → [[{slug} Design]]`.
- **Folder-form PRD (`{slug} Design/{slug} PRD/{slug} PRD.md`)** is the anchor file of its own folder, so it carries a **dispatch table** (breadcrumb in the first cell), not a `:>>` line.

Frontmatter (`--- … ---`, metadata only) precedes either form.

**Check pattern:** skip the leading `--- … ---` block; for a single-file PRD the next non-blank line is a `:>>` breadcrumb and the line **immediately** below it is the `# {slug} PRD` H1 (no blank between); for a folder-form PRD the next table is a dispatch masthead. Delegates the breadcrumb-vs-dispatch choice to R-doc-structure.

**Why:** a PRD is a member document inside its anchor, and every non-anchor member document carries its parent up-edge as a `:>>` breadcrumb glued to the H1 (R-doc-structure-01) — the earlier "H1-first, no breadcrumb" form dropped the up-edge. Anchor-ness (single-file vs folder-form), not the doc kind, decides breadcrumb-vs-dispatch, so this rule defers to R-doc-structure rather than restating it.

### RULE R-prd-04 — Required sections present in order (checked)
check:: required_sections_in_order

The PRD contains H2s `## Overview`, `## Design Workflow`, `## Goals`, `## Non-Goals`, `## User Stories` (in that order). Optional H2s (`## Open Questions`, `## Resolved`, `## See also`) may follow.

**Check pattern:** parse H2 headers; assert the five required ones appear in declared order.

**Why:** downstream design phases read the PRD assuming this section spine. Missing sections force the reader to hunt for what they expect to find in a known location.

### RULE R-prd-05 — User stories use `US-<slug>-<N>` numbering (checked)
check:: user_stories_use_rid_numbering

Every user-story H3 (inline form) matches `^### US-{slug}-\d+: .+` where `{slug}` is the anchor's slug. Folder-form PRDs link to `[[{slug} Stories]]` instead of inline H3s and this rule defers to [[R-stories]].

**Check pattern:** for inline-form PRDs, enumerate H3s under `## User Stories`; assert each matches the pattern.

**Why:** `US-<slug>-<N>` is the load-bearing identifier referenced by feature docs (`Realizes: US-<slug>-<N>`), e2e tests (`Exercises: US-<slug>-<N>`), and Stories sub-facet files. Old `US-<N>` form (no slug) collides across anchors and breaks cross-anchor references.

### RULE R-prd-06 — No legacy `{slug} Open Questions.md` file (checked)
check:: no_legacy_open_questions_file

No file named `{slug} Open Questions.md` exists alongside the PRD. Open questions live as `## Open Questions` H2 directly inside the PRD per [[DAS ask-format]].

**Check pattern:** `ls "{slug} Design/{slug} Open Questions.md"` returns no-such-file.

**Why:** the file-based Open Questions pattern was deprecated when `/ask` became the universal asking surface. Linger of the old file produces ambiguity about where to look.

### RULE R-prd-07 — Design Workflow references modern phase names (checked)

The `## Design Workflow` table references `[[{slug} Architecture]]` (not "System Design"), `[[{slug} Testing]]` (not "Testing Strategy"), and `[[{slug} Decisions]]` (not "Principles").

**Check pattern:** parse the Design Workflow table; assert the wiki-link targets are in the modern naming set.

**Why:** F094 (Architecture vs System Design), F113 (Decisions vs Principles), and the 2026-06-10 CAB Testing facet rename (`Testing.md`, not `Testing Strategy.md`) all renamed canonical phase names. References to old names produce broken wiki-links.

### RULE R-prd-08 — Status tracked centrally, not per-doc (stated)

The PRD file does NOT carry a top-of-doc `status::` dataview field. PRD design-phase completeness is tracked in `{slug} Track/{slug} Status.md` per [[DAS Status]] on the `prd::` line.

**Check pattern:** grep `{slug} PRD.md` for `^status::`; expect zero matches when `{slug} Track/{slug} Status.md` exists.

**Why:** dual-source-of-truth is the failure mode. F130 made `{slug} Status.md` authoritative; per-doc `status::` is a legacy fallback that should fade as anchors land Status.md files.

### RULE R-prd-09 — No `## Design Constraints` (DC-N) section (stated)

The PRD does NOT contain a `## Design Constraints` H2 with DC-numbered entries. Architectural / technical constraints belong in [[DAS Decisions]] (`D<N>`) and [[DAS Ruleset]] (`R-<slug>-<NN>`); business / environmental constraints live in `## Non-Goals` or `## Overview`.

**Check pattern:** grep for `^## Design Constraints` or `^### DC-\d+`; expect zero matches.

**Why:** the pre-F113 DC-N pattern conflated business and architectural constraints, and downstream readers couldn't tell which discipline owned which constraint. Splitting Decisions / Rules / Non-Goals gives each constraint a clear home.

### RULE R-prd-10 — Dispatch table carries a Stories row with proper-name display (checked)

The PRD's top-of-doc dispatch table contains a row whose wiki-link target points at the stories — either `[[{slug} PRD#User Stories\|{slug} Stories]]` (single-file form) or `[[{slug} Stories]]` (folder form). The displayed text is always the proper anchor-prefixed name `{slug} Stories`, matching the display convention used by sibling dispatch rows (`{slug} Architecture`, `{slug} Testing`, etc.).

**Check pattern:** parse the PRD's dispatch table; assert at least one row's link target matches one of the two canonical forms AND the row's displayed text is `{slug} Stories`.

**Why:** Stories are the "what does this product DO for users" of the PRD — readers landing on the PRD need a one-click jump to them without scrolling through Overview / Design Workflow / Goals first. Proper-name display keeps the dispatch table internally consistent; bare "Stories" loses the anchor prefix that every other row carries.

## Adoption

Adopted transitively via [[R-facet]].

## See also

- [[DAS PRD]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
