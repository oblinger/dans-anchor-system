---
description: "F214 — Rule-system testing regime"
---

# [[Warden]] · F214 — Rule-system testing regime

## Summary

Because the rule system instruments **almost every action**, both correctness and performance regressions are high-stakes — a wrong steer or a slow `tool:pre` is felt on every call. F214 is the heavy, careful test discipline that runs **continuously alongside every milestone**, not after. Five layers, with the **Python↔Rust differential harness** as the primary oracle so neither implementation drifts silently, and the **golden corpus** ([[Warden Corpus]]) as the shared behavioral record every layer draws on. Follows the dev discipline: when a bug appears, write the failing test first, then fix; tests live in the repo/vault, never `/tmp`.

## Success Criteria

**Tier:** 1 (gates every other milestone)
**Blocks next:** standing — every milestone's "done-when" includes "existing F214 layers green."

**What done looks like.** Five test layers exist and run as gates; a rule/impl change cannot land if any live layer fails; performance regressions and Python↔Rust divergences both fail the build.

**How it will be verified.** Deliberately break (a) a checker primitive, (b) one impl's verdict, (c) the budget — and confirm the unit, differential, and performance layers respectively fail. A clean tree is green. *(The golden layer's version of this check already ran 2026-07-01: tampering a corpus fixture flips the runner to FAIL; restoring it returns PASS.)*

## Design — five layers

Layers accrete along the [[Warden Roadmap]] and never retire — each milestone's done-when includes "existing layers green."

| Layer | Proves | Starts existing | Gate cadence |
|---|---|---|---|
| **Golden corpus** | a fixed cases × expected-verdicts set; catches semantic drift in any engine | **live today** (seeded against the shipped audit engine) | every commit |
| **Unit** | each checker primitive, taxonomy prefix-match, selector parse, guard eval | M6 build (written alongside the engine code) | every commit |
| **End-to-end / live** | author → adopt → fires at its moment through the real hook surface | per milestone from M6 (a slice exists today: `test-audit-on-write.sh`) | per milestone |
| **Differential (Python ↔ Rust)** | both impls agree on every `(rule, target, moment)` verdict/steer | M8 (contract fixed now, at design time) | every impl commit |
| **Performance** | per-moment p99 vs. budget | M8 enforced; M6 records an informational Python baseline | every impl commit |

### Golden corpus — the heart

Lives at [[Warden Corpus]] (`warden/Warden Corpus/`): `cases/<family>-<nnn>-<slug>/` each with `case.yaml` (id, family, mode, target, provenance, `blessed_against`), a self-contained `fixture/` tree, and `expected.json` — the **canonical verdicts**: the full sorted `(rule, target, status)` set, passes included so a rule that silently stops matching surfaces as a diff; engine `detail` strings are informational and excluded from equality. The runner (`harness/run-corpus.py`) copies fixtures to a temp sandbox before running the engine, so the stored corpus never carries a live `.anchor` and vault sweeps see fixtures as inert files.

- **Pass/fail contract — the PASS/FAIL/STALE trichotomy.** `blessed_against` pins a content hash of the flattened rules' verdict-bearing fields. Rules unchanged + verdicts moved = **FAIL** (engine regression, exit 1). Rules changed + verdicts moved = **STALE-DIFF** (expected churn — requires a conscious `--bless`, and the **review gate is the `expected.json` diff in the commit**). Verdicts unchanged = PASS (starred when the rule pin is stale).
- **Minting.** Harvested cases (a real rule + a real minimized violating/compliant file, source rule named) and synthetic cases (one per `when::` family, `where::` selector form, `if::` guard shape, execution mode). Compliant twins pin both directions of drift. Coverage target at M4 corpus-migration: ≥1 golden per rule family and per language construct.
- **Language-freeze coupling.** The language is not yet frozen (M1), so today's cases are written in the shipped RULESET format against the live rule corpus via the `audit-plan` adapter — the only executable semantics that exist. At M1/M4 the cases are re-expressed in frozen Warden language with a **vendored per-case ruleset** (fully hermetic); `blessed_against` then pins the language version. The runner's adapter layer makes that a swap, not a rewrite.
- **Where it runs.** Directly invocable today (`run-corpus.py`); wired as a `just test-corpus` recipe + pre-commit once the CI/recipe home lands (Q1).

### Unit

