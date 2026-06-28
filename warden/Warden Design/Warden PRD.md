---
description: "product requirements — the rule system, its goals, and the performance constraint"
---

# Warden PRD

The **rule system** is the vault's mechanism for stating a standing constraint once — declaratively — and having it enforced everywhere it applies, at the right moment, for every agent, automatically. A rule names *what must be true* (`when ∧ where ∧ if`); the system makes it fire. This PRD covers the whole system — the language, the corpus, the compiler/installer, and the two run paths — not just the `/rule` skill (which is one surface onto it). Architecture: [[Warden Architecture]]. Format spec: [[FCT Ruleset]]. Moment taxonomy: [[Warden Trigger Taxonomy]].

## Problem

The vault accumulates standing constraints — structural ("every anchor has one backlog"), behavioral ("don't ask the user to commit in Commit mode"), stylistic ("no markdown inside fenced code"). Today they live in three weakly-connected places: prose in `CLAUDE.md` / role files (read by the agent, never enforced), facet specs (enforced only when someone runs `/audit`), and scattered hook scripts (fast but hand-wired, one-off). The result: constraints are stated but drift, are enforced late or never, and adding a new always-on guardrail means writing bespoke hook code. There is no single place to *declare* a constraint and trust it fires.

## Overview

**A Warden rule is a piece of natural-language guidance about the system that knows when it's relevant** — and the engine's core job is **timely relevance**: putting the right guidance in front of the agent at exactly the moment it's actionable. So a rule is **dual-use**:

- **Read it** (statically, filtered by `where::`) to *understand the system* — the rules that touch `*.svg` *are* the SVG conventions, in prose an agent or human can read. The corpus is living documentation.
- **Fire it** (dynamically, at its `when::`) to *steer the agent* — the rule's `tell` lands in context at the right moment.
- **Run it** (directly, by any agent) — the interpretation environment (`file`, `git`, `ask_oracle`, …) is a **real, runnable Python API**, not just notation. Skills already execute Python, so an agent that reads a rule's body is positioned to *run* it and get the result. Warden *schedules* these calls; it doesn't own them. ([[Warden Semantics]] § Rule interpretation.)

Because the guardrail, the documentation, and the runnable code are the **same artifact**, they can't drift. That's the wedge: prose the agent "knows about" but doesn't attend to is useless — Warden fixes the *attention* problem, not a knowledge problem. The `where::`/`tell` are written for a reader; only `when::` is pure delivery machinery the reader can ignore.

This North Star — **read / fire / run from one artifact** — is the design constraint behind the whole language: the interpretation environment ([[Warden Semantics]] § Rule interpretation) is deliberately plain Python over a small, legible object surface, so the same rule serves all three.

One declarative rule language and one runtime:

- **State once.** A rule is dispatch (`where::` + `when::`) + a condition (`if::`) + an action (`tell` / `edit` / `deny`). The author writes the guidance and the test; never the plumbing.
- **Fires everywhere it applies.** The runtime guarantees the rule triggers at its moment — at session start, on a markdown write, after a Bash `git commit`, when a skill runs — across every agent, without per-rule wiring.
- **Cheap enough to be everywhere.** The system instruments **almost every tool use and agent action**. That is only viable if the per-moment cost is negligible, so performance is a first-class product requirement, not an afterthought (§ Performance).
- **Implicit by default, explicit on demand.** Most rules fire implicitly via the compiler/installer; the `/audit` pipeline is the thorough explicit backstop over the same corpus.

## Goals

- A constraint is **declared once** in the rule language and enforced everywhere it applies, with **no per-rule plumbing**.
- The implicit path is **fast enough to instrument nearly every action** (meets the per-moment budget, § Performance).
- One **unified moment taxonomy** ([[Warden Trigger Taxonomy]]) subsumes every existing trigger surface (`compact`, `markdown-write`, `skill:*`) and is open-ended.
- The implicit (compiler) and explicit (audit) paths produce **identical verdicts** over the same corpus.
- A **Python reference** implementation and a **Rust performance** implementation are behavior-identical, with Rust owning the hot path.

## Non-Goals

- A GUI for authoring rules (markdown + the `/rule` skill is the authoring surface).
- Cross-anchor / vault-global rule *orchestration* beyond per-anchor active-set resolution.
- **The `run` (arbitrary-effect) action — deferred** (see [[Warden Semantics]] § THEN). A rule is otherwise *readable guidance*, not arbitrary code; `run` breaks that — it's arbitrary execution, so adopting an *imported* rule would run its code on your moments (a supply-chain risk). If we add it, it needs a **security/trust model first** (sandboxing; effectful actions off for imported rules; explicit opt-in). v1 ships the mediated actions only (`tell` / `edit` / `deny`).

## User Stories

