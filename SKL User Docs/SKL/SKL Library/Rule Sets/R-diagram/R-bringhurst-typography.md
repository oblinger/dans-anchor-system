# RULESET R-bringhurst-typography
description:: Bringhurst-style typographic discipline for diagrams.
include::

> [!info] Provenance
> **Robert Bringhurst**, *The Elements of Typographic Style* (1992; the modern canonical reference for typographic craft). Key principle for diagrams: restricted, well-chosen typographic scales mark professional work; many small variations in font size are amateurish, few well-chosen sizes are professional.

Currently one rule (font-size quantization); will accumulate more as typographic-quality auditing extends to typeface mixing, baseline-grid alignment, etc.

Factored from [[R-diagram]] 2026-06-09.

### R-bringhurst-typography-01 — Font sizes are quantized to a small set (sampled)

The diagram uses at most 4 distinct font sizes (e.g., 14 / 16 / 20 / 24). Title, body, label, and caption — that's the budget.

**Check pattern:** enumerate font-size attributes; fail if more than 4 distinct values.

**Why:** Bringhurst — typographic scale is a quality marker. Many small variations in size is amateurish; few well-chosen sizes is professional.
