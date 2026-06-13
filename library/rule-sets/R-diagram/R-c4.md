# RULESET R-c4
description:: C4-model semantic conventions; the "what does this diagram mean?" rules.
include::

> [!info] Provenance
> **C4 model § Conventions** (Simon Brown) — the architecture-diagramming method that codifies "every arrow is labeled, every box has a title, every diagram has a legend." **Jacques Bertin**, *Sémiologie graphique* (1967) — the foundational text on visual variables (color, shape, size, position, texture, value, orientation) and the principle that each variable should encode exactly one semantic axis.

Every arrow labeled, title or legend present, boxes named meaningfully, one meaning per visual variable.

Factored from [[R-diagram]] 2026-06-09.

### RULE R-c4-01 — Every arrow carries a label (sampled)

Every `<line>`/`<path>` with `marker-end` (i.e., an arrow indicating a directed relationship) has a `<text>` element associated with it via proximity (see [[R-diagram-geometry-05]]), or is in the umbrella set's explicit "unlabeled-arrow allowed" exception list.

**Check pattern:** enumerate arrows; for each, search for an associated text within label-proximity radius. Fail when no associated text is found and no exception is declared.

**Why:** a labeled arrow tells the reader *what kind of relationship*. An unlabeled arrow is a guess.

### RULE R-c4-02 — Title or legend present (checked)

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
