---
description: "audit-tied developer docs dispatch page — file tree and per-module docs"
---
# FCT Dev Dispatch
Facet spec for `{NAME} Dev Docs.md` — the audit-tied dispatch page that lists the Files tree and per-module docs under the root-level `{NAME} Dev Docs/` folder.

| -[[FCT Dev Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)<br>: audit-tied developer docs dispatch page — file tree and per-module docs |
| --- | --- |
| Related | [[FCT User Dispatch]],  [[FCT All Files]],  [[FCT Module Doc]],  [[FCT Anchor Page]],   |
| Examples | [[CAE Dev Docs\|minimal (Files + one module group)]],  [[HBR Dev Docs\|starter stub]],   |

**Location:** `{NAME} Dev Docs/{NAME} Dev Docs.md` (root-level folder, Gen-3)

The `{NAME} Dev Docs.md` dispatch page inside the root-level `{NAME} Dev Docs/` folder. Lists the **audit-tied implementation reference** for the codebase: file tree (`Files`) and per-module docs (one `.md` per source file or logical module). The synthesis-level overviews live elsewhere — Interface in `{NAME} Design/`, the system-architecture story in `{NAME} Design/` (the `{NAME} Architecture` doc).

**Dev Docs vs the synthesis docs:**

| Dev Docs (audit-tied) | Synthesis docs (curated) |
|---|---|
| Files (audit-generated tree) | Interface — human-authored layer contract, in `{NAME} Design/` |
| Per-module docs (one per source file) | Architecture — system overview, in `{NAME} Design/` |
| Reader = engineer doing surgery on the code | Reader = anyone consuming the synthesis layer (integrator, architect, contributor getting oriented) |

**Working example:** `HBR Dev Docs/HBR Dev Docs.md` — Dev Docs dispatch.


# Reference Example
---


# CAE Dev Docs

| -[[CAE Dev Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)<br>: developer documentation |
| --- | --- |
| [[CAE Files\|Files]] | repository file tree (audit-generated) |
| **engine/** |  |
| [[CAE Scheduler\|Scheduler]] | priority queue and worker pool |
| [[CAE RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** |  |
| [[CAE Router\|Router]] | CLI command routing |

(Note: the synthesis docs are not listed here — Interface lives in `{NAME} Design/`, the Architecture story in `{NAME} Design/` (the `{NAME} Architecture` doc). Dev Docs carries only Files + per-module docs.)

---


# Format Specification

## Location

`{NAME} Dev Docs.md` lives inside the root-level `{NAME} Dev Docs/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {NAME} Dev Docs`. Blank line after.
-[[{NAME} Dev Docs]]-`, top-right is `><br>: developer documentation` (or `+>` legacy shorthand).
- **First row** — `[[{NAME} Files]]` (always present for code anchors).
- **Module rows** — grouped by source folder, with bold folder headers (e.g., `**engine/**`).
- **Auto-management separator** — a `---` row enables auto-listing of remaining module docs.

## Contents

| Row | Part |
|-----|------|
| Files | [[FCT All Files]] — single-page codebase file tree |
| Module docs | [[FCT Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

## What does NOT belong in Dev Docs

The synthesis-level docs are not audit-tied reference and live in their own Gen-3 homes:

- **Interface** ([[FCT Interface]]) — required top-level human-authored layer contract. Lives in `{NAME} Design/{NAME} Interface.md`.
- **Architecture** — system-level synthesis (module diagram, data flow). Lives in `{NAME} Design/{NAME} Architecture.md`.

If an audit finds either in Dev Docs, that's a **dev-synthesis-misplaced** finding — migrate to its Gen-3 home.

# RULESET R-dev-dispatch
include::
where:: file:{ANCHOR}/**/{NAME} Dev Docs.md
description:: the `{NAME} Dev Docs.md` developer-docs dispatch page

What `/audit docs` checks on the Dev dispatch page. Cardinality: one per code anchor. Format of this set: [[FCT Ruleset]].

### RULE R-dev-dispatch-01 — Lives at `{NAME} Dev Docs/{NAME} Dev Docs.md` (checked)

The Dev Docs dispatch page sits inside the root-level `{NAME} Dev Docs/` folder.

**Check pattern:** the file's basename is `{slug} Dev Docs.md` and its parent is `{slug} Dev Docs`.

### RULE R-dev-dispatch-02 — First content row is the Files link (checked)

For a code anchor, the first dispatch row links `[[{NAME} Files]]` — the audit-generated repository file tree.

**Check pattern:** the first non-breadcrumb row links `{slug} Files`.

### RULE R-dev-dispatch-03 — Module rows are grouped by source folder with bold headers (sampled)

Per-module doc rows mirror the source tree: each source folder gets a bold header row (e.g. `**engine/**`) followed by its module-doc entries.

**Check pattern:** module rows appear under bold folder-header rows matching the source-tree grouping.

### RULE R-dev-dispatch-04 — Ends with a `---` auto-management separator (checked)

A `---` row enables auto-listing of remaining module docs.

**Check pattern:** the dispatch table contains a `---` auto-list separator row.

### RULE R-dev-dispatch-05 — No Interface or Architecture rows — those are synthesis docs (checked)

Dev Docs is audit-tied (Files + per-module docs); the synthesis docs live elsewhere — Interface in `{NAME} Design/`, the Architecture story in `{NAME} Design/` (the `{NAME} Architecture` doc). Either appearing in Dev Docs is a dev-synthesis-misplaced finding.

**Check pattern:** the Dev Docs dispatch lists no Interface or Architecture row.

**Why:** the split keeps machine-checkable reference separate from human-authored synthesis (F060).

# BRIEF

- **This file is the CAB facet spec for the Dev Docs dispatch page** — it defines the shape and contents of `{NAME} Dev Docs.md`. Edit here when the Dev-dispatch contract changes (new required rows, structural conventions, location moves).
- **NOT a place for per-anchor Dev Docs dispatches** — concrete instances (e.g. `HBR Dev Docs.md`) live in their anchor's root-level `{NAME} Dev Docs/` folder. Only the canonical Reference Example block stays here, as a worked illustration.
- **Inclusion test for new content:** does it apply to *every* `{NAME} Dev Docs.md` in *every* code anchor? If yes, edit here. If it's anchor-local, edit the anchor's Dev Docs dispatch. If it's a synthesis-zone rule, edit the relevant facet ([[FCT Interface]] / [[FCT Architecture]]) instead.
- **Load-bearing constraint — audit-tied vs synthesis:** Dev Docs is audit-tied (Files + per-module docs); the synthesis docs live elsewhere (Interface in `{NAME} Design/`, the Architecture story in `{NAME} Design/` (the `{NAME} Architecture` doc)). Do not reintroduce Interface or Architecture rows into the Dev Docs spec — they were intentionally moved. The §"What does NOT belong in Dev Docs" section is the canonical guard.
- **Cross-references to keep current:** [[FCT All Files]], [[FCT Module Doc]], [[FCT Interface]], [[FCT Architecture]], [[FCT User Dispatch]]. If any of these slugs rename or move, update the wiki-links in the body — the dispatch contract refers to them by basename.
- **Cite, don't inline:** markdown rendering rules live in [[R-markdown]]; dispatch-table formatting rules live in [[FCT Anchor Page]]. Reference those rather than duplicating their content here.
