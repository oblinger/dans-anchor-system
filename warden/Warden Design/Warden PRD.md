---
description: "product requirements — the rule system, its goals, and the performance constraint"
---

# Warden PRD

The **rule system** is the vault's mechanism for stating a standing constraint once — declaratively — and having it enforced everywhere it applies, at the right moment, for every agent, automatically. A rule names *what must be true* (`when ∧ where ∧ if`); the system makes it fire. This PRD covers the whole system — the language, the corpus, the compiler/installer, and the two run paths — not just the `/rule` skill (which is one surface onto it). Architecture: [[Warden Architecture]]. Format spec: [[DAS Ruleset]]. Moment taxonomy: [[Warden Events]]. How each claim here was settled, and what was rejected on the way: [[Warden PRD Discussions]].

## Problem

The vault accumulates standing constraints — structural ("every anchor has one backlog"), behavioral ("don't ask the user to commit in Commit mode"), stylistic ("no markdown inside fenced code"). Today they live in three weakly-connected places: prose in `CLAUDE.md` / role files (read by the agent, never enforced), facet specs (enforced only when someone runs `/audit`), and scattered hook scripts (fast but hand-wired, one-off). The result: constraints are stated but drift, are enforced late or never, and adding a new always-on guardrail means writing bespoke hook code. There is no single place to *declare* a constraint and trust it fires.

## Overview

**A Warden rule is a piece of natural-language guidance about the system that knows when it's relevant** — and the engine's core job is **timely relevance**: putting the right guidance in front of the agent at exactly the moment it's actionable. So a rule is **dual-use**:

- **Read it** (statically, filtered by `where::`) to *understand the system* — the rules that touch `*.svg` *are* the SVG conventions, in prose an agent or human can read. The corpus is living documentation.
- **Fire it** (dynamically, at its `when::`) to *steer the agent* — the rule's `tell` lands in context at the right moment.
- **Run it** (directly, by any agent) — the interpretation environment (`file`, `git`, `ask_oracle`, …) is a **real, runnable Python API**, not just notation. Skills already execute Python, so an agent that reads a rule's body is positioned to *run* it and get the result. Warden *schedules* these calls; it doesn't own them. ([[Warden Semantics]] § The interpretation environment.)

Because the guardrail, the documentation, and the runnable code are the **same artifact**, they can't drift. That's the wedge: prose the agent "knows about" but doesn't attend to is useless — Warden fixes the *attention* problem, not a knowledge problem. The `where::`/`tell` are written for a reader; only `when::` is pure delivery machinery the reader can ignore.

This North Star — **read / fire / run from one artifact** — is the design constraint behind the whole language: the interpretation environment ([[Warden Semantics]] § The interpretation environment) is deliberately plain Python over a small, legible object surface, so the same rule serves all three.

One declarative rule language and one runtime:

- **State once.** A rule is dispatch (`where::` + `when::`) + a condition (`if::`) + an action (`tell` / `edit` / `deny`). The author writes the guidance and the test; never the plumbing.
- **Fires everywhere it applies.** The runtime guarantees the rule triggers at its moment — at session start, on a markdown write, after a Bash `git commit`, when a skill runs — across every agent, without per-rule wiring.
- **Cheap enough to be everywhere.** The system instruments **almost every tool use and agent action**. That is only viable if the per-moment cost is negligible, so performance is a first-class product requirement, not an afterthought (§ Performance).
- **Implicit by default, explicit on demand.** Most rules fire implicitly via the compiler/installer; the `/audit` pipeline is the thorough explicit backstop over the same corpus.

## Refinement — dissatisfaction with an instance, settled as a generality

*Thread: [[Warden PRD Discussions]] § 2026-08-20.*

**Stated 2026-08-20, as a discovery rather than a design.** Dan: *"I don't think we ever said that before. I'm not sure we even designed it, but I'm quite certain now that it's the right way."* It had been the operating model for months; nothing recorded it, so nothing could be built to serve it.

**The user does not review the corpus.** He reads the vault. *"I almost never look at your rules… I look at my vault, and when my vault is wrong, we talk about it."* **A wrong page announces itself; a wrong rule does not** — which is why the corpus cannot be kept right by reading the corpus, and why refinement starts from an instance that came out wrong.

