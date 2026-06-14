---
description: "design docs dispatch page — Architecture, UX Design, Interface, Data Model, Principles, PRD"
---
# FCT Design Dispatch
Facet spec for `{NAME} Design.md` — the dispatch page listing all high-level system-spec documents for an anchor.

| -[[FCT Design Dispatch]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Design Dispatch](hook://p/FCT%20Design%20Dispatch)<br>: design docs dispatch page — Architecture, UX Design, Interface, Data Model, Principles, PRD |
| --- | --- |
| Related | [[FCT Architecture]],  [[FCT UX Design]],  [[FCT Interface]],  [[FCT PRD]],   |
| Examples | [[HBR Design\|minimal]],  [[CAE Design\|fuller]],   |

**TLDR** — `{NAME} Design.md` is the one-per-anchor dispatch page listing every high-level system-spec document (Architecture, UX Design, Interface, Data Model, Principles, PRD, Design Discussion) for an anchor. It lives at `{NAME} Docs/{NAME} Design/{NAME} Design.md`. Architecture and UX Design are siblings here, not parent/child (F094). Interface is required for Code anchors.

**Location:** `{NAME} Docs/{NAME} Design/{NAME} Design.md`

The `{NAME} Design.md` dispatch page inside the `{NAME} Design/` folder. Lists all **high-level system-spec documents** for the anchor.

Per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01) — Design is the **umbrella** that holds Architecture (system-architecture story), UX Design (user-interaction shape), Interface (public-API / layer contract), Data Model, Principles, and design-trade-off discussion. **Architecture and UX Design are siblings here, not parent/child** (Q1=B). Interface relocates here from `{NAME} User/` per Q3=A — its content describes a system contract, not an end-user task.

**Cardinality:** one per anchor — each anchor has exactly one `{NAME} Design.md` dispatch page inside its `{NAME} Design/` folder.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---


# CAE Design

