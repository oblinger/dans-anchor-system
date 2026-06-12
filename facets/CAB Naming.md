# CAB Naming
description:: file-naming facet — every file inside an anchor uses `{NAME} <X>.md` form by default; exceptions for vault-global files and facet-sanctioned unique patterns.

The Naming facet specifies the **default file-naming convention** for files that live inside an anchor folder, plus the canonical list of exceptions where another pattern is allowed.

**Default rule:** files inside `{anchor}/` (and inside its sub-folders like `{NAME} Design/`, `{NAME} Track/`) are named `{NAME} <X>.md` — the anchor slug prefix + space + content name. Examples: `CAE PRD.md`, `CAE Architecture.md`, `MUX Testing.md`, `Disk Log.md`.

**Why slug prefix:** anchor folders frequently get unified into search results, dispatch tables, and wiki-link autocompletes that span the whole vault. A file named just `PRD.md` collides with every other anchor's PRD; `{NAME} PRD.md` is globally unambiguous. Wiki-links from anywhere in the vault resolve correctly without disambiguation gymnastics.

The convention is **the floor, not the ceiling** — a few classes of files are exempt because they have stronger uniqueness guarantees built into their own naming.

## Exception A — vault-global files

Files at the vault root or in vault-meta folders (Atlas, MY, etc.) that are genuinely global to the whole vault can omit the anchor slug prefix. Examples: `Atlas.md`, `ATL Slugs.md`, `kmr.md`, `Q.md`.

The test: would prefixing it with a slug be a category error? *(Atlas is not part of any single anchor — it indexes everything.)* If yes → exempt. If no → use the prefix.

## Exception B — facet-sanctioned unique patterns

Some facets define alternative naming patterns that are unique enough on their own that an anchor prefix would be redundant. The canonical allowlist:

| Pattern | Facet | Example |
|---|---|---|
| `F<NNN> — <title>.md` | [[CAB Features]] | `F138 — Plan→Design skill rename.md` |
| `US-<RID>-<N> — <title>.md` | [[CAB Stories]] | `US-MUX-3 — Browse catalog and place composition.md` |
| `YYYY-MM-DD <topic>.md` | [[CAB Log]] | `2026-06-10 Master consolidation + storage strategy.md` |
| `YYYY-MM <topic>.<ext>` | [[CAB Log]] | `2025-10 BOD Slides.pptx` (year-month precision) |
| `YYYY <topic>.<ext>` | [[CAB Log]] | `2023 Prior Inventions.md` (year-only precision) |

These patterns appear inside anchor sub-folders (`{NAME} Track/{NAME} Features/`, `{NAME} Design/{NAME} PRD/`, `{NAME}/{NAME} Log/`) where the parent folder already encodes the anchor scope. The filename itself doesn't need to.

Each exception pattern is **declared by the facet that owns it**. Facets that define alternative patterns also state their uniqueness contract (e.g., F-numbers are monotonic-forever per anchor; US-<RID>-<N> encodes the RID directly). When a new facet introduces an alternative pattern, this list grows.

## Exception C — slug-prefix sufficient by chance

Names so domain-specific they're unlikely to collide with anything in another anchor — e.g., a file named after a unique external entity (`Sourcetrail 2024 article.md`, `WCAG-2.1 contrast spec.md`). Allowed but use sparingly; the prefix-default catches more cases than the by-chance argument.

**Stated rule, not checked** — manual judgment at authoring time. If you're unsure, prefix.

## Folder-anchor files follow the same rule

The anchor marker file (the `{NAME}.md` inside `{NAME}/` per [[CAB Folder]]) is itself an instance of the default rule: file name = folder name. Sub-anchor folders nested inside an anchor (like `{NAME} Design/`, `{NAME} Track/`) carry their own marker files (`{NAME} Design.md`, `{NAME} Track.md`) — same convention all the way down.

## Trait applicability

Vault-wide. Every anchor in the vault is subject to this naming convention; the exceptions are explicit.

## Cross-references — facets that declare exception patterns

These facets each declare an alternative naming pattern, and their pattern is listed in § Exception B above. When their spec evolves, this facet's exception table updates too.

- [[CAB Features]] — `F<NNN> — <title>.md`
- [[CAB Stories]] — `US-<RID>-<N> — <title>.md`
- [[CAB Log]] — `YYYY-MM-DD <topic>.<ext>` (and year-month / year-only fallbacks)

## Audit

`/audit naming` (future) would flag the rules captured in `R-naming` below — file-name shape, exception-pattern compliance, missing slug prefix on non-exempt files.

## See also

- [[CAB Folder]] — folder layout (the marker-file convention is the simplest instance of this naming rule)
- [[CAB Anchor Page]] — content of the `{NAME}.md` marker file
- [[CAB Files]] — source-tree docs
- F141 (future R-anchor umbrella) — collects R-naming + R-folder + R-anchor-page + R-files when those rule sets exist


# RULESET R-naming
include::
description:: File-naming rules vault-wide — slug-prefix default + explicit exception allowlist.

Embedded rule set for the Naming facet, co-located with the facet spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella. Vault-wide application — every anchor's files are subject to this set, no explicit `include::` needed.

### RULE R-naming-01 — Default file name is `{NAME} <X>.md` inside an anchor (checked)

