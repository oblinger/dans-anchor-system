# RULESET R-diagram
include:: [[R-diagram-geometry]], [[R-sugiyama]], [[R-c4]], [[R-wcag-contrast]], [[R-bringhurst-typography]], [[R-tufte-data-ink]], [[R-svg-hygiene]]
description:: Umbrella for hand-authored figure validation; composes 7 methodology sub-sets.

Hand-authored figures (architecture, flow, sequence, mockup diagrams) ship clean under a PCB-DRC-style discipline: the diagram doesn't ship until rule-checker emits zero errors. Adopting R-diagram pulls all 22 rules via the sub-sets composed in `include::` above; cherry-pick an individual sub-set for finer control.

Factored 2026-06-09 from a monolithic 22-rule R-diagram set, per F132 Phase 1.


> [!info] Composition
> R-diagram has no rules of its own. The 22 rules live in the 7 included sub-sets above. Each sub-set can be adopted independently when an anchor wants only that methodology's rules — e.g., a typography-focused doc might `include:: [[R-bringhurst-typography]], [[R-tufte-data-ink]]` without pulling structural-correctness rules.

## Rule count by sub-set

| Sub-set | Rules | Provenance |
| --- | --- | --- |
| [[R-diagram-geometry]] | 6 | Eichelberger UML-readability + Sourcetrail review + Imhof cartographic labeling |
| [[R-sugiyama]] | 4 | Purchase 1997/2002 + Sugiyama layered drawing + Gestalt alignment |
| [[R-c4]] | 4 | C4 model § Conventions + Bertin *Sémiologie graphique* |
| [[R-wcag-contrast]] | 2 | WCAG 2.1 AA |
| [[R-bringhurst-typography]] | 1 | Bringhurst, *Elements of Typographic Style* |
| [[R-tufte-data-ink]] | 2 | Tufte, *Visual Display of Quantitative Information* |
| [[R-svg-hygiene]] | 3 | File-format hygiene (XML validation, IDs, defs cleanup) |
| **Total** | **22** | (matches pre-factoring count — no rules lost) |

## Migration map (legacy R-diagram-NN → factored ID)

References to the legacy monolithic numbering can be looked up here. Each rule was renumbered to start at 01 in its new methodology sub-set; the body content is identical.

| Legacy | Factored | Body |
| --- | --- | --- |
| R-diagram-01 | [[R-diagram-geometry#R-diagram-geometry-01 — No box-on-box overlap (checked)\|R-diagram-geometry-01]] | No box-on-box overlap |
| R-diagram-02 | [[R-diagram-geometry#R-diagram-geometry-02 — Edge endpoints anchor to box edges (checked)\|R-diagram-geometry-02]] | Edge endpoints anchor to box edges |
| R-diagram-03 | [[R-diagram-geometry#R-diagram-geometry-03 — No edge tunneling through unrelated boxes (checked)\|R-diagram-geometry-03]] | No edge tunneling through unrelated boxes |
| R-diagram-04 | [[R-diagram-geometry#R-diagram-geometry-04 — Text fits inside its container (checked)\|R-diagram-geometry-04]] | Text fits inside its container |
| R-diagram-05 | [[R-diagram-geometry#R-diagram-geometry-05 — Labels are associated with what they label (sampled)\|R-diagram-geometry-05]] | Labels are associated with what they label |
| R-diagram-06 | [[R-diagram-geometry#R-diagram-geometry-06 — No label-label collision (checked)\|R-diagram-geometry-06]] | No label-label collision |
| R-diagram-07 | [[R-c4#R-c4-01 — Every arrow carries a label (sampled)\|R-c4-01]] | Every arrow carries a label |
| R-diagram-08 | [[R-sugiyama#R-sugiyama-01 — Minimize edge crossings (sampled)\|R-sugiyama-01]] | Minimize edge crossings |
| R-diagram-09 | [[R-sugiyama#R-sugiyama-02 — Bend budget (≤2 bends per edge, soft) (sampled)\|R-sugiyama-02]] | Bend budget |
| R-diagram-10 | [[R-sugiyama#R-sugiyama-03 — Monotone flow direction (stated)\|R-sugiyama-03]] | Monotone flow direction |
| R-diagram-11 | [[R-sugiyama#R-sugiyama-04 — Grid alignment (sampled)\|R-sugiyama-04]] | Grid alignment |
| R-diagram-12 | [[R-tufte-data-ink#R-tufte-data-ink-01 — Sibling box-sizing consistency (sampled)\|R-tufte-data-ink-01]] | Sibling box-sizing consistency |
| R-diagram-13 | [[R-c4#R-c4-02 — Title or legend present (checked)\|R-c4-02]] | Title or legend present |
| R-diagram-14 | [[R-c4#R-c4-03 — Boxes have meaningful names (stated)\|R-c4-03]] | Boxes have meaningful names |
| R-diagram-15 | [[R-c4#R-c4-04 — One meaning per visual variable (stated)\|R-c4-04]] | One meaning per visual variable |
| R-diagram-16 | [[R-wcag-contrast#R-wcag-contrast-01 — Contrast ≥ 4.5:1 for text, ≥ 3:1 for non-text UI (checked)\|R-wcag-contrast-01]] | Contrast ≥ 4.5:1 / 3:1 |
| R-diagram-17 | [[R-wcag-contrast#R-wcag-contrast-02 — Color is not the sole communicator of meaning (stated)\|R-wcag-contrast-02]] | Color is not the sole communicator |
| R-diagram-18 | [[R-bringhurst-typography#R-bringhurst-typography-01 — Font sizes are quantized to a small set (sampled)\|R-bringhurst-typography-01]] | Font sizes quantized to a small set |
| R-diagram-19 | [[R-tufte-data-ink#R-tufte-data-ink-02 — Chartjunk budget (stated)\|R-tufte-data-ink-02]] | Chartjunk budget |
| R-diagram-20 | [[R-svg-hygiene#R-svg-hygiene-01 — Stable IDs on every element (sampled)\|R-svg-hygiene-01]] | Stable IDs on every element |
| R-diagram-21 | [[R-svg-hygiene#R-svg-hygiene-02 — No orphan `<defs>` entries (checked)\|R-svg-hygiene-02]] | No orphan `<defs>` entries |
| R-diagram-22 | [[R-svg-hygiene#R-svg-hygiene-03 — SVG validates as XML (checked)\|R-svg-hygiene-03]] | SVG validates as XML |

## See also

- [[Rule Sets]] — parent catalog.
- [[CAB Rules]] — RULESET format spec.
- [[2026-06-08 diagram-auditing-methodologies]] — 20-source survey that seeded these rules.
- F132 Phase 1 — factoring landed 2026-06-09.
