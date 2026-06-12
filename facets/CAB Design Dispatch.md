---
description: design docs dispatch page — high-level system spec (Architecture, UX Design, Interface, Data Model, Principles) for the anchor
---
# CAB Design Dispatch

Facet spec for `{NAME} Design.md` — the dispatch page that lists all high-level system-spec documents (Architecture, UX Design, Interface, Data Model, Principles, PRD) for an anchor.

**Location:** `{NAME} Docs/{NAME} Design/{NAME} Design.md`

The `{NAME} Design.md` dispatch page inside the `{NAME} Design/` folder. Lists all **high-level system-spec documents** for the anchor.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — Design is the **umbrella** that holds Architecture (system-architecture story), UX Design (user-interaction shape), Interface (public-API / layer contract), Data Model, Principles, and design-trade-off discussion. **Architecture and UX Design are siblings here, not parent/child** (Q1=B). Interface relocates here from `{NAME} User/` per Q3=A — its content describes a system contract, not an end-user task.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---


# CAE Design

| -[[CAE Design]]- | ><br>: design — system spec, UX, interface, data, principles |
| --- | --- |
| [[CAE Architecture\|Architecture]] | system-architecture story — components, modules, data flow (folder per F074) |
| [[CAE UX Design\|UX Design]] | user-interaction shape — screens, commands, output formats |
| [[CAE Interface\|Interface]] | top-level layer contract — public API for callers (required for Code anchors) |
| [[CAE Data Model\|Data Model]] | data shapes & schemas |
| [[CAE Decisions\|Principles]] | load-bearing rules & invariants |
| [[CAE PRD\|PRD]] | product requirements |
| [[CAE Design Discussion\|Design Discussion]] | design trade-off conversations |

---



# Format Specification

## Location

`{NAME} Design.md` lives inside `{NAME} Docs/{NAME} Design/`.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {NAME} Design`. Blank line after.
- **Dispatch table** — top-left cell is `-[[{NAME} Design]]-`, top-right is `><br>: design — system spec, UX, interface, data, principles`.
- **Body rows** — one row per design document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[CAB Anchor Page]] § Separators.

## Contents

The Design dispatch page lists all children of the Design folder:

| Document | Part | Notes |
|----------|------|-------|
| `{NAME} Architecture/` | [[CAB Architecture]] | Anchor-folder form (per F074). System-architecture story. |
| `{NAME} UX Design.md` (or `{NAME} UX Design/` if it grows) | [[CAB UX Design]] | User-interaction shape; sibling to Architecture per F094 Q1=B. |
| `{NAME} Interface.md` | [[CAB Interface]] | Top-level layer contract — REQUIRED for Code anchors. Relocated from `{NAME} User/` per F094 Q3=A. |
| `{NAME} Data Model.md` | (when applicable) | Data shapes, schemas, type contracts. |
| `{NAME} Principles.md` | (when applicable) | Load-bearing rules / invariants. |
| `{NAME} PRD.md` | [[CAB PRD]] | Product requirements (when applicable). |
| `{NAME} Design Discussion.md` | design-level discussion | Trade-off conversations whose outcomes land in PRD / Architecture / Interface. |

Not all entries are required — only list documents that exist for this anchor.

**Note — separation of concerns** (per F094 Q1+Q3):

- **Architecture** describes the *system* (modules, interfaces, data flow) — internal structure.
- **UX Design** describes the *user-interaction* (screens, commands, output) — external shape.
- **Interface** describes the *contract callers consume* (types, operations, invariants) — public API.

All three live here because they're all aspects of how the system is *designed*. They're peers; none subordinates the others. The folder name is **Design** (not **Architecture**) so "Architecture" stays precise as the system-architecture facet — instead of being overloaded to mean both "the umbrella" and "one of its facets."

## Audience

System designers, architects, integrators-above-the-layer, and anyone evaluating the design. Distinct from:

- [[CAB Track Dispatch|Track]] — **planning-agent** surface (Backlog, Features, Roadmap)
- [[CAB User Dispatch|User]] — **end-user / consumer** surface (Guide, CLI, FAQ)
- [[CAB Dev Dispatch|Dev]] — **implementer** surface (Files.md, per-module reference)

# BRIEF

- **This file is the facet spec for `{NAME} Design.md`** — it defines the shape, location, and contents of the Design dispatch page that every anchor's `{NAME} Design/` folder carries. Edits here cascade to every anchor that conforms to the facet.
- **Not for per-anchor instances** — concrete `CAE Design.md`, `SKA Design.md`, etc. live in their own anchors. Do not pile anchor-specific content here; only the Reference Example block is allowed as an inline illustration.
- **Inclusion test for the dispatch table** — a document belongs in the Design dispatch table iff it lives inside `{NAME} Design/` AND describes the system's *design* (architecture / UX shape / interface contract / data model / principles / PRD / design-trade-off discussion). Implementation details, end-user guides, and planning artifacts route to Dev / User / Track dispatches respectively per the § Audience section.
- **Architecture and UX Design are siblings, not parent/child** (per F094 Q1=B) — preserve this invariant when editing the Contents table; do not nest UX under Architecture or vice versa. Interface lives here too per F094 Q3=A (system contract, not end-user task).
- **Linking convention** — wiki-links in the dispatch table use `[[{NAME} <Doc>\|<Doc>]]` aliasing, matching the Reference Example. The top-left cell uses the `-[[...]]-` strikethrough form; the top-right uses the `><br>:` description prefix per [[CAB Anchor Page]].
- **Load-bearing — folder name is "Design", not "Architecture"** — this disambiguates the umbrella from the system-architecture facet. Renaming the folder would collide "Architecture" against itself; do not rename without coordinating an F094-scale migration.
- **Cited by** [[CAB Base]], [[CAB Anchor Page]], the Architecture / UX Design / Interface / PRD facets, and the `/design` and `/architect` skills. Changes to facet shape ripple through those; check cross-references before structural edits.
