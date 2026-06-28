---
description: "F215 — Re-evaluation economy — the significant-edit gate"
---

# [[Warden]] · F215 — Re-evaluation economy — the significant-edit gate

## Summary

Warden instruments almost every edit. For **mechanical** rules that's free. For **LLM-judged** rules it is not — re-reading a file and re-reasoning costs tokens, and doing it on *every* edit (including typo-scale ones) would **exhaust the agent** for no benefit: the diagram didn't go wrong because someone fixed a spelling mistake. F215 adds a **re-evaluation gate** — a rule may declare `rerun:: significant`, and after its first evaluation the expensive body re-runs only when the file has changed *significantly* since it last passed. A **cheap gate decides "significant?"** before any LLM tokens are spent. This is the [[Warden Examples|script-assisted mode]] applied to the *re-run decision*: a cheap script guards an expensive judgment.

## Success Criteria

**Tier:** 1 (design, after M0/M1)
**Blocks next:** none (an optimization; LLM rules work without it, just more expensively)

**What done looks like.** A `stated` rule with `when:: write:markdown` + `rerun:: significant` evaluates fully on first fire; a subsequent typo-scale edit does **not** spend LLM tokens (the gate suppresses it, verdict reused); a structural edit re-triggers a full evaluation. The gate's own cost is negligible (no LLM).

**How it will be verified.** A fixture doc + an expensive rule: edit one word → assert no judgment ran (cache served); edit a whole section → assert the judgment re-ran. A token/where-it-fired log proves the gate's decisions.

## Design

### The clause

`rerun::` is a **re-evaluation policy** on a rule — a cost/economy dimension, *separate from the conjunction* `when ∧ where ∧ if` (which is the truth condition). It governs *how often the truth condition is actually evaluated*, not *whether it holds*.

- `rerun:: always` — re-evaluate on every matching fire (the default; right for cheap mechanical rules).
- `rerun:: significant` — re-evaluate only when the change since the last pass crosses a significance threshold (right for expensive LLM rules).

### What "significant" means — staged

This is fuzzy **verdict-cache invalidation**: today the verdict cache invalidates on exact content-hash change; `rerun:: significant` makes invalidation *threshold-based* instead of exact.

1. **v1 — diff magnitude (cheap, mechanical).** Significance = lines-changed / % of file changed since the last evaluated revision, against a default threshold (tunable per rule, e.g. `rerun:: significant > 15 lines`). A script computes the diff; no LLM. Ships with this feature.
2. **Later — semantic update levels (own milestone).** A cheap classifier rates each edit `typo → wording → structural → semantic`; only edits at/above a rule's declared level re-trigger it (`rerun:: level >= structural`). The classifier is itself a small/cheap model or heuristic, never the full rule. Deferred — see [[Warden Roadmap]] M-later.

### Mechanism

Warden tracks, per `(rule, file)`, the **revision last evaluated** (its content hash + size). When the moment fires, the gate compares the current file to that snapshot via the staged significance measure; below threshold → reuse the cached verdict (zero LLM); at/above → run the body, record the new snapshot. The gate is the cheap half of a [[Warden Examples|script-assisted]] rule.

## Open Questions

1. **Threshold defaults + units.** Lines vs. % vs. token-distance for v1; one global default or per-rule only?
2. **First-fire vs. adopt-time.** Is the "first evaluation" at first matching edit, or eagerly when the rule is installed for an anchor?
3. **Interaction with the plan/verdict caches.** `rerun::` is a relaxation of the existing exact-hash invalidation — confirm it composes cleanly with [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]'s verdict cache rather than forking it.
4. **Per-clause vs. per-rule.** Does `rerun::` belong on the rule, or could a ruleset set a default (like `where::`)? (Leaning: rule-level, with a set default — same precedence shape as `where::`.)

## Status

**Designed 2026-06-27.** Demonstrated in [[Warden Examples]] (`R-ex-04`). Not built — sequenced on [[Warden Roadmap]] after the compiler (M1) and the agent-judgment path (M2/M3); the semantic-update-level stage is a later milestone.
