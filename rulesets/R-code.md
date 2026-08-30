# RULESET R-code
description:: Code-flavored rulesets — language- or platform-specific coding conventions. Not armed: R-mac carries no `where::`, so it defaults to `always`.
include:: [[R-mac]] 

Currently one set materialized: [[R-mac]] (macOS app development — code signing, TCC, sandboxing). Future candidates: `R-rust`, `R-python`, `R-typescript`, `R-shell`.

> **Not armed, and arming it as written would be a mistake with a measured price.** Like every umbrella outside the executing closure ([[Tink Backlog#^T208|T208]], [[Tink Backlog#^T349|T349]]), naming a set here reaches no engine — `audit-plan.py` resolves only [[R-doc]] and [[R-anchor]]. But `R-code` is the case where dormancy has been doing us a favor.
>
> [[R-mac]] declares **no `where::` at all**, and a ruleset without one falls through to `always` — every file in every anchor. Its five rules are labeled `(checked)` and carry no `check::` field, which `_needs_judgment` treats as a membership miss and promotes to billed agent judgment. Measured 2026-08-11 by naming `R-code` in [[R-anchor]] and taking the judgment manifest for one anchor: **984 items before, 1,124 after — 140 new LLM judgments on TINK alone**, asking a documentation anchor with no Swift, no bundle and no build script whether it ad-hoc-signs its app. Every one of the 140 is N/A by construction, and the same multiplier lands on all forty anchors.
>
> Two things must be true before this umbrella is worth arming, and they are independent: `R-mac` needs a `where::` that identifies an anchor which actually builds a `.app` (nothing in the current selector vocabulary does that), and its five rules need either real `check::` refs to match their `(checked)` label or an honest demotion. Neither is a sweep — see T212 for the order the ten umbrellas are being taken in.
