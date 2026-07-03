---
description: "F212 — Python reference implementation"
---

# [[Warden]] · F212 — Python reference implementation

## Summary

The **reference implementation** of the whole compile→install→fire loop in Python: clear over fast, the executable spec. It owns authoring-time compilation, the agent-judgment path, and the execution of rules' own Python `trigger`/`guard`. It is the **behavioral oracle** — the Rust performance implementation ([[F213 — Rust performance implementation + ms budget|F213]]) is validated against it by differential testing, so neither can drift silently. It builds directly on today's `audit-plan.py` (already the Python Resolve→Run→Judge engine).

## Success Criteria

**Tier:** 1 (agent-immediate, after F211)
**Blocks next:** [[F213 — Rust performance implementation + ms budget|F213]]

**What done looks like.** The full loop runs in Python: resolve active set → compile per-moment modules → install → fire on a simulated moment stream → emit steers/fixes. All M0–M1 rules fire correctly; the differential harness ([[F214 — Rule-system testing regime|F214]]) records golden outcomes.

**How it will be verified.** The golden-corpus suite (rules × fixtures × moments → recorded verdicts/steers) passes; the ported `R-query-14` fires identically to today's `audit-q.py` autofire.

## Design

- **Reuse** the existing `audit-plan.py` resolver/flattener/selector as the compiler's front half.
- **Add** the moment-indexer, per-moment module builder, an in-process moment dispatcher (simulating the hook surface), and the steer/fix emitter.
- **Expose** a stable verdict/steer API the differential harness snapshots.
- Clarity-first: this is the spec, so readability and exhaustive comments over micro-optimization.

## Status

**Reference loop built 2026-07-02** — `warden/engine/warden_engine.py` (`WardenEngine`) ties the three stages into the single lazy compile→install→fire loop: lazy warm-start (compile the corpus on first fire, memoise for the session — M1 Q1); `fire(anchor_root, moment)` assembles the moment `ctx`, resolves the anchor's active-set from its `.anchor` traits, and dispatches; `run_moments` fires a simulated moment stream. It is a thin composition of the shipped stages (`warden_scan` + `warden_compile` + `warden_fire`) — **one** implementation of each, no parallel engine — so it *is* the behavioral oracle [[F213 — Rust performance implementation + ms budget|F213]] differential-tests against. The real `R-query-14` fires end-to-end through it (`test_warden_engine.py`, green).

**Both fire paths owned 2026-07-02** — `warden/engine/warden_docfire.py` adds the **doc-audit fire path** (the where-major tier doc-rules the compiler records under `doc_rules`), and `WardenEngine.fire_audit(target, mode)` exposes it, so the one reference engine now owns *both* surfaces: the live moment stream **and** the `/audit doc|anchor` pass. It is **IR-driven** — each rule is round-tripped through `warden_compile.compile_rule` into a doc-rule row and executed from that row's declarative `check` action — proving the compiled IR is a faithful executable representation, not just a description. **Verdict-identical to `audit-plan --run`:** the golden corpus ([[Warden Corpus]]) now runs through a `warden` engine adapter and matches the audit-plan-blessed `expected.json` verdict-for-verdict (4/4 cases, same rule-corpus signature), and `test_warden_docfire.py` is a standing **differential test** (warden ≡ audit-plan on every case + signature parity — the F214 differential layer, now with a real second engine). This is the concrete M4 seam: the checker *implementations* stay audit-plan's (referenced by name through `run_checker`), so folding the audit surface onto the compiler adds no parallel checker code. **This satisfies the "golden-corpus suite passes" Success Criterion.**

Remaining M2 work: the stable verdict/steer **snapshot API** the differential harness records (the corpus adapter is the doc-side of this — the moment-side steer snapshot is still to formalise), and mapping the in-process dispatcher to real hook events (Resolved #2) for the e2e layer. Reuses `audit-plan.py` (F001, shipped) for the checker registry the `check::` doc-rule actions reference.

## Resolved

1. ~~Module representation that is *also* faithfully portable to Rust~~ — **RESOLVED** by the [[F211 — Rule compiler and installer|F211]] § IR schema (2026-07-02): shared `rules-ir.json` data-table (declarative surface, both engines interpret it) + emitted `rules_<anchor>.py` module (arbitrary Python clauses). Not Python-only source emission — the table is the portable interchange.
2. How the in-process dispatcher maps to the real harness hook events (PreToolUse/PostToolUse/SessionStart) for the e2e tests.
