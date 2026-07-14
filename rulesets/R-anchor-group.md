# RULESET R-anchor-group
include::
where:: `anchor`
description:: the DAS Anchor family index — the anchor & structure facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (the page chassis is governed by `R-anchor-page`); the rules here are the **group-membership** invariants specific to a facet-family index. Format of this set: [[DAS Ruleset]].

### RULE R-anchor-group-01 — The Facets row indexes every member facet in the family (checked)

The single `Facets` row links every facet file in the DAS Anchor family, and every member facet links back up to this group page in its breadcrumb.

**Check pattern:** the set of `Facets`-row links equals the family's facet specs (per the [[DAS Anchor]] Facets row; no missing, no extra); each member's breadcrumb passes through `~~[[DAS Anchor]]~~`.

**Why:** the index is how the family is discovered — a missing entry is an orphan facet; a stale entry is a dead link.

### RULE R-anchor-group-02 — No facet content of its own (stated)

A facet-group page carries no structural rules or spec prose for any individual facet — it is navigation only. Per-facet rules live in each member facet's own ruleset file.
