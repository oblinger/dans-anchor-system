# RULESET R-exception-discipline
include::
description:: Accepted rule-violations are catalogued as numbered, graded exceptions with a stated justification — audits re-run mechanically and fail on ungraded regressions.

Recurs in HA + MUX + the R-ob enforcement idiom. HA: "Exceptions are numbered (EX001, EX002, …) with grades and For/Against justification"; every accepted site carries an inline `EX<n>` comment. MUX: "Scanner … Exception table destructively rewritten each run" with High/Medium/Low graded findings. [[R-ob-observability]]-01 already requires it per-rule ("listed in an Exceptions table with a grade + justification") — this family generalizes the idiom so any adopted ruleset can lean on it. It is also exactly the enforcement shape Warden's audit tier automates; upgrading this family gives Warden the canonical statement of the discipline it enforces.

### RULE R-exception-discipline-01 — Accepted violations live in a numbered exception table (checked)

Each discipline's accepted deviations are enumerated in an exceptions table with globally-unique numbers (EX001…). A violation neither fixed nor listed is an open finding, not an exception.

### RULE R-exception-discipline-02 — Every exception carries a grade + justification (checked)

Each entry is graded (A–F or High/Medium/Low per the adopting project's convention) with a one-line justification for NOT taking the strict fix. Ungraded exceptions are unreviewed debt.

### RULE R-exception-discipline-03 — Audits re-run mechanically and fail on ungraded regressions (stated)

The discipline has a scanner (or Warden rule) that re-runs on demand; a new High/Medium finding since the last pass, absent a matching exception entry, fails the audit rather than silently growing the pile.
