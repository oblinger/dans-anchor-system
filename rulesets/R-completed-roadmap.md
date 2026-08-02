# RULESET R-completed-roadmap
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Completed Roadmap.md`
description:: completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap

Ruleset for this facet — spec: [[DAS Completed Roadmap]] (extracted from the spec 2026-07-12). Adopted via `R-facet` umbrella.

### RULE R-completed-roadmap-01 — Location is `{slug} Design/{slug} Completed Roadmap.md` (checked)

The doc lives at `{slug} Design/{slug} Completed Roadmap.md` — sibling of `{slug} Roadmap.md`.

**Check pattern:** when one or more milestones have migrated, `ls "{anchor}/{slug} Design/{slug} Completed Roadmap.md"` exists. When zero migrations have occurred, the file may be absent — it's created on first migration.

**Why:** companion location keeps the forward and the completed views adjacent.

### RULE R-completed-roadmap-02 — Body-only, no YAML frontmatter (checked)
check:: h1_no_frontmatter

First non-blank line is `# {slug} Completed Roadmap` (H1). No `---` block precedes.

**Why:** matches the vault-wide body-only convention.

### RULE R-completed-roadmap-03 — Top-to-bottom order is newest-to-oldest (sampled)

Migrated milestone H2 sections appear in reverse-chronological order by migration date. The migration date is in the heading: `## [x] M-<Name> — <Title> (migrated YYYY-MM-DD)`.

**Check pattern:** parse migrated milestone H2s; extract dates; assert monotonically non-increasing top-to-bottom.

**Why:** the reader's primary query is "what shipped most recently?" Reverse-chrono gives that answer first.

### RULE R-completed-roadmap-04 — Standalone groupings interleave with migrated milestones (sampled)

Standalone-completed-features groupings (H2s named `## Completed standalone features (since <date>)`) appear between migrated milestone sections, capturing features that completed in that window. At most one "current" standalone grouping exists at the top.

**Check pattern:** parse H2 headings; classify each as `migrated milestone` or `standalone grouping`; assert structure alternates plausibly (standalone groupings between or above milestones, never below all milestones).

**Why:** standalone-feature completions get a coherent home that's still rough-chronological without forcing them into fake milestones.

### RULE R-completed-roadmap-05 — Migrated milestones preserve their full structure (stated)

A migrated milestone retains its Status line, reference block, and all sub-items (in their final `[x]` / `[~]` / abandoned state) exactly as they were in the Roadmap at migration time.

**Check pattern:** sample migrated milestones; assert presence of Status line and sub-items.

**Why:** migration is structural, not summarizing. Preserves the project's reasoning about what shipped together.

### RULE R-completed-roadmap-06 — Migrated milestones never come back (stated)

Once a milestone migrates to Completed Roadmap, it stays. Reactivation of work in the same domain creates a new milestone (e.g., `M-Auth-V2`), not a revival of the old one.

**Check pattern:** git history — assert no roadmap entry uses an M-name that already appears in Completed Roadmap.

**Why:** keeps the historical record honest. Reopened work is genuinely a new milestone with new scope.
