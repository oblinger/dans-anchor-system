# RULESET R-svg-jiggle
include::
where:: {ANCHOR}/**/*.svg
description:: Geometry-aware layout-repair ("jiggle") for hand-authored SVG diagrams — detect a named, explicit issue list, then resolve each issue with the cheapest resolution that closes it without opening a new one.

> [!info] Provenance
> Modelled on the audit fix-by-default engine ([[F161 — Rule-driven audit engine]] / F166): an **issue rule is a `check::` that emits a finding**; a **resolution is a `fix::` candidate tagged to that issue type**. Runs over the geometry primitive layer in `skills/viz/svg-jiggle.py` (SVG bbox reader + intersection test + edge association). Captured 2026-06-25 per [[F186 — SVG Jiggle — geometry-aware layout-repair ruleset for the viz svg track]].

**The model — explicit issue list, then resolutions.** Jiggle is not a layout engine; it is the repair pass that runs *after* the generator. It **detects and emits a named, located issue list** (`svg-jiggle.py --issues` prints it), then per issue applies the **cheapest resolution that closes it without opening a new issue**, re-detects, and repeats until the list is empty (or only honestly-residual issues remain) or the iteration budget is hit. The materialized issue list is the point: it is the repair's goals, its termination test, and its inspectable residual (the audit-QFix hand-off pattern). Resolution selection minimizes `cost = Wh·(label-over-box) + Ws·(label-over-wrong-line) + Wa·(overweighted-head + crowded-band)`, `Wh ≫ Ws ≫ Wa`.

**Representation boundary.** This ruleset owns the **SVG** track, where the agent controls every coordinate so resolutions rewrite geometry directly. The sibling **D2 Jiggle** (deferred) expresses the same abstract moves as ELK directives. Cross-translation lives in the shared abstract-move vocabulary, not in either ruleset — so this is **not** a CAB-conformance facet and is deliberately absent from [[R-facet]].

## Governing rule

### RULE R-svg-jiggle-01 — Severity order governs resolution selection (governing)
A `<text>` **≥ 70 % contained in a single box** is that box's **node label** — EXEMPT, never moved. A `<text>` fully outside all boxes (title, legend) is exempt. Every issue and every resolution is weighted by three tiers: **hard** (`label ∩ box`, `box ∩ box`) ≫ **soft** (`label ∩ wrong-line`, `overweighted-head`, `crowded-band`) ≫ **free** (whitespace). A resolution that trades a hard issue for a soft one is a **win**; the reverse is forbidden; a resolution that opens a *new* hard issue is rejected.
**Check pattern:** parse geometry — `<text>` (x/y + inherited `font-size`/`text-anchor` → bbox `width ≈ len·font_size·0.58`, `top ≈ y−0.8·font_size`), `<rect>` boxes (stroked, not the canvas background), edges (`<line>`/`<path>` polyline; `<defs>`/`<marker>` skipped). Coverage ≥ 0.70 → node (exempt).
**Why:** the severity order *is* the cost function — without it, the repair has no principled basis to choose a resolution and could "fix" a hard issue by opening another.

## Issue catalog (detection — each a `check::` with a crisp threshold)

### RULE R-svg-jiggle-02 — issue: label-over-box (hard) (checked)
check:: svg_label_over_box
**Check pattern:** an edge-label intersects a box with ≥ 5 px overlap in **both** axes while < 70 % contained. Resolutions: `slide-label` → `flip-label` → `nudge-box`.
**Why:** a label printed across a box is the primary readability killer; it must reach zero.

### RULE R-svg-jiggle-03 — issue: label-over-wrong-line (soft) (checked)
check:: svg_label_over_wrong_line
**Check pattern:** a label intersects a line/path it is **not** associated with (associated = its nearest, color-preferring edge). Resolutions: `flip-label` (to the empty side of its *own* edge) → `slide-label`.
**Why:** a label sitting on a foreign arrow reads as annotating the wrong edge; flipping to the clean side of its own edge fixes it for free.

### RULE R-svg-jiggle-04 — issue: overweighted-head (soft) (checked)
check:: svg_overweighted_head
**Check pattern:** an arrow's marker/head length exceeds **20 %** of its segment length (head swallows a short arrow). Resolutions: `shrink-arrowhead` → `lengthen-segment` (widen).
**Why:** between close boxes the default arrowhead eats the whole arrow, so the direction reads as a blob, not an arrow.

