---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, five complete rules — each a different way a rule's verdict is produced. Some are decided by a script (a named **primitive** or embedded **Python**), some are **judged by the LLM**, one combines the two, and one fires **live** on every edit. How the engine actually runs them is [[Warden Semantics]]; this page is the worked tour.

![[Warden Examples Ruleset.svg]]

*The example ruleset.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How to read these rules

Every rule is **complete** — it binds with `where::` (which files), and the verdict comes from an evaluator (a `check::` primitive, a `python` block, or prose for the LLM). Two facts make the set make sense ([[Warden Semantics]] has the full pipeline):

- **The tier in the heading says who decides it.** `(checked)` = a script (primitive *or* python); `(stated)` = the LLM. That's why there's no "· python" / "· LLM" — the tier already says the evaluator class, and the body shows which form.
- **No `when::` means passive.** R-ex-01…04 have no `when::`, so they run when **`/audit`** visits their `where::` targets. Only R-ex-05 declares `when:: write:markdown` — it fires **live** on every edit (and is gated, below).

Each kind, one at a time:

## 01 · Mechanical, by primitive — `(checked)`

![[Warden Example primitive.svg]]

`where::` picks the ruleset files; `check:: regex_present` names a library primitive that decides pass/fail with no LLM, verdict content-hash cached. Most structural rules are primitives — effectively free, so run them everywhere. Passive: checked at audit time.

## 02 · Mechanical, by Python — `(checked)`

![[Warden Example python.svg]]

Still `(checked)` — a script decides it — but when no primitive fits, the rule carries its own `def check(ctx) -> Verdict` (returns `Pass()`/`Fail(...)`). Here it walks every H2 section and fails on an empty one, which no single regex expresses cleanly. Same deterministic result as a primitive; the cost is that arbitrary Python runs on the Python path, not the native hot path.

## 03 · Judgment, by the LLM — `(stated)`

![[Warden Example llm.svg]]

"The `## Summary` faithfully reflects `## Design`" needs reading and reasoning, so there's **no code** — the rule body *is* the prompt. `(stated)` = the LLM evaluator: it reads `ctx` and returns pass/fail + a one-line reason. Tokens cost real money, so Warden batches and caches these (a verdict is reused until the file changes).

## 04 · Script-assisted — `(stated)`

![[Warden Example script-assisted.svg]]

The expensive part of a judgment rule is reading the whole file. This rule's `def prepare(ctx)` is cheap Python that hands the LLM **only the slice it needs** (`ctx.section('## Open Questions')`); the model then reasons over a paragraph, not the document. **Python prepares, LLM judges** — the most token-efficient way to do a judgment rule.

## 05 · Live + gated — `(stated)`

![[Warden Example gated.svg]]

The only rule with a `when::` — `write:markdown` makes it fire **live** on every edit to an architecture doc. Re-reading and re-reasoning on every keystroke-scale edit would **exhaust the agent**, so `rerun:: significant` re-runs the body only when the file changed *significantly* since it last passed; a cheap gate decides "significant?" before any LLM tokens are spent.

> [!info] Status — `rerun::`, the `prepare()` hand-off, and `significant` are *designed, not yet built*
> Modes 01–03 are the established shape (primitive checks, embedded-Python executables per F180, LLM judgment). The script-assisted `prepare()` hand-off and the **`rerun::`** gate are on the [[Warden Roadmap]] (M7) — design in [[F215 — Re-evaluation economy — the significant-edit gate|F215]]. v1 measures "significant" by diff magnitude; a later milestone (M8) adds semantic update levels.

## Rule of thumb

Reach for the cheapest evaluator that works: **a `check::` primitive if one fits; embedded `python` if you need custom mechanical logic; `(stated)` prose only when it needs the model; script-assisted to keep judgment cheap.** Bind every rule with `where::`; add `when::` only when it should fire live; and gate any live, expensive rule with `rerun:: significant`.
