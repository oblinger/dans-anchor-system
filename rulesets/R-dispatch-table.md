# RULESET R-dispatch-table
include::
where:: `file: {anchor}/**/*.md`
description:: The shape every dispatch table must take — masthead-placement law, member-zone mechanics, and pipe-escaped cell links.

### RULE R-dispatch-table-01 — Masthead rows appear in a fixed order (checked)
After the breadcrumb identity row, the masthead's optional rows appear in this **fixed order**, each present **only if it applies**: **Related** → **type row** (skill / discipline / facet leaf anchors only) → **Design** → **Track** → **User Docs** → **Dev Docs**. There is **no generic `Anchor` row** (superseded — everything is an anchor; the label conveyed nothing). Every row after the breadcrumb has the **same shape**: its **left cell is a link *down* to that sub-area** (the row's name), and its **right cell enumerates that sub-area's key parts** for one-click access. Per-row rules: R-08 (Related) … R-12 (Dev Docs). Full model: § What it is.
**Check pattern:** rows, where present, occur in the order Related, [type], Design, Track, User Docs, Dev Docs; no row labeled `Anchor`.
**Why:** a stable left-to-top-to-bottom reading order makes every anchor page scan the same way; the row *names* the sub-area and the cell jumps you into it.

### RULE R-dispatch-table-08 — Related is the first optional row and absorbs external links (checked)
The first optional row is **Related**. It carries links to genuinely-related anchors / siblings **and external resources** — the code repo, the published project page, a docs site — i.e. anything related that is **not already in the breadcrumb path**. There is **no separate `External` row**; repo / site URLs live in **Related**. **An anchor that has a code repo (a `code:` key in its `.anchor`) carries a `[code](hook://f/{slug}?facet=code)` link in Related** — the hook `f/` (finder) verb opens the anchor's code folder in Finder (`{slug}` = the anchor's slug). Optional and never manufactured (per R-05).
**Check pattern:** no masthead row is labeled `External`; if a `Related` row exists it precedes every sub-area row.
**Why:** "what else is near this?" is answered once, up top, before the reader descends into the anchor's own contents; one row for all not-in-breadcrumb links keeps the switchboard small.

### RULE R-dispatch-table-13 — Code anchors carry a `[code]` link in Related (checked)
Every anchor whose `.anchor` declares a `code:` key (equivalently, carries the `code` trait) includes, in its **Related** row, a markdown link **`[code](hook://f/{slug}?facet=code)`** where `{slug}` is the anchor's slug. The `f/` (finder) hook verb opens the anchor's code folder; one-click reach from the masthead to the code, with no hardcoded path. The link text is exactly `code`.
**Check pattern:** for every dispatch-table page whose anchor has a `code:` key, the Related row contains a `[code](hook://f/<slug>?facet=code)` link.
**Why:** the code is the point of a code anchor; a uniform, path-free `[code]` link makes it reachable from every such masthead and stays correct even if the repo moves (resolution is via the `.anchor` `code:` key, not a hardcoded path).

### RULE R-dispatch-table-09 — Design row links the sub-anchor and enumerates the design parts (checked)
check:: dispatch_area_row Design
When the anchor has a Design sub-area, the masthead carries a **Design** row whose **left cell is `[[{X} Design\|Design]]`** (a link down to the design sub-anchor) and whose **right cell lists the design's key parts** that exist — PRD, Architecture, Decisions, UX Design, Roadmap, Stories. It is **never a bare self-link** (`| Design | [[{X} Design]] |` with nothing else is wrong).
**Check pattern:** a row whose left cell links to `{X} Design` and whose right cell holds ≥1 design-part link, whenever a `{X} Design` folder exists.
**Why:** the design row is the entry into the design flow; surfacing its parts gives one-click reach to the architecture and the rest without opening the sub-page first.

### RULE R-dispatch-table-10 — Track row links the sub-anchor and enumerates the tracking items (checked)
check:: dispatch_area_row Track
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
Every dispatch table **ends with a catch-all auto-enumeration zone**, so no document sitting in the folder can be hidden from the table: **`...`** (compact — the default; one cell that surfaces anything uncovered) or **`| --- | |`** (full auto-list — each uncovered/new doc as its own row, for list containers). The other HA v2 electric separators also satisfy the rule where their ordering fits the content: **`^^^`** (reverse-alpha auto-list — dated/newest-first containers like Features folders) and **`+++`** (alpha with grandchildren). Applies to **every** dispatch table, not just list containers — a masthead gets `...` too, so a stray doc dropped in the anchor's folder still shows.
**Check pattern:** the table's final row is `...`, `| --- | |`, a trailing `+`-group row, or an electric separator (`---`/`^^^`/`+++`) followed only by its auto-emitted member rows.
**Why:** the dispatch table must be an honest index of its folder — a catch-all guarantees stray or newly-added docs surface instead of silently disappearing.
