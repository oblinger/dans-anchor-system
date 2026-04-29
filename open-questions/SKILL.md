---
name: open-questions
description: Discipline for gathering, tracking, and resolving user questions during feature design, plan refinement, or any moment when you need 2+ decisions from the user.
user_invocable: false
---

# Open Questions Discipline

Universal process for asking the user questions during feature design, plan refinement, architecture discussion, or any situation where two or more decisions need the user's input. Applies whether or not a feature doc / plan doc exists.


## Why this exists — the problem it solves

The user is multitasking. The agent makes a lot of edits and prints a lot of output between turns, so questions asked purely on the console scroll off the screen. Answers come back out of order because the user is still reading question 3 while the agent has already asked question 4. The user may not even be watching the console.

Consequence: questions get lost, and decisions that *seemed* made actually weren't — the user never saw them.

**The workflow below moves the questions OUT of the console and INTO a single persistent file that the user sees via `glance`.** The console is still used — but it's a hint, not the system of record. The file is the system of record. With the file open on the user's side, nothing scrolls away, questions can be answered in any order, and there's one (or a small, discoverable number of) place(s) to look for what's outstanding.

This is why the discipline below applies specifically to **feature construction and project planning**, where multiple decisions stack up. A one-off "should I use 4 spaces or tabs?" doesn't need the workflow — ask and move on.


## Intake — batch, number, ask once

1. **Batch at intake.** Before asking anything, review the work and write down EVERY question you might need the user to answer. Do not ask the obvious ones first and hold the edge cases for "follow-up."
2. **Number them Q1, Q2, ..., Qn** in the order you'll present them.
3. **Ask in one message.** Present all Q_n together with enough context on each so the user can answer top-to-bottom.

**Never ask a second round after the user has said "ready" or "go" to the first.** If you realize later you missed a question, surface it as a miss — "I should have asked Qn earlier, surfacing now" — don't sneak it in.


## Resolution — inline, with pointer

For each answered question, write the resolution inline in this exact form:

```
**Q3** — **Resolution:** <one sentence of what was decided>. Incorporated into <design section / plan section / code area / conversation>.
```

The **Incorporated into** pointer makes resolutions auditable — a reader can trace decision → design → code. When no doc exists yet, the pointer may target the conversation ("Incorporated into the design we just agreed on").


## When a file is involved

If a feature doc, plan doc, or PRD exists with `## Open Questions`:

- Open Questions sits ABOVE the H1 as pre-document material (`## Open Questions`)
- Resolved questions move to `### Resolved` H3 subsection — never deleted
- Follow-on questions (children of a pending question) become **sub-bullets** under their parent in `## Open Questions`. When the parent is resolved, the children either resolve with it, become independent questions at the top level, or get moved to Resolved alongside the parent — agent's judgment.
- After an edit to Open Questions, run `open "<path>"` **if pending questions remain** that the user needs to see. **Skip the glance when the edit resolved the last pending question** — the file no longer has anything outstanding for the user to attend to. The glance is for surfacing pending state; an all-resolved file is not surfacing anything.

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
