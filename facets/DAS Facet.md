---
description: "the Facet primitive — what a facet is and how to write its spec"
---

| -[[DAS Facet]]- | → [[DAS]] → [[FCT]] → [DAS Facet](hook://p/DAS%20Facet)  |
| --- | --- |
| Related | [[DAS Skill]],  [[DAS Ruleset]],  [[DAS Facets]] (the index),  [[DAS Aspects]], |
| Examples | [[FEX Manifest\|one per anchor example]],  [[FEX Pin\|many per anchor example]],  [[FEX Bundle\|many folders per anchor example]],   |
| Rules | [[R-facet]],  [[R-facet-spec]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Roadmap]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Facet
A narrow, checkable aspect of an anchor — a file, a folder, a region inside a file, or a constraint riding on all three — and the spec for how to write one.

# Facet Document Structure
A facet spec is one file (`facets/DAS <Name>.md`), authoritative for that facet. Its parts, top to bottom — densest first, per [[DAS progressive-disclosure]]:

- **H1** — `# DAS <Name>`: the slug-name and the full name.
- **One-line summary** — a single sentence on the line directly under the H1 (no blank line between).
- **Dispatch table** — the breadcrumb row, then `Related` (lateral links only) and `Examples`.
- **Document structure** — this dense outline, placed first so a reader sees the doc's shape before any prose.
- **Overview** — a short paragraph: what the facet is and what it's for. *(Optional.)*
- **The Aspect contract** — content the body usefully conveys, mostly via the ruleset (section shapes vary; **not** fixed H2s; all optional): what it is · how it's detected (+ cardinality `one` / `many`) · format · constraints · expected usage · skills and audits that attach · triggers.
- **`# RULESET R-<facet>`** — **REQUIRED.** The embedded ruleset: how to validate and create the facet — detection, format, and constraints in auditable form (e.g. [[R-fex-manifest]]). It's how we know what the facet is and how to check it.
- **`# BRIEF`** — **REQUIRED.** Agent-facing documentation (per [[DAS Brief]]) — what an agent reads before editing this facet. (Agent ≈ maintainer, but the audience is the agent, not the user.)

For a worked facet, open an example in the dispatch table above — there is no embedded copy here, because a facet is itself a full anchor page and embedding one inside this spec just blurs example-vs-spec. The enforceable form of the rules below is the embedded **`R-facet-spec`** ruleset.

# Facet Overview
A **facet** is a narrow, checkable aspect of an anchor — one specific structural feature (a `Backlog` file, the region above a page's H1, the markdown conventions every page obeys), defined by its own spec doc and detected through the `where::` selector of its ruleset. This page is the spec for *the facet kind itself*: what a facet is and the shape every facet spec doc takes. It is the singular **definition**; [[DAS Facets]] (plural) is the **index** of all concrete facets.

A facet **defines a kind**. The concrete `<slug> Backlog.md` inside a real project is an *instance* of the Backlog facet, not a facet itself — keep the two apart.

Facets are one of the two kinds of [[DAS Aspects|Aspect]] — the narrow, selector-detected kind; the broad declared-paradigm kind is the [[DAS Traits|Trait]] (full distinction: [[DAS Aspects]] § Trait vs Facet). The shared model lives in [[DAS Aspects]]; this page is the facet-authoring view of it.

# Facet groups — what the facet attaches to
Every facet attaches to something, and *what* it attaches to is the only axis that has ever separated one kind of facet spec from another. The question is answerable by reading the ruleset's `where::` and asking what it selects. Four groups:

- **File facet** — `where::` selects **files**, by name or location: `` where:: `file:{anchor}/**/* Backlog.md` ``. The instance is a file, and the template is a file. [[DAS Backlog]], [[DAS Query]], [[DAS PRD]].
- **Folder facet** — the selector reaches a **folder**, by globbing its contents — the trailing `/**` is the form: `` where:: `file:{anchor}/**/* Rocks/**` ``. The instance is a directory, and the template is a directory skeleton. [[DAS Rocks]] (`{slug} Rocks/`), [[DAS WP]] (`{slug} WP/`).
- **Slot facet** — the selector picks out a **region inside a file** — an extent with a start and an end, which may appear in documents of many different kinds: `` where:: `sentinel: ^#+ BRIEF\b` ``. The instance is a block, and so is the template. [[DAS Brief]] in its inline form, [[DAS Dispatch Table]], [[DAS spine]], [[DAS heart]].
- **Discipline facet** — the ruleset selects **nothing of its own**; it rides on whatever the other groups already select, which is why its `where::` is `` `always` `` or a bare `**/*.md`. [[DAS markdown]] does not pick out files — it applies wherever markdown appears. [[DAS Disciplines]] is the catalog.

**This is why the template test works.** File, folder and slot facets each have a locatable extent — a file, a directory, a block — so in each case there is something to template. A discipline has no extent, so there is nothing to template — the absence is structural, not a gap someone should go fill in. It is also the positive form of a definition that used to be stated as a negative ("a discipline is what doesn't fit a facet"): a discipline facet is one with **no selector of its own**.

**The group describes the realization, not the identity.** [[DAS Brief]] is a slot facet in its Phase 1 inline `# BRIEF` form and becomes a file facet as a Phase 2 `<Name> Brief.md` sidecar, with its contract unchanged across the move. So the group is **declared in the spec**, never encoded in which folder the spec lives in — a folder forces one answer permanently, and Brief is proof that a facet can legitimately change groups. `facets/` and `disciplines/` remain two folders for historical reasons; the folder is not the taxonomy.

## The one selector the grammar cannot express
`sentinel:` matches a region that announces itself with a marker, which is how a slot facet is normally selected. But a spine (everything above the H1) and a heart (what sits directly below it) are defined by **position** — there is no marker to match — so both fall back to `` where:: `always` ``, indistinguishable in the grammar from a true discipline even though each has an extent and a template. Read those two as slot facets on the strength of their specs, not their `where::` line. The gap is real and named; it is not a reason to doubt the group.

## Folder facets fire only if the selector is written from the parent's side
A folder facet's instance carries **its own `.anchor`**, which drops it out of the parent anchor's scope — so it is only ever audited scoped on *itself*, where `{anchor}` **is** the folder and a selector like `{anchor}/**/* Rocks/**` demands a nested `* Rocks/` inside itself. Unsatisfiable from both ends. Every `R-rocks-*` rule read `(checked)` while firing on nothing, on both live instances, at every scope, until T164 fixed it 2026-08-08 — by matching each file against a path prefixed with the anchor's own directory name, *and* by naming the ruleset in `R-anchor`'s `include::` (being listed in `R-facet` is not adoption; a ruleset reachable only through `R-facet` never loads). **Both halves were required** — fixing either alone changed nothing, which is how the diagnosis was confirmed.

This is the group's characteristic failure and it is a **vacuous zero**: the audit reporting no failures is exactly what the broken state looked like. When adding a folder facet, assert the rules *fire* — `test-t164-folder-facet-selector.py` is the guard.

*(Distinct from [[DAS Folder]], which governs **anchor** folders and does reach its subject by proxy — `` where:: `file: **/.anchor` ``, a marker file standing in for the directory that contains it.)*

# Examples of a facet — project instances vs standalone `FEX` artifacts
A facet's worked examples come in two kinds, and the **prefix tells them apart**:

- **Project instances** — a real `{slug} <Facet>.md` living inside a project example world ([[HBR]], [[FEX Repo]]) or an actual anchor. It keeps the project's slug (`HBR CLI`, `SKA Backlog`) and is linked from the `Examples` row (R-facet-spec-25).
- **Standalone teaching artifacts** — an example that belongs to *no* single project world (a dispatch-table gallery, a page-layout exemplar). It carries the **`FEX`** prefix — `FEX` marks "example" exactly as `DAS` marks "spec", so a reader tells them apart at a glance — and lives as a plain file **in the facet's group folder** (`facets/FEX <Name>.md`), beside the `DAS` specs. **No per-facet anchor is created** (that's the "bunch of anchors" trap); a set of related ones may be gathered by a `FEX <Group>` gallery/dispatch page in the same folder. Group-level placement is what lets a **cross-facet** example (one that teaches several facets at once) have a natural home.

Worked instances of the standalone kind: [[FEX Dispatch Examples]] (+ [[Devtools]] / [[Bridges]] / [[FEX Figure Page]]) in `facets/`; [[FEX Scheduler]] in `examples/`.

# BRIEF

*(Maintainer note — facet-specific cautions for editing this spec.)*

- **`R-facet-spec` (embedded here) ≠ the umbrella [[R-facet]].** This page's ruleset governs facet *spec docs*; `R-facet` aggregates each materialized facet's *instance* rules. Keep the `Facet Document Structure` bullet list and the `R-facet-spec` ruleset **in sync** — the list is the readable form, the ruleset the auditable one.
- **This page deliberately embeds no worked example** (R-facet-spec-20) — it models the rule it states; don't add one.
