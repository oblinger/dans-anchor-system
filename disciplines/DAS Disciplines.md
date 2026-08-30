---
description: "cross-cutting concepts the agent reads"
---

| -[[DAS Disciplines]]- | : cross-cutting concepts the agent reads<br>→ [[DAS]] → [[disciplines]] → [DAS Disciplines](hook://p/DAS%20Disciplines)  |
| --- | --- |
| Related | [[DAS Skills\|Skills]],  [[DAS Facets\|Facets]],  [[DAS Traits\|Traits]],  [[FEX\|Examples]],  [[DAS Rulesets\|Rulesets]],  [[DAS Disciplines Brief\|Brief]],  [[DAS\|dans-anchor-system]],   |
|  |  |
| [[DAS]]  | **DISCIPLINES** — organized by the nine subsystems, in  order |
| [[DAS Anchor Design\|Anchor]]+ | [[DAS anchor-dag\|anchor-dag]],  [[DAS Linked Mode\|Linked Mode]],  [[DAS progressive-disclosure\|progressive-disclosure]],  [[DAS spine\|spine]],  [[DAS heart\|heart]],  [[DAS orientation-line\|orientation-line]],  [[DAS electric-zone\|electric-zone]],   |
| [[DAS Tracking Design\|Tracking]]+ | [[DAS workflow\|workflow]],  [[DAS ask-format\|ask-format]],  [[DAS verification\|verification]],  [[DAS granularity\|granularity]],   |
| [[DAS Code Design\|Code]]+ | [[DAS code-repo\|code-repo]],  [[DAS rust\|rust]],   |
| [[DAS Doc Design\|Doc]]+ | [[DAS markdown\|markdown]],  [[DAS formats\|formats]],  [[DAS stream\|stream]],  [[DAS file-association\|file-association]],  [[DAS technical-answer\|technical-answer]],   |
| [[DAS Drive Design\|Drive]]+ | [[DAS mode\|mode]],  [[DAS role\|role]],   |
| --- | |
| [[DAS feed]]  | Discipline — the second DAG over anchors. `feeds:` in `.anchor` names the anchors that feed into this one; out-edges are computed by inversion. A feed facet materializes as a folder of one-file-per-item with a roster on top, each item carrying `key::` parameters and a `line::` rendering. The top group of a roster is the export set, and it propagates to every anchor declaring this one as a source. Members: Rocks, and the item register. DRAFT — the facet-side naming is pending TINK F312 Q1. |

# DAS Disciplines
The catalog of discipline facets — cross-cutting concepts the agent reads — organized by the nine subsystems in [[DAS]] order (groups owning no disciplines are omitted).

**Disciplines are one *group of facets*, not a rival kind alongside them** (decided 2026-08-11). The definition is positive: a discipline facet's ruleset selects **nothing of its own** — it rides on whatever the file and slot facets already select, which is why its `where::` reads `` `always` `` or a bare `**/*.md`, and why it has no template. Full definitions of the four groups: [[DAS Facet]] § Facet groups. In prose keep saying *discipline*, the way one says *mammal* rather than *mammal animal*; the compound `discipline facet` is for where the structure needs to be visible, as in this catalog's own name.

**Five entries below are not disciplines**, kept beside their siblings while the folders stay as they are. [[DAS spine]], [[DAS heart]], [[DAS orientation-line]] and [[DAS electric-zone]] each govern a **region** (above the H1; directly below it; the one line between them; everything below a dispatch table's separator), so none meets the no-selector test; they read as disciplines only because the `where::` grammar cannot express a *positional* region and all four fall back to `` `always` ``. [[DAS stream]] is a slot facet outright — `R-stream` carries `` where:: `sentinel: ^## \d{4}-\d{2}-\d{2} —` ``, a selector as explicit as any facet's. [[DAS file-association]] is neither, and is the interesting one — see § What the classification found. The folder is not the taxonomy; the spec's own declaration is.

# What the classification found
Every entry was tested mechanically rather than by reading its prose: resolve the discipline to its ruleset, read the ruleset's `where::`, and ask what that selects ([[TINK Backlog#^T196|TINK T196]], 2026-08-11). The test is cheap and it disagreed with the guesses that prompted it, which is the reason for running it rather than arguing.

| Verdict | Count | Evidence |
|---|---|---|
| Genuine disciplines | 15 | No ruleset of their own at all, or one selecting `` `always` `` / `**/*.md` |
| Slot facet | 1 | [[DAS stream]] — `R-stream` selects by `sentinel:` |
| Neither | 1 | [[DAS file-association]] — `R-file-association` selects `` `anchor` `` |
| Already reclassified (Q007) | 2 | [[DAS spine]], [[DAS heart]] |

**Two of the three predictions in T196 were wrong, and the way they were wrong is worth keeping.** The row proposed [[DAS ask-format]], [[DAS stream]] and [[DAS file-association]] as slot candidates, reasoning that `ask-format` governs the `## Open Questions` block and that the other two "declare a cardinality, which a thing with no extent should not have." Only `stream` survived. `ask-format` has **no ruleset of its own**: the `## Open Questions` block is checked by `R-fct-features`, `R-prd`, `R-query` and `R-backlog` — each of which selects its own host *file*, with the block's shape riding along. Governing a region and *selecting* one are different things, and only the second makes a slot facet. That is the no-selector test doing exactly the work it was defined to do, against the intuition of the person who wrote it.

## `where:: anchor` is a fourth way to reach a subject, and the group definitions did not have it
[[DAS file-association]] resolves to `R-file-association`, whose selector is `` where:: `anchor` `` — it is evaluated once per anchor, against the anchor as a whole. That is not "no selector of its own", so it is not a discipline; it is not a file, and it is not a region. It reaches a **folder**, which would make it a folder facet — except that [[DAS Facet]] § Facet groups defined that group as *"the selector reaches a folder by globbing its contents — the trailing `/**` is the form"*, and this selector has no glob at all.

The definition was too narrow. There are **three** ways a selector reaches a folder, all live in the corpus today:

- **by globbing its contents** — `` `file:{anchor}/**/* Rocks/**` `` ([[DAS Rocks]], [[DAS WP]]).
- **by anchor scope** — `` `anchor` ``, evaluated once per anchor. Eleven rules use it, so this is a populated form and not an oddity: `R-anchor-page`, `R-design`, `R-git`, `R-code-surface`, `R-track-group`, `R-output-group`, `R-dispatch-group`, `R-design-docs-group`, `R-documentation-site`, `R-anchor-group`, and `R-file-association`.
- **by marker-file proxy** — `` `file: **/.anchor` `` ([[DAS Folder]], [[DAS Dot Anchor]]), where a file inside the directory stands in for the directory.

All three name a directory as the subject; they differ only in how the engine gets there. So the folder group is defined by **what the selector reaches, not by the syntax it reaches it with** — which was the intended principle from the start, stated too specifically. `file-association` is a folder facet on the corrected reading.

*(This did not turn up when the four groups were minted because the minting pass read `R-fct-folder` and the two `* Rocks/**`-style selectors, and never asked what `` `anchor` `` was. A classification pass over all 19 entries is what found it — the same reason T196 existed.)*

*The `workflow` concept doc lives at [[DAS workflow]]; the `state` tooling stays in `skills/workflow/` (path-referenced). The concept is slated to be renamed `flow` (F158 § D, pending). `CAB Linked Mode` keeps its as-moved name pending the same rename.*
