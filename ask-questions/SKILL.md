---
name: ask-questions
description: Discipline for gathering, tracking, and resolving user questions during feature design, plan refinement, or any moment when you need 2+ decisions from the user.
user_invocable: false
---

# Ask Questions Discipline

Universal process for asking the user questions during feature design, plan refinement, architecture discussion, or any situation where two or more decisions need the user's input. Applies whether or not a feature doc / plan doc exists.


## Why this exists — the problem it solves

The user is multitasking. The agent makes a lot of edits and prints a lot of output between turns, so questions asked purely on the console scroll off the screen. Answers come back out of order because the user is still reading question 3 while the agent has already asked question 4. The user may not even be watching the console.

Consequence: questions get lost, and decisions that *seemed* made actually weren't — the user never saw them.

**The workflow below moves the questions OUT of the console and INTO a single persistent file that the user sees via `glance`.** The console is still used — but it's a hint, not the system of record. The file is the system of record. With the file open on the user's side, nothing scrolls away, questions can be answered in any order, and there's one (or a small, discoverable number of) place(s) to look for what's outstanding.

This is why the discipline below applies specifically to **feature construction and project planning**, where multiple decisions stack up. A one-off "should I use 4 spaces or tabs?" doesn't need the workflow — ask and move on.


## Intake — batch, number, ask once

1. **Batch at intake.** Before asking anything, review the work and write down EVERY question you might need the user to answer. Do not ask the obvious ones first and hold the edge cases for "follow-up."
2. **Q-number them.** Every question gets a unique `Q<n>` prefix — `Q1`, `Q2`, ..., `Qn` — assigned in the order you'll present them. The Q-number lets the user refer back unambiguously: "answer Q3 first" / "Q5 needs more context." Q-numbers are **stable references** — once assigned, never renumber, even when questions get resolved out of order. Skipped numbers are fine.
3. **Ask in one message.** Present all `Q<n>` together with enough context on each so the user can answer top-to-bottom.

**Never ask a second round after the user has said "ready" or "go" to the first.** If you realize later you missed a question, surface it as a miss — "I should have asked Qn earlier, surfacing now" — don't sneak it in.

### Q-number assignment

When questions accumulate over multiple turns (e.g., during a long feature design), prefer the **lowest unused integer** in the file. If active questions cluster at high numbers (most are Q40+), keep counting upward. Once the cluster clears, future questions restart at low numbers. Same soft policy as backlog B-numbers — see [[CAB Backlog]] § Format.


## Question format — options as sub-bullets, recommendation as final sub-bullet

Every question has the same shape so the user can scan many at once and rubber-stamp the high-confidence ones.

### Layout

Lay each question out as:

1. The **question header** — one line: `- **Q<n> — Short question name** — context, why we're asking, what's at stake.`
2. The **options as sub-bullets**, when there are more than one. Inline-prose-with-A-B-C is hard to skim.
3. The **recommendation as the final sub-bullet of the question**, prefixed with the bolded word `**Recommendation:**` (the eye-anchor) followed by the strength label and the answer.

### Recommendation strength — three labels, always explicit

The recommendation sub-bullet uses exactly one of these forms:

| Label | When to use | Format |
|---|---|---|
| **Strong** | High confidence; the agent can name a clear reason and doesn't see meaningful trade-offs in the alternatives. The user can usually rubber-stamp these. | `- **Recommendation:** Strong (B). <optional one-line reason>.` |
| **Lean** | Moderate confidence; one option seems better but the agent recognizes the alternatives are defensible. The user should consider this before accepting. | `- **Recommendation:** Lean (B). <one-line reason>.` |
| **None** | Genuine uncertainty — either the trade-offs are user-preference-dependent or the agent doesn't have enough context. | `- **Recommendation:** None. <one-line reason: why uncertain>.` |

**Pick exactly one label.** Don't fudge with "lean strongly" or "weak recommendation" — those collapse to Lean. The bolded **Recommendation:** prefix is the eye-anchor; the user scans a column of bold "Recommendation:" labels and zips through the strength labels to see which need thought (Lean / None) and which can be accepted at a glance (Strong).

