# RULESET R-diagram
include: R-sugiyama, R-c4, R-wcag-contrast

> [!info] Rule Set
> Authoring + validation rules for hand-authored figures (architecture diagrams, flow diagrams, sequence diagrams, mockups). PCB-DRC-style discipline: diagram doesn't ship until rule-checker emits zero errors. Twenty-two rules in five zones, extracted from the 2026-06-08 diagram-auditing methodologies survey (Sugiyama / Purchase / C4 / Eichelberger / Bertin / Tufte / Munzner / WCAG / Bringhurst / PCB DRC / cartographic labeling).

> [!info] Rule-set format note
> This file is a worked example of the [[CAB Rules]] facet. The format: H1 begins with the sentinel word `RULESET` followed by the rule-set name; an `include:` line immediately under the H1 names other rule sets (comma-separated). Each rule is an H3 named `R-<set>-<NN> — Title (tier)`, with body = declarative statement + `**Check pattern:**` + `**Why:**`. `> [!info]` callouts inside the file are commentary that's not part of any rule. Zone headings (H4) are presentational only — rule identity is the H3.

The rules below are grouped into five zones for readability. The zone H4s are presentational; rule identity is `R-diagram-NN` regardless of zone. When this set is factored per F132 Phase 1, the zones become the included sub-sets (`R-pcb-drc-structural` / `R-sugiyama` / `R-c4` / `R-wcag-contrast` / `R-bringhurst-typography` / `R-tufte-data-ink` / `R-svg-hygiene`) and this file shrinks to just the H1 + `include:` line.

#### Zone A — Structural correctness (DRC-blockers)

The hard-fail rules. A diagram that violates these is broken, not stylistically suboptimal. These are the analog of PCB design-rule-check errors: ship blockers.

### R-diagram-01 — No box-on-box overlap (checked)

No two opaque container elements (`<rect>`, `<ellipse>`, `<polygon>` acting as boxes) have intersecting bounding boxes, except when one is a strict parent container of the other (containment is allowed; overlap is not).

**Check pattern:** parse the SVG; for every pair of container elements (X, Y), compute `bbox(X) ∩ bbox(Y)`. Fail if the intersection is non-empty AND neither is fully contained in the other.

**Why:** Eichelberger's UML-readability study identifies element overlap as a top readability killer. Overlap also breaks the visual hierarchy a reader uses to parse the diagram.

### R-diagram-02 — Edge endpoints anchor to box edges (checked)

Every arrow / edge endpoint terminates on the visible edge of a container or attaches to a marked port; no edge endpoints float in whitespace adjacent to (but not touching) their target.

**Check pattern:** for every `<line>`/`<path>` with `marker-end` (arrow), verify each endpoint coordinate is within 2px of the bounding box edge of some container element (or matches a named anchor point).

**Why:** floating endpoints look like rendering bugs and force the reader to guess which box the arrow connects to.

### R-diagram-03 — No edge tunneling through unrelated boxes (checked)

An edge from A to B does not pass through any box C that is neither A nor B. Edges may pass through arrow labels and other edges; only box-tunneling is forbidden.

**Check pattern:** for every edge segment, intersect with every container bbox. Fail if any container that is not the edge's start or end is intersected.

**Why:** Sourcetrail's system-diagram checklist and the C4 review criteria both flag edge tunneling as a primary clarity defect.

### R-diagram-04 — Text fits inside its container (checked)

Every `<text>` element nominally associated with a container has its rendered bounding box fully inside the container's bounding box (with at least 4px padding on each side as a soft check).

**Check pattern:** for every `<text>` with a `containerId` (or visually associated, e.g., same group), compute rendered text bbox; verify `text.bbox ⊆ container.bbox` (minus padding).

**Why:** text overflow is one of the most common rendering bugs in hand-authored SVG and an instant clarity-killer.

### R-diagram-05 — Labels are associated with what they label (sampled)