**But the instance is only the trigger. The exchange itself is conducted in generalities.**

> **The asymmetry is the design.** The user is fluent in instances, and strong at **eliciting the rule an instance violates**. The agent is fluent in the corpus, and strong at **propagating that rule's consequences and assessing how it interacts with every rule already in force**. Both sides speak in generalities — that is the currency; the instance is what lets the user reach one. Each side speaks the language it is fluent in, and the agent owns the translation between them.

**The rule the user hands over is under-qualified, and that is expected rather than a failure.** He can name the principle the instance violates. He cannot state the conditions under which it holds, the cases it must not reach, or where it collides with what is already stated — **the qualification problem**, and it is the agent's half of the work. Dan, 2026-08-20: *"the rule has the qualification problem, that it's not a fully qualified rule, and you're the expert in figuring out the interactions between those rules."*

**So the agent's reply is a generality too, not a list.** Having propagated the new rule, the useful thing to hand back is not the N affected instances but the **collision**: *"these two things we have said conflict in this area."* That is a question of the right size — one the user settles with a single determination — whereas N instances hands him the corpus. Dan: *"you can come back and you can say, well, there's two different rules that we've said here and they conflict in this area. That's the kind of thing you can come back with, because then I can make a general determination there."*

### What breaks the loop is scale, not exposure

Showing the user a rule is fine — he can read one and say whether it sounds right. Asking him to judge a single deviation is fine. **What breaks is asking him to operate at scale across the corpus**, and that is the thing to re-examine wherever a mechanism implies it.

**Per-instance rulings are the trap, because they do not settle the next one.** A determination about one exception leaves the following exception exactly as open as before, so a loop built on them converges on nothing while consuming the user's attention linearly. That is why he must be asked for a *general* statement even when the instance in front of him is concrete — not because the instance is beneath him, but because only the generality scales.

> **The test is arithmetic.** If settling the question in front of the user would not also settle the next twenty like it, the question is the wrong size. The repair is to ask for the generality — never to ask twenty times.

### Same loop for facets and templates — one variable changes

**The loop governs facets and templates too** (Dan, 2026-08-20), and the difference between those and a ruleset is not a matter of degree: *"those things are designed specifically to be human viewable. That's the main difference."*

**That has a structural statement already in the system.** [[DAS progressive-disclosure]] layers a document into reader zones by audience — a user-facing TLDR and Overview above, an agent-facing `# BRIEF` below, whose own facet spec says it outright: *"a Brief is something an agent reads before editing the source file. Users glancing at the file should NOT need to read the Brief."* A facet or a template is authored with both zones. **A ruleset has no user-facing zone at all — it is entirely Brief.** That, and not size alone, is why a facet's loop can route through the user directly and Warden's cannot.

**What viewability changes is the localization step, and only that.** Given a wrong page, a ruleset gives the user no clue which of ~60 rulesets produced it, so finding the site is the agent's translation work. Given a wrong page from a template, he can go straight to the artifact: *"I can actually go look at the facet. I can look at the template."*

**Three things it does not change:**

- **The trigger is still an instance.** He reads a facet once, ratifies it, and then — his words — *"just runs with it and ignores it."* Viewability buys a **one-time read at adoption, not standing review**, so drift is still caught by a page that looks wrong rather than by anyone re-reading the spec.
- **Qualification is still the agent's.** Standing in front of the facet does not tell him how his correction interacts with everything else already stated. *"But then I would probably talk with you about it."*
- **The scale test is unchanged.** Twenty facets to review is the same failure as twenty exceptions to grade.

> **So viewability is a property to preserve, not an accident of size.** A facet or template that grows past comprehension does not merely get harder to read — it **silently degrades into the Warden mode**, where the user can no longer go look and must wait for the agent to localize. He loses the short path and gains nothing. The disciplines that keep a spec's user-facing zone short are therefore load-bearing for this loop, not cosmetic.

### Diagnose before repairing — three different sites

One symptom, three causes, and picking the wrong one entrenches the problem:

