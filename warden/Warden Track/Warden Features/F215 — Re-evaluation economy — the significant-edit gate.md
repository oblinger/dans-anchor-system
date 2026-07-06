---
description: "F215 — Re-evaluation economy — the significant-edit gate"
---

# [[Warden]] · F215 — Re-evaluation economy — the significant-edit gate

## Summary

Warden instruments almost every edit. For **mechanical** rules that's free. For **LLM-judged** rules it is not — the body goes to the main (expensive) model, and re-judging on *every* edit (including typo-scale ones) would **exhaust the agent** for no benefit: the diagram didn't go wrong because someone fixed a spelling mistake. F215 is the **re-evaluation gate** that throttles the expensive body — and it rides the ordinary condition language rather than a special clause: **`file.diff`** exposes what changed since the rule last evaluated the file, and a normal `if::` gates the body on it:

```
if:: file.diff.lines > 15      # only (re)judge when the change is non-trivial
```

The cheap `if::` runs before any LLM tokens are spent — the [[Warden Examples|script-assisted]] pattern applied to the *re-run decision*. Between significant changes the engine reuses the cached verdict, so the rule's prior finding still stands.

## Success Criteria

**Tier:** 1 (design, after M0/M1)
**Blocks next:** none (an optimization; LLM rules work without it, just more expensively)

**What done looks like.** An LLM-judged rule with `when:: write:markdown`, a prose body, and `if:: file.diff.lines > 15` evaluates fully on first fire; a subsequent typo-scale edit does **not** spend LLM tokens (the `if::` is false, the cached verdict is reused, the prior finding persists); a whole-section edit re-triggers a full judgment. The gate's own cost is negligible (no LLM).

**How it will be verified.** A fixture doc + an expensive rule: edit one word → assert no judgment ran (cache served) and the finding still shows; edit a whole section → assert the judgment re-ran. A token / where-it-fired log proves the gate's decisions.

## Design

### `file.diff` is the primitive

`file.diff` is the change **since this rule last evaluated** the file (not the current write — that's `event.diff`): `.lines` (count changed), `.text` (unified diff), `.added` / `.removed`. On first pass it is the whole file. Significance is therefore expressible in plain Python — `file.diff.lines > 15`, `len(file.diff.added) > 3`, `'## Summary' in file.diff.text` — so the author gates on exactly the change property that matters, in the same language as every other condition.

### What "significant" means — staged

1. **v1 — diff magnitude (cheap, mechanical).** `file.diff.lines` / % of file changed — a script computes the diff, no LLM. Ships with this feature.
2. **Later — semantic update levels (own milestone).** A cheap classifier rates each edit `typo → wording → structural → semantic`, exposed as `file.diff.level`, so a rule can gate `if:: file.diff.level >= 'structural'`. The classifier is a small/cheap model or heuristic, never the full rule. Deferred — see [[Warden Roadmap]] M-later.

### Mechanism — and the persistence subtlety

Warden tracks, per `(rule, file)`, the **revision last evaluated** (content hash + size), against which `file.diff` is computed. When the `if::` gate is **false** (sub-threshold), the body is not run — and the engine **reuses the cached verdict** rather than reading the silence as a pass. That last point is the crux for the *audit* path: a still-present finding must not be cleared by a one-line edit elsewhere in the file. (Live steers have no such issue — emitting nothing on a small edit is exactly right.)

## Resolved

All four were engine-policy calls (reversible, agent-domain) — resolved agent-side 2026-07-05 at build time:

1. **Verdict persistence when throttled — RESOLVED: per-(rule, file) reval record.** ^F215-Q1
   The store keeps, per `(rule_id, file_path)`: the content hash + text of the **last-evaluated revision** and the **verdict that evaluation produced**. When the gate suppresses re-judgment, the engine serves that stored verdict (the finding persists — silence is never read as a pass); a full evaluation overwrites the record wholesale (new hash, new text, new verdict). The stored hash identifies exactly which revision the verdict speaks for.
2. **Threshold defaults + units — RESOLVED: no engine default; `.lines` is the v1 unit.** ^F215-Q2
   The gate is ordinary authored `if::` — an engine-imposed default threshold would be a hidden heuristic (the no-heuristics rule). Ratios/percent compose in plain Python (`file.diff.lines / max(len(file.lines), 1)`); token-distance is deferred with the semantic-levels stage.
3. **First-fire vs. adopt-time — RESOLVED: lazy, at first matching fire.** ^F215-Q3
   On first pass `file.diff` is the whole file, so any positive threshold passes and the rule evaluates fully — no adopt-time eager sweep (which would force target enumeration at install for no benefit).
4. **Interaction with the plan/verdict caches — RESOLVED: no fork.** ^F215-Q4
   [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]'s audit verdict cache covers the mechanical doc-fire path, which stays cheap and un-gated. The reval store gates only python/oracle bodies on the **moment** path. `ask_oracle`'s prompt-hash cache remains the inner layer — a re-judgment whose prompt is unchanged still hits it.

## Status

**Built 2026-07-05.** `warden_reval.py` (RevalStore + `FileView`/`DiffView`), compiler residual-`if::` guard emission + `file_bearing` mark, per-rule `ctx.file` binding in `warden_fire.fire` with mark-evaluated after body execution, `file_path` plumbed through the Python hook, the daemon `fire_rules` request, and the Rust dispatcher. `test_warden_reval.py` pins the Success Criteria fixture (first fire evaluates fully; a typo-scale edit spends no body execution and serves the cached verdict; a section-scale edit re-judges). Earlier: designed 2026-06-27; reframed 2026-06-29 to `file.diff` + `if::` (no separate `rerun::` clause); demonstrated in [[Warden Examples]] (`R-ex-04`). The semantic-update-level stage (`file.diff.level`) remains a later milestone.
