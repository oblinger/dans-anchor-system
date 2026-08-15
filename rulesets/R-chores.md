# RULESET R-chores
where:: `file:{anchor}/**/* Chores.md, !**/DAS *.md`
description:: the `{slug} Chores.md` sub-surface work file — flat list of items the user is neither aware of nor interested in
selector-note:: Spelled `* Chores.md` rather than `{slug} Chores.md` for the same reason as [[R-subs]]'s selector ([[TINK Backlog#^T164|T164]]): when audited scoped on its own containing folder, `{slug}` can resolve to the wrong segment and match nothing.

What `/audit` checks on an anchor's Chores file. Cardinality: one per anchor, elective, present-or-empty. Format of this set: [[DAS Ruleset]]. Facet spec: [[DAS Chores]]. All rules ship (stated) — the facet is one day old with one live instance; checkers wait for a population.

### RULE R-chores-01 — `{slug} Chores.md` lives with the backlog (stated)

Inside the folder-form backlog (`{slug} Track/{slug} Backlog/{slug} Chores.md`) once the anchor has one; the interim flat home is `{slug} Track/{slug} Chores.md`. Nowhere else — chores are backlog-shaped work and live with the backlog's files.

### RULE R-chores-02 — One H1, one flat bulleted list (stated)

The file is an H1 plus a single flat bulleted list. Each bullet is a self-contained instruction executable by any agent cold. No sub-bullet trees, no status brackets, no Q-numbers, no horizon H2s — an item needing any of those is not a chore.

### RULE R-chores-03 — No user-facing content (stated)

Nothing in the file asks the user anything or awaits a user judgment: no questions, no `Verify`-style checks, no options-and-recommendation blocks. An item that needs the user is promoted to a doc-hosted question via `state` and deleted here in the same pass.

### RULE R-chores-04 — Chores never render to user surfaces (stated)

No renderer or skill lists chores in `queries.md`, `Q.md`, status banners, or user-directed summaries. The audience property — the human unaware and uninterested — is the facet's definition, and surfacing an item breaks it by construction.