### Spacing — tight inside, loose between

- **No blank line** between the last option sub-bullet and the recommendation sub-bullet — they belong to the same question. The recommendation is just another sub-bullet at the same indent, flush with the options above it.
- **One blank line after the recommendation**, separating each question from the next so the user can see where one ends and the next begins.

### Example

```
- **Q3 — `/land` + `/roster`: always run roster, or only when work was landed?** When `/land` finds nothing in flight, two options:
  - (A) Always run roster — print state-of-the-work even when zero activities landed. Cost: one extra block of output.
  - (B) Only run roster after work was landed — skip if there was nothing in flight. Cost: lose the "you're at zero, here's the next-action menu" signal in the empty case.
  - **Recommendation:** Lean (A). The empty case still benefits from a "here's what's queued up" view; the cost is tiny.

- **Q4 — Next question name** — context.
  - (A) Option A — short description.
  - (B) Option B — short description.
  - **Recommendation:** Strong (B). One-line reason.
```

When there are no options (open-ended question), the recommendation sub-bullet still applies:

```
- **Q5 — How should we name the new module?** — context.
  - **Recommendation:** None. Pure preference call — your choice between `worker`, `runner`, or `executor`.
```

### Why this matters

Without the explicit strength label, every question reads as if it deserves equal scrutiny — and the user has to re-evaluate even the obvious calls. With the bolded **Recommendation:** anchor + label, **Strong** picks become rubber-stamps, **Lean** picks get a quick read, and **None** picks get the thinking time they need. The user's attention budget is the constraint; the format spends it where it matters.


## Resolution — inline, with pointer

For each answered question, write the resolution inline in this exact form, **preserving the original Q-number**:

```
**Q3** — **Resolution:** <one sentence of what was decided>. Incorporated into <design section / plan section / code area / conversation>.
```

The Q-number stays the same when a question moves from pending to Resolved — it's a stable reference so the user (or a later reader) can trace history.

The **Incorporated into** pointer makes resolutions auditable — a reader can trace decision → design → code. When no doc exists yet, the pointer may target the conversation ("Incorporated into the design we just agreed on").


## When a file is involved

If a feature doc, plan doc, PRD, or any document holds questions: questions live in an `## Open Questions` H2 directly **below** the H1 of the doc. This rule is universal — every document with questions follows the same shape.

### Lifecycle of the questions sections

A document with questions moves through three phases:

**Phase 1 — pending questions exist.**

```markdown
# {H1 title (e.g., F12 — Feature Name)}

## Open Questions

- **Q1 — {pending question}** — {context + options}
- **Q2 — {pending question}** — {context}

### Resolved

- **Q0 — {earlier question}** — **Resolution:** {what was decided}. Incorporated into Design § {section}.

## Summary
{rest of the doc body}
```

The `## Open Questions` H2 sits directly below the H1. Resolved questions accumulate inside this H2 as a `### Resolved` H3 sub-section (temporary holding pen).

**Phase 2 — all questions resolved.** Delete the `## Open Questions` H2 entirely. Migrate all accumulated `### Resolved` content to a new `## Resolved` H2 at the **bottom** of the document. Top of doc is now clean.

```markdown
# {H1 title}

## Summary
{rest of the doc body}

## Status
{status line}

## Resolved

(Permanent archive. Never deleted; this is the historical record.)

- **Q0 — {earlier question}** — **Resolution:** {decided X}. Incorporated into Design § {section}.
- **Q1 — {earlier question}** — **Resolution:** {decided Y}. Incorporated into Design § {section}.
```

**Phase 3 — new question arises later.** Recreate the `## Open Questions` H2 below the H1 with the new pending Q. New resolutions accumulate in the temporary `### Resolved` again until all are answered, then migrate down to the existing bottom `## Resolved` H2.

### Heading text and structure

- **Heading text is just `## Open Questions`** (no `for {descriptor}` suffix — the H1 above provides the descriptor).
- Follow-on questions (children of a pending question) become **sub-bullets** under their parent. When the parent is resolved, children either resolve with it, become independent top-level questions, or get moved to Resolved alongside the parent — agent's judgment.
- **Q-numbers are stable references.** Once assigned, never renumbered, even when questions get resolved out of order. Skipped numbers are fine.

