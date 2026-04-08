---
description: raw incoming content to process
---
# CAB Inbox

The inbox (`{NAME} Inbox.md`) is a drop zone for raw input — long descriptions, change requests, design thoughts, reference material — pasted in for processing and integration into the planning and execution docs.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK Inbox

Items below have been processed and moved to their destination docs.



## 2026-02-28 — Retry backoff tuning    `DONE`
User reported exponential backoff too aggressive for short tasks. Captured in [[TSK Open Questions#14]].

Original input:
> When I schedule a 2-second task and it fails, the retry waits 4s, then 8s, then 16s. For quick tasks this feels excessive. Could we cap the backoff or use linear for tasks under 10s?



## 2026-02-25 — Priority starvation fix    `MOVED → TSK Roadmap#M3`
Discussed promotion logic for starved low-priority tasks. Design notes moved to [[TSK Discussion#2026-02-25]]. Implementation planned for M3.



## 2026-02-20 — Initial feature brainstorm    `DONE`
Raw feature list from kickoff meeting. Items distributed to [[TSK PRD]] and [[TSK Backlog]].

---



# Format Specification

## Location

`{NAME} Inbox.md` lives at the anchor root, alongside the anchor page.

## Format
- Reverse chronological dated sections (H2)
- Each heading: `## YYYY-MM-DD — Topic    \`STATUS\``
- Status tags: `DONE` (processed in place), `MOVED → {destination}` (content relocated)
- Original input preserved as blockquotes when useful as a record

## Lifecycle
- Content is pasted in, then processed by an agent or the user who integrates it into the appropriate planning docs (PRD, Roadmap, Todo, Backlog)
- Processed entries remain with a status tag as a persistent log of what was communicated
- Rarely revisited after processing
