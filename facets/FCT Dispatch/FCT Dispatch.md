---
description: "the per-section sub-folder dispatch-page facets"
---

# Sub-dispatch
The the per-section sub-folder dispatch-page facets.

| -[[FCT Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Dispatch](hook://p/FCT%20Dispatch)<br>: the per-section sub-folder dispatch-page facets |
| --- | --- |
| Facets | [[FCT Dispatch Table\|Dispatch Table]] (base form),  [[FCT Design Dispatch\|Design Dispatch]],  [[FCT Dev Dispatch\|Dev Dispatch]],  [[FCT Plan Dispatch\|Plan Dispatch]],  [[FCT Track Dispatch\|Track Dispatch]],  [[FCT User Dispatch\|User Dispatch]], |

# RULESET R-dispatch-group
include::
where:: anchor
description:: the FCT Dispatch family index — the per-section sub-folder dispatch-page facet group

What `/audit` checks on this facet-group index page. It is a grouped-Container anchor page (chassis governed by `R-anchor-page`); the rules here are the **group-membership** invariants for the sub-dispatch facet family. Format of this set: [[FCT Ruleset]].

### RULE R-dispatch-group-01 — The Facets row indexes every sub-dispatch facet, with Dispatch Table as the base form (checked)

The `Facets` row links every per-section dispatch facet (Design / Dev / Plan / Track / User Dispatch) and names [[FCT Dispatch Table]] as the base form they all specialize; each member's breadcrumb routes through this page.

**Check pattern:** the `Facets`-row link set equals the sub-dispatch facet files under `FCT Dispatch/`; [[FCT Dispatch Table]] is present as the base; each member breadcrumb passes through `[[FCT Dispatch]]`.

### RULE R-dispatch-group-02 — No facet content of its own (stated)

The page is navigation only; each dispatch page's shape lives in that facet's own embedded RULESET. The shared base-form rules live in [[FCT Dispatch Table]].
