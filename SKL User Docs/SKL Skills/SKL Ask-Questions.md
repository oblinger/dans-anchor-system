# Ask-Questions Discipline

The **ask-questions discipline** governs how the agent surfaces decisions to the user — batched, numbered, with explicit recommendations — so questions don't get lost in the scrollback and answers don't come back out of order.

This is a discipline (`user_invocable: false`) — you don't invoke it directly. It runs whenever a skill (`/feature`, `/code plan`, `/code architect`, `/ready`, `fortify`, etc.) needs 2+ decisions from you.

## Why this exists — the problem it solves

Inline questions in the console scroll off the screen. Answers come back in arbitrary order because you're still reading question 3 while the agent has already asked question 4. Worse: questions you never saw end up "decided" by the agent without your input. The discipline moves questions out of the console and into a **persistent file** that you see via `glance` — the file is the source of truth, the console is a hint.

## What it does

- **Batches questions at intake** — before asking anything, the agent reviews the work and lists *every* question. No "we'll figure that out later" trickle.
- **Numbers each question with `Q<n>`** — stable references, never renumbered. You can say "answer Q3 first" and there's no ambiguity.
- **Asks once, in one file** — questions live in a `## Open Questions for <descriptor>` block above the H1 of the relevant feature/plan doc. Resolved questions move to `### Resolved` (never deleted).
- **Recommends explicitly** — every question ends with a sub-bullet `**Recommendation:** Strong / Lean / None — <answer> — <reason>`. The bolded **Recommendation:** prefix is the eye-anchor; the strength label tells you which questions need thought (Lean / None) and which can be rubber-stamped (Strong).
- **Glances the file when you're engaging** — the agent opens the file in your editor only when you're actively engaged with the work. If you've parked the work for later, the agent skips the glance to avoid interrupting deferred work.

## Question format

```
- **Q1 — Short question name** — context, why we're asking, what's at stake.
  - (a) Option A — short description.
  - (b) Option B — short description.
  - **Recommendation:** Strong (b). One-line reason.

- **Q2 — Next question** — context.
  - (a) ...
  - (b) ...
  - **Recommendation:** Lean (a). One-line reason.
```

No blank line between options and the **Recommendation:** sub-bullet (they're one question). One blank line between questions.

## Recommendation strengths

| Label | When the agent uses it | What you should do |
|---|---|---|
| **Strong** | High confidence, no meaningful trade-offs in the alternatives. | Rubber-stamp unless you disagree. |
| **Lean** | Moderate confidence, alternatives are defensible. | Quick read; consider before accepting. |
| **None** | Genuine uncertainty. | Apply your judgment. |

## When you'll notice this

- A feature doc gets created with a `## Open Questions for X` block above the H1 — that's the discipline at work.
- The agent says "I've put 5 Qs in [[2026-04-30 Foo]]" and opens the file at you — active mode, the agent wants you to engage.
- The agent says "I've parked the questions" without opening the file — parking mode, you can come back when you're ready.
- A backlog item shows `→ [[Feature Doc]]` — that's the link convention marking the item as `[Blocked]` on user input.

## Active mode vs Parking mode

The agent decides whether to glance the questions file based on context:

- **Active mode** — you're engaging right now. Signals: "let's design X", "let's discuss", "tell me about". The agent glances.
- **Parking mode** — you've explicitly deferred. Signals: "put it on the backlog", "for later", "/ready" batch processing creating feature docs. The agent does not glance — the file surfaces later when you re-engage.

Default when ambiguous is parking, since the cost of an unwanted glance (interrupting deferred work) is higher than the cost of a missed glance (you can re-engage by saying "let's discuss [feature name]").
