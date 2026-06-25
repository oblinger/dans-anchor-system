---
description: "the design-pipeline doc facets (the `{NAME} Design/` contents)"
---

# Design
The the design-pipeline doc facets (the `{NAME} Design/` contents).

| -[[FCT Design Docs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Design Docs](hook://p/FCT%20Design%20Docs)<br>: the design-pipeline doc facets (the `{NAME} Design/` contents) |
| --- | --- |
| Facets | [[FCT PRD\|PRD]],  [[FCT System Design\|System Design]],  [[FCT Architecture\|Architecture]],  [[FCT Files Architecture\|Files Architecture]],  [[FCT UX Design\|UX Design]],  [[FCT API Design\|API Design]],  [[FCT Testing\|Testing]],  [[FCT Stories\|Stories]],  [[FCT Decisions\|Decisions]],  [[FCT Roadmap\|Roadmap]],  [[FCT Completed Roadmap\|Completed Roadmap]],  [[FCT Design\|Design]],   |

# RULESET R-design-docs-group
include::
where:: anchor
description:: the FCT Design Docs family index — the design-pipeline doc facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the design-pipeline facet family. Format of this set: [[FCT Ruleset]].

### RULE R-design-docs-group-01 — The Facets row indexes every design-pipeline facet (checked)

The `Facets` row links every design-doc facet (`{NAME} Design/` contents — PRD, System Design, Architecture, UX, API, Testing, Decisions, Roadmap, …), and each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the design-pipeline facet files under `FCT Design Docs/`; each member breadcrumb passes through `[[FCT Design Docs]]`.

### RULE R-design-docs-group-02 — No facet content of its own (stated)

The page is navigation only; the structure of each design doc lives in that doc's own embedded RULESET, not here.
