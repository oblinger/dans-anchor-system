# RULESET R-design-docs-group
include::
where:: `anchor`
description:: the DAS Design Docs family index — the design-pipeline doc facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the design-pipeline facet family. Format of this set: [[DAS Ruleset]].

### RULE R-design-docs-group-01 — The Facets row indexes every design-pipeline facet (checked)

The `Facets` row links every design-doc facet (`{slug} Design/` contents — PRD, System Design, Architecture, UX, API, Testing, Stories, Features, Decisions, Roadmap, …), and each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the family's design-pipeline facet specs; each member breadcrumb passes through `~~[[DAS Design Docs]]~~`.

### RULE R-design-docs-group-02 — No facet content of its own (stated)

The page is navigation only; the structure of each design doc lives in that doc's own ruleset file, not here.
