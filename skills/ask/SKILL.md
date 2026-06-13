---
name: ask
description: Universal asking skill, two modes. Bare /ask (no arguments — primary mode) drains an anchor. agent self-resolves what it can (drive-mode-calibrated), writes a three-section {NAME} ask.md (Agent Resolutions / User Verifications / Questions), glances it, surfaces 1–3 items in console, iterates idempotently. Parented /ask (with --doc and/or explicit questions — secondary mode) parks individual questions on a feature doc, or authors them directly in {NAME} ask.md. Both modes regenerate the anchor's section in ~/ob/kmr/Q.md. Slash-only — "ask" is too common a spoken word to be a DMUX prefix-trigger.
user_invocable: true
---

# /Ask — Universal Asking Skill

> **Consult [[DSC technical-answer]] before responding to any user question about how a technical interface, API, signature, library, config, CLI, or wire format works.** `/ask` owns the asking side (formatting agent questions to the user); `[[DSC technical-answer]]` owns the answering side (responding to user questions about technical interfaces). When the user is asking a tech-interface question — even if `/ask` isn't explicitly invoked — apply that discipline's rules. The pair: ask-format for asking; technical-answer for answering.

`/ask` has **two modes**, distinguished by whether arguments are present.

| Mode | Invocation | What it does |
|---|---|---|
| **Bare** (primary) | `/ask` (no arguments) | User-invoked from within an anchor. Drains the anchor's open `[Verify]` and `[Questions]` items: self-resolves what it can (drive-mode-calibrated), writes the three-section `{NAME} ask.md`, glances it, surfaces 1–3 items in console, iterates. |
| **Parented** (secondary) | `/ask [--doc <path>] <q1> [<q2>...]` | Called from another skill's runbook (`/feature`, `/code plan`, `/groom`, `/crank`). Routes batched, numbered, formatted questions to a feature doc's `## Open Questions` block, or authors them directly in the anchor's `{NAME} ask.md` `## Questions` section. |

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


## Two valid surfaces + threshold (per F162, 2026-06-13 — supersedes F127's universal-render)

**A question may live in exactly TWO places — nowhere else:** (1) the anchor ask file `{NAME} ask.md`, or (2) the document where the question exists (feature doc / PRD / spec). Chat is a *dispatch view*, not a question store — a bare reference list in chat (`F113 Q12`) is never valid: it is neither surface and carries no context.

**Threshold — one inline, two-or-more written:**

| Span | Surface | What the agent does |
|---|---|---|
| **Exactly 1 question** | home doc (no render needed) | Ask it **inline in chat with full details** — title, context, labeled options with bodies, recommendation + strength, load-bearing flag. The Q still lives in its home doc as source of truth; no aggregation/glance required. User answers in chat. |
| **2+ Qs, all in ONE feature/doc** | that doc's `## Open Questions` | Write the Qs in (via `state q add`), then **glance the document**. Chat summarizes: *"3 Qs in F123 — Q1 X, Q2 Y, Q3 Z; load-bearing Q2."* User reads full bodies in the glanced doc. No aggregated page — the feature doc IS the surface. |
| **2+ Qs spanning 2+ features** (or anchor-level / à la carte) | `{NAME} ask.md` | Run the **render → audit → glance** procedure below, then spotlight 1-3 in chat. The ask file is the only coherent surface when no single doc holds them all. |

