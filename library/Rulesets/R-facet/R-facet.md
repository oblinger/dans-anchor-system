# RULESET R-facet
include:: [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]], [[R-naming]], [[R-roadmap]], [[R-completed-roadmap]], [[R-ux]], [[R-api]], [[R-discussion]], [[R-cli]], [[R-code-repository]], [[R-anchor-group]], [[R-code-surface]], [[R-module-doc]], [[R-design-docs-group]], [[R-dev-dispatch]], [[R-dispatch-group]], [[R-doc-facet]], [[R-cards]], [[R-documentation-site]], [[R-output-group]], [[R-wp]], [[R-skill-md]], [[R-track-group]], [[R-ruleset]]
description:: Umbrella ruleset aggregating the per-facet rulesets embedded in CAB facet spec files.

Per the 2026-06-09 design decision, each CAB facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file is the catalog-side umbrella that walks all those embedded rulesets via `include::` so adopters get a single name to pull. An anchor that adopts R-facet commits to following every materialized CAB facet's structural rules.

**Materialization progress.** The `include::` line above grows as each facet's RULESET block lands. Currently:

- **R-testing** ([[FCT Testing]]) — first worked example, landed 2026-06-10. 9 rules covering facet doc shape (file name, Strategy + Proposed Tests sections, kind-target symmetry, three-altitude split, status field, Tier Mapping cites [[DSC verification]]).

- **R-ux** ([[FCT UX Design]]) — paired peer to R-api, landed 2026-06-11. 8 rules covering preface zone, audience, entry-points spine, output shapes, error voice, discovery, D-UX rationale rows, and the leakage guard distinguishing UX Design from API Design / CLI / Architecture.
- **R-api** ([[FCT API Design]]) — paired peer to R-ux, landed 2026-06-11. 9 rules covering preface zone, consumer, surface spine, contract semantics, single error envelope, stability posture, concrete compatibility commitments, D-API rationale rows, and the leakage guard.
- **R-discussion** ([[FCT Discussion]]) — first *doc-scoped* (per document, not per anchor) facet ruleset, landed 2026-06-11. Trimmed to 5 Discussion-specific rules after placement / migration / naming / one-form-per-parent / reverse-chronological / dispatch-linkage rules were lifted into [[DSC dated-entry-stream]] (the discipline Discussion cites). Remaining rules: doc-scoped not anchor-scoped, methods-1-and-2-declared, Problem/Options/Decision entry skeleton, append-only after Decision, attachment scope guard.

- **F137 sweep (landed)** — 15 more facets gained embedded RULESET blocks in one pass: `R-cli` ([[FCT CLI]]), `R-code-repository` ([[FCT Code Repository]]), `R-module-doc` ([[FCT Module Doc]]), `R-code-surface` ([[FCT Code]] — the All-Files↔module-doc pairing ruleset; named `R-code-surface` because the slug `R-code` is already the language/platform code-rulesets umbrella; itself includes `R-module-doc`), `R-dev-dispatch` ([[FCT Dev Dispatch]]), `R-doc-facet` ([[FCT Doc]]), `R-cards` ([[FCT Cards]]), `R-documentation-site` ([[FCT Documentation Site]]), `R-wp` ([[FCT WP]]), `R-skill-md` ([[FCT Skill]] — the SKILL.md *file-format* ruleset; named `R-skill-md` because the umbrella slug `R-skill` is already the per-skill aggregator), plus the five facet-**group** index pages whose only honest rule is family-membership completeness: `R-anchor-group` ([[FCT Anchor]]), `R-design-docs-group` ([[FCT Design Docs]]), `R-dispatch-group` ([[FCT Dispatch]]), `R-output-group` ([[FCT Output]]), `R-track-group` ([[FCT Track]]).

- **R-ruleset** ([[FCT Ruleset]]) — the self-applying format ruleset (the meta-spec for `# RULESET` blocks and `{NAME} Rules.md` files); embedded in [[FCT Ruleset]] and added to the umbrella in the F137/F133 pass. (This is the set the older notes called "`R-rules`" — its actual slug is `R-ruleset`, since it governs *ruleset* files.)

Pending — each lands as its CAB facet's RULESET block is drafted: R-architecture, R-decisions, R-features, R-backlog, … (rollout continues per facet; tracked separately).

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

- [[FCT Ruleset]] — meta-spec for the RULESET format; carries the embedded `R-ruleset` block (the self-applying format ruleset), now in the umbrella.
- [[FCT Decisions]] — the master adoption file in an anchor; this is where `include:: [[R-facet]]` belongs.
- [[Rulesets]] — parent catalog.
