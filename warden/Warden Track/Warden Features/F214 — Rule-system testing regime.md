---
description: "F214 — Rule-system testing regime"
---

# [[Warden]] · F214 — Rule-system testing regime

## Summary

Because the rule system instruments **almost every action**, both correctness and performance regressions are high-stakes — a wrong steer or a slow `tool:pre` is felt on every call. F214 is the heavy, careful test discipline that runs **continuously alongside every milestone**, not after. Five layers, with the **Python↔Rust differential harness** as the primary oracle so neither implementation drifts silently. Follows the dev discipline: when a bug appears, write the failing test first, then fix; tests live in the repo/vault, never `/tmp`.

## Success Criteria

**Tier:** 1 (gates every other milestone)
**Blocks next:** standing — every milestone's "done-when" includes "F214 layers green."

**What done looks like.** Five test layers exist and run in CI; a rule/impl change cannot land if any layer fails; performance regressions and Python↔Rust divergences both fail the build.

**How it will be verified.** Deliberately break (a) a checker primitive, (b) one impl's verdict, (c) the budget — and confirm the unit, differential, and performance layers respectively fail. A clean tree is green.

## Design — five layers

| Layer | Proves | Cadence |
|---|---|---|
| **Unit** | each checker primitive, taxonomy match, guard eval | every commit |
| **Differential (Python ↔ Rust)** | both impls agree on every `(rule, target, moment)` verdict/steer | every impl commit |
| **Golden corpus** | a fixed rules × fixtures set with recorded expected outcomes; catches semantic drift | every commit |
| **Performance** | per-moment p99 vs. budget; regression fails CI | every impl commit |
| **End-to-end / live** | author → adopt → fires at its moment in a real session (generalized F180 smoke test) | per milestone |

**Fixtures** are real anchors and rules (reuse the FEX examples [[HBR]], [[ESR]], `CAE`). The **golden corpus** records expected verdicts/steers so any change surfaces as a reviewed diff. The **differential harness** runs each fixture through both implementations and diffs outcomes.

## Open Questions

1. Golden-outcome storage format + how intentional changes are re-blessed (review gate).
2. The performance workload — a synthetic "instrument every tool" trace vs. recorded real sessions.
3. CI home — where the rule-system suite runs (SKA build vs. a dedicated runner) and how the Rust + Python toolchains are provisioned.

## Status

**Defined 2026-06-26** (this doc + [[Warden Roadmap]] § Testing regime). Stands up incrementally with M1–M3; the differential harness lands with F212/F213.
