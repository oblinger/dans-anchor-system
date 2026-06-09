# RULESET R-wcag-contrast
description:: WCAG-2.1-derived accessibility rules for diagrams — contrast ratios and colorblind-safe communication. Diagrams projected on screens or printed B&W must remain readable. Source: WCAG 2.1 AA. Factored from [[R-diagram]] 2026-06-09.
include::

### R-wcag-contrast-01 — Contrast ≥ 4.5:1 for text, ≥ 3:1 for non-text UI (checked)

Every `<text>` element has a contrast ratio of at least 4.5:1 against its background (the box fill it sits on, or canvas if none). Lines, arrows, and borders have ≥ 3:1.

**Check pattern:** compute luminance for each `<text>` fill vs. its background fill; compute contrast ratio per WCAG formula. Same for stroke colors.

**Why:** WCAG 2.1 AA contrast requirements. Not just an accessibility nicety — diagrams projected on screens or printed in B&W must remain readable.

### R-wcag-contrast-02 — Color is not the sole communicator of meaning (stated)

For every semantic distinction conveyed by color (e.g., box fill color = role), the same distinction is also conveyed by a non-color channel (label text, position, shape, or a redundant legend).

**Check pattern:** manual review. Future: extract color clusters; verify each cluster has a redundant identifier (text label including the role name, distinct shape, etc.).

**Why:** WCAG 1.4.1; colorblind readers and B&W printouts depend on this.
