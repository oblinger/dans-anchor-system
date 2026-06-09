# RULESET R-tufte-data-ink
description:: Tufte's data-ink discipline; every visual element carries information.
include::

Decoration competes with content for attention; in a diagram (which is dense with meaning) that competition is always lost. Sibling box-sizing consistency + no chartjunk (no drop shadows on every box, no gradient fills for fun, no decorative borders). Source: Tufte, *The Visual Display of Quantitative Information*.

Factored from [[R-diagram]] 2026-06-09.

### R-tufte-data-ink-01 — Sibling box-sizing consistency (sampled)

Boxes in the same role (e.g., all "subsystem" boxes) have the same width and height within 20%.

**Check pattern:** assume same-color or same-role boxes are siblings; check width and height variance ≤ 0.2 × mean.

**Why:** size variation that doesn't encode meaning is chartjunk (Tufte). Either size means something or it should be constant.

### R-tufte-data-ink-02 — Chartjunk budget (stated)

The diagram contains no decorative elements that don't carry information. No drop shadows on every box, no gradient fills for fun, no decorative borders.

**Check pattern:** manual review against Tufte's data-ink ratio principle. Future: detect gradients, shadows, and 3D effects; flag for review.

**Why:** Tufte. Decoration competes with content for attention; in a diagram (which is dense with meaning) that competition is always lost.
