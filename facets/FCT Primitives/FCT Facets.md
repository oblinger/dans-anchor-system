---
description: Index of every Facet — the narrow, usually-file-based Aspects an anchor can carry (per [[CAB Aspects]])
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Primitives]] → [FCT Facets](hook://p/FCT%20Facets)
# FCT Facets
Facets are one of the two sibling sub-categories of [[CAB Aspects|Aspect]] (the other is [[TRT|Trait]]). Each Facet is a narrow, specific aspect of an anchor — almost always tied to one or more files. Each spec doc under this folder is authoritative for its Facet's detection mechanism, cardinality, format constraints, behavior, Constraints, and Expected Usage (per [[CAB Aspects]] § Facet + § Spec-doc structure).

The test that separates the two siblings: a file-shaped, narrow Aspect is a **Facet** (catalogued here); a broad paradigm declared in `.anchor` is a **[[TRT|Trait]]** (its sibling catalog) — don't conflate them. The **Primitives** row is reflexive: it catalogues the kinds of authored object the system itself is built from (Skill / Facet / Discipline / Ruleset / Trait), each defined in [[FCT Primitives]] and exemplified in [[FEX Repo]].

**[[FCT Primitives\|Primitives]]:** [[FCT Skill\|Skill]],  [[FCT Facet\|Facet]],  [[CAB Disciplines\|Discipline]],  [[FCT Ruleset\|Ruleset]],  [[TRT\|Trait]],  [[FCT Template\|Template]]
**Structure:** [[CAB Folder\|Folder]],  [[CAB Anchor Page\|Anchor Page]],  [[CAB All Files\|All Files]],  [[CAB Docs\|Docs Hub]],  [[CAB Plan Dispatch\|Plan Dispatch]],  [[CAB Dev Dispatch\|Dev Dispatch]],  [[CAB User Dispatch\|User Dispatch]]
**Design:** [[CAB PRD\|PRD]],  [[CAB System Design\|System Design]],  [[CAB UX Design\|UX]],  [[CAB API Design\|API Design]],  [[CAB Decisions\|Decisions]],  [[FCT Ruleset\|Ruleset]],  [[CAB Features\|Features]]
**Execute:** [[CAB Backlog\|Backlog]],  [[CAB Roadmap\|Roadmap]],  [[CAB Triage\|Triage]],  [[CAB Icebox\|Icebox]],  [[CAB Inbox\|Inbox]],  [[CAB WP\|WP]],  [[CAB Outputs\|Outputs]]
**Code:** [[CAB Code Repository\|Code Repo]],  [[CAB Files\|Files]],  [[FCT Module Doc\|Module Doc]]
**User:** [[CAB User Dispatch\|User Dispatch]],  [[CAB Interface\|Interface]],  [[CAB Architecture\|Architecture]],  [[CAB CLI\|CLI]],  [[CAB Cards\|Cards]]
**External / Publish:** [[CAB Documentation Site\|Doc Site]],  [[CAB Project Page\|Project Page]],  [[FCT Versions\|Versions]]
**Skill / Ops:** [[CAB Skill\|Skill]],  [[CAB Claude\|CLAUDE.md]],  [[CAB Move\|Move]]
**Skill Anchor (per F116):** [[CAB Facets/Skill Anchor/skill-testing\|skill-testing]],  [[CAB Facets/Skill Anchor/skill-search-rules\|skill-search-rules]],  [[CAB Facets/Skill Anchor/skill-script\|skill-script]],  [[CAB Facets/Skill Anchor/skill-config\|skill-config]]
**Doc Facet:** [[FCT Discussion\|Discussion]],  [[FCT Brief\|Brief]]

# BRIEF

*(Maintainer note — this is the Facet index, not a spec; conventions for keeping the catalog current.)*

- **Index only — never inline spec content.** Each Facet's detail lives in its own `CAB <Name>.md` spec doc; this file is purely the dispatch of pointers.
- **Adding a Facet:** create `CAB <Name>.md` (single-file) or `CAB <Name>/CAB <Name>.md` (folder form when it grows), follow the spec-doc shape per [[CAB Aspects]] § Spec-doc structure, then wiki-link it into the dispatch row matching its conceptual category.
- **Row grouping is semantic, not alphabetical** — new Facets join the row for their category; if none fits, park in the `...` staging row until a category emerges, then promote out.
- **Primitives-row migration:** Discipline and Trait still point at their pre-migration `CAB <X>` specs; SKA Roadmap M1 moves them to DSC / the library — update those links when it lands.
