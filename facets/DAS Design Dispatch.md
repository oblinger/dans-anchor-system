---
description: "design docs dispatch page — Architecture, UX Design, Interface, Data Model, Principles, PRD"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Dispatch]] → [FCT Design Dispatch](hook://p/DAS%20Design%20Dispatch)
# FCT Design Dispatch
Facet spec for `{slug} Design.md` — the dispatch page listing all high-level system-spec documents for an anchor.

**Related:** [[DAS Architecture]],  [[DAS UX Design]],  [[DAS Interface]],  [[DAS PRD]]
**Examples:** [[HBR Design\|minimal]],  [[HBR Design\|fuller]]

**TLDR** — `{slug} Design.md` is the one-per-anchor dispatch page listing the high-level system-spec documents (UX Design, Interface, Decisions, Data Model, Principles, PRD, Features, Roadmap, Design Discussion) for an anchor. It lives at the root-level `{slug} Design/{slug} Design.md`. The system-architecture story **is** a Design child — `{slug} Architecture` (a single `.md`, or a `{slug} Architecture/` folder-doc once it grows subsystems) inside `{slug} Design/`. (F094's root placement reversed 2026-06-27.) Interface is required for Code anchors.

**Location:** `{slug} Design/{slug} Design.md` (root-level folder, Gen-3)

The `{slug} Design.md` dispatch page inside the root-level `{slug} Design/` folder. Lists the **high-level system-spec documents** for the anchor.

Design holds UX Design (user-interaction shape), Interface (public-API / layer contract), Decisions, Data Model, Principles, PRD, Features, Roadmap, and design-trade-off discussion. The **system-architecture story is a Design child** (`{slug} Design/{slug} Architecture`, per [[DAS Architecture]]) — listed on the Design dispatch like the other design docs. Interface lives here (not in `{slug} User Docs/`) because its content describes a system contract, not an end-user task.

**Cardinality:** one per anchor — each anchor has exactly one `{slug} Design.md` dispatch page inside its `{slug} Design/` folder.

**Working example:** the live working example is migrated per anchor as part of F094 Phase 1; CAE / SKA / CAB are the first to land.

Below is a condensed reference example.

# Reference Example
---

# CAE Design

| -[[HBR Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Dispatch]] → [FCT Design Dispatch](hook://p/DAS%20Design%20Dispatch)<br>: design — system spec, UX, interface, data, principles |
| --- | --- |
| [[FEX Architecture\|Architecture]] | system-architecture story — a Design child (`{slug} Architecture`) |
| [[HBR UX Design\|UX Design]] | user-interaction shape — screens, commands, output formats |
| [[CAE Interface\|Interface]] | top-level layer contract — public API for callers (required for Code anchors) |
| [[CAE Data Model\|Data Model]] | data shapes & schemas |
| [[FEX Decisions\|Principles]] | load-bearing rules & invariants |
| [[HBR PRD\|PRD]] | product requirements |
| [[CAE Design Discussion\|Design Discussion]] | design trade-off conversations |

---

# Format Specification

## Location

`{slug} Design.md` lives inside the root-level `{slug} Design/` folder.

## Structure (per F060)

- **YAML frontmatter** — optional, when the dispatch carries a `description:`.
- **H1** — `# {slug} Design`. Blank line after.
-[[{slug} Design]]-`, top-right is `><br>: design — system spec, UX, interface, data, principles`.
- **Body rows** — one row per design document, with wiki-link in column 1 and short description in column 2.
- **Auto-management separator** — a `---` row enables auto-listing of remaining children. See [[DAS Anchor Page]] § Separators.

## Contents

The Design dispatch page lists the children of the Design folder (plus a cross-link to the root-level Architecture folder):

| Document | Part | Notes |
|----------|------|-------|
| `{slug} Architecture` (`.md` → `{slug} Architecture/` folder-doc on growth) | [[DAS Architecture]] | **A Design child** — the system-architecture story; governed by [[DAS Architecture]]. (F094's root placement reversed 2026-06-27.) |
| `{slug} UX Design.md` (or `{slug} UX Design/` if it grows) | [[DAS UX Design]] | User-interaction shape. |
| `{slug} Interface.md` | [[DAS Interface]] | Top-level layer contract — REQUIRED for Code anchors. Lives in Design (not `{slug} User Docs/`). |
| `{slug} Decisions.md` | [[DAS Decisions]] | Load-bearing rulings / invariants. |
| `{slug} Data Model.md` | (when applicable) | Data shapes, schemas, type contracts. |
| `{slug} Principles.md` | (when applicable) | Load-bearing rules / invariants. |
| `{slug} PRD.md` | [[DAS PRD]] | Product requirements (when applicable). |
| `{slug} Features/` | [[DAS Features]] | Dated feature specs (feature docs are design artifacts). |
| `{slug} Roadmap.md` | [[DAS Roadmap]] | Implementation milestones (sequencing-design). |
| `{slug} Design Discussion.md` | design-level discussion | Trade-off conversations whose outcomes land in PRD / Architecture / Interface. |

Not all entries are required — only list documents that exist for this anchor.

**Note — separation of concerns:**

- **Architecture** describes the *system* (modules, interfaces, data flow) — internal structure. Its own **root-level folder** in Gen-3.
- **UX Design** describes the *user-interaction* (screens, commands, output) — external shape. A Design child.
- **Interface** describes the *contract callers consume* (types, operations, invariants) — public API. A Design child.

The folder is named **Design** (not **Architecture**) so "Architecture" stays precise as the system-architecture facet — a peer root-level folder, never the umbrella over Design.

## Audience

System designers, architects, integrators-above-the-layer, and anyone evaluating the design. Distinct from:

- [[DAS Track Dispatch|Track]] — **planning-agent** surface (Backlog, Status, ephemeral surfaces)
- [[DAS User Dispatch|User Docs]] — **end-user / consumer** surface (Guide, CLI, FAQ)
- [[DAS Dev Dispatch|Dev Docs]] — **implementer** surface (Files.md, per-module reference)

# RULESET R-design-dispatch
include::
where:: `file: **/{{slug}} Design.md`
description:: Rules every `{slug} Design.md` dispatch page must satisfy — location, H1 form, dispatch-table structure, and required-document coverage for Code anchors.

### RULE R-design-dispatch-01 — File lives inside `{slug} Design/` (checked)
The dispatch page `{slug} Design.md` must reside at `{slug} Design/{slug} Design.md` — inside the root-level `{slug} Design/` folder.
**Check pattern:** the file's parent directory name matches `{slug} Design`.
**Why:** the location is the facet's contract; a misplaced dispatch page is invisible to anchor-page resolution and breaks folder-relative linking. (sampled)

### RULE R-design-dispatch-02 — H1 is `# {slug} Design` (checked)
The file's H1 reads exactly `# {slug} Design` where `{slug}` is the anchor's root ID.
**Check pattern:** H1 matches `^# \S+ Design$`.
**Why:** the H1 is used as the anchor-page title in dispatch tables; a wrong H1 surfaces the wrong name everywhere it appears. (checked)

-[[{slug} Design]]-` form (checked)
-[[{slug} Design]]-` in column 1 and the `><br>: design — …` description in column 2.
**Check pattern:** first table row starts with `| -[[` and ends with a `><br>:` description.
**Why:** the strikethrough self-link form is the FCT Anchor Page standard for dispatch tables; deviating breaks the consistent navigation pattern across all anchors. (sampled)

### RULE R-design-dispatch-04 — Interface entry present for Code anchors (sampled)
Anchors that carry the Code trait MUST include a `{slug} Interface.md` row in the dispatch table (per F094 Q3=A — Interface is a system contract, not an end-user doc).
**Check pattern:** for anchors with `traits: [code]` or equivalent, the dispatch table contains a row linking `{slug} Interface`.
**Why:** Interface is required for Code anchors; omitting it leaves callers without the public-API contract the Design folder exists to surface. (sampled)

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above.)*

- **Inclusion test for the dispatch table** — a document belongs iff it lives inside `{slug} Design/` AND describes the system's *design* (UX shape / interface contract / decisions / data model / principles / PRD / features / roadmap / design-trade-off discussion); implementation details → Dev Docs, end-user guides → User Docs, planning metadata → Track (per § Audience).
- **Don't rename the folder** — "Design" and "Architecture" are peer root-level folders kept distinct so "Architecture" stays precise; renaming would collide them, so don't rename without coordinating a vault-wide migration.
- **Cross-ref integrity** — cited by [[CAB Base]], [[DAS Anchor Page]], the Architecture / UX Design / Interface / PRD facets, and the `/design` and `/architect` skills; check these before structural edits.
