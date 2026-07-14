---
description: "Curated, versioned bundles of rules."
---

# Rulesets

| -[[DAS Rulesets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Rulesets](hook://p/DAS%20Rulesets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| Related | [[Rulesets Brief\|Brief]],  [[DAS Ruleset]],  [[DAS Decisions]],   |
| **CAB-aligned umbrellas** | The three primary structural axes — rulesets tied to CAB Facets, Traits, Skills. Adopting an umbrella pulls every per-X ruleset under it. |
| [[R-facet]] | Per-facet rulesets. Each child lives as its own `rulesets/R-<facet>.md` file (bodies migrated out of the facet specs 2026-07-13); the facet spec links it from its masthead `Rules` row. Children: [[R-testing]] (9 rules), [[R-status]] (10 rules), [[R-log]] (9 rules), [[R-stories]] (9 rules), [[R-prd]] (9 rules), [[R-design]] (7 rules), [[R-naming]] (5 rules), [[R-roadmap]] (11 rules), [[R-completed-roadmap]] (6 rules), [[R-ux]] (8 rules), [[R-api]] (9 rules), [[R-discussion]] (9 rules — first doc-scoped facet). Remaining ~40 facets to populate via dedicated sweep. |
| [[R-trait]] | Per-trait rulesets — to embed in `traits/<Trait>.md` specs. Children: [[R-paper]], [[R-simple]], [[R-skill-anchor]], [[R-topic]]. |
| [[R-skill]] | Per-skill rulesets — to embed in `~/.claude/skills/<skill>/SKILL.md` specs. First candidates: R-ask, R-feature, R-atlas. |
| **Cross-cutting** | Not tied to a specific facet, trait, or skill. Pulled in when explicitly opted into. |
| [[R-arch]] | Architecture rules — **umbrella over 5 mined design-rule families, 15 rules total** (F218, upgraded 2026-07-05): [[R-single-source-of-truth]] (3), [[R-one-path]] (3), [[R-interfaces-folder]] (3), [[R-factory-pegboard]] (3), [[R-ownership]] (3). Each carries ≥3-project recurrence evidence; adoption stays per-application by `.anchor` trait. |
| [[R-code]] | Code-flavored rulesets — language/platform conventions. Contains [[R-mac]]. Future: `R-rust`, `R-python`, `R-typescript`, `R-shell`. |
| [[R-diagram]] | Diagram authoring + validation — **umbrella over 7 methodology sub-sets, 22 rules total**: [[R-diagram-geometry]] (6), [[R-sugiyama]] (4), [[R-c4]] (4), [[R-wcag-contrast]] (2), [[R-bringhurst-typography]] (1), [[R-tufte-data-ink]] (2), [[R-svg-hygiene]] (3). Factored 2026-06-09 per F132 Phase 1; reorganized 2026-06-16 per F132 Q5=B into **per-domain folders** under `Rulesets/` — `Diagram/` ([[R-diagram]] umbrella + [[R-c4]]), `Graph/` ([[R-sugiyama]]), `Structural/` ([[R-diagram-geometry]]), `Accessibility/` ([[R-wcag-contrast]]), `Typography/` ([[R-bringhurst-typography]]), `Visualization/` ([[R-tufte-data-ink]]), `SVG/` ([[R-svg-hygiene]]) — so cross-cutting domains can later hold non-diagram rulesets; the umbrella re-composes them via wiki-link `include::`. See [[R-diagram]] § Migration map for legacy R-diagram-NN → factored-ID lookup. |
| [[R-doc]] | Documentation conventions. Contains [[R-markdown]] (10 rules — supersedes legacy [[R-md]]), [[R-file-association]] (7 rules — general typed-association pattern) and its dated specialization [[R-dated-entry-stream]] (3 rules — inherits R-file-association). Future: `R-progressive-disclosure`, `R-wiki-links`, `R-file-naming`. |
| [[R-git]] | Git discipline. Placeholder; future: `R-commit-discipline`, `R-pr-workflow`, `R-no-force-main`. |
| [[R-process]] | Process rules — **umbrella over 4 mined design-rule families, 14 rules total** (F218, upgraded 2026-07-05): [[R-design-gate]] (4 — SVP M15 canonical), [[R-stable-ids]] (4), [[R-exception-discipline]] (3), [[R-wrapper-cli]] (3). Future: `R-feature-lifecycle`, `R-verification-tiers`. |
| [[R-test]] | Testing posture. Placeholder; future: `R-integration-not-mock`, `R-deterministic`, `R-property-based`. |
| **Owner-scoped** | Apply to every anchor a given owner owns, regardless of trait. |
| [[R-ob]] | Dan's personal Ob-flavored rulesets. Children: [[R-ob-state-mgt]] (3 rules), [[R-ob-observability]] (2 rules), [[R-ob-cmd-proc]] (13 rules), [[R-ob-remote-ops]] (1 rule — the F183 bridge-guard, rides `anchor-base`). |
| --- | |

## Status

**Phase 3 scaffolding.** Materialized: [[R-code]] (containing [[R-mac]]); [[R-doc]] (containing [[R-markdown]]); [[R-diagram]] (umbrella over 7 methodology sub-sets, 22 rules total — factored 2026-06-09 per F132 Phase 1); [[R-ob]] (containing 3 sub-sets, 18 rules total); [[R-facet]] now has eleven materialized children: [[R-testing]] (9 rules), [[R-status]] (10 rules), [[R-log]] (9 rules), [[R-stories]] (9 rules), [[R-prd]] (9 rules), [[R-design]] (7 rules), [[R-naming]] (5 rules), [[R-roadmap]] (11 rules), [[R-completed-roadmap]] (6 rules), [[R-ux]] (8 rules), [[R-api]] (9 rules), the last two landed 2026-06-11 as paired peer facets cutting human vs programmatic user surface. **Design pipeline live** — folder presence (`{slug} Design/`) replaces the Code-trait gate; CAB Design facet governs scaffolding + required-children invariants; F140 sweeps the Code trait out of vault anchors. CAB-aligned umbrellas [[R-trait]] / [[R-skill]] remain structural placeholders awaiting rule population as `rulesets/R-*.md` files. Trait-scoped children ([[R-paper]] / [[R-simple]] / [[R-skill-anchor]] / [[R-topic]]) are placeholders pending migration into `traits/<Trait>.md` specs.

## Research

- [[2026-06-08 diagram-auditing-methodologies]] — survey of 20 sources on diagram-validation methodologies (PCB DRC, Sugiyama / Purchase graph-drawing aesthetics, C4 / Sourcetrail checklists, Bertin / Tufte / Munzner, WCAG contrast). Seed material for the [[R-diagram]] set's 22-rule checklist.