### RULE R-svg-jiggle-05 — issue: crowded-band (soft) (checked)
check:: svg_crowded_band
**Check pattern:** a row/column of arrow segments whose lengths fall below the visibility threshold (~24 px) — boxes too close to show their arrows. Resolutions: `widen` → `shrink-arrowhead`. Often **residual** (widen is gated; see R-svg-jiggle-10).
**Why:** when a whole band is cramped, no per-label move helps — the band itself must gain length.

## Resolution catalog (fixes — each a `fix::` tagged to its issue type)

### RULE R-svg-jiggle-06 — slide-label-along-edge (free) (sampled)
fix:: slide_label_along_edge
Translate the label along its associated edge (+ modest perpendicular), accept the **minimum-displacement** clean position (zero box intersection, in-canvas, within ~110 px of the edge). Twins (halo+fill) move together. Tried first for label-over-box / label-over-wrong-line — zero cascade, label stays bound to its edge.

### RULE R-svg-jiggle-07 — flip-label-across-edge (free) (sampled)
fix:: flip_label_across_edge
Mirror the label to the empty side of its **own** edge (foot-of-perpendicular reflection); accept only if clean. Clears label-over-wrong-line (rejected-records → other side of its dashed arrow) and label-over-box where one side is crowded but the mirror side is open. Still free.

### RULE R-svg-jiggle-08 — nudge-box (cascading) (sampled)
fix:: nudge_box
Move a box into adjacent whitespace when that closes a label/box collision and opens clearance; **reconnect every incident edge endpoint** to the box's new boundary, move the box's node label(s) with it, and **reject any nudge that overlaps another box**. The first cascading move — applied only when slide/flip can't clear a hard issue, or to open band clearance (e.g. dead-letter box up → "daily rollups" clears).
**Why:** some hard overlaps can't be cleared by moving the label alone; moving the *box* is the user's "local move of one object, see if it fits," generalized.

### RULE R-svg-jiggle-09 — shrink-arrowhead (local) (sampled)
fix:: shrink_arrowhead
Scale a specific short edge's marker down so the head is ≤ 20 % of its segment (per-edge, long edges untouched). Resolves overweighted-head; helps crowded-band.

### RULE R-svg-jiggle-10 — widen (global, gated) (stated)
fix:: try_widen
Uniformly scale inter-box **gaps** (and the canvas) on the cramped axis so a crowded band gains arrow length; boxes keep relative order, only gaps grow. The most invasive resolution — **gated**: applied only when `shrink-arrowhead` alone cannot clear the crowded-band, and when it can be done without distorting the layout. When unsafe, the crowded-band is left as an **honest residual** in the issue list rather than forced.
**Why:** widen is the only fix for a whole-band crowd, but it is structural; honesty about an un-widened residual beats a distorted diagram.

# BRIEF

**R-svg-jiggle** repairs hand-authored SVG diagrams by the **issue-list model**: detect a named, located issue list (`--issues`), then resolve each with the cheapest resolution that closes it without opening a new one, until the list is empty or only honest residuals remain. Detection + geometry live in `skills/viz/svg-jiggle.py`; the rules here are the policy. It mirrors the F161/F166 engine — issue = `check::`, resolution = `fix::` candidate.

- **R-svg-jiggle-01** — severity tiers (hard = label∩box/box∩box ≫ soft = wrong-line/overweighted-head/crowded ≫ free) are the cost function governing every selection; node labels (≥70% inside a box) and outside-all-boxes labels are exempt.
- **Issue catalog (02–05)** — label-over-box (hard), label-over-wrong-line, overweighted-head (head >20% of segment), crowded-band (arrows <~24px). Each names its candidate resolutions.
- **Resolution catalog (06–10)** — slide (free, first), flip (free), nudge-box (cascading, edge-reconnecting), shrink-arrowhead (local), widen (global, gated; honest residual when unsafe).

Cheapest-first; hard issues must reach 0; soft issues are cleared when a cheap resolution exists, else listed as residual (never faked). SVG track only — D2 Jiggle is the deferred sibling sharing the abstract-move vocabulary, not these rules. Not a CAB-conformance facet; not under [[R-facet]].

Run: `svg-jiggle.py <in.svg> [-o <out>] [--max-iter 20] [--report] [--issues]`.
