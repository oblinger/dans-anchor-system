---
name: ask
description: Universal asking subroutine. Invoke whenever an agent has questions for the user. Routes batched, numbered, formatted questions to the right surface (a feature/PRD doc with --doc, or the project's triage file by default), maintains the global Open Questions page at ~/ob/kmr/Q.md, and (in active mode) glances the file so the user sees it. Replaces the old `ask-questions` discipline.
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
| **À la carte** | (default — no flag) | The project's `{NAME} Triage.md` § `## À la carte` H2 | Question is cross-cutting, agent-raised, or planning-time — doesn't belong to one document. |

If the parent skill is ambiguous about which shape applies, default to **à la carte** — the question still gets surfaced, just at the project level rather than attached to a specific doc.


## Invocation

```
/ask [--doc <path>] <question1> [<question2> ...]
```

- `--doc <path>` → document-attached mode; questions go in that doc's `## Open Questions` block (created if absent).
- No flag → à la carte mode; questions go in the project's triage file under `## À la carte`.
- Multiple positional questions → batched per § Intake — number them all in one pass, never trickle.


## Runbook

### 1. Number the questions

Every question gets a unique `Q<n>` prefix — `Q1`, `Q2`, ..., `Qn` — assigned in the order you'll present them.

**Numbering policy** — lowest unused integer in the **target file**:
- For `--doc` mode: scan the target doc's `## Open Questions` H2 (and the `### Resolved` sub-section, plus any bottom `## Resolved` H2) for existing `Q<n>` markers. Pick the lowest unused integer.
- For à la carte mode: the triage file's à la carte block uses an `A<n>` series instead of `Q<n>` (see § À la carte numbering below).

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

Append the formatted questions to the project's triage file under `## À la carte`. The triage file is `{NAME} Triage.md` in the project's `Plan/` folder (mirroring `{NAME} Backlog.md`).

**À la carte numbering uses `A<n>` instead of `Q<n>`** — A1, A2, A3, ... — to disambiguate from doc-scoped questions. Same lowest-unused-integer policy. A-numbers are stable references too; never renumber.

If the triage file's `## À la carte` H2 doesn't exist yet, create it. The triage file's overall structure is owned by `/triage`; `/ask` only touches the à la carte H2.

```markdown
## À la carte

- **A1 — {short name}** — {context}.
  - **Recommendation:** Lean (B). {reason}.

- **A2 — {short name}** — {context}.
  - **Recommendation:** Strong (A). {reason}.
```

### 4. Update the global Open Questions page

The global page lives at `~/ob/kmr/Q.md`. It aggregates **every anchor in the vault** that has active questions waiting on the user, plus any à la carte questions that aren't anchor-scoped.

**On every `/ask` invocation:**

1. Determine the project's anchor (the `{NAME}` of the triage file, derivable from the working directory or `--doc <path>`).
2. Count the project's currently-active questions: pending `Q<n>` entries across all feature/PRD docs in this anchor + pending `A<n>` entries in `{NAME} Triage.md`.
3. **If the count went 0 → ≥1**: add a row to the `## Anchors` section of `Q.md` linking the project's triage file (`[[{NAME} Triage]]`) and showing the count.
4. **If the count stayed ≥1**: refresh that row's count.
5. **If the count dropped to 0** (last question resolved on this `/ask` call): remove the row from `## Anchors`.
6. Refresh the H1 banner: `# Open Questions   -   Anchors waiting: N    À la carte: M` where `N` is the number of rows in `## Anchors` and `M` is the number of à la carte questions held directly in `Q.md` itself (see § Vault-scoped à la carte below).

**Format of the global page:**

```markdown
---
description: Global Open Questions — every anchor with active questions waiting on user input
---


# Open Questions   -   Anchors waiting: N    À la carte: M


## Anchors

- [[SKA Triage]] — 4 Qs (F10: 3, F14: 1)
- [[HA Triage]] — 5 Qs
- [[MUX Triage]] — 2 Qs


## À la carte

- **A1 — {short name}** — {context}. **Recommendation:** Lean (B). {reason}.
```

The per-anchor row may include a per-feature breakdown when useful (e.g., `(F10: 3, F14: 1)`); use this when there are 2+ docs with pending Qs in the anchor.

**Vault-scoped à la carte questions** (questions with no anchor — global cross-cutting decisions): these go in `Q.md`'s own `## À la carte` H2 directly. They're a small fraction of cases; most à la carte questions have an anchor. Numbering uses the same `A<n>` series, scoped to `Q.md`.

**Empty-state body.** When `Q.md` has zero anchors and zero à la carte questions, the body becomes:

```markdown
_Nothing currently waiting on you. This page is maintained by the `/ask` skill (F10). When any agent in any anchor parks questions for you, this page surfaces them; once they're answered, the anchor disappears from here._


## Anchors

_(none active)_


## À la carte

_(none active)_
```

**The page is agent-owned.** `/ask` rewrites the body on every invocation. The user does not edit `Q.md` directly. To preserve user edits would require a "user-owned area" boundary; the page is intentionally generated, like `{NAME} Triage.md`.

### 5. Glance the file (active mode only)

After writing the question(s), `open <target>` so the file appears on the user's side and they can answer.

**Glance only when both conditions hold:**
1. The edit added or modified a pending question, AND
2. You're in **active mode** — the user is engaging with this work right now (they expect to answer in this turn or the next).

In **parking mode**, skip the glance — the file gets the questions but doesn't open at the user. The global page still updates either way (parked questions still need to surface eventually; the user finds them via the keyboard shortcut to `Q.md` when they choose to engage).

See § Active vs Parking mode for the full disambiguation. **Default when ambiguous: parking.**

**Never glance when the edit only resolved questions** (moved one or more from pending to `### Resolved`, or migrated the H2 to the bottom `## Resolved`). Resolution doesn't surface new state; pending questions were already visible.

### 6. Print one-line summary

After writing and (maybe) glancing, print a single-line summary to chat:

```
/ask — added N Qs to <target>. Global page refreshed.
```

`<target>` is the doc path or `<NAME> à la carte`. Mention the global page only if it changed (added/removed an anchor row, or wrote a new à la carte entry).


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

For each answered question, write the resolution inline in this exact form, **preserving the original Q-number** (or A-number for à la carte):

```
**Q3** — **Resolution:** <one sentence of what was decided>. Incorporated into <design section / plan section / code area / conversation>.
```

The number stays the same when a question moves from pending to Resolved — it's a stable reference so the user (or a later reader) can trace history.

The **Incorporated into** pointer makes resolutions auditable — a reader can trace decision → design → code. When no doc exists yet, the pointer may target the conversation ("Incorporated into the design we just agreed on").

After resolution, **`/ask` itself doesn't usually run** — the parent skill that invoked `/ask` (or the user) writes the resolution. But the global-page count maintenance (step 4 above) is the responsibility of whichever agent updates the question state. If the resolving agent is acting on the user's answer and isn't already inside `/ask`, it should still recompute the anchor's active-Q count and update `Q.md` if that count crossed 0.


## Glance summary table

(Assumes Active mode where applicable; Parking mode never glances.)

| Edit type | Glance (Active mode)? | Glance (Parking mode)? |
|---|---|---|
| Added a new pending `Q{n}` / `A{n}` | **Yes** | **No** |
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
