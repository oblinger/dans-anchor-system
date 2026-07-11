---
description: "canonical facet exemplar"
---

# Design
The marker that an anchor follows the designed-lifecycle convention — if `{slug} Design/` exists, the anchor is in design-mode.

| -[[FEX Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [FEX Facet](hook://p/FEX%20Facet)<br>: canonical facet exemplar |
| --- | --- |
| Related | [[DAS Facets]],  [[DAS Design Folder]] (the live facet),  [[DAS Anchor Page]],  [[progressive-disclosure]] |

> **Canonical facet exemplar.** This page *is* the template every `FCT <name>` facet follows. Structure, top to bottom: **H1** = the facet's readable name → **one line** saying what it is → **masthead** (just `Related` — nothing the breadcrumb already gives) → the **facet body** (the H2s below). Roll this shape out to all facets. The worked content here is the **Design** facet.

## What it is

The **structural marker** that an anchor follows the designed-lifecycle convention. **If `{slug} Design/` exists, the anchor is in design-mode** — `/design` operates on it and the PRD → UX → API → Architecture → Testing → Decisions → Roadmap pipeline applies. Folder presence *is* the signal; no trait field required.

## Location

`{anchor}/{slug} Design/` — an anchor-folder directly under the anchor root, alongside `{slug} Track/`, `{slug} User Docs/`, `{slug} Dev Docs/`.

## Structure

The `{slug} Design/` folder is itself a container (anchor page + dispatch table, per [[progressive-disclosure]]); its members are the design sub-facets — **required**: [[DAS PRD|PRD]], [[DAS Architecture|Architecture]], [[DAS Testing|Testing]]; **recommended**: [[DAS Decisions|Decisions]], [[DAS Roadmap|Roadmap]], [[DAS Features|Features]]; **optional**: [[DAS UX Design|UX]], [[DAS API Design|API]].

## Rules

RULE (design-gate): the **presence of `{slug} Design/`** is the gate — `/design` operates iff the folder exists. (Replaces the retired `Code`-trait check, which conflated *what's built* with *is it designed*.)

## Example

Live instance: [[DAS Design Folder]] (the facet spec itself) and any anchor with a `{slug} Design/` folder (e.g. [[HBR]]).
