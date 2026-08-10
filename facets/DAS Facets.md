---
description: "the per-doc structural specs"
---

| -[[DAS Facets]]- | → [[DAS]] → [[FCT]] → [DAS Facets](hook://p/DAS%20Facets)  |
| --- | --- |
| Related | [[DAS Skills\|Skills]],  [[DAS Disciplines\|Disciplines]],  [[DAS Traits\|Traits]],  [[DAS Examples\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS\|dans-anchor-system]],   |
|  |  |
|  | **FACETS** — organized by the nine subsystems, in [[DAS]] order |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS Anchor\|Anchor]],  [[DAS Dot Anchor\|Dot Anchor]],  [[DAS Anchor Page\|Anchor Page]],  [[DAS Project Page\|Project Page]],  [[DAS Folder\|Folder]],  [[DAS Anchor Tree\|Anchor Tree]],  [[DAS Naming\|Naming]],  [[DAS Claude\|Claude]],  [[DAS Interface\|Interface]],  [[DAS Move\|Move]],  [[DAS Dispatch\|Dispatch]],  [[DAS Dispatch Table\|Dispatch Table]],  [[DAS Dispatch Table Design\|Dispatch Table Design]],  [[DAS Design Dispatch\|Design Dispatch]],  [[DAS Dev Dispatch\|Dev Dispatch]],  [[DAS User Dispatch\|User Dispatch]],  [[FEX Project Root]],   |
| [[DAS Hygiene Design\|Hygiene]]+ | [[DAS Ruleset\|Ruleset]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS Backlog\|Backlog]],  [[DAS Query\|Query]],  [[DAS Status\|Status]],  [[DAS Agenda\|Agenda]],  [[DAS Stone\|Stone]],  [[DAS Rocks\|Rocks]],  [[DAS Roadmap\|Roadmap]],  [[DAS Completed Roadmap\|Completed Roadmap]],  [[DAS Log\|Log]],  [[DAS Messages\|Messages]],  [[DAS Track\|Track]],  [[DAS Inbox\|Inbox]],  [[DAS Icebox\|Icebox]],  [[FEX Agenda]],  [[FEX Icebox]],  [[FEX Inbox]],  [[FEX queries]],   |
| [[DAS Design Design\|Design]]+ | [[DAS Design Docs\|Design Docs]],  [[DAS Design Folder\|Design Folder]],  [[DAS PRD\|PRD]],  [[DAS Stories\|Stories]],  [[DAS Architecture\|Architecture]],  [[DAS System Design\|System Design]],  [[DAS Files Architecture\|Files Architecture]],  [[DAS UX Design\|UX Design]],  [[DAS API Design\|API Design]],  [[DAS Testing\|Testing]],  [[DAS Common Testing Types\|Common Testing Types]],  [[DAS Decisions\|Decisions]],  [[DAS Discussion\|Discussion]],  [[DAS Features\|Features]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Stories]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Roadmap]],  [[FEX Completed Roadmap]],   |
| [[DAS Code Design\|Code]]+ | [[DAS Code\|Code]],  [[DAS Code Repository\|Code Repository]],  [[DAS Module Doc\|Module Doc]],  [[DAS CLI\|CLI]],  [[DAS Changes\|Changes]],  [[DAS Specs\|Specs]],  [[DAS All Files\|All Files]],  [[DAS Versions\|Versions]],  [[FEX Files]],  [[FEX Scheduler]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS Doc\|Doc]],  [[DAS Doc Structure\|Doc Structure]],  [[DAS Brief\|Brief]],  [[DAS Cards\|Cards]],  [[DAS Documentation Site\|Documentation Site]],  [[DAS Output\|Output]],  [[DAS Outputs\|Outputs]],  [[DAS WP\|WP]],   |
| *Meta (proposed)* | [[DAS Facet\|Facet]],  [[DAS Skill\|Skill]],  [[DAS Primitives\|Primitives]],  [[DAS Aspects\|Aspects]],  [[DAS Template\|Template]],  [[DAS Template Files\|Template Files]],  [[DAS Template Folders\|Template Folders]],  [[DAS Template Variables\|Template Variables]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],  [[FEX Facet]],  [[FEX Minimal Facet]],  [[FEX Skill]],  [[FEX Minimal Skill]],  [[FEX Rules]],   |
| **STREAMS** — cross-cutting: facets whose content is a [[DAS stream\|stream]]. Not a group; these live in their subsystem groups above. |  |
| [[DAS stream\|Streams]]  | [[DAS Discussion\|Discussion]] (doc parent, methods 1+2),  [[DAS Log\|Log]] (anchor parent, methods 2+3),  [[DAS Inbox\|Inbox]] (anchor parent, method 2),  [[DAS Outputs\|Outputs]] (anchor parent, method 3),  [[DAS WP\|WP]] (anchor parent, method 3),  [[DAS Completed Roadmap\|Completed Roadmap]] (anchor parent, method 2 — spec-only, no vault instances), |
| Derived, not hand-kept | this row is the include DAG: a facet is a stream iff its ruleset carries `include:: [[R-stream]]`. Six today, armed 2026-08-08, |
| Attaches, not a stream | [[DAS Brief\|Brief]] — undated, two forms; cites [[DAS file-association]] directly, |
|  |  |
|  |  |
|  | **TEMPLATES** — same groups; each template pairs with its facet above |
| [[DAS Anchor Design\|Anchor]]+ | [[anchor-page\|Anchor Page]],  [[project-page\|Project Page]],  [[folder\|Folder]],  [[anchor-tree\|Anchor Tree]],  [[naming\|Naming]],  [[claude\|Claude]],  [[interface\|Interface]],  [[move\|Move]],  [[dot-anchor\|Dot Anchor]],  [[dispatch-table\|Dispatch Table]],  [[design-dispatch\|Design Dispatch]],  [[dev-dispatch\|Dev Dispatch]],  [[user-dispatch\|User Dispatch]],   |
| [[DAS Hygiene Design\|Hygiene]]+ | [[ruleset\|Ruleset]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS Backlog\|Backlog]],  [[query\|Query]],  [[status\|Status]],  [[agenda\|Agenda]],  [[rocks/{slug} Rocks\|Rocks]],  [[roadmap\|Roadmap]],  [[completed-roadmap\|Completed Roadmap]],  [[log\|Log]],  [[messages\|Messages]],  [[inbox\|Inbox]],  [[icebox\|Icebox]],   |
| [[DAS Design Design\|Design]]+ | [[prd\|PRD]],  [[stories\|Stories]],  [[architecture\|Architecture]],  [[system-design\|System Design]],  [[files-architecture\|Files Architecture]],  [[ux-design\|UX Design]],  [[api-design\|API Design]],  [[testing\|Testing]],  [[common-testing-types\|Common Testing Types]],  [[decisions\|Decisions]],  [[discussion\|Discussion]],  [[design\|Design]],  [[features\|Features]],   |
| [[DAS Code Design\|Code]]+ | [[all-files\|All Files]],  [[module-doc\|Module Doc]],  [[cli\|CLI]],  [[code-repository\|Code Repository]],  [[versions\|Versions]],   |
| [[DAS Doc Design\|Doc]]+ | [[doc-structure\|Doc Structure]],  [[brief\|Brief]],  [[cards\|Cards]],  [[outputs\|Outputs]],  [[documentation-site\|Documentation Site]],  [[wp\|WP]],  [[docs-folder\|Docs Folder]],   |
| *Meta (proposed)* | [[skill\|Skill]],  [[facet\|Facet]],  [[discipline\|Discipline]],  [[trait\|Trait]],  [[template\|Template]],  [[template-files\|Template Files]],  [[template-folders\|Template Folders]],  [[template-variables\|Template Variables]],   |
| --- | |
| [[facets/DAS WP]]  | dated work products — papers, reports, polished outputs |

# DAS Facets
The catalog of facets — per-document structural specs — organized by the nine subsystems in [[DAS]] order (groups owning no facets are omitted; *Meta* is a proposed tenth group for the system's own vocabulary).
