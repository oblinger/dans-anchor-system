---
description: Rule Sets — curated, versioned bundles of rules. Trait-scoped sets apply to anchors carrying the matching trait; cross-cutting sets apply across traits when explicitly pulled; owner-scoped sets apply to every anchor a person owns. Renamed from "Decision Sets" 2026-06-08 to honor the rules-vs-decisions vocabulary distinction.
---

# Rule Sets

| -[[Rule Sets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [Rule Sets](hook://p/Rule%20Sets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| **Cross-cutting sets** |  |
| [[R-arch]] | Architecture rules — patterns for code organization, module structure, dependency direction. Placeholder; future: `R-factory-pegboard`, `R-interfaces-folder`, `R-single-source-of-truth`. |
| [[R-code]] | Code-flavored rule sets — language- or platform-specific coding conventions. Currently includes [[R-mac]] (macOS app — code signing, TCC, sandboxing). Future: `R-rust`, `R-python`, `R-typescript`, `R-shell`. |
| [[R-diagram-folder\|R-diagram]] | Diagram authoring + validation. Umbrella [[R-diagram]]: 22 rules across DRC-blockers / Sugiyama aesthetics / C4 semantics / WCAG contrast / hygiene. Will factor into per-methodology sub-sets per F132 Phase 1. |
| [[R-doc]] | Documentation conventions. Currently includes [[R-md]] (markdown rendering — angle brackets, table blank lines). Future: `R-progressive-disclosure`, `R-wiki-links`, `R-file-naming`. |
| [[R-git]] | Git discipline. Placeholder; future: `R-commit-discipline`, `R-pr-workflow`, `R-no-force-main`. |
| [[R-process]] | Process rules. Placeholder; future: `R-feature-lifecycle`, `R-verification-tiers`. |
| [[R-test]] | Testing posture. Placeholder; future: `R-integration-not-mock`, `R-deterministic`, `R-property-based`. |
| **Trait-scoped sets (speculative)** | Speculative scaffolding — may be pruned, merged into cross-cutting, or scrapped. |
| [[R-paper]] | Paper / writing-anchor rule sets — citation conventions, prose-style discipline. Placeholder. |
| [[R-simple]] | Simple-anchor rule sets — minimal-shape collections without full CAB structure. Placeholder. |
| [[R-skill]] | Skill-anchor rule sets — structural shape of skill folders, ask-format / verification / mode-style conventions. Placeholder. |
| [[R-topic]] | Topic-anchor rule sets — knowledge/reference anchors (folders of notes, surveys, glossaries). Placeholder. |
| **Owner-scoped sets** |  |
| [[R-ob]] | Dan's personal Ob-flavored rule sets — apply to every anchor Dan owns regardless of trait. Children: [[R-ob-state-mgt]] (config + state singleton + no-hardcoded; 3 rules), [[R-ob-observability]] (no-silent-fallbacks + 100% OS-bridge logging; 2 rules), [[R-ob-cmd-proc]] (single dispatcher + sensors-engines-effectors pattern; 13 rules). The folder-file body holds the markdown / commit / em-dash rules until split out. |
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

Three kinds of sets:

- **Cross-cutting** — not trait-scoped (`R-arch`, `R-code`, `R-diagram`, `R-doc`, `R-git`, `R-process`, `R-test`). Pulled in when the anchor explicitly opts in.
- **Trait-scoped (speculative)** — keyed to the CAB Traits taxonomy; would pull in automatically when an anchor declares the matching trait. Currently speculative scaffolding (`R-paper`, `R-simple`, `R-skill`, `R-topic`) — may be pruned, merged into cross-cutting, or scrapped as the pattern proves out.
- **Owner-scoped** — pulled in by every anchor a person owns, regardless of trait (`R-ob` = Dan's personal set).

## Folder-file convention (2026-06-09)

Every rule-set folder named `R-<name>/` contains a folder-file `R-<name>.md` that is itself a RULESET. The folder-file's `includes::` (or `include::`) line rolls up all child rule sets in the folder. Adopting the folder umbrella (e.g., `include:: [[R-code]]`) is equivalent to adopting every child set; cherry-pick individual children for finer control.

## Status

**Phase 3 scaffolding.** Currently materialized: [[R-code]] (containing [[R-mac]]); [[R-doc]] (containing [[R-md]]); [[R-diagram]] (22-rule umbrella); [[R-ob]] (containing [[R-ob-state-mgt]] / [[R-ob-observability]] / [[R-ob-cmd-proc]]). Other folder-files are placeholders with empty `includes::` awaiting curation.

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
