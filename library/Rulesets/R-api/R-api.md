# RULESET R-api
include:: [[FCT API Design#RULESET R-api|embedded body]]
description:: Catalog stub — rules for `{NAME} API Design.md`, the *programmatic* user-facing surface intent. Canonical body lives embedded in [[FCT API Design]].

Catalog-side stub for the API Design facet's ruleset. The canonical body lives embedded inside the [[FCT API Design]] facet file per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[FCT API Design#RULESET R-api|the embedded block]]. 9 rules covering:

- **Preface (1)** — TLDR + optional figure (schema diagram, sequence, or canonical code snippet).
- **Spine (2)** — Consumer declared, Surface spine table covers every public callable / endpoint / sub-skill entry.
- **Behavior + envelope (2)** — Contract semantics named (idempotency, side-effects, concurrency, deadlines); single error envelope across the surface.
- **Stability + compatibility (2)** — Stability posture + version scheme declared; compatibility commitments concrete (measurable horizons, not "we'll try").
- **Rationale + scope (2)** — D-API rows for load-bearing decisions; leakage guard against API Doc / Architecture / UX Design content.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). Paired peer to [[R-ux]] — both fire when the anchor has a public user surface; the cut is programmatic vs human consumer. Distinct from R-api-doc (per-module reference rules; pending).

## Adoption

Pulled automatically via the [[R-facet]] umbrella; an anchor adopting `include:: [[R-facet]]` gets R-api for free. No explicit `include:: [[R-api]]` needed.

## See also

- [[FCT API Design]] — facet spec; contains the embedded RULESET body.
- [[R-ux]] — paired peer ruleset for human surface.
- [[R-facet]] — umbrella catalog.
- [[CAE API Design]] — worked example.
- [[FCT API Doc]] — distinct facet covering per-module reference documentation (different altitude — intent vs reference).
- [[Rulesets]] — top-level catalog.
