---
description: Index of every Facet — the narrow, usually-file-based Aspects an anchor can carry (per [[CAB Aspects]])
---

# CAB Facets

Facets are one of the two sibling sub-categories of [[CAB Aspects|Aspect]] (the other is [[CAB Traits|Trait]]). Each Facet is a narrow, specific aspect of an anchor — almost always tied to one or more files. Each spec doc under this folder is authoritative for its Facet's detection mechanism, cardinality, format constraints, behavior, Constraints, and Expected Usage (per [[CAB Aspects]] § Facet + § Spec-doc structure).

| -[[FCT Facets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [FCT Facets](hook://p/FCT%20Facets)<br>:  |
| --- | --- |
| Structure | [[CAB Folder\|Folder]],  [[CAB Anchor Page\|Anchor Page]],  [[CAB All Files\|All Files]],  [[CAB Docs\|Docs Hub]],  [[CAB Plan Dispatch\|Plan Dispatch]],  [[CAB Dev Dispatch\|Dev Dispatch]],  [[CAB User Dispatch\|User Dispatch]],   |
| Design | [[CAB PRD\|PRD]],  [[CAB System Design\|System Design]],  [[CAB UX Design\|UX]],  [[CAB API Design\|API Design]],  [[CAB Principles\|Principles]],  [[FCT Rules\|Rules]],  [[CAB Features\|Features]],   |
| Execute | [[CAB Backlog\|Backlog]],  [[CAB Roadmap\|Roadmap]],  [[CAB Triage\|Triage]],  [[CAB Icebox\|Icebox]],  [[CAB Inbox\|Inbox]],  [[CAB WP\|WP]],  [[CAB Outputs\|Outputs]],   |
| Code | [[CAB Code Repository\|Code Repo]],  [[CAB Files\|Files]],  [[CAB API Doc\|API Doc]],   |
| User | [[CAB User Dispatch\|User Dispatch]],  [[CAB Interface\|Interface]],  [[CAB Architecture\|Architecture]],  [[CAB CLI\|CLI]],  [[CAB Cards\|Cards]],   |
| External / Publish | [[CAB Documentation Site\|Doc Site]],  [[CAB Project Page\|Project Page]],   |
| Skill / Ops | [[CAB Skill\|Skill]],  [[CAB Claude\|CLAUDE.md]],  [[CAB Move\|Move]],   |
| Skill Anchor (per F116) | [[CAB Facets/Skill Anchor/skill-testing\|skill-testing]],  [[CAB Facets/Skill Anchor/skill-search-rules\|skill-search-rules]],  [[CAB Facets/Skill Anchor/skill-script\|skill-script]],  [[CAB Facets/Skill Anchor/skill-config\|skill-config]],   |
| Doc Facet | [[CAB Facets/Doc Facet/CAB Discussion\|Discussion]],  [[CAB Facets/Doc Facet/CAB Brief\|Brief]],   |
| ... |  |

# BRIEF

- **This file is the *index* of every Facet** — narrow, usually-file-based aspects an anchor can carry. Sibling to [[CAB Traits]] (the broad paradigms). Each row in the dispatch points to one Facet's authoritative spec doc.
- **Adding a new Facet**: create `CAB <Name>.md` (single-file form) or `CAB <Name>/CAB <Name>.md` (folder form when the Facet grows large), use the standard spec-doc shape per [[CAB Aspects]] § Spec-doc structure, then add a wiki-link to the appropriate row in the dispatch table here.
- **Grouping rows** (Structure / Design / Execute / Code / User / External-Publish / Skill-Ops / Skill-Anchor-per-F116 / Doc Facet / `...`) is **semantic, not alphabetical**. New Facets go into the row matching their conceptual category. If no row fits cleanly, drop into `...` as a staging area until a category emerges.
- **The `...` row at the bottom is staging.** When a Facet has stabilized into a clear category, promote it out of `...` into the appropriate row.
- **Facet vs Trait**: file-shaped narrow Aspect → Facet (here). Broad paradigm declared in `.anchor` → Trait (sibling catalog [[CAB Traits]]). Don't conflate.
- **Don't pile spec content into this file.** Each Facet's detail lives in its own `CAB <Name>.md` spec doc. This file is purely the index.
