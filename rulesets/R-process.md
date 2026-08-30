# RULESET R-process
description:: Process rulesets — feature lifecycle, verification tiers, state transitions. Adopt the umbrella to pull all process rulesets.
include:: [[R-design-gate]], [[R-stable-ids]], [[R-exception-discipline]], [[R-wrapper-cli]] 

> **None of the four children declares a `where::`, because the scope they want cannot be written — 2026-08-11 ([[Tink Backlog#^T349|T349]]).** *"Adoption stays per-application via `.anchor` traits"*, below, names a condition the selector grammar has no kind for; the four available kinds are `always`, a path glob, `anchor` and `sentinel:`. So all four inherit `always` today. Shared with [[R-arch]]'s five children and `R-mac` — ten sets, 40 rules — and filed as [[Tink Backlog#^T350|T350]], which proposes adding the kind rather than guessing ten globs.

Four children, upgraded from the [[Design-Rules Catalog Proposal]] 2026-07-05 (F218 Q3 = upgrade all): [[R-design-gate]] (4 rules — SVP M15 canonical), [[R-stable-ids]] (4), [[R-exception-discipline]] (3), [[R-wrapper-cli]] (3) — each mined with ≥3-project recurrence evidence. Adoption stays per-application via `.anchor` traits. Still-awaited candidates: `R-feature-lifecycle` (Designing → Ready → Active → Verify → Done), `R-verification-tiers`.
