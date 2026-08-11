# RULESET R-anchor-group
include::
where:: `file:{anchor}/DAS Anchor.md`
description:: the DAS Anchor family index — the anchor & structure facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (the page chassis is governed by `R-anchor-page`); the rules here are the **group-membership** invariants specific to a facet-family index. Format of this set: [[DAS Ruleset]].

> **Armed 2026-08-11 ([[TINK Backlog#^T212|T212]]), after the same two repairs the other group sets needed.**
>
> **The selector named every anchor for a rule about one page.** It read `where:: anchor`, which fires once per anchor — 1,395 of them in the vault — while both rules here are claims about a single file, [[DAS Anchor]]. Measured before repair by arming the four group sets in [[R-anchor]] and taking TINK's judgment manifest: **988 items before, 996 after — 8 new judgments on an anchor holding none of the four pages**, every one N/A by construction, times the whole vault. Repointed at the page itself, the cost is 8 judgments on the `facets` anchor and **zero everywhere else**. This is the [[R-git]] shape read one level in: an anchor-scoped selector standing in for the scope the vocabulary does not have, except that here the scope it wanted — one named file — was available all along.
>
> **`-01` was `(checked)` with no `check::`.** `_needs_judgment` treats an absent ref as a membership miss and bills the rule as agent judgment anyway, so the label promised a mechanical verdict the engine never produced. Demoted to `(stated)`, which is what it has always been. Re-wiring rather than demoting would take a checker that knows the family's membership, and membership is nowhere declared: the rule asserts that two sets are equal — the `Facets`-row links and the family's member specs — and only the first of the two exists in machine-readable form. A `family::` key on each member spec would close that; it is not in the vocabulary, and inventing one is a larger decision than this row.

### RULE R-anchor-group-01 — The Facets row indexes every member facet in the family (stated)

The single `Facets` row links every facet file in the DAS Anchor family, and every member facet links back up to this group page in its breadcrumb.

**Check pattern:** the set of `Facets`-row links equals the family's facet specs (per the [[DAS Anchor]] Facets row; no missing, no extra); each member's breadcrumb passes through `~~[[DAS Anchor]]~~`.

**Why:** the index is how the family is discovered — a missing entry is an orphan facet; a stale entry is a dead link.

### RULE R-anchor-group-02 — No facet content of its own (stated)

A facet-group page carries no structural rules or spec prose for any individual facet — it is navigation only. Per-facet rules live in each member facet's own ruleset file.
