# RULESET R-naming
include::
description:: file-naming facet — `{slug} <X>.md` default + explicit exception allowlist

Embedded ruleset for the Naming facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella. Vault-wide application — every anchor's files are subject to this set, no explicit `include::` needed.

### RULE R-naming-01 — Default file name is `{slug} <X>.md` inside an anchor (checked)
check:: name_slug_prefixed

A markdown file inside `{anchor}/` (or any sub-folder rooted at the anchor) is named `{slug} <X>.md` where `{slug}` is the anchor's slug. Sub-folder marker files match their folder name: `{slug} Design/{slug} Design.md`, `{slug} Track/{slug} Track.md`.

**Check pattern:** for each `.md` file under an anchor, assert the filename starts with `{slug} ` (with a trailing space) OR matches one of the sanctioned exception patterns from R-naming-03.

**Why:** wiki-links from anywhere in the vault resolve correctly; search and dispatch surfaces don't suffer cross-anchor collisions; the file is globally unambiguous.

### RULE R-naming-02 — Vault-global files exempt (stated)

Files at the vault root or in vault-meta folders (Atlas, MY, etc.) that are genuinely global to the whole vault can omit the slug prefix. Examples: `Atlas.md`, `ATL Slugs.md`, `Q.md`, `kmr.md`.

**Check pattern:** vault-root and vault-meta files explicitly excluded from R-naming-01's check. List of exempt locations maintained by the auditor.

**Why:** these files exist *because* they're not scoped to any single anchor. Prefixing them with a slug would be a category error.

### RULE R-naming-03 — Facet-sanctioned unique patterns exempt (checked)

Files matching a facet-sanctioned alternative pattern are exempt from the slug-prefix default. The canonical allowlist:

- `F<NNN> — <title>.md` (per [[DAS Features]])
- `US-<slug>-<N> — <title>.md` (per [[DAS Stories]])
- `YYYY-MM-DD <topic>.<ext>` (per [[DAS Log]])
- `YYYY-MM <topic>.<ext>` (per [[DAS Log]] — year-month precision)
- `YYYY <topic>.<ext>` (per [[DAS Log]] — year-only precision)
- `SKILL.md` (the Claude Code skill entry file — every skill folder has one)
- `R-<x>.md` (ruleset / rule files, per [[F133 — Rulesets folder convention + facet embedding|F133]])

**Check pattern:** R-naming-01's check accepts files matching any of the regex shapes above as a pass.

**Why:** these patterns are unique enough on their own (F-numbers monotonic-forever, `US-<slug>-<N>` encodes the slug directly, ISO dates plus topic). Adding a slug prefix would be redundant. The parent folder (`{slug} Track/{slug} Features/`, `{slug} Design/{slug} PRD/`, `{slug}/{slug} Log/`) already encodes anchor scope.

### RULE R-naming-04 — Slug-prefix-sufficient-by-chance allowed sparingly (stated)

Files with names so domain-specific they're unlikely to collide vault-wide (e.g., `WCAG-2.1 contrast spec.md`, `Sourcetrail 2024 article.md`) are allowed without the slug prefix. Use sparingly — the prefix-default catches more cases than the by-chance argument.

**Check pattern:** manual judgment at authoring time; not mechanically audited. If a name is ambiguous about whether it qualifies, prefix it.

**Why:** rigidly applying the slug prefix to files whose names are *already* unique would produce names like `MUX Sourcetrail 2024 article.md` which is worse than the bare name. The escape valve exists for genuine cases.

### RULE R-naming-05 — Folder-anchor files match their folder name (checked)

A folder-anchor's marker file is named `{folder name}.md` — i.e., `{slug} Design/` contains `{slug} Design.md`; `{slug} Track/{slug} Features/` contains `{slug} Features.md`. The marker file name equals the folder name verbatim. This is the simplest instance of R-naming-01.

**Check pattern:** for each folder whose `.anchor` file is present, assert `<folder>/<folder basename>.md` exists.

**Why:** matches [[DAS Folder]]'s marker-file convention; ensures the folder-anchor pattern is consistent vault-wide.

### RULE R-naming-06 — External-discovery-contract files exempt (stated)

Files whose name is fixed by an external tool / runtime / repo discovery contract are exempt from the slug-prefix default: `CLAUDE.md`, `SKILL.md`, `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md`, `.anchor`, and non-markdown code files (`.py`/`.ts`/`.rs`/…). See § Exception D.

**Check pattern:** these exact names (and non-`.md` files) excluded from R-naming-01's check; the exempt set is fixed by external contracts, not author choice.

**Why:** the filename *is* the discovery key — Claude Code finds `CLAUDE.md`/`SKILL.md` by hard-coded path, GitHub renders `README.md`, HookAnchor names `.anchor`. Prefixing any of them breaks the tool that depends on the literal name.

## Adoption

Vault-wide — every anchor's files are subject to this set, no explicit `include::` required in `{slug} Decisions.md`. Listed in the catalog for completeness.

## See also

- [[DAS Naming]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
- F141 (future R-anchor umbrella) — would collect R-naming + R-folder + R-anchor-page + R-files when those rulesets exist.
