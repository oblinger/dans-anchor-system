---
description: "code facets — the actual source files of a repo and their per-module documentation"
---

# Code
The code facets — a repo's actual source files and the per-module docs they link into.

| -[[FCT Code]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Code](hook://p/FCT%20Code)<br>: code facets — source files and their module docs |
| --- | --- |
| Facets | [[FCT All Files\|All Files]],  [[FCT Module Doc\|Module Doc]],   |

These two facets are a pair: **All Files** is the repo's complete source tree with every file wiki-linked to its module doc; **Module Doc** is the per-module documentation those links resolve to. Together they are the *code* surface of an anchor — distinct from the *anchor structure* facets ([[FCT Anchor]]) and from the *design* of that structure ([[FCT Files Architecture]]).

# RULESET R-code-surface
include:: [[R-module-doc]]
where:: anchor
description:: the code surface of an anchor — All Files tree + per-module docs, kept in correspondence

What `/audit` checks across the code surface of a `code`-trait anchor. The per-doc shape rules live in the included `R-module-doc`; the rules below are the **pairing** invariants between the source tree and its docs. Format of this set: [[FCT Ruleset]].

### RULE R-code-surface-01 — Every public-API source file resolves to a module doc (checked)

The All Files tree wiki-links each source file to its module doc, and each such link resolves to an existing `{NAME} {ClassName}.md` under `{NAME} Dev/`.

**Check pattern:** for every public-API source file in `{NAME} Files.md`, its wiki-link target exists as a module doc.

**Why:** All Files and Module Doc are a pair — a link with no doc behind it is a dead end.

### RULE R-code-surface-02 — The Module Doc set mirrors the source tree (checked)

Every module doc corresponds to a real source module (no orphan docs), and every source directory with public API has its parallel `{NAME} {dir}/` folder.

**Check pattern:** the doc tree under `{NAME} Dev/` and the source tree are in mirror correspondence (per `R-module-doc-01`); flag docs with no source and source dirs with no doc folder.
