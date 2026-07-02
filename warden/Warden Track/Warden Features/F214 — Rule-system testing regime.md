---
description: "F214 — Rule-system testing regime"
---

# [[Warden]] · F214 — Rule-system testing regime

## Summary

Because the rule system instruments **almost every action**, both correctness and performance regressions are high-stakes — a wrong steer or a slow `tool:pre` is felt on every call. F214 is the heavy, careful test discipline that runs **continuously alongside every milestone**, not after. Five layers, with the **Python↔Rust differential harness** as the primary oracle so neither implementation drifts silently, and the **golden corpus** ([[Warden Corpus]]) as the shared behavioral record every layer draws on. Each layer carries a **stated coverage goal** (§ Coverage goals) so "enough testing" is a fixed target we can check the built suite against, not a per-commit judgment call. Follows the dev discipline: when a bug appears, write the failing test first, then fix; tests live in the repo/vault, never `/tmp`.

## Success Criteria

**Tier:** 1 (gates every other milestone)
**Blocks next:** standing — every milestone's "done-when" includes "existing F214 layers green."

**What done looks like.** Five test layers exist and run as gates; a rule/impl change cannot land if any live layer fails; performance regressions and Python↔Rust divergences both fail the build; and each layer meets its stated coverage goal (§ Coverage goals — every primitive tested, ≥1 golden per rule family, one live flow per firing surface, 100% differential, every budgeted moment measured).

**How it will be verified.** Deliberately break (a) a checker primitive, (b) one impl's verdict, (c) the budget — and confirm the unit, differential, and performance layers respectively fail. A clean tree is green. *(The golden layer's version of this check already ran 2026-07-01: tampering a corpus fixture flips the runner to FAIL; restoring it returns PASS.)*

## Design — five layers

Layers accrete along the [[Warden Roadmap]] and never retire — each milestone's done-when includes "existing layers green." (*When* each layer comes online is a roadmap concern — stated in each layer's section below and in [[Warden Roadmap]] — not a design property, so it is not a column here.)

| Layer | Proves | Coverage goal | Gate cadence |
|---|---|---|---|
| **Golden corpus** | a fixed cases × expected-verdicts set; catches semantic drift in any engine | ≥1 case per **rule family** and per **language construct** (each `when::`/`where::`/`if::` form + execution mode), every family with a compliant twin | every commit |
| **Unit** | each checker primitive, taxonomy prefix-match, selector parse, guard eval | **every checker primitive + every compiler/eval method** has a direct test; ≥90% line/branch coverage of the engine core | every commit |
| **End-to-end / live** | author → adopt → fires at its moment through the real hook surface | ≥1 full author→adopt→fire flow **per firing surface** (`tool:pre` veto, `tool:post` steer, `write`, `session`, `prompt:stop`); every hook-output shape (`deny`/`block`/steer) exercised | per milestone |
| **Differential (Python ↔ Rust)** | both impls agree on every `(rule, target, moment)` verdict/steer | **100% of corpus cases** (+ recorded moment streams) byte-equal across both engines — zero exceptions | every impl commit |
| **Performance** | per-moment p99 vs. budget | **every budgeted moment class** (`tool:pre`, `tool:post`, `session`) has a measured p99 each run | every impl commit |

### Coverage goals — the completeness bar we test against

*(added 2026-07-02, user request)* Naming a coverage goal per layer gives a **fixed target to hold the built suite against**: read the goal, look at what exists, decide whether the testing we anticipated is actually there. Goals are concrete where a number earns its keep, qualitative where a number would be false precision.

- **Golden corpus — breadth of behavior** — ≥1 blessed case for **every rule family** and **every language construct** (each `when::` moment family, each `where::` selector form, each `if::` guard shape, each execution mode), plus a **compliant twin** per family so both directions of drift are pinned. Complete when a new rule family shipping *without* a golden is the exception that stands out. (Same target as the golden § minting rule; enforced at the M4 corpus migration.)
- **Unit — every primitive, every branch** — every checker primitive and every compiler/evaluator method carries **≥1 direct test** (method-level coverage is the floor, not the aspiration), and the engine-core modules hold **≥90% line/branch coverage**. Complete when no checker primitive ships untested and coverage never regresses below the floor.
- **End-to-end / live — every firing surface, every output shape** — at least **one full author→adopt→fire flow per firing surface** (`tool:pre` veto, `tool:post` steer, `write:<kind>`, `session`, `prompt:stop`) and **every distinct hook-output shape** (`deny`, `block`, plain steer) driven through the real hook JSON at least once. Complete when every surface a rule can bind to has a green live flow; the flow count grows with the taxonomy, not a fixed number.
- **Differential — total, no sampling** — **100% of corpus cases** (and, once they exist, recorded real-session moment streams) run through **both** engines with byte-equal canonical verdicts. Coverage is inherited from the golden corpus; the differential goal is simply that *no case is skipped* and zero divergence is tolerated.
- **Performance — every budgeted moment** — **every moment class carrying a PRD budget** (`tool:pre`, `tool:post`, `session`) has a measured p99 on each perf run; a budgeted class with no measurement is a coverage gap. Sample depth + host are fixed by the Performance § enforcement rules.

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

## Status

**Design landed 2026-07-01** (this doc; the F214 spec side of [[Warden Roadmap]] M3 — each layer has a concrete contract + fixture plan, and the differential contract is fixed for M6/M8). Golden layer is live with four seed cases against the shipped audit engine. Unit + e2e stand up with the M6 build; differential + performance gates with M8. Defined 2026-06-26.

**First unit test landed 2026-07-02** ahead of M6: the [[F211 — Rule compiler and installer|F211]] scan command ships with `warden/engine/test_warden_scan.py` (5-behavior standalone regression test) — the unit layer's first case, pinning the discovery sweep's read-0-on-unchanged property. Engine modules test alongside the build as they land, not in one M6 batch.

## Resolved

- **Q1 — CI home** — **Resolution (user, 2026-07-01): (B) — stand up GitHub Actions in ob-skills now.** Rationale: good practice getting the rig built; migrating a working workflow to the extracted Warden repo later is trivial. Overrides the filed Lean (A). Realized as `.github/workflows/warden-tests.yml` — golden-corpus job on push/PR touching `warden/**` or the audit engine, plus manual dispatch; the runner's exit code is the gate. Future layers (unit at the build milestone, differential+perf at the Rust milestone) join the same workflow.
