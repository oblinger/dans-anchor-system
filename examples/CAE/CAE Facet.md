---
description: "Canonical facet exemplar — the structure every FCT facet page follows, worked with the Design facet. Roll this out to all facets."
---

# Design
The marker that an anchor follows the designed-lifecycle convention — if `{NAME} Design/` exists, the anchor is in design-mode.

| -[[CAE Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Facet](hook://p/CAE%20Facet)<br>: canonical facet exemplar |
| --- | --- |
| Related | [[FCT]],  [[FCT Design]] (the live facet),  [[FCT Anchor Page]],  [[progressive-disclosure]] |

> **Canonical facet exemplar.** This page *is* the template every `FCT <name>` facet follows. Structure, top to bottom: **H1** = the facet's readable name → **one line** saying what it is → **masthead** (just `Related` — nothing the breadcrumb already gives) → the **facet body** (the H2s below). Roll this shape out to all facets. The worked content here is the **Design** facet.

## What it is

The **structural marker** that an anchor follows the designed-lifecycle convention. **If `{NAME} Design/` exists, the anchor is in design-mode** — `/design` operates on it and the PRD → UX → API → Architecture → Testing → Decisions → Roadmap pipeline applies. Folder presence *is* the signal; no trait field required.

## Location

`{anchor}/{NAME} Design/` — an anchor-folder directly under the anchor root, alongside `{NAME} Track/`, `{NAME} User Docs/`, `{NAME} Dev Docs/`.

## Structure

The `{NAME} Design/` folder is itself a container (anchor page + dispatch table, per [[progressive-disclosure]]); its members are the design sub-facets — **required**: [[FCT PRD|PRD]], [[FCT Architecture|Architecture]], [[FCT Testing|Testing]]; **recommended**: [[FCT Decisions|Decisions]], [[FCT Roadmap|Roadmap]], [[FCT Features|Features]]; **optional**: [[FCT UX Design|UX]], [[FCT API Design|API]].

## Rules

RULE (design-gate): the **presence of `{NAME} Design/`** is the gate — `/design` operates iff the folder exists. (Replaces the retired `Code`-trait check, which conflated *what's built* with *is it designed*.)

## Example

Live instance: [[FCT Design]] (the facet spec itself) and any anchor with a `{NAME} Design/` folder (e.g. [[CAE]]).
