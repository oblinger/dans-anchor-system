---
description: "the work-surface facet group — the {slug} Track/ folder holding an anchor's backlog, queries and streams"
---

| -[[DAS Track]]- | → [[DAS]] → [[FCT]] → [DAS Track](hook://p/DAS%20Track)  |
| --- | --- |
| [[Workflow Design\|Design]]  |  |
| Facets | [[DAS Backlog]],  [[DAS Inbox\|Inbox]],  [[DAS Icebox\|Icebox]],  [[DAS Messages\|Messages]],  [[DAS Log\|Log]],  [[DAS Query\|Query]],  [[DAS Status\|Status]],  [[DAS Agenda\|Agenda]],  [[DAS Rocks\|Rocks]],   |
| Related | [[templates/track/{slug} Track.md\|track template]],   |
| Examples | [[Tink Track\|real instance (SKA anchor)]],   |
| Rules | [[R-track-group]],  [[R-track-dispatch]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Interface]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Track
The work-surface facet group — the `{slug} Track/` folder that houses an anchor's backlog, queries, and streams; § Who owns a Track folder says which anchors get one.

**Linkage** — this facet's existence ⟺ the anchor runs the ~~[[workflow]]~~ discipline; the two share one design folder, [[Workflow Design]] (hosted on the behavioral core), reachable from either page. The one-folder-per-design-unit rule that puts it there is [[DAS Design Folder]] § What the folder's existence claims.

**Cardinality:** one `{slug} Track/` folder per anchor, holding one `{slug} Track.md` dispatch page. The folder is present **iff** the anchor maintains active tracking (R-track-group-03).

**Location:** `{slug} Track/{slug} Track.md` (root-level folder, per F094 — renamed from `{slug} Plan/` to match the [[Track]] trait name).

## Who owns a Track folder — the agent holds the queue, the subject holds the knowledge

**Not every anchor tracks its own work, and the skill ecosystem tracks none of it.** A skill, facet, discipline, or example anchor carries **no Track folder and no `track` row** ([[R-anchor-page]]-15, checked) — each is far too small to earn a backlog, and dozens of near-empty per-anchor queues would bury the handful of real ones. Their work is queued on one shared surface, with the anchor named in the item.

The split that decides *which* surface is **the agent holds the queue, the subject holds the knowledge**:

| Lives with the **agent** (`Tink Track/`) | Lives with the **subject** (`SKA Design/`) |
|---|---|
| [[Tink Backlog]] — the work queue | [[SKA Decisions]] — load-bearing decisions |
| [[Tink queries]] — open questions for the user | `SKA Design/SKA Features/` — one doc per feature |
| [[Tink Messages]], [[Tink Icebox]] | the design docs the features distill into |

Work is *transient and owned by whoever is doing it*, so it belongs to the agent working the ecosystem. Design is *durable and about the thing itself*, so it belongs to the thing. That is why feature docs sit under `SKA Design/`, not beside the backlog: a feature doc is a design artifact with a Summary, Success Criteria, and Open Questions, and it outlives the row that scheduled it.

**Exception by kind, not by location.** A standalone project anchor with its own repo — MUX, HA — does track its own work. The no-tracking rule is specifically the skill ecosystem, which is why [[FEX Project Root]] keeps a `Track` row while [[HBR]], a skill-ecosystem anchor, drops it.

*(Historical note: this arrangement was decided as D07/D08/D10 in the SKA decision log when tracking sat on an `SKA Track/` folder. That folder no longer exists — the queue moved to the Tink agent — so the decisions were corrected against the live layout and **inlined above rather than cited**, and all three are retired at their source. The decision log and the feature that inlined them live in the SYS vault, outside this repo, so they are named here rather than linked: a link that resolves only on the author's machine is worse than a name.)*

## The `{slug} Track.md` dispatch page

`{slug} Track.md` is the folder-note + index for the Track folder — one row per tracking-metadata document that exists for the anchor (wiki-link + short description). Only list documents that exist:

| Document | Part |
|----------|------|
| `{slug} Backlog.md` | [[DAS Backlog]] — **required** for the Track trait (the only mandatory child) |
| `{slug} Status.md` | [[DAS Status]] — per-facet design-phase completeness |
| `{slug} Agenda.md` | [[DAS Agenda]] — strategic frame / theory-of-victory for the activity (optional, elective) |
| `{slug} Rocks/` | [[DAS Rocks]] — the anchor's big chunks of work, ranked; one short-named file per rock (optional, elective) |
| `{slug} Discussion.md` | tracking-level discussion (planning trade-offs only — design discussions live in `{slug} Design/`) |
| `{slug} Icebox.md` | [[DAS Icebox]] — cold-storage / someday-maybe (optional) |
| `{slug} Inbox.md` | [[DAS Inbox]] — raw input to process (optional) |
| `{slug} Messages.md` | [[DAS Messages]] — the agent's background-notification inbox (optional; written by watchers / audit-q) |
| `{slug} Exceptions.md` | [[R-exception-discipline]] — numbered, graded, target-scoped deviations from checked rules (optional; present iff the anchor has accepted any). The audit engine reads it, so a row here is the only thing that suppresses a finding. |

The masthead top-left cell is `-[[{slug} Track]]-`; a `---` auto-management separator lets the page auto-list remaining children (see [[DAS Anchor Page]] § Separators). The dispatch-page invariants — location, identity cell, tracking-metadata-only contents, required Backlog row — are checked by [[R-track-dispatch]].

**What does NOT live in Track** — the "what to build" surface lives in `{slug} Design/`, not here:

- `{slug} PRD.md` / `{slug} System Design.md` / `{slug} UX Design.md` (F094) — product / architecture / UX shape belongs in `{slug} Design/`.
- `{slug} Roadmap.md` and `{slug} Features/` **(2026-06-10 restructure)** — sequencing-design and feature docs are design artifacts; they belong in `{slug} Design/` (`{slug} Design/{slug} Features/`).
- `{slug} Triage.md` (F075) — per-anchor status lives in `~/ob/kmr/Q.md`, rendered from `{slug} queries.md`.

Track holds **tracking metadata**: backlog (work queue), status (design-completeness rollup), agenda (the activity's strategic frame), and the ephemeral surfaces (icebox, inbox, messages). Keep this list synced with [[DAS Design Folder]] — any future relocation between Track and Design must update both.

# BRIEF

*(Maintainer note — cautions for whoever edits this group-facet spec. It defines the `{slug} Track/` folder + its `{slug} Track.md` dispatch page; the member facets are specified in their own `DAS <Facet>.md` pages, and the dispatch-page invariants live in the embedded [[R-track-dispatch]] / [[R-track-group]] rulesets.)*

- **This is the group-index facet, not a member spec** — per-facet format rules live in [[DAS Backlog]] / [[DAS Status]] / [[DAS Agenda]] / [[DAS Icebox]] / [[DAS Inbox]] / [[DAS Messages]] / [[DAS Log]] / [[DAS Query]]; this page owns only the folder shape, the dispatch-page contents, and the Track-vs-Design boundary.
- **[[DAS Agenda|Agenda]] is the one Track member that is user-authored strategy** (added 2026-07-27, T053) — it sits in Track because it is metadata *about the activity*, not design content about the artifact. The Agenda ⟺ Roadmap line (theory vs milestones) is the drift to watch; it is owned by [[DAS Agenda]], not restated here.
- **The Track ⟺ Design boundary is load-bearing** — the § "What does NOT live in Track" list (PRD / System Design / UX / Roadmap / Features → Design) reflects the 2026-06-10 restructure (F094 + Roadmap/Features move); any relocation must update this list AND [[DAS Design Folder]] in the same pass.
- **`{slug} Backlog.md` is the only mandatory child** — the folder exists *iff* the anchor maintains active tracking (R-track-group-03); do not soften to "every anchor has a Track folder."
- **Rulesets were extracted** (2026-07-12 tracking-group pass) — [[R-track-group]] (folder/membership) and [[R-track-dispatch]] (the `{slug} Track.md` page shape) live as sibling rulesets; keep the spec body and both in sync.
