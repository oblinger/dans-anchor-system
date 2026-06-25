---
description: "document facets — content regions a document carries"
---

# Document facets
The doc facets — bounded content **regions authored inside a document** (vs. the structural files/folders that make up an anchor).

| -[[FCT Doc]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [FCT Doc](hook://p/FCT%20Doc)<br>: document facets — content regions a document carries |
| --- | --- |
| Facets | [[FCT Doc Structure\|Doc Structure]],  [[FCT Ruleset\|Ruleset]],  [[FCT Brief\|Brief]],  [[FCT Discussion\|Discussion]],   |

## Overview
A document facet is a **derived/authored region**, not a file in the anchor tree: a `# RULESET` block ([[FCT Ruleset|Ruleset]]), a `# BRIEF` ([[FCT Brief|Brief]]), a `## Discussion` ([[FCT Discussion|Discussion]]), a `## Glossary`. They can appear *inside* any document; contrast the anchor & structure facets, which are whole files/folders. Worked instance of the ruleset facet: [[FEX]] → the `R-anchor-page` ruleset embedded in [[FCT Anchor Page]], and the catalog [[Rulesets]].

# RULESET R-doc-facet
include::
where:: doc-region
description:: what makes a content region a document facet (vs. a structural file/folder)

What classifies a region as a document facet. These are definitional invariants the member facets ([[FCT Ruleset]], [[FCT Brief]], [[FCT Discussion]]) each inherit. Format of this set: [[FCT Ruleset]].

### RULE R-doc-facet-01 — A document facet is a region inside a document, never a whole file (stated)

A document facet is a bounded, named content region *authored inside* a document (a `# RULESET` block, a `# BRIEF`, a `## Discussion`, a `## Glossary`) — not a file or folder in the anchor tree. A facet that is a whole file/folder is an anchor & structure facet ([[FCT Anchor]]), not a document facet.

### RULE R-doc-facet-02 — A document facet is bounded by its heading (checked)

Each document-facet region begins at its own heading (`# RULESET`, `# BRIEF`, `## Discussion`, …) and runs to the next sibling-or-higher heading; it does not bleed across that boundary.

**Check pattern:** the region's content lies entirely between its opening heading and the next heading of equal or higher level.

### RULE R-doc-facet-03 — A document may carry many document facets (stated)

Unlike a structural facet (one file/folder), document facets compose freely — a single document can carry a `# RULESET`, a `# BRIEF`, a `## Discussion`, and a `## Glossary` at once, each governed by its own member facet.
