# RULESET R-design-gate
include::
description:: Explicit user sign-off gates sit between design and dependent construction — contracts freeze before dependent code, design signs off before test construction, decisions are ratified before they are policy.

Recurs in SVP + SKD + MUX + HA. SVP M15 (canonical): "Before any test cases are constructed, all of the design documentation and the skeleton source code must be lined up and **presented to the user for approval**. This is a hard gate" (`SVP Track/SVP Roadmap/SVP Milestones.md`). SKD: "Everything gets fully specified before implementation begins" + the Sufficiency Analysis gate. MUX: decisions are "`(open)` … under design / not yet ratified" until user-`checked`. HA: the publish gate — "a fresh `/audit publish` pass MUST run and surface ZERO high-severity findings" (`HA Design/HA PRD.md`).

### RULE R-design-gate-01 — Design sign-off before test construction (stated)

A milestone gate sits between "design docs + skeleton code complete" and "test cases constructed": the package is walked through with the user as one reviewable unit, and test construction is blocked until explicit sign-off. Tests written against an unfrozen design train churn, not correctness.

### RULE R-design-gate-02 — Contracts freeze before dependent code (stated)

Shared data contracts and interfaces are agreed and stamped with an explicit stability tier ("freezes at M-n sign-off") before code that depends on them is written; until the freeze point, breaking changes are expected without notice — and after it, they are events.

### RULE R-design-gate-03 — Decisions are ratified before they are policy (stated)

A recorded design decision carries a status (`open` → user-`checked`); it is not in force as policy until ratified. Status tracks the decision itself, separate from its implementation.

### RULE R-design-gate-04 — Releases gate on a clean audit (stated)

Public releases require a fresh audit pass with zero high-severity findings, and the gate is written into the PRD itself so no release plan can omit it.
