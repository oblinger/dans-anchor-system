# RULESET R-markdown
include:: [[DSC markdown#RULESET R-markdown\|embedded body]]
description:: Mechanical + authoring rules for every markdown document; cited by every facet and skill that produces markdown.

Catalog-side stub for the markdown discipline's ruleset. Canonical body lives embedded inside the [[DSC markdown]] discipline file per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[DSC markdown#RULESET R-markdown|the embedded block]]. 10 rules covering:

- **Mechanical (5)** — pipe-escape in table wiki-links, blank-line-around-tables, no-markdown-in-fences, em-dash character, dataview `::` collision.
- **Authoring (5)** — vault refs use wiki-links not backticks, body-only preference, no wiki-link form for code identifiers, definition-list shape, per-anchor docs don't restate facet rules.

## Position in the catalog

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella). [[R-md]] (the older "markdown rendering" ruleset under R-doc) is **superseded** by R-markdown — F139 sweeps remaining `[[R-md]]` citations.

## Adoption

Applies to every markdown doc in the vault — no explicit `include:: [[R-markdown]]` required in `{NAME} Decisions.md`. (Listed in the catalog for completeness; vault-wide rules don't need per-anchor opt-in.)

## See also

- [[DSC markdown]] — discipline spec; contains the embedded RULESET body.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[R-md]] — predecessor; superseded by R-markdown per F139.
- [[DSC progressive-disclosure]] — sibling discipline; its rules live separately (preface zone, dispatch patterns, figure placement).
- [[Rulesets]] — top-level catalog.
