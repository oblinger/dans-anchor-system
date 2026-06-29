---
description: "F210 — Conjunction binding (`when ∧ where ∧ if`) + indexing"
---

# [[Warden]] · F210 — Conjunction binding (`when ∧ where ∧ if`) + indexing

## Summary

Defines what a rule *means* and how it gets dispatched. A rule is the **conjunction** of its clauses — `when::` (moment), `where::` (place), and optional `if::` (guard) — and fires only when all hold. `where::` is a deliberately **separate cross-cutting axis** (the same place-predicate recurs under many moments). The author writes only the truth condition; the **engine chooses the dispatch index** — usually by `when::`, sometimes by `where::` — with identical firing semantics either way. This is what lets the system instrument almost every action cheaply.

## Success Criteria

**Tier:** 1 (design + spec)
**Blocks next:** [[F211 — Rule compiler and installer|F211]]

**What done looks like.** The conjunction semantics are specified; the `if::` test (a Python expression over the interpretation environment) is defined; the indexing rule (when-major default, where-major fallback) is specified with the residual-test contract.

**How it will be verified.** Worked examples: a `when:: write:markdown` + `where:: {ANCHOR}/**/*.md` rule, and a `when:: always` + rare-`where::` rule, each shown resolving to the cheaper index with the correct residual check. Guard examples (`if:: git-aspect == Commit`) evaluate correctly.

## Design

- **Truth condition:** `fires ⟺ moment ∈ when:: ∧ target ∈ where:: ∧ guard(ctx)`. (See [[Warden Architecture]] §4.)
- **`where::` cross-cuts** rather than nesting in `when::` — it factors out the place-predicate shared across write/read/audit moments.
- **`if::` guards** — declarative over a fixed context vocabulary (`git-aspect`, `mode`, `trait`, `facet`) compiling to table lookups; Python for the rare arbitrary case. Multiple guards AND.
- **Indexing** — the compiler ([[F211 — Rule compiler and installer|F211]]) picks the index key that guarantees firing most cheaply; the unindexed clauses become the fire-time residual check.

## Resolved

- **`tool:pre` veto — YES, rules may deny.** Per [[Warden Survey]], native `PreToolUse` returns `permissionDecision: "deny"` with a reason fed back to the agent, and `PostToolUse` returns `{decision: "block", reason}`. A `tool:pre` rule may veto an action (gated by the `aow-safety` floor) — not steer-only. Implementation must use **JSON `deny`/`block` output, not exit-code-2** (survey: Claude Code bug #24327). Policy + decision D5: [[Warden Integration Strategy]].

## Open Questions

1. Declarative guard vocabulary — fixed set (`git-aspect`, `mode`, `trait`, `facet`) vs. extensible registry.
2. Does `where::` precedence (rule > set > always) interact with the index choice, or is it resolved before indexing? (Leaning: resolved first.)

## Status

**Drafted 2026-06-26** in [[Warden Architecture]] §4–5. Remaining: pin the `if::` grammar and the veto semantics, then freeze.
