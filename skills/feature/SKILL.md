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

The runbook for the `/feature` skill — drives a feature from idea through Designing → Agreed → Implementing → Testing → Done with a single F-numbered doc, an explicit user-agreement gate, and mandatory backlog/Q.md sync at every transition.

Manage a feature from initial idea through design, agreement, implementation, testing, and completion. Every feature gets a dated design document, posts to stat throughout its lifecycle, and requires explicit user agreement before implementation begins.

**MANDATORY: Post to stat at every lifecycle transition. The user monitors features via the Ops page.**

**MANDATORY: Commit discipline.** Before starting a new feature or switching to any other activity, commit all uncommitted work from the current feature. The natural commit point is the transition — not when you think you're done, but when you're about to do something else.

**Question format**: the `## Open Questions` H2 below the H1 follows the [[DSC ask-format]] discipline (five-piece layout, block-IDs, Phase 1/2/3 lifecycle).

## When to Use

When the user says "let's build a feature", "new feature", "I want to add", "design a feature", or when work is significant enough to warrant a design document rather than a quick code change.

## Lifecycle

```
Designing → Agreed → Implementing → Testing → Done
```

The feature lifecycle uses the canonical state vocabulary from the `[[SKA workflow]]` discipline. Two feature-specific accommodations:

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

**Discipline: write the `## Success Criteria` block at creation time.** Per `[[DSC verification]]`, every feature doc has a `## Success Criteria` H2 near the top (after Summary, before Design) with the verification tier declared explicitly. Four tiers, ranked from most preferred (top) to least preferred (bottom):

- **Tier 1: Agent-immediate.** Agent runs a check in the same turn the work completes. Runnable command, deterministic observation. (Best.)
- **Tier 2: Agent-over-time.** Agent owns the deferred check (soak test, recurrence watchdog, scheduled re-run). User is not involved.
- **Tier 3: User-passive.** User notices in normal use; signal is obvious if it breaks. Agent may ask once after enough time (typically a week), yes-or-no based on observation.
- **Tier 4: User-explicit.** User performs a specific concrete test action they would not otherwise do. Least preferred — only when no lower tier works.

**Blocking-action escape hatch.** If a concrete next action is strictly blocked until verification completes (filled `Blocks next:` line in the Success Criteria block), tier 1 or tier 2 is required. "Nice to have" or "would feel more confident" does not qualify; the blocked action must genuinely be unable to begin until verified.

**Pick the highest applicable tier.** If you find yourself writing tier 4 with no Blocks-next, pause and reconsider: could a passive signal work? Could the user notice this in normal use? Often the answer is yes and the right tier is 3.

Per `[[CAB Backlog]]` § Numbering policy, F-numbers are monotonic-forever, never recycled, **zero-padded to three digits** as `F001` … `F999`. The F-number is **minted by the workflow skill's `state task create`** in § 1.5 below — run § 1.5 first (after the collision check in § 1b), parse the assigned `F<NNN>` from its stdout, then create the feature doc in the anchor's Features folder. Per **F142** the canonical location is the **Design** folder (Features is a design artifact, D07): `{NAME} Design/{NAME} Features/F{NNN} — {Feature Name}.md`.

If `{NAME} Design/{NAME} Features/` doesn't exist, create it. (Legacy anchors still hold features at `{NAME} Track/{NAME} Features/`; the workflow scripts read both during the F142 rollout — but **new** docs go in the Design location.) Filenames carry the F-number prefix from the mint (zero-padded). **Do not read the backlog file directly to compute the next F-number** — `state task create` is the canonical mint.

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

