---
description: Catalog of rule sets. See [[Rule Sets Brief]] for editing conventions, the rules-vs-decisions vocabulary, and the folder-file convention.
---

# Rule Sets

| -[[Rule Sets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [Rule Sets](hook://p/Rule%20Sets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| Related | [[Rule Sets Brief\|Brief]],  [[CAB Rules]],  [[CAB Decisions]],   |
| **CAB-aligned umbrellas** | The three primary structural axes — rule sets tied to CAB Facets, Traits, Skills. Adopting an umbrella pulls every per-X rule set under it. |
| [[R-facet]] | Per-facet rule sets — embed in `CAB Facets/<Facet>.md` specs as `# RULESET R-<facet>` blocks. Empty `includes::` for now; populates as each facet's RULESET block lands. |
| [[R-trait]] | Per-trait rule sets — to embed in `CAB Traits/<Trait>.md` specs. Children: [[R-paper]], [[R-simple]], [[R-skill-anchor]], [[R-topic]]. |
| [[R-skill]] | Per-skill rule sets — to embed in `~/.claude/skills/<skill>/SKILL.md` specs. First candidates: R-ask, R-feature, R-atlas. |
| **Cross-cutting** | Not tied to a specific facet, trait, or skill. Pulled in when explicitly opted into. |
| [[R-arch]] | Architecture rules — code organization, module structure, dependency direction. Placeholder; future: `R-factory-pegboard`, `R-interfaces-folder`, `R-single-source-of-truth`. |
| [[R-code]] | Code-flavored rule sets — language/platform conventions. Contains [[R-mac]]. Future: `R-rust`, `R-python`, `R-typescript`, `R-shell`. |
| [[R-diagram]] | Diagram authoring + validation — **umbrella over 7 methodology sub-sets, 22 rules total**: [[R-pcb-drc-structural]] (6), [[R-sugiyama]] (4), [[R-c4]] (4), [[R-wcag-contrast]] (2), [[R-bringhurst-typography]] (1), [[R-tufte-data-ink]] (2), [[R-svg-hygiene]] (3). Factored 2026-06-09 per F132 Phase 1; see [[R-diagram]] § Migration map for legacy R-diagram-NN → factored-ID lookup. |
| [[R-doc]] | Documentation conventions. Contains [[R-md]] (markdown rendering). Future: `R-progressive-disclosure`, `R-wiki-links`, `R-file-naming`. |
| [[R-git]] | Git discipline. Placeholder; future: `R-commit-discipline`, `R-pr-workflow`, `R-no-force-main`. |
| [[R-process]] | Process rules. Placeholder; future: `R-feature-lifecycle`, `R-verification-tiers`. |
| [[R-test]] | Testing posture. Placeholder; future: `R-integration-not-mock`, `R-deterministic`, `R-property-based`. |
| **Owner-scoped** | Apply to every anchor a given owner owns, regardless of trait. |
| [[R-ob]] | Dan's personal Ob-flavored rule sets. Children: [[R-ob-state-mgt]] (3 rules), [[R-ob-observability]] (2 rules), [[R-ob-cmd-proc]] (13 rules). |
| --- | |
| [[Rule Sets/README]] |  |

## Status

**Phase 3 scaffolding.** Materialized: [[R-code]] (containing [[R-mac]]); [[R-doc]] (containing [[R-md]]); [[R-diagram]] (umbrella over 7 methodology sub-sets, 22 rules total — factored 2026-06-09 per F132 Phase 1); [[R-ob]] (containing 3 sub-sets, 18 rules total). CAB-aligned umbrellas [[R-facet]] / [[R-trait]] / [[R-skill]] are structural placeholders awaiting embedded-RULESET-block population in their respective CAB spec files. Trait-scoped children ([[R-paper]] / [[R-simple]] / [[R-skill-anchor]] / [[R-topic]]) are placeholders pending migration into `CAB Traits/<Trait>.md` specs.

## Research

- [[2026-06-08 diagram-auditing-methodologies]] — survey of 20 sources on diagram-validation methodologies (PCB DRC, Sugiyama / Purchase graph-drawing aesthetics, C4 / Sourcetrail checklists, Bertin / Tufte / Munzner, WCAG contrast). Seed material for the [[R-diagram]] set's 22-rule checklist.
