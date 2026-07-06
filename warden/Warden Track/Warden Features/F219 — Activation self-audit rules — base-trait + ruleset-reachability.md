---
description: "F219 — Activation self-audit rules — base-trait + ruleset-reachability"
---

# [[Warden]] · F219 — Activation self-audit rules — base-trait + ruleset-reachability

## Summary

Activation is a pure function of an anchor's `.anchor` **traits** ([[Warden Semantics]] § Activation): each trait pulls in its omnibus rulesets, and a trait activates all of its rules. The **base trait is implicit** (auto-applied to every anchor, never declared — user 2026-07-02), which **closes the "trait-less anchor obeys nothing" failure by construction**: an anchor with no declared trait still obeys the base trait's always-on rules. That leaves **one** failure mode to audit — the elegant part is that the rule engine guards its own wiring:

- **An orphaned ruleset never fires.** If a ruleset is added but never pulled in by any trait (nor the base trait), it is dead — present, authored, and inert.

F219 is the **reachability self-audit rule** that catches it. *(A base-trait-present check is no longer needed: with the base trait applied by construction there is nothing to forget. `R-warden-base-trait` returns only if a later engine ever makes the base trait declarable.)*

## Success Criteria

**Tier:** 2 — depends on trait-driven activation existing (the per-trait active-set in M1 / [[F211 — Rule compiler and installer|F211]]).
**Blocks next:** none (an integrity backstop).

**What done looks like.**
- **`R-warden-trait-reachable`** — every ruleset in the catalog is **reachable from at least one trait** (pulled in, directly or through `include::`; the implicit base trait counts). A ruleset reachable from no trait flags as dead wiring.
- *(Retired: `R-warden-base-trait`. The base trait is applied by construction — [[Warden Semantics]] § Activation — so "anchor lacks the base trait" cannot occur. Reinstated only if the base trait ever becomes declarable.)*

**How it will be verified.** A fixture: a ruleset wired into no trait → `R-warden-trait-reachable` fires; a correctly-wired catalog → silent. An anchor with no *declared* trait still obeys the base trait (no finding — correct behavior, not a gap).

## Design

Mechanical (Python `if::`, no LLM):
- **reachability** — `where:: anchor` (or a catalog-level pass); `if::` walks every trait's `include::` closure **plus the implicit base trait's**, unions the reachable ruleset ids, and reports any catalog ruleset not in the union.

Authoring the rule body is independent of the activation engine; *running* it meaningfully needs the trait→ruleset wiring (M1) in place, so this lands after it.

## Status

**Built + LIVE 2026-07-05** (M1 shipped 2026-07-02, so the gate had cleared). Realized as the design's catalog-level pass split across compile and fire: `warden compile` stamps the vault's wiring ground truth into the IR (`declared_traits` — every trait some `.anchor` declares, plus the implicit `_base`; `warden_compile.declared_anchor_traits`, one ~0.5 s walk per compile, vault root from `WARDEN_VAULT` env → nearest `kmr` ancestor → scan root), and **`R-warden-dev-02`** ([[Warden Dev Ruleset]]) audits the snapshot at `session:start` in the Warden anchor — a microsecond dict computation over the IR, well inside the hook budget. A trait keying a *moment* rule that no anchor declares is dead wiring (doc-rules fire by `where::` glob on the audit path and need no trait); `warden-selftest` is exempt as the hermetic test-fixture trait.

**The rule proved itself on first run**: `query` — the trait keying `R-query-14`, the original pilot autofire steer — was declared by **no anchor in the vault**, so the flagship rule could never pass `is_active` live (the same silent-inert failure class F209's no-orphan sweep caught on the moment axis, now caught on the trait axis). Fixed by the Warden anchor adopting `query` in its `.anchor` (dogfood — it runs the queries workflow); vault-wide adoption rides the M4 migration when the bespoke audit-q hook retires. Verified: fixture in `test_warden_compile.py` (dead trait fires, wired catalog silent, doc-only trait not flagged, selftest exempt) + live `session:start` at the Warden anchor silent post-fix. `R-warden-base-trait` stays retired (base trait applied by construction).
