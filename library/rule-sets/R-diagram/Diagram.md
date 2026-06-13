---
description: "Diagram authoring + validation rules: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate."
---
# Diagram

> [!info] Rule-set category folder
> This folder groups all rule sets related to diagram authoring + validation. Currently one set: [[R-diagram]] (umbrella, 22 rules in 5 zones). Future composition candidates: `R-sugiyama` (graph-drawing aesthetics), `R-c4` (diagram semantic conventions), `R-wcag-contrast` (accessibility) — each could be factored out and included by `R-diagram` as the catalog grows.

## Rule sets in this folder

- **[[R-diagram]]** — Umbrella set: 22 rules across structural (DRC-blockers) / aesthetic (Sugiyama-style) / semantic (C4) / accessibility-typography (WCAG/Bringhurst) / hygiene zones. Adopted by [[CAE Rules]] as the worked example.

## Source material

- [[2026-06-08 diagram-auditing-methodologies]] — 20-source survey covering PCB DRC, Purchase / Sugiyama / Eichelberger graph-drawing studies, C4 model checklist, Bertin / Tufte / Munzner methodologies, WCAG contrast, cartographic labeling (Imhof). The 22 rules in [[R-diagram]] are the synthesized checklist from this survey.

## See also

- [[Rule Sets]] — parent catalog
- [[FCT Rule Set]] — rule-set format spec
- [[viz-svg]] — companion skill for hand-authoring SVG figures
