---
description: "the facet spec"
group: file
---

| -[[DAS Facet]]- | → [[DAS]] → [[FCT]] → [DAS Facet](hook://p/DAS%20Facet)  |
| --- | --- |
| Related | [[DAS Skill]],  [[DAS Ruleset]],  [[DAS Facets]] (the index),  [[DAS Aspects]], |
| Examples | [[FEX Manifest\|one per anchor example]],  [[FEX Pin\|many per anchor example]],  [[FEX Bundle\|many folders per anchor example]],   |
| Rules | [[R-facet]],  [[R-facet-spec]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS At Entity]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Roadmap]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

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

# Facet and Template — one language, two addresses
A facet and a [[DAS Template|template]] are **not two kinds of thing**. They are the same specimen language at two addresses: a facet is checked into the **packaged tree** and ships with the standard; a template sits in the **content tree** beside the items it describes. Dan, 2026-08-04: *"that's really more about the scope of applicability and shareability, but less about the language. I think it would be best, if possible, that they're all the same."*

Both axes are **positional** — nothing is declared in a key. What an artifact attaches to is read off its form (§ Facet groups below, and [[DAS Template]] § Anchor); how far it reaches is read off its location, on a nearest-wins ladder that runs content folder → facet home → trait home → packaged root ([[DAS Template]] § Scope). A facet simply *is* the top rung of that ladder. Ratified 2026-08-20 as [[TINK302 - Section templates and the scope ladder|F302]] Q1/Q2, which also closed [[F220 — Template facet-or-discipline — design review + vault-wide placement sweep|F220]] Q4's deferral.

**The consequence that lands on this page: a facet spec should carry a template plus examples in that shared format.** The specimen becomes the normative statement of the shape and the prose is what surrounds it — which is why § Facet Document Structure asks for a `# RULESET` and worked examples rather than a prose re-description of a shape the examples already show. Where a spec describes its shape only in prose, the shape exists twice and the two copies can disagree; that is the same parity failure the ruleset discipline exists to prevent.

# Facet groups — what the facet attaches to
Every facet attaches to something, and *what* it attaches to is the only axis that has ever separated one kind of facet spec from another. The question is answerable by reading the ruleset's `where::` and asking what it selects. Four groups:

- **File facet** — `where::` selects **files**, by name or location: `` where:: `file:{anchor}/**/* Backlog.md` ``. The instance is a file, and the template is a file. [[DAS Backlog]], [[DAS Query]], [[DAS PRD]].
- **Folder facet** — the selector reaches a **folder**. The instance is a directory, and the template is a directory skeleton. [[DAS Rocks]] (`{slug} Rocks/`), [[DAS WP]] (`{slug} WP/`), [[DAS file-association]]. What decides the group is *what the selector reaches*, not the syntax it reaches it with, and three syntaxes are live: globbing the folder's contents (`` `file:{anchor}/**/* Rocks/**` ``, the trailing `/**`), **anchor scope** (`` `anchor` ``, evaluated once per anchor — eleven rules use it), and a **marker-file proxy** (`` `file: **/.anchor` ``, a file standing in for its directory). Stating the group as the glob form alone was too narrow and mis-sorted `file-association`; corrected 2026-08-11 by the [[TINK Backlog#^T196|T196]] classification pass — see [[DAS Disciplines]] § `where:: anchor` is a fourth way to reach a subject.
- **Slot facet** — the selector picks out a **region inside a file** — an extent with a start and an end, which may appear in documents of many different kinds: `` where:: `sentinel: ^#+ BRIEF\b` ``. The instance is a block, and so is the template. [[DAS Brief]] in its inline form, [[DAS Dispatch Table]], [[DAS spine]], [[DAS heart]].
- **Discipline facet** — the ruleset selects **nothing of its own**; it rides on whatever the other groups already select, which is why its `where::` is `` `always` `` or a bare `**/*.md`. [[DAS markdown]] does not pick out files — it applies wherever markdown appears. [[DAS Disciplines]] is the catalog.

**This is why the template test works.** File, folder and slot facets each have a locatable extent — a file, a directory, a block — so in each case there is something to template. A discipline has no extent, so there is nothing to template — the absence is structural, not a gap someone should go fill in. It is also the positive form of a definition that used to be stated as a negative ("a discipline is what doesn't fit a facet"): a discipline facet is one with **no selector of its own**.

## The declaration — `group:` in the spec's frontmatter
Every spec doc carries a frontmatter key naming its group, and **that key is what the audit reads**:

group: file

Values are `file`, `folder`, `slot`, `discipline`; a spec whose realization genuinely spans two says both (`group: file, folder` — [[DAS Template]], whose instances are `_{Name} Template.md` files *and* `_{Name} Template/` folders). `R-facet-spec` selects `` where:: `group: file, folder, slot` `` — so a discipline is out of scope by declaring what it is, not by being listed in someone's exclusion set. Landed 2026-08-11 by [[TINK Backlog#^T361|T361]], which replaced a 48-clause hand-maintained negative that had grown one clause at a time, each appended after a finding fired on a document the list had not yet heard of.

**Frontmatter rather than a body `group::` field**, for two reasons: frontmatter is the metadata surface these specs already carry (the `status::` dataview field is likewise specified as living in frontmatter), and a body line inside a spec is one dispatch-table rebuild away from sitting in an electric zone, where anything written is discarded.

**A misspelled value is refused loudly; a missing one is not.** `group: File` or `group: files` raises at plan time rather than silently dropping the spec out of scope — a spec that quietly stops being audited is a green that means nothing. Absence is the residual gap: a new spec that never declares a group is simply not selected, and nothing can tell that apart from an index page without reintroducing a list. Stated so it is a known cost rather than a surprise.

**`anchor` scope reaches a folder, except when its subject is plainly a file.** [[DAS Disciplines]] § `where:: anchor` is a fourth way… reads the eleven `anchor`-scoped rules as folder-reaching, which is right for `R-file-association`, `R-design`, `R-documentation-site` and `R-code-repository`. It is wrong for [[DAS Anchor Page]] (instance: `{slug}.md`) and [[DAS Dot Anchor]] (instance: the `.anchor` file) — anchor scope is *how those rules are evaluated*, not what they reach, and the criterion above is what the selector reaches. Both are declared `group: file`. Same correction for the marker-file proxy: [[DAS Folder]] is a folder facet because its subject is the directory, while `DAS Dot Anchor` reaches the marker file itself.

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
