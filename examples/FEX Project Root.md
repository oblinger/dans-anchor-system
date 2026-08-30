---
description: "canonical project-root exemplar"
traits: [Code]
---

| -[[FEX Project Root]]- | : canonical project-root exemplar<br>→ [[DAS]] → [[FEX]] → [FEX Project Root](hook://p/FEX%20Project%20Root)  |
| --- | --- |
| Related | [[FEX Facet\|Facet]],  [[DAS Project Page]] (the facet),  [Repo](https://github.com/example/clarifier),  [Docs site](https://example.github.io/clarifier/), |
| [[vox]]  | sibling transcript tool |
| [[Clarifier Design\|Design]]+ | [[Clarifier PRD\|PRD]],  [[Clarifier UX Design\|UX Design]],  [[Clarifier CLI\|CLI]],  [[Clarifier API Design\|API]],  [[Clarifier Architecture\|Architecture]],  [[Clarifier Decisions\|Decisions]],  [[Clarifier Testing\|Testing]],  [[Clarifier Roadmap\|Roadmap]],  [[Clarifier Features\|Features]],   |
| [[Clarifier Track\|Track]]+ | [[Clarifier Backlog\|Backlog]],   |
| [[Clarifier User Docs\|User Docs]]+ | [[Clarifier Guide\|Guide]],   |
| [[Clarifier Dev Docs\|Dev Docs]]+ | [[Clarifier Files\|Files]],   |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Devtools]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Dispatch Examples\|Dispatch Examples]],  [[FEX Empty\|Empty]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Minimal Facet\|Minimal Facet]],  [[FEX Minimal Skill\|Minimal Skill]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Hops]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Runbooks]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# CLF — Clarifier
A CLI that turns messy meeting transcripts into clean, attributed minutes.

![[F143-1-top-level.svg]]


> **Canonical project root.** The `{slug}.md` entry page for a designed **project** anchor (`traits: [code]`). It's **masthead-only** — a project is *not* a [[Collection]] of like members; it has **structural parts**, so its dispatch rows are the anchor's standard sub-folders, each a `+` container link *down* to that sub-folder's own dispatch page (the [[progressive-disclosure]] tree of containers):
> - **Masthead order ([[R-anchor-page]]-12/-13/-14):** `Related` is the **1st** row (omit if empty — never blank). If the anchor has the design facet, `Design` is the **2nd** row (mandatory), in the fixed order **PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features** (PRD · the three user-surface docs · Architecture+Decisions · Testing · Roadmap · Features).
> - **`Design+`** → the design pipeline ([[DAS Design Folder]]) · **`Track+`** → the work surface · **`User Docs+`** / **`Dev Docs+`** → the two doc audiences.
> - **`Features` lives under `Design`**, not `track` — per-feature docs are *design* artifacts (`{slug} Design/{slug} Features/`); `track` holds only the live work surface (Roadmap, Backlog).
> - **Track is a *project* row.** A **published section anchor** ([[DAS Facets]], [[DAS Skills]], [[DAS Disciplines]], [[LBR]]) has **no `track` row** — it carries no work of its own; its tracking is centralized in the dev-side **design-home** tree (per D01). Only standalone project anchors track their own work here.
> - **`Related`** (the 1st row) carries related anchors **and** external resources (repo / site links) — added *only because the information exists* (the [[DAS Dispatch Table]] unified placement rule). There is **no separate `External` row**.
> - Ordering follows [[FEX Figure Page]]: H1 → one-liner → figure → dispatch table. No member zone, so no trailing electric-list marker (that's a [[Collection]] rule, not a project-root one).
