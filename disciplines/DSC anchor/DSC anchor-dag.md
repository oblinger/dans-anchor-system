---
name: anchor-dag
description: >
  Discipline — a GLOBAL (corpus-level) one, distinct from the per-artifact
  authoring disciplines. The whole vault is one connected DAG of anchors,
  navigable up (breadcrumbs), down (dispatch tables / Member zones), and sideways
  (Related rows). States the navigability invariant (reachable / down-complete /
  up-complete / adjacency-served) and the verify-and-complete procedure: build the
  graph from disk, walk it, diff against the invariant, surface a graduated-
  confidence report (mechanical fixes applied, semantic placements asked), loop
  until clean. Per-anchor table repair delegates to /audit dispatch. NOT a facet
  (per-doc) or trait (per-anchor) — it is a property of the whole corpus.
tools: Read
user_invocable: false
---

# Anchor DAG

A complete anchoring methodology produces a **graph**, so it must include the check that the graph **coheres**. `anchor-dag` is that check: the whole corpus is one connected DAG of anchors, and from wherever you land you can always reach what you're looking for — even without knowing its name, by climbing or descending from a nearby concept. This discipline states the invariant and the procedure to verify and complete it.

## A new *kind* of discipline — global, not per-artifact

The other disciplines ([[DSC markdown]], [[DSC progressive-disclosure]], [[DSC file-association]], [[DSC granularity]]) are **per-artifact authoring** rules — applied *while you write one doc or anchor*. `anchor-dag` is a **global / corpus-level invariant** — a property of *all the anchors together*, verified by **walking the whole graph**, not by authoring any single thing. It opens a second shelf for siblings of the same shape (candidates: *every-slug-resolves*, *no-orphan-files*, *Atlas-covers-every-named-thing*) — each "a property of the whole corpus, verified by a walk." Cite this discipline when defining or running a corpus-wide integrity check; cite the authoring disciplines when shaping one artifact.

## The invariant (precise)

Treat every `.anchor` folder as a **node**. Three kinds of **edge** connect them:

| Edge | Direction | Mechanism | Owns |
|---|---|---|---|
| **Parent link** | up | the breadcrumb row (`→ … → [This]`) | [[FCT Anchor Page]] |
| **Child links** | down | the dispatch table / Member zone | [[FCT Anchor Page]] + [[FCT Dispatch Table]] |
| **Adjacency links** | sideways | the `Related` row | [[FCT Dispatch Table]] |

The corpus is **navigability-complete** when:

1. **Reachable** — every anchor is reachable from a root by descending dispatch links. No orphans.
2. **Down-complete** — every anchor's on-disk children (sub-anchors + key docs) appear as down-links in its dispatch. No invisible children.
3. **Up-complete** — every anchor page's breadcrumb parent points at the anchor that actually lists it as a child. Up and down agree.
4. **Adjacency-served** — concepts a reader might confuse or pivot between carry `Related` links to each other, so landing on a neighbor still reaches the target.

(1)–(3) are mechanical; (4) is semantic judgment.

## The verify-and-complete procedure

Do not navigate by reading prose — build the graph from disk and compare it to the invariant.

### 1. Build the actual graph
- Enumerate every `.anchor` folder (the nodes).
- For each, parse its anchor page: extract the **breadcrumb parent** (up-edge), the **dispatch-table targets** (down-edges), and the **Related targets** (adjacency-edges).
- Cross-check against the **machine graph** (`.anchor` slug + edges, the host name-resolver) — the `.anchor` edges are ground truth for what *should* connect.

### 2. Walk and diff
- **Descend from the roots**, marking every anchor reached. Unmarked anchors are **orphans**.
- For each anchor, diff on-disk children against dispatch down-links → **missing down-links**.
- For each anchor, check the breadcrumb parent actually lists it → **missing / wrong up-links**.
- Flag anchors whose neighbors (siblings, same-topic anchors) lack a `Related` cross-link → **weak adjacency** (low-confidence, semantic).

### 3. Surface a graduated-confidence report (iterate with the user)

Do **not** silently rewrite the structure. Surface two tables; the user iterates:

- **Table A — high-confidence updates (apply on confirm).** Mechanical, unambiguous: child exists but isn't in the parent's dispatch → add the down-link; breadcrumb missing/wrong → fix to the listing parent.
- **Table B — low-confidence questions (user judgment).** Semantic: orphan placement ("where should this attach? candidates …"), suggested `Related` adjacencies.

The user answers Table B with shorthand (`Baz → Topic`, `X-Y: yes`); apply Table A + answered Table B rows, then **re-scan**, looping until navigability-complete (same loop-until-clean discipline as `/audit q`). Each pass shrinks Table B.

### 4. Per-anchor table repair delegates to /audit dispatch

When a node needs its dispatch table built or fixed (add missing down-links, choose Masthead vs Member zone, member-list vs member-groups, apply the grouping threshold), call **[[audit-dispatch|/audit dispatch]]** — the per-node worker. This discipline owns the **whole-graph walk**; `/audit dispatch` owns **one table's shape**. A single table can't know whether the *corpus* is connected — only the walk can.

## Applying it to a specific vault

This discipline is the reusable check. A specific vault declares its own **application**: which roots to descend from, who runs the walk, and on what cadence. (For this author's vault, that application lives at `[[SYS Anchor DAG]]` — SYS owns the walk over `~/ob/kmr`.) Ship the discipline; each vault writes the thin application.

## Related

- [[FCT Dispatch Table]] — the down + sideways edges (the table form).
- [[FCT Anchor Page]] — the breadcrumb (up edge) + dispatch hosting.
- [[audit-dispatch|/audit dispatch]] — the per-anchor table-repair worker the walk calls.
- [[DSC progressive-disclosure]] / [[DSC file-association]] / [[DSC granularity]] / [[DSC markdown]] — the per-artifact authoring disciplines (this is their corpus-level sibling).
