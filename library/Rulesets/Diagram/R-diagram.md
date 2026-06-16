# RULESET R-diagram
include:: [[R-diagram-geometry]], [[R-sugiyama]], [[R-c4]], [[R-wcag-contrast]], [[R-bringhurst-typography]], [[R-tufte-data-ink]], [[R-svg-hygiene]]
description:: Umbrella for hand-authored figure validation; composes 7 methodology sub-sets, 22 rules total.

Hand-authored figures (architecture, flow, sequence, mockup diagrams) ship clean under a structural-correctness-first discipline: the diagram doesn't ship until the rule-checker emits zero errors. Adopting R-diagram pulls all 22 rules via the sub-sets composed in `include::` above; cherry-pick an individual sub-set for finer control. R-diagram has no rules of its own.

Factored 2026-06-09 from a monolithic 22-rule R-diagram set, per F132 Phase 1. Each sub-set carries its own provenance callout in its file. Reorganized 2026-06-16 (F132 Q5=B): the 5 cross-cutting methodology sub-sets moved into per-domain sibling folders (`Graph/`, `Structural/`, `Accessibility/`, `Typography/`, `Visualization/`, `SVG/`); the umbrella and `R-c4` stay in `Diagram/`. The `include::` above is unchanged — it resolves by wiki-link basename regardless of folder.

## Diagram rulesets

| Ruleset | Rules | What it covers |
| --- | --- | --- |
| [[R-diagram-geometry]] | 6 | Hard-fail geometric correctness — overlap, floating endpoints, tunneling, text overflow, label-target ambiguity, label-label collision. A violation means *broken*, not stylistically off. |
| [[R-sugiyama]] | 4 | Graph-drawing aesthetics — edge-crossing minimization, bend budget, monotone flow direction, grid alignment. Below the hard-fail threshold; violations are warnings. |
| [[R-c4]] | 4 | Semantic conventions — every arrow labeled, title or legend present, meaningful box names, one meaning per visual variable. Makes the diagram *parseable* to a first-time reader. |
| [[R-wcag-contrast]] | 2 | Accessibility — text contrast ≥ 4.5:1, non-text UI ≥ 3:1, and color is never the sole communicator (B&W print + colorblind readers stay readable). |
| [[R-bringhurst-typography]] | 1 | Typographic discipline — font sizes quantized to a small set (title / body / label / caption; ≤ 4 sizes). |
| [[R-tufte-data-ink]] | 2 | Data-ink discipline — sibling box-sizing consistency + chartjunk budget. Every visual element carries information. |
| [[R-svg-hygiene]] | 3 | File-format hygiene — stable IDs on every element, no orphan `<defs>` entries, validates as XML. A malformed SVG isn't a diagram at all. |
| **Total** | **22** | |

## All 22 rules

