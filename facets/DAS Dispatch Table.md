---
description: "the top-of-page navigation table — its own spec, dogfooded"
---

# DAS Dispatch Table
The top-of-file table convention that gives most anchor pages and many facet pages their navigation surface.

| -[[DAS Dispatch Table]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Dispatch Table](hook://p/DAS%20Dispatch%20Table) |
| --- | --- |
| Related | [[Collection]],  [[DAS progressive-disclosure]],  [[audit-dispatch\|/audit dispatch]],  [[DAS Dispatch Table Design\|Design]],   |
| Examples | [[HBR\|minimal]],  [[HBR\|fuller]],  [[FEX Dispatch Examples\|full gallery]],   |
| Rules | [[R-dispatch-table]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — **Cardinality: many** — one dispatch table per page; most anchor and facet pages carry one. The masthead is the breadcrumb plus, in fixed order, the optional **Related → type → Design → Track → User Docs → Dev Docs** rows (a switchboard, not a directory) — each row a link down to a sub-area plus its key parts; anything enumerable beyond those drops to the Member zone below. `/audit dispatch` builds and repairs it.

**Examples** — below the masthead (this page's member zone is its four live exemplars; each row is itself a tiny member list, dogfooding the form):

| [[HBR]] | masthead-only — breadcrumb + structural rows, no member zone |
| --- | --- |
| [[DAS Skills]] | member groups (`+`) — > 15 members, expandable group rows |
| [[SKA Access]] | flat member list — ≤ 15 members, hand-ordered |
| [[SYS]] | hybrid — manual category rows + `...` auto-staging |

## What it is

A markdown table placed immediately under the H1 of a page. The first row carries the breadcrumb cell (anchor path + hook URL); subsequent rows group related links by category. Wiki-links inside table cells escape the pipe as `[[Target\|Display]]`.

**Page-top discipline (every page).** `# <H1>` on the first line, the **one-line summary directly underneath — no blank line between** — then one blank line, then this dispatch table. (An overview figure, if any, sits between the summary and the table.)

**Masthead rows — the model** (worked exemplars: [[HBR]] (project), [[SKA crank]] / [[SKA workflow]] (leaf); vault-wide rollout tracked in [[F189]]). After the breadcrumb identity row, the optional rows appear in a **fixed order**, each present **only if it applies**:

1. **Related** — related anchors / siblings **and external resources** (code repo, project page, docs site) that are **not** already in the breadcrumb. First, because it answers "what else is near this?" before the reader descends into the anchor's own contents. *(This replaces the former `External` row — repo / site links live in Related now.)*
2. **Type row** *(typed leaf anchors only — skill / discipline / facet)* — label is the type word (`skill`, `Discipline`, `Facet`); cell carries the runtime / external links (the `SKILL` object + `[[DAS <Name>|User Docs]]`).
3. **Design** — left cell `[[<X> Design\|Design]]`, right cell the design parts that exist: PRD, Architecture, Decisions, UX Design, Roadmap, Stories.
4. **Track** — left cell `[[<X> Track\|Track]]`, right cell the tracking items that exist: Backlog, Features, Roadmap, Now. *(Absent when tracking is unified at a parent — D10.)*
5. **User Docs** — left cell `[[<X> User Docs\|User Docs]]` (or `[[<X> User\|User Docs]]`), right cell the user docs (Guide, …). Always labeled **User Docs**, never *User*.
6. **Dev Docs** — left cell `[[<X> Dev Docs\|Dev Docs]]` (or `[[<X> Dev\|Dev Docs]]`), right cell the dev docs (Files, …). Always labeled **Dev Docs**, never *Dev*.

Every row after the breadcrumb has the **same shape**: its **left cell is a link *down* to a sub-area** (the row's name) and its **right cell enumerates that sub-area's key parts**. There is **no generic `Anchor` row** — superseded ("everything is an anchor", so the label conveyed nothing). A skill / discipline / facet leaf anchor uses the **type row** (and a Design row) and carries **no** Track / User Docs / Dev Docs rows; a project (Code) anchor uses **Design / Track / User Docs / Dev Docs**. **List only members that exist** — never pre-populate phantom/empty links (they render as strikethrough cruft, and a mis-click mints a blank doc); a stray/new doc is caught by the trailing catch-all marker (R-07), not by dead links.

**Ending — the `...` catch-all.** The masthead's **last row is `| ... |  |`** (R-07): after the standard rows — and after any anchor-specific extra rows that don't fit the standard set — this catch-all auto-surfaces any file in the anchor's folder not already captured above, so a stray or newly-dropped doc never silently disappears. (The optional anchor-specific rows sit *between* the standard rows and this final `...`.)

**Tracking can be unified at a parent** ([[SKA Decisions]] D10). A `track` group-row appears **only on an anchor that owns its own tracking**; sub-anchors whose tracking is unified at a parent (skills / facets / disciplines → the SKA-level backlog) carry **no Track row** — just the type-specific row + a `Design` row. **Coupled facet+discipline share one design folder, dual-linked:** a Track facet + its Workflow discipline (and a Design facet + its Architect skill) each carry a `Design` row pointing at the **same** single design folder (hosted on the behavioral core — `workflow` / `architect`); the folder is reached from either page, never duplicated.

## Anatomy of a dispatch row

A dispatch row is `| left-cell | right-cell |`. The **breadcrumb identity row** is special: its left cell is the page's own name as a struck self-link, its right cell is the parent-chain path ending in the page's `hook://` link, followed by a `<br>` and a one-line description. Every **other** row has the same shape — the left cell names a sub-area (a link *down* to it), the right cell enumerates that sub-area's key parts, comma-separated. Aliased wiki-links inside cells escape the pipe as `[[Target\|Display]]` (R-03). The table's final row is the catch-all marker (R-07). The live rendered form is on [[HBR]] (masthead) and [[FEX Dispatch Examples]] (full gallery).

## Structure — Masthead + Member zone

A dispatch table has up to **two zones** (worked examples: [[FEX Dispatch Examples]]):

### Masthead — the fixed top block (always present)

Hand-authored, one-of-a-kind to this anchor, and deliberately **small** — a switchboard, not a directory. It is the breadcrumb identity row, then the optional rows in the fixed order of § Masthead rows — **Related → type row → Design → Track → User Docs → Dev Docs** — each present **only if it applies**. Every row after the breadcrumb is *sub-area link → that sub-area's key parts*. There is **no** generic `Anchor` row.

**A dispatch table is a pure link table** (`R-dispatch-table-06`): the distilled set of jump-destinations, not an explanation of them. No prose about what a link *means* in a cell — at most one or two parenthetical words, preferably none. A destination's meaning lives on the destination's own top line + `description`.

Anything **enumerable beyond a sub-area's key parts** — a Collection's full member list, sub-items, worked examples — is **not** a masthead row; it drops to the Member zone below.

#### The unified placement rule (one law, not a rule per row)

RULE (masthead-placement): the masthead is **exactly** the breadcrumb row plus the standard rows **Related**, **type row** (skill / discipline / facet only), **Design**, **Track**, **User Docs**, **Dev Docs** — in that order, each present **iff** its information exists:

| Information — *if it exists* | …lives in this row |
|---|---|
| the parent / up-edge | **breadcrumb** (always present) |
| related anchors + external resources (repo / site) not in the breadcrumb | **Related** (first) |
| a typed leaf anchor's runtime / external links | **type row** (Skill / Discipline / Facet) |
| the design flow — PRD, Architecture, Decisions, … | **Design** — `[[X Design\|Design]]` + parts |
| the tracking surface — Backlog, Features, … | **Track** — `[[X Track\|Track]]` + items |
| user-facing documentation | **User Docs** — `[[X User Docs\|User Docs]]` + members |
| developer documentation | **Dev Docs** — `[[X Dev Docs\|Dev Docs]]` + members |
| **anything enumerable beyond key parts** | **none** — it drops to the Member zone |

This is the single law for masthead content: a standard row exists **exactly when** its information does, in the fixed order above, and the canonical row *names* are fixed — never bare `User` / `Dev` (use `User Docs` / `Dev Docs`), never `External` (use `Related`), never a generic `Anchor`.

### Member zone — the members (only on a [[Collection]] anchor)

Below the Masthead, a [[Collection]] anchor enumerates its **members**. Two **orthogonal** axes:

**Axis 1 — layout (the [[DAS progressive-disclosure]] pattern):**
- **Member list** — flat; one row (or compact line) per member. Use ≤ ~15 members.
- **Member groups** — members under labeled group rows; a group row may carry a **`+`** to mark it expandable (it has children of its own). Use > 15 members (the progressive-disclosure size rule; the graduation is [[DAS granularity]]).
  - RULE (grouped-rows-link-down): **each group row's label is a link** *down* to that group's own anchor page + dispatch table — the group is a **container**, per [[DAS progressive-disclosure]] § The tree of containers. A grouped table is therefore one node of the container tree; clicking a group label descends to a finer node (its members). The `+` is the visible mark that the label is an expandable container, not a leaf.
  - RULE (container-ends-electric): a **container's** dispatch table **ends with an electric-list marker** — `...` (compact auto), `| --- | |` (auto-list), or trailing `+`-group rows — so newly-added children have a defined place to land. *(Tied to the container trait.)*

**Axis 2 — automation (who orders the rows):**
- **Manual** — hand-ordered rows; the author controls order and pinning.
- **Auto** — children auto-listed below a **`---`** separator (`| --- | |`), or as a **`...`** compact single-row enumeration. The agent fills them; order is mechanical.
- **Hybrid** — pinned **manual** rows *above* the `---` line (highlights the author chose), with **auto** fill below.

The two axes combine freely: a member list or member groups can each be manual, auto, or hybrid.

### Syntax markers

| Marker | Means |
|---|---|
| `\| --- \| \|` | separator — children **auto-list** below it |
| `...` | **compact** auto-enumeration in one cell (few members, no per-member description) |
| `+` (suffix on a row label — e.g. a group row written `Group+`) | the row is an **expandable group** (member groups layout) |

Dated members (a [[DAS dated-entry-stream]] Collection like a Log) list newest-first with ISO-prefixed names.

**The member zone *is* the [[Collection]] anchor's face** — and `/audit dispatch` ([[audit-dispatch]]) builds/repairs exactly this structure.

## Classification — a facet (the table form)

A dispatch table is the **form** of an anchor's top-of-page switchboard — a concrete, auditable artifact (`/audit dispatch`, the masthead-placement law, the member-zone mechanics) embedded across many surfaces. It is a **facet**, not a discipline: unlike the principles it *obeys* ([[DAS progressive-disclosure]], [[DAS granularity]]), it is a thing you **build and audit**, not a way of thinking. *(Reclassified discipline → facet; the prior "the form is a discipline" framing is retired.)*

- **Form vs role.** This facet owns the table *form* (breadcrumb cell, category rows, masthead-placement law, member-zone axes). The *role* of "dispatching for this particular anchor kind" is layered on by [[DAS Anchor Page]] and its per-kind rulesets — the anchor page **delegates** its table to this facet. ~95% of dispatch tables are exactly that: an anchor page dispatching to its anchor's contents.
- **Shared across surfaces → factored out, not merged.** The form recurs on the per-sub-folder dispatch pages ([[DAS Design Dispatch]], [[DAS User Dispatch]], …) as well as the anchor masthead. Keeping it as its own facet lets every surface cite **one** spec — which is exactly why it is *not* folded into [[DAS Anchor Page]] (that would orphan the sub-folder dispatch facets).
- **Boundary with [[DAS progressive-disclosure]].** This facet owns the table *form* (cell shape, row anatomy, pipe-escape, the `(See …)` variant). `progressive-disclosure` owns *which pattern* — Compact / List / Grouped — and the `>15 → Grouped` size rule. **Form here; pattern there.**
- **Two different "anchor" facets — don't conflate.** [[DAS Anchor Page]] (the `{slug}.md` *entry page* that hosts the dispatch table) is separate from the **anchor spec** itself (the `.anchor` file's slug / traits / DAG edges). The dispatch table lives on the anchor *page*, never in the anchor *spec*.

## Current state

The convention is in active use across the vault; this spec covers the anatomy, the `(See …)` variant, and the classification above. Still TBD for full prescriptive coverage: required-cell enforcement, exhaustive grouping conventions, and the TOC interaction (deferred to [[Anchor TOC Format]]).

## The (See …) variant — for files without a dispatch table

When a file has no dispatch table (typically smaller content pages), the related-links surface becomes a single `(See …)` line under the H1:

Placed directly under the H1 on its own line — e.g. `(See …)` listing the page's Guide and a couple of related anchors, then the rest of the content follows. Format rules:

Format rules:
- Single set of parentheses around the whole list.
- The word `See` capitalized; no colon after it.
- Comma-separated wiki-links inside the parens.
- The Guide (if any) goes first.

## Worked examples

- [[DAS Facets]] — dispatch table with multiple category rows.
- [[SV Roots]] — dispatch table with a `Related` row pointing at [[SV Roots Brief]].

## Related

- [[DAS Dispatch]] — parent catalog.
- [[DAS Brief]] — the Brief discipline; uses the `Related` row or `(See …)` line to surface from the source file.
- [[Anchor TOC Format]] — distinct topic; TOC is generated, not the dispatch table.

# BRIEF

*(Maintainer note — editing the Dispatch Table spec.)*

- **Inclusion/exclusion:** content belongs only if it's a *rule* about dispatch-table shape (row order, cell format, breadcrumb syntax, pipe-escape, the `Related` row, the `(See …)` variant). How a *specific anchor* uses its table goes in that anchor's docs — don't accumulate worked-example links here.
- **Keep the two surface forms in lockstep:** the full table (breadcrumb + category rows) and the `(See …)` line variant; don't let one drift from the other.
- **The load-bearing constraints are downstream-cited everywhere** — the pipe-escape (`[[Target\|Display]]`), the breadcrumb cell shape, and the `Related`-row convention. Changing any requires a **vault-wide sweep**.
- **Boundary:** TOC generation is governed by [[Anchor TOC Format]], not here — cross-reference, don't inline.
- **Status: skeleton** — pending a full prescriptive spec; mark new rules not-yet-enforced-vault-wide as such.
