---
description: Subsystem design for the Tracking group — the surfaces, verbs, and rules that let a human and an agent share one picture of work state. Paradigm doc for per-group subsystem design.
---

:>> [[DAS]] → [design](hook://design) → [DAS Tracking Design](hook://p/DAS%20Tracking%20Design)
# DAS Tracking Design
Tracking is the subsystem that keeps one shared picture of work state between the human and the agent: what is ready, what is blocked, what question is waiting on whom.

![[DAS Tracking Design.svg|3000]]

| **Skills**                              |                                                                                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [[DAS Ask\|/ask]]                       | Eliminate every question the agent can; consolidate the residue into `{slug} queries.md`; render Q.md.                                                                  |
| [[DAS Groom\|/groom]]                   | Frontier planning: get every could-be-next item fully Ready or parked with its blocking question.                                                                       |
| [[DAS Plan\|/design]]                   | Once-per-project planning orchestrator — drives the anchor's planning artifacts to completeness.                                                                        |
|                                         |                                                                                                                                                                         |
| **Facets**                              |                                                                                                                                                                         |
| [[DAS Backlog\|Backlog]]                | The work queue: rows carrying bracket × horizon, F/T-numbered, block-anchored.                                                                                          |
| [[DAS Query\|Query]]                    | The consolidated question pile (`{slug} queries.md`) — banner + body copied verbatim into Q.md.                                                                         |
| [[DAS Status\|Status]]                  | Per-facet planning status via the monotonic tier ladder.                                                                                                                |
| [[DAS Agenda\|Agenda]]                  | The activity's strategic frame — purpose, definition of won, approach, constraints, revisit cadence. Elective, user-authored.                                            |
| [[DAS Roadmap\|Roadmap]]                | Forward-looking milestone state, named `M-<Name>` entries.                                                                                                              |
| [[DAS Completed Roadmap\|Completed Roadmap]] | Migration target for shipped milestones, newest at top.                                                                                                            |
| [[DAS Log\|Log]]                        | Append-only dated history stream — what happened on what day.                                                                                                           |
| [[DAS Messages\|Messages]]              | Inter-agent background notes (vs. user-dropped Inbox input).                                                                                                            |
| [[DAS Inbox\|Inbox]]                    | User-dropped input awaiting agent triage.                                                                                                               |
| [[DAS Icebox\|Icebox]]                  | Cold storage for parked rows — outside every default groom scope.                                                                                       |
| [[DAS Track\|Track]]                    | The `{slug} Track/` folder shape that houses the surfaces above.                                                                                                        |
|                                         |                                                                                                                                                                         |
| **Traits**                              |                                                                                                                                                                         |
| [[Track]]                               | Declares the anchor is actively driven through the planning + backlog lifecycle — turns on the `{slug} Track/` tree and the verbs above; co-requires the Backlog facet. |
|                                         |                                                                                                                                                                         |
| **Library**                             |                                                                                                                                                                         |
| [[DAS State\|`state` CLI]]              | The single write path for rows, questions, statuses, roadmaps; every mutation triggers the Q.md render.                                                                 |
| **`queries-render.py`**                 | Mechanical renderer — rebuilds `{slug} queries.md` and copies it into Q.md after every mutation.                                                                        |
| Disciplines                             | [[DAS workflow]] · [[DAS ask-format]] · [[DAS verification]] · [[DAS granularity]]                                                                                      |
| Rulesets                                | [[R-backlog]] · [[R-query]] · [[R-status]] · [[R-agenda]] · [[R-log]] · [[R-messages]] · [[R-roadmap]] · [[R-completed-roadmap]] · [[R-track-group]] · [[R-track-dispatch]] · [[R-fct-icebox]] · [[R-fct-inbox]] · [[R-state-region]]                        |

## Overview

Tracking's contract: **the agent never asks piecemeal and the user never hunts for state** — questions consolidate into one pile, status renders into one glanceable banner, and every state change flows through one write path. Work state lives in **facet-shaped files** (the surfaces), is mutated only through the **`state` CLI** (the engine), and is operated by a small set of **verbs** (the skills). Two axes organize every work item: *horizon* (Now / Next / Later — when the user wants it) and *workflow state* (the bracket — whether it can proceed). The drive cluster (`/crank`, `/mint`, `/land`) consumes what tracking surfaces as Ready; tracking itself never executes work.

In the table above, every item's name links its docs page directly — the skill dossier (whose masthead links the runbook) or the facet spec (whose masthead leads with breadcrumb · Related · Examples · Rules · ToC and links the template) — so one column of links routes everywhere. Rules live in `rulesets/R-<name>.md` (whole tracking group extracted 2026-07-12; other groups follow at their profile pass). *(Table reduced to two columns per the shape revision of 2026-07-14 — see design record.)*

## The model

Two orthogonal axes place every work item, and a small handle namespace names it.

- **Horizon** (*when*) — `Now` / `Next` / `Later`, owned by [[DAS Backlog]]. Three tiers, deliberately: two collapse back to in-or-frozen, four reintroduce the bucket-shuffling the horizons exist to bound. Below `Later` sits the [[DAS Icebox]] — frozen, outside every default groom scope.
- **Workflow state** (*how far*) — the square-bracket prefix, owned by [[DAS workflow]] (restated in § The state graph). Independent of horizon: `Later [Ready]` (design-clean, unscheduled) and `Now [Designing]` (wanted soon, still open) are both legal.

**Handles** — one namespace per work-item kind, all monotonic, zero-padded, and never recycled: **F** (a feature, with a doc under `{slug} Design/{slug} Features/`), **T** (a task the backlog row fully captures — no doc), **`M-<Name>`** (a roadmap milestone in [[DAS Roadmap]], named not numbered), **R** (a backlog commitment to execute a roadmap entry — the roadmap counterpart of T). Names carry identity; a roadmap entry's order is just its document position, so reorders and inserts never stale a reference — only a rename forces a sweep. Full four-handle model: [[Query PRD]] § Work-item identity.

**The frontier** — the set of items that *could be next*: everything under `## Active` / `## Ready` / `## Now` / `## Next`, plus the next unmet milestone of any live roadmap. `Later` and the icebox are not frontier. [[DAS Groom|/groom]] exists to drive every frontier item to *fully Ready* — a declared `- **Next:**` step, promoted when the Definition of Ready holds, or honestly bracketed behind its named blocker/question. [[DAS Ask|/ask]] mines its anticipatory questions from the same frontier.

**Never ask piecemeal** — the contract's first half. Every question the agent can eliminate, it eliminates; the residue consolidates into `{slug} queries.md` and surfaces as *one* round-trip per pass, never an inline interruption mid-batch. This is why a pending question is a *state* (`[Questions]`, linking the doc where the numbered Qs live), not a side-channel.

## The state graph

Owned by [[DAS workflow]]; restated here so the overview stands alone (discipline-redundancy is intentional). Each item carries a square-bracket state prefix. The happy path is:

`[ ]` → `[Designing]` → `[Ready]` → `[Active]` → `[Verify]` → `[Done]`

with branch states off the path: `[Questions]` — waiting on a user *decision* (the universe needn't change, only the user must answer); `[Blocked]` / `[Blocked F<n>]` — something in the *universe* must change (a dependency, an artifact that doesn't exist yet, another feature landing); and the soak pair `[Waiting]` (observing for an event we *want* to occur) / `[Watching]` (soaking on a shipped fix, observing for *non*-recurrence). **Definition of Ready:** an item is `[Ready]` when the agent believes it can finish without further user involvement. No transition is silent — each is driven by a named verb (`/design`, `/feature`, `/groom`, `/mint`, `/finalize`).

## Coordinated examples

Tracking is illustrated inside the coherent worked worlds at [[FEX]] (HBR, FEX Repo) — one real backlog + queries + status set per world, rather than a standalone example per facet.

## Provenance

One consolidated record of the naming/shape decisions this subsystem carries, kept here rather than scattered across the facet specs:

- **`M-<Name>` milestones are named, not numbered.** A milestone's ordinal is *computed* from its document position, never stored in a handle — so inserting or reordering roadmap entries never stales an `R`/done-log reference; only a rename forces a sweep. Rule: [[DAS Roadmap]] § Names are identity (R-roadmap-12).
- **Completed Roadmap is a separate facet** ([[DAS Completed Roadmap]]), not a `## Done` section of the roadmap — shipped milestones migrate out (newest at top) so the live roadmap stays forward-looking only.
- **`state` is the sole write path.** Every row / question / status / roadmap mutation flows through the `state` CLI ([[DAS State]]), which triggers `queries-render.py` to rebuild `{slug} queries.md` and propagate it into `Q.md`. Hand-edits are never the interface; the render is mechanical and idempotent. (`backlog-edit.py` is the plumbing layer `state` delegates to.)

## Design record

- [[Query PRD]] — the shared resolution-layer design behind /ask and /groom.
- [[DAS Groom Design]] · [[DAS Groom PRD]] — per-verb design docs (Ask's design lives in [[Query PRD]]); [[DAS ask-inline]] is the inline form of /ask.
- [[T009 Phoenix Tracking Survey 2026-07-12]] — demolition survey feeding the Phoenix boil-down of this group.
- This doc is the **paradigm subsystem design** (shape ratified 2026-07-12, encoded as `R-spine-02`): breadcrumb → H1 → orientation line, overview figure, one merged Skills / Facets / Traits / Library table, `## Overview`, coordinated examples, design record — each group gets one of these, linked off [[DAS]]. **Shape revision (user, 2026-07-14, Design session):** the table is **two columns** — the item's name links its docs page directly (which routes on to runbook / template / rules); the separate docs column is retired; descriptions stay to one line. Profile filenames follow the literal formula `DAS <Group> Design.md` (so the Design group's is [[DAS Design Design]], repeat accepted; a gerund or subtitle may soften the H1 title text, never the filename).
- Figure source: same-basename `DAS Tracking Design.excalidraw` beside the SVG (edit in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
