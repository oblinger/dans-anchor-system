---
name: ask
description: Universal asking skill, two modes. Bare `/ask` (no arguments — primary mode) drains an anchor: agent self-resolves what it can (drive-mode-calibrated), writes a three-section `{NAME} ask.md` (Agent Resolutions / User Verifications / Questions), glances it, surfaces 1–3 items in console, iterates idempotently. Parented `/ask` (with `--doc` and/or explicit questions — secondary mode) parks individual questions on a feature doc or the anchor's à la carte facet `{NAME} Questions.md`. Both modes regenerate `{NAME} Triage.md` and the anchor's section in `~/ob/kmr/Q.md`. Slash-only — "ask" is too common a spoken word to be a DMUX prefix-trigger.
user_invocable: true
---

# /Ask — Universal Asking Skill

`/ask` has **two modes**, distinguished by whether arguments are present.

| Mode | Invocation | What it does |
|---|---|---|
| **Bare** (primary) | `/ask` (no arguments) | User-invoked from within an anchor. Drains the anchor's open `[Verify]` and `[Questions]` items: self-resolves what it can (drive-mode-calibrated), writes the three-section `{NAME} ask.md`, glances it, surfaces 1–3 items in console, iterates. |
| **Parented** (secondary) | `/ask [--doc <path>] <q1> [<q2>...]` | Called from another skill's runbook (`/feature`, `/code plan`, `/groom`, `/crank`). Routes batched, numbered, formatted questions to a feature doc's `## Open Questions` block or the anchor's à la carte facet. |

Both modes regenerate `{NAME} Triage.md` and the anchor's section in `~/ob/kmr/Q.md`. Both follow the same recommendation-strength format and Phase 1/2/3 lifecycle for `## Open Questions` blocks. The reliability gain comes for free from Claude Code's skill-loading mechanic: when `/ask` is invoked, this runbook executes — including the glance step. That's the fix for the original "agents forget to glance" pain that motivated F10.


## When to invoke

**Bare `/ask`** — when the user types `/ask` (no arguments) from within an anchor. This is the user saying: *"ask me everything you need to ask me to make progress on this anchor's open work, minimizing round-trips."* See § Bare invocation runbook.

**Parented `/ask`** — whenever a parent skill has **one or more decisions** that need the user. There is no minimum question count — even a single decision routes through `/ask` so the surface (doc or triage), the global page, and the glance are handled uniformly. The scale-up (batching, numbering, recommendation labels) is what makes `/ask` *better* at large question counts; but the *pattern* is the same for one question or twenty.

Parented triggers (non-exhaustive):
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
| **À la carte** | (default — no flag) | The anchor's `{NAME} Questions.md` facet, `## Open Questions` H2 | Question is anchor-level, cross-cutting, agent-raised, or planning-time — doesn't belong to one document. |

If the parent skill is ambiguous about which shape applies, default to **à la carte** — the question still gets surfaced, just at the anchor level rather than attached to a specific doc.

Per F28, à la carte Qs live in their own per-anchor facet file `{NAME} Questions.md` (spec: `[[CAB Questions]]`) — not inside `{NAME} Triage.md` anymore. The Triage file just carries one bullet line under its H1 (`- **[N Questions]**  [[{NAME} Questions]]`) when there are pending à la carte Qs.

