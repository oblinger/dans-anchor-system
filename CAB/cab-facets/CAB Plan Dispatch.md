---
description: planning docs dispatch page
---
# CAB Plan Dispatch

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Plan.md`


The `{NAME} Plan.md` dispatch page inside the `{NAME} Plan/` folder. Lists all planning and execution documents for the anchor.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Plan.md` — Plan dispatch.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---


| -[[CAE Plan]]- | +> |
| --- | --- |
| [[CAE PRD\|PRD]] | product requirements |
| [[CAE System Design\|System Design]] | architecture and design |
| [[CAE UX Design\|UX Design]] | user-facing interface spec |
| [[CAE Discussion\|Discussion]] | design reasoning and trade-offs |
| [[CAE Roadmap\|Roadmap]] | milestones with checkbox tracking |
| [[CAE Backlog\|Backlog]] | deferred work |
| [[CAE Icebox\|Icebox]] | cold-storage / someday-maybe (optional) |
| [[CAE Inbox\|Inbox]] | raw input to process |
| [[CAE Open Questions\|Open Questions]] | unresolved decisions |
| [[CAE Research\|Research]] | research notes |

---



# Format Specification

## Location

`{NAME} Plan.md` lives inside `{NAME} Docs/{NAME} Plan/`.

## Structure

- **Breadcrumb** — navigates back through the dispatch tree
- **Dispatch table** — top-left cell is `-[[{NAME} Plan]]-`, top-right is `+: planning docs`
- **Body rows** — one row per planning document, with wiki-link in column 1 and short description in column 2

## Contents

The Plan dispatch page lists all children of the Plan folder:

| Document | Part |
|----------|------|
| `{NAME} PRD.md` | [[CAB PRD]] |
| `{NAME} System Design.md` | [[CAB System Design]] |
| `{NAME} UX Design.md` | [[CAB UX Design]] |
| `{NAME} Discussion.md` | [[CAB Discussion]] |
| `{NAME} Roadmap.md` | [[CAB Roadmap]] |
| `{NAME} Backlog.md` | [[CAB Backlog]] |
| `{NAME} Icebox.md` | [[CAB Icebox]] (optional) |
| `{NAME} Inbox.md` | [[CAB Inbox]] |
| `{NAME} Open Questions.md` | [[CAB Open Questions]] |
| `{NAME} Features/` | [[CAB Features]] |

Not all entries are required — only list documents that exist for this anchor.
