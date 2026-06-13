# RULESET R-facet
include:: [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]], [[R-naming]], [[R-roadmap]], [[R-completed-roadmap]], [[R-ux]], [[R-api]], [[R-discussion]]
description:: Umbrella rule set aggregating the per-facet rule sets embedded in CAB facet spec files.

Per the 2026-06-09 design decision, each CAB facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file is the catalog-side umbrella that walks all those embedded rule sets via `include::` so adopters get a single name to pull. An anchor that adopts R-facet commits to following every materialized CAB facet's structural rules.

**Materialization progress.** The `include::` line above grows as each facet's RULESET block lands. Currently:

- **R-testing** ([[FCT Testing]]) — first worked example, landed 2026-06-10. 9 rules covering facet doc shape (file name, Strategy + Proposed Tests sections, kind-target symmetry, three-altitude split, status field, Tier Mapping cites [[DSC verification]]).

- **R-ux** ([[FCT UX Design]]) — paired peer to R-api, landed 2026-06-11. 8 rules covering preface zone, audience, entry-points spine, output shapes, error voice, discovery, D-UX rationale rows, and the leakage guard distinguishing UX Design from API Design / CLI / Architecture.
- **R-api** ([[FCT API Design]]) — paired peer to R-ux, landed 2026-06-11. 9 rules covering preface zone, consumer, surface spine, contract semantics, single error envelope, stability posture, concrete compatibility commitments, D-API rationale rows, and the leakage guard.
- **R-discussion** ([[FCT Discussion]]) — first *doc-scoped* (per document, not per anchor) facet rule set, landed 2026-06-11. Trimmed to 5 Discussion-specific rules after placement / migration / naming / one-form-per-parent / reverse-chronological / dispatch-linkage rules were lifted into [[DSC dated-entry-stream]] (the discipline Discussion cites). Remaining rules: doc-scoped not anchor-scoped, methods-1-and-2-declared, Problem/Options/Decision entry skeleton, append-only after Decision, attachment scope guard.

Pending — each lands as its CAB facet's RULESET block is drafted: R-architecture, R-decisions, R-rules, R-features, R-backlog, R-cli, R-api-doc, … (40 CAB facets total; rollout deferred to a dedicated sweep, tracked separately).

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

- [[FCT Rule Set]] — meta-spec for the RULESET format; first facet expected to land an embedded `R-rules` block.
- [[FCT Decisions]] — the master adoption file in an anchor; this is where `include:: [[R-facet]]` belongs.
- [[Rule Sets]] — parent catalog.
