---
description: "Discipline for when/how the agent attends to rules at write-time."
---

# [[Audit]] · F006 — Rule triggering — when the agent attends to rules

## Summary

As the rule catalog grows (currently dozens, heading toward hundreds, plausibly thousands), the agent cannot keep every rule in attention at all times. Most rules are **hyper-specific** — they apply only when a particular file is being edited, a particular operation is run, a particular trait is declared on the cwd anchor. The proposal: **let each rule carry its own triggering logic** that tells the agent when to attend to it. The agent's per-turn ruleset then collapses from "all rules in the catalog" to "rules whose triggers fire for what I'm currently doing."

This feature designs that triggering mechanism. It's the *when-to-attend* half of rule discipline; the *how-to-check* half already exists in the rule spec as `**Check pattern:**`.

## Success Criteria

**Tier:** 2 (agent-over-time)
**Blocks next:** none

**What done looks like.** Every rule in the catalog has a declared trigger (or an explicit "always" marker). The agent's read-and-write loop consults trigger predicates and only loads/attends to rules whose triggers fire for the current action. A `lint-rule-triggers.py` audit verifies coverage.

**How it will be verified.** Deferred-agent watchdog: pick 10 random agent actions across a week and confirm the ruleset attended to was the trigger-filtered set, not the full catalog. Plus the audit script gives a one-shot completeness check.

## Design

### The scale problem

- The rule catalog is going from ~100 to ~1000 rules over the next quarters.
- The agent currently has no mechanism to ignore rules. Every rule is potentially "in scope" for every action.
- Holding ~1000 rules in working attention every turn is impractical and degrades focus on the rules that *actually apply*.
- The good news: most rules are highly specific — they apply only when (a) a particular file is being edited, (b) a particular tool is invoked, (c) the anchor declares a particular trait, (d) some other narrow condition holds.
- If each rule can declare "I apply when X," the agent's per-turn working set shrinks from ~1000 to ~10-50 rules. The cost is paid once per rule (at authoring time), not per turn.

### The triggering mechanism

Each rule (or ruleset) declares one or more **triggers** — predicates that the agent (or harness) can evaluate cheaply to decide "do I attend to this rule right now?"

Trigger axes (initial proposal — to refine in design):

| Axis | Example trigger | What it filters by |
|---|---|---|
| **File path / pattern** | `path:**/*.md` | Path glob — only attend when acting on matching files |
| **File basename / suffix** | `basename:*.tsx`, `suffix:Guide.md` | Specific extensions or suffix conventions |
| **Folder context** | `in:CAB/CAB Facets/` | Action lands in this folder |
| **Tool invocation** | `tool:Write`, `tool:Edit` | Specific tool being used |
| **Anchor trait** | `trait:Code`, `trait:Skill` | Cwd anchor declares this trait in `.anchor` |
| **Facet presence** | `facet:Backlog` | Cwd anchor has this facet |
| **Mode** | `mode:Drive`, `mode:Lean` | Operational mode is active |
| **File-meta presence** | `sibling-exists:<basename> Guide.md` | A related file exists (the read-hook case) |
| **Always** | `always` | Rule attends regardless — for project-wide invariants |

### Connection to existing structure

- **CAB Rules** already specifies `**Check pattern:**` for every rule — that's *how to check*. Triggers are the missing *when to attend*. Both belong in the same rule entry.
- **F091 Trigger discipline** already specs trigger declaration at the Aspect level (`## Triggers § markdown-write` etc.). Rule-level triggers extend the same model finer-grained.
- **Rulesets via `include::`** flatten to a unified rule list at audit time. Trigger filtering happens AFTER flattening — the flattened list is the universe; triggers filter to the working set.

### Surfacing the rule to the agent

Per the read-hook discussion (2026-06-09 with the user) — when a rule's trigger fires, the rule content should be surfaced to the agent with clear provenance:

- The rule's source ruleset is named.
- The rule's check pattern is included.
- The agent knows this rule is harness-injected (not invented by it), and can cite it by `[[R-<set>-<NN>]]`.
- Multiple firing rules accumulate in the per-turn context as a *short* list (not the full catalog).

### Edge cases (preliminary — to harden in design)

These were named during the read-hook conversation (2026-06-09) and likely generalize to rule-triggering:

- **Selective injection on Read.** Hook fires on every `.md` Read; checks rule triggers; injects matching rules. Rules whose triggers don't fire are skipped. Zero cost when no rules match.
- **Pre-write check.** Hook fires before Write/Edit; checks rule triggers; if any fire and aren't yet in context, inject before allowing the write.
- **Partial reads (offset/limit).** Inject anyway — partial reads are usually targeted edits, which is exactly when the trigger matters most.
- **Repeated reads in a session.** Only inject on the first read. The agent already has the rule content; second injection is waste. Cache by `(rule_id, agent_session)`.
- **The rule's source file itself getting read.** Do NOT recursively pull the rule's own meta-rules. Rules don't trigger themselves on themselves; detect by source-file match and skip.
- **Grep/glob hits.** Hook fires only on Read/Write/Edit. Grep doesn't need rule injection because the agent isn't acting on the file as a whole.
- **Write to a new file path (no prior Read).** Hook still fires — pre-write check. Same mechanism, fires earlier.
- **Trigger conflicts / overlapping.** Multiple rules may fire for the same action. Their content concatenates (deduplicated by rule-id). Order: most-specific trigger first.
- **Performance.** Trigger evaluation must be cheap (sub-millisecond per rule, ideally). Path globs and trait lookups are cheap; sibling-file existence checks are O(1) filesystem ops; cross-anchor lookups need indexing.

### Open ideas (not yet designed)

- **Trigger expression language.** Simple ones (`path:**/*.md` + `tool:Write`) are easy; composite (`AND`/`OR`/`NOT`) might be needed. Start simple; add operators only when forced.
- **Trigger-less rules.** Should all rules require a trigger, or is `always` the implicit default? Lean: explicit `always` keyword; no implicit default (forces author to think about scope).
- **Audit `lint-rule-triggers.py`.** Walks every rule, verifies trigger present and parseable, reports rules with no trigger as warnings.
- **Trigger debugging.** "Why did/didn't rule R-X fire here?" — a debug mode that traces trigger evaluation.

### What this is NOT

- It's not a *replacement* for `**Check pattern:**`. Check pattern says *how* to verify; trigger says *when* to consider verifying. Both are required.
- It's not a *priority/tier* system. Audit tiers (`tracked`/`stated`/`sampled`/`checked`) already exist on rules and govern audit frequency, not attention scope.
- It's not the F091 Trigger discipline — that's at the Aspect level (anchor-wide); rule-triggers are finer-grained (per-rule).

## Status

**Designing** — initial ideas captured; user will return to flesh out the model.

**next action:** user reviews the Design section above, marks which trigger axes look right and which are wrong, and either fills the Open Questions block or escalates to `## Resolved` with concrete decisions. Then design pass 2 lands a draft trigger-expression grammar.

## Related

- [[FCT Ruleset]] — rule spec (check pattern lives here; trigger to be added).
- [[F091 — Trigger discipline]] — Aspect-level trigger discipline (companion at coarser grain).
- [[F133 — Rulesets folder convention + facet embedding]] — Rulesets folder convention + facet embedding (sibling structural-migration feature).
- [[FCT Brief]] — uses the read-hook mechanism this feature generalizes.
