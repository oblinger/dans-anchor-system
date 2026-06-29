---
name: query
description: >
  The system for NOT asking the user questions piecemeal. Prime directive:
  ELIMINATE every question the agent can (auto-resolve reversible/soon-visible
  guesses, run checks itself, decide low-stakes/visible calls, infer from the
  codebase), then CONSOLIDATE the irreducible residue into one self-documenting,
  counted, one-shot-answerable pile in the anchor's `{NAME} queries.md` (sections
  Agent Resolutions / Verifications / Immediate Questions / Questions). The doc is
  the always-current STORE of open questions — write every question there the
  moment it is raised; chat is at most a VIEW, never carrying a question the doc
  lacks (the user runs many agents; chat scrolls away). Glance the doc and trim
  answered items. Use when the user runs /query or an agent has a decision to
  route. Per F169 + [[Query PRD]].
tools: Read, Write, Edit, Bash, Glob
user_invocable: true
---

# /query — ask the user questions

`/query` builds and maintains the anchor's **`{NAME} queries.md`** — the single surface where the user answers everything the agents need from them. Its discipline: most "questions" should never reach the user; only genuine user decisions and genuine user-only verifications survive, each made answerable from what's written. **Authoritative purpose + the never-ask invariant: [[Query PRD]]** (the agent's prime directive is to NOT ask — eliminate every question it can, consolidate the irreducible residue into one self-documenting, one-shot-answerable pile; asking in chat, especially after a triage, is the cardinal violation). Full spec: [[F169 — Query skill — queries document + determination logic|F169]]. Replaces `/ask` (which rotted by accreting dashboard + render-pipeline + triage coupling — keep `/query` narrow).

> ## ⚠️ TWO NORTH STARS — NON-NEGOTIABLE
>
> **1. The queries doc is the always-current STORE of open questions — chat is at most a VIEW of it.**
> `{NAME} queries.md` holds the anchor's open questions *at all times*. **The moment you have a question for the user, write it into the doc — at that same moment** (run the determination logic, write the survivors), and *then* you may optionally echo a spotlight to chat. Chat may point *into* the doc, but it **never carries a question the doc doesn't**, and **the doc is never behind chat**. A chat question with no corresponding doc entry means the question was *not actually asked* — redo it through the doc. Why this is non-negotiable: the user runs **many agents at once** and **chat scrolls away**; `queries.md` is the one place they can always return to for the latest open questions. (The doc may legitimately lag only during live back-and-forth before the next triage; every triage — and every question raised — re-syncs it. This is the recurring failure the user has called out: agents ask in chat and never touch the doc. Treat a bare chat-ask as a bug in your own behavior.)
>
> **2. Every surfaced question is SELF-DOCUMENTING.** Reading the entry *alone*, the user must (a) know exactly **what is being asked**, and (b) have **everything needed to answer it** — either stated in the entry or reachable through a link *in* the entry. If answering requires the user to go hunt for context that isn't linked, the entry fails. And every entry that routes a feature's open questions **states its pending-Q count in bold parens** — `[[F181 — …|F181]] **(5Q)**` — so the user sees at a glance how many answers that feature needs from them.

## The document — `{NAME} queries.md` in `{NAME} Track/`

The file's validity rules — sections + order, what each item must look like, the no-user-imperative and no-orphan invariants — live in the **[[FCT Query]] facet** (`R-query`), so the file is auditable (`/audit doc`, the on-write hook) and there's one source of truth. **Write to conform to `R-query`; don't restate it here.** Quick orientation only — five sections, fixed order, omit-if-empty:

`## Agent Resolutions` (reversible-guess records) → `## Verifications` (V-numbered; agent-run, user-judged yes/no; never "you run X") → `## Immediate Questions` (numbered handle + self-contained yes/no) → `## Questions` (catch-all `F<n> Q<m>` links) → `## Ready` (optional; backlog `[Ready]` features, for visibility).

**Every item the user answers carries a citable handle** so they can refer to it: Verifications lead with `V<n>`; Immediate Questions lead with `F<n> Q<m>` (the source feature's native number) when they route a feature-doc question, else an anchor-local `Q<n>`. The handle is bold and leads the bullet — the user answers `F176 Q1: yes`, `Q2: B`, `V1: yes`.

The skill's job below is the *procedure* that produces a conforming file.

## Determination logic — route every open question

**First, look ahead (Query PRD G6 — maximize the unblocked runway).** Before routing the questions that already exist, walk each in-scope backlog item and **anticipate** the questions its execution *will* hit — the forks, missing specs, and taste calls that would otherwise surface mid-build and stop the agent cold. Add those to the item's `## Open Questions` *now* (via `state q add` or the feature doc) so this pass surfaces them alongside everything else. The aim: once the user answers the item's pile, the agent runs it (and ideally the next items) to completion without another interruption. Then route every question — pre-existing **and** anticipated — through the ladder below; most still die in the ladder (auto-resolved / agent-run), and only the irreducible residue reaches the user.

Walk each feature's `## Open Questions` (enumerate only when **≤ 3**; if **> 3**, emit one `## Questions` link to the feature — no enumeration) plus any backlog questions. For each, pick the FIRST that applies (preference order):

> **Pending-only gate (load-bearing — the F125 failure 2026-06-16).** A "question" counts only if it is a genuinely *pending* Q-header — one that is **not** under a `### Resolved` (or `## Resolved`) sub-heading and not otherwise marked answered. A feature whose `## Open Questions` block was deleted (Phase 2) or whose Q-headers all live under `### Resolved` has **zero** open questions: it must **not** appear in `## Questions` (nor anywhere as pending). Before emitting any pending entry for a feature, confirm it has ≥1 truly-pending Q — the same set `audit-q.py`'s `extract_q_entries` returns. Listing an all-resolved feature in `## Questions` is exactly what audit-q **C35** now flags; do not author what the audit will reject.

1. **Auto-resolve → `## Agent Resolutions`** — if (a) the user would **likely notice** a wrong choice soon in the natural course of work, AND (b) it's **relatively reversible**, AND (c) the agent has a **reasonable idea** of the right answer → the agent **guesses and records** the determination. Does not ask.
2. **Do-it-yourself (don't ask)** — if the item is a check the agent **can run itself**, run the test now and answer it (or file the answering task on the backlog). Never pose a self-answerable check to the user.
3. **User-judged verification → `## Verifications`** — a check whose *judgment* needs the user. The agent still **runs** it (ahead of time + embed the result, or live-on-ready); the user only answers yes/no. Never ask the user to run anything (the §2 rule).
4. **Immediate yes/no → `## Immediate Questions`** — a real user decision. **Begin with a bold anchor-local `Q<n>` handle** (so the user answers `Q1: A`), then use the **standard expanded question format** — the same as a feature-doc `## Open Questions` item (`R-query-08` / [[DSC ask-format]]): one-line context naming the feature (as a wiki-link), each option a bold `**(A)**` sub-bullet **on its own line** (not inline), and a `- **Recommendation:**` line (may be `None`). Conforms to `R-query-08`/`R-query-13` + the shared ask-format checks (C6/C8/C9/C19/C20 + C39/C37).
5. **Catch-all → `## Questions`** — not yes/no, or > 3 per feature → a link to the feature, **always carrying its pending-Q count in bold parens**: `[[F181 — Title|F181]] **(5Q)**` (singular `**(1Q)**`). The count is mandatory — it is what tells the user "this feature needs 5 answers from me." The link text + a one-line gloss must still be **self-documenting** per North Star 2: the user reads the entry, knows what the feature is, and clicks through to the feature doc's `## Open Questions` (which holds the fully-formed, answerable questions). Reshape into 1–4 enumerated Immediate Questions first if you can; otherwise the link-with-count is the form.
6. **Actionable, but not a user question/verification → land it or make it a Ready feature (never an orphan line).** If an item is neither a question the user answers nor a check the user judges, it is **not** a queries item. Either **land it now** (small + clear) or make it a **`[Ready]` feature on the backlog** (commission one with `/feature` if none exists) — optionally surfaced in `## Ready`. A line with no yes/no and no user-judgeable artifact is forbidden: convert it to a question, a verification, an immediate landing, or a Ready feature.

## Acceptability pass — final self-check before surfacing

After writing the doc, make a final pass over **every** item you are about to surface and ask: *is this question acceptable?* — not merely well-formed (that's the format audit in step 5), but whether it should reach the user **at all**. An item that fails either criterion below must **not** be surfaced — resolve it instead.

- **Acceptability term 1 — no time/tokens-only trade-off.** A question is **not acceptable if the only thing separating the options is time or tokens.** Set cost aside and ask: ignoring time and tokens, is one choice **strictly better** than the rest — is there genuinely *no trade-off* left? If so, there is nothing for the user to decide: **spend the time/tokens and take that choice yourself.** Only surface a choice when a real trade-off *survives* discounting cost (quality-vs-quality, irreversible commitment, user preference, taste). "Quick version or thorough version?" is never acceptable — do the thorough one.
- **Acceptability term 2 — the answer must be reachable from the question.** A question is **not acceptable if the information needed to answer it is not presented in the question text or reachable through a link *in* the question.** The user must be able to answer without hunting. If a verification asks "are the diagrams in the gallery good enough?", the question **must carry a live link to that gallery** (`[[Gallery]]`, the feature doc, the exact artifact). A bare path, a name, or "see the X" the user has to go find fails this — convert every such reference into a link before surfacing.

This pass runs over the *written* document (Runbook step 4a), before the format audit (step 5). Failing term 1 sends the item back to determination-logic §1/§2 (resolve it yourself); failing term 2 is fixed in place by adding the missing link.

## Console echo

After glancing the doc, `/query` may print a few **immediate** items — resolutions made this pass, user verifications, immediate questions — to the console in the **inline-ask format** ([[SKL ask-inline]]): one context line + a ≤2-line ask. **Invariant:** anything echoed is also in the document (console = dispatch view; doc = store).

## Runbook

> **⚠ The `{NAME} queries.md` DOCUMENT is now mechanically rendered — do NOT hand-author it** (per user direction 2026-06-26: *"purely mechanical, done as part of triage"*). `triage-section.py` rewrites the whole page from backlog state on every `/triage` (banner H1 + `## Verifications` from `[Verify*]`/`[Watching*]` rows + `## Ready` from `[Ready]`/`[Active]` rows with their `Next:` + `## Questions` from `[Questions]` rows). Anything you write into that file by hand is overwritten on the next triage. `/query`'s job is **determination, not authoring**: route each open question to its *source* (resolve it in the feature doc's `## Open Questions`, file/edit a backlog row, run a self-answerable check) — the mechanical render then surfaces it. To change what the queries page shows, **edit the backlog rows / feature-doc Open Questions**, not `queries.md`. (The legacy four-section hand-authoring + `_computed_` H1 below is superseded; kept for the determination-logic reference.)

1. **Locate the anchor** (walk up to `.anchor`). The queries page lives at `{NAME} Track/{NAME} queries.md` and is produced by the mechanical render (above) — you do not create or format it here.
2. **Collect** open questions: each feature doc's `## Open Questions` (≤3 enumerate / >3 link) + backlog questions.
3. **Route** each via the determination logic. For auto-resolves, make the guess and (where it shapes a doc) apply it. For do-it-yourself checks, run them now / backlog them.
4. **Write** the four sections in order, each item in its section's format (per `R-query`). Verifications are compact: `**V<n>` + a bold yes/no. Immediate Questions use the standard expanded format: `**Q<n>` opener + options as own-line `**(A)**` sub-bullets + a `- **Recommendation:**` line. Catch-all questions are `F<n> Q<m>` links. Any `F<n>` a bullet names is a wiki-link (feature doc, else `[[{NAME} Backlog#^F<n>|F<n>]]`).
4a. **Acceptability pass — final self-check (§ Acceptability pass).** Before the format audit, walk every item you are about to surface and apply the two acceptability terms: (1) **no time/tokens-only trade-off** — if cost is the only thing separating the options, there is nothing to ask; spend the time/tokens and decide it yourself. (2) **answer reachable from the question** — the information to answer must be in the question text or behind a link *in* the question (a "is the gallery good enough?" verification must carry a live `[[Gallery]]` / artifact link). Send term-1 failures back to determination-logic §1/§2 (resolve yourself); fix term-2 failures in place by adding the missing link.
5. **Audit the file before surfacing it — MANDATORY** (the F125 lesson: the C35 check only protects you if `/query` actually *runs* it). The on-write hook covers markdown/format on the Write, but the cross-doc consistency checks (C35 stale-pending, C6/C9 Q-format, C36 link-not-backtick) live in `audit-q.py` and are **not** triggered by writing the file — run them explicitly:
   ```bash
   python3 ~/.claude/skills/audit/scripts/audit-q.py --scope backlog --anchor {NAME} --dry
   ```
   **Fix every finding at its source, then re-run until the `{NAME} queries.md` line count is 0.** A C35 ("lists `F<n>` under ## Questions but its linked doc has no pending Qs") means you violated the pending-only gate — remove that entry. Do **not** proceed to the Q.md refresh or the glance with a dirty audit; surfacing a broken queries file is the exact failure this step exists to prevent.
6. **Refresh the Q.md dashboard** — after writing `{NAME} queries.md`, paste it into the vault Q.md so the anchor's per-anchor section shows the freshly-computed queries body (not stale state):
   ```bash
   python3 ~/.claude/skills/triage/scripts/triage-section.py {NAME}
   ```
   `triage-section.py` reads `{NAME} queries.md`, strips its frontmatter + H1, and renders the Q.md section as `<count banner → links to queries.md>` + `_queries computed <timestamp>_` + the queries body. (This is the F176 model — Q.md per-anchor body **is** the queries paste, replacing the legacy backlog-row/ask dump. Anchors with no `queries.md` fall back to the backlog-derived body.)
7. **Glance** `{NAME} queries.md` (`open "<path>"`).
8. **Echo** (optional) a few immediate items to the console in inline-ask format — all also in the doc.
9. **On answer** (`Q1: yes`, `F115 Q3: A`, "verified the panel reopen", prose): record the resolution at the question's home and **trim** the answered item from `{NAME} queries.md`. Re-running `/query` rebuilds from current state, so the doc shrinks monotonically. Sticky context: once the user names a feature, bare `Q<n>` targets it.

## Parented mode — `/query --doc <path> <q1> [<q2> …]`

The secondary invocation, called from another skill's runbook (`/feature`, `/code plan`, `/groom`, `/design`) when it has decisions to park in a *specific* document. It authors numbered, ask-format questions directly into `<path>`'s `## Open Questions` block (created **above the H1** — between frontmatter and H1 — if absent, per the placement rule) and does **not** build the anchor's `queries.md` — the Qs surface there on the next bare `/query` pass via the determination logic.

- **Mechanism:** resolve `<path>` to its feature/PRD doc, then delegate to `state q add` (which enforces the ask-format spec — block-IDs, `Q<n>` numbering, recommendation strength, Phase 1/2/3 lifecycle):
  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} q add F<n> < q-body.md
  ```
- **Multiple questions** are batched — numbered in one pass, never trickled.
- **Glance** the doc only in active mode (the user is engaging now); skip the glance in parking mode (batch filing for later). Mirrors `/feature` § 1a.
- This is the successor to `/ask --doc`; the question *format* discipline is unchanged — it still lives in [[DSC ask-format]], which `/query` cites.

## Boundaries

`/query` only asks, records, and trims. The cross-anchor dashboard (`[[Q]]`), `[Verify]`-row surfacing, and banner/TAG rendering belong to `/triage`. Never write an unanswerable item: if it can't be made a concrete decision/verification, the agent decides it (reversible → guess + record) or does the work that resolves it.
