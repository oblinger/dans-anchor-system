# RULESET R-dev-dispatch
include::
where:: `file:{anchor}/**/{slug} Dev Docs.md`
description:: the `{slug} Dev Docs.md` developer-docs dispatch page

What `/audit docs` checks on the Dev dispatch page. Cardinality: one per code anchor. Format of this set: [[DAS Ruleset]].

### RULE R-dev-dispatch-01 — Lives at `{slug} Dev Docs/{slug} Dev Docs.md` (checked)

The Dev Docs dispatch page sits inside the root-level `{slug} Dev Docs/` folder.

**Check pattern:** the file's basename is `{slug} Dev Docs.md` and its parent is `{slug} Dev Docs`.

### RULE R-dev-dispatch-02 — First content row is the Files link (checked)

For a code anchor, the first dispatch row links `[[{slug} Files]]` — the audit-generated repository file tree.

**Check pattern:** the first non-breadcrumb row links `{slug} Files`.

### RULE R-dev-dispatch-03 — Module rows are grouped by source folder with bold headers (sampled)

Per-module doc rows mirror the source tree: each source folder gets a bold header row (e.g. `**engine/**`) followed by its module-doc entries.

**Check pattern:** module rows appear under bold folder-header rows matching the source-tree grouping.

### RULE R-dev-dispatch-04 — Ends with a `---` auto-management separator (checked)

A `---` row enables auto-listing of remaining module docs.

**Check pattern:** the dispatch table contains a `---` auto-list separator row.

### RULE R-dev-dispatch-05 — No Interface or Architecture rows — those are synthesis docs (checked)

Dev Docs is audit-tied (Files + per-module docs); the synthesis docs live elsewhere — Interface in `{slug} Design/`, the Architecture story in `{slug} Design/` (the `{slug} Architecture` doc). Either appearing in Dev Docs is a dev-synthesis-misplaced finding.

**Check pattern:** the Dev Docs dispatch lists no Interface or Architecture row.

**Why:** the split keeps machine-checkable reference separate from human-authored synthesis (F060).
