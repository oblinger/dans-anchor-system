---
description: "F213 — Rust performance implementation + ms budget"
---

# [[Warden]] · F213 — Rust performance implementation + ms budget

## Summary

The **performance implementation** in Rust, owning the fire-time critical path: moment dispatch + compiled-module execution under a hard per-moment **millisecond budget**. The system instruments nearly every tool use and agent action, so the hot path must be negligible — Python's startup + interpretation is too slow for `tool:pre:*`. Rust handles the dispatch + residual-conjunction checks + mechanical fixes; it is **behavior-identical** to the Python reference ([[F212 — Python reference implementation|F212]]), enforced by differential testing. Rules carrying their own Python run via a **resident Python interpreter** the Rust binary queries over IPC — rules preloaded, so a Python body pays a round-trip, not a startup (see Design).

## Success Criteria

**Tier:** 2 (performance hardening)
**Blocks next:** M4 migration ([[Warden Roadmap]])

**What done looks like.** Fire-time p99 meets the per-moment budget ([[Warden PRD]] § Performance: ~2 ms `tool:pre`, ~10 ms `tool:post`) on a representative workload; the differential suite shows **zero** verdict/steer divergence from the Python reference across the golden corpus.

**How it will be verified.** A performance test fails CI on budget regression; the differential harness ([[F214 — Rule-system testing regime|F214]]) runs every fixture through both impls and diffs outcomes byte-for-byte.

## Design

- **Scope to the hot path** — dispatch table from moment → compiled module; residual `where::`/`if::` checks; corrupting-character-safe mechanical fixers (the always-on Online set).
- **Shared interchange** — consume the compiler's portable module representation (the data-table form from F211/F212), not Python source.
- **Resident Python over IPC (the code-rule path)** — the engine keeps **one logic language**. Native primitives (`check::`) run in-Rust with no interpreter. A rule whose body is *Python* (`def check`/`guard`/`prepare`) is dispatched to a **resident Python interpreter** — rules **preloaded in memory**, queried by the Rust binary over a socket/IPC. The body pays an IPC round-trip, **never an interpreter startup** (the cost that blows the budget). This replaces the old "post-hoc only / bounded bridge" idea: full Python is available at near-native dispatch cost. (A Rust-reimplemented Python *subset* was rejected — more to build, amputates the language.) See [[Warden Architecture]] §7a.
- **Safety floor** — `aow-safety` invariant enforced in Rust on every fix.

## Open Questions

1. Distribution — the Rust binary + the resident-interpreter process must ship without `~/bin` runtime deps (per the packaged-app rule); where do they live and how are they launched/kept warm?
2. IPC shape + budget — socket vs. shared-memory vs. embedded (PyO3); the round-trip cost a `tool:pre` Python body can afford vs. confining heavy Python bodies to `tool:post`.
3. Build/CI — cross-compilation + the differential gate in the SKA build.

## Status

**Planned** — M3 of [[Warden Roadmap]]. Depends on F212 (the oracle).
