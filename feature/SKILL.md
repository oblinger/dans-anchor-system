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
Designing → Agreed → Implementing → Testing → Done
```

The feature lifecycle uses the canonical state vocabulary from the `[[workflow]]` discipline. Two feature-specific accommodations:

- **`Proposed` was dropped** — it collapsed to early `[Designing]`. A freshly-created feature doc starts at `Designing`.
- **`Agreed` is preserved as a feature-doc-specific synonym for `[Ready]`** — kept distinct because the Agreed gate is genuinely meaningful (user-approval-anchored).

| Status | Canonical state | Meaning |
|--------|-----------------|---------|
| Designing | `[Designing]` | Feature doc being written, open questions being resolved. |
| Agreed | `[Ready]` (synonym `[Agreed]`) | User has approved the design — ready to implement. |
| Implementing | `[Active]` | Code is being written. (Implementing = canonical-name alias for Active.) |
| Testing | `[Verify]` | Implementation complete, being tested. |
| Done | `[Done]` | Feature shipped and verified. (Done = canonical-name alias for Completed.) |

If a feature is `[Questions]` or `[Blocked]` mid-flight, that's tracked via the bullet's bracket on the linking backlog item, not on the feature doc Status field.

## Runbook

### 1. Create the Feature Document

Determine the next F-number for the anchor (highest existing F-number + 1; per `[[CAB Backlog]]` § Numbering policy — monotonic-forever, never recycled). Create the feature doc in the project's Features folder:

```
{anchor}/Docs/Plan/Features/F{n} — {Feature Name}.md
```

If the Features folder doesn't exist, create it. Filenames carry the F-number prefix; date is omitted (the F-number itself sorts chronologically since it monotonically increases).

**Feature doc structure — Open Questions sits BELOW the H1 while any pending Qs exist; deleted entirely once all are resolved, with answered Qs migrating to a `## Resolved` H2 at the bottom of the doc.** The lifecycle:

```markdown
---
description: {one-line description}
---

# F{n} — {Feature Name}

## Open Questions

(Only present while pending Qs exist. Deleted entirely when zero pending — see "Phase 2" below.)

Blocking decisions. The feature cannot move from **Designing → Agreed** while this list is non-empty.

- **Q1 — {short question}** — {context + options}
- **Q2 — {short question}** — {context + options}

### Resolved

(Temporary holding pen for resolved Qs while pending Qs still exist. When all Qs are resolved, this content migrates to the bottom `## Resolved` H2 and the entire `## Open Questions` H2 is deleted.)

- **Q0 — {earlier question}** — **Resolution:** {decided X because Y}. Incorporated into Design § {section}.

## Summary

{1-2 paragraphs}

## Design

{The design: API proposals, architecture changes, trade-offs.}

## Status

Designing — awaiting design discussion.

## Resolved

(Bottom-of-doc archive. Populated only after all Qs have been resolved at least once. Never deleted; this is the historical record.)

- **Q0 — {earlier question}** — **Resolution:** {decided X because Y}. Incorporated into Design § {section}.
```

**Lifecycle phases for Questions:**

- **Phase 1 — pending Qs exist.** `## Open Questions` H2 sits directly below the H1, containing pending Qs. Resolved Qs accumulate inside as a `### Resolved` H3 sub-section.
- **Phase 2 — all Qs resolved.** Delete the `## Open Questions` H2 entirely. Migrate all accumulated `### Resolved` content to a `## Resolved` H2 at the **bottom** of the doc (creating that section if it doesn't exist; appending if it does). Top of doc is now clean: H1 → Summary → Design → Status → Resolved.
- **Phase 3 — new Q arises later.** Recreate the `## Open Questions` H2 below H1 with the new Q. New resolutions accumulate in the temporary `### Resolved` H3 again until all are answered, then migrate to the bottom `## Resolved` H2.

**Structural rules:**
- **H1 carries the F-number.** Format: `# F{n} — {Feature Name}`.
- **`## Open Questions` lives below H1 only while pending Qs exist** — deleted otherwise.
- **`## Resolved` at the bottom of the doc is the permanent archive** — populated when all Qs reach resolution; never deleted.
- The ask-questions discipline (`[[ask-questions]]`) applies universally — feature docs, PRDs, plan docs, anything with questions follows this same shape.

### 1a. Surface the Doc — glance only when adding/modifying a pending question AND the user is engaging now

Glance the doc *only when both conditions hold*: (1) the edit added or modified a pending question, AND (2) you're in **active mode** — the user is engaging with this feature right now. See [[ask-questions]] § Active vs Parking mode for the full rule.

```bash
open "<path to feature doc>"
```

**Active mode (do glance)** — user said "let's design X" / "let's discuss X" / invoked `/feature` for this work without saying "for later." The user expects to answer questions in this turn or the next.

**Parking mode (don't glance)** — user said "put it on the backlog" / "for later" / "we'll figure that out" / `/feature` was used to file a stub. The feature doc is created and questions captured, but the user defers engagement. The doc surfaces later when the user opens a backlog item that points at it, or runs `/groom`.

**Never glance when the edit only resolved questions**, regardless of mode. Resolution doesn't surface new state for the user.

**On the create step:** glance only if you're in active mode. If creating a feature stub for backlog filing, skip the glance — the user just told you to file it; opening the file at them is the opposite of what they asked.

### 2. Post to Stat

```bash
skl-stat add "Proposed" "<Feature Name>" "Feature doc created"
```

### 3. Design Discussion

Work with the user to flesh out the design. Update the feature doc as decisions are made. Every open question follows the same three-step resolve discipline:

1. **Move the question** from the pending list in `## Open Questions` to the `### Resolved` subsection. Never delete it.
2. **Rewrite the line** in the form `**Q{N} — <question>** — **Resolution:** <what was decided, in one sentence>. Incorporated into Design § <section>.` The "Incorporated into" pointer makes resolved entries auditable — a reader can see not just that Q3 was answered but where the answer shaped the design.
3. **Update the Design (or relevant) section** with what the resolution means in the spec. The resolved question and the updated design ship together.

When a new question arises mid-discussion, add it to the pending list and glance the file (per step 1a). When you resolve a question, **don't** glance — even if other questions are still pending. The glance is only for moments when the user needs to react to *new or changed* questions.

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

- **F-numbered filename** — `F{n} — {Feature Name}.md` in the Features folder. F-number from the anchor's monotonic-forever counter (per `[[CAB Backlog]]` § Numbering policy).
- **H1 carries the F-number** — `# F{n} — {Feature Name}`.
- **Open Questions BELOW the H1** while pending Qs exist; deleted entirely when zero pending. Resolved Qs migrate to a `## Resolved` H2 at the bottom of the doc.
- **`open` the doc after every Open Questions edit (in active mode)** — mandatory, per step 1a.
- **Status near the bottom** — single line indicating lifecycle stage. (`## Resolved`, when present, sits below Status as the historical archive.)
- **No implementation details in the feature doc** — the feature doc is the *what* and *why*.

## Stat Integration

Every lifecycle transition posts to stat. The user can monitor all active features from the Ops page:

| S# | Status | Output | Activity |
|----|--------|--------|----------|
| S03210930 | Implementing | [[2026-03-21 Standard Rule Sets]] | 3 of 11 rule sets created |
| S03200917 | Agreed | [[2026-03-20 Buffer Origin Point]] | Design approved |
| S03201400 | Proposed | [[Smart Clear]] | Feature doc created |
