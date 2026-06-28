---
description: "worked examples of every kind of rule body (start here)"
---
# Warden Examples

One worked ruleset, six complete rules. A rule is **IF a condition (`when` / `where` / `if`) THEN a body** — and the body is one or more **actions**. These examples show every kind of action. How the engine runs them is [[Warden Semantics]]; this is the tour.

![[Warden Examples Ruleset.svg]]

*The example ruleset.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How to read these rules

Each rule **binds** with `where::` (which files), optionally `when::` (which moment), then a **body** that runs over each matched file and may `ctx.report(...)` a problem. Two facts ([[Warden Semantics]] has the full pipeline):

- **The body shows the kind** — a `check::` line is a primitive, a `python` block is code, plain prose is the LLM. There's no tier label; the body already says who decides.
- **No `when::` means passive** — R-ex-01…04 have no `when::`, so they run when **`/audit`** visits their files. R-ex-05 and R-ex-06 declare a `when::` and fire **live**.

Each kind, one at a time:

## 01 · A primitive check

![[Warden Example primitive.svg]]

The body is one action: `check:: regex_present` names a library checker that reports a problem if the pattern is absent — no LLM, verdict content-hash cached. Most structural rules are primitives: effectively free, so run them everywhere. Passive (audit-time).

## 02 · A Python check

![[Warden Example python.svg]]

When no primitive fits, the body is a `python` action — `def check(ctx)` walks every H2 section and `ctx.report(...)`s each empty one (no single regex expresses that). Same deterministic, no-LLM result as a primitive; the cost is that arbitrary Python runs on the Python path, not the native hot path.

## 03 · An LLM judgment

![[Warden Example llm.svg]]

"The `## Summary` faithfully reflects `## Design`" needs reasoning, so the body is **prose** — that *is* the prompt. The LLM reads `ctx`, and reports drift it finds. Judgments cost tokens, so Warden batches and caches them (reused until the file changes).

## 04 · Script-assisted (two actions)

![[Warden Example script-assisted.svg]]

The expensive part of a judgment is reading the whole file. The body has **two actions**: a cheap `def prepare(ctx)` hands the LLM only one section (`ctx.section('## Open Questions')`), then the prose judges that slice. **Python prepares, LLM judges** — the cheapest way to do a judgment.

## 05 · A message (a rule that *acts*, not checks)

![[Warden Example message.svg]]

Not every rule checks a file — some just **say something** at a moment. This one fires on `when:: skill:audit-q`, and its body reports a **steer to the agent** ("don't ask the user whether to commit — your Git aspect already decides") instead of bothering the user. This is F180's executable-rule shape: the body's action *is* the message. (`message::` is the literal shorthand when the text is fixed.)

## 06 · Live + gated

![[Warden Example gated.svg]]

`when:: write:markdown` makes it fire **live** on every edit to an architecture doc. Re-reading and re-reasoning on every keystroke-scale edit would **exhaust the agent**, so `rerun:: significant` re-runs the body only when the file changed *significantly* since it last passed.

> [!info] Status — `rerun::`, the `prepare()` hand-off, and `significant` are *designed, not yet built*
> The `check::` / `python` / LLM-prose / `message::` bodies are the established shapes (F180 already runs executable bodies). The script-assisted `prepare()` hand-off and the **`rerun::`** gate are on the [[Warden Roadmap]] (M7) — design in [[F215 — Re-evaluation economy — the significant-edit gate|F215]]. v1 measures "significant" by diff magnitude; M8 adds semantic update levels.

## Rule of thumb

Bind every rule with `where::`; add `when::` only when it should fire live. For the body, reach for the cheapest action that works: **a `check::` primitive if one fits; a `python` body for custom mechanical logic; LLM prose only when it needs the model; script-assisted to keep judgment cheap.** Gate any live, expensive body with `rerun:: significant`.
