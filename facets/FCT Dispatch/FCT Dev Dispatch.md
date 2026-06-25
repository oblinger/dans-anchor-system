---
description: "audit-tied developer docs dispatch page — file tree and per-module docs"
---
# FCT Dev Dispatch
Facet spec for `{NAME} Dev.md` — the audit-tied dispatch page that lists the Files tree and per-module docs under `{NAME} Docs/{NAME} Dev/`.

| -[[FCT Dev Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)<br>: audit-tied developer docs dispatch page — file tree and per-module docs |
| --- | --- |
| Related | [[FCT User Dispatch]],  [[FCT All Files]],  [[FCT Module Doc]],  [[FCT Anchor Page]],   |
| Examples | [[CAE Dev Docs\|minimal (Files + one module group)]],  [[HBR Dev Docs\|starter stub]],   |

**Location:** `{NAME} Docs/{NAME} Dev/{NAME} Dev.md`


The `{NAME} Dev.md` dispatch page inside the `{NAME} Dev/` folder. Lists the **audit-tied implementation reference** for the codebase: file tree (`Files`) and per-module docs (one `.md` per source file or logical module). Synthesis-level overviews — Interface, Architecture — live under `{NAME} User/` instead, with their own User dispatch.

**The Dev/User split:**

| Dev | User |
|---|---|
| Audit-tied (machine-checkable currency) | Curated (human-authored synthesis) |
| Files (audit-generated tree) | Interface (human-authored layer contract — required) |
| Per-module docs (one per source file) | Architecture (system overview) |
| Reader = engineer doing surgery on the code | Reader = anyone consuming the synthesis layer (end user, integrator, contributor getting oriented) |

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Dev/CAE Dev.md` — Dev dispatch.


# Reference Example
---


# CAE Dev

| -[[CAE Dev]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dev Dispatch](hook://p/FCT%20Dev%20Dispatch)<br>: developer documentation |
| --- | --- |
| [[CAE Files\|Files]] | repository file tree (audit-generated) |
| **engine/** |  |
| [[CAE Scheduler\|Scheduler]] | priority queue and worker pool |
| [[CAE RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** |  |
| [[CAE Router\|Router]] | CLI command routing |

(Note: Interface and Architecture used to lead this dispatch; they moved to [[CAE User]] in the synthesis/reference split. The [[CAE Files]] row-1 link points at `[[CAE Interface]]` — wiki-link by basename resolves regardless of folder.)

---


# Format Specification

## Location

`{NAME} Dev.md` lives inside `{NAME} Docs/{NAME} Dev/`.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {NAME} Dev`. Blank line after.
-[[{NAME} Dev]]-`, top-right is `><br>: developer documentation` (or `+>` legacy shorthand).
- **First row** — `[[{NAME} Files]]` (always present for code anchors).
- **Module rows** — grouped by source folder, with bold folder headers (e.g., `**engine/**`).
- **Auto-management separator** — a `---` row enables auto-listing of remaining module docs.

## Contents

| Row | Part |
|-----|------|
| Files | [[FCT All Files]] — single-page codebase file tree |
| Module docs | [[FCT Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

## What does NOT belong in Dev

The following used to live in Dev and have moved to User as part of the synthesis-vs-reference split:

- **Interface** ([[FCT Interface]]) — required top-level human-authored layer contract. Lives in `{NAME} User/{NAME} Interface.md`.
- **Architecture** — system-level synthesis (module diagram, data flow). Lives in `{NAME} User/{NAME} Architecture.md`.

If an audit finds either in Dev, that's a **dev-synthesis-misplaced** finding — migrate to User.

# RULESET R-dev-dispatch
include::
where:: file:{ANCHOR}/**/{NAME} Dev.md
description:: the `{NAME} Dev.md` developer-docs dispatch page

What `/audit docs` checks on the Dev dispatch page. Cardinality: one per code anchor. Format of this set: [[FCT Ruleset]].

### RULE R-dev-dispatch-01 — Lives at `{NAME} Docs/{NAME} Dev/{NAME} Dev.md` (checked)

The Dev dispatch page sits inside the `{NAME} Dev/` folder.

**Check pattern:** the file's basename is `{slug} Dev.md` and its parent is `{slug} Dev`.

### RULE R-dev-dispatch-02 — First content row is the Files link (checked)

For a code anchor, the first dispatch row links `[[{NAME} Files]]` — the audit-generated repository file tree.

**Check pattern:** the first non-breadcrumb row links `{slug} Files`.

### RULE R-dev-dispatch-03 — Module rows are grouped by source folder with bold headers (sampled)

Per-module doc rows mirror the source tree: each source folder gets a bold header row (e.g. `**engine/**`) followed by its module-doc entries.

**Check pattern:** module rows appear under bold folder-header rows matching the source-tree grouping.

### RULE R-dev-dispatch-04 — Ends with a `---` auto-management separator (checked)

A `---` row enables auto-listing of remaining module docs.

**Check pattern:** the dispatch table contains a `---` auto-list separator row.

### RULE R-dev-dispatch-05 — No Interface or Architecture rows — those are User-zone (checked)

Dev is audit-tied (Files + per-module docs); the synthesis docs Interface and Architecture live under `{NAME} User/`, not here. Either appearing in Dev is a dev-synthesis-misplaced finding.

**Check pattern:** the Dev dispatch lists no Interface or Architecture row.

**Why:** the Dev/User split keeps machine-checkable reference separate from human-authored synthesis (F060).

# BRIEF

- **This file is the CAB facet spec for the Dev dispatch page** — it defines the shape and contents of `{NAME} Dev.md`. Edit here when the Dev-dispatch contract changes (new required rows, structural conventions, location moves).
- **NOT a place for per-anchor Dev dispatches** — concrete instances (e.g. `CAE Dev.md`) live in their anchor's `{NAME} Docs/{NAME} Dev/` folder. Only the canonical Reference Example block stays here, as a worked illustration.
- **Inclusion test for new content:** does it apply to *every* `{NAME} Dev.md` in *every* code anchor? If yes, edit here. If it's anchor-local, edit the anchor's Dev dispatch. If it's a synthesis-zone rule, edit [[FCT User Dispatch]] instead.
- **Load-bearing constraint — the Dev/User split:** Dev is audit-tied (Files + per-module docs); User is curated (Interface + Architecture). Do not reintroduce Interface or Architecture rows into the Dev spec — they were intentionally moved per F060. The §"What does NOT belong in Dev" section is the canonical guard.
- **Cross-references to keep current:** [[FCT All Files]], [[FCT Module Doc]], [[FCT Interface]], [[FCT User Dispatch]], [[CAE Dev]] (working example). If any of these slugs rename or move, update the wiki-links in the body — the dispatch contract refers to them by basename.
- **Cite, don't inline:** markdown rendering rules live in [[R-markdown]]; dispatch-table formatting rules live in [[FCT Anchor Page]]. Reference those rather than duplicating their content here.
