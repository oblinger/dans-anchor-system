# RULESET R-pcb-drc-structural
description:: PCB-design-rule-check-inspired structural correctness for hand-authored diagrams. Hard-fail rules — a diagram that violates these is broken, not just stylistically suboptimal. Source: Eichelberger UML-readability study + Sourcetrail review criteria + Imhof cartographic labeling. Factored from [[R-diagram]] 2026-06-09.
include::

### R-pcb-drc-structural-01 — No box-on-box overlap (checked)

No two opaque container elements (`<rect>`, `<ellipse>`, `<polygon>` acting as boxes) have intersecting bounding boxes, except when one is a strict parent container of the other (containment is allowed; overlap is not).

**Check pattern:** parse the SVG; for every pair of container elements (X, Y), compute `bbox(X) ∩ bbox(Y)`. Fail if the intersection is non-empty AND neither is fully contained in the other.

**Why:** Eichelberger's UML-readability study identifies element overlap as a top readability killer. Overlap also breaks the visual hierarchy a reader uses to parse the diagram.

### R-pcb-drc-structural-02 — Edge endpoints anchor to box edges (checked)

Every arrow / edge endpoint terminates on the visible edge of a container or attaches to a marked port; no edge endpoints float in whitespace adjacent to (but not touching) their target.

**Check pattern:** for every `<line>`/`<path>` with `marker-end` (arrow), verify each endpoint coordinate is within 2px of the bounding box edge of some container element (or matches a named anchor point).

**Why:** floating endpoints look like rendering bugs and force the reader to guess which box the arrow connects to.

### R-pcb-drc-structural-03 — No edge tunneling through unrelated boxes (checked)

An edge from A to B does not pass through any box C that is neither A nor B. Edges may pass through arrow labels and other edges; only box-tunneling is forbidden.

**Check pattern:** for every edge segment, intersect with every container bbox. Fail if any container that is not the edge's start or end is intersected.

**Why:** Sourcetrail's system-diagram checklist and the C4 review criteria both flag edge tunneling as a primary clarity defect.

### R-pcb-drc-structural-04 — Text fits inside its container (checked)

Every `<text>` element nominally associated with a container has its rendered bounding box fully inside the container's bounding box (with at least 4px padding on each side as a soft check).

**Check pattern:** for every `<text>` with a `containerId` (or visually associated, e.g., same group), compute rendered text bbox; verify `text.bbox ⊆ container.bbox` (minus padding).

**Why:** text overflow is one of the most common rendering bugs in hand-authored SVG and an instant clarity-killer.

### R-pcb-drc-structural-05 — Labels are associated with what they label (sampled)

Every label (`<text>` near an arrow or box but not the box's primary title) is visually disambiguated as belonging to exactly one target — either by proximity (closer to that target than any other), by alignment, or by a leader line.

**Check pattern:** for each candidate label, identify its nearest-neighbor element by Euclidean distance; verify uniqueness of the "nearest" answer and verify proximity ratio (nearest distance < 0.5 × second-nearest distance).

**Why:** automatic-label-placement literature (Imhof, cartographic labeling) makes proximity-disambiguation the foundational rule. Otherwise, the reader plays a guessing game.

### R-pcb-drc-structural-06 — No label-label collision (checked)

No two `<text>` elements have overlapping bounding boxes.

**Check pattern:** pair-test all `<text>` bboxes for intersection.

**Why:** Eichelberger's empirical study: label-label overlap is the *#1* readability killer for class-style diagrams, ahead of edge crossings.
