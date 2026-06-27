---
description: "F211 — Rule compiler / installer"
---

# [[Warden]] · F211 — Rule compiler / installer

## Summary

The engine that makes active rules fire **implicitly** at runtime moments — a *compiler*, not an interpreter. It resolves the rules active in an environment (per anchor, from `{NAME} Decisions.md` adoption + structural facets), indexes each onto its dispatch key (by `when::` moment, or by `where::` place), and **pre-compiles** all rules sharing a moment into one fast module (generalizing today's `/distill`). At fire time the hook subsystem ([[Audit Architecture]]) runs the compiled module for that moment, which checks the residual conjunction and emits steers/fixes. This is the hot path the millisecond budget rides on.

## Success Criteria

**Tier:** 1 (agent-immediate, after F209/F210)
**Blocks next:** [[F212 — Python reference implementation|F212]], [[F213 — Rust performance implementation + ms budget|F213]]

**What done looks like.** Given an anchor's active rule set, the compiler emits per-moment modules; installing them makes a real rule (`R-query-14`, ported) fire at `skill:post:audit-q` with no per-rule wiring, evaluating its residual `where::`/`if::` and emitting the mode-appropriate steer.

**How it will be verified.** A test anchor with two adopted rules on different moments: firing each moment runs only that moment's compiled module; the other rule does not execute (proves indexing). Re-compile is skipped when the active set + rules are unchanged (cache hit).

## Design

1. **Resolve active set** — per anchor: flatten adopted (`include::`) + structurally-present facet rulesets → the rule list.
2. **Index** — choose key per rule (when-major default; where-major when a `when:: always` rule touches a rare path).
3. **Pre-compile** — group by moment; emit one module per moment (the residual checks + each rule's `check`/`trigger`).
4. **Install** — register each moment's module with the runtime hook surface; cache keyed by (active-set hash, rules hash); invalidate on change.
5. **Fire** — the hook calls the module; module evaluates residual conjunction; emits steers (agent-directed) + mechanical fixes (safety-floored). Output uses **JSON `deny`/`block`/`reason`**, never exit-code-2 (per [[Warden Survey]] / [[Warden Integration Strategy]] D5).

The interception substrate is Claude Code hooks, used natively behind a thin portability adapter ([[Warden Integration Strategy]] D2); external checker engines (Vale/Semgrep) are opt-in, adapter-isolated, and confined to the explicit audit path (D3) — the compiler's hot-path modules are self-contained native code.

## Open Questions

1. **When does the compiler run** — once at session start (install all), or incrementally per anchor entered? (Active-set resolution cost trade-off; also [[Warden PRD]] Q1.)
2. **Module format** — emitted Python source vs. a data table the runtime interprets vs. (for Rust) generated/compiled code.
3. **Rule-authored Python in the hot path** — can a compiled module call a rule's `trigger`/`guard` cheaply, or are code-carrying rules confined to post-hoc moments? (Also [[Warden PRD]] Q2.)

## Status

**Designed 2026-06-26** (this doc + [[Warden Architecture]] §7a). Not yet implemented — M1 of [[Warden Roadmap]].
