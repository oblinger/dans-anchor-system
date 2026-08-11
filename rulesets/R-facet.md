# RULESET R-facet
include:: [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]], [[R-naming]], [[R-roadmap]], [[R-completed-roadmap]], [[R-ux]], [[R-api]], [[R-discussion]], [[R-cli]], [[R-code-repository]], [[R-anchor-group]], [[R-code-surface]], [[R-module-doc]], [[R-design-docs-group]], [[R-dev-dispatch]], [[R-dispatch-group]], [[R-doc-facet]], [[R-cards]], [[R-documentation-site]], [[R-output-group]], [[R-wp]], [[R-skill-md]], [[R-track-group]], [[R-ruleset]], [[R-backlog]], [[R-rocks]], [[R-stone]] 
description:: Umbrella ruleset aggregating the per-facet rulesets embedded in DAS facet spec files.

Per the 2026-06-09 design decision, each DAS facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file walks all those embedded rulesets via `include::`, so it is the one place to read what the per-facet layer *contains*.

> **This umbrella is a catalog. It arms nothing, and for most of its life it claimed otherwise.** `audit-plan.py` resolves a **fixed** umbrella — [[R-doc]] in doc mode, [[R-anchor]] in anchor mode — and **nothing reads a per-anchor ruleset declaration**, so `include:: [[R-facet]]` in a `{slug} Decisions.md` has no reader and never had one. Adding a set to the `include::` line above therefore changes nothing that runs. Measured 2026-08-11 ([[TINK Backlog#^T208|T208]], `--verify-registry`): of the **33** rulesets this file flattens to, **16 are armed by another route** and **17 are armed by nothing at all** — `R-api`, `R-ux`, `R-cli`, `R-cards`, `R-module-doc`, `R-code-surface`, `R-code-repository`, `R-skill-md`, `R-doc-facet`, `R-documentation-site`, `R-dev-dispatch`, `R-completed-roadmap`, and the five facet-group sets. Those 17 carry rules, some read `(checked)`, and not one has ever entered a plan.
>
> **The failure mode is that this looks exactly like adoption.** The recipe lists the rules, the tier reads `(checked)`, the audit runs green, and no rule fires — so a green sweep is evidence of nothing. [[R-anchor]] § records the same diagnosis from the T164 side, and [[DAS Stone]] § is the worked example: `R-stone` was added here, measured, and found inert, then armed for real by naming it in `R-anchor`.
>
> **To arm a set, name it in [[R-doc]] or [[R-anchor]]** — `R-doc` when it fires on a document kind, `R-anchor` when it fires on an anchor's shape — and measure the blast radius first. A dormant set meeting the live corpus is where a finding count comes from, not where it stays.

**Materialization progress.** The `include::` line above grows as each facet's RULESET block lands. Currently:

- **R-testing** ([[DAS Testing]]) — first worked example, landed 2026-06-10. 9 rules covering facet doc shape (file name, Strategy + Proposed Tests sections, kind-target symmetry, three-altitude split, status field, Tier Mapping cites [[DAS verification]]).

- **R-ux** ([[DAS UX Design]]) — paired peer to R-api, landed 2026-06-11. 8 rules covering preface zone, audience, entry-points spine, output shapes, error voice, discovery, D-UX rationale rows, and the leakage guard distinguishing UX Design from API Design / CLI / Architecture.
- **R-api** ([[DAS API Design]]) — paired peer to R-ux, landed 2026-06-11. 9 rules covering preface zone, consumer, surface spine, contract semantics, single error envelope, stability posture, concrete compatibility commitments, D-API rationale rows, and the leakage guard.
- **R-discussion** ([[DAS Discussion]]) — first *doc-scoped* (per document, not per anchor) facet ruleset, landed 2026-06-11. Trimmed to 5 Discussion-specific rules after placement / migration / naming / one-form-per-parent / reverse-chronological / dispatch-linkage rules were lifted into [[DAS stream]] (the discipline Discussion cites). Remaining rules: doc-scoped not anchor-scoped, methods-1-and-2-declared, Problem/Options/Decision entry skeleton, append-only after Decision, attachment scope guard.

- **F137 sweep (landed)** — 15 more facets gained embedded RULESET blocks in one pass: `R-cli` ([[DAS CLI]]), `R-code-repository` ([[DAS Code Repository]]), `R-module-doc` ([[DAS Module Doc]]), `R-code-surface` ([[DAS Code]] — the All-Files↔module-doc pairing ruleset; named `R-code-surface` because the slug `R-code` is already the language/platform code-rulesets umbrella; itself includes `R-module-doc`), `R-dev-dispatch` ([[DAS Dev Dispatch]]), `R-doc-facet` ([[DAS Doc]]), `R-cards` ([[DAS Cards]]), `R-documentation-site` ([[DAS Documentation Site]]), `R-wp` ([[DAS WP]]), `R-skill-md` ([[DAS Skill]] — the SKILL.md *file-format* ruleset; named `R-skill-md` because the umbrella slug `R-skill` is already the per-skill aggregator), plus the five facet-**group** index pages whose only honest rule is family-membership completeness: `R-anchor-group` ([[DAS Anchor]]), `R-design-docs-group` ([[DAS Design Docs]]), `R-dispatch-group` ([[DAS Dispatch]]), `R-output-group` ([[DAS Output]]), `R-track-group` ([[DAS Track]]).

- **R-ruleset** ([[DAS Ruleset]]) — the self-applying format ruleset (the meta-spec for `# RULESET` blocks and `{slug} Rules.md` files); embedded in [[DAS Ruleset]] and added to the umbrella in the F137/F133 pass. (This is the set the older notes called "`R-rules`" — its actual slug is `R-ruleset`, since it governs *ruleset* files.)

- **R-backlog** ([[DAS Backlog]]) — the F228 frontier invariants, landed 2026-07-05. 4 rules: the groom-frontier definition (Now + Next + next roadmap milestone), frontier `[Ready]`/`[Active]` rows declare a `Next:` step, `## Now`/`## Next` rows are bracket-resolved, `[Verify*]`/`[Watching*]` rows carry a concrete `Verify:` question. Also in the [[R-doc]] umbrella (fires on `* Backlog.md` by `where::`).

- **R-stone** ([[DAS Stone]]) — the kind-generic generalisation of R-rocks, landed 2026-08-11. 6 rules, of which 4 are `checked`: group location + control file, stone numbering, header-identified-by-link-target, and keys-above-prose. The other two stay `stated` permanently — one asserts what the `stone` mint *refuses* and one forbids *deriving* a prefix from a kind's name; neither is content of any file. Nothing in the checkers names `pebble` or `rock`: every per-kind fact comes from `DAS Stone Kinds.json`, so a new kind needs only its folder shape added to the ruleset's `where::`. Overlaps [[R-rocks]] on folder name and location for the rock kind — deliberate, and consolidating is filed separately because it means touching the tier annotations that have twice folded a checker onto the wrong rule there.

Pending — each lands as its DAS facet's RULESET block is drafted: R-architecture, R-decisions, R-features, … (rollout continues per facet; tracked separately).

## Adoption

**There is no adoption.** This section used to document a one-liner — `include:: [[R-facet]]` in an anchor's `{slug} Decisions.md` — as the way a new anchor became CAB-conformant in one move. No code has ever read that line. It is removed rather than corrected in place, because a documented recipe that quietly does nothing is worse than an absent one: three separate defects ([[TINK Backlog#^T164|T164]], [[DAS Stone]]'s inert arming, [[TINK Backlog#^T208|T208]]) each began with an agent following it and reasonably concluding the facet was covered.

What the three use cases it advertised actually need today:

- **A new anchor that wants every facet rule** — nothing to do, and nothing available to do. Whatever [[R-anchor]] names applies to every anchor already; whatever it does not name applies to none of them. Anchor-selective rule adoption is not a feature this engine has.
- **An audit pass over every facet file** — `/audit anchor`, which resolves [[R-anchor]]. Its coverage is exactly `R-anchor`'s closure, not this file's list.
- **Cherry-pick override** — still real, and still through the anchor's `{slug} Rules.md`; it overrides rules that are already firing, so it is unaffected by any of this.

## See also

- [[DAS Ruleset]] — meta-spec for the RULESET format; carries the embedded `R-ruleset` block (the self-applying format ruleset), now in the umbrella.
- [[R-anchor]] — the umbrella `/audit anchor` resolves, and the only place adding a set arms it for an anchor. Carries the T164 statement of this same defect.
- [[R-doc]] — the umbrella `/audit doc` and the on-write doc-fire resolve; the doc-kind half of the same answer.
- [[DAS Rulesets]] — parent catalog.
