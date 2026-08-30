---
description: "the figure-bearing anchor-page layout"
---

| -[[FEX Figure Page]]- | : the figure-bearing anchor-page layout<br>→ [[DAS]] → [[FEX]] → [FEX Figure Page](hook://p/FEX%20Figure%20Page)  |
| --- | --- |
| Gallery | [[FEX Dispatch Examples\|Dispatch Examples]],   |
| Related | [[FEX Dispatch Examples\|Dispatch Examples]],  [[DAS Dispatch Table]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Devtools]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Empty\|Empty]],  [[FEX Facet\|Facet]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Minimal Facet\|Minimal Facet]],  [[FEX Minimal Skill\|Minimal Skill]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Hops]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Runbooks]],  [[HBR]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Figure Page
A worked example: an anchor page that carries a figure.

![[F143-1-top-level.svg]]

| Part | Is | Does |
|---|---|---|
| [[FEX Empty\|Skills]] | *verbs* | actions taken — `/design`, `/feature`, `/crank` and their kin |
| [[FEX Empty\|Facets]] | *nouns* | docs created — the backlog, the PRD, the spine, the heart |
| [[FEX Empty\|Disciplines]] | *adjectives* | systematic behaviors that ride across many skills and many facets |
| [[FEX Empty\|Rulesets]] | *directives and constraints* | what each of the three above is audited against |

## Why this order

Justified by [[progressive-disclosure]] — broadest first, detail on demand. Top to bottom:

1. **H1** — `<slug> <dash> <Name>` (per [[DAS Anchor Page]]): identity + jump-key. *(This example's name has no short slug, so its H1 is just the name; a slugged anchor would read e.g. `# HBR - Harbor`.)*
2. **One line** — *what the page is*, at the broadest stroke. One sentence (up to three), no detail. An optional **Overview** can follow with more, but the line right under the H1 just says the thing.
3. **The figure** — next, with **no title above it** — just the figure. The big-picture visual before the navigation.
4. **The parts table** — directly below the figure, one row per piece the figure draws, each linking out to the page that describes that piece (here every link is a pretend one to [[FEX Empty]], so nothing gets minted by a click). The figure carries no clickable links, so this table is how a reader gets from the picture to the pieces — Dan, 2026-08-29: *"if you have a figure that describes some pieces, there should be a table that links from there out to the places that describe the pieces."* Figure + parts table together are the page's heart ([[DAS heart]] § Figure).
