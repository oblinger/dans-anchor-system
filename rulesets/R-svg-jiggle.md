# RULESET R-svg-jiggle
include::
import:: skills/viz/svg-jiggle.py
where:: `{anchor}/**/*.svg`
description:: Geometry-aware layout-repair ("jiggle") for hand-authored SVG diagrams — detect a named, explicit issue list, then resolve each issue with the cheapest resolution that closes it without opening a new one.

> [!info] Provenance
> Modelled on the audit fix-by-default engine ([[F161 — Rule-driven audit engine]] / F166): an **issue rule is a `check::` that emits a finding**; a **resolution is a `fix::` candidate tagged to that issue type**. Runs over the geometry primitive layer in `skills/viz/svg-jiggle.py` (SVG bbox reader + intersection test + edge association). Captured 2026-06-25 per [[F186 — SVG Jiggle — geometry-aware layout-repair ruleset for the viz svg track]].

**The model — explicit issue list, then resolutions.** Jiggle is not a layout engine; it is the repair pass that runs *after* the generator. It **detects and emits a named, located issue list** (`svg-jiggle.py --issues` prints it), then per issue applies the **cheapest resolution that closes it without opening a new issue**, re-detects, and repeats until the list is empty (or only honestly-residual issues remain) or the iteration budget is hit. The materialized issue list is the point: it is the repair's goals, its termination test, and its inspectable residual (the audit-QFix hand-off pattern). Resolution selection minimizes `cost = Wh·(label-over-box) + Ws·(label-over-wrong-line) + Wa·(overweighted-head + crowded-band)`, `Wh ≫ Ws ≫ Wa`.

**Representation boundary.** This ruleset owns the **SVG** track, where the agent controls every coordinate so resolutions rewrite geometry directly. The sibling **D2 Jiggle** (deferred) expresses the same abstract moves as ELK directives. Cross-translation lives in the shared abstract-move vocabulary, not in either ruleset — so this is **not** a CAB-conformance facet and is deliberately absent from [[R-facet]].

**Audit scope — authored diagrams only.** `where::` reaches every `.svg` under the anchor, and a **build artifact** is exempt from the `check::` rules. On an export the representation boundary above fails in both directions: a geometry rewrite dies at the next export, and the layout was the generator's decision to make — for `.d2` this ruleset already says those moves belong to D2 Jiggle, as ELK directives. Measured 2026-08-02, **87 of the vault's 123 SVGs are exports**, so unscoped the audit would spend 88 % of its findings restating other tools' layout choices as defects of the anchor. Two grades of evidence, and the verdict names which one fired: a **generator signature in the file's own bytes** (`data-d2-version`, `svg-source:excalidraw`, graphviz, `mxfile`) is proof; a **sibling source under the same basename** (`.d2`, `.excalidraw`, `.dot`, `.mmd`, `.drawio`, `.py`) is the vault's figure-source-beside-output convention, and only a convention — `Viz Bench/renders` names its files `{case}-{technique}`, so a hand-authored `05-svg.svg` has a `05-svg.d2` beside it that is a different technique for the same case, not its source. (That directory is a comparison corpus of deliberately un-repaired specimens, so exempting it is the wanted outcome regardless.) The exemption governs the **audit** only: `--issues` is a deliberate act and still analyses whatever it is handed.

**Run:** `svg-jiggle.py <in.svg> [-o <out>] [--max-iter 20] [--report] [--issues]` — `--issues` prints the located issue list; `--report` shows the resolutions applied.

## Governing rule

### RULE R-svg-jiggle-01 — Severity order governs resolution selection (governing)
A `<text>` **≥ 70 % contained in a single box** is that box's **node label** — EXEMPT, never moved. A `<text>` fully outside all boxes (title, legend) is exempt. Every issue and every resolution is weighted by three tiers: **hard** (`label ∩ node-box`, `box ∩ box`) ≫ **soft** (`label ∩ panel`, `label ∩ wrong-line`, `overweighted-head`, `crowded-band`) ≫ **free** (whitespace). A resolution that trades a hard issue for a soft one is a **win**; the reverse is forbidden; a resolution that opens a *new* hard issue is rejected.
**Check pattern:** parse geometry — `<text>` (x/y + resolved `font-size`/`text-anchor` → bbox `width ≈ len·font_size·0.58`, `top ≈ y−0.8·font_size`), `<rect>` boxes (stroked, not the canvas background), edges (`<line>`/`<path>` polyline; `<defs>`/`<marker>` skipped). Coverage ≥ 0.70 → node (exempt). **Every style property resolves through the full SVG cascade** — a `<defs><style>` rule, then a presentation attribute, then the inherited value — because these documents style themselves by class (`.sub{font-size:12.5px}`, `.core{stroke:…}`, `.arr{marker-end:url(#a)}`). Reading only presentation attributes silently substitutes a 16 px default (a 12 px label 33 % too wide drops under the 0.70 bar and stops being exempt), skips every class-stroked `<rect>` (one Viz Bench diagram parsed to 1 box of 15 — nothing to collide, nothing to repair), and leaves class-markered edges headless so their heads can never be weighed. An arrowhead's length is `markerWidth` scaled by stroke-width **only** under `markerUnits="strokeWidth"` (the SVG default); `userSpaceOnUse` is already in user units.
**Why:** the severity order *is* the cost function — without it, the repair has no principled basis to choose a resolution and could "fix" a hard issue by opening another.

