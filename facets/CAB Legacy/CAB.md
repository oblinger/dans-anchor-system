---
traits: [Skill]
description: Common Anchor Blueprint — the spec model for what an anchor is, what Aspects it carries, and how the system reads it.
---
# CAB — Common Anchor Blueprint

Every anchor is described by **Aspects** (see [[CAB Aspects]] for the unified model): **Traits** (broad paradigms declared in the anchor's `traits:` list — `Code`, `Skill`, `Publishable`, ...) and **Facets** (narrow, usually-file-based aspects defined per-spec under `CAB/CAB Facets/` — `Backlog`, `Architecture`, `Interface`, ...). Every Trait and Facet spec includes a Constraints section (legal usage; mutual exclusion) and an Expected Usage section (positive guidelines). CAB governs anchor **structure/composition** (what an anchor *contains*); it is complementary to — not overlapping with — [[Anchorage]] / [[ANC Standard]], which governs anchor **identity** (slug, metadata declaration, resolution, the DAG). Structure here, identity there.

| -[[CAB]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [CAB](hook://p/CAB)<br>:  |
| --- | --- |
| Related | [[SKA]],  [[SKL]],  [[SKL Skills]],   |
| External | [[cab/SKILL\|/cab skill]],  [[CAB Base\|Base]],   |
| [LINT/LINT](hook://LINT/LINT) | [[LINT Docs]],   |
| Plan | [[FCT Discussion\|Discussion]],   |
| Dev | [[CAB Docs\|Docs]],   |
| Traits | [[Simple Anchor\|Simple]],  [[Topic Anchor\|Topic]],  [[Code Anchor\|Code]],  [[Paper Anchor\|Paper]],  [[Skill Anchor\|Skill]],  [[Track]],   |
| [[Rulesets]]~~+ | [[R-api]],  [[R-arch]],  [[R-code]],  [[R-completed-roadmap]],  [[R-dated-entry-stream]],  [[R-design]],  [[R-diagram]],  [[R-discussion]],  [[R-doc]],  [[R-facet]],  [[R-git]],  [[R-log]],  [[R-markdown]],  [[R-naming]],  [[R-ob]],  [[R-paper]],  [[R-prd]],  [[R-process]],  [[R-roadmap]],  [[R-simple]],  [[R-skill]],  [[R-skill-anchor]],  [[R-status]],  [[R-stories]],  [[R-test]],  [[R-testing]],  [[R-topic]],  [[R-trait]],  [[R-ux]],  [[takehome_20260128/README]],  [[Rulesets Brief]],  [[takehome_20260128/README]],  [[takehome_20260128/README]],  [[takehome_20260128/README]],  [[2025 Online Presence/README]],  [[2025 Online Presence/README]],   |
| [[CAB Disciplines\|Disciplines]]+ | [[FCT Brief\|Brief]],  [[CAB Disciplines Brief\|Disciplines Brief]],  [[DSC Dispatch Table\|Dispatch Table]],  [[DSC Linked Mode\|Linked Mode]],  [[CAB Mode\|Mode]],  [[CAB Dispatch Table Design\|Dispatch Table Design]],   |
| [[CAB Facets\|Facets]]~~+ | [[CAB Facets/Backlog\|Facets/Backlog]],  [[CAB All Files\|All Files]],  [[CAB Anchor Page\|Anchor Page]],  [[CAB API Design\|API Design]],  [[CAB API Doc\|API Doc]],  [[CAB Architecture\|Architecture]],  [[FCT Brief\|Brief]],  [[CAB Cards\|Cards]],  [[CAB Claude\|Claude]],  [[CAB CLI\|CLI]],  [[CAB Code Repository\|Code Repository]],  [[CAB Completed Roadmap\|Completed Roadmap]],  [[CAB Facets/CAB Decisions\|Facets/CAB Decisions]],  [[CAB Design Dispatch\|Design Dispatch]],  [[CAB Facets/CAB Design\|Facets/CAB Design]],  [[CAB Dev Dispatch\|Dev Dispatch]],  [[FCT Discussion\|Discussion]],  ~~[[CAB Documentation Site\|Documentation Site]],  [[CAB Features\|Features]],  [[CAB Files\|Files]],  [[CAB Folder\|Folder]],  [[CAB Icebox\|Icebox]],  [[CAB Inbox\|Inbox]],  [[CAB Interface\|Interface]],  [[CAB/CAB Log]],  [[CAB Facets/CAB Messages\|Facets/CAB Messages]],  [[CAB Move\|Move]],  [[CAB Naming\|Naming]],  [[CAB Outputs\|Outputs]],  [[CAB Plan Dispatch\|Plan Dispatch]],  [[CAB Facets/CAB PRD\|Facets/CAB PRD]],  [[CAB Project Page\|Project Page]],  [[CAB Roadmap\|Roadmap]],  [[FCT Ruleset\|Ruleset]],  [[CAB Skill\|Skill]],  [[CAB Status\|Status]],  [[CAB Stories\|Stories]],  [[CAB System Design\|System Design]],  [[CAB Testing\|Testing]],  [[CAB Track Dispatch\|Track Dispatch]],  [[CAB Triage\|Triage]],  [[CAB User Dispatch\|User Dispatch]],  [[CAB UX Design\|UX Design]],  [[CAB WP\|WP]],  [[Docs]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],  [[TSK User Guide]],  [[Backlog]], |
|  |  |
| --- | |
| [[CAB Conventions\|Conventions]] | Recurring practices that show up across anchors but aren't roles the anchor plays. |
| [[CAB/CAB Log]] | Change log — date-stamped record of CAB structure changes; doubles as the rewire spec source when migrations propagate format changes across anchors. |
| [[CAB Maintain Design\|Maintain Design]] | design distillation — the maintain skill (keep derived files in sync with source files) |
| [[CAB Track\|Track]] | CAB project-work tracking |
| [[compile]] | ~~ |
| [[LINT Design]] | system design — PRD, architecture, interface, principles |
| [[LINT Log]] |  |
| [[LINT Rules]] |  |
| [[LINT System Suppressions]] |  |
| [[LINT Tool]] | Lint an anchor — static analysis against CAB type rules. |
| ~~[[LINT Track]]~~ | execution state — backlog, features, roadmap |

# BRIEF

- **What this file is.** The top-level page for the Common Anchor Blueprint — the spec model for *what an anchor is*. Defines Aspects (Traits + Facets) and points at every sub-catalog. It is the entry point to the CAB system, not a catalog itself.
- **Three sub-anchor groupings.** CAB decomposes into [[TRT]] (broad paradigms declared in `traits:` — `Code`, `Skill`, `Publishable`, ...), [[CAB Facets]] (narrow per-file aspects — `Backlog`, `Architecture`, `Interface`, ...), and [[CAB Disciplines]] (cross-cutting practices like `Brief`, `Dispatch Table`, `Mode`, `Linked Mode`). Each grouping is its own catalog with its own brief.
- **To add a new Facet or Discipline.** Don't edit this page first — go to [[CAB Facets]] / [[CAB Disciplines]] and follow that catalog's `# BRIEF`. The new spec file gets a row in the catalog; this page's dispatch table picks it up via the `Facets+` / `Disciplines+` aggregated rows.
- **To add a new Trait.** Same pattern — author the new trait spec under `traits/` per [[TRT]]'s brief; the `Traits` row on this page surfaces it.
- **What does NOT belong here.** Skills are not CAB. Skills live in `~/.claude/skills/` (mirrored via `symlinks/_.claude/skills/`); CAB *references* skills (e.g. [[cab/SKILL]]) but does not own them. Anchor-local rules belong in `{NAME} Rules.md` / `{NAME} Decisions.md`, not in CAB.
- **Cross-reference integrity.** When CAB structure changes (new Trait/Facet/Discipline, renamed grouping), update [[CAB Base]]'s dispatch tables and [[CAB All Files]]'s file tree in the same pass — they index the same spec set.
- **Don't pile content into this file.** Each Aspect's full detail lives in its own spec file under `CAB Facets/` / `CAB Disciplines/` / `traits/`. The dispatch table row is the dashboard summary; the spec file is the substance.
