---
name: ask
description: Universal asking skill, two modes. Bare `/ask` (no arguments — primary mode) drains an anchor: agent self-resolves what it can (drive-mode-calibrated), writes a three-section `{NAME} ask.md` (Agent Resolutions / User Verifications / Questions), glances it, surfaces 1–3 items in console, iterates idempotently. Parented `/ask` (with `--doc` and/or explicit questions — secondary mode) parks individual questions on a feature doc or the anchor's à la carte facet `{NAME} Questions.md`. Both modes regenerate `{NAME} Triage.md` and the anchor's section in `~/ob/kmr/Q.md`. Slash-only — "ask" is too common a spoken word to be a DMUX prefix-trigger.
user_invocable: true
---

# /Ask — Universal Asking Skill

> **Consult [[technical-answer]] before responding to any user question about how a technical interface, API, signature, library, config, CLI, or wire format works.** `/ask` owns the asking side (formatting agent questions to the user); `[[technical-answer]]` owns the answering side (responding to user questions about technical interfaces). When the user is asking a tech-interface question — even if `/ask` isn't explicitly invoked — apply that discipline's rules. The pair: ask-format for asking; technical-answer for answering.

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


## Output format scales with span (per F125, 2026-06-07)

**Before authoring anything, every `/ask` invocation makes one decision: count pending Qs and the features they touch. The output format follows mechanically.**

| Q-count | Feature-count | Surface | What the agent does |
|---|---|---|---|
| **1 or 2** | any | **Inline in chat, full details** | Print the Q(s) verbatim in chat — title, body context, labeled options with bodies, recommendation with strength, load-bearing flag if any. **NO ask page, NO glance.** User answers in chat directly. |
| **≥ 3** | **1** (all in one feature) | **Glance feature + inline summary** | `open` the feature doc so the user can read full Q bodies. In chat, summarize: *"I've got N questions in F\<n\>. Q1: \<topic\>, Q2: \<topic\>, …. Load-bearing: Q\<k\>."* User clicks the glanced file for full bodies; chat carries enough context to triage which to answer first. **NO ask page** — the feature doc IS the ask surface for single-feature spans. |
| **≥ 3** | **≥ 2** (multi-feature) | **Ask page (`{NAME} ask.md`) + spotlight in chat** | Run the full bare-`/ask` § Questions surface — write `## Agent Resolutions` / `## User Verifications` / `## Questions` sections to `{NAME} ask.md`, glance it, surface 1–3 spotlight items in chat with one-line each. The page is the coherent surface across features; chat is the dispatch view. |

The rule is mechanical: count → pick row → execute. The agent does not choose the format based on judgment; **the count picks it**.

**Why "1-2 Qs inline" and not just "1 inline / 2+ surface":** for a small batch, all the information fits in chat and a glance/page would be friction. The threshold is "still readable inline" — at 3 Qs (or non-trivial 2-Q bodies), summary becomes load-bearing and the file or page is cheaper to surface.

**Failure mode this rule defeats (2026-06-07):** `/crank` exited with *"Pending input: F113 Q12, F117 (4 Qs), F118 (3 Qs)"* — a reference-only Q-list across three features. The user reasonably responded: *"I have no fucking idea what Q12 is."* Q-numbers without context are not actionable. Multi-feature spans **must** route to the ask page; single-feature ≥3 Qs **must** glance the doc; small spans **must** inline the full text. Reference lists are forbidden.

### User-story scenarios (the rule in motion)

- **Story 1 — Crank reaches no-Ready and cascades to /ask.** Crank invoked /ask after exhausting the queue. /ask counts pending Qs across all feature docs in the anchor; applies the table above.
- **Story 2 — One question pending.** /ask detects "1 Q total". Inline in chat with full details. No page, no glance.
- **Story 3 — Two questions, same or different features.** Same as one Q, both inline. Borderline; default is inline.
- **Story 4 — Three or more Qs, all in one feature.** /ask glances `F<n> — Title.md`. Chat summary: *"N Qs in F<n>. Q1: <topic>, … Load-bearing: Q<k>."* User reads bodies from the glanced file.
- **Story 5 — Multi-feature span.** /ask MUST create the ask page. Chat spotlights 1–3 items.


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

