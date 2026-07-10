---
description: "audit-tied developer docs dispatch page — file tree and per-module docs"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)
# FCT Dev Dispatch
Facet spec for `{slug} Dev Docs.md` — the audit-tied dispatch page that lists the Files tree and per-module docs under the root-level `{slug} Dev Docs/` folder.

**Related:** [[FCT User Dispatch]],  [[FCT All Files]],  [[FCT Module Doc]],  [[FCT Anchor Page]]
**Examples:** [[HBR Dev Docs\|minimal (Files + one module group)]],  [[HBR Dev Docs\|starter stub]]

**Location:** `{slug} Dev Docs/{slug} Dev Docs.md` (root-level folder, Gen-3)

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

| -[[HBR Dev Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)<br>: developer documentation |
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
| Files | [[FCT All Files]] — single-page codebase file tree |
| Module docs | [[FCT Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

## What does NOT belong in Dev Docs

The synthesis-level docs are not audit-tied reference and live in their own Gen-3 homes:

- **Interface** ([[FCT Interface]]) — required top-level human-authored layer contract. Lives in `{slug} Design/{slug} Interface.md`.
- **Architecture** — system-level synthesis (module diagram, data flow). Lives in `{slug} Design/{slug} Architecture.md`.

If an audit finds either in Dev Docs, that's a **dev-synthesis-misplaced** finding — migrate to its Gen-3 home.

# RULESET R-dev-dispatch
include::
where:: `file:{ANCHOR}/**/{slug} Dev Docs.md`
description:: the `{slug} Dev Docs.md` developer-docs dispatch page

What `/audit docs` checks on the Dev dispatch page. Cardinality: one per code anchor. Format of this set: [[FCT Ruleset]].

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

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above.)*

- **Inclusion test** — content belongs here iff it applies to *every* `{slug} Dev Docs.md` in *every* code anchor; anchor-local content goes in the anchor's Dev Docs dispatch, and synthesis-zone rules go in [[FCT Interface]] / [[FCT Architecture]] instead.
- **Don't regress audit-tied vs synthesis** — Dev Docs is audit-tied (Files + per-module docs); do not reintroduce Interface or Architecture rows (they were intentionally moved to `{slug} Design/`). The § "What does NOT belong in Dev Docs" section + R-dev-dispatch-05 are the canonical guard.
- **Cross-ref integrity** — keep [[FCT All Files]], [[FCT Module Doc]], [[FCT Interface]], [[FCT Architecture]], [[FCT User Dispatch]] wiki-links current; the dispatch contract refers to them by basename.
