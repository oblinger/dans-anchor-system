---
description: "product requirements"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [Query PRD](hook://p/Query%20PRD)
# Query PRD


**Scope — this is the shared design doc for the whole resolution layer: both `/groom` (frontier planning + backlog states) and `/ask` (determination + consolidation).** They are deliberately kept in one PRD, not two: they are one system, and the frontier, the F/T/M work-item-identity model, the question bar, and the never-ask discipline are all *shared* — a single home keeps them from drifting. The two *skills* stay separate runbooks (`groom SKILL.md` / `query SKILL.md`, so groom can be called alone); this one PRD governs both. (Named "Query PRD" for link stability; read it as the resolution-layer PRD.)

## Overview

`/ask` exists for one reason: **so the agent does not interrupt the user with questions.** Every question put to the user is a cost — it fragments their attention, arrives out of context, and scrolls away. The agent's prime directive is to **resolve, decide, and verify on its own**; and for the small irreducible residue that *genuinely* needs the user, to **consolidate it into one place, fully prepared**, so the user answers everything in a single pass — *bam, bam, bam, down the list* — instead of being dribbled questions one at a time across a conversation.

**`{NAME} queries.md` is the always-current store of open questions; chat is at most a view of it.** The doc holds the anchor's open questions *at all times*, and the moment any question is raised — whenever that happens — it is written there **simultaneously**. A question may be *spotlighted* in chat, but **only if it is also in the doc at that same moment**: chat never carries a question the doc doesn't, and the doc is never behind chat. The cardinal violation is a chat question with **no corresponding queries-doc entry** — because chat **scrolls away** (the user runs many agents at once) and the question is then lost, whereas `queries.md` is the one place the user can always return to for the latest open questions. *After any render especially*, don't fragment the freshly-built pile with loose chat questions — the pile *in the doc* is the surface; any chat line is a pointer into it. (The doc legitimately lags only during live back-and-forth before the next render; the target is always-current.)

**And the goal is not merely *fewer* interruptions — it is the longest possible *unblocked runway* between them.** Query does not only surface the questions that exist *right now*; it **looks ahead**. For each backlog item it proactively reasons about the decisions execution *will* hit — the forks, the missing specs, the taste calls that surface only once you start building — and surfaces those **early**, in the same pile, *before* they block anything. The metric query optimizes is **work-done-per-answered-pile**: how far the agent can execute after the user answers one round of questions before it is forced to stop and ask again. Front-loading every foreseeable question for an item means that once its pile is answered, the agent runs that item to completion — and ideally the *next* items too — without another interruption. This is the backlog-wide generalization of "Ready means ready: ask **all** implementation questions upfront."

`/ask` is the **resolution + consolidation** half of the query machine; `queries-render.py` is the mechanical **render** half. Together with `/groom` they form one autonomous loop that grooms, resolves, piles, and presents — and never asks.

## Goals

- **G1 — Eliminate.** Drive the open-question count toward zero by the agent's own effort. Every open question runs the full determination ladder *to exhaustion* before any of it reaches the user: auto-resolve reversible/soon-visible guesses (and record them); run every check the agent can run itself and answer it; decide the low-stakes / visible / reversible calls (assume-and-announce); infer from context and the codebase. A question survives to the user **only** when it genuinely needs *user judgment* AND is high-stakes / irreversible / a matter of taste the agent has no basis to pick. Most "questions" die here — that is the point. "I could resolve this myself but it's easier to ask" is a violation.
- **G2 — Consolidate.** The survivors land in `{NAME} queries.md`: one pile, each entry **self-documenting** (answerable from the entry text + the links *inside* it, nothing to hunt for), each carrying its **pending-Q count** (`[[F181 …]] **(5Q)**`), ordered so the user rips through the whole stack in one sitting. Everything they need has been lined up in advance.
- **G3 — The doc is the store; chat never leads it (R1).** Every question is written into `{NAME} queries.md` the moment it is raised (simultaneously, not deferred to the next render). Chat may *spotlight* a question but never carries one the doc lacks — chat is a view, the doc is the source of truth, and the doc is never stale relative to chat. A chat question with no doc entry is the violation: it scrolls away and the user (running many agents) loses it.
- **G4 — The resolution + render pipeline is bulletproof (R5).** `/groom` (top-level) runs the resolution layer (frontier planning + backlog states), and — because `queries-render.py` fires automatically on every `state` mutation — the render is always current by the time it exits; it glances the result — fully autonomously — and ends with a **status report, never a question (R6).**
- **G5 — One-shot answerable (R3/R4).** The user can answer the entire pile in one pass without opening any other document to understand a question.
- **G6 — Maximize the unblocked runway (anticipatory surfacing).** Don't only surface the questions you have *now* — **look ahead**: for each **frontier** item (§ The groom frontier), proactively reason about the decisions execution *will* hit and surface those *early*, in the same pile, before they block anything. The optimization target is **work-done-per-answered-pile** — the stretch of autonomous work one answering pass buys before the next forced question. Front-load every foreseeable question per item so that answering its pile runs the item (and ideally the next ones) to completion uninterrupted.

## Groom's three activities

`/groom` is the resolution layer's planner. It does three things, in order, and the rest of this PRD elaborates them:

1. **Work-item identity** — guarantee every tracked activity has a unique handle on the backlog/roadmap (below).
2. **Identify the executable frontier** — the tasks that could be next for execution (§ The groom frontier).
3. **Groom the frontier** — plan each frontier item to one of three known exit states: executable (with next steps), questioned (enumerated), or blocked (named) (§ Grooming the frontier).

## Work-item identity — every activity has a handle (activity 1)

**No tracked work is anonymous.** Before anything else, groom ensures every piece of work resolves to a unique identifier that lives on the backlog or roadmap:

- **`F<n>` — a feature.** Backed by a feature doc under `{NAME} Design/{NAME} Features/`; the backlog row links to it. `F` numbers are monotonic, never reused.
- **`T<n>` — a task.** A unit of work with **no** feature doc — the backlog row *is* the spec. A task usually *operates on other documents*; its body carries wiki-links to the design-doc sections / files / artifacts it acts on. `T<n>` is unique on the backlog, monotonic and never reused, and is the referent for every mention of the work (questions, `Q.md`, cross-links).
- **`M-<Name>…` — a roadmap entry.** A *nested* item in `{NAME} Roadmap.md` (per [[DAS Roadmap]]); its handle is `M-<Name>.<path>`, where the name-path already encodes its position in the tree. Entries nest; the roadmap is a hierarchy.
- **`R…` — a roadmap task.** A backlog commitment to **execute a roadmap entry**. On the backlog the reference is **flat**: it points at one entry — a **leaf** entry (the usual case: "do this item") or a **non-leaf** entry ("do the whole subtree"). Its handle is `R` + the entry's identifier (e.g. `R-CLI.3.5`).

**Names are identity; order is document position, never a stored number.** A roadmap entry is resolved on its **name-path** — its ordering is simply its position in the roadmap file (a display ordinal, if shown, is *computed* from that position, never written into a handle). So there is no number to go stale: inserting/reordering entries shifts positions automatically, and every reference (sub-entries, backlog `R` tasks, done-logs, cross-links) keeps resolving because it's keyed on the name. Only **renaming** an entry forces a sweep (far rarer than reorder/insert). This is why `R` task handles are word-only (`R-CLI.3.5`), not numbered. Full convention: [[DAS Roadmap]] § Names are identity.

The identity is *achieved by linking*: a row links to its feature doc (`F<n>`), is itself the task record (`T<n>`), or references a roadmap entry (`R…`, leaf or non-leaf). A feature doc unlinked from the backlog/roadmap has no place in the system — groom gives it one rather than leaving an orphan. This is why every question can (and must) name its work-item handle: the handle exists first. (Numbering policy for `F`/`T`/`M`/`R` lives in the [[DAS Backlog|FCT Backlog]] facet + [[DAS Roadmap]]; the `state` mint is the source of new handles.)

## The groom frontier (activity 2)

**The frontier is the set of tasks that could be next for execution** (defined 2026-07-05, [[F228 — Groom frontier — groom plans the frontier to Ready; query asks about it|F228]]): rows in the backlog's **`## Now` or `## Next` horizons** (plus `## Active` / `## Ready`, which are already past it), **feature docs linked from a Now/Next row**, and items **soon on the relevant roadmaps** — the next unmet milestone of `{NAME} Roadmap.md` when the anchor has one, *a milestone that could plausibly be executed soon if fully specified*. `## Later` and the icebox are *not* frontier; they are touched only on explicit invocation (`/groom later`, `/groom icebox`).

The frontier is the shared scope of the resolution layer:

- **`/groom` plans the frontier to Ready.** Its purpose is to get every frontier task **fully ready to be executed** — investigate, draft the approach, declare the `- **Next:**` step, promote to `[Ready]` when the Definition of Ready holds; when it doesn't, file the blocking questions (or the honest `[Blocked]`/`[Waiting]`/`[Watching]` state) so the obstacle is named. A frontier row left unplanned and unbracketed is groom's unfinished work.
- **`/ask` asks about the frontier.** The determination ladder and the G6 look-ahead walk frontier tasks — the pile the user answers is exactly what unblocks the next stretch of execution. (Non-frontier `[Questions]`/`[Verify]` brackets still render per the render rules; they just don't drive anticipatory question-mining.)
- **The audit checks it.** The frontier invariants are encoded as the `R-backlog` ruleset in the [[DAS Backlog|FCT Backlog]] facet (frontier rows planned + bracket-resolved; Verify rows carry a concrete question), fired by the rule engine at doc-audit.

## Grooming the frontier (activity 3)

Grooming a frontier item means **planning it out until you know, as concretely as possible, how you would execute it** — then recording that knowledge as one of **five explicit groomed states**, each with a body contract enforced by a checked `R-backlog` rule (canonical table: [[DAS Backlog|FCT Backlog]] § The groomed states). Groom never leaves a frontier item in an unknown state:

- **Executable** (`[Ready]`/`[Active]`) → the row declares a concrete `- **Next:**` step the agent takes with zero user involvement (R-backlog-02).
- **Questions** (`[Questions]`) → the questions are **enumerated** and reachable from the row — inline numbered `Q<n>` or a `→ [[Feature Doc]]` link — each satisfying the question bar below (R-backlog-05 + the R-query rules).
- **Blocked / Waiting** (`[Blocked …]` / `[Waiting …]`) → the row names **specifically what it is blocked on / awaiting** (`[Blocked F<NNN>]` exempt); timed forms carry an absolute `YYYY-MM-DD` (R-backlog-06 / R-backlog-07).
- **Verify** (`[Verify]`) → the row declares a `- **Verify:**` concrete yes/no the user answers from where they sit (R-backlog-04).
- **Watching** (`[Watching …]`) → a `- **Verify:**` non-recurrence question plus the absolute soak-expiry date (R-backlog-04 / R-backlog-07).

A frontier row must not rest in transient `[Designing]` after a groom, and a vague blocker/verify is not a groomed state. `/ask` surfaces the residue of states 2 (Questions) and 4/5 (Verify/Watching) — the question bar is the Questions-state contract.

**The question bar — every parked question satisfies all five (else it is a defect the audit flags).** This is what makes the pile one-shot answerable (G2/G5). Each question carries:

1. **its work-item identifier** — the `[[F<n>]]` / `[[T<n>]]` / `[[M<n>]]` handle it belongs to (`R-query-13` / C37);
2. **a specific question** — the concrete decision/assessment, naming the exact thing being judged;
3. **labeled options** `**(A)** / **(B)** / **(C)**`, each on its own line (C19);
4. **a recommendation** — `Lean`/`Strong`/`None`, always present (C9);
5. **direct wiki-links to every artifact** the user must look at to answer (C42 / `R-query-15`).

The recurring failure this bar kills (real, Warden 2026-07-05): a `## Questions` entry — *"Design-rules — … Q3 (which families upgrade?) …"* — with no work-item handle, no link to where `Q3` lives, no specific ask, no options, no recommendation, no artifact links. A failure all the way around.

## Non-Goals

- **Not a dashboard / status renderer.** Painting `Q.md` and the queries-doc body is `queries-render.py`'s mechanical job. `/ask`'s job is *determination* — deciding what dies and what survives — not formatting.
- **Chat is not the store.** Chat is a *view*, never the source of truth — `/ask` never raises a question in chat without writing it to the doc at the same moment, so the doc is never behind chat. (A chat *spotlight* that points into the doc is fine; a chat question the doc lacks is the violation. A creation-time inline yes/no the user is actively engaged in *that instant* — e.g. `/feature`'s title-collision prompt — is owned by the invoking skill, not query, and is still mirrored to the doc if it defers.)
- **Not an agent action-log.** `## Agent Resolutions` records reversible *guesses*, not a diary of edits the agent made (per the durable feedback rule).
- **Not a place to defer work the agent could do.** If an item is actionable-but-not-a-user-question, the agent lands it or files it as a `[Ready]` feature — it never becomes an orphan "question."

## User Stories

- **US1 — Don't interrupt me.** *As the user, I want the agent to figure out everything it possibly can on its own, so that I am not pulled into a conversation for things the agent could have decided, run, or inferred itself.*
- **US2 — One shot, zero hunting.** *As the user, when I do turn my attention to the pile, I want every question lined up with all the context I need to answer it right there, so I can go down the whole list and answer them all in one sitting — bam, bam, bam — without opening other docs.*
- **US3 — One pile, counted.** *As the user, I want all residual questions in one place with a count per feature, so I know exactly how much input is being asked of me at a glance.*
- **US4 — The bulletproof button never asks.** *As the user, after I run `/groom`, I want a status report — what was groomed, what was resolved, how many questions remain in the doc — and NOT a question in chat, because a chat question fragments the pile the render exists to consolidate.*
- **US5 — Front-load so my answers go far.** *As the user, when I answer the pile, I want to unblock the maximum amount of work — so I want the agent to have thought ahead about every decision each item's execution will hit and asked them all now, rather than answering, watching it work briefly, then being stopped for the next question it could have foreseen.*

## Success criteria

**Tier 1 (agent-immediate).** After `/groom` (or `/ask`), the agent's own chat turn contains **no question directed at the user** (no "Want me to…?", "Should I…?", "which do you prefer?"). Every user-answerable item is present in `{NAME} queries.md`, self-documenting, with a count. `audit-q` is clean before the doc is surfaced.

## The composition — groom / query / render are one autonomous machine

| Layer | What it does | Skills |
|---|---|---|
| **Resolution** | plan the frontier to Ready — rebracket stale states, investigate + declare each frontier task's next step, promote what meets the Definition of Ready, auto-resolve reversible guesses, run every agent-runnable check, decide low-stakes calls, **park the irreducible residue into the queries surface** | `/groom` (frontier planning + backlog states) + `/ask` (determination ladder over the frontier) |
| **Render** | mechanically paint `Q.md` + `{NAME} queries.md` from current state, then glance | `queries-render.py` (fired automatically via `state`) |

- **`/groom` (top-level)** = resolution layer **+** render + glance. The bulletproof button: grooms, queries, piles, presents — and **never asks**.
- **`/crank` dry-fallback** = resolution layer (groom → ask); no question ever dribbled to chat.

The agent does **everything it can** to figure things out, line them up, and resolve them in one shot. What remains — the honest residual it *cannot* resolve without the user — is stacked in the doc, each entry prepared so that when the user turns to it, they answer the whole stack in one pass. That is the whole product.