Then read `{NAME} Backlog.md` and enumerate every item bracketed `**[N Questions]**` or `**[Verify]**` across the **Active / Ready / Now / Next** sections only. **`## Later` and `## Icebox` are disregarded entirely** — regardless of bracket, regardless of why the item is there. Later means *not in scope for now*; if the user has parked something in Later, that's the user's explicit signal to not surface it. This applies *universally* to every path through bare `/ask` — survey (this step), reasoning (step 2), drain-page write (step 3), and console interleave (step 6). Even a `[Questions]` or `[Verify]` row sitting in `## Later` is out of scope; bare `/ask` does not see it, does not self-resolve it, does not list it, does not mention it. (Triage's selective-surfacing of Later items is a Triage behavior; bare `/ask` does not inherit it.) If `{NAME} Questions.md` exists, also include its pending à la carte Qs.

If the survey returns zero pending items, write a one-line summary (`/ask — nothing pending in {NAME}.`), refresh the anchor's section in `Q.md` (will likely drop it), and exit.

### 2. Reasoning pass — self-resolve what you can

For each surveyed item, attempt to resolve it autonomously. Calibrate the threshold by the active drive mode (see `[[SKA mode]]`):

- **`[Verify]` items** — read the linked feature doc's `## Success Criteria` block first (per `[[verification]]`). The tier label tells you what to do:
  - **Tier 1 (agent-immediate):** run the named check now. If it passes, mark Done via `backlog-edit.py`; do not surface to the user. If it fails, rebracket to `[Active]` and the work is not done.
  - **Tier 2 (agent-over-time):** the agent owns the deferred check (hook, schedule, watchdog). Do not surface; do not block.
  - **Tier 3 (user-passive):** add a brief reminder in the ask page of what to watch for; do not block on a user answer. Optionally ask once after enough time has passed (typically a week).
  - **Tier 4 (user-explicit):** surface as a User Verification with the specific steps from the feature doc. Even here, challenge yourself: has enough time passed that a passive signal might already have arrived? If yes, downgrade to tier 3 and drop the surfacing.

  Mark verifications Done via `backlog-edit.py` (auto-refreshes Q.md) and update the feature doc's Status field:

  ```bash
  ~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} Done <row-id> Done
  ```

  Title and body are preserved.

  **Feature docs without a `## Success Criteria` block** (predating F101) default to tier 4 surfacing for safety, but the agent should add the missing block on the next touch rather than perpetuating the bother-the-user default.

  **Batching when multiple tier-3 or tier-4 Verifies surface** (per `[[verification]]` § How to surface a Verify to the user): if several Verify rows reduce to the same user action ("did this work in normal use?", "did the bug recur?"), combine them into one targeted question with the linked feature docs listed. The user gives a single yes-or-no answer; the agent applies it to all listed rows. Never write "verify F57, F58, F59" as separate items if a single observation would resolve all three. The question itself must carry the answer-enabling context, not point at a doc to read.
- **`[Questions]` items** — *can I confidently pick the most likely answer?* Read the feature doc's `## Open Questions` block, the surrounding code, prior similar decisions in the anchor's `## Resolved`, the user's stated preferences (memory), and the design rationale. For each Q where the answer is clear, write the inline resolution per § Resolution and update the feature doc.

- **Pre-ask self-check (per F105)** — before queuing any Q for the user, run the five named patterns from `[[ask-format]]` § Pre-ask self-check: (1) aggregate across all feature docs + à la carte within this anchor — don't surface one feature's Qs in isolation when others have pending ones; (2) "continue or stop?" → continue; (3) "burn tokens for a better outcome?" → yes; (4) "how to split the work?" → agent decides, file new features `[Ready]` when independently doable; (5) "quick way or complete way?" → complete (file quick-way's complete version as `[Ready]` if doing quick first). Any Q matching one of these is auto-resolved into the relevant `## Resolved` H2 (feature doc) or `## Agent Resolutions` (this anchor's ask page), never surfaced.

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

**`## Agent Resolutions` accumulates across calls; `## User Verifications` and `## Questions` rebuild each call.** Per [[F086]]:

1. **Read the prior `{NAME} ask.md`** if present. Parse the `## Agent Resolutions` section; carry forward every entry.
2. **Live re-check each carried-forward entry** (cost gate: <100ms each). Read the underlying feature doc's `## Resolved` H2 (or backlog row state); confirm it still matches what the resolution claims. If drift detected (user edited the feature doc directly, or another agent changed it), drop that entry and flag in chat: *"Dropped carried-forward resolution for F<n> — feature doc state diverged."*
3. **Prepend this call's new resolutions** to the surviving carried-forward list (newest at top; the user sees most-recent decisions first).
4. **Rebuild `## User Verifications` and `## Questions` from scratch** based on the current survey — these always reflect the live backlog.
5. **Soft cap warning:** if accumulated `## Agent Resolutions` > 20 entries, append a chat note: *"21 unaccepted resolutions accumulated — say 'the resolutions look good' to clear, or work through them."* No hard limit; the user is in control.

Acceptance / rollback are processed in § 7, not here. Step 3's job is just to write the current accumulated state to disk.

Three sections in fixed order. Frontmatter `description: bare `/ask` snapshot — agent resolutions and what the user still needs to verify or answer.`

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

### 4. Regenerate the anchor's section in `~/ob/kmr/Q.md` — **run the script** (per F104)

Per F104 (2026-06-02) the regen is mechanical. Per-anchor `{NAME} Triage.md` files were retired in F075; Q.md sections are the only rendered form. The agent shells out:

```bash
python3 ~/.claude/skills/triage/scripts/triage-section.py {NAME}
```

The script walks the backlog (which step 2's self-resolutions may have mutated — Verify→Done, pending Q→Resolved), derives the banner, renders the body H2s, and atomically replaces the section in Q.md. Agent does not edit Q.md by hand.

### 5. Glance `{NAME} ask.md`

Always glance — bare `/ask` is the user explicitly engaging; always active mode. The user opens the doc, reads Agent Resolutions first, and is ready to push back or move on.

### 6. Console interleave — present 1–3 items

In chat, present an **auto-resolved-this-round** summary line (only when this call added new Agent Resolutions; omit otherwise), followed by **1–3 items** from the top of the User Verifications and Questions sections. Format each item with its short name + the action needed:

```
Auto-resolved this round: F081 (5 Qs → all per stated Leans), F085 (3 Qs → all per stated Leans),
QFix Q1 → D1. Say "resolutions look good" to accept; reference a specific one to roll back.

**Up next** (1–3 of N pending):

1. **[Verify F26]** — Open the app and confirm the panel renders on Cmd+Shift+P.
2. **F29 Q1** — max-retries cap: 3, 5, or unbounded? Recommendation: Lean (5).
3. **{NAME} Q3** — rename the slug from `foo` to `bar`? Recommendation: None.
```

**Auto-resolved line rules:**
- **Show only newly-added resolutions this call** — not the full accumulated list. The user sees fresh decisions; the carried-forward entries remain visible in `{NAME} ask.md` for review.
- **Omit entirely when this call added zero new resolutions** (don't surface noise).
- **Closing nudge** — always include *"Say 'resolutions look good' to accept; reference a specific one to roll back."* so the user has the acceptance vocabulary at hand.

**Cap of 3** for the **Up next** items — more would overflow the user's working memory in a single chat round. The user has the full queue in the doc.

### 7. Process user response

Four response shapes (per [[F086]]):

- **Acceptance of accumulated resolutions — full or partial.** The hard constraint: the user must explicitly mention the word **"resolution(s)"** in an accepting context. Bare phrases like *"looks good"* / *"accept"* / *"lgtm"* / *"approved"* do **not** count (too ambiguous in conversation — could be referring to any other open thing). Match flexibly once the word is present: *"resolutions look good"* / *"accept the resolutions"* / *"resolutions approved"* → **full accept** (clear all entries from `## Agent Resolutions`). *"accept the first 5 resolutions"* / *"the QFix resolutions look good"* / *"accept the F085 and F081 resolutions"* → **partial accept** (remove the named subset; the rest stay accumulated). On acceptance: remove the accepted entries from `{NAME} ask.md`, log in chat: *"Accepted N resolutions across {list of features}."*
- **Rollback of a specific resolution.** *"Roll back F24 Q3"* / *"undo the resolution on F23"* / *"no, do (B) on F085 Q1 instead"* → reverse the underlying change (feature-doc Resolved → Open Questions; backlog row may need rebracket via `backlog-edit.py {NAME} same <row-id> <PriorStatus>` per the workflow skill). **The remaining accumulated resolutions stay** — rollback does NOT implicitly accept the rest (superseded earlier design lean). The user closes by saying *"the rest of the resolutions look good"* when they've rejected everything they want to reject.
- **Answers to console questions** — *"F29 Q1: 5"* / *"verified F26"* / *"{NAME} Q3: yes"* → apply the resolution per § Resolution to the underlying feature doc / backlog. This **adds** to the accumulated `## Agent Resolutions` (one more entry at the top of the list); it does NOT clear what's already there.
- **Anything else** — continue normally; don't infer acceptance from ambiguous phrases.

After processing, regenerate `{NAME} ask.md` and surface the next 1–3 items in console. Repeat until the doc reports no pending items (User Verifications + Questions both empty AND `## Agent Resolutions` cleared) or the user disengages.

### 8. Idempotency

Bare `/ask` is **idempotent for the survey + write step**. State lives in `{NAME} ask.md`, the feature docs, and the backlog — never in invocation history. Re-invoking `/ask`:
- Re-runs the reasoning pass against the current backlog state.
- Carries forward accumulated `## Agent Resolutions` (re-checking each for drift per § 3).
- Rebuilds `## User Verifications` and `## Questions` from scratch.
- New auto-resolutions from this call prepend to the accumulated list.
- Resolutions the user already accepted stay accepted (they were removed from the file on acceptance and don't re-surface unless the underlying state changed back).


## Parented runbook

### 1. Number the questions

Every question gets a unique `Q<n>` prefix — `Q1`, `Q2`, ..., `Qn` — assigned in the order you'll present them.

**Numbering policy** — lowest unused integer in the **target file**:
- For `--doc` mode: scan the target doc's `## Open Questions` H2 (and the `### Resolved` sub-section, plus any bottom `## Resolved` H2) for existing `Q<n>` markers. Pick the lowest unused integer.
- For à la carte mode: scan the anchor's `{NAME} Questions.md` for existing `Q<n>` markers across `## Open Questions` (pending + `### Resolved`) and any bottom `## Resolved` H2. Pick the lowest unused integer. (À la carte uses `Q<n>` — same prefix as feature-attached Qs, in its own scoped namespace.)

**Q-numbers are stable references.** Once assigned, never renumber, even when questions get resolved out of order. Skipped numbers are fine. Same soft policy as backlog F-numbers — see [[CAB Backlog]] § Numbering policy.

### 2. Format each question

The full question-format spec — five-piece layout, recommendation-strength labels, spacing rules, block-ID navigation invariant, canonical examples — lives in the **[[ask-format]]** discipline. Every parented `/ask` invocation writes per that discipline. See `skills/ask-format/SKILL.md`.

Summary of the rules `/ask` applies when writing a question:
- Question header at top level with mandatory `^<container>-Q<n>` block-ID.
- Alternatives as labeled sub-bullets `(A)`, `(B)`, `(D1)`, etc. — one per bullet, never embedded prose.
- Recommendation outdented as sibling of the Question header — `**Recommendation:**` + Strong/Lean/None + reason.
- Block-ID link form (`[[file#^id|label]]`) for any external reference to a specific Q.

See [[ask-format]] for details, edge cases (open-ended Qs, follow-on child Qs), and enforcement.

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

### 4. Regenerate the anchor's section in `~/ob/kmr/Q.md` — **run the script** (per F104)

Per F104 (2026-06-02) this is mechanical: shell out, don't hand-write. Per F075 the per-anchor `{NAME} Triage.md` files were retired — Q.md sections are the only rendered form.

```bash
python3 ~/.claude/skills/triage/scripts/triage-section.py {NAME}
```

The script walks `{NAME} Backlog.md` (whose state step 3's `## Open Questions` edits just modified, by introducing or resolving Qs that affect the anchor's TAG / banner counts), derives the banner with cascading-TAG rule, renders body H2s (`## Active` / `## Ready` / `## Now` / `## Next` / `## Later` / `## Verify`) with bullets in source order, and atomically replaces the per-anchor section in `~/ob/kmr/Q.md`. De-dupes any existing section for `{NAME}` and bubbles the fresh one to the top.

If TAG is `[]` (anchor has zero live items anywhere), the script removes the section. Done.

The full spec for what the script writes (banner format, bracket forms, à la carte bullet line, body rendering rules, overflow handling) lives in `triage/SKILL.md` § 2–5 — those sections are the script's contract.

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

### 5. Glance the file (active mode only)

After writing the question(s) and regenerating Q.md via the script, `open <target>` so the file appears on the user's side and they can answer.

**Glance only when both conditions hold:**
1. The edit added or modified a pending question, AND
2. You're in **active mode** — the user is engaging with this work right now (they expect to answer in this turn or the next).

In **parking mode**, skip the glance — the file gets the questions but doesn't open at the user. The global page still updates either way (parked questions still need to surface eventually; the user finds them via the keyboard shortcut to `Q.md` when they choose to engage).

See § Active vs Parking mode for the full disambiguation. **Default when ambiguous: parking.**

**Never glance when the edit only resolved questions** (moved one or more from pending to `### Resolved`, or migrated the H2 to the bottom `## Resolved`). Resolution doesn't surface new state; pending questions were already visible.

### 6. Print one-line summary

After writing and (maybe) glancing, print a single-line summary to chat:

```
/ask — added N Qs to <target>; refreshed Q.md.
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
- `~/ob/kmr/Q.md` — the vault-level Agent Status dashboard, regenerated by `triage-section.py` per F104.
