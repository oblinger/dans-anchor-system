---
description: "the per-doc structural specs"
---

| -[[DAS Facets]]- | → [[DAS]] → [[FCT]] → [DAS Facets](hook://p/DAS%20Facets)  |
| --- | --- |
| Related | [[DAS Skills\|Skills]],  [[DAS Disciplines\|Disciplines]],  [[DAS Traits\|Traits]],  [[DAS Examples\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS\|dans-anchor-system]],   |
|  |  |
|  | **FACETS** |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS Anchor\|Anchor]],  [[DAS Dot Anchor\|Dot Anchor]],  [[DAS Anchor Page\|Anchor Page]],  [[DAS Project Page\|Project Page]],  [[DAS Folder\|Folder]],  [[DAS Anchor Tree\|Anchor Tree]],  [[DAS Naming\|Naming]],  [[DAS Claude\|Claude]],  [[DAS Interface\|Interface]],  [[DAS Move\|Move]],  [[DAS Subs\|Subs]],  [[DAS Dispatch\|Dispatch]],  [[DAS Dispatch Table\|Dispatch Table]],  [[DAS Dispatch Table Design\|Dispatch Table Design]],  [[DAS Design Dispatch\|Design Dispatch]],  [[DAS Dev Dispatch\|Dev Dispatch]],  [[DAS User Dispatch\|User Dispatch]],  [[FEX Project Root]],   |
| [[DAS Hygiene Design\|Hygiene]]+ | [[DAS Ruleset\|Ruleset]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS Backlog\|Backlog]],  [[DAS Query\|Query]],  [[DAS Status\|Status]],  [[DAS Agenda\|Agenda]],  [[DAS Stone\|Stone]],  [[DAS Rocks\|Rocks]],  [[DAS Roadmap\|Roadmap]],  [[DAS Notebook\|Notebook]],  [[DAS Messages\|Messages]],  [[DAS Track\|Track]],  [[DAS Icebox\|Icebox]],  [[DAS Chores\|Chores]],  [[FEX Agenda]],  [[FEX Icebox]],  ~~[[FEX queries]]~~,   |
| [[DAS Design Design\|Design]]+ | [[DAS Design Docs\|Design Docs]],  [[DAS Design Folder\|Design Folder]],  [[DAS PRD\|PRD]],  [[DAS Stories\|Stories]],  [[DAS Architecture\|Architecture]],  [[DAS System Design\|System Design]],  [[DAS Files Architecture\|Files Architecture]],  [[DAS UX Design\|UX Design]],  [[DAS API Design\|API Design]],  [[DAS Testing\|Testing]],  [[DAS Common Testing Types\|Common Testing Types]],  [[DAS Decisions\|Decisions]],  [[DAS Features\|Features]],  [[FEX API]],  [[FEX API Design]],  [[FEX Architecture]],  [[FEX Stories]],  [[FEX Decisions]],  [[FEX Decisions Details]],  [[FEX Roadmap]],   |
| [[DAS Code Design\|Code]]+ | [[DAS Code\|Code]],  [[DAS Code Repository\|Code Repository]],  [[DAS Module Doc\|Module Doc]],  [[DAS CLI\|CLI]],  [[DAS Changes\|Changes]],  [[DAS Specs\|Specs]],  [[DAS All Files\|All Files]],  [[DAS Versions\|Versions]],  [[FEX Files]],  [[FEX Scheduler]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS Doc\|Doc]],  [[DAS Doc Structure\|Doc Structure]],  [[DAS Brief\|Brief]],  [[DAS Cards\|Cards]],  [[DAS Documentation Site\|Documentation Site]],  [[DAS Output\|Output]],   |
| [[DAS stream\|Stream]]  | [[DAS Discussion\|Discussion]],  [[DAS Log\|Log]],  [[DAS Inbox\|Inbox]],  [[DAS Outputs\|Outputs]],  [[DAS WP\|WP]],  [[DAS Completed Roadmap\|Completed Roadmap]],  [[FEX Inbox]],  [[FEX Completed Roadmap]],   |
| *Meta (proposed)* | [[DAS Facet\|Facet]],  [[DAS Skill\|Skill]],  [[DAS Primitives\|Primitives]],  [[DAS Aspects\|Aspects]],  [[DAS Template\|Template]],  [[DAS Template Files\|Template Files]],  [[DAS Template Folders\|Template Folders]],  [[DAS Template Variables\|Template Variables]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],  [[FEX Facet]],  [[FEX Minimal Facet]],  [[FEX Skill]],  [[FEX Minimal Skill]],  [[FEX Rules]],   |
|  |  |
| [[DAS Templates\|Templates]]  | [[agenda]],  [[backlog]],  [[completed-roadmap]],  [[decisions]],  [[icebox]],  [[inbox]],  [[log]],  [[messages]],  [[prd]],  [[query]],  [[roadmap]],  [[rocks]],  [[status]],  [[testing]],  [[track]],   |
| --- | |
| [[anchor-page]]  |  |
| [[project-page]]  |  |
| [[facets/DAS WP]]  | dated work products — papers, reports, polished outputs |

# DAS Facets
The catalog of facets — per-document structural specs — organized by the nine subsystems in [[DAS]] order (groups owning no facets are omitted; *Meta* is a proposed tenth group for the system's own vocabulary).

**Stream is a row here, and each facet appears exactly once.** A stream is a facet whose entries are **dated** — that is the whole differentia, and it is why undated [[DAS Brief|Brief]] sits under Doc rather than here. Membership is still derived rather than hand-kept: a facet is a stream iff its ruleset carries `include:: [[R-stream]]` (six today). Stream facets used to be listed twice — once in their subsystem and again in a cross-cutting block — which is the duplication this row replaces. The cost of the trade is real and worth naming: `Log` and `Inbox` no longer read as Tracking facets, and `Discussion` no longer reads as a Design facet.

**Templates collapsed from seven rows to one, 2026-08-18.** The block mirrored the subsystem rows above it, which was the duplication; and it had rotted badly — of roughly 65 links, **33 were dead**, naming templates that do not exist. `templates/` holds **15** real ones and they are all listed now. The block could not simply be deleted, because it is the only enumeration of them: `templates/` carries an `.anchor` but no marker page, and [[DAS Templates]] specifies the authoring pattern without listing anything. Giving `templates/` a proper anchor page with a catch-all would let this row go away entirely and stay correct by construction — worth doing, and not done here. (Its breadcrumb also points at `[[Templates]]`, which resolves to the unrelated Obsidian template folder in `SYS/Templates/` — a separate latent bug.)

**Singular or plural is decided by what the facet word names** (Dan, 2026-08-18). If the word names the **container**, it is singular — a log, an inbox, a backlog, a notebook are each one thing that holds entries. If it names the **elements**, it is plural — discussions, outputs, rocks, messages, chores are each many things. Most facets name a container, which is why most are singular. This supersedes the older "plural suffix when extracted and multiple" reading in [[DAS file-association]], and it settles a live disagreement in the corpus: the ten anchor-level `{slug} Log/` folders are **correct as singular**, not overdue for a rename to `Logs/`.
