---
name: feature
description: >
  Feature lifecycle — design, ready, implement. Manage a feature from idea
  through design, agreement, implementation, testing, and completion.
  Use when the user says: "new feature", "let's build", "design a feature",
  "feature for", "I want to add".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Feature — Feature Lifecycle

Manage a feature from initial idea through design, agreement, implementation, testing, and completion. Every feature gets a dated design document, posts to stat throughout its lifecycle, and requires explicit user agreement before implementation begins.

**MANDATORY: Post to stat at every lifecycle transition. The user monitors features via the Ops page.**

**MANDATORY: Commit discipline.** Before starting a new feature or switching to any other activity, commit all uncommitted work from the current feature. The natural commit point is the transition — not when you think you're done, but when you're about to do something else.

## When to Use

When the user says "let's build a feature", "new feature", "I want to add", "design a feature", or when work is significant enough to warrant a design document rather than a quick code change.

## Lifecycle

```
Proposed → Designing → Agreed → Implementing → Testing → Done
```

| Status | Meaning |
|--------|---------|
| Proposed | Idea captured, not yet designed |
| Designing | Feature doc being written, open questions being resolved |
| Agreed | User has approved the design — ready to implement |
| Implementing | Code is being written |
| Testing | Implementation complete, being tested |
| Done | Feature shipped and verified |

## Runbook

### 1. Create the Feature Document

Create a dated feature doc in the project's Features folder:

```
<anchor>/Docs/Plan/Features/YYYY-MM-DD <Feature Name>.md
```

If the Features folder doesn't exist, create it.

**Feature doc structure — note the Open Questions block comes BEFORE the H1.** This is intentional: open questions are pre-document material that the user needs to see first, every time they open the file. The H1 and everything below is the "document proper."

```markdown
---
description: <one-line description>
---

## Open Questions

Blocking decisions. The feature cannot move from **Designing → Agreed** while this list is non-empty. When a question is resolved, move it to **Resolved** below with the answer and where it landed in the design.

- **Q1 — <short question>** — <context + options>
- **Q2 — <short question>** — <context + options>

### Resolved

- **Q0 — <earlier question>** — **Resolution:** <decided X because Y>. Incorporated into Design § <section>.



# <Feature Name>

<Brief description of what the feature does and why.>

## Summary

<1-2 paragraphs>

## Design

<The design: API proposals, architecture changes, trade-offs.>

## Status

Proposed — awaiting design discussion.
```

**Structural rules for Open Questions:**
- **H2 `## Open Questions` sits ABOVE the H1** — it is pre-document material, not a section of the feature spec.
- **H3 `### Resolved` is a subsection of Open Questions.** Resolved questions never get deleted; they get moved down with their resolution.
- **The section always exists**, even if empty — leave a one-liner like "_None — design is clean._" under the H2 so the structure is visible.

### 1a. Surface the Doc — glance when pending questions remain

Every time you touch the Open Questions section *while pending questions remain* — add a question, resolve one of several, move one to Resolved with siblings still open — run this immediately after saving:

```bash
open "<path to feature doc>"
```

This opens the doc in the user's default editor so they see the updated state of what's still outstanding. The user watches for these moments; they are the decision points where your work is blocked on their input.

**Skip the glance when the edit resolved the last pending question.** With nothing left under `## Open Questions`, there's no outstanding state for the user to attend to — the glance would just open a now-quiet file. The glance is for surfacing pending state, not for announcing completion.

Do this on the create step too — once the feature doc is written, `open` it so the user can start reading while you move to stat (since at create time there are typically pending questions to show).

### 2. Post to Stat

```bash
skl-stat add "Proposed" "<Feature Name>" "Feature doc created"
```

### 3. Design Discussion

Work with the user to flesh out the design. Update the feature doc as decisions are made. Every open question follows the same three-step resolve discipline:

1. **Move the question** from the pending list in `## Open Questions` to the `### Resolved` subsection. Never delete it.
2. **Rewrite the line** in the form `**Q{N} — <question>** — **Resolution:** <what was decided, in one sentence>. Incorporated into Design § <section>.` The "Incorporated into" pointer makes resolved entries auditable — a reader can see not just that Q3 was answered but where the answer shaped the design.
3. **Update the Design (or relevant) section** with what the resolution means in the spec. The resolved question and the updated design ship together.

When a new question arises mid-discussion, add it to the pending list. Whether adding, resolving, or rewording — after an edit to `## Open Questions` that leaves pending questions, run step 1a's `open` on the file. Skip the glance when the edit just closed the last pending question; the file no longer has anything outstanding to show.

Update stat as you work:
```bash
skl-stat update <S#> "Designing" "Resolving open questions"
```

### 4. Reach Agreement

When all open questions are resolved and the design is complete:
- Update the feature doc's Status section to "Agreed"
- Get explicit user confirmation: "This design is agreed — ready to implement?"
- Only proceed to implementation after the user says yes

```bash
skl-stat update <S#> "Agreed" "Design approved by user"
```

**This is a gate.** Do not implement without agreement. If the user says "just do it" without a design discussion, still create the feature doc (even if minimal) and confirm before coding.

### 5. Implement

Use `/mint` or work directly. The feature doc is the spec.

```bash
skl-stat update <S#> "Implementing" "Starting implementation"
```

During implementation:
- Reference the feature doc for decisions
- If new questions arise, add them to `## Open Questions` (pending list), run `open "<feature doc path>"` so the user sees them, and pause if the question is blocking
- Resolve any questions with the three-step discipline from § 3 before continuing
- Do NOT commit during implementation unless switching to another activity

### 6. Test

Run tests, verify the feature works as designed.

```bash
skl-stat update <S#> "Testing" "Implementation complete, running tests"
```

### 7. Complete

When tests pass and the feature is verified:
- Update the feature doc's Status to "Done"
- Commit all uncommitted work for this feature
- Post final stat update

```bash
skl-stat update <S#> "Done" "Feature complete and tested"
```

## Commit Discipline

**Commit on transition, not on completion.** The natural commit point is when you're about to switch to something else.

**Rules:**
1. **Before starting a new `/feature`** — commit all uncommitted work from the previous feature
2. **Before switching to any other activity** — commit current feature work
3. **On `/feature` complete** (step 7) — commit as part of completion
4. **If the session is ending** — commit whatever you have
5. **Never leave uncommitted feature work across sessions**

**Commit message format:** Reference the feature name and S-number:
```
Implement <Feature Name> (S03200917)

<brief description of what changed>
```

## Feature Doc Conventions

- **Dated filename** — `YYYY-MM-DD <Feature Name>.md` in the Features folder
- **Open Questions ABOVE the H1** — pre-document material; first thing the user sees
- **Resolved as H3 under Open Questions** — answered questions move down, never get deleted
- **`open` the doc after every Open Questions edit** — mandatory, per step 1a
- **Status at the bottom** — single line indicating lifecycle stage
- **No implementation details in the feature doc** — the feature doc is the *what* and *why*

## Stat Integration

Every lifecycle transition posts to stat. The user can monitor all active features from the Ops page:

| S# | Status | Output | Activity |
|----|--------|--------|----------|
| S03210930 | Implementing | [[2026-03-21 Standard Rule Sets]] | 3 of 11 rule sets created |
| S03200917 | Agreed | [[2026-03-20 Buffer Origin Point]] | Design approved |
| S03201400 | Proposed | [[Smart Clear]] | Feature doc created |
