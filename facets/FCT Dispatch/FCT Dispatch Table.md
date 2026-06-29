---
description: "the top-of-page navigation table — its own spec, dogfooded"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Dispatch Table](hook://p/FCT%20Dispatch%20Table)

# FCT Dispatch Table
The top-of-file table convention that gives most anchor pages and many facet pages their navigation surface.

**Related:** [[Collection]],  [[DSC progressive-disclosure]],  [[audit-dispatch\|/audit dispatch]]

| Table of Contents |  |
|---|---|
| [[#What it is]] |  |
| [[#Anatomy of a dispatch row]] |  |
| [[#Structure — Masthead + Member zone]] |  |
| [[#Classification — a facet (the table form)]] |  |
| [[#Current state]] |  |
| [[#The (See …) variant — for files without a dispatch table]] |  |
| [[#Worked examples]] |  |
| [[#Related]] |  |
| **[[#BRIEF]]** |  |
**Design:** [[CAB Dispatch Table Design\|Design]]
**Examples:** [[CAE\|minimal]],  [[HBR\|fuller]],  [[CAE Dispatch Examples\|full gallery]]

**TLDR** — **Cardinality: many** — one dispatch table per page; most anchor and facet pages carry one. The masthead is the breadcrumb plus, in fixed order, the optional **Related → type → Design → Track → User Docs → Dev Docs** rows (a switchboard, not a directory) — each row a link down to a sub-area plus its key parts; anything enumerable beyond those drops to the Member zone below. `/audit dispatch` builds and repairs it.

**Examples** — below the masthead (this page's member zone is its four live exemplars; each row is itself a tiny member list, dogfooding the form):

| [[CAE]] | masthead-only — breadcrumb + structural rows, no member zone |
| --- | --- |
| [[SKL]] | member groups (`+`) — > 15 members, expandable group rows |
| [[SKA Access]] | flat member list — ≤ 15 members, hand-ordered |
| [[SYS]] | hybrid — manual category rows + `...` auto-staging |

## What it is

A markdown table placed immediately under the H1 of a page. The first row carries the breadcrumb cell (anchor path + hook URL); subsequent rows group related links by category. Wiki-links inside table cells escape the pipe as `[[Target\|Display]]`.

**Page-top discipline (every page).** `# <H1>` on the first line, the **one-line summary directly underneath — no blank line between** — then one blank line, then this dispatch table. (An overview figure, if any, sits between the summary and the table.)

**Masthead rows — the model** (worked exemplars: [[CAE]] (project), [[SKA crank]] / [[SKA workflow]] (leaf); vault-wide rollout tracked in [[F189]]). After the breadcrumb identity row, the optional rows appear in a **fixed order**, each present **only if it applies**:

1. **Related** — related anchors / siblings **and external resources** (code repo, project page, docs site) that are **not** already in the breadcrumb. First, because it answers "what else is near this?" before the reader descends into the anchor's own contents. *(This replaces the former `External` row — repo / site links live in Related now.)*
2. **Type row** *(typed leaf anchors only — skill / discipline / facet)* — label is the type word (`Skill`, `Discipline`, `Facet`); cell carries the runtime / external links (the `SKILL` object + `[[SKL <Name>\|User Docs]]`).
3. **Design** — left cell `[[<X> Design\|Design]]`, right cell the design parts that exist: PRD, Architecture, Decisions, UX Design, Roadmap, Stories.
4. **Track** — left cell `[[<X> Track\|Track]]`, right cell the tracking items that exist: Backlog, Features, Roadmap, Now. *(Absent when tracking is unified at a parent — D10.)*
5. **User Docs** — left cell `[[<X> User Docs\|User Docs]]` (or `[[<X> User\|User Docs]]`), right cell the user docs (Guide, …). Always labeled **User Docs**, never *User*.
6. **Dev Docs** — left cell `[[<X> Dev Docs\|Dev Docs]]` (or `[[<X> Dev\|Dev Docs]]`), right cell the dev docs (Files, …). Always labeled **Dev Docs**, never *Dev*.

Every row after the breadcrumb has the **same shape**: its **left cell is a link *down* to a sub-area** (the row's name) and its **right cell enumerates that sub-area's key parts**. There is **no generic `Anchor` row** — superseded ("everything is an anchor", so the label conveyed nothing). A skill / discipline / facet leaf anchor uses the **type row** (and a Design row) and carries **no** Track / User Docs / Dev Docs rows; a project (Code) anchor uses **Design / Track / User Docs / Dev Docs**. **List only members that exist** — never pre-populate phantom/empty links (they render as strikethrough cruft, and a mis-click mints a blank doc); a stray/new doc is caught by the trailing catch-all marker (R-07), not by dead links.

**Ending — the `...` catch-all.** The masthead's **last row is `| ... |  |`** (R-07): after the standard rows — and after any anchor-specific extra rows that don't fit the standard set — this catch-all auto-surfaces any file in the anchor's folder not already captured above, so a stray or newly-dropped doc never silently disappears. (The optional anchor-specific rows sit *between* the standard rows and this final `...`.)

**Tracking can be unified at a parent** ([[SKA Decisions]] D10). A `Track` group-row appears **only on an anchor that owns its own tracking**; sub-anchors whose tracking is unified at a parent (skills / facets / disciplines → the SKA-level backlog) carry **no Track row** — just the type-specific row + a `Design` row. **Coupled facet+discipline share one design folder, dual-linked:** a Track facet + its Workflow discipline (and a Design facet + its Architect skill) each carry a `Design` row pointing at the **same** single design folder (hosted on the behavioral core — `workflow` / `architect`); the folder is reached from either page, never duplicated.

## Anatomy of a dispatch row

A dispatch row is `| left-cell | right-cell |`. The **breadcrumb identity row** is special: its left cell is the page's own name as a struck self-link, its right cell is the parent-chain path ending in the page's `hook://` link, followed by a `<br>` and a one-line description. Every **other** row has the same shape — the left cell names a sub-area (a link *down* to it), the right cell enumerates that sub-area's key parts, comma-separated. Aliased wiki-links inside cells escape the pipe as `[[Target\|Display]]` (R-03). The table's final row is the catch-all marker (R-07). The live rendered form is on [[CAE]] (masthead) and [[CAE Dispatch Examples]] (full gallery).

## Structure — Masthead + Member zone

A dispatch table has up to **two zones** (worked examples: [[CAE Dispatch Examples]]):

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

**Axis 1 — layout (the [[DSC progressive-disclosure]] pattern):**
- **Member list** — flat; one row (or compact line) per member. Use ≤ ~15 members.
- **Member groups** — members under labeled group rows; a group row may carry a **`+`** to mark it expandable (it has children of its own). Use > 15 members (the progressive-disclosure size rule; the graduation is [[DSC granularity]]).
  - RULE (grouped-rows-link-down): **each group row's label is a link** *down* to that group's own anchor page + dispatch table — the group is a **container**, per [[DSC progressive-disclosure]] § The tree of containers. A grouped table is therefore one node of the container tree; clicking a group label descends to a finer node (its members). The `+` is the visible mark that the label is an expandable container, not a leaf.
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

Dated members (a [[DSC dated-entry-stream]] Collection like a Log) list newest-first with ISO-prefixed names.

**The member zone *is* the [[Collection]] anchor's face** — and `/audit dispatch` ([[audit-dispatch]]) builds/repairs exactly this structure.

## Classification — a facet (the table form)

A dispatch table is the **form** of an anchor's top-of-page switchboard — a concrete, auditable artifact (`/audit dispatch`, the masthead-placement law, the member-zone mechanics) embedded across many surfaces. It is a **facet**, not a discipline: unlike the principles it *obeys* ([[DSC progressive-disclosure]], [[DSC granularity]]), it is a thing you **build and audit**, not a way of thinking. *(Reclassified discipline → facet; the prior "the form is a discipline" framing is retired.)*

- **Form vs role.** This facet owns the table *form* (breadcrumb cell, category rows, masthead-placement law, member-zone axes). The *role* of "dispatching for this particular anchor kind" is layered on by [[FCT Anchor Page]] and its per-kind rulesets — the anchor page **delegates** its table to this facet. ~95% of dispatch tables are exactly that: an anchor page dispatching to its anchor's contents.
- **Shared across surfaces → factored out, not merged.** The form recurs on the per-sub-folder dispatch pages ([[FCT Design Dispatch]], [[FCT User Dispatch]], …) as well as the anchor masthead. Keeping it as its own facet lets every surface cite **one** spec — which is exactly why it is *not* folded into [[FCT Anchor Page]] (that would orphan the sub-folder dispatch facets).
- **Boundary with [[DSC progressive-disclosure]].** This facet owns the table *form* (cell shape, row anatomy, pipe-escape, the `(See …)` variant). `progressive-disclosure` owns *which pattern* — Compact / List / Grouped — and the `>15 → Grouped` size rule. **Form here; pattern there.**
- **Two different "anchor" facets — don't conflate.** [[FCT Anchor Page]] (the `{NAME}.md` *entry page* that hosts the dispatch table) is separate from the **anchor spec** itself (the `.anchor` file's slug / traits / DAG edges). The dispatch table lives on the anchor *page*, never in the anchor *spec*.

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

- [[FCT Facets]] — dispatch table with multiple category rows.
- [[SV Roots]] — dispatch table with a `Related` row pointing at [[SV Roots Brief]].

## Related

- [[FCT Dispatch]] — parent catalog.
- [[FCT Brief]] — the Brief discipline; uses the `Related` row or `(See …)` line to surface from the source file.
- [[Anchor TOC Format]] — distinct topic; TOC is generated, not the dispatch table.

# RULESET R-dispatch-table
include::
where:: file: {ANCHOR}/**/*.md
description:: The shape every dispatch table must take — masthead-placement law, member-zone mechanics, and pipe-escaped cell links.

### RULE R-dispatch-table-01 — Masthead rows appear in a fixed order (checked)
After the breadcrumb identity row, the masthead's optional rows appear in this **fixed order**, each present **only if it applies**: **Related** → **type row** (skill / discipline / facet leaf anchors only) → **Design** → **Track** → **User Docs** → **Dev Docs**. There is **no generic `Anchor` row** (superseded — everything is an anchor; the label conveyed nothing). Every row after the breadcrumb has the **same shape**: its **left cell is a link *down* to that sub-area** (the row's name), and its **right cell enumerates that sub-area's key parts** for one-click access. Per-row rules: R-08 (Related) … R-12 (Dev Docs). Full model: § What it is.
**Check pattern:** rows, where present, occur in the order Related, [type], Design, Track, User Docs, Dev Docs; no row labeled `Anchor`.
**Why:** a stable left-to-top-to-bottom reading order makes every anchor page scan the same way; the row *names* the sub-area and the cell jumps you into it.

### RULE R-dispatch-table-08 — Related is the first optional row and absorbs external links (checked)
The first optional row is **Related**. It carries links to genuinely-related anchors / siblings **and external resources** — the code repo, the published project page, a docs site — i.e. anything related that is **not already in the breadcrumb path**. There is **no separate `External` row**; repo / site URLs live in **Related**. **An anchor that has a code repo (a `code:` key in its `.anchor`) carries a `[code](hook://f/{SLUG}?facet=code)` link in Related** — the hook `f/` (finder) verb opens the anchor's code folder in Finder (`{SLUG}` = the anchor's slug). Optional and never manufactured (per R-05).
**Check pattern:** no masthead row is labeled `External`; if a `Related` row exists it precedes every sub-area row.
**Why:** "what else is near this?" is answered once, up top, before the reader descends into the anchor's own contents; one row for all not-in-breadcrumb links keeps the switchboard small.

### RULE R-dispatch-table-13 — Code anchors carry a `[code]` link in Related (checked)
Every anchor whose `.anchor` declares a `code:` key (equivalently, carries the `Code` trait) includes, in its **Related** row, a markdown link **`[code](hook://f/{SLUG}?facet=code)`** where `{SLUG}` is the anchor's slug. The `f/` (finder) hook verb opens the anchor's code folder; one-click reach from the masthead to the code, with no hardcoded path. The link text is exactly `code`.
**Check pattern:** for every dispatch-table page whose anchor has a `code:` key, the Related row contains a `[code](hook://f/<slug>?facet=code)` link.
**Why:** the code is the point of a code anchor; a uniform, path-free `[code]` link makes it reachable from every such masthead and stays correct even if the repo moves (resolution is via the `.anchor` `code:` key, not a hardcoded path).

### RULE R-dispatch-table-09 — Design row links the sub-anchor and enumerates the design parts (checked)
When the anchor has a Design sub-area, the masthead carries a **Design** row whose **left cell is `[[{X} Design\|Design]]`** (a link down to the design sub-anchor) and whose **right cell lists the design's key parts** that exist — PRD, Architecture, Decisions, UX Design, Roadmap, Stories. It is **never a bare self-link** (`| Design | [[{X} Design]] |` with nothing else is wrong).
**Check pattern:** a row whose left cell links to `{X} Design` and whose right cell holds ≥1 design-part link, whenever a `{X} Design` folder exists.
**Why:** the design row is the entry into the design flow; surfacing its parts gives one-click reach to the architecture and the rest without opening the sub-page first.

### RULE R-dispatch-table-10 — Track row links the sub-anchor and enumerates the tracking items (checked)
When the anchor **owns its tracking**, the masthead carries a **Track** row: **left cell `[[{X} Track\|Track]]`**, **right cell the key tracking items** that exist — Backlog, Features, Roadmap, Now. Absent when tracking is unified at a parent (per [[SKA Decisions]] D10).
**Check pattern:** a row whose left cell links to `{X} Track` and whose right cell holds ≥1 tracking-item link, whenever the anchor owns a `{X} Track` folder.
**Why:** the track row is the direct line to the backlog and in-flight work; surfacing the items makes the anchor's status reachable in one click.

### RULE R-dispatch-table-11 — User-docs row is labeled "User Docs" (checked)
When the anchor has user-facing docs, the masthead carries a row **labeled `User Docs`** — never bare `User`. Left cell `[[{X} User Docs\|User Docs]]` (or `[[{X} User\|User Docs]]` where the folder is `{X} User`); right cell the user docs (Guide, …).
**Check pattern:** no masthead row is labeled bare `User`; the user-docs row's display text is `User Docs`.
**Why:** the bare word "User" reads as a person/role; "User Docs" names the artifact and keeps the four doc-area rows (Design / Track / User Docs / Dev Docs) parallel.

### RULE R-dispatch-table-12 — Dev-docs row is labeled "Dev Docs" (checked)
When the anchor has developer docs, the masthead carries a row **labeled `Dev Docs`** — never bare `Dev`. Left cell `[[{X} Dev Docs\|Dev Docs]]` (or `[[{X} Dev\|Dev Docs]]` where the folder is `{X} Dev`); right cell the dev docs (Files, …).
**Check pattern:** no masthead row is labeled bare `Dev`; the dev-docs row's display text is `Dev Docs`.
**Why:** parallel to R-11 — "Dev Docs" names the artifact, not a stage, and keeps the doc-area rows uniform.

### RULE R-dispatch-table-02 — Anything enumerable drops to the Member zone (stated)
Members, sub-items, and worked examples are **not** masthead rows — they live in the Member zone below, on [[Collection]] anchors.
**Why:** the masthead stays small and fixed; enumerable content grows and belongs in the auditable member zone.

### RULE R-dispatch-table-03 — Cell wiki-links escape the pipe (checked)
Inside table cells, aliased wiki-links escape the pipe: `[[Target\|Display]]`.
**Check pattern:** no unescaped `[[Target|Display]]` appears inside a table row.
**Why:** an unescaped pipe ends the table cell, breaking the row.

### RULE R-dispatch-table-04 — No breadcrumb-redundant links (checked)
No masthead row may link to an anchor that already appears in the **breadcrumb path**. The parent / up-edge lives **only** in the breadcrumb; re-linking it (in any sub-area row, the Related row, or anywhere) is forbidden — every anchor is trivially related to its parent, so the link adds nothing. (The sub-area rows therefore carry **down-edges only** — the anchor's own contents — never its parent catalog.)
**Check pattern:** no wiki-link target in a non-breadcrumb row matches any anchor in the breadcrumb chain.
**Why:** redundant — the breadcrumb already carries the up-edge directly above; the duplicate link only clutters the switchboard.

### RULE R-dispatch-table-05 — Related is optional; never manufactured (stated)
The **Related** row may be **empty or omitted**. List only *genuinely* related siblings/material plus any one-off links the user deliberately pinned. Do **not** invent a relation to fill the row — when nothing is truly related, the correct Related row is no row (or an empty one).
**Why:** a forced relation is noise; an honest empty is information. The table is a switchboard, not a quota to fill.

### RULE R-dispatch-table-06 — Pure link table; minimal annotation (stated)
A dispatch table is the **distilled set of jump-destinations**, not an explanation of them. No meta-discussion of what a link *means* belongs in a cell. At most **one or two words in parentheses** as an adjective — and **prefer none**. A link's meaning belongs on the linked page itself — its top line (H1 + first sentence) and its `description` frontmatter — not in the table that points at it.
**Why:** the table's value is the distilled essence of *where you can jump*; prose about each destination dilutes that and duplicates what the destination already says about itself.

### RULE R-dispatch-table-07 — Every dispatch table ends with a catch-all marker (checked)
Every dispatch table's **last row is a catch-all auto-enumeration marker**, so no document sitting in the folder can be hidden from the table: **`...`** (compact — the default; one cell that surfaces anything uncovered) or **`| --- | |`** (full auto-list — each uncovered/new doc as its own row, for list containers). Applies to **every** dispatch table, not just list containers — a masthead gets `...` too, so a stray doc dropped in the anchor's folder still shows.
**Check pattern:** the table's final row is `...`, `| --- | |`, or a trailing `+`-group row.
**Why:** the dispatch table must be an honest index of its folder — a catch-all guarantees stray or newly-added docs surface instead of silently disappearing.

# BRIEF

- **This file is the spec for the Dispatch Table facet** — the prescriptive rules for the top-of-file table convention used across anchor and facet pages. Edit here only to refine the convention itself.
- **NOT a catalog of pages that use dispatch tables** — don't pile worked-example links here beyond a small representative set; per-page application of the convention belongs in those pages' own files or in [[FCT Facets]] / trait specs.
- **Inclusion test** — content belongs on this page if it is a *rule* about dispatch-table shape (row order, cell format, breadcrumb syntax, escape conventions, the `Related` row, the `(See …)` variant). Anything about *how a specific anchor uses* its dispatch table goes in that anchor's docs.
- **Two surface forms coexist** — full dispatch table (under H1, breadcrumb row + category rows) and the `(See …)` line variant for files without a dispatch table. Keep both spec'd in lockstep; don't let one drift.
- **Load-bearing constraints** — the pipe-escape rule for wiki-links inside cells (`[[Target\|Display]]`), the breadcrumb cell shape (`→ [[kmr]] → … → [Name](hook://...)`), and the `Related`-row convention (Brief first, comma-separated thereafter) are downstream-cited from many places; changing them requires a vault-wide sweep.
- **Sibling-discipline boundary** — TOC generation is governed by [[Anchor TOC Format]] (figure-space mechanics, regeneration tooling), not here. Don't inline TOC rules into this spec; cross-reference instead.
- **Current state is skeleton** — the page is a stub pending a full prescriptive spec; new rules added here should be marked as such if not yet enforced vault-wide.
