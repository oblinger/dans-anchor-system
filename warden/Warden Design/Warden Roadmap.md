---
description: "the build sequence — design → compiler → Python ref → Rust perf → testing regime"
---

# Warden Roadmap

The sequenced build plan for the rule system. The **language design** is largely complete ([[Warden Architecture]], [[Warden Events]], [[FCT Ruleset]]); the runway ahead is the **compiler/installer**, the **two implementations** (Python reference → Rust performance), and a **heavy testing regime** that runs alongside every milestone — not after. Requirements + perf budgets: [[Warden PRD]].

> [!info] How to read this
> Milestones are roughly sequential but the testing regime (M6) is **continuous** — every milestone ships with its tests green before the next starts. Each milestone names its feature doc(s) in [[Warden Features]]. "Done-when" is the gate to the next milestone.

## Milestones

### M0 — Language design  *(in progress — mostly done)*

The declarative surface: what a rule is and how it binds.

| Piece | State | Doc |
|---|---|---|
| Rule + Ruleset format, `include::`, `where::` | done | [[FCT Ruleset]] |
| `when::` clause + executable rules | done (F180) | [[F180 — When-trigger executable rules\|F180]] |
| Unified moment taxonomy | **drafted** | [[Warden Events]], [[F209 — Unified trigger taxonomy + when language\|F209]] |
| Conjunction model (`when ∧ where ∧ if`) + `if::` guards | **drafted** | [[Warden Architecture]] §4–5, [[F210 — Conjunction binding + indexing\|F210]] |

**Done-when:** the taxonomy + conjunction specs are reviewed and frozen; every existing trigger surface (`compact`, `markdown-write`, `skill:*`) maps cleanly onto a moment path; F209/F210 open questions resolved.

### M1 — Compiler / installer design + skeleton

The engine that turns the active rule set into installed, fast-firing dispatch.

- Active-set resolution (per anchor, from `{NAME} Decisions.md` adoption + structural facets).
- Index selection (by-`when` vs by-`where`) and the per-moment grouping.
- Pre-compilation to one module per moment (generalizing `/distill`).
- The fire-time contract the hook subsystem calls.

**Doc:** [[F211 — Rule compiler and installer\|F211]]. **Done-when:** a moment fires a compiled module that evaluates the residual conjunction and emits steers/fixes, on the Python path, for one real rule (port `R-query-14`).

### M2 — Python reference implementation

The clear, correct, executable spec. Owns authoring-time compilation and the agent-judgment path; the behavioral oracle the Rust impl is validated against.

**Doc:** [[F212 — Python reference implementation\|F212]]. **Done-when:** the full Resolve→compile→install→fire loop runs in Python; all M0–M1 rules fire correctly; differential-test harness (M6) green.

### M3 — Rust performance implementation

The hot-path engine. Owns fire-time dispatch + compiled-module execution under the ms budget. Behavior-identical to the Python reference (differential-tested).

**Doc:** [[F213 — Rust performance implementation + ms budget\|F213]]. **Done-when:** fire-time p99 meets the per-moment budget ([[Warden PRD]] § Performance) on a representative workload; differential tests vs. Python show zero verdict/steer divergence.

### M4 — Migration of existing surfaces

Fold today's bespoke paths onto the unified compiler: F180 `audit-q` autofire, F091 `compact` / `markdown-write`, the `audit-on-write` distill module. Each becomes "just rules" on the compiler.

**Done-when:** no bespoke per-rule hook code remains for the migrated surfaces; behavior unchanged (regression-tested).

### M5 — Perf hardening

Profile the hot path, tighten the budget, add the budget-enforcement policy (advisory vs. demote-to-audit, [[Warden PRD]] Q3), cache invalidation correctness.

**Done-when:** budgets enforced; no regression under a stress workload (instrument-every-tool simulation).

### M6 — Testing regime  *(continuous, spans M0–M5)*

The heavy, careful test discipline — see [[F214 — Rule-system testing regime\|F214]]. Not a phase; a standing gate on every milestone.

### M7 — Re-evaluation economy (so expensive rules can be everywhere)

Two pieces that let **LLM-judged** rules be instrumented as widely as mechanical ones without exhausting the agent: the **script-assisted mode** (a cheap Python / `sh` gate narrows the input the LLM judges — reasons over a section, not the whole file) and the **automatic re-evaluation gate** (an expensive rule re-runs only when a file changed *significantly* since it last passed; `rerun::` is the override). v1 measures significance by **diff magnitude** (lines / % changed) — a cheap, no-LLM gate.

**Doc:** [[F215 — Re-evaluation economy — the significant-edit gate\|F215]]. **Done-when:** a `rerun:: significant` rule skips typo-scale edits (cached verdict reused) and re-fires on a structural edit, spending no LLM tokens on the gate itself.

### M8 — Semantic update levels  *(later)*

Upgrade M7's significance measure from diff-magnitude to a **cheap classifier** rating each edit `typo → wording → structural → semantic`; rules declare a level (`rerun:: level >= structural`) and only edits at or above it re-trigger. The classifier is small/cheap, never the full rule. **Doc:** [[F215 — Re-evaluation economy — the significant-edit gate\|F215]] § What "significant" means — staged.

## The testing regime (summary — full spec in F214)

Because this instruments almost every action, correctness and performance regressions are both high-stakes. The regime has five layers:

| Layer | What it proves | Runs |
|---|---|---|
| **Unit** | each checker primitive, each taxonomy match, each guard | every commit |
| **Differential (Python ↔ Rust)** | the two implementations agree on every `(rule, target, moment)` verdict/steer | every commit touching either impl |
| **Golden corpus** | a fixed set of rules × fixtures with recorded expected outcomes; catches semantic drift | every commit |
| **Performance** | per-moment p99 vs. budget; a regression fails CI | every impl commit |
| **End-to-end / live** | a rule authored → adopted → fires at its moment in a real session (the F180-style smoke test, generalized) | per milestone |

Guiding rules (per the dev discipline): when a bug is found, **first write the failing test, then fix** — never iterate by hand; tests live in the vault/repo, not `/tmp`; the differential harness is the primary oracle so neither implementation can drift silently.

## Sequencing at a glance

```
M0 design ──► M1 compiler ──► M2 Python ref ──► M3 Rust perf ──► M4 migrate ──► M5 harden
                                   │                  │
                                   └──── M6 testing regime (continuous) ────┘
```

## Open questions

1. **Repo home for the implementations.** Python ref + Rust impl — new code anchor under SKA, or alongside the audit scripts? (Affects `.anchor` + build wiring.)
2. **Migration ordering (M4).** Which existing surface ports first — `audit-q` (smallest, already `when::`) is the natural pilot.
3. **Budget-enforcement policy (M5).** Advisory logging vs. hard demote-to-audit for over-budget rules (also [[Warden PRD]] Q3).
