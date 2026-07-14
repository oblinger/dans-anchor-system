---
name: ask
description: >
  The system for NOT asking the user questions piecemeal. Prime directive:
  ELIMINATE every question the agent can (auto-resolve reversible/soon-visible
  guesses, run checks itself, decide low-stakes/visible calls, infer from the
  codebase), then CONSOLIDATE the irreducible residue into one self-documenting,
  counted, one-shot-answerable pile in the anchor's `{slug} queries.md` (sections
  Agent Resolutions / Verifications / Immediate Questions / Questions). The doc is
  the always-current STORE of open questions — write every question there the
  moment it is raised; chat is at most a VIEW, never carrying a question the doc
  lacks (the user runs many agents; chat scrolls away). Glance the doc and trim
  answered items. Use when the user runs /ask or an agent has a decision to
  route. Per F169 + [[Query PRD]].
tools: Read, Write, Edit, Bash, Glob
user_invocable: true
---

# /ask — ask the user questions
requires:: vault, anchor-cli, skill:audit, facet:query

`/ask` builds and maintains the anchor's **`{slug} queries.md`** — the single surface where the user answers everything the agents need from them. Its discipline: most "questions" should never reach the user; only genuine user decisions and genuine user-only verifications survive, each made answerable from what's written. **Authoritative purpose + the never-ask invariant: [[Query PRD]]** (the agent's prime directive is to NOT ask — eliminate every question it can, consolidate the irreducible residue into one self-documenting, one-shot-answerable pile; asking in chat, especially after a render, is the cardinal violation). Full spec: [[F169 — Query skill — queries document + determination logic|F169]]. Replaces `/ask` (which rotted by accreting dashboard + render-pipeline + triage coupling — keep `/ask` narrow).

> ## ⚠️ TWO NORTH STARS — NON-NEGOTIABLE
>
> **1. The queries doc is the always-current STORE of open questions — chat is at most a VIEW of it.**
> `{slug} queries.md` holds the anchor's open questions *at all times*. **The moment you have a question for the user, write it into the doc — at that same moment** (run the determination logic, write the survivors), and *then* you may optionally echo a spotlight to chat. Chat may point *into* the doc, but it **never carries a question the doc doesn't**, and **the doc is never behind chat**. A chat question with no corresponding doc entry means the question was *not actually asked* — redo it through the doc. Why this is non-negotiable: the user runs **many agents at once** and **chat scrolls away**; `queries.md` is the one place they can always return to for the latest open questions. (The doc may legitimately lag only during live back-and-forth before the next render; every render — and every question raised — re-syncs it. This is the recurring failure the user has called out: agents ask in chat and never touch the doc. Treat a bare chat-ask as a bug in your own behavior.)
>
> **2. Every surfaced question is SELF-DOCUMENTING.** Reading the entry *alone*, the user must (a) know exactly **what is being asked**, and (b) have **everything needed to answer it** — either stated in the entry or reachable through a link *in* the entry. If answering requires the user to go hunt for context that isn't linked, the entry fails. And every entry that routes a feature's open questions **states its pending-Q count in bold parens** — `[[F181 — …|F181]] **(5Q)**` — so the user sees at a glance how many answers that feature needs from them.
>
> **3. 🚨 HARD REQUIREMENT — EVERY ARTIFACT YOU NAME, YOU LINK. NO EXCEPTIONS.** If a surfaced question or verification tells the user to *open / look at / skim / check* a doc, file, template, folder, gallery, report, or section, that artifact **MUST appear as a live `[[wiki-link]]`** (or a clickable URL) — right there in the item. **It is illegal to name a thing the user should look at and not link it.** Bare text (`DAS PRD`, `traits/Drive`), a code-span filename (`` `_Disk {{LABEL}} Template.md` ``), a bare path, or "see the X" all **fail** — the user cannot click a name. Author the source so the reference is `[[DAS PRD]]`, `[[Drive|traits/Drive]]`, `[[_Disk {{LABEL}} Template]]`. This generalizes rule-2: an unlinked artifact reference is *never* self-documenting, because "answerable without hunting" requires the link to be *in the item*. Enforced mechanically — audit-q **C42** (`R-query-15`) flags any answerable item that names a resolvable doc in bare text or a code-span filename. The failure this exists to kill: surfacing "open DAS PRD, DAS Decisions" and making the user go find them.

## The question bar — every surfaced question carries FIVE things

A question that reaches the user must let them answer it **in one shot**. Every Verification / Immediate Question / Questions entry carries all five — miss one and it is a defect the audit flags:

1. **Its work-item identifier** — the `[[F<n>]]` (feature) / `[[T<n>]]` (task) / `[[M<n>]]` (milestone) handle the question belongs to, as a wiki-link, so the user knows *which task* is asking. (Enforced: `R-query-13` / audit-q **C37**.)
2. **A specific question** — the concrete fork being decided or assessed, not a vague gesture. If it's about the *behavior/performance* of something, name the exact thing being assessed.
3. **Labeled options** — `**(A)** / **(B)** / **(C)**`, each on its own line. (Enforced: **C19**.)
4. **A recommendation** — `Lean (A)` / `Strong (B)` / `None`, always present. (Enforced: **C9**.)
5. **Direct wiki-links to every artifact** the user must look at to answer — the link is *in* the question (North Star 3). (Enforced: **C42** / `R-query-15`.)

**Anti-pattern (real — Warden, 2026-07-05).** A `## Questions` entry reading:

> Design-rules — **mined + drafted 2026-07-05, awaiting review** Q3 (which families upgrade?) is the one pending question…

fails all five: **no** work-item handle (what task is "Design-rules"?), **no** link to where `Q3` actually lives, **no** specific ask, **no** labeled options, **no** recommendation, **no** artifact links. A failure all the way around — exactly what this bar exists to prevent. The fix lives at the source (the backlog row / feature-doc `## Open Questions`), never in the rendered `queries.md`.

## The document — `{slug} queries.md` in `{slug} Track/`

The file's validity rules — sections + order, what each item must look like, the no-user-imperative and no-orphan invariants — live in the **[[DAS Query]] facet** (`R-query`), so the file is auditable (`/audit doc`, the on-write hook) and there's one source of truth. **Write to conform to `R-query`; don't restate it here.** Quick orientation only — five sections, fixed order, omit-if-empty:

`## Agent Resolutions` (reversible-guess records) → `## Verifications` (V-numbered; agent-run, user-judged yes/no; never "you run X") → `## Immediate Questions` (numbered handle + self-contained yes/no) → `## Questions` (catch-all `F<n> Q<m>` links) → `## Ready` (optional; backlog `[Ready]` features, for visibility).

**Every item the user answers carries a citable handle** so they can refer to it: Verifications lead with `V<n>`; Immediate Questions lead with `F<n> Q<m>` (the source feature's native number) when they route a feature-doc question, else an anchor-local `Q<n>`. The handle is bold and leads the bullet — the user answers `F176 Q1: yes`, `Q2: B`, `V1: yes`.

The skill's job below is the *procedure* that produces a conforming file.

## Determination logic — route every open question

**First, look ahead (Query PRD G6 — maximize the unblocked runway).** Before routing the questions that already exist, walk each **frontier** item — the tasks that could be next for execution: `## Ready` / `## Now` / `## Next` rows plus the next unmet roadmap milestone (per [[Query PRD]] § The groom frontier, F228; `## Later` and the icebox don't drive anticipation) — and **anticipate** the questions its execution *will* hit — the forks, missing specs, and taste calls that would otherwise surface mid-build and stop the agent cold. Add those to the item's `## Open Questions` *now* (via `state "<feature doc>" Q+ define` or the feature doc) so this pass surfaces them alongside everything else. The aim: once the user answers the item's pile, the agent runs it (and ideally the next items) to completion without another interruption. Then route every question — pre-existing **and** anticipated — through the ladder below; most still die in the ladder (auto-resolved / agent-run), and only the irreducible residue reaches the user.

Walk each feature's `## Open Questions` plus any backlog questions. A feature's questions may be enumerated individually or carried as one `## Questions` link to the feature with its bold `**(nQ)**` count — agent's judgment (enumerate when few, link when many) — but **the choice of form never affects whether a question is in the queue file: every pending question is reachable from it, always, regardless of count.** For each question, pick the FIRST that applies (preference order):

> **Pending-only gate (load-bearing — the F125 failure 2026-06-16).** A "question" counts only if it is a genuinely *pending* Q-header — one that is **not** under a `### Resolved` (or `## Resolved`) sub-heading and not otherwise marked answered. A feature whose `## Open Questions` block was deleted (Phase 2) or whose Q-headers all live under `### Resolved` has **zero** open questions: it must **not** appear in `## Questions` (nor anywhere as pending). Before emitting any pending entry for a feature, confirm it has ≥1 truly-pending Q — the same set `audit-q.py`'s `extract_q_entries` returns. Listing an all-resolved feature in `## Questions` is exactly what audit-q **C35** now flags; do not author what the audit will reject.

1. **Auto-resolve → `## Agent Resolutions`** — if (a) the user would **likely notice** a wrong choice soon in the natural course of work, AND (b) it's **relatively reversible**, AND (c) the agent has a **reasonable idea** of the right answer → the agent **guesses and records** the determination. Does not ask.
2. **Do-it-yourself (don't ask)** — if the item is a check the agent **can run itself**, run the test now and answer it (or file the answering task on the backlog). Never pose a self-answerable check to the user.
3. **User-judged verification → `## Verifications`** — a check whose *judgment* needs the user. The agent still **runs** it (ahead of time + embed the result, or live-on-ready); the user only answers yes/no. Never ask the user to run anything (the §2 rule).
4. **Immediate yes/no → `## Immediate Questions`** — a real user decision. **Begin with a bold anchor-local `Q<n>` handle** (so the user answers `Q1: A`), then use the **standard expanded question format** — the same as a feature-doc `## Open Questions` item (`R-query-08` / [[DAS ask-format]]): one-line context naming the feature (as a wiki-link), each option a bold `**(A)**` sub-bullet **on its own line** (not inline), and a `- **Recommendation:**` line (may be `None`). Conforms to `R-query-08`/`R-query-13` + the shared ask-format checks (C6/C8/C9/C19/C20 + C39/C37).
5. **Catch-all → `## Questions`** — not yes/no, or too many to enumerate cleanly → a link to the feature, **always carrying its pending-Q count in bold parens**: `[[F181 — Title|F181]] **(5Q)**` (singular `**(1Q)**`). The count is mandatory — it is what tells the user "this feature needs 5 answers from me." The link text + a one-line gloss must still be **self-documenting** per North Star 2: the user reads the entry, knows what the feature is, and clicks through to the feature doc's `## Open Questions` (which holds the fully-formed, answerable questions). Reshape into 1–4 enumerated Immediate Questions first if you can; otherwise the link-with-count is the form.
6. **Actionable, but not a user question/verification → land it or make it a Ready feature (never an orphan line).** If an item is neither a question the user answers nor a check the user judges, it is **not** a queries item. Either **land it now** (small + clear) or make it a **`[Ready]` feature on the backlog** (commission one with `/feature` if none exists) — optionally surfaced in `## Ready`. A line with no yes/no and no user-judgeable artifact is forbidden: convert it to a question, a verification, an immediate landing, or a Ready feature.

## Acceptability pass — final self-check before surfacing

After writing the doc, make a final pass over **every** item you are about to surface and ask: *is this question acceptable?* — not merely well-formed (that's the format audit in step 5), but whether it should reach the user **at all**. An item that fails either criterion below must **not** be surfaced — resolve it instead.

- **Acceptability term 1 — no time/tokens-only trade-off.** A question is **not acceptable if the only thing separating the options is time or tokens.** Set cost aside and ask: ignoring time and tokens, is one choice **strictly better** than the rest — is there genuinely *no trade-off* left? If so, there is nothing for the user to decide: **spend the time/tokens and take that choice yourself.** Only surface a choice when a real trade-off *survives* discounting cost (quality-vs-quality, irreversible commitment, user preference, taste). "Quick version or thorough version?" is never acceptable — do the thorough one.
- **Acceptability term 2 — the answer must be reachable from the question (North Star 3 — every named artifact is a live link).** A question is **not acceptable if the information needed to answer it is not presented in the question text or reachable through a link *in* the question.** The user must be able to answer without hunting. If a verification asks "are the diagrams in the gallery good enough?", the question **must carry a live link to that gallery** (`[[Gallery]]`, the feature doc, the exact artifact). **Every doc/file/template/report/section the item names MUST be a `[[wiki-link]]`** — a bare name (`DAS PRD`), a bare path (`traits/Drive`), a code-span filename (`` `_Disk {{LABEL}} Template.md` ``), or "see the X" all fail; convert every such reference into a link before surfacing. This is a HARD requirement, enforced by audit-q **C42** / `R-query-15` — a dirty C42 on step 5 means an artifact reached the user unlinked; fix it at the source (the backlog `- **Verify:**` line / question body) and re-render, never edit the rendered `queries.md`.

This pass runs over the *written* document (Runbook step 4a), before the format audit (step 5). Failing term 1 sends the item back to determination-logic §1/§2 (resolve it yourself); failing term 2 is fixed in place by adding the missing link.

## Console echo

After glancing the doc, `/ask` may print a few **immediate** items — resolutions made this pass, user verifications, immediate questions — to the console in the **inline-ask format** ([[DAS ask-inline]]): one context line + a ≤2-line ask. **Invariant:** anything echoed is also in the document (console = dispatch view; doc = store).

## Runbook

> **⚠ The `{slug} queries.md` DOCUMENT is now mechanically rendered — do NOT hand-author it** (per user direction 2026-06-26: *"purely mechanical"*). `queries-render.py` rebuilds the whole page from backlog state on every `state` mutation (via `audit-q --fix`): banner H1 + `## Verifications` from `[Verify*]`/`[Watching*]` rows + `## Ready` from `[Ready]`/`[Active]` rows with their `Next:` + `## Questions` from `[Questions]` rows — and copies that body into the anchor's `Q.md` section (F231). Anything you write into that file by hand is overwritten on the next render. `/ask`'s job is **determination, not authoring**: route each open question to its *source* (resolve it in the feature doc's `## Open Questions`, file/edit a backlog row, run a self-answerable check) — the mechanical render then surfaces it. To change what the queries page shows, **edit the backlog rows / feature-doc Open Questions**, not `queries.md`. (The legacy four-section hand-authoring + `_computed_` H1 below is superseded; kept for the determination-logic reference.)

1. **Locate the anchor** (walk up to `.anchor`). The queries page lives at `{slug} Track/{slug} queries.md` and is produced by the mechanical render (above) — you do not create or format it here.
2. **Collect** open questions: each feature doc's `## Open Questions` (enumerate or link-with-count, agent's judgment — every pending Q reachable from the queue file either way) + backlog questions.
3. **Route** each via the determination logic. For auto-resolves, make the guess and (where it shapes a doc) apply it. For do-it-yourself checks, run them now / backlog them.
4. **Write** the four sections in order, each item in its section's format (per `R-query`). Verifications are compact: `**V<n>` + a bold yes/no. Immediate Questions use the standard expanded format: `**Q<n>` opener + options as own-line `**(A)**` sub-bullets + a `- **Recommendation:**` line. Catch-all questions are `F<n> Q<m>` links. Any `F<n>` a bullet names is a wiki-link (feature doc, else `[[{slug} Backlog#^F<n>|F<n>]]`).
4a. **Acceptability pass — final self-check (§ Acceptability pass).** Before the format audit, walk every item you are about to surface and apply the two acceptability terms: (1) **no time/tokens-only trade-off** — if cost is the only thing separating the options, there is nothing to ask; spend the time/tokens and decide it yourself. (2) **answer reachable from the question** — the information to answer must be in the question text or behind a link *in* the question (a "is the gallery good enough?" verification must carry a live `[[Gallery]]` / artifact link). Send term-1 failures back to determination-logic §1/§2 (resolve yourself); fix term-2 failures in place by adding the missing link.
5. **Audit the file before surfacing it — MANDATORY** (the F125 lesson: the C35 check only protects you if `/ask` actually *runs* it). The on-write hook covers markdown/format on the Write, but the cross-doc consistency checks (C35 stale-pending, C6/C9 Q-format, C36 link-not-backtick) live in `audit-q.py` and are **not** triggered by writing the file — run them explicitly:
   ```bash
   python3 ~/.claude/skills/audit/scripts/audit-q.py --scope backlog --anchor {slug} --dry
   ```
   **Fix every finding at its source, then re-run until the `{slug} queries.md` line count is 0.** A C35 ("lists `F<n>` under ## Questions but its linked doc has no pending Qs") means you violated the pending-only gate — remove that entry. Do **not** proceed to the Q.md refresh or the glance with a dirty audit; surfacing a broken queries file is the exact failure this step exists to prevent.
6. **Regenerate the queries file + Q.md** — after routing questions to their sources (backlog rows / feature-doc Open Questions), render:
   ```bash
   python3 ~/.claude/skills/audit/scripts/queries-render.py {slug}
   ```
   `queries-render.py` rebuilds `{slug} queries.md` from backlog state (banner H1 + `## Verifications` / `## Ready`+Next / `## Questions`) **and copies that same body into the anchor's `Q.md` section** under the queue-file banner (F231 — the query file IS the queue-file content; one render, two destinations, no separate triage view). Every `state` mutation already triggers this via `audit-q --fix`, so an explicit call is only needed when you edited sources without going through `state`.
7. **Glance** `{slug} queries.md` (`open "<path>"`).
8. **Echo** (optional) a few immediate items to the console in inline-ask format — all also in the doc.
9. **On answer** (`Q1: yes`, `F115 Q3: A`, "verified the panel reopen", prose): record the resolution at the question's home and **trim** the answered item from `{slug} queries.md`. Re-running `/ask` rebuilds from current state, so the doc shrinks monotonically. Sticky context: once the user names a feature, bare `Q<n>` targets it.

## Parented mode — `/ask --doc <path> <q1> [<q2> …]`

The secondary invocation, called from another skill's runbook (`/feature`, `/code plan`, `/groom`, `/design`) when it has decisions to park in a *specific* document. It authors numbered, ask-format questions directly into `<path>`'s `## Open Questions` block (created **above the H1** — between frontmatter and H1 — if absent, per the placement rule) and does **not** build the anchor's `queries.md` — the Qs surface there on the next bare `/ask` pass via the determination logic.

- **Mechanism:** resolve `<path>` to its feature/PRD doc, then delegate to the state CLI's `Q+ define` (which enforces the ask-format spec — block-IDs, `Q<n>` numbering, recommendation strength, Phase 1/2/3 lifecycle):
  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {slug} "F<n> — <Title>" Q+ define < q-body.md
  ```
- **Multiple questions** are batched — numbered in one pass, never trickled.
- **Glance** the doc only in active mode (the user is engaging now); skip the glance in parking mode (batch filing for later). Mirrors `/feature` § 1a.
- This is the successor to `/ask --doc`; the question *format* discipline is unchanged — it still lives in [[DAS ask-format]], which `/ask` cites.

## Boundaries

`/ask` only asks, records, and trims. The mechanical render — banner/TAG, `[Verify]`-row surfacing, and copying the queries body into the cross-anchor dashboard (`[[Q]]`) — belongs to `queries-render.py` (driven by `state`/`audit-q --fix`), not to `/ask`. Never write an unanswerable item: if it can't be made a concrete decision/verification, the agent decides it (reversible → guess + record) or does the work that resolves it.
