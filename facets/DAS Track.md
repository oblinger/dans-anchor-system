---
description: "the work-surface facets (centralized in SKA per D08, but specified here)"
---

# Track Facet
The work-surface facet group — the `{slug} Track/` folder that houses an anchor's backlog, queries, and streams (centralized in SKA per D08, but specified here).

| -[[DAS Track]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Track](hook://p/DAS%20Track) |
| --- | --- |
| [[Workflow Design\|Design]] |  |
| Facets | [[DAS Backlog]],  [[DAS Features\|Features]],  [[DAS Inbox\|Inbox]],  [[DAS Icebox\|Icebox]],  [[DAS Messages\|Messages]],  [[DAS Log\|Log]],  [[DAS Query\|Query]],  [[DAS Status\|Status]],   |
| Related | [[templates/track/{slug} Track.md\|track template]],   |
| Rules | [[R-track-group]],  [[R-track-dispatch]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Interface]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Linkage** — this facet's existence ⟺ the anchor runs the ~~[[workflow]]~~ discipline; the two share one design folder, [[Workflow Design]] (hosted on the behavioral core), reachable from either page per [[SKA Decisions]] D10.

**Cardinality:** one `{slug} Track/` folder per anchor, holding one `{slug} Track.md` dispatch page. The folder is present **iff** the anchor maintains active tracking (R-track-group-03).

**Location:** `{slug} Track/{slug} Track.md` (root-level folder, per F094 — renamed from `{slug} Plan/` to match the [[Track]] trait name).

## The `{slug} Track.md` dispatch page

`{slug} Track.md` is the folder-note + index for the Track folder — one row per tracking-metadata document that exists for the anchor (wiki-link + short description). Only list documents that exist:

| Document | Part |
|----------|------|
| `{slug} Backlog.md` | [[DAS Backlog]] — **required** for the Track trait (the only mandatory child) |
| `{slug} Status.md` | [[DAS Status]] — per-facet design-phase completeness |
| `{slug} Discussion.md` | tracking-level discussion (planning trade-offs only — design discussions live in `{slug} Design/`) |
| `{slug} Icebox.md` | [[DAS Icebox]] — cold-storage / someday-maybe (optional) |
| `{slug} Inbox.md` | [[DAS Inbox]] — raw input to process (optional) |
| `{slug} Messages.md` | [[DAS Messages]] — the agent's background-notification inbox (optional; written by watchers / audit-q) |

The masthead top-left cell is `-[[{slug} Track]]-`; a `---` auto-management separator lets the page auto-list remaining children (see [[DAS Anchor Page]] § Separators). The dispatch-page invariants — location, identity cell, tracking-metadata-only contents, required Backlog row — are checked by [[R-track-dispatch]].

**What does NOT live in Track** — the "what to build" surface lives in `{slug} Design/`, not here:

- `{slug} PRD.md` / `{slug} System Design.md` / `{slug} UX Design.md` (F094) — product / architecture / UX shape belongs in `{slug} Design/`.
- `{slug} Roadmap.md` and `{slug} Features/` **(2026-06-10 restructure)** — sequencing-design and feature docs are design artifacts; they belong in `{slug} Design/` (`{slug} Design/{slug} Features/`).
- `{slug} Triage.md` (F075) — per-anchor status lives in `~/ob/kmr/Q.md`, rendered from `{slug} queries.md`.

Track holds **tracking metadata**: backlog (work queue), status (design-completeness rollup), and the ephemeral surfaces (icebox, inbox, messages). Keep this list synced with [[DAS Design Folder]] — any future relocation between Track and Design must update both.
