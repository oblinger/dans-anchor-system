---
description: "cross-cutting concepts the agent reads"
---

# DAS Disciplines
The catalog of disciplines — cross-cutting concepts the agent reads — organized by the nine subsystems in [[DAS]] order (groups owning no disciplines are omitted).

| -[[DAS Disciplines]]- | → [[DAS]] → [[disciplines]] → [DAS Disciplines](hook://p/DAS%20Disciplines)<br>: cross-cutting concepts the agent reads |
| --- | --- |
| Related | [[DAS Skills\|Skills]],  [[DAS Facets\|Facets]],  [[DAS Traits\|Traits]],  [[DAS Examples\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS Disciplines Brief\|Brief]],  [[DAS\|dans-anchor-system]],   |
|  |  |
|  | **DISCIPLINES** — organized by the nine subsystems, in [[DAS]] order |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS anchor-dag\|anchor-dag]],  [[DAS Linked Mode\|Linked Mode]],  [[DAS progressive-disclosure\|progressive-disclosure]],  [[DAS spine\|spine]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS workflow\|workflow]],  [[DAS ask-format\|ask-format]],  [[DAS verification\|verification]],  [[DAS granularity\|granularity]],   |
| [[DAS Code Design\|Code]]+ | [[DAS code-repo\|code-repo]],  [[DAS rust\|rust]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS markdown\|markdown]],  [[DAS formats\|formats]],  [[DAS stream\|stream]],  [[DAS file-association\|file-association]],  [[DAS technical-answer\|technical-answer]],   |
| [[DAS Drive Design\|Drive]]+ | [[DAS mode\|mode]],  [[DAS role\|role]],   |
| --- | |
| [[DAS feed]]  | Discipline — the second DAG over anchors. `feeds:` in `.anchor` names the anchors that feed into this one; out-edges are computed by inversion. A feed facet materializes as a folder of one-file-per-item with a roster on top, each item carrying `key::` parameters and a `line::` rendering. The top group of a roster is the export set, and it propagates to every anchor declaring this one as a source. Members: Rocks, and the item register. DRAFT — the facet-side naming is pending TINK F312 Q1. |
| [[DAS rider]]  | Discipline. A RIDER is typed content that rides on a parent — Discussion, Log, Brief, Decisions and their kin. Owns the three placement methods (inline H1 / sibling file / sibling folder), the cardinality→placement rule, the suffix-naming convention, one-way migration, the one-form-per-parent invariant, and parent linkage. The parent may be a document OR an anchor. Two dimensions ride on top: dated? and cardinality. The dated case is the specialization [[DAS stream]] (Discussion, Log); undated riders (Brief, Decisions) cite this umbrella directly. Renamed from `file-association` 2026-08-06. NOT progressive-disclosure (reader layering) or markdown (text rules). |
| [Mode](hook://Mode)  |  |
| [Role](hook://Role)  |  |

*The `workflow` concept doc lives at [[DAS workflow]]; the `state` tooling stays in `skills/workflow/` (path-referenced). The concept is slated to be renamed `flow` (F158 § D, pending). `CAB Linked Mode` keeps its as-moved name pending the same rename.*
