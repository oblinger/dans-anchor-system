---
description: developer docs dispatch page — audit-tied implementation reference
---
# CAB Dev Dispatch

Facet spec for `{NAME} Dev.md` — the audit-tied dispatch page that lists the Files tree and per-module docs under `{NAME} Docs/{NAME} Dev/`.

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

| -[[CAE Dev]]- | ><br>: developer documentation |
| --- | --- |
| [[CAE Files\|Files]] | repository file tree (audit-generated) |
| **engine/** | |
| [[CAE Scheduler\|Scheduler]] | priority queue and worker pool |
| [[CAE RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** | |
| [[CAE Router\|Router]] | CLI command routing |

(Note: Interface and Architecture used to lead this dispatch; they moved to [[CAE User]] in the synthesis/reference split. The [[CAE Files]] row-1 link points at `[[CAE Interface]]` — wiki-link by basename resolves regardless of folder.)

---


# Format Specification

## Location

`{NAME} Dev.md` lives inside `{NAME} Docs/{NAME} Dev/`.

## Structure (per F060)

- **YAML frontmatter** — optional.
- **H1** — `# {NAME} Dev`. Blank line after.
- **Dispatch table** — top-left cell is `-[[{NAME} Dev]]-`, top-right is `><br>: developer documentation` (or `+>` legacy shorthand).
- **First row** — `[[{NAME} Files]]` (always present for code anchors).
- **Module rows** — grouped by source folder, with bold folder headers (e.g., `**engine/**`).
- **Auto-management separator** — a `---` row enables auto-listing of remaining module docs.

## Contents

| Row | Part |
|-----|------|
| Files | [[FCT Files]] — single-page codebase file tree |
| Module docs | [[FCT API Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

## What does NOT belong in Dev

The following used to live in Dev and have moved to User as part of the synthesis-vs-reference split:

- **Interface** ([[FCT Interface]]) — required top-level human-authored layer contract. Lives in `{NAME} User/{NAME} Interface.md`.
- **Architecture** — system-level synthesis (module diagram, data flow). Lives in `{NAME} User/{NAME} Architecture.md`.

If an audit finds either in Dev, that's a **dev-synthesis-misplaced** finding — migrate to User.

# BRIEF

- **This file is the CAB facet spec for the Dev dispatch page** — it defines the shape and contents of `{NAME} Dev.md`. Edit here when the Dev-dispatch contract changes (new required rows, structural conventions, location moves).
- **NOT a place for per-anchor Dev dispatches** — concrete instances (e.g. `CAE Dev.md`) live in their anchor's `{NAME} Docs/{NAME} Dev/` folder. Only the canonical Reference Example block stays here, as a worked illustration.
- **Inclusion test for new content:** does it apply to *every* `{NAME} Dev.md` in *every* code anchor? If yes, edit here. If it's anchor-local, edit the anchor's Dev dispatch. If it's a synthesis-zone rule, edit [[FCT User Dispatch]] instead.
- **Load-bearing constraint — the Dev/User split:** Dev is audit-tied (Files + per-module docs); User is curated (Interface + Architecture). Do not reintroduce Interface or Architecture rows into the Dev spec — they were intentionally moved per F060. The §"What does NOT belong in Dev" section is the canonical guard.
- **Cross-references to keep current:** [[FCT Files]], [[FCT API Doc]], [[FCT Interface]], [[FCT User Dispatch]], [[CAE Dev]] (working example). If any of these slugs rename or move, update the wiki-links in the body — the dispatch contract refers to them by basename.
- **Cite, don't inline:** markdown rendering rules live in [[R-markdown]]; dispatch-table formatting rules live in [[FCT Anchor Page]]. Reference those rather than duplicating their content here.
