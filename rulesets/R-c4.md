# RULESET R-c4
description:: C4-model semantic conventions; the "what does this diagram mean?" rules.
include::
where:: `{anchor}/**/*.svg`

> [!info] Provenance
> **C4 model § Conventions** (Simon Brown) — the architecture-diagramming method that codifies "every arrow is labeled, every box has a title, every diagram has a legend." **Jacques Bertin**, *Sémiologie graphique* (1967) — the foundational text on visual variables (color, shape, size, position, texture, value, orientation) and the principle that each variable should encode exactly one semantic axis.

Every arrow labeled, title or legend present, boxes named meaningfully, one meaning per visual variable.

Factored from [[R-diagram]] 2026-06-09.

### RULE R-c4-01 — Every arrow carries a label (sampled)

Every `<line>`/`<path>` with `marker-end` (i.e., an arrow indicating a directed relationship) has a `<text>` element associated with it via proximity (see [[R-diagram-geometry-05]]), or is in the umbrella set's explicit "unlabeled-arrow allowed" exception list.

**Check pattern:** enumerate arrows; for each, search for an associated text within label-proximity radius. Fail when no associated text is found and no exception is declared.

**Why:** a labeled arrow tells the reader *what kind of relationship*. An unlabeled arrow is a guess.

### RULE R-c4-02 — Title or legend present (checked)

> **`svg_title_or_legend` NOT wired 2026-08-11 ([[Tink Backlog#^T349|T349]]) — the checker is a faithful transcription of the Check pattern below, and the corpus simply does not comply.** Measured over all **127** vault SVGs: **104 fail, 22 pass, 1 unparseable** — 82%, the [[R-naming]]-01 signature at 39% and the [[R-prd]]-07 signature at 99%. The 22 passers are the real architecture diagrams ([[MUX Architecture]], `HA Scanner`, `SVP Architecture Layers`, the SV streaming set) so the rule is satisfiable and is being satisfied by the documents it was written for; the 104 are icons, test fixtures, bench renders, and a long tail of authored diagrams that never carried a title.
>
> **One hypothesis was tested before refusing, and it was wrong** — worth recording, because it is the shape of defect this walk has kept finding. The Check pattern says *"typically y < 60px **in a 480px canvas**"* — a proportional criterion — while the implementation hard-codes `y < 60` absolute, so a tall canvas would place a legitimate title below the line and fail. Re-measured with the threshold scaled to each file's `viewBox` height: it rescues **2 of the 104**. The other 102 still fail, and **99 of them carry no text at font-size ≥ 24 anywhere in the file** — there is no title to find at any threshold. The implementation is not the problem.
>
> **What would make this wirable is scope, as with [[R-prd]].** `where:: {anchor}/**/*.svg` selects every SVG in an anchor, and a C4 convention is a claim about architecture diagrams, not about `Forum Icon.svg` or `test-classes.svg`. Until the set can say *a diagram of this kind*, wiring turns a silent judgment into 104 loud ones. The absolute-vs-proportional threshold should still be fixed at that point — it is a real, if small, divergence between the rule as written and the rule as implemented.

Every diagram has either a title text element (H1-equivalent in the figure) or a legend block explaining the visual variables used.

**Check pattern:** look for a `<text>` element above the main canvas region (typically y < 60px in a 480px canvas) with a font size ≥ 24px, OR a labeled `<g>` group titled "Legend" or "Key".

**Why:** C4 model § Conventions: a diagram without a title or legend is unparseable for first-time readers.

### RULE R-c4-03 — Boxes have meaningful names (stated)

Every box has a `<text>` label with a name that's a noun or noun phrase from the system's vocabulary. Names like "Box1", "Component A", "Module" are forbidden.

**Check pattern:** manual review (or LLM-judged sampling) of box labels; flag generic placeholders.

**Why:** the boxes ARE the system's vocabulary in a diagram. Generic labels mean the diagram is incomplete.

### RULE R-c4-04 — One meaning per visual variable (stated)

A visual variable (color, shape, line-style) encodes exactly one semantic axis throughout the diagram. If green = "storage" once, green must mean "storage" everywhere.

**Check pattern:** manual review against a declared legend. Future: cluster boxes by visual variable and verify clusters align with semantic groupings.

**Why:** Bertin's *Sémiologie graphique* foundational principle. Overloading variables is the fastest way to make a diagram unreadable.
