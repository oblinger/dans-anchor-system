# RULESET R-dated-entry-stream
include:: [[DSC dated-entry-stream#RULESET R-dated-entry-stream|embedded body]]
description:: Catalog stub — rules for streams of dated, typed, reverse-chronological entries attached to a parent doc or anchor. Canonical body lives embedded in [[DSC dated-entry-stream]].

Catalog-side stub for the dated-entry-stream sub-discipline's ruleset. The canonical body lives embedded inside the [[DSC dated-entry-stream]] discipline file per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[DSC dated-entry-stream#RULESET R-dated-entry-stream|the embedded block]]. 3 rules — the **dated extras** only; the general placement rules (methods, cardinality, naming, migration, one-form, linkage, sibling-folder shape) are **inherited from [[R-file-association]]** (per F154) and not repeated here:

- **Order (1)** — reverse chronological, newest-first, prepend-immutable.
- **Entry shape (1)** — parallel entry skeleton declared by the citing facet; uniformity enforced within a facet's stream.
- **Dated naming (1)** — ISO date prefix for method-3 entry files.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella). Sub-discipline of [[DSC file-association]] (the broader umbrella covering structural patterns for attaching content to a parent). Cited by every facet whose content is a dated entry stream: [[FCT Discussion]] today; [[FCT Log]] pending refactor.

## Adoption

This ruleset is cited explicitly by each facet that uses it (in their `R-<facet>` block, via a delegation note). Not pulled by the [[R-facet]] umbrella — it is a discipline ruleset, not a per-facet ruleset.

## See also

- [[DSC dated-entry-stream]] — sub-discipline spec; contains the embedded RULESET body.
- [[DSC file-association]] — parent umbrella discipline.
- [[R-doc]] — documentation-conventions catalog row this stub sits under.
- [[FCT Discussion]] — citing facet (doc-scoped, methods 1 + 2).
- [[FCT Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[Rulesets]] — top-level catalog.
