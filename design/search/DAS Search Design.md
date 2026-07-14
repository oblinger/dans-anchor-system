---
description: Subsystem design for the Search group — the research verbs that answer questions about the world (find one, profile one, compare many, buy one) and file dated result docs.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Search Design](hook://p/DAS%20Search%20Design)
# DAS Search Design — the design of the Search subsystem
Search is the research subsystem: four verbs that answer a question about the world — locate one entity, build a dossier on one, compare many, or find where to buy one — each running at a declared depth tier and filing a dated, source-attributed result doc.

![[DAS Search Design.svg|3000]]

| **Skills**                       |                                                                                                                |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [[DAS Find\|/find]]              | Locate ONE entity from many candidates — identifier + canonical URL + confidence; disambiguates ties.           |
| [[DAS Profile\|/profile]]        | Structured description of ONE entity — summary card → full profile → complete dossier ("Dig").                  |
| [[DAS Survey\|/survey]]          | Multi-dimensional comparison across MANY entities — table + interpretive notes; meta-survey sub-pattern.        |
| [[DAS Purchase\|/buy]]           | For a known product: verified buy locations, live prices, stock — driven through a real browser.                |
|                                  |                                                                                                                |
| **Facets**                       |                                                                                                                |
| [[DAS Topic\|Topic]]             | The standing topic tree — Search's results file into `Topic/Search/{Find,Profile,Survey}/` as dated docs.       |
|                                  |                                                                                                                |
| **Traits**                       |                                                                                                                |
| [[Topic Anchor]]                 | The output home — Search writes into the standing Topic anchor rather than declaring anything per-anchor.       |
|                                  |                                                                                                                |
| **Library**                      |                                                                                                                |
| **Type rules**                   | Per-entity-type playbooks the verbs load — [[DAS Person\|person]] · [[DAS Corp\|corp]] · [[DAS Product\|product]] · [[DAS Book\|book]] · [[DAS Software\|software]]. |
| [[DAS Search Overview\|Search Overview]] | The group's own routing doc — which verb for which question shape.                                      |

## Overview

Search's contract: **one verb per question shape, one dated doc per answer.** The shapes partition cleanly — *which one is it?* (`/find`), *tell me about it* (`/profile`), *how do the candidates compare?* (`/survey`), *where do I get it?* (`/buy`) — and each verb refuses the neighboring shape (find won't dossier; survey won't pick one). Every run declares a depth tier (**Quick / Standard / Deep**) so cost is a conscious choice, loads the entity's **type rules** (person · corp · product · book · software) for what a complete answer must cover, and lands a `YYYY-MM-DD {name}.md` result under `Topic/Search/` — source-attributed, confidence-marked, findable across sessions. `/buy` carries the operational edge: retailers bot-wall every headless fetch, so it drives a real browser via `/ctrl`.

Boundaries: **Search answers about the *world*, not the vault** — locating things inside the vault is `ha` + wiki-link resolution, not a Search verb. **Utility provides the reach** — `/ctrl`'s browser automation is how `/buy` and deep research get past bot walls. **Results are content, not tracking** — dated docs in the Topic tree, never backlog rows; a research task that spawns work gets its row through Tracking.

## Coordinated examples

Search is illustrated by its own output tree — the dated result docs under `Topic/Search/Find/`, `Topic/Search/Profile/`, and `Topic/Search/Survey/` are the worked examples.

## Design record

- [[DAS Find Design]] · [[DAS Profile Design]] · [[DAS Survey Design]] · [[DAS Purchase Design]] — per-verb design docs.
- [[DAS Research\|Research]] · [[DAS Research Skill\|Research Skill]] · [[DAS Meta Survey\|Meta Survey]] — the research playbook pages the verbs draw on.
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Search Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
