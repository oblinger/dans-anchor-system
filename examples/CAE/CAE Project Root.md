---
description: "Canonical project-root exemplar — the {NAME}.md anchor page for a designed software project (masthead-only; structural rows, no member zone). Roll out to project anchors."
traits: [Code]
---

# CLF — Clarifier
A CLI that turns messy meeting transcripts into clean, attributed minutes.

![[F143-1-top-level.svg]]

| -[[CAE Project Root]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Project Root](hook://p/CAE%20Project%20Root)<br>: canonical project-root exemplar |
| --- | --- |
| Related | [[CAE Facet]],  [[FCT Project Page]] (the facet),  [[vox]] (sibling transcript tool) |
| [[Clarifier Design\|Design]]+ | [[Clarifier PRD\|PRD]],  [[Clarifier UX Design\|UX Design]],  [[Clarifier CLI\|CLI]],  [[Clarifier API Design\|API]],  [[Clarifier Architecture\|Architecture]],  [[Clarifier Decisions\|Decisions]],  [[Clarifier Testing\|Testing]],  [[Clarifier Roadmap\|Roadmap]],  [[Clarifier Features\|Features]],   |
| [[Clarifier Track\|Track]]+ | [[Clarifier Backlog\|Backlog]],   |
| [[Clarifier User Docs\|User Docs]]+ | [[Clarifier Guide\|Guide]],   |
| [[Clarifier Dev Docs\|Dev Docs]]+ | [[Clarifier Files\|Files]],   |
| External | [Repo](https://github.com/example/clarifier), [Docs site](https://example.github.io/clarifier/) |

> **Canonical project root.** The `{NAME}.md` entry page for a designed **project** anchor (`traits: [Code]`). It's **masthead-only** — a project is *not* a [[Collection]] of like members; it has **structural parts**, so its dispatch rows are the anchor's standard sub-folders, each a `+` container link *down* to that sub-folder's own dispatch page (the [[progressive-disclosure]] tree of containers):
> - **Masthead order ([[SKA Decisions|D07]]):** `Related` is the **1st** row (omit if empty — never blank). If the anchor has the design facet, `Design` is the **2nd** row (mandatory), in the fixed order **PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features** (PRD · the three user-surface docs · Architecture+Decisions · Testing · Roadmap · Features).
> - **`Design+`** → the design pipeline ([[FCT Design]]) · **`Track+`** → the work surface · **`User Docs+`** / **`Dev Docs+`** → the two doc audiences.
> - **`Features` lives under `Design`**, not `Track` — per-feature docs are *design* artifacts (`{NAME} Design/{NAME} Features/`); `Track` holds only the live work surface (Roadmap, Backlog).
> - **Track is a *project* row.** A **published section anchor** ([[FCT]], [[SKL]], [[DSC]], [[LBR]]) has **no `Track` row** — it carries no work of its own; its tracking is centralized in the dev-side **[[SKA]]** tree (per D01). Only standalone project anchors track their own work here.
> - **`External`** (repo / site links) and **`Related`** are the only non-structural masthead rows — added *only because the information exists* (the [[DSC Dispatch Table]] unified placement rule).
> - Ordering follows [[CAE Figure Page]]: H1 → one-liner → figure → dispatch table. No member zone, so no trailing electric-list marker (that's a [[Collection]] rule, not a project-root one).
