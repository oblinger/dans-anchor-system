---
description: Subsystem design for the Anchor group — the folder-shape substrate every other subsystem rides on, plus the lifecycle verbs that create, restructure, relocate, publish, and archive anchors.
---

:>> [[DAS]] → [design](hook://design) → [DAS Anchor Design](hook://p/DAS%20Anchor%20Design) 
# DAS Anchor Design — the design of the Anchor subsystem
Anchor is the substrate subsystem: a named folder + `.anchor` marker + dispatch-table anchor page is the unit all of the vault's organization rides on, and this group's verbs carry an anchor through its whole life — created, restructured, relocated, published, and finally archived.

![[DAS Anchor Design.svg|3000]] 

| **Skills**                             |                                                                                                                                                           |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[DAS Create\|/create]]                | Create a new thing — anchor, work-product folder (`/create wp`), feature, spec, rule.                                                                     |
| [[DAS Migrate\|/migrate]]              | Change an anchor in place — slug, traits, structure, naming.                                                                                              |
| [[DAS Move\|/move]]                    | Relocate an anchor and update every path-dependent system (HookAnchor, breadcrumbs, cross-references).                                                    |
| [[DAS Publish\|/publish]]              | Deploy the anchor's public page to the web (method from `.anchor`).                                                                                       |
| [[DAS Yore\|/yore]]                    | Archive to `Yore/` — date-prefixed zips in the parent's archival folder.                                                                                  |
| [[DAS Streams\|/streams]]              | Content-stream definitions for an anchor (stub — runbook to come).                                                                                        |
| [[DAS Anchor Toolkit\|/anchor]]        | The toolkit umbrella — single-anchor ops (config, docs-audit) and system ops (scan, status, `/anchor install`).                                           |
|                                        |                                                                                                                                                           |
| **Facets**                             |                                                                                                                                                           |
| [[DAS Anchor\|Anchor]]                 | The concept itself — a named folder referenceable as a whole; slug, description, traits.                                                                  |
| [[DAS Dot Anchor\|.anchor]]            | The marker file — slug, description, `traits:`, `code:`, `mirror:` keys.                                                                                  |
| [[DAS Anchor Page\|Anchor Page]]       | `{NAME}.md` — the anchor's home page, led by its dispatch masthead.                                                                                       |
| [[DAS Dispatch Table\|Dispatch Table]] | The masthead table — identity cell, group rows, separator-row automation.                                                                                 |
| [[DAS Anchor Tree\|Anchor Tree]]       | The standard folder tree an anchor unfolds into.                                                                                                          |
|                                        |                                                                                                                                                           |
| **Traits**                             |                                                                                                                                                           |
| `traits:` *(the mechanism)*            | The `.anchor` `traits:` list is itself this group's contribution — every other subsystem's trait rides it.                                                |
| [[anchor-base]] · [[Simple Anchor]] · [[collection]] · [[Skill Anchor]] | The anchor-kind traits — the base behaviors every anchor rides, plus the simple / collection / skill-folder shapes.      |
|                                        |                                                                                                                                                           |
| **Library**                            |                                                                                                                                                           |
| **`anchor-system`**                    | The management CLI — config namespace, user-env keys, install plumbing.                                                                                   |
| Disciplines                            | [[DAS anchor-dag]] · [[DAS Linked Mode]] · [[DAS progressive-disclosure]]                                                                                 |
| Rulesets                               | [[R-anchor]] · [[R-dot-anchor]] · [[R-anchor-page]] · [[R-anchor-tree]] · [[R-anchor-group]] · [[R-dispatch-table]] · [[R-dispatch-group]] · [[R-naming]] · [[R-project-page]] · [[R-fct-folder]] · [[R-fct-move]] · [[R-fct-claude]] · [[R-fct-interface]] · [[R-topic]] · [[R-simple]] |

## Overview

Anchor's contract: **everything lives in an anchor, and an anchor is always navigable.** A named folder becomes an anchor by carrying a `.anchor` marker (slug + description + traits); its `{NAME}.md` page opens with the dispatch masthead that routes one or two clicks to anything inside (per [[DAS progressive-disclosure]]); slug and basename resolution rides [[HA|HookAnchor]] — a separate application the anchor system is compatible with, not part of it. The lifecycle runs left to right: `/create` mints the shape (anchors, and dated work-product folders via `/create wp`) → `/migrate` evolves it in place and `/move` relocates it (updating every path-dependent system) → `/publish` optionally ships its public page → `/yore` retires content as date-prefixed archives. `/anchor` is the toolkit umbrella, covering both single-anchor operations and the system machinery, including the per-machine `/anchor install`.

Boundaries: **the substrate serves the other subsystems** — Tracking, Design, Code, and the rest are traits and folder shapes declared *on* an anchor, never parallel structures beside it. **Hygiene audits what Anchor defines** — the R-anchor family is authored here, fired by Warden and `/audit`. **Code anchors extend the marker** — the `code:` and `mirror:` keys (Two-Way Doc Mirror per [[DAS Code Repository]] § Doc Mirror) are `.anchor` vocabulary owned by this group, exercised by the Code subsystem. **HookAnchor is a separate application** — the anchor system depends on it for slug/name → path resolution (`ha -p`) and stays compatible with it, but `ha` is not part of this group's library; it has its own anchor, backlog, and release life at [[HA]].

## Coordinated examples

Anchor is illustrated inside the coherent worked worlds at [[FEX]] (HBR, FEX Repo) — each world is itself a complete anchor with marker, masthead, and tree.

## Design record

- [[DAS Anchor Toolkit Design]] · [[DAS Create Design]] · [[DAS Install Design]] · [[DAS Migrate Design]] · [[DAS Move Design]] · [[DAS Publish Design]] · [[DAS Streams Design]] · [[DAS WP Design]] · [[DAS Yore Design]] — per-verb design docs.
- **Consolidation (user, 2026-07-14 — F234 Q1=A, executed as [[Tink Backlog#^T020|T020]]):** nine verbs → seven. `/wp` folded into `/create` (action file `create-wp`); `/anchor` promoted to the user-invocable toolkit umbrella absorbing `/install` (action file `anchor-install`), deliberately overloaded across single-anchor and whole-system operations; `/migrate` = identity/shape in place, `/move` = location ("location" struck from migrate's claim). The stale CAB-era `/create` and `/install` runbooks were rewritten in the same pass; `cab-create` promoted from legacy to `create-anchor`.
- [[DAS Dispatch Table Design]] — the masthead's own design record.
- **Boundary ruling (user, 2026-07-14):** HookAnchor (`ha`) is a *separate application*, not part of the anchor system's library — the system is compatible with it and depends on it for resolution, but does not own it. Profiles reference it as an external dependency only.
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Anchor Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
