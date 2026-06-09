---
description: Diagram — decisions and validation approaches for hand-authored figures (architecture diagrams, flow diagrams, mockups). Cross-cutting set pulled in when an anchor authors visual artifacts.
---

# Diagram

| -[[Diagram]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[SKL]] → [[SKL Library]] → [[Rule Sets]] → [Diagram](hook://p/Diagram)<br>: Decisions and validation approaches for hand-authored figures. |
| --- | --- |
| --- | |

## What this set is

A cross-cutting decision set bundling the rules and discipline an agent applies when authoring or revising a visual figure (architecture diagram, flow diagram, sequence diagram, mockup). Pulled in by anchors that include visual artifacts in their documentation.

Two scopes covered:

- **Authoring decisions** — which tool to reach for, file-format conventions, source-alongside-output rule, style guidelines (color palette, typography, spacing).
- **Validation / audit rules** — machine-checkable rules a future `/audit diagram` or `audit-svg.py` should enforce. Inspired by PCB design-rule-check discipline ("diagram doesn't ship until rule-checker emits zero errors"). Empirical grounding: edge-crossing minimization (Purchase) and label-overlap detection (Eichelberger) are the two highest-leverage hard-fail checks.

## Decisions in this set

(Not yet populated. Each decision below would become a `D-NN` entry when pulled into an anchor's `{NAME} Decisions.md`. The intent is to migrate the disciplines listed in § Source material into formal decision entries here, with audit-tier annotation per CAB Decisions convention.)

| D | Decision | Source |
|---|---|---|

## Source material

Disciplines and reference material already established that should feed into this set:

- **ASCII art forbidden** in architecture diagrams. Source: durable feedback memory `feedback_no_ascii_in_architecture_diagrams` (2026-06-08).
- **Figure source alongside output** — every figure ships with its source file (`.svg` self / `.excalidraw` / `.d2` / `.py`) in the same folder with the same basename. Source: durable feedback memory `feedback_figure_source_alongside_output` (2026-06-08).
- **Hand-written SVG is the default** for architecture diagrams (full control of look). Excalidraw for hand-drawn aesthetic; D2 only when user names D2 specifically. Source: [[viz-svg]] + CAB Architecture facet § Architecture diagram requirements.
- **Style guidelines for SVG architecture figures** — Helvetica/Arial font, role-coded box palette (`#fff3f3` boundary / `#bac8ff` compute / `#fff9db` storage / `#ebfbee` policy), 2px box stroke, 3px arrow stroke, italic blue arrow labels, single `<defs>` arrowhead marker. Source: [[viz-svg]].
- **22-item audit checklist** — five zones (Structural / Aesthetic / Semantic / Accessibility / Hygiene) covering box overlap, edge crossings, label collision, contrast ratios, monotone flow, color-not-sole-channel, etc. Source: `~/ob/kmr/Topic/Search/Survey/2026-06-08 diagram-auditing-methodologies.md`.

## Validation discipline (proposed)

Modeled on PCB DRC:

1. Author the figure.
2. Run the audit (future `/audit diagram` or `audit-svg.py`).
3. Each rule emits warning / error / info; errors block ship.
4. Fix to zero errors before the figure is considered done.

Implementation gap (per survey § Gaps): no off-the-shelf SVG layout linter exists — `svglint` / `svgo` are file-hygiene only. The audit-svg script would be original work; the 22-item checklist gives the rule catalog to build it against.

## See also

- [[Rule Sets]] — parent set catalog
- [[viz-svg]] — hand-written SVG authoring skill
- [[CAB Architecture]] — architecture-facet diagram requirements
- [[2026-06-08 diagram-auditing-methodologies]] — survey of methodologies and tools
