---
description: "Diagram authoring + validation rules: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate."
---
# Diagram

> [!info] Diagram domain folder
> This folder holds the diagram-domain rulesets: the [[R-diagram]] umbrella (22 rules, composed via `include::`) and [[R-c4]] (diagram-semantic conventions). The other 5 methodology sub-sets that the umbrella composes now live in sibling **domain** folders under `Rulesets/` — `Graph/` ([[R-sugiyama]]), `Structural/` ([[R-diagram-geometry]]), `Accessibility/` ([[R-wcag-contrast]]), `Typography/` ([[R-bringhurst-typography]]), `Visualization/` ([[R-tufte-data-ink]]), `SVG/` ([[R-svg-hygiene]]) — so those cross-cutting domains can later hold non-diagram rulesets too. The umbrella still pulls them all back together by wiki-link (basename) include, regardless of folder. Reorganized 2026-06-16 per F132 Q5=B.

## Rulesets in this folder

- **[[R-diagram]]** — Umbrella set: 22 rules across structural (DRC-blockers) / aesthetic (Sugiyama-style) / semantic (C4) / accessibility-typography (WCAG/Bringhurst) / hygiene zones, composed from the sub-sets via `include::`. Adopted by [[CAE Rules]] as the worked example.
- **[[R-c4]]** — Semantic-convention sub-set (4 rules): every arrow labeled, title or legend present, meaningful box names, one meaning per visual variable. Diagram-specific, so it stays in the Diagram domain.

## Source material

- [[2026-06-08 diagram-auditing-methodologies]] — 20-source survey covering PCB DRC, Purchase / Sugiyama / Eichelberger graph-drawing studies, C4 model checklist, Bertin / Tufte / Munzner methodologies, WCAG contrast, cartographic labeling (Imhof). The 22 rules in [[R-diagram]] are the synthesized checklist from this survey.

## See also

- [[Rulesets]] — parent catalog
- [[FCT Ruleset]] — ruleset format spec
- [[viz-svg]] — companion skill for hand-authoring SVG figures