This is the one place in `/feature` where an inline question is appropriate (vs. routing through `/query`'s batch surface): it's a yes/no creation-time prompt that needs an answer in the same turn, and the user is in active mode by virtue of having invoked `/feature`.

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

(**No boilerplate prose** under `## Open Questions` or `### Resolved` headings. No "Blocking decisions / cannot move from Designing → Agreed" intro. Just the heading then the bullets. Per durable feedback memory.)

## Summary

{1-2 paragraphs}

## Success Criteria

**Tier:** 1 (agent-immediate) | 2 (agent-over-time) | 3 (user-passive) | 4 (user-explicit)
**Blocks next:** none, OR [[F<n>]] (link to action this verification gates)

**What done looks like.** {One or two sentences describing the falsifiable end-state.}

**How it will be verified.** {The specific check, sized to the tier — runnable command for tier 1; deferred-agent-check for tier 2; user-passive-observation for tier 3; specific user-action-steps for tier 4.}

## Design

{The design: API proposals, architecture changes, trade-offs.}

## Status

Designing — awaiting design discussion.

## Resolved

(Bottom-of-doc archive of all resolved decisions — both agent-auto-decided and user-answered. Each entry is an H3. Populated as decisions resolve; never deleted; this is the historical record.)

### {Title — H3, agent-decided form}
**Choice:** {what was decided}

{Brief reasoning. Alternatives considered. Why they were rejected.}

### Q{N} — {Title — H3, user-answered form}
**Choice:** {what was decided}

{Brief reasoning. Includes what was discussed; references Design § X if the resolution was incorporated.}
```

**Lifecycle phases for Questions:**

- **Phase 1 — pending user Qs exist.** `## Open Questions` H2 sits directly below the H1, containing pending Qs. Resolved Qs accumulate inside as a `### Resolved` H3 sub-section *until all are answered*.
- **Phase 2 — all Qs resolved.** Delete the `## Open Questions` H2 entirely. Migrate the staged `### Resolved` H3 content to the bottom `## Resolved` H2 (creating it if absent). Top of doc is now clean: H1 → Summary → Design → Status → Resolved.
- **Phase 3 — new Q arises later.** Recreate `## Open Questions` H2 below H1 with the new Q. Same lifecycle as Phase 1.
- **Auto-decisions skip Phase 1 entirely.** Agent decisions made under the [[F068 — Assume-and-announce discipline (Drive mode)|F068]] visibility + low-recoverability rule go *directly* into the bottom `## Resolved` H2 as H3 entries, without staging at top. They co-exist there with user-answered Qs.

**Structural rules:**
- **H1 carries the anchor-slug breadcrumb + F-number.** Format: `# [[{NAME}]] · F{n} — {Feature Name}`. The leading `[[{NAME}]]` is a wiki-link to the anchor page (jumps back to the anchor's home from any feature doc) and tells the reader at a glance which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them.
- **`## Open Questions` lives below H1 only while pending user Qs exist** — deleted otherwise.
- **`## Resolved` at the bottom holds all resolved decisions as H3 entries** — both agent-decided and user-answered. The H3 outline IS the decision list; click any H3 to read its full record. H3 title format: `### Q{N} — {Title}` for user-answered (Q-numbered); `### {Title}` for agent-decided (no Q-number — they were never asked). Each H3 body has: `**Choice:** X.` + brief reasoning + alternatives considered + why rejected.
- The `/query` skill (`[[SKA queries]]`) is the universal asking subroutine — feature docs, PRDs, plan docs, anything with questions follows the same shape. Invoke `/query --doc <path>` to add questions to a feature doc; the runbook handles formatting, glance, and global-page maintenance.

**When to ask vs auto-decide (per [[F068 — Assume-and-announce discipline (Drive mode)|F068]] amendment 2026-05-22):**

Before adding a question to `## Open Questions`, self-check: is the choice **visible** (user encounters it in normal workflow within a session or two) AND has **low recoverability cost** (cheap to reverse later — accounting for downstream lock-in, not just whether reversal is theoretically possible)?

- If BOTH = yes → don't ask. Emit `**Assuming: <choice>.**` in the moment AND add an H3 entry directly under `## Resolved` at the bottom of the feature doc. The H3 title is the short decision name (no Q-number); body is `**Choice:** X.` plus brief reasoning and alternatives considered.
- If EITHER = no → escalate to `## Open Questions` as a numbered Q.

Always ASK when: invisible OR high recoverability cost OR irreversible (push / external messages / hard deletes / deploys) OR interface-decision-sticky (slash command names, frontmatter schemas, default keybindings, durable file naming). New-feature-without-approval always asks.

### 1.5. Mint the backlog (or roadmap) row — MANDATORY (per [[SKA workflow]] § Active-work invariant)

Per the active-work invariant: **every feature doc must be reachable from `{NAME} Backlog.md` or `{NAME} Roadmap.md`** at creation time. No exceptions, no `--orphan` flag.

**For a backlog feature** (the common case): mint the row via the workflow skill's `state task create`. This both reserves the F-number (returned in stdout) and creates the row atomically — no direct backlog edits. Run this **before** creating the feature doc file in § 1 (the F-number names the file).

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task create --status Designing --title "{Feature Name}"
```

Output: `{NAME}: added F<NNN> in Now [Designing]` — parse `F<NNN>` from the second word after `added`. Use that F-number for the feature doc filename (§ 1).

After § 1 creates the feature doc, run a follow-up call to add the wiki-link body so the row links back to the new doc:

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update F<NNN> --body "→ [[F<NNN> — {Feature Name}]]"
```

Use `--horizon Later` for parking-mode stubs (`/feature` used to file something for later). Use `--status Questions` once the Open Questions block has been written and the row should surface to triage as user-actionable.

**For a roadmap milestone**: the feature doc gets an M-number prefix (`Features/M{n} — {Name}.md` with H1 `# M{n} — {Name}`). `state` is backlog-only — roadmap milestones currently use a separate path (manual `Roadmap.md` edit). M-numbers are hierarchical (M1, M1.2, M1.2.3) — see `[[SKA workflow]]` § Active-work invariant for the namespace rules.

**The row is minted in the SAME turn the feature doc is created.** Don't defer; orphans accumulate when the row-creation step is "for later."

### 1a. Surface the Doc — glance only when adding/modifying a pending question AND the user is engaging now

Glance the doc *only when both conditions hold*: (1) the edit added or modified a pending question, AND (2) you're in **active mode** — the user is engaging with this feature right now. See [[SKA queries]] § Active vs Parking mode for the full rule. (Better still: invoke `/query --doc <path>` and the skill handles the glance for you.)

```bash
open "<path to feature doc>"
```

**Active mode (do glance)** — user said "let's design X" / "let's discuss X" / invoked `/feature` for this work without saying "for later." The user expects to answer questions in this turn or the next.

**Parking mode (don't glance)** — user said "put it on the backlog" / "for later" / "we'll figure that out" / `/feature` was used to file a stub. The feature doc is created and questions captured, but the user defers engagement. The doc surfaces later when the user opens a backlog item that points at it, or runs `/groom`.

**Never glance when the edit only resolved questions**, regardless of mode. Resolution doesn't surface new state for the user.

**On the create step:** glance only if you're in active mode. If creating a feature stub for backlog filing, skip the glance — the user just told you to file it; opening the file at them is the opposite of what they asked.

### 1c. Refresh the anchor's Q.md section — automatic via `state`

**Rule:** every Phase transition in `/feature` (Phase 1 → Phase 2 when all Qs resolve; Phase 2 → Phase 3 when a new Q arises; Status changes Designing → Agreed → Implementing → Done) is a state-touching action that must update the backlog row + refresh `~/ob/kmr/Q.md`.

**The mechanism:** call `state task update` with the new status for **every** transition — it auto-refreshes Q.md as a side effect (invokes `audit-q.py --scope backlog --anchor {NAME} --fix`).

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update F<NNN> --status Agreed
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update F<NNN> --status Active
# ... and so on for Verify, Done.
```

Omit `--horizon` to leave the row in its current H2; pass `--horizon Active` / `--horizon Done` to move it.

The audit's fix-by-default behavior catches any drift introduced by this skill's row edits — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (rare) files a `QFix [Ready]` backlog entry the user can address later. **Surfacing any QFix entry is part of this skill's "done" criteria** — read the script's stderr/stdout output for QFix lines, surface them to the user.

**Active mode (the user is engaging now)** — after the post-condition runs, the glance step (§ 1a) already opens `~/ob/kmr/Q.md` per the F075 single-glance-target rule.

**Parking mode skips the glance**, but the Q.md update post-condition **still fires** — Q.md is the persistent dashboard; it should reflect the just-filed feature even when the user said "for later." The next time the user opens Q.md, the parked feature is at the top.

### 2. Post to Stat

```bash
skl-stat add "Proposed" "<Feature Name>" "Feature doc created"
```

### 3. Design Discussion

Work with the user to flesh out the design. **Per F128/F129 (2026-06-07), Q-state changes delegate to `state q`** — the canonical state-editor enforces ask-format spec, Q-numbering policy, and Phase 1/2/3 lifecycle at write time. Agents should not hand-edit `## Open Questions` blocks.

```bash
# Resolve a Q (script auto-migrates to bottom ## Resolved with audit trail):
state --anchor {NAME} q answer F<n> -n <Q-num> --choice "(A)" < resolution-body.md

# Add a new Q mid-discussion:
state --anchor {NAME} q add F<n> < q-body.md

# Remove a Q that's no longer relevant (preserves audit trail in ### Removed):
state --anchor {NAME} q remove F<n> -n <Q-num> --reason "..."

# Rewrite a Q's body (no --force gate in F129; verb name IS the explicit intent):
state --anchor {NAME} q rewrite F<n> -n <Q-num> < new-body.md
```

After EVERY Q-state change, update the Design (or relevant) section with what the resolution means in the spec. The resolved question and the updated design ship together. **Resolution body should include "Incorporated into Design § `<section>`"** as the closing line so the audit trail in `## Resolved` cross-references where the answer shaped the design.

When a new question arises mid-discussion, add it via `q add` and glance the file (per step 1a). When you resolve a question, **don't** glance — even if other questions are still pending. The glance is only for moments when the user needs to react to *new or changed* questions.

Full F129 spec: [[SKL State]]. Predecessor: [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] (legacy CLI shape).

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
| S03210930 | Implementing | [[F017 — Standard Rulesets]] | 3 of 11 rulesets created |
| S03200917 | Agreed | [[F005 — Buffer Origin Point]] | Design approved |
| S03201400 | Proposed | [[Smart Clear]] | Feature doc created |
