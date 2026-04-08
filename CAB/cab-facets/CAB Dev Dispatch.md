---
description: developer docs dispatch page
---
# CAB Dev Dispatch

The `{NAME} Dev.md` dispatch page inside the `{NAME} Dev/` folder. Lists developer documentation including the file tree, architecture, and all module docs.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---


| -[[TSK Dev]]- | +> |
| --- | --- |
| [[TSK Files\|Files]] | repository file tree |
| [[TSK Architecture\|Architecture]] | system architecture |
| **engine/** | |
| [[TSK Scheduler\|Scheduler]] | priority queue and worker pool |
| [[TSK RetryManager\|RetryManager]] | backoff and retry logic |
| **api/** | |
| [[TSK Router\|Router]] | CLI command routing |

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
| Files | [[CAB Files]] — single-page codebase file tree |
| Architecture | System-level design overview |
| Module docs | [[CAB Module Doc]] — one row per documented module, grouped by source folder |

Module doc rows mirror the source tree structure. Each source folder gets a bold header row, followed by its module doc entries.
