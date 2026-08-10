---
description: "canonical facet exemplar"
---

# Design
The marker that an anchor follows the designed-lifecycle convention — if `{slug} Design/` exists, the anchor is in design-mode.

| -[[FEX Facet]]- | : canonical facet exemplar<br>→ [[DAS]] → [[examples]] → [FEX Facet](hook://p/FEX%20Facet)  |
| --- | --- |
| Related | [[DAS Facets]],  [[DAS Design Folder]] (the live facet),  [[DAS Anchor Page]],  [[progressive-disclosure]]  |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[Bridges]],  [[Clarifier]],  [[CSE]],  [[DAS Examples]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[Devtools]],  [[ESP]],  [[Espresso]],  [[FEX Agenda]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Claude]],  [[FEX Completed Roadmap]],  [[FEX CSE]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Dispatch Examples]],  [[FEX Figure Page]],  [[FEX Files]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX Minimal Facet]],  [[FEX Minimal Skill]],  [[FEX Project Root]],  [[FEX Repo]],  [[FEX Roadmap]],  [[FEX Rules]],  [[FEX Scheduler]],  [[FEX Skill]],  [[FEX Spine Examples]],  [[FEX Stories]],  [[FEX System Design]],  [[Forum Stories]],  [[Harbor Hops]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Runbooks]],  [[HBR PRD User Stories]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

> **Canonical facet exemplar.** This page *is* the template every `DAS <name>` facet follows. Structure, top to bottom: **H1** = the facet's readable name → **one line** saying what it is → **masthead** (just `Related` — nothing the breadcrumb already gives) → the **facet body** (the H2s below). Roll this shape out to all facets. The worked content here is the **Design** facet.

## What it is

The **structural marker** that an anchor follows the designed-lifecycle convention. **If `{slug} Design/` exists, the anchor is in design-mode** — `/design` operates on it and the PRD → UX → API → Architecture → Testing → Decisions → Roadmap pipeline applies. Folder presence *is* the signal; no trait field required.

## Location

`{anchor}/{slug} Design/` — an anchor-folder directly under the anchor root, alongside `{slug} Track/`, `{slug} User Docs/`, `{slug} Dev Docs/`.

## Structure

The `{slug} Design/` folder is itself a container (anchor page + dispatch table, per [[progressive-disclosure]]); its members are the design sub-facets — **required**: [[DAS PRD|PRD]], [[DAS Architecture|Architecture]], [[DAS Testing|Testing]]; **recommended**: [[DAS Decisions|Decisions]], [[DAS Roadmap|Roadmap]], [[DAS Features|Features]]; **optional**: [[DAS UX Design|UX]], [[DAS API Design|API]].

## Rules

RULE (design-gate): the **presence of `{slug} Design/`** is the gate — `/design` operates iff the folder exists. (Replaces the retired `code`-trait check, which conflated *what's built* with *is it designed*.)

## Example

Live instance: [[DAS Design Folder]] (the facet spec itself) and any anchor with a `{slug} Design/` folder (e.g. [[HBR]]).