| Rule | Description |
| --- | --- |
| [[R-diagram-geometry#R-diagram-geometry-01 — No box-on-box overlap (checked)\|R-diagram-geometry-01]] | No two opaque container elements have intersecting bounding boxes (containment is allowed; overlap is not). |
| [[R-diagram-geometry#R-diagram-geometry-02 — Edge endpoints anchor to box edges (checked)\|R-diagram-geometry-02]] | Every arrow / edge endpoint terminates on a container edge or marked port — no endpoints float in whitespace. |
| [[R-diagram-geometry#R-diagram-geometry-03 — No edge tunneling through unrelated boxes (checked)\|R-diagram-geometry-03]] | An edge from A to B does not pass through any third box C. |
| [[R-diagram-geometry#R-diagram-geometry-04 — Text fits inside its container (checked)\|R-diagram-geometry-04]] | Every `<text>` element associated with a container has its rendered bbox fully inside the container's bbox (≥ 4px padding). |
| [[R-diagram-geometry#R-diagram-geometry-05 — Labels are associated with what they label (sampled)\|R-diagram-geometry-05]] | Each label is disambiguated to exactly one target via proximity (nearest distance < 0.5× second-nearest), alignment, or a leader line. |
| [[R-diagram-geometry#R-diagram-geometry-06 — No label-label collision (checked)\|R-diagram-geometry-06]] | No two `<text>` elements have overlapping bounding boxes. |
| [[R-sugiyama#R-sugiyama-01 — Minimize edge crossings (sampled)\|R-sugiyama-01]] | Crossing count is at or below the minimum achievable (or within a small budget — ≤ 2 for graphs with ≤ 10 nodes). |
| [[R-sugiyama#R-sugiyama-02 — Bend budget (≤2 bends per edge, soft) (sampled)\|R-sugiyama-02]] | No edge has more than two right-angle bends; average bend count across edges ≤ 1. |
| [[R-sugiyama#R-sugiyama-03 — Monotone flow direction (stated)\|R-sugiyama-03]] | Dominant edge direction (L→R or T→B) is consistent across ≥ 80% of edges; counter-flow only for back-edges. |
| [[R-sugiyama#R-sugiyama-04 — Grid alignment (sampled)\|R-sugiyama-04]] | Box centroids cluster onto a small set of row + column grid lines; distinct bands ≤ ceil(sqrt(boxes)) + 1. |
| [[R-c4#R-c4-01 — Every arrow carries a label (sampled)\|R-c4-01]] | Every arrow has an associated `<text>` label within proximity (or sits in the explicit unlabeled-arrow exception list). |
| [[R-c4#R-c4-02 — Title or legend present (checked)\|R-c4-02]] | Every diagram has a title text element OR a labeled legend / key block. |
| [[R-c4#R-c4-03 — Boxes have meaningful names (stated)\|R-c4-03]] | Box labels are noun phrases from the system's vocabulary — no `Box1` / `Component A` / `Module` placeholders. |
| [[R-c4#R-c4-04 — One meaning per visual variable (stated)\|R-c4-04]] | A visual variable (color, shape, line-style) encodes exactly one semantic axis throughout the diagram. |
| [[R-wcag-contrast#R-wcag-contrast-01 — Contrast ≥ 4.5:1 for text, ≥ 3:1 for non-text UI (checked)\|R-wcag-contrast-01]] | Text contrast ≥ 4.5:1 against background; lines, arrows, borders ≥ 3:1. |
| [[R-wcag-contrast#R-wcag-contrast-02 — Color is not the sole communicator of meaning (stated)\|R-wcag-contrast-02]] | Every semantic distinction conveyed by color is also conveyed by a non-color channel (label, position, shape). |
| [[R-bringhurst-typography#R-bringhurst-typography-01 — Font sizes are quantized to a small set (sampled)\|R-bringhurst-typography-01]] | At most 4 distinct font sizes across the diagram (title / body / label / caption is the budget). |
| [[R-tufte-data-ink#R-tufte-data-ink-01 — Sibling box-sizing consistency (sampled)\|R-tufte-data-ink-01]] | Boxes in the same role have width and height within 20% of each other. |
| [[R-tufte-data-ink#R-tufte-data-ink-02 — Chartjunk budget (stated)\|R-tufte-data-ink-02]] | No decorative elements that don't carry information — no gratuitous shadows, gradients, or borders. |
| [[R-svg-hygiene#R-svg-hygiene-01 — Stable IDs on every element (sampled)\|R-svg-hygiene-01]] | Every interactive or stateful element has a meaningful `id` (e.g., `scheduler-box`, not `rect42`). |
| [[R-svg-hygiene#R-svg-hygiene-02 — No orphan `<defs>` entries (checked)\|R-svg-hygiene-02]] | Every `<marker>` / `<linearGradient>` / `<filter>` defined under `<defs>` is referenced by some rendered element. |
| [[R-svg-hygiene#R-svg-hygiene-03 — SVG validates as XML (checked)\|R-svg-hygiene-03]] | The file parses as well-formed XML under `xmllint --noout` — no warnings, exit 0. |

## See also

- [[viz-diagram]] — `/viz diagram` create + cleanup skill; the user-facing surface for these rules.
- [[Rulesets]] — parent catalog.
- [[FCT Ruleset]] — RULESET format spec.
- [[2026-06-08 diagram-auditing-methodologies]] — 20-source survey that seeded these rules.
- F132 Phase 1 — factoring landed 2026-06-09; per-domain reorganization landed 2026-06-16 (Q5=B).
