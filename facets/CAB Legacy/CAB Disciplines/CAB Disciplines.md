---
description: Catalog of CAB Disciplines — cross-anchor patterns for how we work. Sibling to CAB Facets and to skill-level [[SKL Discipline]].
---

# CAB Disciplines

Catalog of CAB Disciplines — cross-anchor patterns for how we work, sibling to CAB Facets and skill-level [[SKL Discipline]].

| -[[CAB Disciplines]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[CAB Legacy]] → [CAB Disciplines](hook://p/CAB%20Disciplines)<br>: Cross-anchor patterns for how we work. |
| --- | --- |
| Related | [[CAB Disciplines Brief\|Brief]],  ~~[[CAB Facets]]~~,  [[CAB Aspects]],  [[SKL Discipline]],   |
| Global disciplines | ~~[[DSC Dispatch Table\|Dispatch Table]]~~,   |
| Corpus-level invariants | ~~[[anchor-dag]]~~ (the vault is one navigable DAG — verified by a whole-graph walk), |
| Anchor-level disciplines | [[DSC Linked Mode\|Linked Mode]],   |
| Skill-level disciplines | [[SKL Discipline\|SKL Discipline catalog]] — [[SKL Mode\|Mode]] (Drive / Discuss / Active / Parking), [[SKL Drive\|Drive]], ask-format, verification, … |
| --- | |
| [[CAB Dispatch Table Design]] | Design rationale + standing decisions for the Dispatch Table discipline — the why behind the spec, so it isn't relitigated. |

**Two kinds of discipline by *scope of application*.** Most disciplines are **per-artifact authoring** rules — applied while you write one doc or anchor (~~[[markdown]]~~, ~~[[progressive-disclosure]]~~, ~~[[file-association]]~~, ~~[[granularity]]~~, the per-facet shape rules). A newer kind is the **corpus-level invariant** — a property of *all the anchors together*, verified by **walking the whole graph**, not by authoring any single thing. ~~[[anchor-dag]]~~ is the first; siblings of the same shape would be *every-slug-resolves*, *no-orphan-files*, *Atlas-covers-every-named-thing*. When defining a vault-wide integrity check, it's a corpus-level invariant; when shaping one artifact, it's an authoring discipline.

# BRIEF

- **Purpose.** Catalog of *cross-anchor* disciplines — patterns we follow because we agreed it's how we organize things. Sibling to ~~[[CAB Facets]]~~ (file-based aspects of one anchor) and [[SKL Discipline]] (skill-level disciplines).
- **Detailed editing guidance lives in the sidecar.** See [[CAB Disciplines Brief]] for the full *what-belongs / when-to-add / how-to-add* spec. Read it before adding or restructuring an entry.
- **Entry format.** One wiki-link per discipline in the appropriate dispatch-table row (Global / Anchor-level / Skill-level), aliased to a short name: `~~[[CAB <Name>\|<Name>]]~~`. Each entry resolves to a spec page at `CAB Disciplines/CAB <Name>.md`.
- **Inclusion test (tight).** A discipline earns a row when it applies across multiple anchors, is operational (a constraint on how we work), and warrants its own spec page. See the sidecar for the long form.
- **What does NOT belong.** Project-wide rules (→ `CLAUDE.md`), facet-shape conventions (→ `CAB <Facet>.md`), anchor-local rules (→ `{NAME} Rules.md` / `{NAME} Decisions.md`), skill-level disciplines (→ [[SKL Discipline]]), end-user documentation (→ `<App> User Guide.md`).
- **Don't pile per-discipline content into this file.** Each discipline's full spec lives in its own `CAB <Name>.md`. The row here is just the dispatch pointer.
