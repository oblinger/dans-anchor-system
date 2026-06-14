# RULESET R-file-association
include:: [[DSC file-association#RULESET R-file-association|embedded body]]
description:: Catalog stub — the general pattern for attaching typed content to a parent doc or anchor (the three placement methods, cardinality-drives-placement, suffix naming, one-way migration, one-form-per-parent, parent linkage). Canonical body lives embedded in [[DSC file-association]].

Catalog-side stub for the file-association discipline's ruleset. The canonical body lives embedded inside the [[DSC file-association]] discipline file per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[DSC file-association#RULESET R-file-association|the embedded block]]. 7 rules covering:

- **Methods (1)** — exactly three named placement methods (inline H1 / sibling file / sibling folder).
- **Cardinality (1)** — cardinality drives placement (one → inline; few → sibling file; many → sibling folder).
- **Naming (1)** — parent prefix + plural facet suffix when extracted.
- **Migration (1)** — one-way `1 → 2 → 3`; reverse only as a deliberate refactor.
- **Coexistence (1)** — one form per parent at a time.
- **Linkage (1)** — dispatch row in the parent doc when extracted.
- **Sibling-folder shape (1)** — anchor file inside the folder + per-member files.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella) and applies to every document (`always`). It is the **general** typed-association pattern; its dated specialization [[R-dated-entry-stream]] inherits these rules and adds reverse-chronological + ISO-naming extras.

## Adoption

A convention set on the `R-doc` umbrella — pulled into **`/audit doc`** via `R-doc`'s `include::` line. Citing disciplines/facets reference it explicitly where they constrain attachment (e.g. [[DSC dated-entry-stream]] delegates its general placement rules here).

## See also

- [[DSC file-association]] — discipline spec; contains the embedded RULESET body.
- [[DSC dated-entry-stream]] — dated specialization that inherits this ruleset.
- [[R-doc]] — documentation-conventions catalog row this stub sits under.
- [[R-dated-entry-stream]] — the dated sub-discipline's stub.
- [[Rulesets]] — top-level catalog.
