# RULESET R-proj
where:: `file:{anchor}/**/* Proj/**, {anchor}/**/* Subs/**, !**/DAS *.md`
description:: the `{slug} Proj/` subprojects zone — a dated reverse-chronological stream of project folders (renamed from Subs)
selector-note:: Spelled `* Proj/` rather than `{slug} Proj/` for the same reason as [[R-wp]]'s selector ([[Tink Backlog#^T522|T522]]): a folder zone is audited scoped on itself, where `{slug}` resolves to the zone's own folder name and would match nothing. The `* Subs/` glob keeps legacy pre-rename instances ([[A2X Subs]]) in audit scope.

What `/audit` checks on an anchor's Proj zone. Cardinality: one zone per anchor, many projects within. Format of this set: [[DAS Ruleset]]. Facet spec: [[DAS Proj]]. All rules (stated) — checkers wait for enough instances to show which invariants actually bind.

### RULE R-proj-01 — `{slug} Proj/` lives at the anchor root with one index page (stated)

The Proj zone is `{slug} Proj/` at the anchor root — sibling of Design/Track/Log, never inside them — containing a single `{slug} Proj.md` index page (reverse-chronological listing) plus per-project folders, and optionally a `{slug} Proj Prior/` archive. Legacy zones named `{slug} Subs/` remain valid and are never renamed.

### RULE R-proj-02 — A project folder is dated or minted, with a matching top page (stated)

Each project is a folder in one of two grammars: **dated** — `YYYY-MM-DD Name/` or `YYYY-MM Name/` (default; no mint; the index page is the registry) — or **minted** — `{SLUG}{NNN} - Name/` (fused slug + zero-padded F-number from `state define <anchor> Backlog F+`, ASCII hyphen with a space each side). Either way the folder contains a top page of the same name.

### RULE R-proj-03 — Minted projects' internal files carry the `{SLUG}{NNN}` prefix (stated)

Every file inside a **minted** project folder is prefixed `{SLUG}{NNN} ` (e.g. `A2X010 Vasu Tasks.md`). Dated projects carry no prefix requirement — the dated folder name scopes them.

### RULE R-proj-04 — The container folder carries no `.anchor`; a project's `.anchor` declares its own slug (stated)

`{slug} Proj/` itself is a zone of the parent anchor, never an anchor — no `.anchor` on the container. A project folder may carry one, and when it does the `slug:` is the project's own (for minted projects, the fused form `A2X010`), never the parent's — a duplicate parent slug makes anchor resolution ambiguous.

### RULE R-proj-05 — Every minted project has a live backlog row in the parent anchor (stated)

The F-row minted with a minted project is its tracking handle for life: `[Active]` while in flight, `[Done]` at retirement; a minted folder whose F-row is missing is orphaned work. Dated projects are exempt — their tracking surface is the index page and their own spine.

### RULE R-proj-06 — A project whose content lives remote declares `proj-home::` (stated)

If most or all of a project's working content lives in an external tool (Notion, Drive, a partner system), its spine page carries a `proj-home::` DataView inline field — in the body or masthead table, never frontmatter — linking the remote home. The local folder is then deliberately thin (spine + register + pointers), not incomplete. Remote-only projects — in the stream but with no local folder — are the violation this rule exists to name.
