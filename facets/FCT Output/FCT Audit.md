---
description: "STUB — the audit-report doc kind"
---

# FCT Audit
**Stub — candidate facet (worked example for the two-hierarchy model, 2026-06-23).** The facet spec for an **audit report**: the durable artifact a recorded `/audit` run produces — what it checked, what it found, what it fixed, and what it left for the user.

| -[[FCT Audit]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT Audit](hook://p/FCT%20Audit)<br>: STUB — the audit-report doc kind |
| --- | --- |
| Skill | [[Audit]] — the *verb* that produces a report conforming to this *noun*. `audit` is the worked example of a concept placed in **both** pillars (`skills/audit/` + this facet), cross-linked each way. |
| Related | [[FCT Output\|Output]] (parent group),  [[FCT Ruleset]] (audit *consumes* rulesets — this facet governs what it *emits*) |
| Examples | `examples/Audited/` — the coherent example world of audited artifacts these reports describe (the fixture; **not** a per-concept `FEX Audit` page) |

**TLDR** — An audit report records one `/audit` pass over a target: scope, the rules applied, findings by severity, fixes applied, items left for the user. Cardinality: one per *recorded* run — most passes fix in place and emit no durable report; this facet governs the case where a report is kept. **Candidate, parked for review:** `audit` is *primarily a skill*, so whether its output warrants its own facet (vs. relying on the backlog/query facets when it files findings) is the open question this stub exists to evaluate.

# Audit Report Structure
*(stub — to be filled when the facet is ratified)*

- **Scope + target** — what was audited, and when.
- **Rules applied** — which rulesets / `# RULESET` blocks were resolved for the target.
- **Findings** — by severity; each citing the rule and the location.
- **Fixes applied** — corrected mechanically vs. by bounded judgment; **never deletions** (flagged, not removed — the no-delete invariant).
- **Left for the user** — items needing a human decision.

# RULESET R-audit
*(stub — no rules ratified yet. This block exists so the facet is shaped correctly per [[FCT Facet]]; populate when the report structure above is agreed.)*

# BRIEF

- **Candidate facet, not yet ratified** — created 2026-06-23 as the worked example for [[SKA File Tree Architecture]] § *Two hierarchies*. Demonstrates a concept (`audit`) placed in **both** the skill pillar (`skills/audit/`, the verb) and the facet pillar (this page, the noun), cross-linked each way.
- **The example is a world, not a page** — the conformance fixture is the `examples/Audited/` world (masthead Examples row); there is no `FEX Audit.md`. This is the deliberate non-hierarchy: examples are coherent worlds pointed into.
- **Open question** — does audit's output genuinely need its own facet, or is it governed by existing facets (backlog / query) when it files findings? Resolve before promoting out of candidate status.
- **Intentionally NOT in the facets index** (decided 2026-06-23, one-page-per-concept model) — audit's noun-aspect is light, so this candidate stays a **satellite of the [[SKL Audit]] page**, reached only from there. It earns a row in [[FCT Output]] only if/when it becomes a substantial, independently-referenced spec. Until then, do not wire it into the group dispatch table.
