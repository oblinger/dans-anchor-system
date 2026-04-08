---
description: planning docs dispatch page
---
# CAB Plan Dispatch

The `{NAME} Plan.md` dispatch page inside the `{NAME} Plan/` folder. Lists all planning and execution documents for the anchor.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---


| -[[TSK Plan]]- | +> |
| --- | --- |
| [[TSK PRD\|PRD]] | product requirements |
| [[TSK System Design\|System Design]] | architecture and design |
| [[TSK UX Design\|UX Design]] | user-facing interface spec |
| [[TSK Discussion\|Discussion]] | design reasoning and trade-offs |
| [[TSK Roadmap\|Roadmap]] | milestones with checkbox tracking |
| [[TSK Backlog\|Backlog]] | deferred work |
| [[TSK Inbox\|Inbox]] | raw input to process |
| [[TSK Open Questions\|Open Questions]] | unresolved decisions |
| [[TSK Research\|Research]] | research notes |

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
| `{NAME} Inbox.md` | [[CAB Inbox]] |
| `{NAME} Open Questions.md` | [[CAB Open Questions]] |
| `{NAME} Features/` | [[CAB Features]] |

Not all entries are required — only list documents that exist for this anchor.
