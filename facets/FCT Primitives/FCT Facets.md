---
description: Index of every Facet — the narrow, usually-file-based Aspects an anchor can carry (per [[DAS Aspects]])
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [FCT Primitives](hook://FCT%20Primitives) → [FCT Facets](hook://p/FCT%20Facets)
# FCT Facets
Facets are one of the two sibling sub-categories of [[DAS Aspects|Aspect]] (the other is [[DAS Traits|Trait]]). Each Facet is a narrow, specific aspect of an anchor — almost always tied to one or more files. Each spec doc under this folder is authoritative for its Facet's detection mechanism, cardinality, format constraints, behavior, Constraints, and Expected Usage (per [[DAS Aspects]] § Facet + § Spec-doc structure).

The test that separates the two siblings: a file-shaped, narrow Aspect is a **Facet** (catalogued here); a broad paradigm declared in `.anchor` is a **[[DAS Traits|Trait]]** (its sibling catalog) — don't conflate them. The **Primitives** row is reflexive: it catalogues the kinds of authored object the system itself is built from (Skill / Facet / Discipline / Ruleset / Trait), each defined in [[DAS Primitives]] and exemplified in [[FEX Repo]].

**[[DAS Primitives\|Primitives]]:** [[DAS Skill\|Skill]],  [[DAS Facet\|Facet]],  [[DAS Disciplines\|Discipline]],  [[DAS Ruleset\|Ruleset]],  [[DAS Traits\|Trait]],  [[DAS Template\|Template]]
**Structure:** [[DAS Folder\|Folder]],  [[DAS Anchor Page\|Anchor Page]],  [[DAS All Files\|All Files]],  [[DAS Docs\|Docs Hub]],  [[DAS Plan Dispatch\|Plan Dispatch]],  [[DAS Dev Dispatch\|Dev Dispatch]],  [[DAS User Dispatch\|User Dispatch]]
**Design:** [[DAS PRD\|PRD]],  [[DAS System Design\|System Design]],  [[DAS UX Design\|UX]],  [[DAS API Design\|API Design]],  [[DAS Decisions\|Decisions]],  [[DAS Ruleset\|Ruleset]],  [[DAS Features\|Features]]
**Execute:** [[DAS Backlog\|Backlog]],  [[DAS Roadmap\|Roadmap]],  [[DAS Query\|Query]],  [[DAS Icebox\|Icebox]],  [[DAS Inbox\|Inbox]],  [[DAS WP\|WP]],  [[DAS Outputs\|Outputs]]
**Code:** [[DAS Code Repository\|Code Repo]],  [[DAS Files Architecture\|Files]],  [[DAS Module Doc\|Module Doc]]
**User:** [[DAS User Dispatch\|User Dispatch]],  [[DAS Interface\|Interface]],  [[DAS Architecture\|Architecture]],  [[DAS CLI\|CLI]],  [[DAS Cards\|Cards]]
**External / Publish:** [[DAS Documentation Site\|Doc Site]],  [[DAS Project Page\|Project Page]],  [[DAS Versions\|Versions]]
**Skill / Ops:** [[DAS Skill\|Skill]],  [[DAS Claude\|CLAUDE.md]],  [[DAS Move\|Move]]
**Skill Anchor (per F116):** [[skill-testing\|skill-testing]],  [[skill-search-rules\|skill-search-rules]],  [[skill-script\|skill-script]],  [[skill-config\|skill-config]]
**Doc Facet:** [[DAS Discussion\|Discussion]],  [[DAS Brief\|Brief]]

# BRIEF

*(Maintainer note — this is the Facet index, not a spec; conventions for keeping the catalog current.)*

- **Index only — never inline spec content.** Each Facet's detail lives in its own `CAB <Name>.md` spec doc; this file is purely the dispatch of pointers.
- **Adding a Facet:** create `CAB <Name>.md` (single-file) or `CAB <Name>/CAB <Name>.md` (folder form when it grows), follow the spec-doc shape per [[DAS Aspects]] § Spec-doc structure, then wiki-link it into the dispatch row matching its conceptual category.
- **Row grouping is semantic, not alphabetical** — new Facets join the row for their category; if none fits, park in the `...` staging row until a category emerges, then promote out.
- **Primitives-row migration:** Discipline and Trait still point at their pre-migration `CAB <X>` specs; SKA Roadmap M1 moves them to DSC / the library — update those links when it lands.