| The instance is wrong because… | Repair site |
|---|---|
| a deviation was **graded** too generously (or refused too harshly) | `exception-grading::` on the rule — [[R-exception-discipline]]-12 |
| the **rule itself** says the wrong thing | the rule |
| the rule is right and the artifact still came out wrong | the **template or generator** the artifact came from |

The third is the one most often missed: a rule can be correct and still be innocent, because the thing that produced the page never consulted it. It also takes the shortest route back — a template has a user-facing zone, so the user can often localize it himself (§ Same loop for facets and templates).

### Impact before applying, and pushback only when it is earned

A rule or grading change is retroactive by nature — it re-decides every instance already decided under the old text. **So the agent measures the blast radius before applying it**, and this is already the practice for rules: a change is routinely reported as *"this would rewrite N places"* before it lands. `-12` extends the same duty to exception grading, because a changed `exception-grading::` block re-grades every exception against that rule.

**Raise it with the user only when the agent genuinely doubts the consequence is intended** — showing a sample of the affected instances if that is what makes the doubt concrete. A confirmation requested on every change is the conversation this loop exists to replace; a change applied silently across 300 places the user did not picture is the failure the measurement exists to prevent. The judgment about which one this is belongs to the agent.

### Cross-anchor is a query, not a mechanism

Exception **tables** are per-anchor, because a deviation is a fact about one tree. **Grading guidance is not** — it lives on the rule, and rulesets are intrinsically cross-anchor, so a correction given once applies everywhere the rule does. That is the right split, and it is why `exception-grading::` sits on the rule rather than in any anchor.

Seeing every exception against a rule is then **a vault search for the rule id**, run at the moment a change is on the table — which is exactly when it is wanted. Dan, 2026-08-20: *"I'm not sure you need to do that very much… you can search for the rule number and you can find all of the exception tables."* Standing cross-anchor surveillance was considered and declined: it would monitor continuously for a signal needed only at change time, and it runs against this PRD's own Non-Goal — *"cross-anchor / vault-global rule orchestration beyond per-anchor active-set resolution."*

### The loop, run twice, on 2026-08-20

The session that produced this section is itself an instance of it, which is the best evidence that it was already the operating model.

**Round one.** The instance: [[Eli Exceptions]], five rows, every grade `?`. The user's claim: *"I want to push back on the idea that it's my responsibility to generate those grades."* The agent's rule said the opposite — `R-exception-discipline-06`, *"grading it is the user's act."* The agent searched the corpus and found the user was right by evidence he had not cited: `MUX-R04 Exceptions.md` auto-grades 32 sites from a scanner with no user in the loop. `-06` had been over-read from a narrower instruction about the spine rules. Rule rewritten; five exceptions graded.

**Round two.** The instance: the fix itself — a rubric block the agent had just written. The user's claim: *"if the determinations are so obvious to you, I don't think you even need to write down."* The agent found its own one-hour-old block held four predicates of which three restated its own reasoning and one was **already contradicted** by a grade it had issued in the interim. `-12` rewritten to record only what reasoning does not already supply.

Neither round required the user to read a rule. Both produced a durable change to one.

## Goals

- A constraint is **declared once** in the rule language and enforced everywhere it applies, with **no per-rule plumbing**.
- The implicit path is **fast enough to instrument nearly every action** (meets the per-moment budget, § Performance).
- One **unified moment taxonomy** ([[Warden Events]]) subsumes every existing trigger surface (`compact`, `markdown-write`, `skill:*`) and is open-ended.
- The implicit (compiler) and explicit (audit) paths produce **identical verdicts** over the same corpus.
- A **Python reference** implementation and a **Rust performance** implementation are behavior-identical, with Rust owning the hot path.
- **Refinable from instances, settled in generalities** (§ Refinement): the corpus is corrected by the user objecting to a *page*, and the correction he gives is a general statement the agent then qualifies and propagates. Showing him one rule or one deviation is fine; **any mechanism that would have him work at scale across the corpus is a design smell**, because per-instance rulings never settle the next instance.
- **Explainability** *(commissioned 2026-07-06, [[F231 — Warden observability — the why-did-that-happen log|F231]])*: the user and the agent can **look back and understand why something happened the way it did** — which rules were considered and fired at a moment, what each said or denied, what actions were taken, and what was suppressed or throttled. When Warden misbehaves, the log answers "did the LLM ignore the steer, or did we never send the right one?"

