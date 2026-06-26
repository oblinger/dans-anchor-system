---
description: "Viz Bench — a fixed set of reference figures drafted by different techniques (Scribe / D2 / Draw.io) from different starting points (formal spec / natural text), so the inputs and outputs can be compared side by side."
---

# Viz Bench
A benchmark for **figure-drafting techniques**: one fixed set of reference figures, each drafted by several techniques from a recorded starting point — so you can click any cell and see *what went in* (the spec, JSON, or natural text) and *what came out* (the rendered figure) for each approach, and pick the one that works best.

| -[[Viz Bench]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [Viz Bench](hook://p/Viz%20Bench)<br>: figure-drafting techniques compared across a fixed reference set |
| --- | --- |
| Related | [[viz]] (the skill under test),  [[R-diagram]] / [[R-svg-jiggle]] (the Scribe rules),  [[drawio-skill]] (the Draw.io engine) |
| Members | [[Gallery — Draw.io\|Draw.io Gallery]],  [[Gallery\|Scribe + D2 Gallery]],   |

## Two axes being compared

- **Technique (engine)** — *how* the figure is drafted:
  - **Scribe** — the in-house approach: the agent hand-authors the SVG directly (`/viz svg` / `/viz diagram`), governed by the [[R-diagram]] ruleset and cleaned up by the [[R-svg-jiggle]] repair pass. Full pixel control; the label-over-box problem is solved by jiggle.
  - **D2** — text → [D2](https://d2lang.com) DSL → ELK auto-layout → SVG (`/viz d2`).
  - **Draw.io** — natural-language or JSON → draw.io XML → the official draw.io engine renders it, with a vision self-check ([[drawio-skill]]). Routes edges + places labels in corridors by construction.
- **Input mode** — *what it starts from*:
  - **Formal spec** — the detailed `NN — …` spec docs below (every node + edge enumerated). The current corpus.
  - **Natural text** — a free-prose description of the same figure (no node/edge enumeration), to test how each technique copes with looser input. *(Planned — not yet populated.)*
  - **Derived JSON** — e.g. Draw.io's `autolayout.py` consumes a graph JSON derived from the spec; that JSON is kept alongside the output as the technique's actual starting material.

## The matrix — inputs → outputs

Each row is a reference figure. **Input** links the starting material; the technique columns link the rendered output (`✓` = done, `—` = not yet drafted). Click any cell to see it.

| # | Figure | Input (spec) | Scribe (svg) | D2 | Draw.io |
|---|---|---|---|---|---|
| 01 | Layered system architecture | [[01 — Layered system architecture\|spec]] | [svg](renders/01-svg.svg) | [d2](renders/01-d2.svg) | [drawio](renders/01-drawio.png) · [json](renders/01-drawio.json) |
| 02 | Linear data pipeline (ETL) | [[02 — Linear data pipeline (ETL)\|spec]] | [svg](renders/02-svg.svg) | [d2](renders/02-d2.svg) | [drawio](renders/02-drawio.png) · [src](renders/02-drawio.drawio) |
| 03 | Sequence diagram | [[03 — Sequence diagram\|spec]] | [svg](renders/03-svg.svg) | [d2](renders/03-d2.svg) | — |
| 04 | State machine | [[04 — State machine\|spec]] | [svg](renders/04-svg.svg) | [d2](renders/04-d2.svg) | — |
| 05 | Entity-relationship | [[05 — Entity-relationship\|spec]] | [svg](renders/05-svg.svg) | [d2](renders/05-d2.svg) | — |
| 06 | Hierarchy / org tree | spec (legacy filename) | [svg](renders/06-svg.svg) | [d2](renders/06-d2.svg) | — |
| 07 | Network / deployment | spec (legacy filename) | [svg](renders/07-svg.svg) | [d2](renders/07-d2.svg) | — |
| 08 | Dependency DAG (dense) | [[08 — Dependency DAG (dense)\|spec]] | [svg](renders/08-svg.svg) | [d2](renders/08-d2.svg) | — |
| 09 | Flowchart with decisions | [[09 — Flowchart with decisions\|spec]] | [svg](renders/09-svg.svg) | [d2](renders/09-d2.svg) | [drawio](renders/09-drawio.png) · [json](renders/09-drawio.json) |
| 10 | Class diagram | [[10 — Class diagram\|spec]] | [svg](renders/10-svg.svg) | [d2](renders/10-d2.svg) | — |
| 11 | Mind map / radial | spec (legacy filename) | [svg](renders/11-svg.svg) | [d2](renders/11-d2.svg) | — |
| 12 | Swimlane process | [[12 — Swimlane process\|spec]] | [svg](renders/12-svg.svg) | [d2](renders/12-d2.svg) | — |

## Galleries (per technique)

- **[[Gallery — Draw.io|Draw.io Gallery]]** — every figure drafted via draw.io (3 of 12 so far: 01, 02, 09), each with its starting material + the vision-self-check verdict.
- **[[Gallery|Scribe + D2 Gallery]]** — the original per-figure comparison of Scribe (hand-SVG) vs D2, with fidelity + legibility scores. *(Per-technique split into separate Scribe-only / D2-only galleries is a refinement TODO.)*

## Status / TODO

- **Done:** corpus of 12 formal specs; Scribe + D2 renders for all 12; Draw.io for 01 / 02 / 09; the inputs→outputs matrix above.
- **Next:** Draw.io for the remaining 9; the **natural-text** input mode (a prose version of each figure → drafted by each technique); split the Scribe + D2 gallery into per-technique galleries; clean the 3 legacy spec filenames (06 / 07 / 11).