A markdown file inside `{anchor}/` (or any sub-folder rooted at the anchor) is named `{NAME} <X>.md` where `{NAME}` is the anchor's slug. Sub-folder marker files match their folder name: `{NAME} Design/{NAME} Design.md`, `{NAME} Track/{NAME} Track.md`.

**Check pattern:** for each `.md` file under an anchor, assert the filename starts with `{NAME} ` (with a trailing space) OR matches one of the sanctioned exception patterns from R-naming-03.

**Why:** wiki-links from anywhere in the vault resolve correctly; search and dispatch surfaces don't suffer cross-anchor collisions; the file is globally unambiguous.

### RULE R-naming-02 — Vault-global files exempt (stated)

Files at the vault root or in vault-meta folders (Atlas, MY, etc.) that are genuinely global to the whole vault can omit the slug prefix. Examples: `Atlas.md`, `ATL Slugs.md`, `Q.md`, `kmr.md`.

**Check pattern:** vault-root and vault-meta files explicitly excluded from R-naming-01's check. List of exempt locations maintained by the auditor.

**Why:** these files exist *because* they're not scoped to any single anchor. Prefixing them with a slug would be a category error.

### RULE R-naming-03 — Facet-sanctioned unique patterns exempt (checked)

Files matching a facet-sanctioned alternative pattern are exempt from the slug-prefix default. The canonical allowlist:

- `F<NNN> — <title>.md` (per [[CAB Features]])
- `US-<RID>-<N> — <title>.md` (per [[CAB Stories]])
- `YYYY-MM-DD <topic>.<ext>` (per [[CAB Log]])
- `YYYY-MM <topic>.<ext>` (per [[CAB Log]] — year-month precision)
- `YYYY <topic>.<ext>` (per [[CAB Log]] — year-only precision)

**Check pattern:** R-naming-01's check accepts files matching any of the regex shapes above as a pass.

**Why:** these patterns are unique enough on their own (F-numbers monotonic-forever, US-<RID>-<N> encodes RID directly, ISO dates plus topic). Adding a slug prefix would be redundant. The parent folder (`{NAME} Track/{NAME} Features/`, `{NAME} Design/{NAME} PRD/`, `{NAME}/{NAME} Log/`) already encodes anchor scope.

### RULE R-naming-04 — Slug-prefix-sufficient-by-chance allowed sparingly (stated)

Files with names so domain-specific they're unlikely to collide vault-wide (e.g., `WCAG-2.1 contrast spec.md`, `Sourcetrail 2024 article.md`) are allowed without the slug prefix. Use sparingly — the prefix-default catches more cases than the by-chance argument.

**Check pattern:** manual judgment at authoring time; not mechanically audited. If a name is ambiguous about whether it qualifies, prefix it.

**Why:** rigidly applying the slug prefix to files whose names are *already* unique would produce names like `MUX Sourcetrail 2024 article.md` which is worse than the bare name. The escape valve exists for genuine cases.

### RULE R-naming-05 — Folder-anchor files match their folder name (checked)

A folder-anchor's marker file is named `{folder name}.md` — i.e., `{NAME} Design/` contains `{NAME} Design.md`; `{NAME} Track/{NAME} Features/` contains `{NAME} Features.md`. The marker file name equals the folder name verbatim. This is the simplest instance of R-naming-01.

**Check pattern:** for each folder whose `.anchor` file is present, assert `<folder>/<folder basename>.md` exists.

**Why:** matches [[CAB Folder]]'s marker-file convention; ensures the folder-anchor pattern is consistent vault-wide.

# BRIEF

- **This file is the Naming facet spec** — the authoritative source for the `{NAME} <X>.md` default and the exception allowlist. Audit tooling (`/audit naming`) and cross-cutting facet specs cite this file; treat it as load-bearing.
- **NOT a place to invent new exceptions.** A new exempt pattern enters § Exception B only after the facet that owns it (Features, Stories, Log, etc.) declares the pattern in its own spec with a uniqueness contract. Add the row here only after that prior step, and link back to the owning facet.
- **Inclusion test for § Exception B**: the pattern must (1) be declared by another facet spec, (2) have a stated uniqueness contract that makes a slug prefix redundant, and (3) live inside an anchor sub-folder that already encodes anchor scope. If any leg fails, the file should carry the `{NAME}` prefix instead.
- **Keep the prose spec and R-naming ruleset aligned.** The H2 sections above and the `# RULESET R-naming` block below are two views of the same rules — edit both together. The exception table in § Exception B mirrors the allowlist in R-naming-03; don't let them drift.
- **Link format for cross-referenced facets** is `[[CAB <Facet>]]` (e.g., `[[CAB Features]]`, `[[CAB Log]]`) — not bare names, not relative paths. The § Cross-references section is the canonical list; update it when adding/removing exception rows.
- **Do NOT inline trait-wide rules or anchor-local rules here.** Trait-specific naming conventions belong in `CAB <Trait>.md`; anchor-local naming exceptions belong in `{NAME} Rules.md` or `{NAME} Decisions.md`. This facet is the vault-wide default + exception allowlist only.
- **The `description::` Dataview field and the one-paragraph TLDR under the H1 are load-bearing** — facet-listing pages and audit scripts read them. Don't replace either with a callout or restructure them into a different shape.