**As soon as there is more than one question it MUST be written down** in one of the two surfaces before surfacing. The single-Q-inline path is the *only* inline path — two questions inline is not allowed (this tightens F125's floated "maybe 2 inline").

### Render → audit → glance (the multi-feature / bare-drain procedure, per F127)

When the surface is `{NAME} ask.md` (a multi-feature span, or any **bare `/ask`** anchor-drain — multi-feature by nature), execute these three steps before producing any chat response:

1. **Render.** `python3 ~/.claude/skills/ask/scripts/ask-render.py {NAME}` — refreshes `{NAME} ask.md` from current source-of-truth markdown (feature docs' `## Open Questions` and backlog `[Verify]` rows), while **preserving** the page's own authored sections — `## Agent Resolutions` and any anchor-level questions authored directly in `## Questions`. Always writes the file (one-line empty-state when nothing's pending).
2. **Audit.** `python3 ~/.claude/skills/audit/scripts/audit-q.py --scope q --dry` — verifies the rendered report passes C1/C22 link-existence, C35 drift, C36 backtick-filepath checks. If errors surface, fix them at source (feature doc / backlog Open Question with the broken link) and re-render. Do NOT surface a broken ask report to the user.
3. **Glance.** `open "{NAME} ask.md"` — the rendered, audited page opens for the user.

Then respond in chat with the **spotlight format**: 1-3 items, one line each, naming the load-bearing Q and pointing at the glanced page. **The written surface is the source of truth for question bodies; chat is the dispatch view.**

```
Up next (1-3 of N pending):

1. **F<n> Q<k>** — <topic, ≤ 10 words>. **Load-bearing** (if any).
2. **F<m> Q<j>** — <topic>.
3. **{NAME} Q<l>** — <topic>.

(Full bodies in [[{NAME} ask]] — glanced.)
```

**Bare `/ask` always uses the ask-file procedure** — it drains the whole anchor, multi-feature by nature; render → audit → glance is mandatory there regardless of how many Qs surface. The inline path is for *targeted* single-Q asks (e.g. crank's cascade landing on one decision), not anchor drains.

**Relationship to F125 / F127.** [[F125 — Stop-and-ask cascade — crank must invoke ask on no-Ready; ask format scales with Q-count and feature-span|F125]] first scaled the format by span; [[F127 — Always-render ask report — ask invariant render + audit + glance before dialogue|F127]] replaced it with universal render-audit-glance because agents short-cut the inline path and produced context-less questions. F162 keeps F127's load-bearing lesson — once N>1, questions live in a written, navigable, link-resolvable surface — while restoring the single-Q-inline and single-feature-doc paths; the render-audit-glance machinery is retained on the ask-file surface. See [[F162 — Two-surface ask rule + crank-must-ask cascade|F162]].

### User-story scenarios

- **Story 1 — Crank cascades, one decision.** Crank exhausted Ready, groom dry, exactly one Q remains → ask it **inline with full details**, no page. User answers in chat.
- **Story 2 — 2+ Qs in one feature.** Write them into the feature doc (`state q add`), **glance the doc**, summarize topics + load-bearing one in chat. No aggregated page.
- **Story 3 — 2+ Qs across features.** Render → audit → glance `{NAME} ask.md`; spotlight the load-bearing 1-3.
- **Story 4 — Bare /ask anchor-drain.** Always the ask-file procedure; render → audit → glance, spotlight 1-3.
- **Story 5 — Zero pending.** Bare-drain renders the empty-state page (`_Nothing pending in scope._`), audit passes, glance opens it, chat says *"nothing pending in {NAME}."* A targeted single-Q ask with nothing pending simply doesn't fire.


## Two question shapes

Every question lands on one of two surfaces. The parent skill (or the user invoking `/ask` directly) tells `/ask` which.

| Shape | Flag | Surface | When |
|---|---|---|---|
| **Document-attached** | `--doc <path>` | The doc's `## Open Questions` H2 below the H1 | Question is about a specific feature doc / PRD / design doc / spec — it's already being asked inside that document. |
| **Ask-file** | (default — no flag) | The anchor's `{NAME} ask.md`, authored directly in `## Questions` | Question is anchor-level, cross-cutting, agent-raised, or planning-time — doesn't belong to one document. |

If the parent skill is ambiguous about which shape applies, default to **ask-file** — the question still gets surfaced, just at the anchor level rather than attached to a specific doc.

**There is no separate per-anchor questions file.** Anchor-level questions are written, in full ask-format, straight into `{NAME} ask.md` under its `## Questions` H2, where they sit alongside the rendered pointers to feature docs that have pending questions. The render **preserves** them across re-renders, exactly the way it preserves `## Agent Resolutions`.

**Anchor-level questions use `Q<n>` numbering, not `A<n>`** — same `Q<n>` prefix as feature-attached Qs, scoped per container (each feature doc has its own Q-namespace; the anchor's `{NAME} ask.md` has its own Q-namespace). When referenced in conversation: feature-scoped → `F010 Q3`; anchor-level → `{NAME} Q3` (e.g., "SKA Q3").


## Invocation

```
/ask                                  # bare mode — drain the current anchor
/ask <SLUG>                           # bare mode — drain a named anchor (cross-anchor)
/ask [--doc <path>] <q1> [<q2> ...]   # parented mode — park questions
```

- **No arguments** → bare mode; runs the § Bare invocation runbook against the **current anchor** (detected by walking up from cwd to the nearest `.anchor`).
- **Single positional argument matching an anchor slug** (e.g. `/ask SKA`, `/ask MUX`) → bare mode against the **named anchor**. The current agent does the work but reads the target anchor's Triage / Questions / feature docs. **Uncommon** — the local agent for that anchor usually has more context and will do a better self-resolution pass; use cross-anchor only when you specifically want the current agent to handle it.
- `--doc <path>` → parented document-attached mode; questions go in that doc's `## Open Questions` block (created if absent).
- No flag + positional `<question>` arguments → parented ask-file mode; questions are authored directly in the anchor's `{NAME} ask.md` `## Questions` section.
- Multiple positional questions → batched — number them all in one pass, never trickle.

**Disambiguation: anchor slug vs. question text.** A single positional argument is treated as an anchor slug if all three hold:
1. It's one token (no spaces).
2. It matches the shape `[A-Z][A-Za-z0-9]+` (starts with a capital, alphanumeric).
3. It resolves to a known anchor (walk the vault's `slug-index`, or check that `<SLUG>/.anchor` exists, or that `<SLUG> Triage.md` / `<SLUG> Backlog.md` exists somewhere reachable).

If any check fails, treat the argument as anchor-level question text and run the parented runbook. Multiple positional arguments are always parented (no anchor slug has spaces).

**Slash-only invocation.** Unlike `crank`, `groom`, `triage`, etc., the spoken word "ask" is **not** a DMUX prefix-trigger — it's too common in everyday speech. Invoke via `/ask` only.


## Bare invocation runbook

Bare `/ask` (no arguments) drains the anchor's open `[Verify]` and `[Questions]` items in a way that minimizes round-trips with the user. The agent does the work that *can* be done without the user, then surfaces only the residue.

### 1. Identify the anchor and survey open work

**Default (no argument):** walk up from the working directory to the nearest `.anchor` to determine `{NAME}`. This is the common case — the agent's own anchor.

**Cross-anchor (single slug argument):** if invoked as `/ask <SLUG>` and the slug resolves to a known anchor (per the § Invocation disambiguation rules), set `{NAME}` = `<SLUG>` and read that anchor's files instead of the current one. The current agent does the work using the target anchor's Triage / Questions / feature docs.

Then read `{NAME} Backlog.md` and enumerate every item bracketed `**[N Questions]**` or `**[Verify]**` across the **Active / Ready / Now / Next / Verify** sections. The dedicated `## Verify` horizon (per F100) is where most user-actionable `[Verify]` rows live — surfacing them is a core purpose of bare `/ask`, so it is **in scope**. **`## Later` and `## Icebox` are disregarded entirely** — regardless of bracket, regardless of why the item is there. Later means *not in scope for now*; if the user has parked something in Later, that's the user's explicit signal to not surface it. This applies *universally* to every path through bare `/ask` — survey (this step), reasoning (step 2), drain-page write (step 3), and console interleave (step 6). Even a `[Questions]` or `[Verify]` row sitting in `## Later` is out of scope; bare `/ask` does not see it, does not self-resolve it, does not list it, does not mention it. (Triage's selective-surfacing of Later items is a Triage behavior; bare `/ask` does not inherit it.) Also include any anchor-level Qs already authored in `{NAME} ask.md` § `## Questions`.

If the survey returns zero pending items, write a one-line summary (`/ask — nothing pending in {NAME}.`), refresh the anchor's section in `Q.md` (will likely drop it), and exit.

### 2. Reasoning pass — self-resolve what you can

For each surveyed item, attempt to resolve it autonomously. Calibrate the threshold by the active drive mode (see `[[SKA mode]]`):

- **`[Verify]` items** — read the linked feature doc's `## Success Criteria` block first (per `[[DSC verification]]`). The tier label tells you what to do:
  - **Tier 1 (agent-immediate):** run the named check now. If it passes, mark Done via `state task update`; do not surface to the user. If it fails, rebracket to `[Active]` and the work is not done.
  - **Tier 2 (agent-over-time):** the agent owns the deferred check (hook, schedule, watchdog). Do not surface; do not block.
  - **Tier 3 (user-passive):** add a brief reminder in the ask page of what to watch for; do not block on a user answer. Optionally ask once after enough time has passed (typically a week).
  - **Tier 4 (user-explicit):** surface as a User Verification with the specific steps from the feature doc. Even here, challenge yourself: has enough time passed that a passive signal might already have arrived? If yes, downgrade to tier 3 and drop the surfacing.

  Mark verifications Done via `state task update` (auto-refreshes Q.md) and update the feature doc's Status field:

  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Done --horizon Done
  ```

  Title and body are preserved.

  **Feature docs without a `## Success Criteria` block** (predating F101) default to tier 4 surfacing for safety, but the agent should add the missing block on the next touch rather than perpetuating the bother-the-user default.

  **Batching when multiple tier-3 or tier-4 Verifies surface** (per `[[DSC verification]]` § How to surface a Verify to the user): if several Verify rows reduce to the same user action ("did this work in normal use?", "did the bug recur?"), combine them into one targeted question with the linked feature docs listed. The user gives a single yes-or-no answer; the agent applies it to all listed rows. Never write "verify F57, F58, F59" as separate items if a single observation would resolve all three. The question itself must carry the answer-enabling context, not point at a doc to read.
- **`[Questions]` items** — *can I confidently pick the most likely answer?* Read the feature doc's `## Open Questions` block, the surrounding code, prior similar decisions in the anchor's `## Resolved`, the user's stated preferences (memory), and the design rationale. For each Q where the answer is clear, write the inline resolution per § Resolution and update the feature doc.

- **Pre-ask self-check (per F105)** — before queuing any Q for the user, run the five named patterns from `[[DSC ask-format]]` § Pre-ask self-check: (1) aggregate across all feature docs + the ask file's anchor-level Qs within this anchor — don't surface one feature's Qs in isolation when others have pending ones; (2) "continue or stop?" → continue; (3) "burn tokens for a better outcome?" → yes; (4) "how to split the work?" → agent decides, file new features `[Ready]` when independently doable; (5) "quick way or complete way?" → complete (file quick-way's complete version as `[Ready]` if doing quick first). Any Q matching one of these is auto-resolved into the relevant `## Resolved` H2 (feature doc) or `## Agent Resolutions` (this anchor's ask page), never surfaced.

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

### 3. Write `{NAME} ask.md` — **run `ask-render.py`** (per F117, 2026-06-07)

Per F117 the ask page is a **rendered view** of canonical markdown sources (feature docs + backlog), with two **authored** sections that live only here and are preserved across renders: `## Agent Resolutions`, and any anchor-level questions inside `## Questions`. Don't hand-edit the *rendered* lines (feature-doc Q pointers, Verify rows) — fix those at source. Do author anchor-level Qs directly into `## Questions`.

```bash
python3 ~/.claude/skills/ask/scripts/ask-render.py {NAME}
```

The script:
- Walks reachable feature docs via `extract_q_entries` (audit-q's H3-aware Q parser) for pending Qs → rendered pointer lines in `## Questions` (e.g. `- [[F28]] — 3 Qs (Q1, Q2, Q5).`).
- Walks `{NAME} Backlog.md` for `[Verify]` / `[Verify-by ...]` rows in **in-scope horizons** (`Active`/`Ready`/`Now`/`Next`/`Verify` — `## Later` and `## Icebox` disregarded, mirroring step 1; the dedicated `## Verify` horizon per F100 is where most live) → `## User Verifications` body. Each row renders the row's `**Verify (you):** <actionable steps>` marker after the link (falling back to the title only when the marker is absent — see the actionability rule below).
- **Preserves the page's authored content verbatim**: the `## Agent Resolutions` body (F086 carry-forward) AND any anchor-level Q bullets already in `## Questions` (those not matching the rendered feature-pointer shape). Drift-checking belongs to `/ask`, not the script.
- Writes the three-section page atomically.

**Agent-side responsibilities (the script does NOT do these — the runbook does):**

1. **Add new resolutions to the page before invoking the script** — when this call's reasoning pass (step 2) auto-resolved Qs or Verifies, edit `{NAME} ask.md`'s `## Agent Resolutions` H2 *before* calling `ask-render.py`. Prepend new entries at the top (newest first); the script will preserve whatever's there.
2. **Live drift-check carried-forward resolutions** — for each entry already in `## Agent Resolutions`, confirm the underlying feature doc's `## Resolved` H2 (or backlog row state) still matches. On drift, delete the entry from the section before invoking the script, and flag in chat: *"Dropped carried-forward resolution for F<n> — feature doc state diverged."*
3. **Soft cap warning** — after the script writes, if accumulated `## Agent Resolutions` > 20 entries, append a chat note: *"21 unaccepted resolutions accumulated — say 'the resolutions look good' to clear, or work through them."*

Acceptance / rollback are processed in § 7.

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

- [[F26 — Manual UX flow]] **[Verify]** — Open the Window Settings dialog (Cmd+R), resize it, Cmd+Q and relaunch — confirm the panel reopens at the size you left it.

## Questions

- [[F28 — Naming]] — 3 Qs (Q1, Q2, Q5). Naming-convention fork; see the feature doc.
- [[F29 — Retry policy]] **Q1** — max-retries cap: 3, 5, or unbounded?

- **Q3 — Rename the `foo` slug to `bar`?** — `foo` collides with [[bar]] vault-wide; renaming sweeps ~12 refs. ^{NAME}-Q3
  - (A) Rename to `bar` — removes the collision.
  - (B) Keep `foo` — accept the ambiguity.
  - **Recommendation:** None — user-preference call.
```

(The first two bullets are **rendered pointers** to feature docs with pending Qs; `Q3` is an **anchor-level question authored directly here** in full ask-format — its durable home is this file. The render keeps the pointers fresh and leaves the authored Q untouched.)

Rules:
- **Every User Verification states the concrete action, not the feature name.** "verify F125" is useless — the user can't tell what cognitive work is required, so they'd either rubber-stamp it or ignore it. Each row, *after* the header link, must say exactly what to do: *go to this screen, click this button, do X, confirm Y.* The source is a `**Verify (you):** <do this — open X, click Y, confirm Z>` marker placed on the backlog `[Verify]` row (or distilled from the feature doc's `## Success Criteria` → "How it will be verified"); `ask-render` renders that marker after the link, falling back to the row title only when the marker is absent (a gap to fix, not a valid state). Tier-1/Tier-2 verifies are agent-owned and self-resolved in step 2 — they never reach this section; only Tier-3/Tier-4 user-actionable verifies render here, so every one MUST carry runnable steps.
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

### 4a. Audit the rendered report — **F127 mandatory gate**

Per F127, every `/ask` MUST run audit-q on the rendered ask.md before glancing. The audit verifies that wiki-links in the question summaries resolve (C1/C22), that ask.md content matches what's pending at source (C35 drift), and that backtick file-paths have been replaced with clickable links (C36):

```bash
python3 ~/.claude/skills/audit/scripts/audit-q.py --scope q --dry
```

- **0 errors** → proceed to glance (step 5).
- **Errors related to ask.md content** → fix at SOURCE (the feature doc whose Open Question has the broken link / the backlog row with the stale Verify) and re-run `ask-render.py {NAME}`; re-audit until clean.
- **Pre-existing errors elsewhere in the vault** unrelated to this anchor's ask surface → record them in chat, don't block. The user's pain that motivated F127 is *navigation* of the surfaced questions; pre-existing drift in other anchors doesn't gate this anchor's surface.

This is non-skippable. A broken ask report (broken links the user can't click) is the failure mode F127 exists to prevent.

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
- **Rollback of a specific resolution.** *"Roll back F24 Q3"* / *"undo the resolution on F23"* / *"no, do (B) on F085 Q1 instead"* → reverse the underlying change (feature-doc Resolved → Open Questions; backlog row may need rebracket via `state --anchor {NAME} task update <row-id> --status <PriorStatus>` per the workflow skill). **The remaining accumulated resolutions stay** — rollback does NOT implicitly accept the rest (superseded earlier design lean). The user closes by saying *"the rest of the resolutions look good"* when they've rejected everything they want to reject.
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
- For ask-file mode: scan the anchor's `{NAME} ask.md` `## Questions` section for `Q<n>` markers on anchor-level questions. Pick the lowest unused integer. (Anchor-level Qs use `Q<n>` — same prefix as feature-attached Qs, in their own scoped namespace.)

**Q-numbers are stable references.** Once assigned, never renumber, even when questions get resolved out of order. Skipped numbers are fine. Same soft policy as backlog F-numbers — see [[CAB Backlog]] § Numbering policy.

### 2. Format each question

The full question-format spec — five-piece layout, recommendation-strength labels, spacing rules, block-ID navigation invariant, canonical examples — lives in the **[[DSC ask-format]]** discipline. Every parented `/ask` invocation writes per that discipline. See `skills/ask-format/SKILL.md`.

Summary of the rules `/ask` applies when writing a question:
- Question header at top level with mandatory `^<container>-Q<n>` block-ID.
- Alternatives as labeled sub-bullets `(A)`, `(B)`, `(D1)`, etc. — one per bullet, never embedded prose.
- Recommendation outdented as sibling of the Question header — `**Recommendation:**` + Strong/Lean/None + reason.
- Block-ID link form (`[[file#^id|label]]`) for any external reference to a specific Q.

See [[DSC ask-format]] for details, edge cases (open-ended Qs, follow-on child Qs), and enforcement.

### 3. Write to the target surface

**Per F128/F129 (2026-06-07), Q-writes delegate to `state q`** — the canonical state-editor for everything below the anchor level. Agents should NOT hand-edit `## Open Questions` blocks directly; the script enforces ask-format spec (block-IDs, Q-numbering, Phase 1/2/3 lifecycle) at write time.

#### Document-attached mode (`--doc <path>`) — preferred form via script

```bash
# Add a Q to a feature doc (stdin form — primary):
state --anchor {NAME} q add F<n> < q-body.md

# Or with --from-file for longer Qs:
state --anchor {NAME} q add F<n> --from-file path/to/q.md

# Or inline for short one-liners:
state --anchor {NAME} q add F<n> -m "**Q<n> — short** — body."

# Resolve a Q (with chosen option + resolution body):
state --anchor {NAME} q answer F<n> -n <n> --choice "(A)" < resolution.md

# Remove a Q (preserves audit trail in ### Removed):
state --anchor {NAME} q remove F<n> -n <n> --reason "..."

# Rewrite a Q's body (no --force gate in F129):
state --anchor {NAME} q rewrite F<n> -n <n> < new-body.md
```

The script auto-mints the next Q-number, formats per ask-format, ensures `## Open Questions` H2 exists, and runs `ask-render.py {NAME}` + lenient `audit-q --scope q --dry` as post-conditions per F127's render-audit-glance invariant. Spec details in [[SKL State]]; predecessor [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] documents the legacy CLI shape.

#### Document-attached mode — legacy hand-edit form

If the script isn't reachable (rare), append the formatted questions to the doc's `## Open Questions` H2 manually. The H2 sits **directly below** the H1 of the doc.

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

#### Ask-file mode (default)

Author the formatted questions **directly** into the anchor's `{NAME} ask.md`, under its `## Questions` H2, as full ask-format bullets (block-ID, labeled options, `**Recommendation:**`). They sit below any rendered feature-doc pointer lines and are **preserved** by `ask-render.py` across re-renders. **There is no separate questions file.**

- **Block-ID:** `^{NAME}-Q<n>` (e.g. `^SKA-Q3`) — the anchor slug scopes the namespace.
- **Numbering:** lowest unused `Q<n>` among the anchor-level questions already in `## Questions` (per § 1).
- **If `## Questions` doesn't exist yet**, add the H2 when authoring the first anchor-level Q (or let `ask-render.py` create it on the next render).
- **Resolution:** when the user answers, write the resolution into `## Agent Resolutions` (per § 7) and remove the answered Q bullet from `## Questions`. The ask file is a live drain, not an archive — there is no `### Resolved` holding pen here. When an anchor-level decision deserves a durable record, it goes in the relevant feature doc's `## Resolved` or in `[[SKA Decisions]]`, not in the ask file.

Workflow: author the Q into `## Questions`, then run `ask-render.py {NAME}` (it preserves the authored Q and refreshes the feature-doc pointers), then audit + glance per the F127 invariant.

`state q` (F128/F129) operates on feature docs only — anchor-level Qs are hand-authored into `## Questions` and don't go through it.

**Legacy migration**: if an anchor still has a `{NAME} Questions.md` file (pre-removal), move its pending `## Open Questions` bullets into `{NAME} ask.md` § `## Questions` (preserving Q-numbers and `^{NAME}-Q<n>` block-IDs), then delete `{NAME} Questions.md`. Resolved/archived Qs in that file can be dropped, or moved to the relevant feature doc / `[[SKA Decisions]]` if still useful.

### 4. Regenerate the anchor's section in `~/ob/kmr/Q.md` — **run the script** (per F104)

Per F104 (2026-06-02) this is mechanical: shell out, don't hand-write. Per F075 the per-anchor `{NAME} Triage.md` files were retired — Q.md sections are the only rendered form.

```bash
python3 ~/.claude/skills/triage/scripts/triage-section.py {NAME}
```

The script walks `{NAME} Backlog.md` (whose state step 3's `## Open Questions` edits just modified, by introducing or resolving Qs that affect the anchor's TAG / banner counts), derives the banner with cascading-TAG rule, renders body H2s (`## Active` / `## Ready` / `## Now` / `## Next` / `## Later` / `## Verify`) with bullets in source order, and atomically replaces the per-anchor section in `~/ob/kmr/Q.md`. De-dupes any existing section for `{NAME}` and bubbles the fresh one to the top.

If TAG is `[]` (anchor has zero live items anywhere), the script removes the section. Done.

The full spec for what the script writes (banner format, bracket forms, body rendering rules, overflow handling) lives in `triage/SKILL.md` § 2–5 — those sections are the script's contract.

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

`<target>` is the doc path or `{NAME} ask.md`.


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

- `[[FCT Triage]]` — sibling facet that surfaces (reads) the questions `/ask` writes. `/ask` is the writer; `/triage` is the reader/router.
- `[[CAB Backlog]]` § Numbering policy — same lowest-unused-integer rule for Q numbers.
- `~/ob/kmr/Q.md` — the vault-level Agent Status dashboard, regenerated by `triage-section.py` per F104.
