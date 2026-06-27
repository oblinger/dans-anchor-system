---
description: "F213 — Rust performance implementation + ms budget"
---

# [[Warden]] · F213 — Rust performance implementation + ms budget

## Summary

The **performance implementation** in Rust, owning the fire-time critical path: moment dispatch + compiled-module execution under a hard per-moment **millisecond budget**. The system instruments nearly every tool use and agent action, so the hot path must be negligible — Python's startup + interpretation is too slow for `tool:pre:*`. Rust handles the dispatch + residual-conjunction checks + mechanical fixes; it is **behavior-identical** to the Python reference ([[F212 — Python reference implementation|F212]]), enforced by differential testing. Rules carrying their own Python may be confined to post-hoc (non-critical) moments or bridged (see Open Questions).

## Success Criteria

**Tier:** 2 (performance hardening)
**Blocks next:** M4 migration ([[Warden Roadmap]])

**What done looks like.** Fire-time p99 meets the per-moment budget ([[Warden PRD]] § Performance: ~2 ms `tool:pre`, ~10 ms `tool:post`) on a representative workload; the differential suite shows **zero** verdict/steer divergence from the Python reference across the golden corpus.

**How it will be verified.** A performance test fails CI on budget regression; the differential harness ([[F214 — Rule-system testing regime|F214]]) runs every fixture through both impls and diffs outcomes byte-for-byte.

## Design

- **Scope to the hot path** — dispatch table from moment → compiled module; residual `where::`/`if::` checks; corrupting-character-safe mechanical fixers (the always-on Online set).
- **Shared interchange** — consume the compiler's portable module representation (the data-table form from F211/F212), not Python source.
- **Bridge for code-rules** — declarative guards run natively; rules with Python `trigger`/`guard` either run on the post-hoc Python path or via a bounded bridge (decided in F211 Q3).
- **Safety floor** — `aow-safety` invariant enforced in Rust on every fix.

## Open Questions

1. Distribution — the Rust binary must ship without `~/bin` runtime deps (per the packaged-app rule); where does it live and how is it invoked from the hook?
2. Python-bridge cost — is calling into a rule's Python from Rust ever cheap enough for a critical-path moment, or strictly post-hoc?
3. Build/CI — cross-compilation + the differential gate in the SKA build.

## Status

**Planned** — M3 of [[Warden Roadmap]]. Depends on F212 (the oracle).
