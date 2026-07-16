---
description: "audit-tied developer docs dispatch page — file tree and per-module docs"
---

# DAS Dev Dispatch
Facet spec for `{slug} Dev Docs.md` — the audit-tied dispatch page that lists the Files tree and per-module docs under the root-level `{slug} Dev Docs/` folder.

| -[[DAS Dev Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Dev Dispatch](hook://p/DAS%20Dev%20Dispatch) |
| --- | --- |
| Related | [[DAS User Dispatch]],  [[DAS All Files]],  [[DAS Module Doc]],  [[DAS Anchor Page]],   |
| Examples | [[HBR Dev Docs\|minimal (Files + one module group)]],  [[HBR Dev Docs\|starter stub]],   |
| Rules | [[R-dev-dispatch]],   |
| ... | [[anchor-page]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Log]],  [[DAS Messages]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Location:** `{slug} Dev Docs/{slug} Dev Docs.md` (root-level folder, Gen-3)

**Cardinality: one per anchor** — exactly one Dev Docs dispatch page, present only when the anchor carries developer docs.

The `{slug} Dev Docs.md` dispatch page inside the root-level `{slug} Dev Docs/` folder. Lists the **audit-tied implementation reference** for the codebase: file tree (`Files`) and per-module docs (one `.md` per source file or logical module). The synthesis-level overviews live elsewhere — Interface in `{slug} Design/`, the system-architecture story in `{slug} Design/` (the `{slug} Architecture` doc).

**Dev Docs vs the synthesis docs:**

| Dev Docs (audit-tied) | Synthesis docs (curated) |
|---|---|
| Files (audit-generated tree) | Interface — human-authored layer contract, in `{slug} Design/` |
| Per-module docs (one per source file) | Architecture — system overview, in `{slug} Design/` |
| Reader = engineer doing surgery on the code | Reader = anyone consuming the synthesis layer (integrator, architect, contributor getting oriented) |

**Working example:** `HBR Dev Docs/HBR Dev Docs.md` — Dev Docs dispatch.

# Reference Example
---

# CAE Dev Docs

| -[[HBR Dev Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Dispatch]] → [DAS Dev Dispatch](hook://p/DAS%20Dev%20Dispatch)<br>: developer documentation |
| --- | --- |
| [[FEX Files\|Files]] | repository file tree (audit-generated) |
| **engine/** |  |
| [[FEX Scheduler\|Scheduler]] | priority queue and worker pool |
| [[CAE RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** |  |
| [[CAE Router\|Router]] | CLI command routing |

(Note: the synthesis docs are not listed here — Interface lives in `{slug} Design/`, the Architecture story in `{slug} Design/` (the `{slug} Architecture` doc). Dev Docs carries only Files + per-module docs.)

---

# Format Specification

## Location

`{slug} Dev Docs.md` lives inside the root-level `{slug} Dev Docs/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {slug} Dev Docs`. Blank line after.
-[[{slug} Dev Docs]]-`, top-right is `><br>: developer documentation` (or `+>` legacy shorthand).
- **First row** — `[[{slug} Files]]` (always present for code anchors).
- **Module rows** — grouped by source folder, with bold folder headers (e.g., `**engine/**`).
- **Auto-management separator** — a `---` row enables auto-listing of remaining module docs.

## Contents

| Row | Part |
|-----|------|
| Files | [[DAS All Files]] — single-page codebase file tree |
| Module docs | [[DAS Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

## What does NOT belong in Dev Docs

The synthesis-level docs are not audit-tied reference and live in their own Gen-3 homes:

- **Interface** ([[DAS Interface]]) — required top-level human-authored layer contract. Lives in `{slug} Design/{slug} Interface.md`.
- **Architecture** — system-level synthesis (module diagram, data flow). Lives in `{slug} Design/{slug} Architecture.md`.

If an audit finds either in Dev Docs, that's a **dev-synthesis-misplaced** finding — migrate to its Gen-3 home.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above.)*

- **Inclusion test** — content belongs here iff it applies to *every* `{slug} Dev Docs.md` in *every* code anchor; anchor-local content goes in the anchor's Dev Docs dispatch, and synthesis-zone rules go in [[DAS Interface]] / [[DAS Architecture]] instead.
- **Don't regress audit-tied vs synthesis** — Dev Docs is audit-tied (Files + per-module docs); do not reintroduce Interface or Architecture rows (they were intentionally moved to `{slug} Design/`). The § "What does NOT belong in Dev Docs" section + R-dev-dispatch-05 are the canonical guard.
- **Cross-ref integrity** — keep [[DAS All Files]], [[DAS Module Doc]], [[DAS Interface]], [[DAS Architecture]], [[DAS User Dispatch]] wiki-links current; the dispatch contract refers to them by basename.
