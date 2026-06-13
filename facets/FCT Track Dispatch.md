---
description: track docs dispatch page — work tracking + planning for a Track-trait anchor
---
# CAB Track Dispatch

Spec for the `{NAME} Track.md` dispatch page that lists all work-tracking and planning documents inside a Track-trait anchor's `{NAME} Track/` folder.

**Location:** `{NAME} Docs/{NAME} Track/{NAME} Track.md`

The `{NAME} Track.md` dispatch page inside the `{NAME} Track/` folder. Lists all work-tracking and planning documents for the anchor.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — renamed from `{NAME} Plan/` to `{NAME} Track/` matching the [[Track]] trait name. The `Plan` slot is freed for a future top-level strategic-plan *document* inside the tree.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---


# CAE Track

| -[[CAE Track]]- | ><br>: tracking metadata + backlog |
| --- | --- |
| [[CAE Backlog\|Backlog]] | workflow-state core (required for Track) |
| [[CAE Status\|Status]] | per-facet design-phase completeness (consumed by `/design` picker) |
| [[CAE Discussion\|Discussion]] | tracking-level discussion (planning trade-offs only — design discussions go in [[CAE Design Discussion]]) |
| [[CAE Icebox\|Icebox]] | cold-storage / someday-maybe (optional) |
| [[CAE Inbox\|Inbox]] | raw input to process (optional) |
| [[CAE ask\|ask]] | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |

*Roadmap + Features moved to [[CAE Design]] 2026-06-10 per the design-includes-features restructure — feature docs are design artifacts, the roadmap is sequencing-design. See [[FCT Design]] for the new home.*

---



# Format Specification

## Location

`{NAME} Track.md` lives inside `{NAME} Docs/{NAME} Track/`.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {NAME} Track`. Blank line after.
- **Dispatch table** — top-left cell is `-[[{NAME} Track]]-`, top-right is `><br>: work tracking + planning`.
- **Body rows** — one row per planning document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[FCT Anchor Page]] § Separators.

## Contents

The Track dispatch page lists all children of the Track folder:

| Document | Part |
|----------|------|
| `{NAME} Backlog.md` | [[CAB Backlog]] — REQUIRED for Track trait |
| `{NAME} Status.md` | [[FCT Status]] — per-facet design-phase completeness |
| `{NAME} Discussion.md` | tracking-level discussion |
| `{NAME} Icebox.md` | [[FCT Icebox]] (optional) |
| `{NAME} Inbox.md` | [[FCT Inbox]] (optional) |
| `{NAME} ask.md` | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |
| `{NAME} Messages.md` | [[FCT Messages]] — agent's inbox for background-process notifications (optional; written by watchers / audit-q) |

Not all entries are required — only list documents that exist for this anchor.

**Note — what does NOT live in Track** (moved by successive restructures):

- `{NAME} PRD.md` (F094) — product-shape decisions belong in `{NAME} Design/`.
- `{NAME} System Design.md` (F094) — system-design content belongs in `{NAME} Design/{NAME} Architecture/`.
- `{NAME} UX Design.md` (F094) — UX shape belongs in `{NAME} Design/`.
- `{NAME} Roadmap.md` **(2026-06-10 restructure)** — sequencing-design belongs in `{NAME} Design/`.
- `{NAME} Features/` **(2026-06-10 restructure)** — feature docs are design artifacts; belong in `{NAME} Design/{NAME} Features/`.
- `{NAME} Triage.md` (F075) — per-anchor triage lives in `~/ob/kmr/Q.md`.

Track holds **tracking metadata**: backlog (work queue), status (design completeness rollup), and ephemeral surfaces (icebox, inbox, ask, messages). The "what to build" surface — including feature docs and roadmap — lives in Design alongside PRD / UX / Architecture / Testing / Decisions.

# BRIEF

- **This is the spec for the Track-folder dispatch page**, not a Track dispatch instance — describes the required H1, dispatch-table shape, body rows, and auto-management separator for `{NAME} Track.md` in any Track-trait anchor.
- **Inclusion test for the Contents table**: a file belongs in the Track folder only if it is *tracking metadata* — workflow state (Backlog, Status), ephemeral surfaces (Inbox, Icebox, ask, Messages, Questions), or planning discussion. Design artifacts (PRD, UX, Architecture, Features, Roadmap, Testing, Decisions) go to `{NAME} Design/` and MUST NOT be re-listed here.
- **Keep the "what does NOT live in Track" note synchronized** with the F094 + 2026-06-10 restructure boundaries — any future relocation between Track and Design must update both this note and `CAB Design` so the two specs stay in lockstep.
- **The Reference Example block is illustrative, not normative** — when CAE / SKA / CAB ship their migrated Track pages per F094 Phase 1, refresh this example but do not turn it into a directive (the Format Specification section is the authority).
- **Wiki-links use the bare anchor `{NAME}` placeholder** in spec text and the live RID in the Reference Example. Don't mix the two within one row.
- **Don't pile per-anchor Track guidance here** — anchor-specific tracking conventions live in that anchor's `{NAME} Decisions.md` or local rules, not in this facet spec.
- **Load-bearing constraint**: the top-left cell `-[[{NAME} Track]]-` and the `---` auto-management separator row are what wire the dispatch table to CAB Anchor Page mechanics — do not reformat or remove either when editing example rows.
