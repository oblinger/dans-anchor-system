---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, five rules — each a different way a rule's "what to check" is written and run. Some are a one-line **named primitive**, some carry their own **Python**, some are **judged by the LLM**, and some combine a cheap script with the LLM. Here's the whole ruleset at a glance:

![[Warden Examples Ruleset.svg]]

*The example ruleset.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How a check is written

The executable part of a rule is written one of two ways — and which one you can use is mostly about **speed**:

- **A named `check::` primitive** (`check:: regex_present …`) — a curated checker from Warden's library. Fast and native, so it can run on the hot (Rust) path. Use it whenever a primitive fits.
- **An embedded `python` block** (`def check(ctx)` / `def prepare(ctx)` / `def trigger(ctx)`) — arbitrary logic when no primitive fits. Maximally flexible, but arbitrary Python runs on the Python path (post-hoc, not the fastest hot path). Same executable-rule mechanism F180 already uses.

Plus the LLM, for anything that needs *reasoning* rather than a *pattern*. Every glob / regex value is wrapped in **backticks** — the standing convention ([[F007 — Backtick all where expressions — parser swap|F007]]) so the expression can't trip Obsidian's renderer; the parser strips them.

Each kind, one at a time:

## 01 · Mechanical, by primitive

![[Warden Example primitive.svg]]

`check:: regex_present` names a library primitive; the script answers pass/fail with no LLM and the verdict is content-hash cached. Most structural rules are primitives — effectively free, so run them everywhere.

## 02 · Mechanical, by Python

![[Warden Example python.svg]]

When no primitive fits, the rule carries its own check as an embedded `python` block — a `def check(ctx)` returning `Pass()`/`Fail(...)`. Same *result* as a primitive (a mechanical pass/fail), but arbitrary: here it walks every H2 section and fails on an empty one — something no single regex expresses cleanly. The cost is that arbitrary Python runs on the Python path, not the native hot path.

## 03 · Judgment, by the LLM

![[Warden Example llm.svg]]

"The `## Summary` faithfully reflects `## Design`" can't be a regex or a tidy function — it needs reading and reasoning. So there's **no code**: the LLM reads both sections and judges, returning pass/fail + reason. Judgment rules cost tokens, so Warden batches and caches them (a verdict is reused until the file changes).

## 04 · Script-assisted

![[Warden Example script-assisted.svg]]

The expensive part of a judgment rule is usually *reading the whole file*. This rule's `def prepare(ctx)` is cheap Python that hands the LLM **only the slice it needs** (`ctx.section('## Open Questions')`); the LLM then reasons over a paragraph, not the document. **Python prepares, LLM judges** — the bridge between the two pure modes, and the most token-efficient way to do a judgment rule.

## 05 · Judgment, gated

![[Warden Example gated.svg]]

An expensive LLM rule that *could* fire on every edit to an architecture doc (`when:: write:markdown`). Re-reading and re-reasoning on every keystroke-scale edit would **exhaust the agent** for no benefit. So it adds **`rerun:: significant`**: after the first evaluation the body re-runs only when the file changed *significantly* since it last passed — a cheap gate decides "significant?" before any LLM tokens are spent.

> [!info] Status — `rerun::`, the `prepare()` hand-off, and `significant` are *designed, not yet built*
> Modes 01–03 are the established shape (primitive checks, embedded-Python executables per F180, LLM judgment). The script-assisted `prepare()` hand-off and the **`rerun::`** gate are on the [[Warden Roadmap]] (M7) — design in [[F215 — Re-evaluation economy — the significant-edit gate|F215]]. v1 measures "significant" by diff magnitude; a later milestone (M8) adds semantic update levels. The syntax shown is the intended form.

## Rule of thumb

Reach for the cheapest expression that works: **a `check::` primitive if one fits; embedded `python` if you need custom mechanical logic; pure judgment only when it needs the model; script-assisted to keep judgment cheap.** And gate any expensive rule that fires on writes with `rerun:: significant`, so Warden can instrument almost every edit without exhausting the agent.
