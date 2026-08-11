---
description: "cross-cutting concepts the agent reads"
---

| -[[DAS Disciplines]]- | : cross-cutting concepts the agent reads<br>→ [[DAS]] → [[disciplines]] → [DAS Disciplines](hook://p/DAS%20Disciplines)  |
| --- | --- |
| Related | [[DAS Skills\|Skills]],  [[DAS Facets\|Facets]],  [[DAS Traits\|Traits]],  [[DAS Examples\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS Disciplines Brief\|Brief]],  [[DAS\|dans-anchor-system]],   |
|  |  |
|  | **DISCIPLINES** — organized by the nine subsystems, in [[DAS]] order |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS anchor-dag\|anchor-dag]],  [[DAS Linked Mode\|Linked Mode]],  [[DAS progressive-disclosure\|progressive-disclosure]],  [[DAS spine\|spine]] *(slot)*,  [[DAS heart\|heart]] *(slot)*,,   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS workflow\|workflow]],  [[DAS ask-format\|ask-format]],  [[DAS verification\|verification]],  [[DAS granularity\|granularity]],   |
| [[DAS Code Design\|Code]]+ | [[DAS code-repo\|code-repo]],  [[DAS rust\|rust]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS markdown\|markdown]],  [[DAS formats\|formats]],  [[DAS stream\|stream]],  [[DAS file-association\|file-association]],  [[DAS technical-answer\|technical-answer]],   |
| [[DAS Drive Design\|Drive]]+ | [[DAS mode\|mode]],  [[DAS role\|role]],   |
| --- | |
| [[DAS feed]]  | Discipline — the second DAG over anchors. `feeds:` in `.anchor` names the anchors that feed into this one; out-edges are computed by inversion. A feed facet materializes as a folder of one-file-per-item with a roster on top, each item carrying `key::` parameters and a `line::` rendering. The top group of a roster is the export set, and it propagates to every anchor declaring this one as a source. Members: Rocks, and the item register. DRAFT — the facet-side naming is pending TINK F312 Q1. |

# DAS Disciplines
The catalog of discipline facets — cross-cutting concepts the agent reads — organized by the nine subsystems in [[DAS]] order (groups owning no disciplines are omitted).

**Disciplines are one *group of facets*, not a rival kind alongside them** (decided 2026-08-11). The definition is positive: a discipline facet's ruleset selects **nothing of its own** — it rides on whatever the file and slot facets already select, which is why its `where::` reads `` `always` `` or a bare `**/*.md`, and why it has no template. Full definitions of the three groups: [[DAS Facet]] § Facet groups. In prose keep saying *discipline*, the way one says *mammal* rather than *mammal animal*; the compound `discipline facet` is for where the structure needs to be visible, as in this catalog's own name.

**Two entries below are slot facets shelved here**, kept beside their siblings while the folders stay as they are — [[DAS spine]] and [[DAS heart]] each govern a **region** (above the H1; directly below it) and each has a template, so neither meets the no-selector test. They read as disciplines only because the `where::` grammar cannot express a *positional* region and both fall back to `` `always` ``. The folder is not the taxonomy; the spec's own declaration is.

*The `workflow` concept doc lives at [[DAS workflow]]; the `state` tooling stays in `skills/workflow/` (path-referenced). The concept is slated to be renamed `flow` (F158 § D, pending). `CAB Linked Mode` keeps its as-moved name pending the same rename.*
