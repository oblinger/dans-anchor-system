---
description: "file-naming facet — every file inside an anchor uses `{slug} <X>.md` form by default; exceptions for vault-global files and facet-sanctioned unique patterns"
---

# DAS Naming
File-naming facet — every file inside an anchor uses `{slug} <X>.md` form by default; exceptions for vault-global files and facet-sanctioned unique patterns.

| -[[DAS Naming]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Naming](hook://p/DAS%20Naming) |
| --- | --- |
| Related | [[DAS Folder]],  [[DAS Anchor Page]],  [[DAS All Files]],  [[DAS Features]],   |
| Examples | [[HBR\|minimal anchor]],  [[HBR\|fuller anchor]],   |
| Rules | [[R-naming]],   |
| ... | [[anchor-page]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — Every `.md` file inside an anchor is named `{slug} <X>.md` (the anchor slug as prefix). Three exception classes are allowed: vault-global files, facet-sanctioned alternative patterns (F-numbers, US-IDs, ISO dates), and genuinely unique domain-specific names. **Cardinality: one per anchor** — a single naming convention applies to each anchor, not a per-file choice.

The Naming facet specifies the **default file-naming convention** for files that live inside an anchor folder, plus the canonical list of exceptions where another pattern is allowed.

**Default rule:** files inside `{anchor}/` (and inside its sub-folders like `{slug} Design/`, `{slug} Track/`) are named `{slug} <X>.md` — the anchor slug prefix + space + content name. Examples: `CAE PRD.md`, `CAE Architecture.md`, `MUX Testing.md`, `Disk Log.md`.

**Why slug prefix:** anchor folders frequently get unified into search results, dispatch tables, and wiki-link autocompletes that span the whole vault. A file named just `PRD.md` collides with every other anchor's PRD; `{slug} PRD.md` is globally unambiguous. Wiki-links from anywhere in the vault resolve correctly without disambiguation gymnastics.

The convention is **the floor, not the ceiling** — a few classes of files are exempt because they have stronger uniqueness guarantees built into their own naming.

## Exception A — vault-global files

Files at the vault root or in vault-meta folders (Atlas, MY, etc.) that are genuinely global to the whole vault can omit the anchor slug prefix. Examples: `Atlas.md`, `ATL Slugs.md`, `kmr.md`, `Q.md`.

The test: would prefixing it with a slug be a category error? *(Atlas is not part of any single anchor — it indexes everything.)* If yes → exempt. If no → use the prefix.

## Exception B — facet-sanctioned unique patterns

Some facets define alternative naming patterns that are unique enough on their own that an anchor prefix would be redundant. The canonical allowlist:

| Pattern | Facet | Example |
|---|---|---|
| `F<NNN> — <title>.md` | [[DAS Features]] | `F138 — Plan→Design skill rename.md` |
| `US-<slug>-<N> — <title>.md` | [[DAS Stories]] | `US-MUX-3 — Browse catalog and place composition.md` |
| `YYYY-MM-DD <topic>.md` | [[DAS Log]] | `2026-06-10 Master consolidation + storage strategy.md` |
| `YYYY-MM <topic>.<ext>` | [[DAS Log]] | `2025-10 BOD Slides.pptx` (year-month precision) |
| `YYYY <topic>.<ext>` | [[DAS Log]] | `2023 Prior Inventions.md` (year-only precision) |

These patterns appear inside anchor sub-folders (`{slug} Track/{slug} Features/`, `{slug} Design/{slug} PRD/`, `{slug}/{slug} Log/`) where the parent folder already encodes the anchor scope. The filename itself doesn't need to.

Each exception pattern is **declared by the facet that owns it**. Facets that define alternative patterns also state their uniqueness contract (e.g., F-numbers are monotonic-forever per anchor; `US-<slug>-<N>` encodes the slug directly). When a new facet introduces an alternative pattern, this list grows.

**Inclusion test** — a pattern enters this table only when it (1) is declared by another facet spec, (2) carries a stated uniqueness contract that makes a slug prefix redundant, and (3) lives inside an anchor sub-folder that already encodes anchor scope. If any leg fails, the file carries the `{slug}` prefix instead.

## Exception C — slug-prefix sufficient by chance

Names so domain-specific they're unlikely to collide with anything in another anchor — e.g., a file named after a unique external entity (`Sourcetrail 2024 article.md`, `WCAG-2.1 contrast spec.md`). Allowed but use sparingly; the prefix-default catches more cases than the by-chance argument.

**Stated rule, not checked** — manual judgment at authoring time. If you're unsure, prefix.

## Exception D — external-discovery-contract files

Files whose name is fixed by an **external discovery contract** — a tool, runtime, or repo convention that hard-codes the filename — are never prefixed; a slug prefix would break the contract that finds them.

| File | Contract |
|---|---|
| `CLAUDE.md` | Claude Code config — hard-coded discovery path, one per project root |
| `SKILL.md` | Claude Code skill entry — hard-coded discovery path, one per skill folder |
| `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md` | repo / GitHub conventions |
| `.anchor` | anchor marker file — named by HookAnchor |
| code files (`.py`, `.ts`, `.rs`, …) | not markdown; outside Obsidian's link graph entirely |

Distinct from Exception B (which is *facet*-sanctioned **markdown** patterns living inside an anchor): these are *external*-tool-mandated names, several of them non-markdown. **Stated rule** — don't add a row without naming the external contract that forces the exemption.

## Folder-anchor files follow the same rule

The anchor marker file (the `{slug}.md` inside `{slug}/` per [[DAS Folder]]) is itself an instance of the default rule: file name = folder name. Sub-anchor folders nested inside an anchor (like `{slug} Design/`, `{slug} Track/`) carry their own marker files (`{slug} Design.md`, `{slug} Track.md`) — same convention all the way down.

## Cardinality and applicability

**Cardinality: one per anchor.** Each anchor has exactly one naming convention — the `{slug} <X>.md` default — not a per-file or per-folder choice. The exception classes are part of that single convention, not alternatives to it.

Vault-wide. Every anchor in the vault is subject to this naming convention; the exceptions are explicit.

This facet holds the **vault-wide default + exception allowlist only** — trait-specific naming conventions belong in the owning trait's spec (`CAB <Trait>.md`), and anchor-local naming exceptions belong in that anchor's `{slug} Rules.md` or `{slug} Decisions.md`, not here.

## Cross-references — facets that declare exception patterns

These facets each declare an alternative naming pattern, and their pattern is listed in § Exception B above. When their spec evolves, this facet's exception table updates too.

- [[DAS Features]] — `F<NNN> — <title>.md`
- [[DAS Stories]] — `US-<slug>-<N> — <title>.md`
- [[DAS Log]] — `YYYY-MM-DD <topic>.<ext>` (and year-month / year-only fallbacks)

## Audit

`/audit naming` (future) would flag the rules captured in `R-naming` below — file-name shape, exception-pattern compliance, missing slug prefix on non-exempt files.

## See also

- [[DAS Folder]] — folder layout (the marker-file convention is the simplest instance of this naming rule)
- [[DAS Anchor Page]] — content of the `{slug}.md` marker file
- [[DAS All Files]] — source-tree docs
- F141 (future R-anchor umbrella) — collects R-naming + R-folder + R-anchor-page + R-files when those rulesets exist

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above plus the `# RULESET R-naming` block below.)*

- **Don't invent new exceptions here.** A pattern enters § Exception B only after the facet that owns it declares it in its own spec with a stated uniqueness contract (per the § Exception B inclusion test); then add the row here and link back to the owning facet.
- **Keep the two views aligned** — § Exception B's table and R-naming-03's allowlist are the same list; edit them together, and update § Cross-references when adding or removing an exception row.
