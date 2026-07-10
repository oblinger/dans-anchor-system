# RULESET R-arch
description:: Architecture rulesets — patterns for code organization, module structure, dependency direction. Adopt the umbrella to pull all architecture rulesets, or cherry-pick individual sets.
include:: [[R-single-source-of-truth]], [[R-one-path]], [[R-interfaces-folder]], [[R-factory-pegboard]], [[R-ownership]]

Five children, upgraded from the [[Design-Rules Catalog Proposal]] 2026-07-05 (F218 Q3 = upgrade all): [[R-single-source-of-truth]] (3 rules), [[R-one-path]] (3), [[R-interfaces-folder]] (3), [[R-factory-pegboard]] (3), [[R-ownership]] (3) — each mined with ≥3-project recurrence evidence (HA, SVP, MUX, A2X, SKD, SVAR). Adoption stays per-application: an app opts in via its `.anchor` trait list.
