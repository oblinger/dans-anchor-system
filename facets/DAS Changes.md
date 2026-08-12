---
description: "specification for the OpenSpec-conformant changes/ folder — C-numbered change folders that land on the backlog like features"
group: file
---

| -[[DAS Changes]]- | → [[DAS]] → [[FCT]] → [DAS Changes](hook://p/DAS%20Changes)  |
| --- | --- |
| Related | [[DAS Specs]],  [[DAS Features]],  [[DAS Backlog]],  [[F230 — OpenSpec conversion\|F230]],   |
| Skills | [[skills/change/SKILL\|/change]] (create),  [[skills/mint/SKILL\|/mint]] (execute),  [[skills/finalize/SKILL\|/finalize]] (archive-merge) |
| Rules | [[R-changes]],   |
| Examples | none yet — first adoption pending ([[F230 — OpenSpec conversion\|F230]]) |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Changes
Specification for the **Changes** facet — the OpenSpec-conformant `changes/` folder holding C-numbered change folders, each a self-contained unit of work that lands on the backlog exactly like a feature does.

**Location:** `changes/` at the anchor root (lowercase, [OpenSpec](https://github.com/Fission-AI/OpenSpec/)-conformant — their tooling reads it unmodified). One folder per change: `changes/C<NNN>-<kebab-slug>/`.

**Cardinality:** at most one `changes/` folder per anchor; any number of change folders inside it. An anchor adopts `changes/` deliberately (per F230 incremental adoption) — the `{slug} Design/{slug} Features/` path stays the default; the two coexist.

## C-numbers

A change is identified by a **C-number**: monotonic per-anchor, zero-padded to three digits (`C001` … `C999`), never reused, minted by `state define {slug} Backlog C+`. C-numbers are a separate namespace from F-numbers — an anchor can hold `F023` and `C023` simultaneously. The backlog row carries the change through the same status-bracket lifecycle as a feature row ([[DAS Backlog]] § Status brackets), with the row body linking to the change's `proposal.md` by path-qualified wiki-link (the OpenSpec-required filenames repeat across changes, so bare `[[proposal]]` is ambiguous).

## Change folder structure

Each `changes/C<NNN>-<slug>/` folder holds:

- `proposal.md` — **required.** Why the change exists and what it does. Carries the change's `## Open Questions` zone while questions are pending (same lifecycle as a feature doc's; manage via `state <path-to-proposal.md> Q+ define`).
- `tasks.md` — **required.** The implementation checklist as `- [ ]` checkboxes. `/mint` executes a C-row by walking this file top to bottom, checking boxes as work lands.
- `design.md` — optional; transient design notes for the change. An epic-scale change may instead carry a `design/` folder (architecture, ux, subsystems) whose content `/finalize` reconciles into the anchor's durable design docs.
- `specs/<capability>/spec.md` — the **delta**: what this change ADDs / MODIFIEs / REMOVEs in the anchor's durable [[DAS Specs|specs/]]. This is the only directory OpenSpec tooling scans inside a change. Every ADDED or MODIFIED requirement needs at least one `#### Scenario:` block (their validator hard-errors otherwise — the accepted tax; it forces a minimum acceptance criterion onto every change).

## Lifecycle

1. **Create** — `/change` mints the C-row (`[Designing]`) and materializes the folder skeleton.
2. **Agree** — same user-agreement gate as `/feature` § Reach Agreement (compact confirm form); row → `[Ready]`.
3. **Execute** — `/mint` picks up the `[Ready]` C-row, drives `tasks.md` to all-checked; row → `[Active]` → `[Verify]`.
4. **Finalize** — `/finalize`'s archive-merge folds the change's `specs/` delta into the anchor's top-level `specs/`, reconciles any `design/` content into the durable design docs, then moves the folder to `changes/archive/C<NNN>-<slug>/`; row → `[Done]`.

An archived change is history — never edited, never un-archived; a follow-up is a new C-number.

# BRIEF

*(Maintainer note — agent-facing cautions.)*

- **Do not rename the OpenSpec-required filenames** (`proposal.md`, `tasks.md`, `spec.md`) to anchor-style names — conformance is the point of this facet. Anchor naming lives one level up (the folder and the backlog row).
- **The `specs/` delta is scanned by OpenSpec tooling; nothing else in the change folder is.** Extra files are ours and safe.
- **Migration of existing Features/ content into changes/ is F238's job** — per-project, user-reviewed. This facet never authorizes bulk conversion.
