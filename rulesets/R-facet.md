# RULESET R-facet
include:: [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]], [[R-naming]], [[R-roadmap]], [[R-completed-roadmap]], [[R-ux]], [[R-api]], [[R-discussion]], [[R-cli]], [[R-code-repository]], [[R-anchor-group]], [[R-code-surface]], [[R-module-doc]], [[R-design-docs-group]], [[R-dev-dispatch]], [[R-dispatch-group]], [[R-doc-facet]], [[R-cards]], [[R-documentation-site]], [[R-output-group]], [[R-wp]], [[R-skill-md]], [[R-track-group]], [[R-ruleset]], [[R-backlog]]
description:: Umbrella ruleset aggregating the per-facet rulesets embedded in DAS facet spec files.

Per the 2026-06-09 design decision, each DAS facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file is the catalog-side umbrella that walks all those embedded rulesets via `include::` so adopters get a single name to pull. An anchor that adopts R-facet commits to following every materialized DAS facet's structural rules.

**Materialization progress.** The `include::` line above grows as each facet's RULESET block lands. Currently:

- **R-testing** ([[DAS Testing]]) — first worked example, landed 2026-06-10. 9 rules covering facet doc shape (file name, Strategy + Proposed Tests sections, kind-target symmetry, three-altitude split, status field, Tier Mapping cites [[DAS verification]]).

- **R-ux** ([[DAS UX Design]]) — paired peer to R-api, landed 2026-06-11. 8 rules covering preface zone, audience, entry-points spine, output shapes, error voice, discovery, D-UX rationale rows, and the leakage guard distinguishing UX Design from API Design / CLI / Architecture.
- **R-api** ([[DAS API Design]]) — paired peer to R-ux, landed 2026-06-11. 9 rules covering preface zone, consumer, surface spine, contract semantics, single error envelope, stability posture, concrete compatibility commitments, D-API rationale rows, and the leakage guard.
- **R-discussion** ([[DAS Discussion]]) — first *doc-scoped* (per document, not per anchor) facet ruleset, landed 2026-06-11. Trimmed to 5 Discussion-specific rules after placement / migration / naming / one-form-per-parent / reverse-chronological / dispatch-linkage rules were lifted into [[DAS dated-entry-stream]] (the discipline Discussion cites). Remaining rules: doc-scoped not anchor-scoped, methods-1-and-2-declared, Problem/Options/Decision entry skeleton, append-only after Decision, attachment scope guard.

- **F137 sweep (landed)** — 15 more facets gained embedded RULESET blocks in one pass: `R-cli` ([[DAS CLI]]), `R-code-repository` ([[DAS Code Repository]]), `R-module-doc` ([[DAS Module Doc]]), `R-code-surface` ([[DAS Code]] — the All-Files↔module-doc pairing ruleset; named `R-code-surface` because the slug `R-code` is already the language/platform code-rulesets umbrella; itself includes `R-module-doc`), `R-dev-dispatch` ([[DAS Dev Dispatch]]), `R-doc-facet` ([[DAS Doc]]), `R-cards` ([[DAS Cards]]), `R-documentation-site` ([[DAS Documentation Site]]), `R-wp` ([[DAS WP]]), `R-skill-md` ([[DAS Skill]] — the SKILL.md *file-format* ruleset; named `R-skill-md` because the umbrella slug `R-skill` is already the per-skill aggregator), plus the five facet-**group** index pages whose only honest rule is family-membership completeness: `R-anchor-group` ([[DAS Anchor]]), `R-design-docs-group` ([[DAS Design Docs]]), `R-dispatch-group` ([[DAS Dispatch]]), `R-output-group` ([[DAS Output]]), `R-track-group` ([[DAS Track]]).

- **R-ruleset** ([[DAS Ruleset]]) — the self-applying format ruleset (the meta-spec for `# RULESET` blocks and `{slug} Rules.md` files); embedded in [[DAS Ruleset]] and added to the umbrella in the F137/F133 pass. (This is the set the older notes called "`R-rules`" — its actual slug is `R-ruleset`, since it governs *ruleset* files.)

- **R-backlog** ([[DAS Backlog]]) — the F228 frontier invariants, landed 2026-07-05. 4 rules: the groom-frontier definition (Now + Next + next roadmap milestone), frontier `[Ready]`/`[Active]` rows declare a `Next:` step, `## Now`/`## Next` rows are bracket-resolved, `[Verify*]`/`[Watching*]` rows carry a concrete `Verify:` question. Also in the [[R-doc]] umbrella (fires on `* Backlog.md` by `where::`).

Pending — each lands as its DAS facet's RULESET block is drafted: R-architecture, R-decisions, R-features, … (rollout continues per facet; tracked separately).

## Adoption

```markdown
# {slug} Decisions
include:: [[R-facet]]
```

This single include pulls in every DAS facet's structural rules. Audit walks the included sets and verifies the anchor's facet files satisfy them. Use cases:

- A new anchor that wants to be CAB-conformant: one-liner adoption.
- An audit pass that checks every facet file's structure in one walk.
- Cherry-pick override: include `R-facet` AND override individual facet rules in the anchor's `{slug} Rules.md`.

## See also

- [[DAS Ruleset]] — meta-spec for the RULESET format; carries the embedded `R-ruleset` block (the self-applying format ruleset), now in the umbrella.
- [[DAS Decisions]] — the master adoption file in an anchor; this is where `include:: [[R-facet]]` belongs.
- [[DAS Rulesets]] — parent catalog.
