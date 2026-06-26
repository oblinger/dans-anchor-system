---
description: "Viz Bench — figures drafted via the Draw.io technique (drawio-skill): NL/JSON → draw.io XML → official engine render + vision self-check. 3 of 12 done."
---

# Viz Bench — Draw.io Gallery

Figures drafted with the **Draw.io** technique ([[drawio-skill]]): a graph description (JSON for auto-layout, or hand-authored draw.io XML) → the official draw.io engine renders it → an agent **vision self-check** reads the rendered PNG and auto-fixes overlaps / clipped labels / off-canvas / stacked edges before it's shown. Routes edges and places labels in corridors by construction, so the label-over-box problem the Scribe track fights with [[R-svg-jiggle]] mostly doesn't arise.

**Done: 3 of 12** (01, 02, 09). The rest are TODO — see [[Viz Bench]] § Status.

Back to the comparison hub: **[[Viz Bench]]**.

## 02 — Linear data pipeline (ETL)

Input: hand-authored draw.io XML ([src](renders/02-drawio.drawio)) from [[02 — Linear data pipeline (ETL)|the spec]]. **Self-check: 0 issues** — clean first pass, no auto-fix rounds.

![[02-drawio.png]]

Every edge label sits in the routing corridor (none on a box); the `validate → dead-letter` branch is dashed + red, routed straight down into the corridor above `aggregate`, distinct from the happy path; serpentine fold across 3 rows, aspect ~1.4. This is the figure the Scribe track needed jiggle (5 overlaps + a box-nudge + 8 arrowhead-shrinks) to clear — draw.io produced it clean with zero repair.

## 09 — Flowchart with decisions

Input: [json](renders/09-drawio.json) (autolayout) from [[09 — Flowchart with decisions|the spec]], routed by Graphviz. **Self-check: clean.**

![[09-drawio.png]]

The two things that tangle hand-drawn flowcharts are handled: the dashed **"yes — retry"** loop-back routes up the left margin without crossing the forward flow, and all four failure branches converge cleanly into "Notify team → Pipeline failed." Decision diamonds, terminators (rounded, red for failure), and branch labels (yes/no) all correct. The clearest win — Graphviz auto-layout doing routing the hand-SVG track wouldn't attempt.

## 01 — Layered system architecture

Input: [json](renders/01-drawio.json) (autolayout) from [[01 — Layered system architecture|the spec]]. **Self-check: structurally complete, center is busy** (the honest hard case).

![[01-drawio.png]]

All 12 nodes role-colored (grey external / blue containers / yellow Kafka hub / green datastores / purple ops), and the control plane reads as distinct (the 8 Config / Metrics edges are dashed-purple vs solid data edges). **But** the center is cluttered — the 8 dashed fan-out edges converge through the middle, one label collides (`consume raw` + `publish enriched`), and validate.py flagged 3 edge crossings. This is the pathological case (a hub with 18 edges *plus* a double broadcast fan-out) — busy in any engine; a vision self-check round would help the label collision but not fully de-clutter the converging dashed edges.

## Remaining (TODO)

03 Sequence · 04 State machine · 05 ER · 06 Hierarchy · 07 Network/deployment · 08 Dependency DAG · 10 Class diagram · 11 Mind map · 12 Swimlane — not yet drafted via Draw.io.