**À la carte questions use `Q<n>` numbering, not `A<n>`** — same `Q<n>` prefix as feature-attached Qs, scoped per container (each feature doc has its own Q-namespace; each anchor's `{NAME} Questions.md` has its own Q-namespace). When referenced in conversation: feature-scoped → `F010 Q3`; à la carte → `{NAME} Q3` (e.g., "SKA Q3").


## Invocation

```
/ask                                  # bare mode — drain the current anchor
/ask <SLUG>                           # bare mode — drain a named anchor (cross-anchor)
/ask [--doc <path>] <q1> [<q2> ...]   # parented mode — park questions
```

- **No arguments** → bare mode; runs the § Bare invocation runbook against the **current anchor** (detected by walking up from cwd to the nearest `.anchor`).
- **Single positional argument matching an anchor slug** (e.g. `/ask SKA`, `/ask MUX`) → bare mode against the **named anchor**. The current agent does the work but reads the target anchor's Triage / Questions / feature docs. **Uncommon** — the local agent for that anchor usually has more context and will do a better self-resolution pass; use cross-anchor only when you specifically want the current agent to handle it.
- `--doc <path>` → parented document-attached mode; questions go in that doc's `## Open Questions` block (created if absent).
- No flag + positional `<question>` arguments → parented à la carte mode; questions go in the anchor's `{NAME} Questions.md` facet's `## Open Questions` block (created if absent).
- Multiple positional questions → batched — number them all in one pass, never trickle.

**Disambiguation: anchor slug vs. question text.** A single positional argument is treated as an anchor slug if all three hold:
1. It's one token (no spaces).
2. It matches the shape `[A-Z][A-Za-z0-9]+` (starts with a capital, alphanumeric).
3. It resolves to a known anchor (walk the vault's `slug-index`, or check that `<SLUG>/.anchor` exists, or that `<SLUG> Triage.md` / `<SLUG> Backlog.md` exists somewhere reachable).

If any check fails, treat the argument as à la carte question text and run the parented runbook. Multiple positional arguments are always parented (no anchor slug has spaces).

**Slash-only invocation.** Unlike `crank`, `groom`, `triage`, etc., the spoken word "ask" is **not** a DMUX prefix-trigger — it's too common in everyday speech. Invoke via `/ask` only.


## Bare invocation runbook

Bare `/ask` (no arguments) drains the anchor's open `[Verify]` and `[Questions]` items in a way that minimizes round-trips with the user. The agent does the work that *can* be done without the user, then surfaces only the residue.

### 1. Identify the anchor and survey open work

**Default (no argument):** walk up from the working directory to the nearest `.anchor` to determine `{NAME}`. This is the common case — the agent's own anchor.

**Cross-anchor (single slug argument):** if invoked as `/ask <SLUG>` and the slug resolves to a known anchor (per the § Invocation disambiguation rules), set `{NAME}` = `<SLUG>` and read that anchor's files instead of the current one. The current agent does the work using the target anchor's Triage / Questions / feature docs.

Then read `{NAME} Triage.md` and enumerate every item bracketed `**[N Questions]**` or `**[Verify]**` across the **Active / Ready / Now / Next** sections. **Skip `## Later` and `## Icebox`** — bare `/ask` surfaces only items in scope for *now*. If `{NAME} Questions.md` exists, also include its pending à la carte Qs.

If the survey returns zero pending items, write a one-line summary (`/ask — nothing pending in {NAME}.`), refresh the anchor's section in `Q.md` (will likely drop it), and exit.

### 2. Reasoning pass — self-resolve what you can

For each surveyed item, attempt to resolve it autonomously. Calibrate the threshold by the active drive mode (see `[[mode]]`):

- **`[Verify]` items** — *can I verify this myself well enough that the user doesn't need to?* Run the grep / test / script / log inspection / source-dip that would settle it. If the verification mechanically passes, mark the item Done in the backlog (update its row + the feature doc's Status).
- **`[Questions]` items** — *can I confidently pick the most likely answer?* Read the feature doc's `## Open Questions` block, the surrounding code, prior similar decisions in the anchor's `## Resolved`, the user's stated preferences (memory), and the design rationale. For each Q where the answer is clear, write the inline resolution per § Resolution and update the feature doc.

**Drive-mode thresholds:**

| Drive mode | Self-resolution threshold |
|---|---|
| **Cautious** (fortify-flavored) | Self-resolve only when mechanically obvious — a test that passes, a Q whose answer is already stated in memory or prior conversation. Escalate everything else. |
| **Standard** | Self-resolve the clear ones; surface the rest. |
| **Aggressive** (crank-flavored) | Self-resolve anything plausible; let the user push back on Agent Resolutions if a call was wrong. |

The reasoning pass produces three buckets:
1. **Resolved by agent** — verifies the agent ran, questions the agent answered.
2. **User verifications** — verifies the agent can't run alone (needs human eyes, judgment, prod-system check).
3. **User questions** — questions the agent can't confidently pick.

### 3. Write `{NAME} ask.md`

Destructively (re)generate `{NAME} Docs/{NAME} Plan/{NAME} ask.md`. **Three sections in fixed order.** Frontmatter `description: bare `/ask` snapshot — agent resolutions and what the user still needs to verify or answer.`

```markdown
---
description: bare `/ask` snapshot — agent resolutions and what the user still needs to verify or answer.
---


# [[{NAME}]] ask

## Agent Resolutions

- [[F23 — Some Feature]] **[Verify→Done]** — ran the integration test; output matched expected. Marked Done in backlog.
- [[F24 — Other Feature]] **Q3** — chose default path; user prefers fewer flags by default.

## User Verifications

- [[F26 — Manual UX flow]] **[Verify]** — needs human eyes on the UI; can't be automated. Run the app, click through, confirm the panel renders.

## Questions

- [[F28 — Naming]] — 3 Qs (Q1, Q2, Q5). Naming-convention fork; see the feature doc.
- [[F29 — Retry policy]] **Q1** — max-retries cap: 3, 5, or unbounded?
- [[{NAME} Q3]] — the à la carte slug-renaming question.
```

Rules:
- **Agent Resolutions section first** — the user's first action is to review and challenge wrong calls.
- **Order each section** by backlog source order (mirrors Triage).
- **Condense large Q batches** — when a single feature has many Qs, list the feature with a count rather than every Q inline (`- [[F28]] — 3 Qs (Q1, Q2, Q5).`).
- **Soft cap ≈ 10 items** in the User Verifications + Questions sections combined. If the queue is longer, list the top 10 in priority order; the user re-invokes `/ask` to surface the next batch.
- **Omit empty sections** entirely (don't leave `## Agent Resolutions` with no body — drop the H2).

### 4. Regenerate `{NAME} Triage.md` and the anchor's section in `~/ob/kmr/Q.md`

Same regeneration as § Parented runbook steps 4–5. The agent's resolutions in step 2 may have moved items in the backlog (Verify→Done, pending Q→Resolved), so the regenerated Triage reflects fresh state.

### 5. Glance `{NAME} ask.md`

Always glance — bare `/ask` is the user explicitly engaging; always active mode. The user opens the doc, reads Agent Resolutions first, and is ready to push back or move on.

### 6. Console interleave — present 1–3 items

In chat, present **1–3 items** from the top of the User Verifications and Questions sections. Format each item with its short name + the action needed:

```
**Up next** (1–3 of N pending):

1. **[Verify F26]** — Open the app and confirm the panel renders on Cmd+Shift+P.
2. **F29 Q1** — max-retries cap: 3, 5, or unbounded? Recommendation: Lean (5).
3. **{NAME} Q3** — rename the slug from `foo` to `bar`? Recommendation: None.
```

**Cap of 3** — more would overflow the user's working memory in a single chat round. The user has the full queue in the doc.

### 7. Process user response

Two response shapes:

- **Pushback on Agent Resolutions** — "Roll back F24 Q3" / "Undo the resolution on F23" → roll back the change (re-open the Q or set Verify back), move the item into User Verifications or Questions, regenerate `{NAME} ask.md`.
- **Answers to console questions** — "F29 Q1: 5" / "verified F26" / "{NAME} Q3: yes" → apply the resolution per § Resolution to the underlying feature doc / backlog, regenerate `{NAME} ask.md`.

Then surface the next 1–3 items in console. Repeat until the doc reports no pending items (User Verifications + Questions both empty) or the user disengages.

### 8. Idempotency

Bare `/ask` is **idempotent**. State lives in `{NAME} ask.md`, the feature docs, and the backlog — never in invocation history. Re-invoking `/ask` re-runs the reasoning pass against the current backlog state. Resolutions the user already accepted stay resolved; new ones accumulate; the next ~10 items surface.


## Parented runbook

### 1. Number the questions

Every question gets a unique `Q<n>` prefix — `Q1`, `Q2`, ..., `Qn` — assigned in the order you'll present them.

**Numbering policy** — lowest unused integer in the **target file**:
- For `--doc` mode: scan the target doc's `## Open Questions` H2 (and the `### Resolved` sub-section, plus any bottom `## Resolved` H2) for existing `Q<n>` markers. Pick the lowest unused integer.
- For à la carte mode: scan the anchor's `{NAME} Questions.md` for existing `Q<n>` markers across `## Open Questions` (pending + `### Resolved`) and any bottom `## Resolved` H2. Pick the lowest unused integer. (À la carte uses `Q<n>` — same prefix as feature-attached Qs, in its own scoped namespace.)

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

Append the formatted questions to the anchor's per-anchor questions facet at `{NAME} Docs/{NAME} Plan/{NAME} Questions.md`, inside its `## Open Questions` H2 (per `[[CAB Questions]]`). Format is identical to a feature doc's `## Open Questions` block: pending Qs as top-level bullets; resolutions accumulate in a `### Resolved` H3 holding pen until all pending Qs resolve, then migrate to a bottom `## Resolved` H2 (Phase 1 / Phase 2 / Phase 3 lifecycle, identical to feature docs).

**À la carte numbering uses `Q<n>`** — Q1, Q2, Q3, ... — same prefix as feature-attached Qs, scoped to this anchor's `{NAME} Questions.md` (each anchor has its own à la carte Q-namespace, independent of any feature doc's Q-namespace). Same lowest-unused-integer policy. Q-numbers are stable references; never renumber.

**Create the file if it doesn't exist.** Frontmatter `description: anchor-level à la carte questions (agent-owned)`, then H1 `# [[{NAME}]] Questions`, then `## Open Questions`. See `[[CAB Questions]]` for the full spec.

```markdown
---
description: anchor-level à la carte questions (agent-owned)
---


# [[{NAME}]] Questions

## Open Questions

- **Q1 — {short name}** — {context}.
  - **Recommendation:** Lean (B). {reason}.

- **Q2 — {short name}** — {context}.
  - **Recommendation:** Strong (A). {reason}.
```

**Legacy migration**: if the anchor's `{NAME} Triage.md` still has a `## À la carte` H2 (pre-F28), move that content into `{NAME} Questions.md` § `## Open Questions` (preserving Q-numbers), then strip the H2 from Triage. The next regeneration of `{NAME} Triage.md` (in step 4) will produce the new format with the bullet line under H1.

### 4. Regenerate `{NAME} Triage.md`

After writing the new question(s), regenerate the anchor's local triage file from scratch — same logic `/triage` runs. This keeps the local triage consistent with the just-added Q. See `triage/SKILL.md` § Runbook for the full regen logic. Summary (per F28):

- Walk `{NAME} Backlog.md`. Compute the H1 banner counts (Questions / Verify | Active / Ready | Now / Next / Later / Icebox) and the anchor TAG (cascading rule: U / A / U+A / G / ? / `[]`).
- Render the H1 banner: `# [<TAG>]  [[{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N`.
- If `{NAME} Questions.md` has any pending Qs, render the bullet line directly under the H1: `- **[N Questions]**  [[{NAME} Questions]]`.
- Render `## Active`, `## Ready`, `## Now`, `## Next` H2s (in that order), each with one bullet per item in source order from the backlog. Bracket forms: `**[Active]**` / `**[Ready]**` / `**[N Ready]**` / `**[Verify]**` / `**[N Questions]**`. Omit any H2 with zero items.
- **No blank lines in the body.** No `## À la carte` H2 (the bullet line under H1 replaces it). No items from `## Later` or `## Icebox` in the body.
- Write the file destructively.

### 5. Regenerate the anchor's section in `~/ob/kmr/Q.md`

`Q.md` is the **vault-level Agent Status dashboard**. Every anchor with TAG ≠ `[]` has a per-anchor section. Per F28 (format updated from F25):

**On every `/ask` invocation, regenerate the anchor's section in `Q.md`:**

1. Determine the anchor (`{NAME}`) from `--doc <path>` or the working directory (walk up to `.anchor`).
2. Compute the same H1 banner as the just-generated `{NAME} Triage.md` — same TAG, same counts, same spacing — but with the slug as a wiki-link to the Triage file via `[[{NAME} Triage|{NAME}]]` syntax (renders as the slug, links to Triage):
   ```
   # [<TAG>]  [[{NAME} Triage|{NAME}]] Triage  -  Questions N    Verify N   |   Active N    Ready N   |   Now N    Next N    Later N    Icebox N
   ```
3. **If TAG is `[]`** (no items anywhere): remove any existing per-anchor section for `{NAME}` from `Q.md`. Done.
4. **Otherwise**: render the per-anchor section as the **identical body** to the just-generated `{NAME} Triage.md` (per F028 Q3 — full body always):
   - The H1-equivalent line above (with the wiki-link slug-prefix).
   - The à la carte bullet line (`- **[N Questions]** [[{NAME} Questions]]`) if any pending à la carte Qs.
   - `## Active` / `## Ready` / `## Now` / `## Next` H2s with their bullets, in source order from the backlog. (These render at H2 inside Q.md since each per-anchor section opens at H1 level.)
   - **No blank lines in the body** — same density as the Triage file.
5. **Remove any existing per-anchor section for `{NAME}`** from `Q.md` (de-dupe).
6. **Insert the new section at the top of the body** — immediately after the H1 banner, before any other anchor section. Always move-to-front, regardless of whether the body changed (per F025 Q6).
7. Refresh the H1 banner: `# Agent Status   -   Questions: N    Ready: M` where:
   - `N` = number of per-anchor sections whose TAG is `[U]` or `[U+A]` (anchors needing user attention).
   - `M` = number of per-anchor sections whose TAG is `[A]` or `[U+A]` (anchors with agent-actionable work).

**Overflow rule.** If `Q.md` as a whole grows too large (soft cap ~2 screenfuls; tune in implementation), individual per-anchor sections collapse to **just the H1-equivalent line** (which contains the wiki-link to Triage). The user clicks through to the full body in the Triage file. **No partial paste** — either the whole body, or just the link line.

**Format of the global page:**

```markdown
---
description: Agent Status — every anchor with active questions or ready work, surfaced in one keystroke
---


# Agent Status   -   Questions: 2    Ready: 1


# [U+A]  [[Q#CAE Triage|CAE]] Triage  -  Questions 2    Verify 1   |   Active 1    Ready 1   |   Now 2    Next 1    Later 1    Icebox 0
- **[3 Questions]**  [[CAE Questions]]
## Active
- **[Active]** [[F001 — Cron Syntax]] — Cron expressions for recurring task schedules.
## Ready
- **[Ready]** [[F003 — Retry Backoff Polish]] — Tune exponential-backoff caps after user feedback.
## Now
- **[4 Questions]** [[F002 Task Groups]] — Rendering of task groups.
- **[Verify]** [[F007 — Webhook Notifications]] — Webhook fires on task completion.
## Next
- **[5 Questions]** [[F004 Priority Levels]] — 2 pending Qs (Q1, Q3).


# [A]  [[Q#MUX Triage|MUX]] Triage  -  Questions 0    Verify 0   |   Active 0    Ready 3   |   Now 0    Next 0    Later 0    Icebox 0
## Ready
- **[Ready]** [[F001 — A]] — desc.
- **[Ready]** [[F002 — B]] — desc.
- **[Ready]** [[F003 — C]] — desc.
```

**Empty-state body.** When `Q.md` has zero anchors with TAG ≠ `[]`, the body is empty — just the H1 banner stands alone.

```markdown
# Agent Status   -   Questions: 0    Ready: 0
```

**The page is agent-owned.** `/ask` and `/triage` rewrite the relevant per-anchor section on every invocation. The user does not edit `Q.md` directly.

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

`<target>` is the doc path or `{NAME} Questions.md`.


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

- `[[CAB Triage]]` — sibling facet that surfaces (reads) the questions `/ask` writes. `/ask` is the writer; `/triage` is the reader/router.
- `[[CAB Questions]]` — sibling facet for à la carte Qs (the per-anchor file `/ask` writes to in à la carte mode).
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule for Q numbers.
- `~/ob/kmr/Q.md` — the vault-level Agent Status dashboard maintained by step 5 of this runbook.
