# RULESET R-log
include:: [[DAS Log#RULESET R-log\|embedded body]]
description:: Rules for the {slug} Log facet — folder shape, entry filenames, dispatch table, content scope.

Catalog-side stub for the Log facet ruleset. Canonical body lives embedded inside [[DAS Log]] per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[DAS Log#RULESET R-log|the embedded block]]. 9 rules covering: path location, dispatch-file presence, entry filename `YYYY-MM-DD <topic>` pattern, no-spec-content discipline, newest-first dispatch ordering, append-only history, no Brief restating facet rules, anchor-page link, sub-anchor scoping.

## Adoption

Adopted transitively via [[R-facet]] — `include:: [[R-facet]]` pulls every materialized per-facet ruleset including this one.

## See also

- [[DAS Log]] — facet spec; contains the embedded RULESET body.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
