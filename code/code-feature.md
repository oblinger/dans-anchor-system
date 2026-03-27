# Feature — Feature Lifecycle

Manage a feature from initial idea through design, agreement, implementation, testing, and completion. Every feature gets a dated design document, posts to stat throughout its lifecycle, and requires explicit user agreement before implementation begins.

**MANDATORY: Post to stat at every lifecycle transition. The user monitors features via the Ops page.**

**MANDATORY: Commit discipline.** Before starting a new feature or switching to any other activity, commit all uncommitted work from the current feature. The natural commit point is the transition — not when you think you're done (you might not be), but when you're about to do something else. This ensures every feature's work is captured before context shifts.

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

## Workflow

### 1. Create the Feature Document

Create a dated feature doc in the project's Features folder:

```
<anchor>/Docs/Plan/Features/YYYY-MM-DD <Feature Name>.md
```

If the Features folder doesn't exist, create it.

**Feature doc structure:**
```markdown
---
description: <one-line description>
---
:>> [[RID]] → [[RID Plan]] → [[RID Features]] → [Feature Name]

# <Feature Name>

<Brief description of what the feature does and why.>

## Open Questions

<List anything unresolved. These must be answered before status moves to Agreed.>

## Proposed Design

<The design. Can include API proposals, architecture changes, file format specs.>

## Status

Proposed — awaiting design discussion.
```

### 2. Post to Stat

```bash
skl-stat add "<Feature Name>" "Proposed" "Feature doc created"
```

If `--output` is warranted (complex feature), use it and write a summary to the detail file.

### 3. Design Discussion

Work with the user to flesh out the design. Update the feature doc as decisions are made. Resolve open questions.

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

Delegate to `/code it` or work directly. The feature doc is the spec.

```bash
skl-stat update <S#> "Implementing" "Starting implementation"
```

During implementation:
- Reference the feature doc for decisions
- If new questions arise, update the feature doc's Open Questions and pause if needed
- Use `/code delegate` for parallel work if appropriate
- Do NOT commit during implementation unless switching to another activity (see Commit Discipline below)

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

The stat entry can be archived when the user has reviewed it.

## Commit Discipline

**Commit on transition, not on completion.** The natural commit point is when you're about to switch to something else — a new feature, a bugfix, a different activity. This is when you commit everything from the current feature.

**Why not commit when you think you're done?** Because you're often not done. You think the feature works, then find an edge case, then fix it, then find another. Committing at each "done" moment creates noisy history. Committing at the transition creates clean, complete commits.

**Rules:**
1. **Before starting a new `/code feature`** — commit all uncommitted work from the previous feature
2. **Before switching to any other activity** (bugfix, spike, different project) — commit current feature work
3. **On `/code feature` complete** (step 7) — commit as part of completion
4. **If the session is ending** (user says goodbye, context is running low) — commit whatever you have
5. **Never leave uncommitted feature work across sessions** — if you're about to pause, commit

**Commit message format:** Reference the feature name and S-number:
```
Implement <Feature Name> (S03200917)

<brief description of what changed>
```

## Feature Doc Conventions

- **Dated filename** — `YYYY-MM-DD <Feature Name>.md` in the Features folder
- **Open Questions at the top** — these are the blocking items. When they're all resolved, the feature is ready for agreement.
- **Status at the bottom** — single line indicating lifecycle stage
- **No implementation details in the feature doc** — the feature doc is the *what* and *why*. Implementation details go in the code, commit messages, and module docs.

## Stat Integration

Every lifecycle transition posts to stat. The user can monitor all active features across all projects from the Ops page:

| S# | Status | Ref | Notes |
|----|--------|-----|-------|
| S03210930 | Implementing | [[2026-03-21 Standard Rule Sets]] | 3 of 11 rule sets created |
| S03200917 | Agreed | [[2026-03-20 Buffer Origin Point]] | Design approved, starting implementation |
| S03201400 | Proposed | [[Smart Clear]] | Feature doc created, needs design discussion |

This gives the user a dashboard view of all features in flight.
