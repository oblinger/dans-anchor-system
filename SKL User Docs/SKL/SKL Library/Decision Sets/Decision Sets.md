---
description: Decision Sets — curated, versioned bundles of decisions per F113 Phase 3. Trait-scoped sets apply to anchors carrying the matching trait; cross-cutting sets apply across traits when explicitly pulled; owner-scoped sets apply to every anchor a person owns.
---

# Decision Sets

| -[[Decision Sets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [Decision Sets](hook://p/Decision%20Sets)<br>: Curated, versioned bundles of decisions per F113 Phase 3. |
| --- | --- |
| **Cross-cutting sets** |  |
| **Arch/** | Architecture decisions: `factory-pegboard` (factory pattern per F108), `interfaces-folder` (single Interfaces/ folder), `single-source-of-truth` (no duplicate code; use imports). |
| **[[Diagram]]** | Diagram authoring + validation: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate. |
| **Doc/** | Documentation conventions: `md-formatting` (markdown formatting), `progressive-disclosure` (the discipline as decisions), `wiki-links` (Obsidian wiki-link conventions), `file-naming` (file and folder naming). |
| **Git/** | Git discipline: `commit-discipline` (commit-on-transition, no amend), `pr-workflow` (PR-based development), `no-force-main` (never force-push to main). |
| **Process/** | Process decisions: `feature-lifecycle` (Designing → Ready → Active → Verify → Done), `verification-tiers` (citing the verification discipline). |
| **Test/** | Testing posture: `integration-not-mock` (integration tests hit real systems), `deterministic` (no clock/random dependence), `property-based` (proptest patterns). |
| **Owner-scoped sets** |  |
| **Ob/** | Dan's personal cross-project set — applies to every anchor Dan owns regardless of trait. Currently one set: `ob/ob.md` (markdown-valid-for-Obsidian, kmr-flavored commit discipline, em-dash policy for authored content, etc.). |
| --- | |
| [[Diagram]] | Diagram — decisions and validation approaches for hand-authored figures (architecture diagrams, flow diagrams, mockups). Cross-cutting set pulled in when an anchor authors visual artifacts. |
| [[mac-app]] | macOS app development — code signing, TCC permissions, sandboxing, build conventions |
| [[ob]] | ob decisions — Dan's personal cross-project decisions that apply to all of his work, regardless of trait or domain. |
| [[Decision Sets/README]] |  |

## Overview 

Curated, versioned bundles of decisions (post-F113 successor to `~/.claude/skills/rule/sets/`). Each set is a standalone markdown doc bundling related decisions that apply to a specific style of anchor or a specific cross-cutting concern. When an anchor pulls a set in, the set's decisions get renumbered into the anchor's local D-NN namespace and appended as an H2 grouping in `{NAME} Decisions.md` (per F113 Q2 — copy-in semantics).

Two committed kinds of sets:

- **Cross-cutting** — not trait-scoped (Arch, Doc, Git, Process, Test). Pulled in when the anchor explicitly opts in.
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

**Phase 3 scaffolding.** Per F113 Phase 3, the set catalog is being populated. Currently materialized: `Code/mac-app.md` + `Ob/ob.md`. The other entries are folder placeholders awaiting curation. Each set when authored carries its own frontmatter with `set-id`, `trait`, and `applies-when`.

## Pull semantics

When an anchor pulls a set in (Phase 6 mechanic, per F113 Q2 = copy-in):

1. The set's decisions are physically copied into the anchor's `{NAME} Decisions.md` as an H2 grouping (set name as heading + `*(imported v<X>, <date>)*` suffix).
2. Decisions are renumbered into the anchor's local D-NN namespace at pull-in time.
3. The anchor is free to diverge from the source set; divergence is visible in the local copy.
4. Set updates get pulled when the user runs `/decision refresh <set>` — never silently. New decisions append at the end of the set's H2 with the next unused D-numbers.

## File format

Each set file follows this shape:

```markdown
---
description: <one-line description of when this set applies>
trait: <Trait name — matches parent folder; omit for cross-cutting sets>
applies-when: <free-form condition string for /decision recommend>
set-id: <short-prefix used in D-numbering inside this set, e.g., MA for mac-app>
---

# <Folder>/<set-name> — <Title>

Brief paragraph: what this set is, when it applies.

### D-<SET>01 — <decision name> (<tier>)
<declarative statement>

**Check pattern:** <how /audit decisions detects violations>

**Exceptions:** <table + per-row blocks, or absent>
```

## Related

- CAB Decisions — facet spec (what `{NAME} Decisions.md` looks like). Lives at [[CAB Decisions]].
- F113 — origin feature. [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]].
- CAB Traits — trait taxonomy that scopes which sets apply.