Every label (`<text>` near an arrow or box but not the box's primary title) is visually disambiguated as belonging to exactly one target — either by proximity (closer to that target than any other), by alignment, or by a leader line.

**Check pattern:** for each candidate label, identify its nearest-neighbor element by Euclidean distance; verify uniqueness of the "nearest" answer and verify proximity ratio (nearest distance < 0.5 × second-nearest distance).

**Why:** automatic-label-placement literature (Imhof, cartographic labeling) makes proximity-disambiguation the foundational rule. Otherwise, the reader plays a guessing game.

### R-diagram-06 — No label-label collision (checked)

No two `<text>` elements have overlapping bounding boxes.

**Check pattern:** pair-test all `<text>` bboxes for intersection.

**Why:** Eichelberger's empirical study: label-label overlap is the *#1* readability killer for class-style diagrams, ahead of edge crossings.

### R-diagram-07 — Every arrow carries a label (sampled)

Every `<line>`/`<path>` with `marker-end` (i.e., an arrow indicating a directed relationship) has a `<text>` element associated with it via § R-diagram-05 proximity, or is in the umbrella set's explicit "unlabeled-arrow allowed" exception list.

**Check pattern:** enumerate arrows; for each, search for an associated text within label-proximity radius. Fail when no associated text is found and no exception is declared.

**Why:** a labeled arrow tells the reader *what kind of relationship*. An unlabeled arrow is a guess.

#### Zone B — Aesthetic (Sugiyama-style graph drawing)

Quality rules below the DRC-blocker threshold. Violations are warnings, not errors. Based on Purchase's empirical work — edge-crossing minimization is the #1 readability driver overall.

### R-diagram-08 — Minimize edge crossings (sampled)

The crossing count is at or below the minimum achievable for this graph (or within a small budget — say, ≤2 crossings for graphs with ≤10 nodes).

**Check pattern:** brute-force count edge-edge intersections; compare against the graph's known minimum crossing number (computable for small graphs) or a heuristic budget.

**Why:** Purchase (1997, 2002): edge crossings are empirically the single largest factor in graph readability — more impactful than aesthetics like grid-alignment or symmetry.

### R-diagram-09 — Bend budget (≤2 bends per edge, soft) (sampled)

No edge has more than two right-angle bends, and the average bend count across edges is at or below 1.

**Check pattern:** for each `<path>` edge, count direction changes. Aggregate average across edges.

**Why:** Sugiyama-style layouts emphasize edge-bend minimization as a readability heuristic; reading a one-bend or two-bend edge is fast, three-bend is slow.

### R-diagram-10 — Monotone flow direction (stated)

The dominant edge direction is consistent (left-to-right OR top-to-bottom). Counter-flow edges (right-to-left when L→R is dominant) are minimized and only used for back-edges (e.g., feedback loops).

**Check pattern:** compute the dominant axis from edge vectors; verify ≥80% of edges align with it.

**Why:** Sugiyama's layered drawing algorithm enforces this; without it, the reader can't establish a flow direction and the diagram reads as a tangle.

### R-diagram-11 — Grid alignment (sampled)

Box X-coordinates and Y-coordinates cluster onto a small set of "column" and "row" grid lines; outlier positions are intentional.

**Check pattern:** for each box, compute its centroid; cluster centroids into bands (along X and Y separately); verify the number of distinct bands is ≤ ceil(sqrt(boxes)) + 1.

**Why:** Gestalt principle of alignment — readers infer relationships from co-aligned elements. A grid makes the diagram parseable at a glance.

### R-diagram-12 — Sibling box-sizing consistency (sampled)

Boxes in the same role (e.g., all "subsystem" boxes) have the same width and height within 20%.

**Check pattern:** assume same-color or same-role boxes are siblings; check width and height variance ≤ 0.2 × mean.

**Why:** size variation that doesn't encode meaning is chartjunk (Tufte). Either size means something or it should be constant.

#### Zone C — Semantic (C4 model)

The "what does this diagram *mean*?" rules.

### R-diagram-13 — Title or legend present (checked)

Every diagram has either a title text element (H1-equivalent in the figure) or a legend block explaining the visual variables used.

**Check pattern:** look for a `<text>` element above the main canvas region (typically y < 60px in a 480px canvas) with a font size ≥ 24px, OR a labeled `<g>` group titled "Legend" or "Key".

**Why:** C4 model § Conventions: a diagram without a title or legend is unparseable for first-time readers.

### R-diagram-14 — Boxes have meaningful names (stated)

Every box has a `<text>` label with a name that's a noun or noun phrase from the system's vocabulary. Names like "Box1", "Component A", "Module" are forbidden.

**Check pattern:** manual review (or LLM-judged sampling) of box labels; flag generic placeholders.

**Why:** the boxes ARE the system's vocabulary in a diagram. Generic labels mean the diagram is incomplete.

### R-diagram-15 — One meaning per visual variable (stated)

A visual variable (color, shape, line-style) encodes exactly one semantic axis throughout the diagram. If green = "storage" once, green must mean "storage" everywhere.

**Check pattern:** manual review against a declared legend. Future: cluster boxes by visual variable and verify clusters align with semantic groupings.

**Why:** Bertin's *Sémiologie graphique* foundational principle. Overloading variables is the fastest way to make a diagram unreadable.

#### Zone D — Accessibility & typography (WCAG / Bringhurst)

### R-diagram-16 — Contrast ≥ 4.5:1 for text, ≥ 3:1 for non-text UI (checked)

Every `<text>` element has a contrast ratio of at least 4.5:1 against its background (the box fill it sits on, or canvas if none). Lines, arrows, and borders have ≥ 3:1.

**Check pattern:** compute luminance for each `<text>` fill vs. its background fill; compute contrast ratio per WCAG formula. Same for stroke colors.

**Why:** WCAG 2.1 AA contrast requirements. Not just an accessibility nicety — diagrams projected on screens or printed in B&W must remain readable.

### R-diagram-17 — Color is not the sole communicator of meaning (stated)

For every semantic distinction conveyed by color (e.g., box fill color = role), the same distinction is also conveyed by a non-color channel (label text, position, shape, or a redundant legend).

**Check pattern:** manual review. Future: extract color clusters; verify each cluster has a redundant identifier (text label including the role name, distinct shape, etc.).

**Why:** WCAG 1.4.1; colorblind readers and B&W printouts depend on this.

### R-diagram-18 — Font sizes are quantized to a small set (sampled)

The diagram uses at most 4 distinct font sizes (e.g., 14 / 16 / 20 / 24). Title, body, label, and caption — that's the budget.

**Check pattern:** enumerate font-size attributes; fail if more than 4 distinct values.

**Why:** Bringhurst — typographic scale is a quality marker. Many small variations in size is amateurish; few well-chosen sizes is professional.

### R-diagram-19 — Chartjunk budget (stated)

The diagram contains no decorative elements that don't carry information. No drop shadows on every box, no gradient fills for fun, no decorative borders.

**Check pattern:** manual review against Tufte's data-ink ratio principle. Future: detect gradients, shadows, and 3D effects; flag for review.

**Why:** Tufte. Decoration competes with content for attention; in a diagram (which is dense with meaning) that competition is always lost.

#### Zone E — Hygiene

### R-diagram-20 — Stable IDs on every element (sampled)

Every interactive or stateful SVG element (rects, paths, text used as labels) has a `id` attribute. IDs are meaningful (e.g., `id="scheduler-box"`, not `id="rect42"`).

**Check pattern:** enumerate elements lacking `id`; flag. Future: heuristically detect machine-generated ID patterns and flag.

**Why:** stable IDs are required for any future tooling that wants to reference specific elements (interactive overlays, automated audit feedback, regression testing).

### R-diagram-21 — No orphan `<defs>` entries (checked)

Every `<marker>`, `<linearGradient>`, `<filter>`, etc. defined under `<defs>` is referenced by at least one rendered element (via `marker-end`, `fill="url(#…)"`, etc.).

**Check pattern:** enumerate all `id`s under `<defs>`; verify each is referenced by some attribute elsewhere in the document.

**Why:** dead `<defs>` accumulate during iteration; they bloat the file and create confusing "what's this for?" moments on later edits.

### R-diagram-22 — SVG validates as XML (checked)

The SVG file parses as well-formed XML with no warnings under `xmllint --noout`.

**Check pattern:** `xmllint --noout {file}.svg` returns exit code 0 with no stderr output.

**Why:** the absolute baseline. A malformed SVG isn't a diagram at all.
