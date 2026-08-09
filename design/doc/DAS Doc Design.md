---
description: Subsystem design for the Doc group — the authoring verbs that shape, illustrate, polish, and route documents, plus the round-trip to external document apps.
---

:>> [[DAS]] → [design](hook://design) → [DAS Doc Design](hook://p/DAS%20Doc%20Design)
# DAS Doc Design — the design of the Doc subsystem
Doc is the authoring subsystem: its verbs shape a document's structure (`/md`), illustrate it (`/viz`), polish its prose (`/redline`), and round-trip its content with the outside document apps (`/io`).

![[DAS Doc Design.svg|3000]]

| **Skills**                                 |                                                                                                          |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| [[DAS MD\|/md]]                            | Markdown utility verbs — TOC, dispatch tables, cards, file-trees, track-changes.                          |
| [[DAS Viz\|/viz]]                          | Visual drafting — hand-written SVG, excalidraw, charts, mermaid, dot, slides, docx/pdf export.            |
| [[redline/SKILL\|/redline]]                | Collaborative text polish — section mode with writeback, file mode with versioned dated copies.           |
| [[DAS IO\|/io]]                            | External I/O — Google Sheets / Slides / Docs / Drive, Apple Mail, Notion.                                 |
|                                            |                                                                                                          |
| **Facets**                                 |                                                                                                          |
| [[DAS Doc\|Doc]]                           | The base document facet — what any vault doc owes its reader.                                             |
| [[DAS Doc Structure\|Doc Structure]]       | Structural conventions — heading spine, zones, section ordering.                                          |
| [[DAS Brief\|Brief]]                       | The agent-facing condensed form — lean body, detail lives here.                                           |
| [[DAS Cards\|Cards]]                       | Cheat / summary / detail card sets built by `/md cards`.                                                  |
| [[DAS Documentation Site\|Documentation Site]] | A published multi-page documentation surface.                                                        |
|                                            |                                                                                                          |
| **Traits**                                 |                                                                                                          |
| [[Paper Anchor]]                           | Declares an anchor whose product is a written work — paper-shaped tree and verbs.                         |
|                                            |                                                                                                          |
| **Library**                                |                                                                                                          |
| **`md-toc.py` + `/md` scripts**            | The mechanical markdown maintainers — TOC regeneration, dispatch-table builds, card builds.               |
| **`excalidraw_to_svg.py` / `svg-jiggle.py`** | The figure toolchain — excalidraw → SVG/PNG export; deterministic geometric repair.                     |
| **`gsa` CLI**                              | Google Suite Access — the engine under `/io` (never called directly; `/io` is the interface).             |
| Disciplines                                | [[DAS stream]] · [[DAS file-association]] · [[DAS technical-answer]]                          |
| Rulesets                                   | [[R-markdown]] · [[R-md]] · [[R-doc]] · [[R-doc-facet]] · [[R-doc-structure]] · [[R-progressive]] · [[R-brief]] · [[R-cards]] · [[R-paper]] · [[R-wp]] · [[R-output-group]] · [[R-fct-outputs]] · [[R-fct-user-dispatch]] · [[R-documentation-site]] · [[R-file-association]] · [[R-stream]] · [[R-diagram]] · [[R-diagram-geometry]] · [[R-sugiyama]] · [[R-c4]] · [[R-svg-hygiene]] · [[R-svg-jiggle]] · [[R-tufte-data-ink]] · [[R-wcag-contrast]] · [[R-bringhurst-typography]] |

## Overview

Doc's contract: **every document conforms to a facet, and the verbs keep it that way.** The [[DAS markdown]] discipline sets the writing form (definition lists, wiki-links live, no markdown inside fences); the facet specs say what each document *kind* owes its reader; the `/md` verbs mechanically maintain the derived structure (TOCs, dispatch tables, cards) so hand-editing never drifts it. `/viz` produces every figure with an editable source beside the export (per [[feedback_figure_source_alongside_output|the source-alongside-output rule]] — `.excalidraw`/`.d2`/`.py` next to `.svg`/`.png`); `/redline` polishes prose without stealing the author's voice. `/io` is the boundary crossing: content moves to and from Google Workspace, Apple Mail, and Notion through one interface.

Boundaries: **structure rules are Doc's, firing is Hygiene's** — the R-markdown family is authored here and enforced by Warden and `/audit`. **Progressive disclosure is anchor navigation** — the dispatch-table and preface-zone disciplines belong to the Anchor group; Doc's verbs build the tables mechanically to that spec. **Figures serve every group** — the other subsystem profiles' figures are `/viz` products; the toolchain lives here.

## Coordinated examples

Doc is illustrated by the vault's own high-traffic pages — every dispatch masthead, TOC table, and subsystem-profile figure is a `/md` / `/viz` product conforming to this group's facets.

## Design record

- [[DAS MD Design]] · [[DAS Viz Design]] — per-verb design docs.
- **Grouping (agent, 2026-07-14):** `/redline` — previously ungrouped — assigned here at this profile pass. `/atlas` was briefly here, then moved to [[DAS Utility Design|Utility]] (user ruling, same day: it maintains the vault, it doesn't author documents).
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Doc Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