| -[[CAE Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Design Dispatch](hook://p/FCT%20Design%20Dispatch)<br>: design — system spec, UX, interface, data, principles |
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
-[[{NAME} Design]]-`, top-right is `><br>: design — system spec, UX, interface, data, principles`.
- **Body rows** — one row per design document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[FCT Anchor Page]] § Separators.

## Contents

The Design dispatch page lists all children of the Design folder:

| Document | Part | Notes |
|----------|------|-------|
| `{NAME} Architecture/` | [[FCT Architecture]] | Anchor-folder form (per F074). System-architecture story. |
| `{NAME} UX Design.md` (or `{NAME} UX Design/` if it grows) | [[FCT UX Design]] | User-interaction shape; sibling to Architecture per F094 Q1=B. |
| `{NAME} Interface.md` | [[FCT Interface]] | Top-level layer contract — REQUIRED for Code anchors. Relocated from `{NAME} User/` per F094 Q3=A. |
| `{NAME} Data Model.md` | (when applicable) | Data shapes, schemas, type contracts. |
| `{NAME} Principles.md` | (when applicable) | Load-bearing rules / invariants. |
| `{NAME} PRD.md` | [[FCT PRD]] | Product requirements (when applicable). |
| `{NAME} Design Discussion.md` | design-level discussion | Trade-off conversations whose outcomes land in PRD / Architecture / Interface. |

Not all entries are required — only list documents that exist for this anchor.

**Note — separation of concerns** (per F094 Q1+Q3):

- **Architecture** describes the *system* (modules, interfaces, data flow) — internal structure.
- **UX Design** describes the *user-interaction* (screens, commands, output) — external shape.
- **Interface** describes the *contract callers consume* (types, operations, invariants) — public API.

All three live here because they're all aspects of how the system is *designed*. They're peers; none subordinates the others. The folder name is **Design** (not **Architecture**) so "Architecture" stays precise as the system-architecture facet — instead of being overloaded to mean both "the umbrella" and "one of its facets."

## Audience

System designers, architects, integrators-above-the-layer, and anyone evaluating the design. Distinct from:

- [[FCT Track Dispatch|Track]] — **planning-agent** surface (Backlog, Features, Roadmap)
- [[FCT User Dispatch|User]] — **end-user / consumer** surface (Guide, CLI, FAQ)
- [[FCT Dev Dispatch|Dev]] — **implementer** surface (Files.md, per-module reference)

# RULESET R-design-dispatch
include::
where:: file: **/{{NAME}} Design.md
description:: Rules every `{NAME} Design.md` dispatch page must satisfy — location, H1 form, dispatch-table structure, and required-document coverage for Code anchors.

### RULE R-design-dispatch-01 — File lives inside `{NAME} Design/` (checked)
The dispatch page `{NAME} Design.md` must reside at `{NAME} Docs/{NAME} Design/{NAME} Design.md` — not at the anchor root or under a different subfolder.
**Check pattern:** the file's parent directory name matches `{NAME} Design`.
**Why:** the location is the facet's contract; a misplaced dispatch page is invisible to anchor-page resolution and breaks folder-relative linking. (sampled)

### RULE R-design-dispatch-02 — H1 is `# {NAME} Design` (checked)
The file's H1 reads exactly `# {NAME} Design` where `{NAME}` is the anchor's root ID.
**Check pattern:** H1 matches `^# \S+ Design$`.
**Why:** the H1 is used as the anchor-page title in dispatch tables; a wrong H1 surfaces the wrong name everywhere it appears. (checked)

-[[{NAME} Design]]-` form (checked)
-[[{NAME} Design]]-` in column 1 and the `><br>: design — …` description in column 2.
**Check pattern:** first table row starts with `| -[[` and ends with a `><br>:` description.
**Why:** the strikethrough self-link form is the FCT Anchor Page standard for dispatch tables; deviating breaks the consistent navigation pattern across all anchors. (sampled)

### RULE R-design-dispatch-04 — Interface entry present for Code anchors (sampled)
Anchors that carry the Code trait MUST include a `{NAME} Interface.md` row in the dispatch table (per F094 Q3=A — Interface is a system contract, not an end-user doc).
**Check pattern:** for anchors with `traits: [code]` or equivalent, the dispatch table contains a row linking `{NAME} Interface`.
**Why:** Interface is required for Code anchors; omitting it leaves callers without the public-API contract the Design folder exists to surface. (sampled)

# BRIEF

- **This file is the facet spec for `{NAME} Design.md`** — it defines the shape, location, and contents of the Design dispatch page that every anchor's `{NAME} Design/` folder carries. Edits here cascade to every anchor that conforms to the facet.
- **Not for per-anchor instances** — concrete `CAE Design.md`, `SKA Design.md`, etc. live in their own anchors. Do not pile anchor-specific content here; only the Reference Example block is allowed as an inline illustration.
- **Inclusion test for the dispatch table** — a document belongs in the Design dispatch table iff it lives inside `{NAME} Design/` AND describes the system's *design* (architecture / UX shape / interface contract / data model / principles / PRD / design-trade-off discussion). Implementation details, end-user guides, and planning artifacts route to Dev / User / Track dispatches respectively per the § Audience section.
- **Architecture and UX Design are siblings, not parent/child** (per F094 Q1=B) — preserve this invariant when editing the Contents table; do not nest UX under Architecture or vice versa. Interface lives here too per F094 Q3=A (system contract, not end-user task).
-[[...]]-` strikethrough form; the top-right uses the `><br>:` description prefix per [[FCT Anchor Page]].
- **Load-bearing — folder name is "Design", not "Architecture"** — this disambiguates the umbrella from the system-architecture facet. Renaming the folder would collide "Architecture" against itself; do not rename without coordinating an F094-scale migration.
- **Cited by** [[CAB Base]], [[FCT Anchor Page]], the Architecture / UX Design / Interface / PRD facets, and the `/design` and `/architect` skills. Changes to facet shape ripple through those; check cross-references before structural edits.
