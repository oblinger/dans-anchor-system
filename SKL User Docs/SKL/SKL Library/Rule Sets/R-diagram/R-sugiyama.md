# RULESET R-sugiyama
description:: Sugiyama-style graph-drawing aesthetics; quality rules below the hard-fail threshold.
include::

> [!info] Provenance
> **Kozo Sugiyama** (layered-drawing algorithm, 1981) — the canonical method for drawing directed graphs with minimized crossings + monotone layers. **Helen Purchase** (1997, 2002 empirical studies on graph-drawing aesthetics) — established edge crossings as the single largest factor in readability, ahead of grid-alignment / symmetry / bend count. **Gestalt principle of alignment** — readers infer relationships from co-aligned elements.

Edge-crossing minimization, bend budget, monotone flow, grid alignment — violations are warnings, not ship-blockers.

Factored from [[R-diagram]] 2026-06-09.

### R-sugiyama-01 — Minimize edge crossings (sampled)

The crossing count is at or below the minimum achievable for this graph (or within a small budget — say, ≤2 crossings for graphs with ≤10 nodes).

**Check pattern:** brute-force count edge-edge intersections; compare against the graph's known minimum crossing number (computable for small graphs) or a heuristic budget.

**Why:** Purchase (1997, 2002): edge crossings are empirically the single largest factor in graph readability — more impactful than aesthetics like grid-alignment or symmetry.

### R-sugiyama-02 — Bend budget (≤2 bends per edge, soft) (sampled)

No edge has more than two right-angle bends, and the average bend count across edges is at or below 1.

**Check pattern:** for each `<path>` edge, count direction changes. Aggregate average across edges.

**Why:** Sugiyama-style layouts emphasize edge-bend minimization as a readability heuristic; reading a one-bend or two-bend edge is fast, three-bend is slow.

### R-sugiyama-03 — Monotone flow direction (stated)

The dominant edge direction is consistent (left-to-right OR top-to-bottom). Counter-flow edges (right-to-left when L→R is dominant) are minimized and only used for back-edges (e.g., feedback loops).

**Check pattern:** compute the dominant axis from edge vectors; verify ≥80% of edges align with it.

**Why:** Sugiyama's layered drawing algorithm enforces this; without it, the reader can't establish a flow direction and the diagram reads as a tangle.

### R-sugiyama-04 — Grid alignment (sampled)

Box X-coordinates and Y-coordinates cluster onto a small set of "column" and "row" grid lines; outlier positions are intentional.

**Check pattern:** for each box, compute its centroid; cluster centroids into bands (along X and Y separately); verify the number of distinct bands is ≤ ceil(sqrt(boxes)) + 1.

**Why:** Gestalt principle of alignment — readers infer relationships from co-aligned elements. A grid makes the diagram parseable at a glance.
