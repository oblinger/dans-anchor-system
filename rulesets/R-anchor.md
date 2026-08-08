# RULESET R-anchor
include:: [[R-doc]], [[R-anchor-page]], [[R-naming]], [[R-design]], [[R-roadmap]], [[R-prd]], [[R-status]], [[R-stories]], [[R-fct-features]], [[R-rocks]], [[R-wp]], [[R-fct-outputs]], [[R-examples]] 
description:: Everything checked when auditing a whole anchor — the entry page + naming + planning facets, plus the doc-level rulesets (via R-doc) for every document the anchor contains.

The umbrella that **`/audit anchor <path|slug>`** resolves ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]). Auditing an anchor *includes* auditing its documents, so this umbrella `include::`s [[R-doc]] (markdown / file-association / ruleset / brief / discussion / log / messages) on top of the anchor-structural sets:

- [[R-anchor-page]] — the `.anchor` marker + entry page (`anchor` / `file:` scope).
- [[R-naming]] — file-naming rules across the anchor tree.
- [[R-design]] / [[R-roadmap]] / [[R-prd]] / [[R-status]] / [[R-stories]] — planning facets; each fires only on its own `where::` targets, so an anchor without that facet simply N/A's those rules (selector-miss, never a failure).
- [[R-rocks]] / [[R-wp]] / [[R-fct-outputs]] — the **folder-shaped** facets, added 2026-08-08 by [[TINK Backlog#^T164|T164]]. Listed here individually rather than by pulling [[R-facet]], because that umbrella also carries the domain-specific sets the paragraph below deliberately keeps out.

Add an anchor-level facet's ruleset to the `include::` line to bring it into `/audit anchor`. Domain-specific facets (code / API / testing / UX / paper / architecture) are intentionally **not** in the general anchor umbrella — they belong to kind-specific umbrellas pulled in when a future selector or anchor-kind warrants them.

**Being listed in [[R-facet]] is not adoption, and that was the T164 defect.** `R-facet` describes itself as the umbrella an anchor "adopts" to commit to every materialized facet's rules — but there is **no per-anchor adoption mechanism**: `audit-plan.py` resolves a fixed umbrella (`R-anchor` for anchor mode, `R-doc` for doc mode) and nothing reads a per-anchor ruleset declaration. So a ruleset reachable only through `R-facet` is outside the closure and never loads, no matter what its own header claims. Measured 2026-08-08: 91 rulesets carry rules, **65 of them are outside the closure**. Adding a facet's rules here is the only thing that arms them.
