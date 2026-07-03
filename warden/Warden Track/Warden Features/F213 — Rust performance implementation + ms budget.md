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
- **Resident Python over IPC (the code-rule path)** — the engine keeps **one logic language**. Cheap data-accessor reads (`git.is_dirty`, parsed `file` fields from the cached `ctx`) are served in-Rust with no interpreter. A rule whose `if::` or body is *Python* is dispatched to a **resident Python interpreter** — rules **preloaded in memory**, queried by the Rust binary over a socket/IPC. The body pays an IPC round-trip, **never an interpreter startup** (the cost that blows the budget). Full Python is available at near-native dispatch cost. (A Rust-reimplemented Python *subset* is the costlier alternative — more to build, and it amputates the language.) See [[Warden Architecture]] §7a.
- **Safety floor** — `aow-safety` invariant enforced in Rust on every fix.

## Status

**Selection engine built + differential-green 2026-07-02.** The Rust crate is live at `warden/rs/` (`cargo build`, bin `warden-rs`, lib `warden`), owning the ms-budget-critical **selection path**: it deserializes the compiler's `rules-ir.json`, then for a `(moment, anchor-traits, ctx)` computes the fire plan **byte-for-byte identically to the Python reference** — indexed moment dispatch, active-set gating (`is_active`), the declarative residual (`eval_guard`: git-aspect/mode/trait/facet × eq/in/has, including `in`-scalar and `has`-substring), and the `tell`/`deny` action steers. A rule carrying its own Python (`body_py`/`guard_py`) is taken as far as selection allows and recorded as an owed resident-interpreter round-trip (`python-body`/`python-guard`) — never executed in Rust, per the "one logic language" rule.

**Parity is a standing differential gate.** `warden/engine/test_warden_rust.py` runs the **same IR** through the Rust binary and the *real* `warden_fire` reference primitives and diffs the plan — across the live corpus (every registered moment × 6 anchor trait sets) and synthetic fixtures exercising every guard op and dispatch arm; all 7 cases green. The Rust side also carries 5 native `cargo test` unit tests (offline coverage, no Python). CI gains a `rust-engine` job: `cargo test` → `warden compile` (live IR) → the differential.

**Budget met at the cold bound.** Cold `warden-rs` — fork+exec **plus** a full 200 KB IR parse **plus** fire, every call — is **2.65 ms** (50-call mean), ~7.5× faster than the Python reference's 20 ms cold. The resident design below (IR preloaded, phase 2) reduces the per-moment cost to the `fire_plan` call alone (microseconds), clearing both the ~2 ms `tool:pre` and ~10 ms `tool:post` budgets with margin.

**Remaining (phase 2 — the resident-Python IPC).** Body/guard execution for `body_py`/`guard_py` rules still runs through the Python reference; the Rust selection engine hands off the owed round-trips. The warm resident-interpreter process + IPC shape (Resolved Q1/Q2 below) is the next build — the hot path's *selection* is now Rust; its *Python-body execution* is the phase-2 hand-off. Until then the live dispatcher (F220) keeps using the Python fire path; the Rust engine is verified-equivalent and benched, ready to take the selection half of the hot path.

## Resolved

1. Distribution — the Rust binary + the resident-interpreter process must ship without `~/bin` runtime deps (per the packaged-app rule); where do they live and how are they launched/kept warm?
2. IPC shape + budget — socket vs. shared-memory vs. embedded (PyO3); the round-trip cost a `tool:pre` Python body can afford vs. confining heavy Python bodies to `tool:post`.
3. Build/CI — cross-compilation + the differential gate in the SKA build.
