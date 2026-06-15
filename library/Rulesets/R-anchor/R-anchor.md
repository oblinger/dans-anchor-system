# RULESET R-anchor
include:: [[R-doc]], [[R-anchor-page]], [[R-naming]], [[R-design]], [[R-roadmap]], [[R-prd]], [[R-status]], [[R-stories]]
description:: Everything checked when auditing a whole anchor — the entry page + naming + planning facets, plus the doc-level rulesets (via R-doc) for every document the anchor contains.

The umbrella that **`/audit anchor <path|slug>`** resolves ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]). Auditing an anchor *includes* auditing its documents, so this umbrella `include::`s [[R-doc]] (markdown / file-association / ruleset / brief / discussion / log / messages) on top of the anchor-structural sets:

- [[R-anchor-page]] — the `.anchor` marker + entry page (`anchor` / `file:` scope).
- [[R-naming]] — file-naming rules across the anchor tree.
- [[R-design]] / [[R-roadmap]] / [[R-prd]] / [[R-status]] / [[R-stories]] — planning facets; each fires only on its own `where::` targets, so an anchor without that facet simply N/A's those rules (selector-miss, never a failure).

Add an anchor-level facet's ruleset to the `include::` line to bring it into `/audit anchor`. Domain-specific facets (code / API / testing / UX / paper / architecture) are intentionally **not** in the general anchor umbrella — they belong to kind-specific umbrellas pulled in when a future selector or anchor-kind warrants them.
