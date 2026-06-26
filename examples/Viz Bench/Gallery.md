---
description: "Side-by-side review gallery for the Viz Bench — each of the 12 prompts rendered by both the /viz svg (hand-authored SVG) and /viz d2 (D2 engine) renderers, with fidelity and legibility verdicts scored against each prompt's acceptance criteria."
---
# Viz Bench Gallery

This gallery assembles every render from the viz benchmark for side-by-side review: each of the 12 prompts is shown twice — once via the hand-authored `/viz svg` track and once via the `/viz d2` (D2 + ELK) track. Both renderers achieved **perfect fidelity (12/12)** — every node, edge, label, direction, and style in each spec was reproduced with nothing added, dropped, merged, or reordered. The renderers diverge on **legibility at the 800px embed width**: hand-authored SVG passes 8/12 (it controls font size against canvas width directly), while D2 passes 7/12 (its layout grows the canvas to satisfy ELK's crossing-free spacing, so text scales down proportionally at a fixed embed width — the misses are dense diagrams whose native resolution is genuinely large). Legibility misses are noted per render; in every case the diagram is fully legible at native resolution and only falls short of the strict `font_px × 800 / width ≥ 18` thumbnail metric.

## Score Table

| # | Kind | svg fidelity | svg legible | d2 fidelity | d2 legible |
|---|------|:---:|:---:|:---:|:---:|
| 01 | Service / data-flow topology | PASS | PASS | PASS | fail |
| 02 | Linear pipeline (with DLQ) | PASS | PASS | PASS | PASS |
| 03 | Sequence diagram (auth flow) | PASS | fail | PASS | fail |
| 04 | State machine (transcode job) | PASS | PASS | PASS | fail |
| 05 | ER diagram (crow's-foot) | PASS | PASS | PASS | fail |
| 06 | Org / reporting tree | PASS | PASS | PASS | PASS |
| 07 | Deployment topology (tiers) | PASS | PASS | PASS | PASS |
| 08 | Dependency DAG | PASS | PASS | PASS | PASS |
| 09 | CI/CD flowchart | PASS | PASS | PASS | PASS |
| 10 | UML class diagram | PASS | fail | PASS | fail |
| 11 | Radial mind map | PASS | PASS | PASS | PASS |
| 12 | Swimlane process | PASS | fail | PASS | PASS |
| **Totals** | **12 prompts** | **12/12** | **8/12** | **12/12** | **7/12** |

## 01 — Service / data-flow topology

Spec: **12 nodes, 18 edges.**

**/viz svg:** ![[01-svg.svg|800]]

**/viz d2:** ![[01-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (980×1000, aspect 1.02). Hand-authored, layered top-to-bottom (Sources→Ingest→Bus→Process→Serve→Clients) with config-svc fanning from the left and metrics-col from the right. All 12 nodes / 18 edges (10 solid data + 8 dashed: 4 config purple + 4 metrics teal); all 4 distinct kafka-bus topic edges present; every edge labeled; nodes color-coded by role; marker arrowheads in 3 colors. Body text 24px → 19.6px at 800px embed. Minor: the two ops fan-out arcs sweep wide to avoid crossings, making the canvas near-square rather than landscape.
- **d2** — fidelity PASS, legible **fail** (2692×1824, aspect 1.48). d2 0.7.1 + ELK, direction:down. 12/12 nodes, 18/18 edges (10 solid + 8 dashed, dashed colored per source), all fan-outs distinct, clean layered reading order, no overlaps. Legibility miss: box font 36px → 10.7px at 800px embed. Geometrically forced — 18 labeled edges + two wide fan-outs need ~2700px for a crossing-free ELK layout; the diagram is fully legible at native 2692px.

## 02 — Linear pipeline (with DLQ)

Spec: **11 nodes, 10 edges.**

**/viz svg:** ![[02-svg.svg|800]]

**/viz d2:** ![[02-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (900×920, aspect 0.98). Serpentine 3-row fold (L→R, R→L, L→R) of the 10-node main chain plus dlq as a downward dashed/red side-branch off validate. All 11 nodes + 10 edges, every edge labeled, directions correct; validate→dlq dashed-red and distinct from the 9 solid happy-path edges. Color-coded by role with a legend. Body/edge text 21px → 18.7px at 800px embed. Minor: a couple of sublabels abbreviated to fit 190px boxes without dropping below 18px.
- **d2** — fidelity PASS, legible PASS (1224×1003, aspect 1.22). Folded the 10-stage chain into a 3-column serpentine grid (grid-columns:3, gap:120) so fold seams are short horizontal hops; validate→dlq is the single dashed side-branch. Box text 28px → 18.3px at 800px embed; edge labels 22px → 14.4px (secondary). Minor: two horizontal seam labels slightly clip a neighbor box edge but stay readable — an inherent D2-grid seam-label artifact; gap:120 is the legibility/cleanliness sweet spot.

## 03 — Sequence diagram (auth flow)

Spec: **7 nodes, 18 edges.**

**/viz svg:** ![[03-svg.svg|800]]

**/viz d2:** ![[03-d2.svg|800]]

- **svg** — fidelity PASS, legible **fail** (1500×1880, aspect 0.80). Hand-authored: 7 vertical lifelines (head+foot boxes, color-coded by role, User as actor stick figure) and all 18 ordered messages stacked in time order. Self-message #3 as an amber loop; all dashed returns/redirects (#4,6,9,12,14,16,17,18) in purple, solid calls black; legend at bottom. Counts and labels match exactly. Legibility: main body 34px → 18.1px at 800px, but the longest labels and legend are 28–30px → ~14.9–16.0px to avoid overflow — honestly under the strict 18px bar. The inherent width-vs-font tension of a 7-participant sequence diagram.
- **d2** — fidelity PASS, legible **fail** (3562×2636, aspect 1.35). Native D2 `shape: sequence_diagram`. All 7 lifelines (AuthZ/TokenSvc kept distinct), all 18 messages in strict order incl. self-message #3 and exactly 8 dashed returns. Legibility: edge text 40px → 9.0px at 800px embed. Intrinsic to a 7-participant sequence diagram — lifeline spacing must fit message text, so the ratio asymptotes ~9px regardless of font; no grid-columns lever exists for the sequence_diagram shape. Genuinely legible at native size / a ~1600px embed.

## 04 — State machine (transcode job)

Spec: **9 nodes, 14 edges.** (Spec prose says 15, but the enumerated `## Edges` list has only 14; both renders follow the enumerated list as ground truth and flag the internal discrepancy.)

**/viz svg:** ![[04-svg.svg|800]]

**/viz d2:** ![[04-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (940×1060, aspect 0.89). Vertical happy-path spine (Queued→…→Published) with terminals offset (Failed red right, Cancelled purple left, Published green bottom). Rendered exactly the 14 enumerated edges with correct directions/labels/styles; both self-loops drawn on the right; both back-edges routed distinctly (Validating→Transcoding dashed far-left; Uploading→Queued dashed far-right). Body labels 23px → 19.6px, node labels 26px → 22px at 800px. No box overlaps.
- **d2** — fidelity PASS, legible **fail** (1764×1799, aspect 0.98). d2 v0.7.1, ELK. 9 nodes + 14 edges, both self-loops, exactly 4 dashed red edges (2 back-edges + 2 aborts). Queued green initial, terminals double-border. Legibility: box font 28px → 12.7px at 800px embed. A complexity floor, not a layout fault — a 9-node cyclic graph with long transition labels needs ~1764px to avoid overlaps; fully legible at native resolution.

## 05 — ER diagram (crow's-foot)

Spec: **10 nodes, 11 edges.**

**/viz svg:** ![[05-svg.svg|800]]

**/viz d2:** ![[05-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1160×1420, aspect 0.82). Hand-authored crow's-foot ER diagram: exactly the 10 entities and 11 one-to-many relationships, each edge labeled, with a "1" glyph at the parent and crow's-foot + "N" at the child via defs markers. Full attribute lists with PK/FK markers; junctions sit between their parents; color-coded by role with a legend. Attr font 28px → 19.3px at 800px embed. No overlaps; long CUSTOMER→REVIEW edge routed cleanly through margin lanes.
- **d2** — fidelity PASS, legible **fail** (1510×1956, aspect 0.77). d2 `sql_table` shapes (ELK): all 10 entities with full attribute lists (9 PK + 11 FK markers) and all 11 directed "1—N" edges. Legibility: smallest body text 20px → 10.6px at 800px embed. The 10 fully-attributed entities carry too much text for an 800px thumbnail; the canvas wants ~1500px. Note: d2 does not honor font-size config/class on sql_table, so the big-font knob is inert for tables.

## 06 — Org / reporting tree

Spec: **13 nodes, 12 edges.**

**/viz svg:** ![[06-svg.svg|800]]

**/viz d2:** ![[06-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1415×976, aspect 1.45). Hand-authored top-down org tree, 6 levels, color-coded by rank (purple CTO → crimson Engineer). All 13 nodes + 12 "reports to" edges; uneven branch depths preserved. Orthogonal elbow connectors; the uniform "reports to" annotated once (italic note) to avoid 12 redundant labels. Name font 32px → 18.1px at 800px embed. Minor: role strings abbreviated to fit 210px boxes.
- **d2** — fidelity PASS, legible PASS (1892×2397, aspect 0.79). Top-down ELK; all 13 nodes + 12 edges. Body font 46px box → 19.5px at 800px embed. Key fixes: wrapped long titles onto 2 lines to keep boxes narrow; compacted rank spacing via `--elk-nodeNodeBetweenLayers=45` to lift the deep 6-level chain out of an extreme tall-strip aspect (~0.58) up to 0.79. That flag is not expressible in-file in d2 0.7.1, so the exact render command is documented atop 06-d2.d2.

## 07 — Deployment topology (tiers)

Spec: **12 nodes, 17 edges.**

**/viz svg:** ![[07-svg.svg|800]]

**/viz d2:** ![[07-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1050×920, aspect 0.88). Left-to-right tier-cluster layout (Edge/App/Data dashed cluster boxes; INET+SES external). All 12 nodes + 17 edges (14 solid + 3 dashed: WEB1/WEB2→PG_REPLICA read-only + PG_PRIMARY→PG_REPLICA replication), every edge labeled with port/protocol. Node labels 24px → 18.3px at 800px. Minor: secondary sub-labels (18px) and edge labels (16px) render below 18px at 800px; only the primary node labels clear the threshold.
- **d2** — fidelity PASS, legible PASS (1602×2546, aspect 0.63). 3 tier-container boxes + 2 external nodes, direction:down. 12 leaf nodes, 17 edges, 3 dashed correctly styled. Node text 40px → 20.0px, edge labels 36px → 18.0px at 800px (both ≥18). Key levers: Data tier as a 2×2 grid collapsed the widest row (svg width 2857→1602); per-edge label font set to 36px; compact box heights to keep aspect ≥0.6.

## 08 — Dependency DAG

Spec: **14 nodes, 41 edges.**

**/viz svg:** ![[08-svg.svg|800]]

**/viz d2:** ![[08-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1240×910, aspect 0.73). Layered top-down DAG (gateway root at top, leaves at bottom) over 7 topo rows; all 14 nodes + 41 edges point downward (acyclic preserved), color-coded by source role with a legend eliding the uniform "depends on" label per spec. Primary node titles 28px → 18.1px at 800px. Weaker: dense fan-in/fan-out produces some edge crossings inherent to a 41-edge dense DAG with straight lines; 18px package sub-labels render ~11.6px at 800px (secondary text).
- **d2** — fidelity PASS, legible PASS (1447×2322, aspect 0.62). d2 0.7.1 + ELK, direction:up preserves topological order. Exactly 14 nodes + 41 arrows; uniform sibling boxes color-coded by role; "depends on" elided to a legend (spec-permitted), every directed edge still distinct. Text 34px → 18.8px at 800px. Minor: two longest labels overflow their 132px box width so d2 renders the text just under the box — readable, no ambiguity; width is floored by those two longest names.

## 09 — CI/CD flowchart

Spec: **16 nodes, 19 edges.**

**/viz svg:** ![[09-svg.svg|800]]

**/viz d2:** ![[09-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1140×1520, aspect 0.75). Hand-authored vertical flowchart; all 16 nodes + 19 edges 1:1 with spec, color-coded by role (green terminators, blue process, amber decision diamonds, red failure). Dashed orange retry loop-back (flaky_check→unit_tests) distinct from forward flow. The four failure edges merge onto a shared right-side bus with one arrowhead into notify_fail (the spec's four-way merge); all yes/no branch labels present. Body font 26px → 18.2px at 800px.
- **d2** — fidelity PASS, legible PASS (1658×2400, aspect 0.69). d2 0.7.1, direction:down. All 16 nodes + 19 edges; branch labels exact (yes×4, no×5, "yes — retry"×1); single dashed loop-back; four failure edges converge on notify_fail then one edge to done_fail. Rounded ovals / rectangles / diamonds color-coded by class. Node body font 38px → 18.3px at 800px. Edge labels 26px → ~12.5px (secondary yes/no markers); a couple of diamond texts slightly overflow the outline (inherent to d2 diamond fit, readable). Widening nodes pulled aspect from an initial 0.39 strip into range.

## 10 — UML class diagram

Spec: **12 nodes, 14 edges.**

**/viz svg:** ![[10-svg.svg|800]]

**/viz d2:** ![[10-d2.svg|800]]

- **svg** — fidelity PASS, legible **fail** (1640×1240, aspect 0.76). Hand-authored UML class diagram, all 12 classes + 14 edges (incl. italic abstract Account). 4 relationship semantics visually distinct via defs markers + color: generalization=hollow green triangle, composition=filled magenta diamond at whole-end, association=blue open arrow with multiplicities, dependency=dashed orange. Every multiplicity preserved; color-coded by cluster; legend bottom-right; no overlaps, orthogonal routing. Legibility: 21px member text → ~10px at 800px embed. A 12-class model with full name+attr+ops compartments is genuinely too dense to honor ≥18px-at-800px without truncating content — crisp at ~1400px+ embed.
- **d2** — fidelity PASS, legible **fail** (2098×2585, aspect 0.81). d2 0.7.1 / ELK. All 12 `shape:class` with full compartments; Account carries `{abstract}`. All 14 edges with exact labels+multiplicities; four semantics distinct via separate markers. Legibility: member text 26px → 9.9px at 800px embed. Inherent to a 12-class diagram with complete compartments — the canvas is ~2100px wide and cannot shrink to the ~1150px needed for 18px@800px without dropping member text or overlapping.

## 11 — Radial mind map

Spec: **15 nodes, 14 edges.**

**/viz svg:** ![[11-svg.svg|800]]

**/viz d2:** ![[11-d2.svg|800]]

- **svg** — fidelity PASS, legible PASS (1000×820, aspect 0.82). Hand-authored radial mind map: dark hub circle at center, 5 color-coded branch rounded-rects fanned at ~72° intervals, 9 leaf pills hanging outward. All 15 nodes + 14 directed edges (arrowheads color-matched to branch hue); strict tree, no cross-links, no labels (none specified). Leaf text 24px → 19.2px, branch labels 26px → 20.8px at 800px. Minor cosmetic: hub label slightly wider than the 78px circle but fully legible.
- **d2** — fidelity PASS, legible PASS (1228×982, aspect 1.25). d2 0.7.1 + ELK, direction:right gives a left-rooted radial tree: hub → 5 branches → 9 leaves. All 15 nodes + 14 edges, labels exact. Quantized fonts (hub 30 / branch 28 / leaf 28): leaf 28px → 18.2px at 800px (bumped from 26 to clear the 18px floor). No overlaps; width fixed by the 3-deep horizontal layout so grid-columns wasn't needed.

## 12 — Swimlane process

Spec: **14 nodes, 15 edges.**

**/viz svg:** ![[12-svg.svg|800]]

**/viz d2:** ![[12-d2.svg|800]]

- **svg** — fidelity PASS, legible **fail** (1160×1490, aspect 0.78). Hand-authored vertical-swimlane layout (4 lanes as columns, flow top-to-bottom): Applicant / Loan Officer / Underwriting / Funding, tinted lane backgrounds + bold headers. All 14 nodes + 15 edges with directed arrowheads and per-edge labels — 13 solid forward edges grey, 2 backward rework loops (N6→N3, N9→N6) dashed orange. Node shapes encode type (pill start/end, rect steps, amber decisions). Legibility: smallest text (19px edge labels, 21px node titles) → ~13–14.5px at 800px; the binding constraint is the 1160px width needed for four lanes. Comfortably readable in practice; only misses the formal cutoff.
- **d2** — fidelity PASS, legible PASS (1452×1358, aspect 1.07). 14 nodes + 15 edges exact. 4 swimlanes built as D2 grid containers (root grid-columns:1 stacks lanes; each lane grid-rows:1 lays nodes left-to-right); both rework loops dashed; node roles color-coded. Box font 33px → 18.2px at 800px (passes). Edge labels 27px → 14.9px (secondary). Long labels split to ≤2–3 short lines to keep box width 250. The lane-grid forces a compact 2-D layout (naive direction:right gave aspect 8.2; direction:down gave 0.39 — both extreme). Minor wart: two start nodes feed N4 with diagonal cross-lane connectors, slightly busy but no overlaps.