- **As an agent**, I want to be steered at the moment a constraint applies (e.g. corrected before asking the user a question Commit-mode already answers), so I don't bother the user — *via implicit firing + steer messages.*
- **As the user**, I want to declare a new standing constraint once and trust it is enforced for every agent, so guardrails don't depend on prose nobody re-reads — *via authoring a rule + adopting it in `{NAME} Decisions.md`.*
- **As the user**, I want to audit an anchor's conformance on demand and get an actionable report, so I can catch drift — *via `/audit anchor`.*
- **As a facet/skill author**, I want to ship my spec with its rules embedded and have them enforced wherever my facet is present, so the spec and its enforcement never diverge — *via an embedded `# RULESET`.*

## Capabilities (what the system must do)

1. **Define** rules and rulesets in the prescriptive format ([[FCT Ruleset]]) — sentinels, tiers, `check::` primitives, executable `trigger`/`guard`.
2. **Compose** rulesets via `include::` (acyclic, depth-first flatten, no-renumber) and aggregate them into umbrellas.
3. **Place & adopt** — catalog / facet-embedded / anchor-local homes; per-anchor adoption via `{NAME} Decisions.md`. The active rule set for an anchor is resolvable.
4. **Bind** each rule to its moment(s) (`when::`, the unified taxonomy), place (`where::`), and optional guard (`if::`) — the conjunction.
5. **Compile & install** the active rules onto runtime moments — index (by-when or by-where), pre-compile to one fast module per moment, run implicitly via the hook subsystem.
6. **Audit** explicitly — `Resolve → Run → Judge → Fix`, mechanical-by-script / judgment-by-agent, cached.
7. **Stay safe** — every automated fix gated by the never-delete floor (`aow-safety`).
8. **Extend** — a new moment, checker primitive, or guard key is an additive change, never a redesign.

## Performance — a first-class requirement

The system sits in the **hot path of nearly every tool call and agent action**. A few milliseconds per call, multiplied across a session, is the difference between an invisible guardrail and an unusable one. Therefore:

- **No per-event resolution.** The compiler resolves + indexes + pre-compiles *ahead* of firing; the fire-time path is a dispatch + a tiny compiled module, not a rule walk.
- **Per-moment budget.** Each instrumented moment carries a wall-clock budget (indicative, to be set on the roadmap):

| Moment class | Budget (p99, fire-time) | Why |
|---|---|---|
| `tool:pre:*` (in the critical path, can block) | ≤ ~2 ms | runs before every tool; user-perceptible if slow |
| `tool:post:*` / `write:*` (post-hoc) | ≤ ~10 ms | runs after every write/edit; throttled today |
| `session:*` (once per session) | ≤ ~100 ms | rare; cost amortized |

- **Two implementations.** A **Python reference implementation** (clear, the executable spec, where rules' own Python `trigger`/`guard` run) and a **performance implementation in Rust** for the hot dispatch + compiled-module execution. The two must be behavior-identical (the Rust path is validated against the Python reference — see § Testing). Rust owns the fire-time critical path; Python owns authoring-time compilation and the rare agent-judgment path.
- **Pre-compilation is the lever.** Generalize today's `/distill` (merge applicable rule bodies into one module) into the compiler's per-moment output; cache it, invalidate on rule/active-set change.

## Implicit vs. explicit

| | Implicit (compiler/installer) | Explicit (audit pipeline) |
|---|---|---|
| Trigger | a runtime moment fires | a user/skill runs `/audit` |
| Latency | hot-path, ms-budgeted | seconds, thorough |
| Coverage | active `when::` rules at that moment | the full applicable corpus for a target |
| Output | steer messages + mechanical fixes | per-rule pass/fail report + backlog rows |
| Role | always-on guardrail | thorough backstop |

Same corpus, same `when/where/if` vocabulary; the explicit path is the safety net under the implicit one.

## Success metrics

- A new rule with a `when::` moment, authored in a ruleset and adopted by an anchor, **fires at that moment with zero per-rule wiring** (the compiler installs it).
- The fire-time path meets the per-moment budget on the Rust implementation, validated against the Python reference for identical verdicts/steers.
- The existing F180 `R-query-14` (push/commit interception) and F091 `compact` / `markdown-write` surfaces are expressible as `when::` moments and run through the unified compiler — no bespoke per-rule hook code.
- `/audit` and the implicit path produce the same verdicts for the same `(rule, target)`.

## Place in the system

The rule system is a part of **[[SKA]]**, tied to the **ruleset** primitive ([[FCT Ruleset]]) as its definitional core, and cross-linked into **[[Audit Architecture|audit]]** (the explicit consumer) and the **hook subsystem** (the implicit consumer) — and open to other future consumers (any skill that wants to fire rules at a moment). [[Warden Architecture]] is the unified map; this PRD is the why + the requirements; the [[Warden Roadmap]] sequences the build.

## Open questions

1. **Where does the compiler live and when does it run?** At session start (install once), or incrementally as anchors are entered? (Ties to active-set resolution cost.)
2. **Rust ↔ Python boundary for rule-authored Python.** A rule's own `trigger(ctx)`/`guard(ctx)` is Python; can the Rust hot path call into it cheaply, or are code-carrying rules confined to post-hoc (non-critical) moments?
3. **Budget enforcement.** Is the per-moment budget advisory (logged) or enforced (a rule exceeding it is dropped from the hot path and demoted to the audit path)?
