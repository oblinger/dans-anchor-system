# RULESET R-dated-entry-stream
include:: [[dated-entry-stream#RULESET R-dated-entry-stream|embedded body]]
description:: Catalog stub — rules for streams of dated, typed, reverse-chronological entries attached to a parent doc or anchor. Canonical body lives embedded in [[dated-entry-stream]].

Catalog-side stub for the dated-entry-stream sub-discipline's rule set. The canonical body lives embedded inside the [[dated-entry-stream]] discipline file per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[dated-entry-stream#RULESET R-dated-entry-stream|the embedded block]]. 9 rules covering:

- **Methods (1)** — exactly three placement methods (inline H1 / sibling file / sibling folder).
- **Naming (1)** — parent name + plural facet suffix when extracted; ISO date prefix for method-3 entry files.
- **Migration (1)** — one-way `1 → 2 → 3`; reverse only as deliberate refactor.
- **Coexistence (1)** — one form per parent at a time.
- **Order (1)** — reverse chronological, newest first.
- **Entry shape (1)** — parallel skeleton declared by the citing facet; uniformity enforced within a facet's stream.
- **Linkage (1)** — dispatch row in parent doc when extracted.
- **Method 3 shape (1)** — anchor file inside folder + per-entry dated files.
- **Facet declaration (1)** — every citing facet declares supported methods + default.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella). Sub-discipline of [[file-association]] (the broader umbrella covering structural patterns for attaching content to a parent). Cited by every facet whose content is a dated entry stream: [[CAB Discussion]] today; [[CAB Log]] pending refactor.

## Adoption

This rule set is cited explicitly by each facet that uses it (in their `R-<facet>` block, via a delegation note). Not pulled by the [[R-facet]] umbrella — it is a discipline rule set, not a per-facet rule set.

## See also

- [[dated-entry-stream]] — sub-discipline spec; contains the embedded RULESET body.
- [[file-association]] — parent umbrella discipline.
- [[R-doc]] — documentation-conventions catalog row this stub sits under.
- [[CAB Discussion]] — citing facet (doc-scoped, methods 1 + 2).
- [[CAB Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[Rule Sets]] — top-level catalog.
