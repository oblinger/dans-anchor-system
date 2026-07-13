# RULESET R-naming
include:: [[DAS Naming#RULESET R-naming\|embedded body]]
description:: File-naming rules vault-wide — slug-prefix default + explicit exception allowlist.

Catalog-side stub for the Naming facet ruleset. Canonical body lives embedded inside [[DAS Naming]] per [[F133 — Rulesets folder convention + facet embedding|F133]].

**To see the actual rules:** follow [[DAS Naming#RULESET R-naming|the embedded block]]. 5 rules covering: default `{slug} <X>.md` form inside anchors, vault-global exemption (Atlas, MY, etc.), facet-sanctioned unique patterns allowlist (F-numbers, `US-<slug>-<N>`, ISO dates per CAB Features / Stories / Log), slug-prefix-sufficient-by-chance escape valve, folder-anchor marker-file matches folder name.

## Adoption

Vault-wide — every anchor's files are subject to this set, no explicit `include::` required in `{slug} Decisions.md`. Listed in the catalog for completeness.

## See also

- [[DAS Naming]] — facet spec; contains the embedded RULESET body.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
- F141 (future R-anchor umbrella) — would collect R-naming + R-folder + R-anchor-page + R-files when those rulesets exist.
