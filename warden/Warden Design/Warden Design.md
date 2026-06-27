---
description: system design for the rule system — PRD, architecture, trigger taxonomy, roadmap
---
# Warden Design

| -[[Warden Design]]- | : system design for the rule system — PRD, architecture, trigger taxonomy, roadmap |
| --- | --- |
| [[Warden PRD]] | product requirements — the rule system, its goals, and the performance constraint |
| [[Warden Architecture]] | the unified map: rules, rulesets, `include::` containment, the `when ∧ where ∧ if` binding, the hook subsystem, and the compiler/audit engine |
| [[Warden Rule]] | the rule language — the file format for a rule and a ruleset (sentinels, clauses, tiers, composition) |
| [[Warden Trigger Taxonomy]] | the formal `when::` moment taxonomy — one recursive single-parameter tree |
| [[Warden Roadmap]] | the build sequence — design → compiler → Python ref → Rust perf → testing regime |
| [[Warden Integration Strategy]] | what to adopt vs. build (prior art) + the dependency/repository policy |
| [[Warden Survey]] | prior-art survey of existing rule/hook systems + recommended adaptation |

Warden spans more than the `/rule` skill — its rule-language format is [[Warden Rule]] (with `when::` in [[Warden Trigger Taxonomy]] and `where::` in [[FCT Ruleset]]), adoption in [[FCT Decisions]], the catalog in [[Rulesets]], and the runtime in [[Audit Architecture]]. [[Warden Architecture]] is the unified map that ties those together; the feature specs for the build live in [[Warden Features]].
