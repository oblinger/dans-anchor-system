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
requires:: vault, anchor-cli, skill:ask, skill:mint, facet:backlog, facet:query
subsystem:: [[DAS Drive Design]] — the Drive group's subsystem profile

The runbook for the `/feature` skill — drives a feature from idea through Designing → Agreed → Implementing → Testing → Done with a single F-numbered doc, an explicit user-agreement gate, and mandatory backlog/Q.md sync at every transition.

| Table of Contents |  |
|---|---|
| **[[#When to Use]]** |  |
| **[[#Lifecycle]]** |  |
| **[[#Runbook]]** |  |
|    [[#1. Create the Feature Document]] |  |
|    [[#1.5. Mint the backlog (or roadmap) row — MANDATORY (per [[SKA workflow]] § Active-work invariant)]] |  |
|    [[#1a. Surface the Doc — glance only when adding/modifying a pending question AND the user is engaging now]] |  |
|    [[#1c. Refresh the anchor's Q.md section — automatic via `state`]] |  |
|    [[#2. Design Discussion]] |  |
|    [[#3. Reach Agreement]] |  |
|    [[#4. Implement]] |  |
|    [[#5. Test]] |  |
|    [[#5a. Promote Success Criteria — mint the FINAL question (F305 D5)]] |  |
|    [[#6. Complete]] |  |
| **[[#Commit Discipline]]** |  |
| **[[#Feature Doc Conventions]]** |  |

Manage a feature from initial idea through design, agreement, implementation, testing, and completion. Every feature gets a dated design document and requires explicit user agreement before implementation begins.

**MANDATORY: Commit discipline.** Before starting a new feature or switching to any other activity, commit all uncommitted work from the current feature. The natural commit point is the transition — not when you think you're done, but when you're about to do something else.

**Question format**: the `## Open Questions` H2 (first H2, below the H1) follows the [[DAS ask-format]] discipline (five-piece layout, block-IDs, the two-zone block lifecycle).

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

**Discipline: write the `## Success Criteria` block at creation time.** Per `[[DAS verification]]`, every feature doc has a `## Success Criteria` H2 near the top (after Summary, before Design) with the verification tier declared explicitly. Four tiers, ranked from most preferred (top) to least preferred (bottom):

- **Tier 1: Agent-immediate.** Agent runs a check in the same turn the work completes. Runnable command, deterministic observation. (Best.)
- **Tier 2: Agent-over-time.** Agent owns the deferred check (soak test, recurrence watchdog, scheduled re-run). User is not involved.
- **Tier 3: User-passive.** User notices in normal use; signal is obvious if it breaks. Agent may ask once after enough time (typically a week), yes-or-no based on observation.
- **Tier 4: User-explicit.** User performs a specific concrete test action they would not otherwise do. Least preferred — only when no lower tier works.

**Blocking-action escape hatch.** If a concrete next action is strictly blocked until verification completes (filled `Blocks next:` line in the Success Criteria block), tier 1 or tier 2 is required. "Nice to have" or "would feel more confident" does not qualify; the blocked action must genuinely be unable to begin until verified.

**Pick the highest applicable tier.** If you find yourself writing tier 4 with no Blocks-next, pause and reconsider: could a passive signal work? Could the user notice this in normal use? Often the answer is yes and the right tier is 3.

Per `[[DAS Backlog]]` § Numbering policy, F-numbers are monotonic-forever, never recycled, **zero-padded to three digits** as `F001` … `F999`. The F-number is **minted by the workflow skill's `state define <anchor> Backlog F+`** in § 1.5 below — run § 1.5 first (after the collision check in § 1b), parse the assigned `F<NNN>` from its stdout, then create the feature doc in the anchor's Features folder. Per **F142** the canonical location is the **Design** folder (Features is a design artifact, D07): `{slug} Design/{slug} Features/{SLUG}{NNN} - {Feature Name}.md`.

**The filename is the slug fused to a bare number, in ASCII (F300, 2026-08-02).** `{SLUG}` is the anchor's slug **read verbatim from `.anchor`'s `slug:` key** — never upcased, never downcased, never translated to the file-prefix form. Most are uppercase (`TINK`, `SKA`, `LUMEN`, `MUX`, `HA`, `OBU`) but `Warden` is mixed-case, so the rule is *the slug's own casing*, not "uppercase". The separator is a plain **ASCII hyphen** with a space each side. Dan, 2026-08-02: *"whatever the slug is with that case, without a space and then the number… the idea is really that I can quickly type it once you know the structure of it"* and *"make sure that it's not an M dash… We don't want to get fancy with the file name."*

The slug is in the filename because F-numbers are a **per-anchor** namespace that resets at F1 in every anchor, so a bare `F26` names as many files as there are anchors and cannot be turned into a file search — Dan, 2026-08-02: *"if you tell me that you're working on F26 — the problem is, I can't actually find that document, because the slug is not part of it."* Fusing it to the number makes `TINK300` a **stronger** discriminator than `F300` ever was: it names one anchor rather than every anchor at once.

**Feature titles avoid em-dashes.** The filename is a faithful ASCII transcription of the H1 title (R-fct-features-03 requires the two to match), so a title carrying an em-dash could not round-trip without leaving the filename typographic in one position and ASCII in the next. Prefer a colon, a comma, or a shorter title. `Hook fan-in - one computed entrypoint per hook moment`, not `Hook fan-in — one computed entrypoint per hook moment`.

**Only the filename changes.** In chat, keep saying the bare `F300` — the session window already names the anchor, so the context that disambiguates is on screen; an F-number is ambiguous only *out of* context, and the filename is the one surface that has none. Backlog rows, block-IDs (`^F300-Q1`), `queries.md`, and `Q.md` also stay bare. Where a wiki-link must *target* a slug-named doc, use the pipe form so the displayed text stays bare: `[[TINK300 - Title|F300]]` — which is what audit-q **C37** requires anyway.

**Older docs keep their form and are never renamed** (Dan's call). Two of them: the bare `F{NNN} — {Title}.md` carried by everything before 2026-08-02, and the slug-prefixed `{slug} F{NNN} — {Title}.md` (F298) from the single morning that convention lasted. The corpus stays permanently mixed; every matcher accepts all three forms rather than switching between them. The canonical grammar — including the `F` **reconstruction** the fused form requires — is `backlog_edit.feature_number`.

If `{slug} Design/{slug} Features/` doesn't exist, create it. (Legacy anchors still hold features at `{slug} Track/{slug} Features/`; the workflow scripts read both during the F142 rollout — but **new** docs go in the Design location.) Filenames carry the F-number from the mint (zero-padded). **Do not read the backlog file directly to compute the next F-number** — `state define <anchor> Backlog F+` is the canonical mint.

#### 1b. Collision check — within-anchor title only (F27, narrowed by F298)

**Before writing the file**, check the *current anchor's* Features folder for an existing feature doc with the same H1 title. Within-anchor titles must be unique.

**The cross-anchor half of this check retired with F298.** It existed because the same `F<n> — <Title>` filename could appear in several anchors, making Obsidian's path-proximity wiki-link resolution ambiguous across anchors. With the slug in the filename that collision is **impossible by construction** — `[[SKA294 - Title]]` and `[[TINK294 - Title]]` are distinct filenames — so there is nothing left to warn about and no inline question to ask. Two anchors may now freely hold same-titled features.

**Procedure:**

1. **Read the current anchor's `{slug} Features/` folder** (both the `{slug} Design/` and legacy `{slug} Track/` locations).
2. **Branch on results:**
   - **No same-titled doc in this anchor** — proceed to the file write.
   - **Same title already in this anchor** — surface a hard error: "Within-anchor title collision — pick a different title." Block creation; do not write the file.

No vault-wide grep is needed, and no user prompt is raised: the one surviving case is an error the agent resolves by choosing a different title, not a fork the user decides.

**Feature doc structure — Open Questions is the first H2 BELOW the H1 (after the H1's one-line orientation) while any pending Qs exist; deleted entirely once all are resolved, with answered Qs migrating to a `## Resolved` H2 at the bottom of the doc** (per [[F241 — Questions block below H1 + state-stamped integrity hash|F241]], 2026-07-15 — supersedes the earlier above-the-H1 placement). The lifecycle:

```markdown
---
description: {one-line description}
---

# [[{slug}]] · F{n} — {Feature Name}
{One-line orientation summary of the feature.}

## Open Questions
<!-- state:q XX -->

- **Q1 — {short question}** — {context + options}
- **Q2 — {short question}** — {context + options}

### Resolved

- **Q0 — {earlier question}** — **Resolution:** {decided X because Y}. Incorporated into Design § {section}.

(**No boilerplate prose** under `## Open Questions` or `### Resolved` headings. No "Blocking decisions / cannot move from Designing → Agreed" intro. Just the heading then the bullets. Per durable feedback memory. **Placement:** while pending Qs exist this block is the file's first H2, immediately below the H1's orientation line. The `<!-- state:q XX -->` stamp is written by the state script on every write — do not hand-edit it or the block; route changes through `state <verb> <anchor> <doc> Q<n>`. The last `resolve` of a round deletes this block and migrates its decisions to the bottom `## Resolved` H2 — `state` does that, not you.)

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

**Lifecycle for Questions (F291) — you call `resolve`; the transitions are not yours to make:**

- **The block exists, with N unresolved.** `## Open Questions` H2 is the file's first H2, directly BELOW the H1 (after its one-line orientation). It carries a `<!-- state:q XX -->` integrity stamp the state script maintains; hand-edits that break it trip the on-write warning (R-state-region-03 / audit-q C48). The block has two zones: unresolved questions first, then a `### Resolved` zone. `state resolve <anchor> <doc> Q<n>` moves a question from the first to the second — it does not remove it, so the open count is always the prefix above the zone heading.
- **The block has migrated.** The `resolve` that empties the unresolved zone also deletes the block and writes every entry to the top of the bottom `## Resolved` H2, keeping each `^F<n>-Q<n>` block-ID. **`state` does this; the agent performs no part of it.** Top of doc is then clean: H1 → Summary → Design → Status → Resolved.
- **A new Q later re-opens the block**, numbered above the doc's high-water mark rather than recycling. **This applies even when the feature is `[Done]`** — a re-decision or extension of a feature's design reopens *this doc* (the backlog row rebrackets `[Questions]`); never mint a spin-off backlog row to host the decision (per [[Query PRD]] § Work-item identity: decisions live on the feature's record, rows carry work). When the new resolution supersedes an earlier one, stamp the superseded `## Resolved` entry with a one-line *"superseded {date} → Q{n}"* in the same pass.
- **Auto-decisions never enter the block.** Agent decisions made under the [[F068 — Assume-and-announce discipline (Drive mode)|F068]] visibility + low-recoverability rule go *directly* into the bottom `## Resolved` H2 as H3 entries. They co-exist there with migrated rounds — which is also why that section is hand-writable while the open block is not.

**Structural rules:**
- **H1 carries the anchor-slug breadcrumb + F-number.** Format: `# [[{slug}]] · F{n} — {Feature Name}`. The leading `[[{slug}]]` is a wiki-link to the anchor page (jumps back to the anchor's home from any feature doc) and tells the reader at a glance which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them.
- **`## Open Questions` lives below the H1 as the file's first H2 only while pending user Qs exist** — deleted otherwise; answered Qs migrate to the bottom `## Resolved` H2. The state script stamps the block for tamper-evidence (F241).
- **`## Resolved` at the bottom holds all resolved decisions as H3 entries** — both agent-decided and user-answered. The H3 outline IS the decision list; click any H3 to read its full record. H3 title format: `### Q{N} — {Title}` for user-answered (Q-numbered); `### {Title}` for agent-decided (no Q-number — they were never asked). A migrated Q-entry is machine-written as question → `**Resolved:**` → options → `**Lean:**`; an agent-decided entry is hand-written as `**Choice:** X.` + brief reasoning + alternatives considered + why rejected.
- The `/ask` skill (`[[SKA queries]]`) is the universal asking subroutine — feature docs, PRDs, plan docs, anything with questions follows the same shape. Invoke `/ask --doc <path>` to add questions to a feature doc; the runbook handles formatting, glance, and global-page maintenance.

**When to ask vs auto-decide (per [[F068 — Assume-and-announce discipline (Drive mode)|F068]] amendment 2026-05-22):**

Before adding a question to `## Open Questions`, self-check: is the choice **visible** (user encounters it in normal workflow within a session or two) AND has **low recoverability cost** (cheap to reverse later — accounting for downstream lock-in, not just whether reversal is theoretically possible)?

- If BOTH = yes → don't ask. Emit `**Assuming: <choice>.**` in the moment AND add an H3 entry directly under `## Resolved` at the bottom of the feature doc. The H3 title is the short decision name (no Q-number); body is `**Choice:** X.` plus brief reasoning and alternatives considered.
- If EITHER = no → escalate to `## Open Questions` as a numbered Q.

Always ASK when: invisible OR high recoverability cost OR irreversible (push / external messages / hard deletes / deploys) OR interface-decision-sticky (slash command names, frontmatter schemas, default keybindings, durable file naming). New-feature-without-approval always asks.

### 1.5. Mint the backlog (or roadmap) row — MANDATORY (per [[SKA workflow]] § Active-work invariant)

Per the active-work invariant: **every feature doc must be reachable from `{slug} Backlog.md` or `{slug} Roadmap.md`** at creation time. No exceptions, no `--orphan` flag.

**For a backlog feature** (the common case): mint the row via the workflow skill's `state define <anchor> Backlog F+`. This both reserves the F-number (returned in stdout) and creates the row atomically — no direct backlog edits. Run this **before** creating the feature doc file in § 1 (the F-number names the file).

```bash
echo '- **F+ — {Feature Name}** [Designing]' | ~/.claude/skills/workflow/scripts/state define {slug} Backlog F+
```

Output: `{slug}: added F<NNN> in Now [Designing]` — parse `F<NNN>` from the second word after `added`. Use that F-number for the feature doc filename (§ 1).

After § 1 creates the feature doc, run a follow-up call to add the wiki-link body so the row links back to the new doc:

```bash
~/.claude/skills/workflow/scripts/state set {slug} Backlog F<NNN> --doc "{SLUG}<NNN> - {Feature Name}"
```

`--doc` writes the pointer `→ [[{SLUG}<NNN> - {Feature Name}|F<NNN>]]` and nothing else — the text after it regenerates from the doc (F332), and `--body` on a doc-backed row is **refused** (T578, 2026-08-28) rather than half-landed. The link **targets** the filename (Obsidian resolves by filename, so it must) and **displays** the bare `F<NNN>`. For an older doc, target whichever form its file actually carries — `[[{slug} F<NNN> — {Feature Name}|…]]` or the plain `[[F<NNN> — {Feature Name}]]`; those are never renamed.

Use `--horizon Later` for parking-mode stubs (`/feature` used to file something for later). Use `--status Questions` once the Open Questions block has been written and the row should surface (via the queries render) as user-actionable.

**For a roadmap milestone**: the feature doc gets an M-number prefix (`Features/M{n} — {Name}.md` with H1 `# M{n} — {Name}`). `state` is backlog-only — roadmap milestones currently use a separate path (manual `Roadmap.md` edit). M-numbers are hierarchical (M1, M1.2, M1.2.3) — see `[[SKA workflow]]` § Active-work invariant for the namespace rules.

**The row is minted in the SAME turn the feature doc is created.** Don't defer; orphans accumulate when the row-creation step is "for later."

### 1a. Surface the Doc — glance only when adding/modifying a pending question AND the user is engaging now

Glance the doc *only when both conditions hold*: (1) the edit added or modified a pending question, AND (2) you're in **active mode** — the user is engaging with this feature right now. See [[Tink queries]] § Active vs Parking mode for the full rule. (Better still: invoke `/ask --doc <path>` and the skill handles the glance for you.)

```bash
open "<path to feature doc>"
```

**Active mode (do glance)** — user said "let's design X" / "let's discuss X" / invoked `/feature` for this work without saying "for later." The user expects to answer questions in this turn or the next.

**Parking mode (don't glance)** — user said "put it on the backlog" / "for later" / "we'll figure that out" / `/feature` was used to file a stub. The feature doc is created and questions captured, but the user defers engagement. The doc surfaces later when the user opens a backlog item that points at it, or runs `/groom`.

**Never glance when the edit only resolved questions**, regardless of mode. Resolution doesn't surface new state for the user.

**On the create step:** glance only if you're in active mode. If creating a feature stub for backlog filing, skip the glance — the user just told you to file it; opening the file at them is the opposite of what they asked.

### 1c. Refresh the anchor's Q.md section — automatic via `state`

**Rule:** every lifecycle transition in `/feature` (the block migrating when its last Q resolves; a new Q re-opening it; Status changes Designing → Agreed → Implementing → Done) is a state-touching action that must update the backlog row + refresh `~/ob/kmr/Q.md`.

**The mechanism:** call `state set <anchor> Backlog F<NNN>` with the new status for **every** transition — it auto-refreshes Q.md as a side effect (invokes `audit-q.py --scope backlog --anchor {slug} --fix`).

```bash
~/.claude/skills/workflow/scripts/state set {slug} Backlog F<NNN> --status Agreed
~/.claude/skills/workflow/scripts/state set {slug} Backlog F<NNN> --status Active
# ... and so on for Verify, Done.
```

Omit `--horizon` to leave the row in its current H2; pass `--horizon Active` / `--horizon Done` to move it.

The audit's fix-by-default behavior catches any drift introduced by this skill's row edits — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (rare) files a `QFix [Ready]` backlog entry the user can address later. **Surfacing any QFix entry is part of this skill's "done" criteria** — read the script's stderr/stdout output for QFix lines, surface them to the user.

**Active mode (the user is engaging now)** — after the post-condition runs, the glance step (§ 1a) already opens `~/ob/kmr/Q.md` per the F075 single-glance-target rule.

**Parking mode skips the glance**, but the Q.md update post-condition **still fires** — Q.md is the persistent dashboard; it should reflect the just-filed feature even when the user said "for later." The next time the user opens Q.md, the parked feature is at the top.

### 2. Design Discussion

Work with the user to flesh out the design. **Per F128/F129/F236, Q-state changes delegate to `state` (the v2 query grammar)** — the canonical state-editor enforces ask-format spec, Q-numbering policy, and the block lifecycle at write time. Agents should not hand-edit `## Open Questions` blocks.

```bash
# Resolve a Q (script auto-migrates to bottom ## Resolved with audit trail):
state resolve {slug} "F<n> — {Title}" Q<num> --choice "(A)" < resolution-body.md

# Add a new Q mid-discussion:
state define {slug} "F<n> — {Title}" Q+ < q-body.md

# Remove a Q that's no longer relevant (preserves audit trail in ### Removed):
state remove {slug} "F<n> — {Title}" Q<num> --reason "..."

# Rewrite a Q's body (no --force gate in F129; verb name IS the explicit intent):
state define {slug} "F<n> — {Title}" Q<num> < new-body.md
```

After EVERY Q-state change, update the Design (or relevant) section with what the resolution means in the spec. The resolved question and the updated design ship together. **Resolution body should include "Incorporated into Design § `<section>`"** as the closing line so the audit trail in `## Resolved` cross-references where the answer shaped the design.

When a new question arises mid-discussion, add it via `Q+ define` and glance the file (per step 1a). The `q-body` **must** carry a `- **Damage:**` line whose first word is one of the six categories (`waste` / `priority` / `irreversible` / `locking` / `taste` / `other` — see [[DAS ask-format]] § The Damage field): a `waste`/`priority` question **auto-resolves on define** to your lean and never surfaces, so only genuine `irreversible`/`locking`/`taste`/`other` questions reach the user. When you resolve a question, **don't** glance — even if other questions are still pending. The glance is only for moments when the user needs to react to *new or changed* questions.

Full F129 spec: [[DAS State]]. Predecessor: [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] (legacy CLI shape).

### 3. Reach Agreement

When all open questions are resolved and the design is complete:
- Update the feature doc's Status section to "Agreed"
- Get explicit user confirmation: "This design is agreed — ready to implement?"
- Only proceed to implementation after the user says yes

**This is a gate.** Do not implement without agreement. If the user says "just do it" without a design discussion, still create the feature doc (even if minimal) and confirm before coding.

**Gate presentation — the compact confirm form (user-endorsed exemplar, 2026-07-13).** The chat message that asks for the go is NOT a paste of the feature doc; it is a compressed, one-shot-answerable summary with the doc as the deep-read behind it. Shape, top to bottom:

1. **Status line** — `F<n> → [Ready] · Status = Agreed. Design complete.`
2. **Q resolutions, one line each** — `Q1 = (A) <five-word gist>` … so the user can audit every fork without opening the doc.
3. **Implementation plan, numbered** — the concrete steps in execution order, each a single line naming the artifact it produces; include any user-action step explicitly ("walk you to System Settings → …").
4. **Cleanup/leftovers** — one `Also:` line for reverts, commits, or loose ends riding along.
5. **Single ask** — `Say go and I'll drive end-to-end.`

Why it works: the user confirms design + plan in one glance, every choice is visible as a line (not buried in prose), and the full feature doc still exists for the deeper look. Model instance: the MUSE F019 gate (trust-helper build) — status line, 3 Q-lines, 7 plan steps, one `Also:` line, one ask.

### 4. Implement

Use `/mint` or work directly. The feature doc is the spec.

During implementation:
- Reference the feature doc for decisions
- If new questions arise, add them to `## Open Questions` (pending list), run `open "<feature doc path>"` so the user sees them, and pause if the question is blocking
- Resolve any questions with the three-step discipline from § 2 before continuing
- Do NOT commit during implementation unless switching to another activity

### 5. Test

Run tests, verify the feature works as designed.

### 5a. Promote Success Criteria — mint the FINAL question (F305 D5)

When the agent believes the feature done, Success Criteria stops being passive: apply the F240 positioning test to its check. Agent-runnable (tier 1/2) → run it now. User-owned (tier 3/4) → **mint the doc's final question** — one more `Q<n>` in the doc's own numbering, in the final-question form (zero labeled options, an explicit `yes / no` cue, `- **Recommendation:** None` — the write gate admits exactly this shape) — and set the row `[Verify]`, whose class is Parked: done, nothing waiting, only the check remains. The user answers `Q<n>: yes` to close it out; **no records the outcome and closes nothing** — mint the follow-up work the failed observation implies. Never a separate `V<n>` item or a positional page handle (T127).

```bash
echo '**Q+ — Verified in use?** — <the tier-3/4 observation, phrased for the user> **yes / no**
- **Recommendation:** None
- **Damage:** taste — <what their eyes judge>' | state define <anchor> "<feature doc>" Q+
state set <anchor> Backlog F<n> --status Verify
```

### 6. Complete

When tests pass and the feature is verified (the final question answered yes):
- Update the feature doc's Status to "Done"
- Commit all uncommitted work for this feature

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

- **F-numbered filename** — `F{n} — {Feature Name}.md` in the Features folder. F-number from the anchor's monotonic-forever counter (per `[[DAS Backlog]]` § Numbering policy).
- **H1 carries the anchor-slug breadcrumb + F-number** — `# [[{slug}]] · F{n} — {Feature Name}`.
- **Open Questions as the first H2 BELOW the H1** (after the H1's orientation line) while pending Qs exist; deleted entirely when zero pending. Resolved Qs migrate to a `## Resolved` H2 at the bottom of the doc.
- **`open` the doc after every Open Questions edit (in active mode)** — mandatory, per step 1a.
- **Status near the bottom** — single line indicating lifecycle stage. (`## Resolved`, when present, sits below Status as the historical archive.)
- **No implementation details in the feature doc** — the feature doc is the *what* and *why*.

