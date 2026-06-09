---
description: Rule Sets — curated, versioned bundles of rules. Trait-scoped sets apply to anchors carrying the matching trait; cross-cutting sets apply across traits when explicitly pulled; owner-scoped sets apply to every anchor a person owns. Renamed from "Decision Sets" 2026-06-08 to honor the rules-vs-decisions vocabulary distinction.
---

# Rule Sets

| -[[Rule Sets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [Rule Sets](hook://p/Rule%20Sets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| **CAB-aligned umbrellas** | The three primary structural axes — rule sets tied to CAB Facets, Traits, and Skills. Adopting an umbrella pulls every per-X rule set under it. |
| [[R-facet]] | Per-facet rule sets — embedded in `CAB Facets/<Facet>.md` specs. Adopt to commit to every CAB facet's structural rules. |
| [[R-trait]] | Per-trait rule sets — to embed in `CAB Traits/<Trait>.md` specs. Children: [[R-paper]], [[R-simple]], [[R-skill-anchor]], [[R-topic]]. |
| [[R-skill]] | Per-skill rule sets — to embed in `~/.claude/skills/<skill>/SKILL.md` specs. Empty `includes::` for now; first candidates: R-ask, R-feature, R-atlas. |
| **Cross-cutting sets** | Not tied to a specific facet, trait, or skill — pulled in when explicitly opted into. |
| [[R-arch]] | Architecture rules — code organization, module structure, dependency direction. Placeholder; future: `R-factory-pegboard`, `R-interfaces-folder`, `R-single-source-of-truth`. |
| [[R-code]] | Code-flavored rule sets — language/platform conventions. Currently includes [[R-mac]]. Future: `R-rust`, `R-python`, `R-typescript`, `R-shell`. |
| [[R-diagram-folder\|R-diagram]] | Diagram authoring + validation. Umbrella [[R-diagram]]: 22 rules across DRC-blockers / Sugiyama aesthetics / C4 semantics / WCAG contrast / hygiene. Factors per F132 Phase 1. |
| [[R-doc]] | Documentation conventions. Currently includes [[R-md]]. Future: `R-progressive-disclosure`, `R-wiki-links`, `R-file-naming`. |
| [[R-git]] | Git discipline. Placeholder; future: `R-commit-discipline`, `R-pr-workflow`, `R-no-force-main`. |
| [[R-process]] | Process rules. Placeholder; future: `R-feature-lifecycle`, `R-verification-tiers`. |
| [[R-test]] | Testing posture. Placeholder; future: `R-integration-not-mock`, `R-deterministic`, `R-property-based`. |
| **Trait-scoped sets** | Children of [[R-trait]] above; will migrate into `CAB Traits/<Trait>.md` specs as each one's content firms up. |
| [[R-paper]] | Paper / writing-anchor rule sets. Placeholder. |
| [[R-simple]] | Simple-anchor rule sets. Placeholder. |
| [[R-skill-anchor]] | Skill-anchor rule sets (formerly `R-skill`; renamed 2026-06-09 to free `R-skill` for the per-skill umbrella). Placeholder. |
| [[R-topic]] | Topic-anchor rule sets. Placeholder. |
| **Owner-scoped sets** | Apply to every anchor a given owner owns, regardless of trait. |
| [[R-ob]] | Dan's personal Ob-flavored rule sets. Children: [[R-ob-state-mgt]] (3 rules), [[R-ob-observability]] (2 rules), [[R-ob-cmd-proc]] (13 rules). |
| [[Rule Sets/README]] |  |

## Rules vs decisions — the vocabulary distinction (2026-06-08)

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. "ASCII forbidden in architecture diagrams." "Must use Helvetica." Lives in a Rule Set; gets adopted across many anchors.

A **decision** is a specific applied choice with rationale, recorded at the anchor level in `{NAME} Decisions.md`. "We chose SQLite for TaskStore because of operator-readability." A decision cites the rule(s) it applies; the rationale is what makes it a *decision* and not just a rule citation.

The relationship:

- **Rule Sets** (this catalog) bundle rules. Each rule has an audit-tier annotation (tracked / checked / sampled / stated).
- **Anchor Decisions** (`{NAME} Decisions.md`) record the anchor's specific applied choices. Each decision typically references one or more rules from Rule Sets and explains why.
- **Audit** walks the decisions in an anchor's `{NAME} Decisions.md`, collects every referenced rule, and verifies each rule is satisfied. The rules are what get checked; the decisions are how the anchor declares which rules apply here and why.

(Renamed from "Decision Sets" 2026-06-08. The previous naming collapsed the rules-and-decisions distinction; this rename honors both terms in their proper role.)

## Overview

Curated, versioned bundles of rules. Each set is a standalone markdown doc bundling related rules that apply to a specific style of anchor or a specific cross-cutting concern. When an anchor adopts a set, the set's rules are referenced from `{NAME} Decisions.md` as adopted constraints; the decision body explains why (which rationale picked this rule set for this anchor).

Five kinds of sets:

- **CAB-aligned umbrellas** — the three primary structural axes paralleling CAB's own categories: [[R-facet]] (per-facet), [[R-trait]] (per-trait), [[R-skill]] (per-skill). Each umbrella's `includes::` rolls up rule sets that eventually embed into the corresponding CAB spec file (CAB Facet, CAB Trait, or `~/.claude/skills/<skill>/SKILL.md`).
- **Cross-cutting** — not tied to a specific facet, trait, or skill (`R-arch`, `R-code`, `R-diagram`, `R-doc`, `R-git`, `R-process`, `R-test`). Pulled in when an anchor explicitly opts in.
- **Trait-scoped** — children of [[R-trait]] (`R-paper`, `R-simple`, `R-skill-anchor`, `R-topic`). Activate when the anchor declares the matching Trait. Migrate into `CAB Traits/<Trait>.md` specs as content firms up.
- **Owner-scoped** — pulled in by every anchor a person owns, regardless of trait (`R-ob` = Dan's personal set).
- **Folder-file** — every `R-<name>/` folder contains an `R-<name>.md` folder-file RULESET (see the convention below).

## Folder-file convention (2026-06-09)

Every rule-set folder named `R-<name>/` contains a folder-file `R-<name>.md` that is itself a RULESET. The folder-file's `includes::` (or `include::`) line rolls up all child rule sets in the folder. Adopting the folder umbrella (e.g., `include:: [[R-code]]`) is equivalent to adopting every child set; cherry-pick individual children for finer control.

## Status

**Phase 3 scaffolding.** Currently materialized: [[R-code]] (containing [[R-mac]]); [[R-doc]] (containing [[R-md]]); [[R-diagram]] (22-rule umbrella); [[R-ob]] (containing [[R-ob-state-mgt]] / [[R-ob-observability]] / [[R-ob-cmd-proc]]). CAB-aligned umbrellas [[R-facet]], [[R-trait]], [[R-skill]] are structural placeholders awaiting embedded-RULESET-block population in their respective CAB spec files. Other folder-files are placeholders with empty `includes::` awaiting curation.

## Pull semantics

When an anchor adopts a rule set:

1. The set's rules are referenced from the anchor's `{NAME} Decisions.md` as an H2 grouping (set name + `*(adopted v<X>, <date>)*` suffix).
2. Each rule gets renumbered into the anchor's local R-NN namespace at adoption time.
3. The anchor is free to diverge from the source set; divergence is visible in the local copy.
4. Set updates get pulled when the user runs `/rule refresh <set>` — never silently. New rules append at the end of the set's H2 with the next unused R-numbers.

## File format

See [[CAB Rules]] for the prescriptive RULESET format (H1 sentinel + `include::` + `description::` + H3 rule entries with tier annotation). The earlier YAML-frontmatter form is legacy; remaining instances ([[R-mac]]) will be migrated.

## Related

- CAB Decisions — anchor-level facet spec (what `{NAME} Decisions.md` looks like; decisions cite rules from Rule Sets). Lives at [[CAB Decisions]].
- F113 — origin feature. [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]] (historical name retained; F113 introduced the unified concept, this rename refines the vocabulary).
- CAB Traits — trait taxonomy that scopes which sets apply.

## Research

- [[2026-06-08 diagram-auditing-methodologies]] — survey of 20 sources on diagram-validation methodologies (PCB DRC, Sugiyama / Purchase graph-drawing aesthetics, C4 / Sourcetrail checklists, Bertin / Tufte / Munzner, WCAG contrast). Seed material for the [[R-diagram]] set's audit checklist.
