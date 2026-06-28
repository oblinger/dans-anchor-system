---
description: "design docs dispatch page — Architecture, UX Design, Interface, Data Model, Principles, PRD"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Design Dispatch](hook://p/FCT%20Design%20Dispatch)

# FCT Design Dispatch
Facet spec for `{NAME} Design.md` — the dispatch page listing all high-level system-spec documents for an anchor.

**Related:** [[FCT Architecture]],  [[FCT UX Design]],  [[FCT Interface]],  [[FCT PRD]]
**Examples:** [[HBR Design\|minimal]],  [[CAE Design\|fuller]]

**TLDR** — `{NAME} Design.md` is the one-per-anchor dispatch page listing the high-level system-spec documents (UX Design, Interface, Decisions, Data Model, Principles, PRD, Features, Roadmap, Design Discussion) for an anchor. It lives at the root-level `{NAME} Design/{NAME} Design.md`. The system-architecture story **is** a Design child — `{NAME} Architecture` (a single `.md`, or a `{NAME} Architecture/` folder-doc once it grows subsystems) inside `{NAME} Design/`. (F094's root placement reversed 2026-06-27.) Interface is required for Code anchors.

**Location:** `{NAME} Design/{NAME} Design.md` (root-level folder, Gen-3)

The `{NAME} Design.md` dispatch page inside the root-level `{NAME} Design/` folder. Lists the **high-level system-spec documents** for the anchor.

Design holds UX Design (user-interaction shape), Interface (public-API / layer contract), Decisions, Data Model, Principles, PRD, Features, Roadmap, and design-trade-off discussion. The **system-architecture story is a Design child** (`{NAME} Design/{NAME} Architecture`, per [[FCT Architecture]]) — listed on the Design dispatch like the other design docs. Interface lives here (not in `{NAME} User Docs/`) because its content describes a system contract, not an end-user task.

**Cardinality:** one per anchor — each anchor has exactly one `{NAME} Design.md` dispatch page inside its `{NAME} Design/` folder.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---

# CAE Design

| -[[CAE Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Design Dispatch](hook://p/FCT%20Design%20Dispatch)<br>: design — system spec, UX, interface, data, principles |
| --- | --- |
| [[CAE Architecture\|Architecture]] | system-architecture story — a Design child (`{NAME} Architecture`) |
| [[CAE UX Design\|UX Design]] | user-interaction shape — screens, commands, output formats |
| [[CAE Interface\|Interface]] | top-level layer contract — public API for callers (required for Code anchors) |
| [[CAE Data Model\|Data Model]] | data shapes & schemas |
| [[CAE Decisions\|Principles]] | load-bearing rules & invariants |
| [[CAE PRD\|PRD]] | product requirements |
| [[CAE Design Discussion\|Design Discussion]] | design trade-off conversations |

---

# Format Specification

## Location

`{NAME} Design.md` lives inside the root-level `{NAME} Design/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {NAME} Design`. Blank line after.
-[[{NAME} Design]]-`, top-right is `><br>: design — system spec, UX, interface, data, principles`.
- **Body rows** — one row per design document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[FCT Anchor Page]] § Separators.

## Contents

The Design dispatch page lists the children of the Design folder (plus a cross-link to the root-level Architecture folder):

| Document | Part | Notes |
|----------|------|-------|
| `{NAME} Architecture` (`.md` → `{NAME} Architecture/` folder-doc on growth) | [[FCT Architecture]] | **A Design child** — the system-architecture story; governed by [[FCT Architecture]]. (F094's root placement reversed 2026-06-27.) |
| `{NAME} UX Design.md` (or `{NAME} UX Design/` if it grows) | [[FCT UX Design]] | User-interaction shape. |
| `{NAME} Interface.md` | [[FCT Interface]] | Top-level layer contract — REQUIRED for Code anchors. Lives in Design (not `{NAME} User Docs/`). |
| `{NAME} Decisions.md` | [[FCT Decisions]] | Load-bearing rulings / invariants. |
| `{NAME} Data Model.md` | (when applicable) | Data shapes, schemas, type contracts. |
| `{NAME} Principles.md` | (when applicable) | Load-bearing rules / invariants. |
| `{NAME} PRD.md` | [[FCT PRD]] | Product requirements (when applicable). |
| `{NAME} Features/` | [[FCT Features]] | Dated feature specs (feature docs are design artifacts). |
| `{NAME} Roadmap.md` | [[FCT Roadmap]] | Implementation milestones (sequencing-design). |
| `{NAME} Design Discussion.md` | design-level discussion | Trade-off conversations whose outcomes land in PRD / Architecture / Interface. |

Not all entries are required — only list documents that exist for this anchor.

**Note — separation of concerns:**

- **Architecture** describes the *system* (modules, interfaces, data flow) — internal structure. Its own **root-level folder** in Gen-3.
- **UX Design** describes the *user-interaction* (screens, commands, output) — external shape. A Design child.
- **Interface** describes the *contract callers consume* (types, operations, invariants) — public API. A Design child.

The folder is named **Design** (not **Architecture**) so "Architecture" stays precise as the system-architecture facet — a peer root-level folder, never the umbrella over Design.

## Audience

System designers, architects, integrators-above-the-layer, and anyone evaluating the design. Distinct from:

- [[FCT Track Dispatch|Track]] — **planning-agent** surface (Backlog, Status, ephemeral surfaces)
- [[FCT User Dispatch|User Docs]] — **end-user / consumer** surface (Guide, CLI, FAQ)
- [[FCT Dev Dispatch|Dev Docs]] — **implementer** surface (Files.md, per-module reference)

# RULESET R-design-dispatch
include::
where:: file: **/{{NAME}} Design.md
description:: Rules every `{NAME} Design.md` dispatch page must satisfy — location, H1 form, dispatch-table structure, and required-document coverage for Code anchors.

### RULE R-design-dispatch-01 — File lives inside `{NAME} Design/` (checked)
The dispatch page `{NAME} Design.md` must reside at `{NAME} Design/{NAME} Design.md` — inside the root-level `{NAME} Design/` folder.
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
- **Inclusion test for the dispatch table** — a document belongs in the Design dispatch table iff it lives inside `{NAME} Design/` AND describes the system's *design* (UX shape / interface contract / decisions / data model / principles / PRD / features / roadmap / design-trade-off discussion). Implementation details, end-user guides, and planning metadata route to Dev Docs / User Docs / Track dispatches respectively per the § Audience section.
- **Architecture IS a Design child** — the system-architecture story is `{NAME} Design/{NAME} Architecture` (governed by [[FCT Architecture]]), listed on the Design dispatch like the other design docs. (F094's root placement reversed 2026-06-27.) Interface lives in Design (system contract, not end-user task); UX Design lives in Design too.
-[[...]]-` strikethrough form; the top-right uses the `><br>:` description prefix per [[FCT Anchor Page]].
- **Load-bearing — folder name is "Design", not "Architecture"** — Design and Architecture are peer root-level folders; keeping the names distinct stops "Architecture" being overloaded. Renaming would collide the two; do not rename without coordinating a vault-wide migration.
- **Cited by** [[CAB Base]], [[FCT Anchor Page]], the Architecture / UX Design / Interface / PRD facets, and the `/design` and `/architect` skills. Changes to facet shape ripple through those; check cross-references before structural edits.
