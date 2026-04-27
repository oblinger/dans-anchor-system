---
description: developer docs dispatch page
---
# CAB Dev Dispatch

**Location:** `{NAME} Docs/{NAME} Dev/{NAME} Dev.md`


The `{NAME} Dev.md` dispatch page inside the `{NAME} Dev/` folder. Lists developer documentation including the file tree, architecture, and all module docs.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Dev/CAE Dev.md` — Dev dispatch.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---


| -[[CAE Dev]]- | +> |
| --- | --- |
| **Start here** | [[CAE Rollup\|Rollup]] — whole-crate API overview |
| [[CAE Files\|Files]] | repository file tree |
| [[CAE Architecture\|Architecture]] | system architecture |
| **engine/** | |
| [[CAE Scheduler\|Scheduler]] | priority queue and worker pool |
| [[CAE RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** | |
| [[CAE Router\|Router]] | CLI command routing |

---



# Format Specification

## Location

`{NAME} Dev.md` lives inside `{NAME} Docs/{NAME} Dev/`.

## Structure

- **Breadcrumb** — navigates back through the dispatch tree
- **Dispatch table** — top-left cell is `-[[{NAME} Dev]]-`, top-right is `+: developer documentation`
- **Fixed rows** — Files and Architecture always appear first
- **Module rows** — grouped by source folder, with bold folder headers (e.g., `**engine/**`)

## Contents

| Row | Part |
|-----|------|
| Start here | [[CAB Rollup]] — whole-codebase API overview (first row, labeled **Start here**) |
| Files | [[CAB Files]] — single-page codebase file tree |
| Architecture | System-level design overview |
| Module docs | [[CAB Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.

The **Start here** row is the top entry and links to `{NAME} Rollup.md`. Every Dev dispatch for a `code`-trait anchor must have this row — `/audit docs` flags its absence.