Pytest suite living next to the engine source (its repo home rides [[Warden Roadmap]] Q1), written with the M6 build: checker primitives, moment-taxonomy prefix matching, `where::` selector parsing and brace expansion, `if::` guard evaluation, cache keys and invalidation. Contract: pytest exit 0. Fixtures are inline strings/paths — anything needing a real file tree graduates to a corpus case.

### Differential (Python ↔ Rust)

The adapter contract is fixed now so both engines are built to it: every engine exposes a run-case entry point on a sandboxed fixture and emits **canonical verdict JSON** — the same canonicalization the golden layer uses (sorted `(rule, target, status)`, anchor-relative paths). The harness runs the entire corpus (plus recorded moment streams once those exist) through both implementations and compares canonical JSON for **byte equality**.

- **Divergence policy: zero tolerance.** Any divergence fails the build. The Python reference is the spec — the fix is a new failing corpus case first, then align Rust; when the Python side is shown to be the bug, fix Python and re-bless through the standard review gate.
- **Where it runs.** Every commit touching either implementation (`just test-diff`; CI per Q1).

### Performance

Measures fire-time per-moment latency of compiled-module dispatch against the [[Warden PRD]] § Performance budgets (p99: ~2 ms `tool:pre`, ~10 ms `tool:post`, ~100 ms `session`).

- **Workload.** A deterministic synthetic "instrument everything" moment trace generated from the corpus fixtures (thousands of moments across `tool:pre` / `tool:post` / `write`), so runs are reproducible; recorded real-session traces are added later, additively, once hook logging exists.
- **Enforcement without flaky CI.** Absolute ms budgets are enforced only on a designated perf host (`just perf`, the pre-merge gate for impl changes): p99 over ≥10k moment samples, warm cache, median of 3 runs. Any shared-runner CI enforces **relative regression** against a committed same-runner baseline with a tolerance band (fail on >25% p99 regression) — never absolute ms on unpinned hardware. Budget-exceedance *policy* (advisory vs. demote-to-audit) is [[Warden PRD]] Q3 / [[Warden Roadmap]] Q3, not re-decided here.
- **Starts.** Enforced at M8; M6 records an informational Python baseline so the Rust speedup and any Python regressions are visible early.

### End-to-end / live

Generalizes the F180 smoke test (`test-audit-on-write.sh` is the existing slice): author a rule → adopt it in a scratch anchor → drive the **real hook surface** (PreToolUse/PostToolUse JSON on stdin) → assert the JSON `deny`/`block`/steer output. Scripted, run as a per-milestone gate from M6 (`just smoke`); at M7 dogfood a live-session variant runs — the rule adopted in a real anchor, observed firing in a real session.

### Fixtures across layers

The corpus fixtures are the common pool: unit tests inline what they can; the golden, differential, and performance layers all consume `cases/`; e2e adopts corpus rules into its scratch anchor. Real anchors (the FEX examples [[HBR]], `ESR`, `CAE`) are the harvesting ground for corpus cases rather than live test targets — cases vendor a minimized copy, so example-anchor churn never moves test results.

## Scaffolded 2026-07-01

[[Warden Corpus]] is live: format doc, the runner (`run-corpus.py` — engine adapter, canonicalization, bless flow, PASS/FAIL/STALE trichotomy), and four seed cases blessed against the shipped `audit-plan.py`: `msg-001-wrong-h1`, `query-001-no-frontmatter`, `query-002-clean` (the compliant twin), `anchor-001-bare` (the anchor-structure verdict surface). The seeds already pinned one live finding: `R-query-04/-08/-13` name checkers that don't exist in `audit-plan.py` (verdict `error: unknown checker`) — now recorded golden behavior, so both fixing those checkers and losing more of them will surface as diffs.

## Open Questions

1. **CI home** — where the suite runs beyond the dev Mac. **(A)** `just` recipes on the dev machine only; defer CI until Warden extracts to its own repo ([[Warden Roadmap]] Q1) and gets Actions with pinned toolchains there. **(B)** Stand up GitHub Actions in ob-skills now. *(Lean: A — the repo-home decision lands first, and CI built here would move with it.)*

## Status

**Design landed 2026-07-01** (this doc; the F214 spec side of [[Warden Roadmap]] M3 — each layer has a concrete contract + fixture plan, and the differential contract is fixed for M6/M8). Golden layer is live with four seed cases against the shipped audit engine. Unit + e2e stand up with the M6 build; differential + performance gates with M8. Defined 2026-06-26.
