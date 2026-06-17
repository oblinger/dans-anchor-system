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

The file's validity rules — sections + order, what each item must look like, the no-user-imperative and no-orphan invariants — live in the **[[FCT Query]] facet** (`R-query`), so the file is auditable (`/audit doc`, the on-write hook) and there's one source of truth. **Write to conform to `R-query`; don't restate it here.** Quick orientation only — five sections, fixed order, omit-if-empty:

`## Agent Resolutions` (reversible-guess records) → `## Verifications` (V-numbered; agent-run, user-judged yes/no; never "you run X") → `## Immediate Questions` (numbered handle + self-contained yes/no) → `## Questions` (catch-all `F<n> Q<m>` links) → `## Ready` (optional; backlog `[Ready]` features, for visibility).

**Every item the user answers carries a citable handle** so they can refer to it: Verifications lead with `V<n>`; Immediate Questions lead with `F<n> Q<m>` (the source feature's native number) when they route a feature-doc question, else an anchor-local `Q<n>`. The handle is bold and leads the bullet — the user answers `F176 Q1: yes`, `Q2: B`, `V1: yes`.

The skill's job below is the *procedure* that produces a conforming file.

## Determination logic — route every open question

Walk each feature's `## Open Questions` (enumerate only when **≤ 3**; if **> 3**, emit one `## Questions` link to the feature — no enumeration) plus any backlog questions. For each, pick the FIRST that applies (preference order):

> **Pending-only gate (load-bearing — the F125 failure 2026-06-16).** A "question" counts only if it is a genuinely *pending* Q-header — one that is **not** under a `### Resolved` (or `## Resolved`) sub-heading and not otherwise marked answered. A feature whose `## Open Questions` block was deleted (Phase 2) or whose Q-headers all live under `### Resolved` has **zero** open questions: it must **not** appear in `## Questions` (nor anywhere as pending). Before emitting any pending entry for a feature, confirm it has ≥1 truly-pending Q — the same set `audit-q.py`'s `extract_q_entries` returns. Listing an all-resolved feature in `## Questions` is exactly what audit-q **C35** now flags; do not author what the audit will reject.

1. **Auto-resolve → `## Agent Resolutions`** — if (a) the user would **likely notice** a wrong choice soon in the natural course of work, AND (b) it's **relatively reversible**, AND (c) the agent has a **reasonable idea** of the right answer → the agent **guesses and records** the determination. Does not ask.
2. **Do-it-yourself (don't ask)** — if the item is a check the agent **can run itself**, run the test now and answer it (or file the answering task on the backlog). Never pose a self-answerable check to the user.
3. **User-judged verification → `## Verifications`** — a check whose *judgment* needs the user. The agent still **runs** it (ahead of time + embed the result, or live-on-ready); the user only answers yes/no. Never ask the user to run anything (the §2 rule).
4. **Immediate yes/no → `## Immediate Questions`** — a real user decision framable as a self-contained yes/no. **Begin the bullet with a bold anchor-local `Q<n>` handle** (numbered within the section, so the user answers `Q1: A`); name any feature as a wiki-link in the body (a feature's native `F<n> Q<m>` is *referenced* there, but the answer handle is the queries-local `Q<n>`). Each bullet carries an **answer shape** (bold `**yes/no**` or bold `**(A)** / **(B)** / **(C)**` options) and the word **Recommendation** (may be `None`). Conforms to `R-query-08`/`R-query-13` (audit-q C39/C40/C41/C37).
5. **Catch-all → `## Questions`** — not yes/no, or > 3 per feature → a `F<n> Q<m>` link. Reshape into 1–4 first if you can.
6. **Actionable, but not a user question/verification → land it or make it a Ready feature (never an orphan line).** If an item is neither a question the user answers nor a check the user judges, it is **not** a queries item. Either **land it now** (small + clear) or make it a **`[Ready]` feature on the backlog** (commission one with `/feature` if none exists) — optionally surfaced in `## Ready`. A line with no yes/no and no user-judgeable artifact is forbidden: convert it to a question, a verification, an immediate landing, or a Ready feature.

## Console echo

After glancing the doc, `/query` may print a few **immediate** items — resolutions made this pass, user verifications, immediate questions — to the console in the **inline-ask format** ([[SKL ask-inline]]): one context line + a ≤2-line ask. **Invariant:** anything echoed is also in the document (console = dispatch view; doc = store).

## Runbook

1. **Locate the anchor** (walk up to `.anchor`). Target `{NAME} Track/{NAME} queries.md` (create if absent: frontmatter + the H1 + the four sections). **H1 format (load-bearing):** `# [[{NAME}|{NAME}]] Queries · _computed {YYYY-MM-DD HH:MM}_` — the anchor name is a live link to its anchor page, and the `_computed …_` stamp is the date+time you (re)build the list. **Refresh the timestamp on every run** (`date "+%Y-%m-%d %H:%M"`) so staleness is visible at a glance — it's surfaced on the Q.md dashboard.
2. **Collect** open questions: each feature doc's `## Open Questions` (≤3 enumerate / >3 link) + backlog questions.
3. **Route** each via the determination logic. For auto-resolves, make the guess and (where it shapes a doc) apply it. For do-it-yourself checks, run them now / backlog them.
4. **Write** the four sections in order, each item in its section's format (per `R-query`). Verifications begin with `**V<n>` + a bold yes/no; immediate questions begin with `**Q<n>` + answer shape + the word `Recommendation`; catch-all questions are `F<n> Q<m>` links. Any `F<n>` a bullet names is a wiki-link (feature doc, else `[[{NAME} Backlog#^F<n>|F<n>]]`).
5. **Audit the file before surfacing it — MANDATORY** (the F125 lesson: the C35 check only protects you if `/query` actually *runs* it). The on-write hook covers markdown/format on the Write, but the cross-doc consistency checks (C35 stale-pending, C6/C9 Q-format, C36 link-not-backtick) live in `audit-q.py` and are **not** triggered by writing the file — run them explicitly:
   ```bash
   python3 ~/.claude/skills/audit/scripts/audit-q.py --scope backlog --anchor {NAME} --dry
   ```
   **Fix every finding at its source, then re-run until the `{NAME} queries.md` line count is 0.** A C35 ("lists F<n> under ## Questions but its linked doc has no pending Qs") means you violated the pending-only gate — remove that entry. Do **not** proceed to the Q.md refresh or the glance with a dirty audit; surfacing a broken queries file is the exact failure this step exists to prevent.
6. **Refresh the Q.md dashboard** — after writing `{NAME} queries.md`, paste it into the vault Q.md so the anchor's per-anchor section shows the freshly-computed queries body (not stale state):
   ```bash
   python3 ~/.claude/skills/triage/scripts/triage-section.py {NAME}
   ```
   `triage-section.py` reads `{NAME} queries.md`, strips its frontmatter + H1, and renders the Q.md section as `<count banner → links to queries.md>` + `_queries computed <timestamp>_` + the queries body. (This is the F176 model — Q.md per-anchor body **is** the queries paste, replacing the legacy backlog-row/ask dump. Anchors with no `queries.md` fall back to the backlog-derived body.)
7. **Glance** `{NAME} queries.md` (`open "<path>"`).
8. **Echo** (optional) a few immediate items to the console in inline-ask format — all also in the doc.
9. **On answer** (`Q1: yes`, `F115 Q3: A`, "verified the panel reopen", prose): record the resolution at the question's home and **trim** the answered item from `{NAME} queries.md`. Re-running `/query` rebuilds from current state, so the doc shrinks monotonically. Sticky context: once the user names a feature, bare `Q<n>` targets it.

## Parented mode — `/query --doc <path> <q1> [<q2> …]`

The secondary invocation, called from another skill's runbook (`/feature`, `/code plan`, `/groom`, `/design`) when it has decisions to park in a *specific* document. It authors numbered, ask-format questions directly into `<path>`'s `## Open Questions` block (created below the H1 if absent) and does **not** build the anchor's `queries.md` — the Qs surface there on the next bare `/query` pass via the determination logic.

- **Mechanism:** resolve `<path>` to its feature/PRD doc, then delegate to `state q add` (which enforces the ask-format spec — block-IDs, `Q<n>` numbering, recommendation strength, Phase 1/2/3 lifecycle):
  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} q add F<n> < q-body.md
  ```
- **Multiple questions** are batched — numbered in one pass, never trickled.
- **Glance** the doc only in active mode (the user is engaging now); skip the glance in parking mode (batch filing for later). Mirrors `/feature` § 1a.
- This is the successor to `/ask --doc`; the question *format* discipline is unchanged — it still lives in [[DSC ask-format]], which `/query` cites.

## Boundaries

`/query` only asks, records, and trims. The cross-anchor dashboard (`[[Q]]`), `[Verify]`-row surfacing, and banner/TAG rendering belong to `/triage`. Never write an unanswerable item: if it can't be made a concrete decision/verification, the agent decides it (reversible → guess + record) or does the work that resolves it.
