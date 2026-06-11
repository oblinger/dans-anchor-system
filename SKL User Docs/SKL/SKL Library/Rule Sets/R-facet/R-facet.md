# RULESET R-facet
include:: [[R-testing]], [[R-status]], [[R-log]]
description:: Umbrella rule set aggregating the per-facet rule sets embedded in CAB facet spec files.

Per the 2026-06-09 design decision, each CAB facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file is the catalog-side umbrella that walks all those embedded rule sets via `include::` so adopters get a single name to pull. An anchor that adopts R-facet commits to following every materialized CAB facet's structural rules.

**Materialization progress.** The `include::` line above grows as each facet's RULESET block lands. Currently:

- **R-testing** ([[CAB Testing]]) — first worked example, landed 2026-06-10. 9 rules covering facet doc shape (file name, Strategy + Proposed Tests sections, kind-target symmetry, three-altitude split, status field, Tier Mapping cites [[verification]]).

Pending — each lands as its CAB facet's RULESET block is drafted: R-prd, R-architecture, R-ux, R-decisions, R-rules, R-roadmap, R-features, R-backlog, R-cli, R-api-doc, … (40 CAB facets total; rollout deferred to a dedicated sweep, tracked separately).

## Adoption

```markdown
# {NAME} Decisions
include:: [[R-facet]]
```

This single include pulls in every CAB facet's structural rules. Audit walks the included sets and verifies the anchor's facet files satisfy them. Use cases:

- A new anchor that wants to be CAB-conformant: one-liner adoption.
- An audit pass that checks every facet file's structure in one walk.
- Cherry-pick override: include `R-facet` AND override individual facet rules in the anchor's `{NAME} Rules.md`.

## See also

- [[CAB Rules]] — meta-spec for the RULESET format; first facet expected to land an embedded `R-rules` block.
- [[CAB Decisions]] — the master adoption file in an anchor; this is where `include:: [[R-facet]]` belongs.
- [[Rule Sets]] — parent catalog.
