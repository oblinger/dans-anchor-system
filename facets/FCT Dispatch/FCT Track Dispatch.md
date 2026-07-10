---
description: track docs dispatch page — work tracking + planning for a Track-trait anchor
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Track Dispatch](hook://p/FCT%20Track%20Dispatch)
# FCT Track Dispatch
Spec for the `{slug} Track.md` dispatch page that lists all work-tracking and planning documents inside a Track-trait anchor's `{slug} Track/` folder.

**Related:** [[FCT Dispatch]],  [[FCT Backlog]],  [[FCT Design Dispatch]],  [[CAB Track]]
**Examples:** [[HBR Track\|fuller example]],  [[HBR Track\|minimal example]]

**Cardinality:** one per anchor (each Track-trait anchor has exactly one `{slug} Track.md` dispatch page).

**Location:** `{slug} Track/{slug} Track.md` (root-level folder, Gen-3)

The `{slug} Track.md` dispatch page inside the root-level `{slug} Track/` folder. Lists all work-tracking and planning documents for the anchor.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — renamed from `{slug} Plan/` to `{slug} Track/` matching the [[Track]] trait name. The `Plan` slot is freed for a future top-level strategic-plan *document* inside the tree.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---

# CAE Track

| -[[HBR Track]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Track Dispatch](hook://p/FCT%20Track%20Dispatch)<br>: tracking metadata + backlog |
| --- | --- |
| [[HBR Backlog\|Backlog]] | workflow-state core (required for Track) |
| [[CAE Status\|Status]] | per-facet design-phase completeness (consumed by `/design` picker) |
| [[CAE Discussion\|Discussion]] | tracking-level discussion (planning trade-offs only — design discussions go in [[CAE Design Discussion]]) |
| [[FEX Icebox\|Icebox]] | cold-storage / someday-maybe (optional) |
| [[FEX Inbox\|Inbox]] | raw input to process (optional) |
| [[CAE ask\|ask]] | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |

*Roadmap + Features moved to [[HBR Design]] 2026-06-10 per the design-includes-features restructure — feature docs are design artifacts, the roadmap is sequencing-design. See [[FCT Design]] for the new home.*

---

# Format Specification

## Location

`{slug} Track.md` lives inside the root-level `{slug} Track/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {slug} Track`. Blank line after.
-[[{slug} Track]]-`, top-right is `><br>: work tracking + planning`.
- **Body rows** — one row per planning document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[FCT Anchor Page]] § Separators.

## Contents

The Track dispatch page lists all children of the Track folder:

| Document | Part |
|----------|------|
| `{slug} Backlog.md` | [[CAB Backlog]] — REQUIRED for Track trait |
| `{slug} Status.md` | [[FCT Status]] — per-facet design-phase completeness |
| `{slug} Discussion.md` | tracking-level discussion |
| `{slug} Icebox.md` | [[FCT Icebox]] (optional) |
| `{slug} Inbox.md` | [[FCT Inbox]] (optional) |
| `{slug} ask.md` | agent-regenerated ask snapshot; also holds anchor-level questions (optional) |
| `{slug} Messages.md` | [[FCT Messages]] — agent's inbox for background-process notifications (optional; written by watchers / audit-q) |

Not all entries are required — only list documents that exist for this anchor.

**Note — what does NOT live in Track** (moved by successive restructures):

- `{slug} PRD.md` (F094) — product-shape decisions belong in `{slug} Design/`.
- `{slug} System Design.md` (F094) — system-design / architecture content belongs in `{slug} Design/` (the `{slug} Architecture` doc).
- `{slug} UX Design.md` (F094) — UX shape belongs in `{slug} Design/`.
- `{slug} Roadmap.md` **(2026-06-10 restructure)** — sequencing-design belongs in `{slug} Design/`.
- `{slug} Features/` **(2026-06-10 restructure)** — feature docs are design artifacts; belong in `{slug} Design/{slug} Features/`.
- `{slug} Triage.md` (F075) — per-anchor triage lives in `~/ob/kmr/Q.md`.

Track holds **tracking metadata**: backlog (work queue), status (design completeness rollup), and ephemeral surfaces (icebox, inbox, ask, messages). The "what to build" surface — including feature docs and roadmap — lives in Design alongside PRD / UX / Architecture / Testing / Decisions.

# RULESET R-track-dispatch
include::
where:: `file: **/{slug} Track.md`
description:: Rules every `{slug} Track.md` dispatch page must satisfy — location, structure, top-left cell identity, and contents restricted to tracking metadata only.

### RULE R-track-dispatch-01 — File lives inside the Track folder (checked)
The file is named `{slug} Track.md` and lives at `{slug} Track/{slug} Track.md` — inside the root-level `{slug} Track/` folder.
**Check pattern:** the file's path matches `{slug} Track/{slug} Track.md`.
**Why:** the Track dispatch page is the entry point for the Track folder; misplacing it breaks the folder's navigation chain.

-[[{slug} Track]]-` (checked)
-[[{slug} Track]]-` (with surrounding dashes); the second cell begins with `>` and includes a `: work tracking + planning` label.
**Check pattern:** the first table row matches `| -\[\[.+ Track\]\]- |`.
**Why:** the top-left cell anchors CAB Anchor Page mechanics (the `-...-` dash pattern wires the dispatch table to the auto-management system); reformatting it breaks structural tooling.

### RULE R-track-dispatch-03 — Contents restricted to tracking metadata (sampled)
Body rows list only tracking-metadata documents: Backlog (required), Status, Discussion, Icebox, Inbox, ask, Messages, Questions. Design artifacts (PRD, UX, Architecture, Features, Roadmap, Testing, Decisions) MUST NOT appear as rows.
**Check pattern:** no row links a file from the `{slug} Design/` subtree or any design-artifact type listed in § What does NOT live in Track.
**Why:** Track holds workflow state and ephemeral surfaces; design artifacts live in `{slug} Design/`. Mixing them collapses the Track/Design split that F094 and the 2026-06-10 restructure established.

### RULE R-track-dispatch-04 — Backlog row is required when Track trait is present (checked)
The dispatch table includes a row linking `{slug} Backlog.md`; this is the only mandatory child of the Track folder.
**Check pattern:** a row linking `[[{slug} Backlog]]` (or its pipe-aliased form) exists.
**Why:** the [[CAB Backlog]] is required for the Track trait; a Track dispatch page without a Backlog row signals the backlog is missing, not optional.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + RULESET R-track-dispatch above.)*

- **Keep the “what does NOT live in Track” note synced with CAB Design** — any future relocation between Track and Design (per F094 + the 2026-06-10 restructure) must update both this spec and `CAB Design`, so the two stay in lockstep.
- **The Reference Example is illustrative, not normative** — refresh it as CAE / SKA / CAB land their migrated Track pages (F094 Phase 1), but the Format Specification section is the authority; don't promote the example into a directive.
- **Spec text uses the bare `{slug}` placeholder; the Reference Example uses live slugs** — don't mix the two notations within one row.
- **Don't pile per-anchor Track guidance here** — anchor-specific tracking conventions live in that anchor's `{slug} Decisions.md` or local rules, not in this facet spec.
