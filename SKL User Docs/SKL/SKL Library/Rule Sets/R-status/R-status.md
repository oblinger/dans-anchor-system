# RULESET R-status
include:: [[FCT Status#RULESET R-status\|embedded body]]
description:: Rules for the {NAME} Status.md facet doc; canonical body lives embedded in CAB Status.md.

Catalog-side stub for the Status facet rule set. Per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention, the actual rules are co-located with their facet spec — defined as a `# RULESET R-status` second-H1 block inside [[FCT Status]] alongside the prose that motivates them. This file exists so the catalog-side wiring (`R-facet` include::, `Rule Sets.md` dispatch row) has a clean `[[R-status]]` wiki-link to point at.

**To see the actual rules:** follow [[FCT Status#RULESET R-status|the embedded block]]. 10 rules covering file name, location, body-only shape, `description::` line, per-facet declared-order lines, cell-value ladder, date format, `*-user` note requirement, Track-dispatch wiring, and monotonic-promotion.

## Adoption

Adopted transitively via [[R-facet]] — `include:: [[R-facet]]` pulls every materialized per-facet rule set including this one.

## See also

- [[FCT Status]] — facet spec; contains the embedded RULESET body.
- [[R-facet]] — parent umbrella.
- [[R-testing]] — sibling materialized facet rule set.
- [[Rule Sets]] — top-level catalog.
