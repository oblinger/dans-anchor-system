---
description: "the figure-bearing anchor-page layout"
---

| -[[FEX Figure Page]]- | : the figure-bearing anchor-page layout<br>→ [[DAS]] → [[examples]] → [FEX Figure Page](hook://p/FEX%20Figure%20Page)  |
| --- | --- |
| Gallery | [[FEX Dispatch Examples]],   |
| Related | [[FEX Dispatch Examples]],  [[DAS Dispatch Table]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[Clarifier]],  [[CSE]],  [[DAS Examples]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Devtools]],  [[ESP]],  [[Espresso]],  [[FEX Agenda]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Claude]],  [[FEX Completed Roadmap]],  [[FEX CSE]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Facet]],  [[FEX Files]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX Minimal Facet]],  [[FEX Minimal Skill]],  [[FEX Project Root]],  [[FEX Repo]],  [[FEX Roadmap]],  [[FEX Rules]],  [[FEX Scheduler]],  [[FEX Skill]],  [[FEX Spine Examples]],  [[FEX Stories]],  [[FEX System Design]],  [[Forum Stories]],  [[Harbor Hops]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Runbooks]],  [[HBR]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Figure Page
A worked example: an anchor page that carries a figure.

![[F143-1-top-level.svg]]


## Why this order

Justified by [[progressive-disclosure]] — broadest first, detail on demand. Top to bottom:

1. **H1** — `<slug> <dash> <Name>` (per [[DAS Anchor Page]]): identity + jump-key. *(This example's name has no short slug, so its H1 is just the name; a slugged anchor would read e.g. `# HBR - Harbor`.)*
2. **One line** — *what the page is*, at the broadest stroke. One sentence (up to three), no detail. An optional **Overview** can follow with more, but the line right under the H1 just says the thing.
3. **The figure** — next, with **no title above it** — just the figure. The big-picture visual before the navigation.
4. **The dispatch table** — directly below the figure. When a figure is present it typically *is* the page's link surface, because the figure itself carries no clickable links — so the table supplies the navigation the picture can't.
