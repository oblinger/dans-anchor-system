# RULESET R-subs
where:: `file:{anchor}/**/* Subs/**, !**/DAS *.md`
description:: the `{slug} Subs/` subprojects zone — week-scale sub-efforts numbered from the anchor's F-mint
selector-note:: Spelled `* Subs/` rather than `{slug} Subs/` for the same reason as [[R-wp]]'s selector ([[TINK Backlog#^T164|T164]]): a folder zone is audited scoped on itself, where `{slug}` resolves to the zone's own folder name and would match nothing.

What `/audit` checks on an anchor's Subs zone. Cardinality: one zone per anchor, many subprojects within. Format of this set: [[DAS Ruleset]]. Facet spec: [[DAS Subs]]. All rules ship (stated) — the convention is one day old with one live instance ([[A2X Subs]]); checkers wait for a second instance to show which invariants actually bind.

### RULE R-subs-01 — `{slug} Subs/` lives at the anchor root with one index page (stated)

The Subs zone is `{slug} Subs/` at the anchor root — sibling of Design/Track/Log, never inside them — containing a single `{slug} Subs.md` index page plus per-subproject folders.

### RULE R-subs-02 — A subproject folder is `{SLUG}{NNN} - Name/` with a matching top page (stated)

Each subproject is a folder `{SLUG}{NNN} - Name/` (fused slug + zero-padded F-number, ASCII hyphen with a space each side) containing `{SLUG}{NNN} - Name.md` of the same name. The number comes from the anchor's ordinary `state define <anchor> Backlog F+` mint — never a separate registry.

### RULE R-subs-03 — Internal files carry the `{SLUG}{NNN}` prefix (stated)

Every file inside a subproject folder is prefixed `{SLUG}{NNN} ` (e.g. `A2X010 Vasu Tasks.md`), keeping names unambiguous vault-wide while visibly naming the parent universe.

### RULE R-subs-04 — The container folder carries no `.anchor`; a subproject's `.anchor` declares its own fused slug (stated)

`{slug} Subs/` itself is a zone of the parent anchor, never an anchor — no `.anchor` on the container. A subproject folder may carry one, and when it does the `slug:` is the subproject's own fused form (`slug: A2X010`), never the parent's — a duplicate parent slug makes anchor resolution ambiguous.

### RULE R-subs-05 — Every subproject has a live backlog row in the parent anchor (stated)

The F-row minted with the subproject is its tracking handle for life: `[Active]` while in flight, `[Done]` at retirement. A subproject folder whose F-row is missing from the parent's backlog is orphaned work.