## Issue catalog (detection — each a `check::` with a crisp threshold)

### RULE R-svg-jiggle-02 — issue: label-over-box (hard) (checked)
check:: svg_label_over_box
**Check pattern:** an edge-label intersects a **node** box with ≥ 5 px overlap in **both** axes while < 70 % contained. A box that fully encloses another box is a *panel*, not a node — that case is R-svg-jiggle-11. Resolutions: `slide-label` → `flip-label` → `nudge-box`.
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

### RULE R-svg-jiggle-11 — issue: label-over-panel (soft) (checked)
check:: svg_label_over_panel
**Check pattern:** the same geometry as R-svg-jiggle-02 — ≥ 5 px overlap in both axes, < 70 % contained — but the box it lands on **fully encloses at least one other box**, making it a grouping panel rather than a node. Resolutions: `slide-label` → `flip-label`. **`nudge-box` is deliberately withheld**, so an unclearable straddle stays in the issue list as an honest residual (the bargain R-svg-jiggle-10 strikes for an un-widened band).
**Why:** the words stay legible — a panel border is a region boundary, not a surface printed over — so this is a discomfort rather than a readability failure. Dan, 2026-08-04: *"a minor discomfort. If one can move elements around to avoid having that line overlap… then we should refactor the image. But if it's a problem to refactor the image, then it is acceptable… it really is discouraged."* The tier encodes exactly that: cheap moves are tried, an expensive restructure is never forced, and the residual is still reported so the discouragement is visible. Graded soft rather than exempted because all six of the vault's audit-scoped hard findings are this shape — exempting would have taken the hard tier to zero by deleting its only signal instead of re-grading it ([[F297 — Route non-markdown document rules — audit sweeps and the write moment|F297]] Q2).

## Resolution catalog (fixes — resolutions inside `svg-jiggle.py`'s repair loop, not `fix::` refs)

These five are moves the repair loop selects and re-detects after each application, not standalone document fixers an on-write hook could fire one at a time — so none carries a `fix::`; `svg-jiggle.py` remains the way to apply them.

### RULE R-svg-jiggle-06 — slide-label-along-edge (free) (sampled)
Translate the label along its associated edge (+ modest perpendicular), accept the **minimum-displacement** clean position (zero box intersection, in-canvas, within ~110 px of the edge). Twins (halo+fill) move together. Tried first for label-over-box / label-over-wrong-line — zero cascade, label stays bound to its edge.

### RULE R-svg-jiggle-07 — flip-label-across-edge (free) (sampled)
Mirror the label to the empty side of its **own** edge (foot-of-perpendicular reflection); accept only if clean. Clears label-over-wrong-line (rejected-records → other side of its dashed arrow) and label-over-box where one side is crowded but the mirror side is open. Still free.

### RULE R-svg-jiggle-08 — nudge-box (cascading) (sampled)
Move a box into adjacent whitespace when that closes a label/box collision and opens clearance; **reconnect every incident edge endpoint** to the box's new boundary, move the box's node label(s) with it, and **reject any nudge that overlaps another box**. The first cascading move — applied only when slide/flip can't clear a hard issue, or to open band clearance (e.g. dead-letter box up → "daily rollups" clears).
**Why:** some hard overlaps can't be cleared by moving the label alone; moving the *box* is the user's "local move of one object, see if it fits," generalized.

### RULE R-svg-jiggle-09 — shrink-arrowhead (local) (sampled)
Scale a specific short edge's marker down so the head is ≤ 20 % of its segment (per-edge, long edges untouched). Resolves overweighted-head; helps crowded-band.

### RULE R-svg-jiggle-10 — widen (global, gated) (stated)
Uniformly scale inter-box **gaps** (and the canvas) on the cramped axis so a crowded band gains arrow length; boxes keep relative order, only gaps grow. The most invasive resolution — **gated**: applied only when `shrink-arrowhead` alone cannot clear the crowded-band, and when it can be done without distorting the layout. When unsafe, the crowded-band is left as an **honest residual** in the issue list rather than forced. (`try_widen` is the one named resolver that exists as real code in `svg-jiggle.py` — it currently always takes the unsafe branch, so the residual is what it does today.)
**Why:** widen is the only fix for a whole-band crowd, but it is structural; honesty about an un-widened residual beats a distorted diagram.
