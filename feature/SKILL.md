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

Determine the next F-number for the anchor (highest existing F-number + 1; per `[[CAB Backlog]]` § Numbering policy — monotonic-forever, never recycled, **zero-padded to three digits** as `F001` … `F999`). Create the feature doc in the project's Features folder:

```
{anchor}/Docs/Plan/Features/F{NNN} — {Feature Name}.md
```

If the Features folder doesn't exist, create it. Filenames carry the F-number prefix zero-padded to three digits; the padding is structural — it makes filename sort order match numeric order without special tooling.

#### 1b. Collision check — vault grep for duplicate H1 (per F27)

**Before writing the file**, scan the vault for an existing feature doc with the same H1. F-numbers are per-anchor namespaces that reset at F1 in each anchor (per `[[CAB Backlog]]` § Numbering policy), so the same `F<n> — <Title>` filename can appear in multiple anchors. Obsidian wiki-link resolution by path-proximity makes this safe within an anchor but ambiguous across anchors — F27 catches the collision at creation time.

**Procedure:**

1. **Resolve the vault root** from `cwd` — walk up to the kmr root (the directory containing the user's anchors), or fall back to `~/ob/kmr/`.
2. **Grep all `Features/` folders** under the vault root for an H1 that exactly matches `# F<n> — <Title>` with the new file's title. Equivalent forms are acceptable:
   ```bash
   grep -lr "^# F[0-9]\+ — <exact title>$" <vault root>/**/Features/
   ```
   Or a Read of every `Features/` folder followed by H1 inspection.
3. **Branch on results:**
   - **Zero matches** — proceed normally to the file write.
   - **One or more matches in *other* anchors** — surface as a single inline question (active mode, since the user is engaging with `/feature` right now):
     ```
     /feature — heads up: this title already exists at:
     - <path/to/other/file>
     [...]
     Options:
       (A) proceed with the same title — cross-anchor wiki-links to either file must be qualified per [[CAB Backlog]] § Wiki-link conventions for feature docs.
       (B) rename — suggest a slightly disambiguating title and re-run.
     Recommendation: lean (A) if cross-anchor links to this feature are not anticipated; lean (B) if you expect cross-anchor references.
     ```
     Wait for the user's pick before writing the file.
   - **Match in the *same* anchor** — within-anchor title collision is genuinely bad (within-anchor titles must be unique). Surface as a stronger error: "Within-anchor title collision — pick a different title." Block creation; do not write the file.

This is the one place in `/feature` where an inline question is appropriate (vs. routing through `/ask`'s batch surface): it's a yes/no creation-time prompt that needs an answer in the same turn, and the user is in active mode by virtue of having invoked `/feature`.

**Feature doc structure — Open Questions sits BELOW the H1 while any pending Qs exist; deleted entirely once all are resolved, with answered Qs migrating to a `## Resolved` H2 at the bottom of the doc.** The lifecycle:

```markdown
---
description: {one-line description}
---

# [[{NAME}]] · F{n} — {Feature Name}

## Open Questions

- **Q1 — {short question}** — {context + options}
- **Q2 — {short question}** — {context + options}

### Resolved

- **Q0 — {earlier question}** — **Resolution:** {decided X because Y}. Incorporated into Design § {section}.

(**No boilerplate prose** under `## Open Questions` or `### Resolved` headings. No "Blocking decisions / cannot move from Designing → Agreed" intro, no "(Temporary holding pen for resolved Qs...)" caption. Just the heading then the bullets. Per durable feedback memory.)

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
- **H1 carries the anchor-slug breadcrumb + F-number.** Format: `# [[{NAME}]] · F{n} — {Feature Name}`. The leading `[[{NAME}]]` is a wiki-link to the anchor page (jumps back to the anchor's home from any feature doc) and tells the reader at a glance which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them.
- **`## Open Questions` lives below H1 only while pending Qs exist** — deleted otherwise.
- **`## Resolved` at the bottom of the doc is the permanent archive** — populated when all Qs reach resolution; never deleted.
- The `/ask` skill (`[[ask]]`) is the universal asking subroutine — feature docs, PRDs, plan docs, anything with questions follows the same shape. Invoke `/ask --doc <path>` to add questions to a feature doc; the runbook handles formatting, glance, and global-page maintenance.

### 1.5. Add a backlog (or roadmap) row — MANDATORY (per [[workflow]] § Active-work invariant)

Per the active-work invariant: **every feature doc must be reachable from `{NAME} Backlog.md` or `{NAME} Roadmap.md`** at creation time. No exceptions, no `--orphan` flag.

**For a backlog feature** (the common case): add an `F{n}` row to `{NAME} Backlog.md` with the feature's F-number and a `→ [[F{n} — {Feature Name}]]` link. Bracket = `[Designing]` (fresh feature with open questions about to be parked) or `[Questions]` (after the Open Questions block has been written). Default placement: under `## Now` H2.

```
- **F{n} — {Feature Name}** [Designing] — → [[F{n} — {Feature Name}]]
```

**For a roadmap milestone**: the feature doc gets an M-number prefix (`Features/M{n} — {Name}.md` with H1 `# M{n} — {Name}`). Add a milestone row to `{NAME} Roadmap.md`. M-numbers are hierarchical (M1, M1.2, M1.2.3) — see `[[workflow]]` § Active-work invariant for the namespace rules.

**The row is added in the SAME turn the feature doc is created.** Don't defer; orphans accumulate when the row-creation step is "for later."

### 1a. Surface the Doc — glance only when adding/modifying a pending question AND the user is engaging now

Glance the doc *only when both conditions hold*: (1) the edit added or modified a pending question, AND (2) you're in **active mode** — the user is engaging with this feature right now. See [[ask]] § Active vs Parking mode for the full rule. (Better still: invoke `/ask --doc <path>` and the skill handles the glance for you.)

```bash
open "<path to feature doc>"
```

**Active mode (do glance)** — user said "let's design X" / "let's discuss X" / invoked `/feature` for this work without saying "for later." The user expects to answer questions in this turn or the next.

**Parking mode (don't glance)** — user said "put it on the backlog" / "for later" / "we'll figure that out" / `/feature` was used to file a stub. The feature doc is created and questions captured, but the user defers engagement. The doc surfaces later when the user opens a backlog item that points at it, or runs `/groom`.

**Never glance when the edit only resolved questions**, regardless of mode. Resolution doesn't surface new state for the user.

**On the create step:** glance only if you're in active mode. If creating a feature stub for backlog filing, skip the glance — the user just told you to file it; opening the file at them is the opposite of what they asked.

### 1c. Refresh Triage if you're about to ask the user questions about this feature

**Rule (cheap check, expensive action only when needed):** if the feature was just created with pending Qs in `## Open Questions` AND you're going to discuss those Qs with the user in this turn or the next (i.e., active mode, not parking), the feature MUST be present in `{NAME} Triage.md` so the user can navigate to it.

**Procedure:**

1. Read `{NAME} Triage.md` (~200 tokens, sub-second). Search for the new F-number.
2. If found → done; Triage is current enough.
3. If absent → invoke `/triage` (regenerates Triage and the anchor's section in `~/ob/kmr/Q.md`).

**Why this is its own step (not just "always /triage"):** running /triage reads every in-scope feature doc to count Qs (~30 sec wall-clock on a busy anchor). Wall-clock loop time with the user matters more than tokens — auto-/triaging on every /feature would slow the design loop. The cheap-check + conditional-fire pattern keeps the common case (already in Triage) instant and pays the cost only when needed.

**Parking mode skips this step entirely.** If the user said "put it on the backlog" / "for later," they're not engaging now; Triage will refresh on the next user-driven /triage. Same active/parking gate as the glance rule above.

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
- **H1 carries the anchor-slug breadcrumb + F-number** — `# [[{NAME}]] · F{n} — {Feature Name}`.
- **Open Questions BELOW the H1** while pending Qs exist; deleted entirely when zero pending. Resolved Qs migrate to a `## Resolved` H2 at the bottom of the doc.
- **`open` the doc after every Open Questions edit (in active mode)** — mandatory, per step 1a.
- **Status near the bottom** — single line indicating lifecycle stage. (`## Resolved`, when present, sits below Status as the historical archive.)
- **No implementation details in the feature doc** — the feature doc is the *what* and *why*.

## Stat Integration

Every lifecycle transition posts to stat. The user can monitor all active features from the Ops page:

| S# | Status | Output | Activity |
|----|--------|--------|----------|
| S03210930 | Implementing | [[F017 — Standard Rule Sets]] | 3 of 11 rule sets created |
| S03200917 | Agreed | [[F005 — Buffer Origin Point]] | Design approved |
| S03201400 | Proposed | [[Smart Clear]] | Feature doc created |
