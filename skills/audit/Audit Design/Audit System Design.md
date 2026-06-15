---
description: "How a single audit runs — the resolve → run → judge → fix pipeline, with automation level as a fix-stage parameter and the no-delete safety guard."
---


# Audit System Design

The per-audit pipeline — how one audit executes against a target. [[Audit Architecture]] gives the system's structure (rule sets + components); this page is the flow inside the engine.

![[Audit System Design.svg|2400]]

## The pipeline

A single audit runs four stages over the target (an anchor or a document):

1. **Resolve** — detect the target's facets, flatten their rule sets through `include::` containment, and bind each rule to the target via its `where::` selector. The output is the concrete `(rule × target)` set to evaluate. (Rules that match nothing are N/A — never failed.)
2. **Run** — execute the mechanical rules (`checked` / `sampled` tier) by script, with **content-hash verdict caching** so an unchanged target reuses its prior verdict and re-audits are cheap.
3. **Judge** — hand the `stated` / `sampled` rules that need a human-like read to the agent, which records a pass/fail verdict per rule.
4. **Fix** — apply the fixers the current automation level permits (see below), then **re-run to convergence** so a fix that exposes a second finding is caught in the same pass.

The on-demand `/audit` surface runs all four stages; the online write-hook runs a distilled form of Resolve+Run+Fix pinned to the Online level (the agent is the only judge it has, in the moment).

## Automation level is a parameter on the fix stage

The four levels ([[Audit PRD]] § Automation scale) are not separate engines — they **mask the fixer set** the Fix stage may apply:

- **Informational** — fix stage disabled; emit findings only.
- **Online** — only the corrupting-character fixers (whitespace, escapes, stray angle brackets, table blank lines); structural fixers withheld.
- **Standard** — the full `fix::` set + bounded-judgment fixes.
- **Aggressive** — Standard + structural-refactor fixers.

A future per-anchor setting selects the explicit-pass level; the online hooks are hard-pinned to Online regardless.

## The safety guard

Every fix passes `aow-safety.py` before it lands ([[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]]): the document's alphanumeric sequence must survive the fix as a subsequence. A repair that would drop any letter or digit is **reverted on disk and downgraded to a flag** — the mechanical floor under the never-delete invariant, identical across both trigger modes.

## Format-driven, audit-independent

The engine reads `check::` / `fix::` / `where::` from the specs themselves, so the pipeline never hardcodes a rule — as the facets and disciplines evolve, audit follows with no script edit. The selector grammar (`always` / `file:<glob>` / `anchor` / `sentinel:<regex>`, `{ANCHOR}` / `{NAME}` tokens, backtick-wrapped per [[F007 — Backtick all where expressions — parser swap\|F007]]) is the single binding language shared by the on-demand resolve and the distilled on-write hook.
