# RULESET R-ux
include:: [[FCT UX Design#RULESET R-ux|embedded body]]
description:: Catalog stub — rules for `{NAME} UX Design.md`, the *human* user-facing surface intent. Canonical body lives embedded in [[FCT UX Design]].

Catalog-side stub for the UX Design facet's rule set. The canonical body lives embedded inside the [[FCT UX Design]] facet file per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[FCT UX Design#RULESET R-ux|the embedded block]]. 8 rules covering:

- **Preface (1)** — TLDR + figure (annotated session transcript for CLI, mockup for GUI, snippet for slash surfaces).
- **Spine (3)** — Audience declared, Entry-points spine table, Output shapes named in both human + structured form.
- **Voice + discovery (2)** — Error voice declared once with envelope; Discovery mechanism named.
- **Rationale + scope (2)** — D-UX rows for load-bearing decisions; leakage guard against API Design / CLI / Architecture content.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). Paired peer to [[R-api]] — both fire when the anchor has a public user surface; the cut is human vs programmatic consumer.

## Adoption

Pulled automatically via the [[R-facet]] umbrella; an anchor adopting `include:: [[R-facet]]` gets R-ux for free. No explicit `include:: [[R-ux]]` needed.

## See also

- [[FCT UX Design]] — facet spec; contains the embedded RULESET body.
- [[R-api]] — paired peer rule set for programmatic surface.
- [[R-facet]] — umbrella catalog.
- [[CAE UX Design]] — worked example.
- [[Rule Sets]] — top-level catalog.
