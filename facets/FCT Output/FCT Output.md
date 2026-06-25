---
description: "the output / published-doc facets"
---

# Output & docs
The the output / published-doc facets.

| -[[FCT Output]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Output](hook://p/FCT%20Output)<br>: the output / published-doc facets |
| --- | --- |
| Facets | [[FCT Cards\|Cards]],  [[FCT Outputs\|Outputs]],  [[FCT Documentation Site\|Documentation Site]],  [[FCT WP\|WP]],  [[Docs]],  [[TSK User Guide]],   |

# RULESET R-output-group
include::
where:: anchor
description:: the FCT Output family index — the output / published-doc facet group page

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the output facet family. Format of this set: [[FCT Ruleset]].

### RULE R-output-group-01 — The Facets row indexes every output facet (checked)

The `Facets` row links every output / published-doc facet (Cards, Outputs, Documentation Site, WP, …), and each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the output facet files under `FCT Output/`; each member breadcrumb passes through `[[FCT Output]]`.

### RULE R-output-group-02 — No facet content of its own (stated)

The page is navigation only; each output facet's structure lives in that facet's own embedded RULESET.
