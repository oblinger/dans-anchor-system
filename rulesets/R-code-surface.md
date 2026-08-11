# RULESET R-code-surface
include:: ~~[[R-module-doc]]~~
where:: `anchor`
description:: the code surface of an anchor — All Files tree + per-module docs, kept in correspondence

What `/audit` checks across the code surface of a `code`-trait anchor. The per-doc shape rules live in the included `R-module-doc`; the rules below are the **pairing** invariants between the source tree and its docs. Format of this set: [[DAS Ruleset]].

> **Not armed 2026-08-11 ([[TINK Backlog#^T212|T212]]) — blocked twice over.**
>
> **Its own selector is the [[R-git]] shape.** `where:: anchor` fires once per anchor, 1,395 times across the vault, for two rules whose subject is a *pairing* between `{slug} Files.md` and the module docs under `{slug} Dev Docs/` — a correspondence that exists in 14 anchors. Both rules read `(checked)` and carry **no `check::`**, so arming as written buys 2,790 agent judgments to ask 14 real questions.
>
> **And the set it includes cannot fire either.** [[R-module-doc]] is unsatisfiable in three independent ways, measured in its own header; a pairing ruleset whose doc-side half matches nothing has no pair to check. Both halves must land before either is worth arming, so this set waits on that one rather than being repaired ahead of it.

### RULE R-code-surface-01 — Every public-API source file resolves to a module doc (checked)

The All Files tree wiki-links each source file to its module doc, and each such link resolves to an existing `{slug} {ClassName}.md` under `{slug} Dev/`.

**Check pattern:** for every public-API source file in `{slug} Files.md`, its wiki-link target exists as a module doc.

**Why:** All Files and Module Doc are a pair — a link with no doc behind it is a dead end.

### RULE R-code-surface-02 — The Module Doc set mirrors the source tree (checked)

Every module doc corresponds to a real source module (no orphan docs), and every source directory with public API has its parallel `{slug} {dir}/` folder.

**Check pattern:** the doc tree under `{slug} Dev/` and the source tree are in mirror correspondence (per `R-module-doc-01`); flag docs with no source and source dirs with no doc folder.
