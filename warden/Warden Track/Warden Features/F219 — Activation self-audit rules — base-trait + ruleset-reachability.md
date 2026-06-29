---
description: "F219 — Activation self-audit rules — base-trait + ruleset-reachability"
---

# [[Warden]] · F219 — Activation self-audit rules — base-trait + ruleset-reachability

## Summary

Activation is a pure function of an anchor's `.anchor` **traits** ([[Warden Semantics]] § Activation): each trait pulls in its omnibus rulesets, and a trait activates all of its rules. That model has two failure modes — both **closable by Warden auditing its own wiring**, which is the elegant part: the rule engine guards the rule engine.

1. **A trait-less anchor obeys nothing.** If an anchor carries no trait, its active-set is empty and it silently follows no rules.
2. **An orphaned ruleset never fires.** If a ruleset is added but never pulled in by any trait, it is dead — present, authored, and inert.

F219 is the **two self-audit rules** that catch these.

## Success Criteria

**Tier:** 2 — depends on trait-driven activation existing (the per-trait active-set in M1 / [[F211 — Rule compiler and installer|F211]]).
**Blocks next:** none (an integrity backstop).

**What done looks like.**
- **`R-warden-base-trait`** — every anchor carries the **base trait** (so its active-set is never empty; the universal rules always apply). A bare anchor flags.
- **`R-warden-trait-reachable`** — every ruleset in the catalog is **reachable from at least one trait** (pulled in, directly or through `include::`). A ruleset reachable from no trait flags as dead wiring.

**How it will be verified.** A fixture: an anchor with no trait → `R-warden-base-trait` fires; a ruleset wired into no trait → `R-warden-trait-reachable` fires; a correctly-wired anchor + catalog → both silent.

## Design

Both are mechanical (Python `if::`, no LLM):
- **base-trait** — `where:: anchor`; `if::` reads the `.anchor` traits and tests for the base trait.
- **reachability** — `where:: anchor` (or a catalog-level pass); `if::` walks every trait's `include::` closure, unions the reachable ruleset ids, and reports any catalog ruleset not in the union.

Authoring the rule bodies is independent of the activation engine; *running* them meaningfully needs the trait→ruleset wiring (M1) in place, so this lands after it.

## Status

**Later** — backlog; lands after trait-driven activation ([[F211 — Rule compiler and installer|F211]]).
