---
description: "F217 — Conversation-content gating — rules on what the agent said and didn't say"
---

# [[Warden]] · F217 — Conversation-content gating — rules on what the agent said and didn't say

## Summary

Beyond the agent's generic *state* ([[F216 — Agent-state model]]), some rules want to gate on **what the agent actually said — or didn't say — in the conversation**. For example: "whenever the agent asks the user *this kind* of question, surface guidance about how it's reasoning," or "if the agent claimed a task was done but never ran the test, flag it." F217 extends the observable surface from *state* to the **conversation transcript**, so an `if::` (or an `ask_oracle` over a turn) can condition on the content of a turn.

## Success Criteria

**Tier:** 2 (after F216) — depends on the agent-state plumbing and the `prompt:*` moments.
**Blocks next:** none.

**What done looks like.** A rule on `when:: prompt:stop` can read the **last turn's content** (what the agent said, the user's prior message, what was *absent*) and gate on it — directly in Python for simple cases, or via `ask_oracle` for judgment ("did the agent answer the user's actual question?"). The transcript slice is bounded (the current turn, not the whole history) and lazy.

**How it will be verified.** Fixture turns: an agent message that asks a flagged kind of question → the rule fires; a turn that omits a required step → the "didn't say" rule fires; a normal turn → silence.

## Design

**The observable.** Add a bounded **`turn`** view to the environment (the current turn's agent message + the triggering user message), exposed lazily — most rules never read it. *Not* the full history (cost + privacy); the current turn, with an opt-in to a few prior turns if a rule needs it.

**Two gating styles** (the same split as elsewhere):
- **Mechanical** — plain Python over `turn.text` (`'?' in turn.agent_said and …`) for cheap pattern gates.
- **Judgment** — `ask_oracle(f'…{turn.agent_said}')` (a **Sonnet** call, ~1¢) for "is this the kind of question that needs guidance?" — exactly the "oracle on ~10% of responses" pattern.

**"Didn't say" is the interesting case.** Detecting an *absence* (the agent finished without running the test, without surfacing the question) is naturally a judgment or a structured check against an expectation — likely an `ask_oracle` or a checklist rule.

**Open questions.**
1. Transcript access — from the tmux pane (F216) or a structured turn log? How much history is in scope?
2. Privacy/cost bound — default to the current turn only; opt-in for more.
3. Overlap with `ask_oracle` on responses — this is the "oracle checks 10% of responses" use case made declarative.

## Status

**Ready** — design item; depends on [[F216 — Agent-state model]].
