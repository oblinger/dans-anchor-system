---
description: track docs dispatch page — work tracking + planning for a Track-trait anchor
---

# DAS Track Dispatch
Spec for the `{slug} Track.md` dispatch page that lists all work-tracking and planning documents inside a Track-trait anchor's `{slug} Track/` folder.

| -[[DAS Track Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Track Dispatch](hook://p/DAS%20Track%20Dispatch) |
| --- | --- |
| Related | [[DAS Dispatch]],  [[DAS Backlog]],  [[DAS Design Dispatch]],  [[DAS Track]],   |
| Examples | [[HBR Track\|fuller example]],  [[HBR Track\|minimal example]],   |
| Rules | [[R-track-dispatch]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Cardinality:** one per anchor (each Track-trait anchor has exactly one `{slug} Track.md` dispatch page).

**Location:** `{slug} Track/{slug} Track.md` (root-level folder, Gen-3)

The `{slug} Track.md` dispatch page inside the root-level `{slug} Track/` folder. Lists all work-tracking and planning documents for the anchor.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — renamed from `{slug} Plan/` to `{slug} Track/` matching the [[Track]] trait name. The `Plan` slot is freed for a future top-level strategic-plan *document* inside the tree.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---

# CAE Track

| -[[HBR Track]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Dispatch]] → [DAS Track Dispatch](hook://p/DAS%20Track%20Dispatch)<br>: tracking metadata + backlog |
| --- | --- |
| [[HBR Backlog\|Backlog]] | workflow-state core (required for Track) |
| [[CAE Status\|Status]] | per-facet design-phase completeness (consumed by `/design` picker) |
| [[CAE Discussion\|Discussion]] | tracking-level discussion (planning trade-offs only — design discussions go in [[CAE Design Discussion]]) |
| [[FEX Icebox\|Icebox]] | cold-storage / someday-maybe (optional) |
| [[FEX Inbox\|Inbox]] | raw input to process (optional) |
| [[CAE ask\|ask]] | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |

*Roadmap + Features moved to [[HBR Design]] 2026-06-10 per the design-includes-features restructure — feature docs are design artifacts, the roadmap is sequencing-design. See [[DAS Design Folder]] for the new home.*

---

# Format Specification

## Location

`{slug} Track.md` lives inside the root-level `{slug} Track/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {slug} Track`. Blank line after.
-[[{slug} Track]]-`, top-right is `><br>: work tracking + planning`.
- **Body rows** — one row per planning document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[DAS Anchor Page]] § Separators.

## Contents

The Track dispatch page lists all children of the Track folder:

| Document | Part |
|----------|------|
| `{slug} Backlog.md` | [[DAS Backlog]] — REQUIRED for Track trait |
| `{slug} Status.md` | [[DAS Status]] — per-facet design-phase completeness |
| `{slug} Discussion.md` | tracking-level discussion |
| `{slug} Icebox.md` | [[DAS Icebox]] (optional) |
| `{slug} Inbox.md` | [[DAS Inbox]] (optional) |
| `{slug} ask.md` | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |
| `{slug} Messages.md` | [[DAS Messages]] — agent's inbox for background-process notifications (optional; written by watchers / audit-q) |

Not all entries are required — only list documents that exist for this anchor.

**Note — what does NOT live in Track** (moved by successive restructures):

- `{slug} PRD.md` (F094) — product-shape decisions belong in `{slug} Design/`.
- `{slug} System Design.md` (F094) — system-design / architecture content belongs in `{slug} Design/` (the `{slug} Architecture` doc).
- `{slug} UX Design.md` (F094) — UX shape belongs in `{slug} Design/`.
- `{slug} Roadmap.md` **(2026-06-10 restructure)** — sequencing-design belongs in `{slug} Design/`.
- `{slug} Features/` **(2026-06-10 restructure)** — feature docs are design artifacts; belong in `{slug} Design/{slug} Features/`.
- `{slug} Triage.md` (F075) — per-anchor status lives in `~/ob/kmr/Q.md`, rendered from `{slug} queries.md`.

Track holds **tracking metadata**: backlog (work queue), status (design completeness rollup), and ephemeral surfaces (icebox, inbox, ask, messages). The "what to build" surface — including feature docs and roadmap — lives in Design alongside PRD / UX / Architecture / Testing / Decisions.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + RULESET R-track-dispatch above.)*

- **Keep the “what does NOT live in Track” note synced with CAB Design** — any future relocation between Track and Design (per F094 + the 2026-06-10 restructure) must update both this spec and `CAB Design`, so the two stay in lockstep.
- **The Reference Example is illustrative, not normative** — refresh it as CAE / SKA / CAB land their migrated Track pages (F094 Phase 1), but the Format Specification section is the authority; don't promote the example into a directive.
- **Spec text uses the bare `{slug}` placeholder; the Reference Example uses live slugs** — don't mix the two notations within one row.
- **Don't pile per-anchor Track guidance here** — anchor-specific tracking conventions live in that anchor's `{slug} Decisions.md` or local rules, not in this facet spec.
