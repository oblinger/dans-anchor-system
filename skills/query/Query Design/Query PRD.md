---
description: PRD for the /query skill — the system for NOT asking the user questions. Eliminate every question the agent can; consolidate the irreducible residual into one self-documenting, one-shot-answerable pile. Asking in chat (especially after triage) is the cardinal violation.
---

# Query PRD

:>> [[SKA]] → [[SKA query]] → Query Design

## Overview

`/query` exists for one reason: **so the agent does not interrupt the user with questions.** Every question put to the user is a cost — it fragments their attention, arrives out of context, and scrolls away. The agent's prime directive is to **resolve, decide, and verify on its own**; and for the small irreducible residue that *genuinely* needs the user, to **consolidate it into one place, fully prepared**, so the user answers everything in a single pass — *bam, bam, bam, down the list* — instead of being dribbled questions one at a time across a conversation.

**`{NAME} queries.md` is the always-current store of open questions; chat is at most a view of it.** The doc holds the anchor's open questions *at all times*, and the moment any question is raised — at a triage, or any other time — it is written there **simultaneously**. A question may be *spotlighted* in chat, but **only if it is also in the doc at that same moment**: chat never carries a question the doc doesn't, and the doc is never behind chat. The cardinal violation is a chat question with **no corresponding queries-doc entry** — because chat **scrolls away** (the user runs many agents at once) and the question is then lost, whereas `queries.md` is the one place the user can always return to for the latest open questions. *After a triage especially*, don't fragment the freshly-built pile with loose chat questions — the pile *in the doc* is the surface; any chat line is a pointer into it. (The doc legitimately lags only during live back-and-forth before the next triage; the target is always-current.)

**And the goal is not merely *fewer* interruptions — it is the longest possible *unblocked runway* between them.** Query does not only surface the questions that exist *right now*; it **looks ahead**. For each backlog item it proactively reasons about the decisions execution *will* hit — the forks, the missing specs, the taste calls that surface only once you start building — and surfaces those **early**, in the same pile, *before* they block anything. The metric query optimizes is **work-done-per-answered-pile**: how far the agent can execute after the user answers one round of questions before it is forced to stop and ask again. Front-loading every foreseeable question for an item means that once its pile is answered, the agent runs that item to completion — and ideally the *next* items too — without another interruption. This is the backlog-wide generalization of "Ready means ready: ask **all** implementation questions upfront."

`/query` is the **resolution + consolidation** half of the triage machine; `triage-section.py` is the mechanical **render** half. Together with `/groom` they form one autonomous loop that grooms, resolves, piles, and presents — and never asks.

## Goals

- **G1 — Eliminate.** Drive the open-question count toward zero by the agent's own effort. Every open question runs the full determination ladder *to exhaustion* before any of it reaches the user: auto-resolve reversible/soon-visible guesses (and record them); run every check the agent can run itself and answer it; decide the low-stakes / visible / reversible calls (assume-and-announce); infer from context and the codebase. A question survives to the user **only** when it genuinely needs *user judgment* AND is high-stakes / irreversible / a matter of taste the agent has no basis to pick. Most "questions" die here — that is the point. "I could resolve this myself but it's easier to ask" is a violation.
- **G2 — Consolidate.** The survivors land in `{NAME} queries.md`: one pile, each entry **self-documenting** (answerable from the entry text + the links *inside* it, nothing to hunt for), each carrying its **pending-Q count** (`[[F181 …]] **(5Q)**`), ordered so the user rips through the whole stack in one sitting. Everything they need has been lined up in advance.
- **G3 — The doc is the store; chat never leads it (R1).** Every question is written into `{NAME} queries.md` the moment it is raised (simultaneously, not deferred to the next triage). Chat may *spotlight* a question but never carries one the doc lacks — chat is a view, the doc is the source of truth, and the doc is never stale relative to chat. A chat question with no doc entry is the violation: it scrolls away and the user (running many agents) loses it.
- **G4 — Triage is the bulletproof orchestrator (R5).** `"` / `/triage` runs the resolution layer (groom + query) then the render layer then glances — fully autonomously — and ends with a **status report, never a question (R6).**
- **G5 — One-shot answerable (R3/R4).** The user can answer the entire pile in one pass without opening any other document to understand a question.
- **G6 — Maximize the unblocked runway (anticipatory surfacing).** Don't only surface the questions you have *now* — **look ahead**: for each backlog item, proactively reason about the decisions execution *will* hit and surface those *early*, in the same pile, before they block anything. The optimization target is **work-done-per-answered-pile** — the stretch of autonomous work one answering pass buys before the next forced question. Front-load every foreseeable question per item so that answering its pile runs the item (and ideally the next ones) to completion uninterrupted.

