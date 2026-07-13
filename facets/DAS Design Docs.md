---
description: "the design-pipeline doc facets (the `{slug} Design/` contents)"
---

# Design
The the design-pipeline doc facets (the `{slug} Design/` contents).

| -[[DAS Design Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Design Docs](hook://p/DAS%20Design%20Docs)<br>: the design-pipeline doc facets (the `{slug} Design/` contents) |
| --- | --- |
| Facets | [[DAS PRD\|PRD]],  [[DAS System Design\|System Design]],  [[DAS Architecture\|Architecture]],  [[DAS Files Architecture\|Files Architecture]],  [[DAS UX Design\|UX Design]],  [[DAS API Design\|API Design]],  [[DAS CLI\|CLI]],  [[DAS Testing\|Testing]],  [[DAS Stories\|Stories]],  [[DAS Decisions\|Decisions]],  [[DAS Roadmap\|Roadmap]],  [[DAS Completed Roadmap\|Completed Roadmap]],  [[DAS Design Folder\|Design]],   |

# RULESET R-design-docs-group
include::
where:: `anchor`
description:: the FCT Design Docs family index — the design-pipeline doc facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the design-pipeline facet family. Format of this set: [[DAS Ruleset]].

### RULE R-design-docs-group-01 — The Facets row indexes every design-pipeline facet (checked)

The `Facets` row links every design-doc facet (`{slug} Design/` contents — PRD, System Design, Architecture, UX, API, Testing, Decisions, Roadmap, …), and each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the design-pipeline facet files under `FCT Design Docs/`; each member breadcrumb passes through `~~[[DAS Design Docs]]~~`.

### RULE R-design-docs-group-02 — No facet content of its own (stated)

The page is navigation only; the structure of each design doc lives in that doc's own embedded RULESET, not here.