### Glance rules

**Glance only when you've added or modified a pending question AND the user is actively engaging with this work right now.** Two conditions, both required. Adding `Q{n}` to a doc isn't enough — the user also has to be expecting to answer it now. If the user said "put it on the backlog" or "we'll figure that out later," they explicitly deferred; opening the file at them pulls them into something they parked. See § Active vs Parking mode below.

**Never glance when the edit only resolved questions** (moved one or more from pending to `### Resolved`, or migrated the H2 to the bottom `## Resolved`). Resolution doesn't surface new state — pending questions were already visible; resolved ones don't need attention. Glancing on resolution just opens a quieter file at the user, which trains them to ignore the signal.

Summary table (assumes Active mode; see below):

| Edit type | Glance (Active mode)? | Glance (Parking mode)? |
|---|---|---|
| Added a new pending `Q{n}` | **Yes** | **No** |
| Rewrote a pending question's wording | **Yes** | **No** |
| Added a sub-bullet under a pending parent | **Yes** | **No** |
| Resolved one or more questions (others still pending) | **No** | **No** |
| Resolved the last pending question (Phase 1 → Phase 2 transition) | **No** | **No** |
| No-op edit (formatting only) | **No** | **No** |


## Active vs Parking mode

Questions get added to a doc in two very different contexts. Treat them differently.

**Active mode** — the user is engaging with the work *right now*. They asked you to design / discuss / debate / plan something, and they expect to answer the questions in this turn or the next. The glance is meaningful: it tells them *"I just added something you need to look at."*

Signals that you're in active mode:
- User said: "let's design X" / "let's discuss X" / "what do you think about Y" / "let's work on this" / "tell me about X"
- User invoked `/feature` *without* saying "for later"
- User is in the middle of answering a previous batch of questions and you're adding follow-ons

**Parking mode** — the user is filing the work for later engagement. The questions get captured in a doc so they're not lost, but the user has explicitly said they're not engaging now. The doc gets surfaced when the user later chooses to engage with it (via `/groom`, the user opening a backlog item directly, etc.).

Signals that you're in parking mode:
- User said: "put it on the backlog" / "file this" / "for later" / "we'll figure that out" / "we can talk about it at that time" / "add to the icebox"
- User invoked `/feature` *and* said any of the above
- Another skill (`/groom`, `/groom`) is creating feature docs to park questions during a batch run
- User is creating a backlog stub and wants the work captured but not engaged with

**Default when ambiguous: parking.** If you can't tell whether the user wants engagement now, prefer parking — never glance, just file the questions and tell the user "filed; let me know when you want to discuss." The cost of an unwanted glance (interrupts deferred work) is higher than the cost of a missed glance (the user can re-engage by saying "let's discuss [feature name]").

See [[CAB Features]] for the canonical pre-document layout.

**Console vs. file:** it's fine to echo the new questions in the console so the user has an immediate hint, but the file is the source of truth. The user will answer from the file, not from the scrolled-away console.


## When no file is involved yet

The discipline still applies. Batch, number, resolve with the **Incorporated into** pointer. The pointer may target the conversation turn. When the discussion stabilizes enough to write a doc, the numbered/resolved questions transfer directly into that doc's `## Open Questions` and `### Resolved` sections.


## Triggers — when to apply

Apply this discipline whenever:

- You're working a `/feature` lifecycle (any phase)
- You're in `/code plan` or `/code architect` design loops
- You're refining a spec, PRD, UX Design, or System Design
- You're about to ask the user 2+ questions in a row, in any context

For a single, simple clarifying question mid-task, this is overkill — ask and move on. The discipline kicks in at volume, or when decisions will shape a design.


## Anti-patterns

- Asking one question, getting the answer, then asking the next. **Batch instead.**
- Resolving a question in prose ("we'll do X") without the `**Qn** — **Resolution:** ...` form. **The format makes it auditable.**
- Deleting a resolved question. **Move it to Resolved; the history matters.**
- Adding a new question after "ready." **Flag it as a miss; don't sneak it in.**
