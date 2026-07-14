# RULESET R-dispatch-group
include::
where:: `anchor`
description:: the DAS Dispatch family index — the per-section sub-folder dispatch-page facet group

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the sub-dispatch facet family. Format of this set: [[DAS Ruleset]].

### RULE R-dispatch-group-01 — The Facets row indexes every sub-dispatch facet, with Dispatch Table as the base form (checked)

The `Facets` row links every per-section dispatch facet (Design / Dev / Plan / Track / User Dispatch) and names [[DAS Dispatch Table]] as the base form they all specialize; each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the family's sub-dispatch facet specs; [[DAS Dispatch Table]] is present as the base; each member breadcrumb passes through `~~[[DAS Dispatch]]~~`.

### RULE R-dispatch-group-02 — No facet content of its own (stated)

The page is navigation only; each dispatch page's shape lives in that facet's own ruleset file. The shared base-form rules live in [[DAS Dispatch Table]].
