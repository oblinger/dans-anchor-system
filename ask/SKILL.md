---
name: ask
description: Universal asking subroutine. Invoke whenever an agent has questions for the user. Routes batched, numbered, formatted questions to the right surface (a feature/PRD doc with --doc, or the project's à la carte block in {NAME} Triage.md by default). Always regenerates {NAME} Triage.md and the anchor's H2 in ~/ob/kmr/Q.md (the vault-level Agent Status dashboard). In active mode glances the file. Slash-only — "ask" is too common a spoken word to be a DMUX prefix-trigger.
user_invocable: true
---

# /Ask — Universal Asking Subroutine

`/ask` is how any agent asks the user one or more questions. Parent skills (`/feature`, `/code`, `/groom`, `/triage`, `/crank`, ...) invoke `/ask` via the Skill tool whenever they need user input. The agent never writes question batches to docs by hand — it routes them through this skill so formatting, numbering, surface routing, glance, and global-page maintenance all happen the same way every time.

The reliability gain comes for free from Claude Code's skill-loading mechanic: when a parent invokes `/ask`, this runbook executes, including the glance step. That's the fix for the original "agents forget to glance" pain that motivated F10.


## When to invoke

Invoke `/ask` whenever you have **one or more decisions** that need the user. There is no minimum question count — even a single decision routes through `/ask` so the surface (doc or triage), the global page, and the glance are handled uniformly.

The scale-up — batching, numbering, recommendation labels — is what makes `/ask` *better* at large question counts; but the *pattern* is the same for one question or twenty.

Triggers (non-exhaustive):
- A `/feature` lifecycle phase has open questions.
- `/code plan` or `/code architect` is in a design loop with trade-offs to settle.
- `/groom` or `/triage` surfaces a backlog item that needs a user decision before becoming Ready.
- `/crank` hits a blocker that needs disambiguation.
- A spec, PRD, UX design, or system design is being refined.
- An agent is about to ask any question — route through `/ask`.


## Two question shapes

Every question lands on one of two surfaces. The parent skill (or the user invoking `/ask` directly) tells `/ask` which.

| Shape | Flag | Surface | When |
|---|---|---|---|
| **Document-attached** | `--doc <path>` | The doc's `## Open Questions` H2 below the H1 | Question is about a specific feature doc / PRD / design doc / spec. |
| **À la carte** | (default — no flag) | The project's `{NAME} Triage.md` § `## À la carte` H2 | Question is anchor-level, cross-cutting, agent-raised, or planning-time — doesn't belong to one document. |

If the parent skill is ambiguous about which shape applies, default to **à la carte** — the question still gets surfaced, just at the anchor level rather than attached to a specific doc.

**À la carte questions use `Q<n>` numbering, not `A<n>`** — same `Q<n>` prefix as feature-attached Qs, scoped per container (each feature doc has its own Q-namespace; each anchor's à la carte block has its own Q-namespace). When referenced in conversation: feature-scoped → `F10 Q3`; à la carte → `{NAME} Q3` (e.g., "SKA Q3").


## Invocation

```
/ask [--doc <path>] <question1> [<question2> ...]
```

- `--doc <path>` → document-attached mode; questions go in that doc's `## Open Questions` block (created if absent).
- No flag → à la carte mode; questions go in the anchor's `{NAME} Triage.md` under `## À la carte`.
- Multiple positional questions → batched per § Intake — number them all in one pass, never trickle.

**Slash-only invocation.** Unlike `crank`, `groom`, `triage`, etc., the spoken word "ask" is **not** a DMUX prefix-trigger — it's too common in everyday speech. Invoke via `/ask` only.


## Runbook

### 1. Number the questions

Every question gets a unique `Q<n>` prefix — `Q1`, `Q2`, ..., `Qn` — assigned in the order you'll present them.

**Numbering policy** — lowest unused integer in the **target file**:
- For `--doc` mode: scan the target doc's `## Open Questions` H2 (and the `### Resolved` sub-section, plus any bottom `## Resolved` H2) for existing `Q<n>` markers. Pick the lowest unused integer.
- For à la carte mode: scan the anchor's `{NAME} Triage.md § ## À la carte` block for existing `Q<n>` markers. Pick the lowest unused integer. (À la carte uses `Q<n>` — same prefix as feature-attached Qs, in its own scoped namespace.)

**Q-numbers are stable references.** Once assigned, never renumber, even when questions get resolved out of order. Skipped numbers are fine. Same soft policy as backlog F-numbers — see [[CAB Backlog]] § Numbering policy.

### 2. Format each question

Every question has the same shape so the user can scan many at once and rubber-stamp the high-confidence ones.

**Layout:**

1. **Question header** — one line: `- **Q<n> — Short question name** — context, why we're asking, what's at stake.`
2. **Options as sub-bullets** when there are more than one. Inline-prose-with-A-B-C is hard to skim.
3. **Recommendation as the final sub-bullet**, prefixed with the bolded word `**Recommendation:**` (the eye-anchor) followed by the strength label and the answer.

**Recommendation strength — three labels, always explicit:**

| Label | When to use | Format |
|---|---|---|
| **Strong** | High confidence; clear reason; alternatives have no meaningful trade-off. User can rubber-stamp. | `- **Recommendation:** Strong (B). <optional one-line reason>.` |
| **Lean** | Moderate confidence; one option seems better but alternatives are defensible. User should consider. | `- **Recommendation:** Lean (B). <one-line reason>.` |
| **None** | Genuine uncertainty — user-preference-dependent or insufficient context. | `- **Recommendation:** None. <one-line reason: why uncertain>.` |

**Pick exactly one label.** Don't fudge with "lean strongly" or "weak recommendation" — those collapse to Lean. The bolded **Recommendation:** prefix is the eye-anchor; the user scans a column of bold "Recommendation:" labels and zips through strength labels to see which need thought (Lean / None) and which can be accepted at a glance (Strong).

**Spacing — tight inside, loose between:**

- **No blank line** between the last option sub-bullet and the recommendation sub-bullet — they belong to the same question.
- **One blank line after the recommendation**, separating each question from the next.

**Example:**

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

**Why this matters.** Without the explicit strength label, every question reads as if it deserves equal scrutiny — the user has to re-evaluate even the obvious calls. With the bolded **Recommendation:** anchor + label, **Strong** picks become rubber-stamps, **Lean** picks get a quick read, and **None** picks get the thinking time they need. The user's attention budget is the constraint; the format spends it where it matters.

### 3. Write to the target surface

#### Document-attached mode (`--doc <path>`)

Append the formatted questions to the doc's `## Open Questions` H2. The H2 sits **directly below** the H1 of the doc.

**If the H2 doesn't exist yet** (Phase 3 transition or first-ever question on this doc): create it directly below the H1, **above** any other content. The shape is:

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

The `### Resolved` H3 inside `## Open Questions` is a temporary holding pen — resolutions accumulate there until **all** questions on this doc are resolved (Phase 2 transition; see § Phase lifecycle).

#### À la carte mode (default)

Append the formatted questions to the anchor's triage file under `## À la carte`. The triage file is `{NAME} Triage.md` in `{NAME} Docs/{NAME} Plan/`.

**À la carte numbering uses `Q<n>`** — Q1, Q2, Q3, ... — same prefix as feature-attached Qs, scoped to this à la carte block (each anchor has its own à la carte Q-namespace, independent of any feature doc's Q-namespace). Same lowest-unused-integer policy. Q-numbers are stable references; never renumber.

If the triage file's `## À la carte` H2 doesn't exist yet, create it.

```markdown
## À la carte

- **Q1 — {short name}** — {context}.
  - **Recommendation:** Lean (B). {reason}.

- **Q2 — {short name}** — {context}.
  - **Recommendation:** Strong (A). {reason}.
```

### 4. Regenerate `{NAME} Triage.md`

After writing the new question(s), regenerate the anchor's local triage file from scratch — same logic `/triage` runs. This keeps the local triage consistent with the just-added Q. See `triage/SKILL.md` § Runbook for the full regen logic. Summary:

- Walk `{NAME} Backlog.md`. Filter to items with `[Questions]` or `[Verify]` brackets.
- Render the H1 banner with per-bucket counts.
- Render `## À la carte` H2 with the (just-updated) à la carte Q-block.
- Render `## Now` / `## Next` / `## Later` H2s with filtered backlog rows.
- Write the file destructively.

This replaces today's `## À la carte` H2 (which used `A<n>`) with `Q<n>` numbering. Per F25 Q5 resolution.

### 5. Regenerate the anchor's H2 in `~/ob/kmr/Q.md`

`Q.md` is the **vault-level Agent Status dashboard**. Every active anchor (questions OR ready items) has an H2 entry. Per F25:

**On every `/ask` invocation, regenerate the anchor's H2 in `Q.md`:**

1. Determine the anchor (`{NAME}`) from `--doc <path>` or the working directory (walk up to `.anchor`).
2. Count two things for this anchor:
   - **Pending questions**: sum of pending `Q<n>` across all feature docs in `{NAME} Docs/{NAME} Plan/{NAME} Features/` plus pending `Q<n>` in `{NAME} Triage.md § ## À la carte`.
   - **Ready items**: count of bullets under `## Ready` in `{NAME} Backlog.md`.
3. **If pending = 0 AND ready = 0**: remove any existing `## QUESTIONS — {NAME}` or `## READY — {NAME}` H2 from `Q.md`. Done.
4. **Otherwise**: build the new H2 entry:
   - Pick the prefix: `QUESTIONS` if pending ≥ 1, else `READY`.
   - H2 line: `## {PREFIX} — {NAME} — [[{NAME}]] · [[{NAME} Triage]] — {summary tail}`
     - Summary tail: `{N} pending` for QUESTIONS prefix; or `{N} pending · {M} ready` if both > 0; or `{M} ready` for READY prefix.
   - **Body** — populated only when prefix is QUESTIONS:
     - **À la carte questions first** (bare bullets directly under H2, no H3 wrapper) — per F25 Q8.
     - Then `### F<n> — {Feature Name}` H3 per feature with pending Qs (F-number ascending), each with its bullet list of pending Qs.
     - **Bullet format** (per F25 Q3): condensed inline — `- **Q<n> — Short name** — context. **Recommendation:** Strength (Letter).`
     - **Body cap (per F25 Q1): 12-line soft cap.** If the H2 body would exceed 12 lines, truncate and append `- … and {K} more in [[{NAME} Triage]]` as the final bullet.
   - For READY prefix, the body is empty — the H2 line itself is the entire entry.
5. **Remove any existing `## QUESTIONS — {NAME}` or `## READY — {NAME}` H2** from `Q.md` (de-dupe, since prefix may have flipped).
6. **Insert the new H2 at the top of the body** — immediately after the H1 banner, before any other anchor H2. Always move-to-front, regardless of whether the body changed (per F25 Q6).
7. Refresh the H1 banner: `# Agent Status   -   Questions: N    Ready: M` where:
   - `N` = number of `## QUESTIONS — *` H2 sections in the file.
   - `M` = number of `## READY — *` H2 sections in the file.

**Format of the global page:**

```markdown
---
description: Agent Status — every anchor with active questions or ready work, surfaced in one keystroke
---


# Agent Status   -   Questions: 2    Ready: 1


## QUESTIONS — SKA — [[SKA]] · [[SKA Triage]] — 4 pending

- **Q1 — short à la carte question** — context. **Recommendation:** Lean (A).

### F25 — Q.md as Agent Status Dashboard

- **Q1 — body cap question** — context. **Recommendation:** Lean (A).
- **Q3 — bullet content** — context. **Recommendation:** Lean (B).


## QUESTIONS — HA — [[HA]] · [[HA Triage]] — 2 pending · 1 ready

### F8 — Some HA Feature

- **Q1 — short question name** — context. **Recommendation:** Lean (B).
- **Q2 — another question** — context. **Recommendation:** Strong (A).


## READY — MUX — [[MUX]] · [[MUX Triage]] — 3 ready
```

**Empty-state body.** When `Q.md` has zero anchors active:

```markdown
# Agent Status   -   Questions: 0    Ready: 0


_No active agents. This page is maintained by `/ask` and `/triage` (and `/crank` on its no-action path). When any agent in any anchor has pending questions or ready backlog items, an H2 entry surfaces here; once both are zero, the anchor disappears._
```

**The page is agent-owned.** `/ask` and `/triage` rewrite the relevant H2 on every invocation. The user does not edit `Q.md` directly.

### 6. Glance the file (active mode only)

After writing the question(s) and regenerating the local + global pages, `open <target>` so the file appears on the user's side and they can answer.

**Glance only when both conditions hold:**
1. The edit added or modified a pending question, AND
2. You're in **active mode** — the user is engaging with this work right now (they expect to answer in this turn or the next).

In **parking mode**, skip the glance — the file gets the questions but doesn't open at the user. The global page still updates either way (parked questions still need to surface eventually; the user finds them via the keyboard shortcut to `Q.md` when they choose to engage).

See § Active vs Parking mode for the full disambiguation. **Default when ambiguous: parking.**

**Never glance when the edit only resolved questions** (moved one or more from pending to `### Resolved`, or migrated the H2 to the bottom `## Resolved`). Resolution doesn't surface new state; pending questions were already visible.

### 7. Print one-line summary

After writing and (maybe) glancing, print a single-line summary to chat:

```
/ask — added N Qs to <target>; refreshed {NAME} Triage and Q.md.
```

`<target>` is the doc path or `<NAME> à la carte`.


## Active vs Parking mode

Questions get added in two very different contexts. Treat them differently.

**Active mode** — the user is engaging with the work *right now*. They asked you to design / discuss / debate / plan something, and they expect to answer questions in this turn or the next. The glance is meaningful: it tells them *"I just added something you need to look at."*

Signals that you're in active mode:
- User said: "let's design X" / "let's discuss X" / "what do you think about Y" / "let's work on this" / "tell me about X"
- User invoked `/feature` *without* saying "for later"
- User is in the middle of answering a previous batch of questions and you're adding follow-ons

**Parking mode** — the user is filing the work for later engagement. The questions get captured so they're not lost, but the user has explicitly said they're not engaging now. The doc / triage entry surfaces later when the user opens the global page (or the user re-engages by name).

Signals that you're in parking mode:
- User said: "put it on the backlog" / "file this" / "for later" / "we'll figure that out" / "we can talk about it at that time" / "add to the icebox"
- User invoked `/feature` *and* said any of the above
- Another skill (`/groom`, `/triage`, `/crank`) is creating feature docs / batch-routing questions during a multi-item run
- User is creating a backlog stub and wants the work captured but not engaged with

**Default when ambiguous: parking.** If you can't tell whether the user wants engagement now, prefer parking — never glance, just file the questions and tell the user "filed; let me know when you want to discuss." The cost of an unwanted glance (interrupts deferred work) is higher than the cost of a missed glance (the user can re-engage by opening `Q.md`).

**Console vs. file:** it's fine to echo the new questions in the console so the user has an immediate hint, but the file is the source of truth. The user will answer from the file (or from the global page → triage → file path), not from the scrolled-away console.


## Phase lifecycle of `## Open Questions` blocks (document-attached mode)

A document with questions moves through three phases.

**Phase 1 — pending questions exist.**

```markdown
# {H1 title}

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

**Heading text and structure:**

- **Heading text is just `## Open Questions`** (no `for {descriptor}` suffix — the H1 above provides the descriptor).
- Follow-on questions (children of a pending question) become **sub-bullets** under their parent. When the parent is resolved, children either resolve with it, become independent top-level questions, or get moved to Resolved alongside the parent — agent's judgment.


## Resolution — inline, with pointer

For each answered question, write the resolution inline in this exact form, **preserving the original Q-number**:

```
**Q3** — **Resolution:** <one sentence of what was decided>. Incorporated into <design section / plan section / code area / conversation>.
```

The Q-number stays the same when a question moves from pending to Resolved — it's a stable reference so the user (or a later reader) can trace history.

The **Incorporated into** pointer makes resolutions auditable — a reader can trace decision → design → code. When no doc exists yet, the pointer may target the conversation ("Incorporated into the design we just agreed on").

After resolution, **`/ask` itself doesn't usually run** — the parent skill that invoked `/ask` (or the user) writes the resolution. But the global-page count maintenance (step 4 above) is the responsibility of whichever agent updates the question state. If the resolving agent is acting on the user's answer and isn't already inside `/ask`, it should still recompute the anchor's active-Q count and update `Q.md` if that count crossed 0.


## Glance summary table

(Assumes Active mode where applicable; Parking mode never glances.)

| Edit type | Glance (Active mode)? | Glance (Parking mode)? |
|---|---|---|
| Added a new pending `Q{n}` | **Yes** | **No** |
| Rewrote a pending question's wording | **Yes** | **No** |
| Added a sub-bullet under a pending parent | **Yes** | **No** |
| Resolved one or more questions (others still pending) | **No** | **No** |
| Resolved the last pending question (Phase 1 → Phase 2 transition) | **No** | **No** |
| No-op edit (formatting only) | **No** | **No** |


## Anti-patterns

- Asking one question, getting the answer, then asking the next. **Batch instead.** Front-load every question you can foresee.
- Resolving a question in prose ("we'll do X") without the `**Q<n>** — **Resolution:** ...` form. **The format makes it auditable.**
- Deleting a resolved question. **Move it to Resolved; the history matters.**
- Adding a new question after "ready." **Flag it as a miss; don't sneak it in.** Say "I should have asked Q<n> earlier, surfacing now."
- Renumbering questions to "fill gaps." **Q-numbers are stable references** — skipped numbers are fine.
- Editing `Q.md` by hand to reflect an anchor's state. **The page is agent-owned**; the next `/ask` will overwrite the body. Update the underlying triage file or feature doc instead.


## Cross-references

- `[[CAB Triage]]` — sibling skill that surfaces (reads) the questions `/ask` writes. `/ask` is the writer; `/triage` is the reader/router.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule for Q/A numbers.
- `~/ob/kmr/Q.md` — the global page maintained by step 4 of this runbook.
