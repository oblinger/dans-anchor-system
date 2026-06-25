# RULESET R-svg-jiggle
include::
where:: {ANCHOR}/**/*.svg
description:: Geometry-aware layout-repair ("jiggle") for hand-authored SVG diagrams — clear label-over-box overlaps with the cheapest topological move (slide / flip), governed by a three-tier severity order.

> [!info] Provenance
> The *repair* counterpart to [[R-diagram-geometry]]'s *detection*. Where R-diagram-geometry reports geometric faults, R-svg-jiggle **fixes** them — modelled on the audit fix-by-default engine ([[F161 — Rule-driven audit engine]] / F166): each move is a rule with a `check::` (overlap predicate) and a `fix::` (the move). Runs over the geometry primitive layer in `skills/viz/svg-jiggle.py` (SVG bbox reader + intersection test + edge association). Captured 2026-06-25 per [[F186 — SVG Jiggle — geometry-aware layout-repair ruleset for the viz svg track]].

A diagram is **repaired** when the loop reports zero hard overlaps. This is not a layout engine — it is the repair pass that runs *after* the generator: detect → apply the cheapest move that clears each hard overlap without creating a new one → repeat until clean or the iteration budget is hit.

**Representation boundary.** This ruleset owns the **SVG** track, where the agent controls every coordinate so moves rewrite `<text>` x/y directly. The sibling **D2 Jiggle** (deferred) expresses the same abstract moves as ELK directives. Cross-translation lives in the shared abstract-move vocabulary, not in either ruleset — so this is **not** a CAB-conformance facet and is deliberately absent from [[R-facet]].

### RULE R-svg-jiggle-01 — Severity order governs every move (governing)
check:: svg_hard_overlap

Every trade-off is decided by three tiers, cheapest-first:

- **Hard-forbidden** — `label ∩ box` (a `<text>` that intersects a `<rect>` box but is *not* a node label) and `box ∩ box` (two boxes overlapping, neither containing the other). The loop **must** clear every hard overlap.
- **Soft (acceptable only if nothing cheaper clears the hard one)** — `label ∩ edge-line` / `label ∩ arc`. A label resting on its own arrow is fine.
- **Free** — whitespace. The target state for every moved label.

A move that trades a hard overlap for a soft one is a **win**; the reverse is forbidden. A `<text>` that is **≥ 70 % contained in a single box** is that box's **node label** — EXEMPT, never moved (the box title). A `<text>` fully outside all boxes (diagram title, legend, axis band) is also exempt. Only a label that *spills across a box boundary* (intersects a box but is < 70 % inside it) is the hard overlap to fix.

**Check pattern:** parse the SVG into geometry — `<text>` labels (x/y + inherited `font-size`/`text-anchor` → estimated bbox: `width ≈ len·font_size·0.58`, `top ≈ y − 0.8·font_size`, `height ≈ font_size`), `<rect>` boxes (a *box* is a stroked rect that is not the full-canvas background; no-stroke rects — background fills, white label halos — are not boxes), and edges (`<line>`, `<path>` sampled to a polyline; `<defs>`/`<marker>` skipped). For each label compute max single-box coverage; ≥ 0.70 → node (exempt). Otherwise an intersection with overlap ≥ 5 px in **both** axes against any box → **hard**. Count hard label-over-box + box-over-box incidents; the repaired count must be 0.

**Why:** the severity order *is* the cost function. Without it, a repair pass has no principled basis to choose between candidate moves and can "fix" a hard overlap by creating an equally bad one. Hard overlaps (label-over-box, box-over-box) are the readability killers; soft overlaps (label on its own arrow) read fine.

### RULE R-svg-jiggle-02 — slide-label-along-edge (free)
check:: svg_hard_overlap
fix:: slide_label_along_edge

A hard label may travel **along the direction of its associated edge** (plus a modest perpendicular offset) and still read as belonging to that edge. The first free move tried.

**Check pattern:** the label is hard per R-svg-jiggle-01 (`label ∩ box`, < 70 % contained). Associate it with its nearest edge — minimum distance from the label's center to any edge segment.

**fix::** search candidate positions = `center + t·d + s·n` (where `d` is the unit edge direction at the nearest segment and `n` its perpendicular), over parallel offsets `t` (bounded to ≈ half the edge length + pad, so the label stays within the edge's span) and perpendicular offsets `s`. Accept the **minimum-displacement** candidate that (a) has **zero** box intersection, (b) stays inside the canvas, and (c) keeps the label's center within ~110 px of its edge. Rewrite only the `<text>` x/y (and any identical twin — e.g. a halo + fill pair — by the same delta).

**Why:** sliding a label along its arrow is the cheapest repair — zero cascade (no box moves), and the label remains visually bound to the edge it annotates. Almost every label-over-box case on a clean diagram is a label dropped into a box that has open whitespace a short slide away (typically just above/below the arrow).

### RULE R-svg-jiggle-03 — flip-label-across-edge (free)
check:: svg_hard_overlap
fix:: flip_label_across_edge

When no slide clears the label, mirror it to the **empty side** of its edge — same perpendicular distance, opposite side. The second free move.

**Check pattern:** the label is hard per R-svg-jiggle-01 and `slide-label-along-edge` (R-svg-jiggle-02) found no clean position.

**fix::** reflect the label's center across the line of its associated edge segment (foot-of-perpendicular reflection); translate the `<text>` x/y by that delta (twins together). Accept only if the reflected position is clean (zero box intersection, inside canvas, within ~110 px of the edge); otherwise leave the label and report it **unresolved** — the signal that a cascading move (`nudge-box`, `space-rank`; deferred) is needed. Never fake the count.

**Why:** flip handles the case where one side of the edge is crowded but the mirror side is open — a label that overlaps a box below its arrow may sit cleanly above it. It is still free (no cascade). When both free moves fail, honesty about the residual is the correct output: a cascading move is a later phase, not a reason to under-count.

# BRIEF

**R-svg-jiggle** is the repair pass for hand-authored SVG diagrams: it clears **label-over-box** overlaps (the hard tier) by applying the cheapest topological move and repeating until clean. Detection lives in the geometry primitive layer (`skills/viz/svg-jiggle.py`); the three rules here are the policy.

- **R-svg-jiggle-01** — the **three severity tiers** (hard = label∩box / box∩box; soft = label∩edge; free = whitespace) govern every choice; node labels (≥ 70 % inside one box) and outside-all-boxes labels are exempt. Hard count must reach 0.
- **R-svg-jiggle-02** — **slide-label-along-edge**: translate the label parallel to its edge (+ modest perpendicular), pick the nearest clean spot within the edge's span. Tried first.
- **R-svg-jiggle-03** — **flip-label-across-edge**: mirror to the empty side of the edge. Tried second. If neither clears it, report the label **unresolved** (cascading move deferred) — never fake the count.

Cheapest-first: both moves are **free** (no box moves, no cascade). Box-nudging and rank-spacing are deferred until the free moves demonstrably fail to converge. This ruleset owns the **SVG** representation only; D2 Jiggle is the deferred sibling, sharing the abstract-move vocabulary, not these rules. It is a viz ruleset, **not** a CAB-conformance facet — not listed under [[R-facet]].

Run: `svg-jiggle.py <in.svg> [-o <out.svg>] [--max-iter 20] [--report]`. Prints `hard overlaps: before N → after M` + a per-move log; writes only the moved `<text>` x/y (rest of the file byte-identical).
