---
description: "anchor & structure facets — what makes a folder an anchor and how its files are named"
---

# Anchor & structure
The anchor & structure facets.

| -[[FCT Anchor]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Anchor](hook://p/FCT%20Anchor)<br>: anchor & structure facets — what makes a folder an anchor and how its files are named |
| --- | --- |
| Facets | [[FCT Anchor Page\|Anchor Page]],  [[FCT Project Page\|Project Page]],  [[FCT Folder\|Folder]],  [[FCT Anchor Tree\|Anchor Tree]],  [[FCT Naming\|Naming]],  [[FCT Claude\|Claude]],  [[FCT Move\|Move]],  [[FCT Interface\|Interface]],  [[FCT CLI\|CLI]],  [[FCT Code Repository\|Code Repository]],   |

# RULESET R-anchor-group
include::
where:: anchor
description:: the FCT Anchor family index — the anchor & structure facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (the page chassis is governed by `R-anchor-page`); the rules here are the **group-membership** invariants specific to a facet-family index. Format of this set: [[FCT Ruleset]].

### RULE R-anchor-group-01 — The Facets row indexes every member facet in the family (checked)

The single `Facets` row links every facet file in the `FCT Anchor/` family, and every member facet links back up to this group page in its breadcrumb.

**Check pattern:** the set of `Facets`-row links equals the set of facet files under `FCT Anchor/` (no missing, no extra); each member's breadcrumb passes through `[[FCT Anchor]]`.

**Why:** the index is how the family is discovered — a missing entry is an orphan facet; a stale entry is a dead link.

### RULE R-anchor-group-02 — No facet content of its own (stated)

A facet-group page carries no structural rules or spec prose for any individual facet — it is navigation only. Per-facet rules live in each member facet's own embedded RULESET.