## Non-Goals

- **Not a dashboard / status renderer.** Painting `Q.md` and the queries-doc body is `triage-section.py`'s mechanical job. `/query`'s job is *determination* — deciding what dies and what survives — not formatting.
- **Chat is not the store.** Chat is a *view*, never the source of truth — `/query` never raises a question in chat without writing it to the doc at the same moment, so the doc is never behind chat. (A chat *spotlight* that points into the doc is fine; a chat question the doc lacks is the violation. A creation-time inline yes/no the user is actively engaged in *that instant* — e.g. `/feature`'s title-collision prompt — is owned by the invoking skill, not query, and is still mirrored to the doc if it defers.)
- **Not an agent action-log.** `## Agent Resolutions` records reversible *guesses*, not a diary of edits the agent made (per the durable feedback rule).
- **Not a place to defer work the agent could do.** If an item is actionable-but-not-a-user-question, the agent lands it or files it as a `[Ready]` feature — it never becomes an orphan "question."

## User Stories

- **US1 — Don't interrupt me.** *As the user, I want the agent to figure out everything it possibly can on its own, so that I am not pulled into a conversation for things the agent could have decided, run, or inferred itself.*
- **US2 — One shot, zero hunting.** *As the user, when I do turn my attention to the pile, I want every question lined up with all the context I need to answer it right there, so I can go down the whole list and answer them all in one sitting — bam, bam, bam — without opening other docs.*
- **US3 — One pile, counted.** *As the user, I want all residual questions in one place with a count per feature, so I know exactly how much input is being asked of me at a glance.*
- **US4 — Triage never asks.** *As the user, after I press `"`, I want a status report — what was groomed, what was resolved, how many questions remain in the doc — and NOT a question in chat, because a chat question fragments the pile that triage exists to consolidate.*
- **US5 — Front-load so my answers go far.** *As the user, when I answer the pile, I want to unblock the maximum amount of work — so I want the agent to have thought ahead about every decision each item's execution will hit and asked them all now, rather than answering, watching it work briefly, then being stopped for the next question it could have foreseen.*

## Success criteria

**Tier 1 (agent-immediate).** After `"`, the agent's own chat turn contains **no question directed at the user** (no "Want me to…?", "Should I…?", "which do you prefer?"). Every user-answerable item is present in `{NAME} queries.md`, self-documenting, with a count. `audit-q` is clean before the doc is surfaced.

## The composition — triage / groom / query are one autonomous machine

| Layer | What it does | Skills |
|---|---|---|
| **Resolution** | rebracket stale states, promote ready items, auto-resolve reversible guesses, run every agent-runnable check, decide low-stakes calls, **park the irreducible residue into the queries surface** | `/groom` (backlog states) + `/query` (determination ladder) |
| **Render** | mechanically paint `Q.md` + `{NAME} queries.md` from current state, then glance | `triage-section.py` |

- **`"` / `/triage` (top-level)** = resolution layer **+** render + glance. The bulletproof button: grooms, queries, piles, presents — and **never asks**.
- **`/groom` (top-level)** = resolution layer + render. Same never-ask rule.
- **`/crank` dry-fallback** = resolution layer (groom → query); no question ever dribbled to chat.

The agent does **everything it can** to figure things out, line them up, and resolve them in one shot. What remains — the honest residual it *cannot* resolve without the user — is stacked in the doc, each entry prepared so that when the user turns to it, they answer the whole stack in one pass. That is the whole product.
