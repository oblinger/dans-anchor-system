# RULESET R-anchor-tree
include::
where:: `file: **/DAS Anchor Tree.md`
description:: Rules governing the DAS Anchor Tree facet spec — the annotated master file tree of a DAS anchor. Covers content integrity, naming conventions, tree rendering, and cross-reference sync.

### RULE R-anchor-tree-01 — Every named element is wiki-linked to its facet spec (checked)
Every named file or folder placeholder in the tree (e.g. `{slug} Backlog.md`, `CLAUDE.md`) carries a `[[DAS <Name>]]` wiki-link to the governing facet spec. Inline aliases to the on-disk filename are permitted (`~~[[DAS Anchor Page|{slug}.md]]~~`).
**Check pattern:** no unlinked placeholder name in the tree body (scan for `{slug} <Word>.md` lines lacking `[[`).
**Tier:** checked

### RULE R-anchor-tree-02 — Box-drawing characters and monospace cssclass are preserved (checked)
The tree uses Unicode box-drawing characters (`├──`, `│`, `└──`). The frontmatter must carry `cssclasses: monospace` (or a list including `monospace`) so the tree renders correctly in Obsidian.
**Check pattern:** frontmatter contains `cssclasses` with `monospace`; tree lines contain `├──` or `└──`.
**Tier:** checked

### RULE R-anchor-tree-03 — Two trees are kept separate by the Optional divider (sampled)
The anchor folder tree (top) and the optional Code Repository tree (bottom) are separated by a `─── Optional … ───` divider line. No code-repo paths appear above the divider; no anchor-tree placeholders appear below it.
**Check pattern:** the divider line `─── Optional` is present; `{repo}/` section is below it.
**Tier:** sampled

### RULE R-anchor-tree-04 — This tree is the self-canonical anchor file tree (stated)
This file is the single canonical anchor file tree; named elements are kept in sync with their governing `DAS <Name>.md` facet specs (via the wiki-links in the tree), not with any external dispatch table. (The legacy CAB-era three-way sync with `CAB Base.md` / `SKILL.md` / `CAB Rules.md` is retired — CAB Base is superseded by this file.)
**Check pattern:** stated principle; agent verifies each named element resolves to a live facet spec on tree edits.
**Tier:** stated
