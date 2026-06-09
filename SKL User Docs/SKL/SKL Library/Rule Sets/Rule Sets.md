---
description: Rule Sets — curated, versioned bundles of rules. Trait-scoped sets apply to anchors carrying the matching trait; cross-cutting sets apply across traits when explicitly pulled; owner-scoped sets apply to every anchor a person owns. Renamed from "Decision Sets" 2026-06-08 to honor the rules-vs-decisions vocabulary distinction.
---

# Rule Sets

| -[[Rule Sets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [Rule Sets](hook://p/Rule%20Sets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| **Cross-cutting sets** |  |
| **Arch/** | Architecture rules: `factory-pegboard` (factory pattern per F108), `interfaces-folder` (single Interfaces/ folder), `single-source-of-truth` (no duplicate code; use imports). |
| **[[Diagram]]** | Diagram authoring + validation rules: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate. |
| **Doc/** | Documentation conventions: `md-formatting` (markdown formatting), `progressive-disclosure` (the discipline as rules), `wiki-links` (Obsidian wiki-link conventions), `file-naming` (file and folder naming). |
| **Git/** | Git discipline: `commit-discipline` (commit-on-transition, no amend), `pr-workflow` (PR-based development), `no-force-main` (never force-push to main). |
| **Process/** | Process rules: `feature-lifecycle` (Designing → Ready → Active → Verify → Done), `verification-tiers` (citing the verification discipline). |
| **Test/** | Testing posture: `integration-not-mock` (integration tests hit real systems), `deterministic` (no clock/random dependence), `property-based` (proptest patterns). |
| **Owner-scoped sets** |  |
| **Ob/** | Dan's personal Ob-flavored rule sets — apply to every anchor Dan owns regardless of trait. Folder of rule sets named `R-ob-*`: [[R-ob-state-mgt]] (config + state singleton + no-hardcoded; 3 rules), [[R-ob-observability]] (no-silent-fallbacks + 100% OS-bridge logging; 2 rules), [[R-ob-cmd-proc]] (single dispatcher + sensors-engines-effectors pattern; 13 rules). Legacy `Ob/ob.md` holds the markdown / commit / em-dash rules until split out. |
| --- | |
| [[mac-app]] | macOS app development — code signing, TCC permissions, sandboxing, build conventions |
| [[ob]] | ob rules — Dan's personal cross-project rules that apply to all of his work, regardless of trait or domain. |
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

Two committed kinds of sets:

- **Cross-cutting** — not trait-scoped (Arch, Diagram, Doc, Git, Process, Test). Pulled in when the anchor explicitly opts in.
- **Owner-scoped** — pulled in by every anchor a person owns, regardless of trait (Ob/ = Dan's personal set).

A third — **trait-scoped** sets keyed to the CAB Traits taxonomy — is proposed but not committed. Surfaced separately below.

## Proposed trait-scoped sets

Trait-scoped sets would key off the CAB Traits taxonomy and pull in automatically when an anchor declares the matching trait. **Not committed** — the catalog below is speculative scaffolding, possibly too granular. May be pruned, merged into cross-cutting categories, or scrapped entirely as the pattern proves out (or doesn't).

| **Code/** | macOS app, iOS, Rust crate, Python tooling, shell scripts, TypeScript/React frontend, backend services, CLI tool design. |
| --- | --- |
| **Skill/** | skill-anchor structural shape, discipline-style skill conventions (ask-format, verification, mode style). |
| **Topic/** | knowledge/reference anchors (folders of notes, surveys, glossaries). |
| **Paper/** | writing-style and citation conventions for paper anchors. |
| **Simple/** | minimal-shape anchors (lightweight collections without full CAB structure). |

## Status

**Phase 3 scaffolding.** Per F113 Phase 3, the set catalog is being populated. Currently materialized: `Code/mac-app.md` + `Ob/ob.md` + `Diagram/Diagram.md` (seed). The other entries are folder placeholders awaiting curation. Each set when authored carries its own frontmatter with `set-id`, `trait`, and `applies-when`.

## Pull semantics

When an anchor adopts a rule set:

1. The set's rules are referenced from the anchor's `{NAME} Decisions.md` as an H2 grouping (set name + `*(adopted v<X>, <date>)*` suffix).
2. Each rule gets renumbered into the anchor's local R-NN namespace at adoption time.
3. The anchor is free to diverge from the source set; divergence is visible in the local copy.
4. Set updates get pulled when the user runs `/rule refresh <set>` — never silently. New rules append at the end of the set's H2 with the next unused R-numbers.

## File format

Each rule-set file follows this shape:

```markdown
---
description: <one-line description of when this set applies>
trait: <Trait name — matches parent folder; omit for cross-cutting sets>
applies-when: <free-form condition string for /rule recommend>
set-id: <short-prefix used in R-numbering inside this set, e.g., MA for mac-app, DG for diagram>
---

# <Folder>/<set-name> — <Title>

Brief paragraph: what this set is, when it applies.

### R-<SET>01 — <rule name> (<tier>)
<declarative statement>

**Check pattern:** <how /audit rules detects violations>

**Exceptions:** <table + per-row blocks, or absent>
```

## Related

- CAB Decisions — anchor-level facet spec (what `{NAME} Decisions.md` looks like; decisions cite rules from Rule Sets). Lives at [[CAB Decisions]].
- F113 — origin feature. [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]] (historical name retained; F113 introduced the unified concept, this rename refines the vocabulary).
- CAB Traits — trait taxonomy that scopes which sets apply.

## Research

- [[2026-06-08 diagram-auditing-methodologies]] — survey of 20 sources on diagram-validation methodologies (PCB DRC, Sugiyama / Purchase graph-drawing aesthetics, C4 / Sourcetrail checklists, Bertin / Tufte / Munzner, WCAG contrast). Seed material for the [[Diagram]] set's audit checklist.
