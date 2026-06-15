---
description: "The unified rule-processing engine — rule sources → resolve/run/judge/fix, shared by the explicit pass and the online hooks, gated by the no-delete safety guard."
---

# Audit Architecture

One rule corpus, two consumers. Rules live in the facet/discipline specs; the explicit `/audit` pass and the online write-hooks both read them, differing only in trigger and automation level.

![[Audit Architecture.svg]]

## Components

| Component | Role |
|---|---|
| **Rule sources** | The `# RULESET R-<name>` blocks embedded in facet/discipline specs ([[FCT Ruleset]]). Each rule carries `check::` (detect), optional `fix::` (repair), and `where::` (which targets it applies to). |
| **Resolve** | Detect the target's facets → flatten their rulesets through `include::` → bind each rule to a concrete target via its `where::` selector. The matcher + scheduler ([[F001 — Rule-driven audit engine — resolve, run, judge\|F001]]). |
| **Run** | Execute `checked`/`sampled` rules mechanically by script, with content-hash verdict caching so re-audits are cheap. |
| **Judge** | Hand `stated`/`sampled` rules to the agent for a pass/fail verdict; record it. |
| **Fix** | Apply each `fix::` whose `check::` failed, plus bounded-judgment fixes; re-run to convergence. The fix-by-default stage ([[F002 — Audit fix-by-default + Python rule functions\|F002]]). |
| **/distill** | Compile the applicable rule bodies (built-in primitives + python rules) into one merged module in the config folder — no per-write discovery cost. |
| **Online hooks** | `PostToolUse` on read/write run the merged module against the just-touched file, at the Online level ([[F003 — On-write rule hook + test workflow\|F003]]). |
| **Safety guard** | `aow-safety.py` gates every fix: the document's alphanumeric sequence must survive as a subsequence, else the fix is reverted to a flag ([[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]]). |

## Data flow

1. **Resolve → Run → Judge → Fix** is the explicit pipeline. The target's facets determine the ruleset union; `where::` binds rules to files; mechanical rules run by script (cached), judgment rules by agent; then `fix::` + bounded-judgment repairs apply and the pipeline re-runs until clean.
2. **`/distill`** gathers the same rule bodies into a merged module so the **online hooks** can run them in milliseconds on every write — the cheap always-on guardrail to the explicit pass's thorough backstop. One `where::` vocabulary serves both.
3. **Every fix passes the safety guard** before it lands. A repair that would drop a letter or digit is reverted and downgraded to a flag — the mechanical floor under the never-delete invariant.

## Automation level as a fix-stage parameter

The four levels ([[Audit PRD]] § Automation scale) are a **parameter on the fix stage**, not separate engines:

- **Informational** — fix stage disabled; resolve/run/judge only, emit findings.
- **Online** — fix stage restricted to the corrupting-character fixers (whitespace, escapes, stray angle brackets, table blank lines); structural fixers withheld.
- **Standard** — full `fix::` set + bounded-judgment fixes.
- **Aggressive** — Standard + structural-refactor fixers.

A future per-anchor setting selects the level; the engine reads it and masks the fixer set accordingly. The online hooks are hard-pinned to Online regardless of the anchor's explicit-pass level.

## Where the rule format lives

The engine is **format-driven and audit-independent**: rules declare their `check::`/`fix::`/`where::` in the specs, and the engine reads them — as specs evolve, audit follows with no script edit. The selector grammar (`always` / `file:<glob>` / `anchor` / `sentinel:<regex>`, `{ANCHOR}`/`{NAME}` tokens; backtick-wrapped per [[F007 — Backtick all where:: expressions — parser swap|F007]]) is the one binding language shared by resolve and the distilled hook.
