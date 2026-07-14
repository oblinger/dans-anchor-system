---
description: "the figure-bearing anchor-page layout"
---

# FEX Figure Page
A worked example: an anchor page that carries a figure.

![[F143-1-top-level.svg]]

| -[[FEX Figure Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [FEX Figure Page](hook://p/FEX%20Figure%20Page)<br>: the figure-bearing anchor-page layout |
| --- | --- |
| Gallery | [[FEX Dispatch Examples]],   |
| Related | [[FEX Dispatch Examples]],  [[DAS Dispatch Table]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[CAE Architecture]],  [[CAE Decisions]],  [[CAE PRD]],  [[CAE Stories]],  [[CAE Testing]],  [[Clarifier]],  [[CSE]],  [[DAS Examples]],  [[Devtools]],  [[Decisions/DKT Decisions]],  [[PRD/DMUX PRD]],  [[Espresso]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Completed Roadmap]],  [[FEX CSE]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Facet]],  [[FEX Files]],  [[FEX Grouped Dispatch]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX List Dispatch]],  [[FEX Minimal Facet]],  [[FEX Minimal Skill]],  [[FEX Project Root]],  [[FEX queries]],  [[FEX Repo]],  [[FEX Roadmap]],  [[FEX Rules]],  [[FEX Scheduler]],  [[FEX Skill]],  [[FEX Stories]],  [[Forum Stories]],  [[Architecture/HA Architecture]],  [[HBR]],  [[Architecture/HBR Architecture]],  [[Decisions/HBR Decisions]],  [[PRD/HBR PRD]],  [[HBR PRD User Stories]],  [[Testing/HBR Testing]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Decisions/Mini Decisions]],  [[PRD/Mini PRD]],  [[Testing/Mini Testing]],  [[Architecture/MUX Architecture]],  [[Architecture/OBU Architecture]],  [[PRD/OBU PRD]],  [[SKA Bridge Testing]],  [[Snap]],  [[Testing/MUX Testing]],  [[Decisions/UCM Decisions]],  [[US-CAE-1 — Schedule a Task]],  [[US-CAE-3 — Retry Failed Tasks]],  [[Viz Bench]],   |

## Why this order

Justified by [[progressive-disclosure]] — broadest first, detail on demand. Top to bottom:

1. **H1** — `<slug> - <Name>` (per [[DAS Anchor Page]] / [[SKA Decisions|D06]]): identity + jump-key. *(This example's name has no short slug, so its H1 is just the name; a slugged anchor would read e.g. `# SKL - Skills`.)*
2. **One line** — *what the page is*, at the broadest stroke. One sentence (up to three), no detail. An optional **Overview** can follow with more, but the line right under the H1 just says the thing.
3. **The figure** — next, with **no title above it** — just the figure. The big-picture visual before the navigation.
4. **The dispatch table** — directly below the figure. When a figure is present it typically *is* the page's link surface, because the figure itself carries no clickable links — so the table supplies the navigation the picture can't.
