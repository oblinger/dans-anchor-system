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

**Phase 2 built + LIVE 2026-07-05 — Rust owns the whole live hot path.** Three pieces, per the resolved design (portable socket daemon, not PyO3):

- **`warden_daemon.py` — the resident interpreter.** A warm Python process holding the compiled IR + rules module **preloaded** (459 rules), serving one-JSON-per-connection requests on `$WARDEN_HOME/daemon.sock`: `fire_rules` (runs each owed rule through the *reference* fire path with a single-rule bucket — semantics are `warden_fire.fire`'s by construction, returned per-rule so the caller re-interleaves into bucket order), `audit` (the F222 doc-fire, warm — the audit-plan import happens once per daemon lifetime, not per write), plus `ping`/`reload`/`shutdown`. Artifacts auto-reload on mtime change; idle-exit (default 30 min) + respawn-on-demand means no stale process lingers. Fail-safe per request.
- **`warden-rs hook` — the live dispatcher in Rust.** The full `warden_hook.py` hot path ported: kill switch first, event→moments, anchor walk + trait sensing, **selection via the differential-tested `fire_plan`**, declarative steers emitted in-Rust; `body_py`/`guard_py` rules cross to the daemon as an IPC round-trip and their steers re-interleave into exact Python fire order; audit-on-write rides the same socket. Daemon down + round-trip owed → spawn from `$WARDEN_HOME/daemon.cmd` (written by `warden compile`) with a short warm-up retry; a miss skips the owed steers this call (logged), fires next call. Always exits 0.
- **Live wiring.** `warden install --rust` registers the binary in `settings.json` (`warden daemon start|stop|status` manages the resident process). **Installed live 2026-07-05** and verified: `session:start` at the Warden anchor fires `R-warden-dev`'s Python body through the daemon; `WARDEN_DISABLED=1` silences everything.

**Verified.** `test_warden_daemon.py` (protocol + per-rule fire/audit parity against the reference, 5/5) and `test_warden_hook_rust.py` (**differential: identical hook output from both dispatchers** across python-body fires, trait gating, audit-on-write, kill switch, malformed stdin, non-anchor cwd — 7/7); both joined CI. Auto-spawn proven from a cold home (first call steers within the warm-up window). Full suite (8 unit files + both corpus engines) green.

**Benched (mean of 50, end-to-end fork+exec).** Rust hook **2.98 ms** on a no-fire call (the typical case — pure Rust, no daemon contact) and **3.71 ms** when a Python body fires through the daemon, vs the Python hook's 23.6/24.1 ms — ~7× the live path. The `tool:post` ~10 ms budget clears with margin; `tool:pre` sits at the ~3 ms fork+exec bound (the IR parse + selection are microseconds; a persistent-process host would be the next squeeze if ever needed).

## Resolved

1. Distribution — the Rust binary + the resident-interpreter process must ship without `~/bin` runtime deps (per the packaged-app rule); where do they live and how are they launched/kept warm?
2. IPC shape + budget — socket vs. shared-memory vs. embedded (PyO3); the round-trip cost a `tool:pre` Python body can afford vs. confining heavy Python bodies to `tool:post`.
3. Build/CI — cross-compilation + the differential gate in the SKA build.
