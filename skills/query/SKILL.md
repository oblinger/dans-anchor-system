---
name: query
description: >
  Ask the user questions by building the anchor's `{NAME} queries.md` (in
  `{NAME} Track/`). Walk every open question; decide per question how to raise it
  — auto-resolve a reversible soon-visible guess, do a check yourself rather than
  ask, request a SPECIFIC user verification, ask a self-contained yes/no, or link
  out — into four sections (Agent Resolutions / Verifications / Immediate
  Questions / Questions). Glance the doc, optionally echo immediate items to the
  console in the inline-ask format, and trim answered items. The clean successor
  to /ask. Use when the user runs /query or an agent needs a decision. Per F169.
tools: Read, Write, Edit, Bash, Glob
user_invocable: true
---

# /query — ask the user questions

`/query` builds and maintains the anchor's **`{NAME} queries.md`** — the single surface where the user answers everything the agents need from them. Its discipline: most "questions" should never reach the user; only genuine user decisions and genuine user-only verifications survive, each made answerable from what's written. Full spec: [[F169 — Query skill — queries document + determination logic|F169]]. Replaces `/ask` (which rotted by accreting dashboard + render-pipeline + triage coupling — keep `/query` narrow).

## The document — `{NAME} queries.md` in `{NAME} Track/`

Slug-prefixed (sorts to front), agent-owned, four sections in **fixed order** (omit a section when empty):

1. **`## Agent Resolutions`** — decisions the agent made on its own. One line each: what was decided + why + a link to the question's home. The user's catch-a-wrong-guess surface.
2. **`## Verifications`** (numbered **V1, V2, …**) — a check the user **judges**, never one they run. The agent runs it; the user only looks and answers **yes/no**. Default: run it **ahead of time** and embed the result in the line (image / output / rendered artifact), then ask — e.g. *"V1 — I rendered ![[X.svg]]; is it legible? (yes/no)"*. If it genuinely must run live: *"V1 — tell me when you're ready; I'll run it and show you the result to judge."* **Forbidden:** asking the user to run/execute anything ("run X and tell me…"), "verify F113", or a whole-document general eyeball. Every verification ends in a yes/no on something the agent produced. (No yes/no, no judgeable artifact ⇒ it isn't a verification — see determination §6.)
3. **`## Immediate Questions`** (preferred user-question form) — self-contained yes/no questions: **one context line** (names the feature + what it's about) then **one line** (the question, ideally yes/no; ≤ 2 lines). Readable without opening anything. Link the feature-doc question (`F<n> Q<m>`) when one exists.
4. **`## Questions`** (least preferred catch-all) — links to feature-doc questions in `F<n> Q<m>` form (clickable to background). For non-yes/no questions, or features with **> 3** open questions (link the feature, don't enumerate).
5. **`## Ready`** (optional, bottom) — features that are decided + ready to build (on the backlog as `[Ready]`), listed for visibility. Where actionable non-question items land (determination §6). Source of truth is the backlog; listing here is optional.

## Determination logic — route every open question

Walk each feature's `## Open Questions` (enumerate only when **≤ 3**; if **> 3**, emit one `## Questions` link to the feature — no enumeration) plus any backlog questions. For each, pick the FIRST that applies (preference order):

1. **Auto-resolve → `## Agent Resolutions`** — if (a) the user would **likely notice** a wrong choice soon in the natural course of work, AND (b) it's **relatively reversible**, AND (c) the agent has a **reasonable idea** of the right answer → the agent **guesses and records** the determination. Does not ask.
2. **Do-it-yourself (don't ask)** — if the item is a check the agent **can run itself**, run the test now and answer it (or file the answering task on the backlog). Never pose a self-answerable check to the user.
3. **User-judged verification → `## Verifications`** — a check whose *judgment* needs the user. The agent still **runs** it (ahead of time + embed the result, or live-on-ready); the user only answers yes/no. Never ask the user to run anything (the §2 rule).
4. **Immediate yes/no → `## Immediate Questions`** — a real user decision framable as a self-contained yes/no.
5. **Catch-all → `## Questions`** — not yes/no, or > 3 per feature → a `F<n> Q<m>` link. Reshape into 1–4 first if you can.
6. **Actionable, but not a user question/verification → land it or make it a Ready feature (never an orphan line).** If an item is neither a question the user answers nor a check the user judges, it is **not** a queries item. Either **land it now** (small + clear) or make it a **`[Ready]` feature on the backlog** (commission one with `/feature` if none exists) — optionally surfaced in `## Ready`. A line with no yes/no and no user-judgeable artifact is forbidden: convert it to a question, a verification, an immediate landing, or a Ready feature.

## Console echo

After glancing the doc, `/query` may print a few **immediate** items — resolutions made this pass, user verifications, immediate questions — to the console in the **inline-ask format** ([[SKL ask-inline]]): one context line + a ≤2-line ask. **Invariant:** anything echoed is also in the document (console = dispatch view; doc = store).

## Runbook

1. **Locate the anchor** (walk up to `.anchor`). Target `{NAME} Track/{NAME} queries.md` (create if absent: frontmatter + `# {NAME} Queries` H1 + the four sections).
2. **Collect** open questions: each feature doc's `## Open Questions` (≤3 enumerate / >3 link) + backlog questions.
3. **Route** each via the determination logic. For auto-resolves, make the guess and (where it shapes a doc) apply it. For do-it-yourself checks, run them now / backlog them.
4. **Write** the four sections in order, each item in its section's format. Verifications must be specific; immediate questions self-contained; catch-all questions are `F<n> Q<m>` links.
5. **Glance** `{NAME} queries.md` (`open "<path>"`).
6. **Echo** (optional) a few immediate items to the console in inline-ask format — all also in the doc.
7. **On answer** (`Q1: yes`, `F115 Q3: A`, "verified the panel reopen", prose): record the resolution at the question's home and **trim** the answered item from `{NAME} queries.md`. Re-running `/query` rebuilds from current state, so the doc shrinks monotonically. Sticky context: once the user names a feature, bare `Q<n>` targets it.

## Boundaries

`/query` only asks, records, and trims. The cross-anchor dashboard (`[[Q]]`), `[Verify]`-row surfacing, and banner/TAG rendering belong to `/triage`. Never write an unanswerable item: if it can't be made a concrete decision/verification, the agent decides it (reversible → guess + record) or does the work that resolves it.
