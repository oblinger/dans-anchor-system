---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, five rules — each a different way a rule's "what to check" is written and run. A Warden rule isn't decided the same way every time: some are a one-line **named primitive**, some carry their own **Python**, some are **judged by the LLM**, and some combine a cheap script with the LLM. This page walks through all of them.

![[Warden Examples Ruleset.svg]]

*One ruleset, five rules.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How a check is written

The executable part of a rule is written one of two ways — and which one you can use is mostly about **speed**:

- **A named `check::` primitive** (`check:: regex_present …`) — a curated checker from Warden's library. Fast and native, so it can run on the hot (Rust) path. Use it whenever a primitive fits.
- **An embedded ` ```python ` block** (`def check(ctx)` / `def prepare(ctx)` / `def trigger(ctx)`) — arbitrary logic when no primitive fits. Maximally flexible, but arbitrary Python runs on the Python path (post-hoc, not the fastest hot path). This is the same executable-rule mechanism F180 already uses for steer messages.

Plus the LLM, for anything that needs *reasoning* rather than a *pattern*. Note every glob / regex value is wrapped in **backticks** — the standing convention ([[F007 — Backtick all where expressions — parser swap|F007]]) so the expression can't trip Obsidian's renderer; the parser strips the backticks.

## The five rules

| # | Rule | "What to check" is… | Who decides | Cost |
|---|---|---|---|---|
| 01 | Has a description | a **`check::` primitive** | script (hot path) | ~free |
| 02 | Custom mechanical check | **embedded `python`** `def check(ctx)` | script (Python path) | ~free |
| 03 | Summary matches the body | **prose** | the LLM reads + reasons | tokens |
| 04 | Open Questions still open | **embedded `python`** `def prepare(ctx)` → prose | Python narrows, then LLM judges the slice | reduced tokens |
| 05 | Diagram matches prose | prose + **`rerun:: significant`** | the LLM, only on significant change | amortized |

### 01 · Mechanical, by primitive — `R-ex-01`
`check:: regex_present \`^description::\`` names a library primitive; the script answers pass/fail with no LLM and the verdict is content-hash cached. Most structural rules are primitives — effectively free, so run them everywhere.

### 02 · Mechanical, by Python — `R-ex-02`
When no primitive fits, the rule carries its own check as an embedded ` ```python ` block: `def check(ctx) -> bool`. Same *result* as a primitive (a mechanical pass/fail), but arbitrary — it can do anything Python can. The cost is that arbitrary Python runs on the Python path, not the native hot path.

### 03 · Judgment — `R-ex-03`
"The `## Summary` faithfully reflects `## Design`" can't be a regex or a tidy function — it needs reading and reasoning. So there's **no code**: the LLM reads both sections and judges, returning pass/fail + reason. Judgment rules cost tokens, so Warden batches and caches them (a verdict is reused until the file changes).

### 04 · Script-assisted — `R-ex-04`
The expensive part of a judgment rule is usually *reading the whole file*. `R-ex-04`'s embedded `def prepare(ctx)` is cheap Python that hands the LLM **only the slice it needs** (`ctx.section('## Open Questions')`); the LLM then reasons over a paragraph, not the document. **Python prepares, LLM judges** — the bridge between the two pure modes, and the most token-efficient way to do a judgment rule.

### 05 · Judgment, gated — `R-ex-05` (the re-evaluation economy)
`R-ex-05` is an expensive LLM rule that *could* fire on every edit to an architecture doc (`when:: write:markdown`). Re-reading and re-reasoning on every keystroke-scale edit would **exhaust the agent** for no benefit. So it adds **`rerun:: significant`**: after the first evaluation the body re-runs only when the file changed *significantly* since it last passed — a cheap gate decides "significant?" before any LLM tokens are spent.

> [!info] Status — `rerun::`, `prepare()`/script-assisted, and `significant` are *designed, not yet built*
> Modes 01–03 are the established shape (primitive checks, embedded-Python executables per F180, LLM judgment). The script-assisted `prepare()` hand-off and the **`rerun::`** gate are on the [[Warden Roadmap]] (M7) — design in [[F215 — Re-evaluation economy — the significant-edit gate|F215]]. v1 measures "significant" by diff magnitude; a later milestone (M8) adds semantic update levels. The syntax above is the intended form.

## Rule of thumb

Reach for the cheapest expression that works: **a `check::` primitive if one fits; embedded `python` if you need custom mechanical logic; pure judgment only when it needs the model; script-assisted to keep judgment cheap.** And gate any expensive rule that fires on writes with `rerun:: significant`, so Warden can instrument almost every edit without exhausting the agent.
