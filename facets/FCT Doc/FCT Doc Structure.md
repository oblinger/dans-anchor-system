---
description: "the canonical document layering — progressive disclosure for a document"
---

# FCT Doc Structure
The standard top-to-bottom structure every document follows — progressive disclosure specialized for a single document: each layer reveals more depth for a more-committed reader.

| -[[FCT Doc Structure]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Doc]] → [FCT Doc Structure](hook://p/FCT%20Doc%20Structure)<br>: the canonical document layering — progressive disclosure for a document |
| --- | --- |
| Anchor | [[FCT Doc]] (parent) |
| Related | [[DSC progressive-disclosure]] (the discipline this specializes),  [[FCT Brief]],  [[FCT Anchor Page]], |

## Overview
[[DSC progressive-disclosure]] is the general discipline — reveal information in layers so a reader gets the gist first and drills in only as far as they need. **Doc Structure** is that discipline applied to a *single document*: a fixed top-to-bottom order of layers, each aimed at a more-committed reader than the last. Every document the system owns — anchor page, facet spec, feature doc, design doc, user guide — follows this skeleton; specific document kinds (e.g. [[FCT Anchor Page]]) refine it but never violate the layer order.

## The layers (top to bottom)

*Skeleton — to fill in. The seed comes from [[FCT Brief]] § "three reader zones"; this generalizes it to every document.*

| # | Layer | Audience (by depth) | Purpose | Required? |
|---|---|---|---|---|
| 1 | **H1 title** | everyone | what this document is, in a few words | required |
| 2 | **TLDR** — one sentence under the H1 | glance-reader / link-follower | what it IS in plain language; usually enough on its own | required |
| 3 | **Figure** (optional) | visual orienter | one diagram when a picture beats prose | optional |
| 4 | **Dispatch table** | navigator | breadcrumb + the document's outbound links / members | per kind |
| 5 | **Overview** (optional H2) | deeper reader | a paragraph — added only when the one-sentence TLDR isn't enough | optional |
| 6 | **Body** | reader + agent | the actual content the document holds | required |
| 7 | **Brief** (`# BRIEF` at bottom) | agent only | how to maintain the document | optional |

*To fill in: exact rule per layer, the ordering invariant, the required-vs-optional matrix by document kind, the audience-by-depth mapping, and the `# RULESET R-doc-structure`.*

## Relationship to other facets
- **[[DSC progressive-disclosure]]** — the general discipline; this facet is its document-scoped specialization.
- **[[FCT Anchor Page]]** — a specific document kind (the `{slug}.md` anchor page) that refines this skeleton.
- **[[FCT Brief]]** — owns the bottom (agent-facing) layer; its three-reader-zones model is the seed of this facet.

# BRIEF
- **This is the spec for the document skeleton**, not an instance — never paste a real document here.
- **Stub status (2026-06-13):** created as a fillable skeleton. The layer table is the seed; per-layer rules, the required/optional matrix, and `# RULESET R-doc-structure` are TBD.
- **Don't duplicate [[FCT Anchor Page]] or [[FCT Brief]]** — this facet is the *general* layering; those refine or own specific layers. Link, don't restate.
- **Stay document-scoped** — anchor-folder / multi-file structure is [[FCT Folder]] / [[FCT All Files]], not this facet. Doc Structure is about the inside of one file.
