---
description: "design trade-off threads on the Warden PRD — dated, Problem / Options / Decision"
---

# Warden PRD Discussions
Dated trade-off threads behind [[Warden PRD]] — how each of its claims came to be settled, and what was rejected on the way.

Split from the PRD's inline `# Discussion` H1 on 2026-08-20 ([[DAS Discussion]] method 1 → method 2), the first entry having already outgrown the *"~1–2 screens of body content"* threshold on its own. Newest first.

## 2026-08-20 — How the rule corpus is refined, and who holds which half

**Problem.** Warden's PRD described what a rule *is* and how it fires, and said nothing about how the corpus becomes and stays *right*. The implicit model was that the user reviews rules. He does not, has not, and — measured against the size the corpus reached — could not. The gap surfaced through exceptions rather than rules: [[Eli Exceptions]] carried five rows graded `?`, waiting on a review that was never going to arrive, because `R-exception-discipline-06` said grading was the user's act.

**Options considered.**

**(A) Make the review cheaper.** A grading rubric so the user could judge each deviation at a glance; a gallery of worked A/B/C examples per rule. Rejected — it optimises the wrong step. The user's objection was not that grading was *hard*, it was that it was *his*: *"I have to cognitively get into each one of these areas to understand what's going on, to have a meaningful opinion. It's not a very good use of time."* A cheaper per-item review is still per-item.

**(B) Push the corpus to the user in summary.** Reports that surface concentrations, cross-anchor counts, drift dashboards. Rejected, and this is the option that took two rounds to kill because the agent proposed it twice under different names. A summary of N findings is still an at-scale artifact: settling one row does not settle the next, so the user's attention is consumed linearly no matter how well the list is sorted. It also runs against the standing Non-Goal on cross-anchor orchestration.

**(C) Refinement from instances, settled in generalities.** Adopted. The user brings a page that came out wrong plus his claim about the principle it breaks; the agent qualifies that principle against the whole corpus, propagates it, and hands back **collisions** rather than lists.

**Decision.** (C), recorded as § Refinement. Three things in it are load-bearing and were not obvious at the start of the thread:

1. **Both sides speak in generalities.** The first draft framed this as instances-vs-corpus, which was wrong: the user is *strong* at eliciting the rule an instance violates, and that rule is a generality. What he cannot do is qualify it. Dan's correction: *"The user is fluent in instances and strong in identifying the rule violated by an instance. The agent is fluent in the corpus and is strong in assessing the global consequences and interaction of any given rule."*
2. **The qualification problem is the agent's half**, and naming it is what makes the division honest — the user's rule arrives *deliberately* under-qualified, and treating that as an incomplete request rather than a normal handoff is what would push the corpus back onto him.
3. **The failure test is scale, not exposure.** The first draft said any mechanism asking the user to read a rule or grade a deviation was a smell; that is too strong and would forbid the conversation this whole loop is made of. The real line: *"every mechanism that tries to ask the user to operate at scale across the corpus is working against that."*

**How this sits with the rest of Warden.**

- **It explains the read/fire/run North Star's blind spot.** § Overview argues the guardrail, the documentation and the runnable code cannot drift because they are one artifact. True — and it says nothing about whether that one artifact is *right*. § Refinement is the missing half: one artifact solves drift *between* representations, and the instance-driven loop is what corrects the artifact itself.
- **It is the product justification for `deny` being floor-gated and for `tell` being the default action** ([[Warden Semantics]]). A `tell` that steers wrongly produces a page the user can see and object to, which feeds the loop. A `deny` that fires wrongly produces *nothing* — no artifact, no instance, no complaint — so a mis-stated `deny` is invisible to the only detector the system has.
- **It sets a bar for [[F231 — Warden observability — the why-did-that-happen log|F231]] explainability.** The log's stated job is answering *"did the LLM ignore the steer, or did we never send the right one?"* Under this loop that question is asked **after** the user has objected to a page, which means the log's real workload is retrospective and instance-anchored: given this wrong page, what fired? That is a narrower and more answerable query than continuous observability.
- **It predicts where new mechanisms will go wrong.** Anything that accumulates a pile for the user to work through — a review queue, a pending-approval list, an ungraded backlog of proposals — is the shape to refuse. `?`-graded exceptions were exactly that pile, which is how the thread started.

**Resolved same day — facets and templates, yes, with one variable.** Dan: *"I think that the same refinement loop governs facets and templates… but I think the difference is, those things are designed specifically to be human viewable."* Developed as § Same loop for facets and templates. The instinct in the paragraph this replaces was right about the loop and wrong about why it was uncertain: what varies is not whether the loop applies but **whether the artifact has a user-facing zone**, which turns out to be a statement [[DAS progressive-disclosure]] and [[DAS Brief]] already make — a ruleset is entirely Brief, a facet is not. The consequence worth carrying forward is that comprehensibility is now **load-bearing**: a spec that outgrows its user-facing zone loses the short path back to the user and reverts to Warden's longer one, which no size discipline in the system currently frames as a cost of that kind.

**Open.** Nothing from this thread. The nearest untested claim is the one in § Same loop — that a facet's user-facing zone is read once at adoption and not again — which is asserted from Dan's description of his own habit and has not been measured.
