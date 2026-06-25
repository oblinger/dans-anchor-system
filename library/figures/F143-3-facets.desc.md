# F143-3 — Facets detail (grouped by domain)

description:: Stated intent for `F143-3-facets.svg`. Maintained alongside the `.d2` source by `/viz diagram`; rewritten as the user clarifies (never appended).

## What it conveys

The **facets** — per-document structural specs — grouped by the domain they belong to, so a reader drilling into the Facets peer (F143-1) sees that facets are not a flat pile but cluster into a few coherent families that hand off to one another. Selective, not exhaustive (the `facets/` tree carries many more).

## Layout

- **Anchor base** (top-left): Anchor Page · Anchor Tree · Naming · Folder — the structural foundation every anchor carries.
- **Doc & output** (top-right): Brief · Cards · WP · Doc Site — facets for produced documents and published outputs.
- **Design pipeline** (middle band): PRD · UX Design · Architecture · Testing · Stories · Roadmap — the design-doc family.
- **Track & governance** (bottom band): Backlog · Status · Log · Query · Features — the tracking + governance family.

Two arrows carry the editorial flow: **Anchor base → Design pipeline** (*scaffolds*) and **Design pipeline → Track & governance** (*feeds*). The lifecycle reads top-to-bottom: an anchor's base scaffolds its design docs, which feed its tracking surfaces.

## Color

All cluster zones use the **Facets** color `#ebfbee` (pale green), locked across figures 1–4. Same color → same meaning: everything here is a *facet*.

## What it does NOT contain

- **Not every facet.** The `facets/` tree (FCT Anchor / FCT Design Docs / FCT Track / FCT Doc / FCT Output / FCT Primitives / FCT Dispatch / FCT Code) carries dozens; this names the recognizable spine of each family.
- **No dispatch-table or primitives plumbing** — FCT Dispatch and FCT Primitives are infrastructure, omitted to keep the editorial picture clean.
- **No skill / discipline content** — those are figures 2 / 4.

## Source

`F143-3-facets.d2` (D2). Regenerate exports with `d2 F143-3-facets.d2 F143-3-facets.svg` and `d2 F143-3-facets.d2 F143-3-facets.png`.