## Non-Goals

- A GUI for authoring rules (markdown + the `/rule` skill is the authoring surface).
- Cross-anchor / vault-global rule *orchestration* beyond per-anchor active-set resolution.
- **A Python sandbox for rule bodies.** A Python rule body is **real code — the same trust class as a skill** (skills also run Python you adopt). So the trust boundary is the rule's *source*, not an engine sandbox (a real Python sandbox is leaky anyway). The asterisk is *exposure*: rules fire automatically, are adopted in bulk, and read like docs — so **imported rulesets get vetted like skills**, with effectful operations off until vetted. v1 ships the mediated conveniences (`tell` / `edit` / `deny`, the latter floor-gated); a `run` / `sh` effect helper is a later convenience, not a new threat class. (Detail: [[Warden Semantics]] § The actions.)

## User Stories

- **As an agent**, I want to be steered at the moment a constraint applies (e.g. corrected before asking the user a question Commit-mode already answers), so I don't bother the user — *via implicit firing + steer messages.*
- **As the user**, I want to declare a new standing constraint once and trust it is enforced for every agent, so guardrails don't depend on prose nobody re-reads — *via authoring a rule + activating it through the anchor's traits.*
- **As the user**, I want to audit an anchor's conformance on demand and get an actionable report, so I can catch drift — *via `/audit anchor`.*
- **As the user**, I want to complain about a *page that is wrong*, say what principle I think it breaks, and have the agent work out which rule, grading, or template caused it, qualify my half-stated principle against everything else already said, and tell me where it collides — so I settle one general question instead of N instances — *via § Refinement.*
- **As a facet/skill author**, I want to ship my spec with its rules embedded and have them enforced wherever my facet is present, so the spec and its enforcement never diverge — *via an embedded `# RULESET`.*

## Capabilities (what the system must do)

1. **Define** rules and rulesets in the prescriptive format ([[Warden Rule]]) — sentinels, the condition (`where` / `when` / `if`), and a prose-or-Python body.
2. **Compose** rulesets via `include::` (acyclic, depth-first flatten, no-renumber) and aggregate them into umbrellas.
3. **Place & adopt** — catalog / facet-embedded / anchor-local homes; per-anchor adoption via the anchor's traits (`.anchor`). The active rule set for an anchor is resolvable.
4. **Bind** each rule to its moment(s) (`when::`, the unified taxonomy), place (`where::`), and test (`if::`) — the conjunction.
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

The rule system is a part of **[[SKA]]**, tied to the **ruleset** primitive ([[DAS Ruleset]]) as its definitional core, and cross-linked into **[[DAS Audit Architecture|audit]]** (the explicit consumer) and the **hook subsystem** (the implicit consumer) — and open to other future consumers (any skill that wants to fire rules at a moment). [[Warden Architecture]] is the unified map; this PRD is the why + the requirements; the [[Warden Roadmap]] sequences the build.

## Open questions

1. ~~**Where does the compiler live and when does it run?**~~ **Resolved by the build (2026-07-02):** `warden compile` runs explicitly (CLI / on rule change) and caches on the scan-index hash; the hooks load the pre-compiled artifacts from `~/.warden/` — no per-hook or per-session compile.
2. ~~**Rust ↔ Python boundary for rule-authored Python.**~~ **Resolved by F213 phase 2 (2026-07-05):** Rust owns selection; rule-authored Python crosses as an IPC round-trip to the warm resident daemon (~3.7 ms with a Python body firing) — cheap enough that code-carrying rules are not confined to post-hoc moments.
3. ~~**Budget enforcement.**~~ **Resolved advisory-first (M5, 2026-07-05):** an over-budget fire is LOGGED to `hook.log` (`OVER-BUDGET <moment> fired in X ms`), never dropped — both dispatchers time each moment against the § Performance budgets. Demote-to-audit stays a future escalation to take only if advisory data shows a persistent offender.
