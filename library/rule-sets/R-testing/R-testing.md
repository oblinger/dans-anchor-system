# RULESET R-testing
include:: [[FCT Testing#RULESET R-testing\|embedded body]]
description:: Rules for the {NAME} Testing.md facet doc; canonical body lives embedded in CAB Testing.md.

Catalog-side stub for the Testing facet rule set. Per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention, the actual rules are co-located with their facet spec — defined as a `# RULESET R-testing` second-H1 block inside [[FCT Testing]] alongside the prose that motivates them. This file exists so the catalog-side wiring (`R-facet` include::, `Rule Sets.md` dispatch row) has a clean `[[R-testing]]` wiki-link to point at, parallel to how [[R-facet]], [[R-trait]], [[R-skill]] are catalog-side umbrella stubs.

**To see the actual rules:** follow [[FCT Testing#RULESET R-testing|the embedded block]]. There are 9 rules covering file naming, Strategy section shape, Proposed Tests grouping by kind, kind-target symmetry, three-altitude split (link/bracket Spec column, never inlined low-level specs), `status::` frontmatter field, and Tier Mapping citing [[DSC verification]].

## Adoption

Adopted transitively via [[R-facet]] — `include:: [[R-facet]]` in an anchor's `{NAME} Decisions.md` pulls every materialized per-facet rule set including this one.

Direct adoption (if an anchor wants only the Testing rules without the rest of R-facet):

```markdown
# {NAME} Decisions
include:: [[R-testing]]
```

## See also

- [[FCT Testing]] — facet spec; contains the embedded RULESET body.
- [[CAE Testing]] — worked example that conforms to R-testing.
- [[R-facet]] — parent umbrella; pulls R-testing alongside future per-facet sets.
- [[Rule Sets]] — top-level catalog.
- [[F133 — Rule sets folder convention + facet embedding]] — the convention this file follows.
