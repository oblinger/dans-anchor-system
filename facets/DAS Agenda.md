---
description: "the strategy facet — one {slug} Agenda.md per anchor carrying the theory-of-victory for a big-chunk activity"
---
# DAS Agenda
The strategic frame — one optional `{slug} Agenda.md` per anchor saying why this activity exists, what winning looks like, and how we plan to attack it.

| -[[DAS Agenda]]- | → [[DAS]] → [[FCT]] → [DAS Agenda](hook://p/DAS%20Agenda)  |
| --- | --- |
| Related | [[templates/agenda.md\|agenda template]],  [[DAS Track]],  [[DAS Roadmap]],  [[DAS PRD]],  [[DAS Brief]],  [[DAS Backlog]],   |
| Examples | [[FEX Agenda\|worked example]],   |
| Rules | [[R-agenda]],   |

**TLDR** — `{slug} Track/{slug} Agenda.md` is the anchor's **strategy** surface: five required H2s (`## Purpose` · `## Success — what "won" looks like` · `## Approach` · `## Constraints` · `## Cadence`) plus optional `## Open Questions` / `## History` / `## Links down`. User-authored by default (the agent may draft, the user ratifies), prose-only — no bracketed work rows. It sits **above** the Roadmap: Roadmap says "next milestone: X"; Agenda says "this activity exists because Y, winning 12 months out is Z, and our approach is W." **Cardinality: 0-or-1 per anchor, elective** — most anchors neither have nor need one.

|  |  |
|---|---|
| **Table of Contents** |  |
| [[#Location]] |  |
| [[#Reference Example]] |  |
| [[#Format Specification]] |  |
| [[#When appropriate]] |  |
| [[#Discipline]] |  |
| [[#Relationship to other facets]] |  |
| [[#Audit]] |  |

## Location

`{slug} Track/{slug} Agenda.md` — inside the Track folder, alongside [[DAS Backlog|Backlog]] and [[DAS Status|Status]]. Strategy is tracking metadata about *the activity*, not design content about *the artifact*, so it sits on the Track side of the Track ⟺ Design boundary ([[DAS Track]] § What does NOT live in Track).

Reachable from `{slug} Track.md`'s dispatch table via an `[[{slug} Agenda]]` row (R-agenda-09).

**Single-file default; folder-doc upgrade.** When an Agenda outgrows one file — strategy discussion accumulates, sub-approaches want their own pages — upgrade to the folder-doc form `{slug} Track/{slug} Agenda/{slug} Agenda.md`. The same-named index keeps the upgrade link-transparent, matching the [[DAS PRD]] / [[DAS Architecture]] upgrade pattern.

## Reference Example

[[FEX Agenda]] — a worked Agenda for the [[HBR]] example project, showing all five required H2s plus `## Open Questions` and `## History`.

## Format Specification

An Agenda is ordinary markdown prose under H2 headers. There is no dataview line, no bracket grammar, and no script mediation — it is written and read by humans and agents directly.

**Required H2s, in this order:**

1. **`## Purpose`** — one to two paragraphs: why this activity exists, what it is for, who it serves. The anchor's *raison d'être* stated in one place.
2. **`## Success — what "won" looks like`** — the concrete definition of victory at the activity's time-horizon (a quarter, a year, five years). Observable, not aspirational: a reader must be able to tell from the outside whether it happened.
3. **`## Approach`** — the theory of how we win. Not tasks, not milestones — the *strategy*. A named approach is preferable ("bottom-up bootstrapping", "warm-intro-first", "buy-vs-build with three vendors evaluated in parallel") because a named approach can be argued with, and an unnamed one can only be nodded at.
4. **`## Constraints`** — what limits the space of possible approaches: budget, time, dependencies, non-negotiables, and the tradeoffs the user has already made and is committing to.
5. **`## Cadence`** — how often this Agenda gets revisited (weekly / monthly / quarterly) and by whom (user / agent / joint). **This section is load-bearing.** A Backlog gets pinged by execution and so stays honest on its own; an Agenda has no such forcing function, and a stale Agenda misleads worse than a stale Backlog does. The Cadence section IS the maintenance schedule.

**Optional H2s:**

6. **`## Open Questions`** — strategy-level unresolved questions parked for a decision-with-user moment. Format per [[DAS ask-format]] when they are live asks.
7. **`## History`** — dated decisions and pivots; how the Agenda evolved. Newest-first.
8. **`## Links down`** — pointers to the Roadmap / Backlog / Design / PRD / Brief that execute this strategy. Not required — the anchor page's dispatch table already carries these; add it only when the tactical layers are numerous enough that a curated subset helps.

The file carries YAML frontmatter with a `description:` key and a `# {slug} Agenda` H1, per the ordinary [[DAS Doc Structure]] shape.

## When appropriate

**Cardinality: 0-or-1 per anchor. Elective.**

**An anchor gets an Agenda when:**

- it appears on a routing list — [[Rocks]] (quarterly / annual), [[Prime]] (multi-year priorities), [[Q2]] (secondary long-term) — or is a mission-scale activity;
- the user (or the agent on the user's behalf) has strategic framing worth writing down, not just tasks to execute;
- the activity has enough time-horizon and complexity that a Backlog plus a Roadmap leaves the *why* implicit and easy to lose.

**An anchor keeps its framing in the Brief or the Backlog when:**

- it is historical / archival ([[Yore]], Past Jobs, Attic) — the strategy already played out;
- it is a purely operational tracking anchor (a Log, a simple Container) — Backlog plus Brief cover it;
- the activity is small enough that a Backlog `- **Next:**` step or the anchor page's Brief already carries the framing.

**Rule of thumb:** if you find yourself wanting to write more than two or three sentences of "why this exists and how we're attacking it" into the anchor page's Brief, promote that content into an Agenda.

## Discipline

- **Agenda is user-authored by default.** The agent may draft it and the user ratifies. The flip side is the tell: [[DAS Roadmap|Roadmap]] is agent-authored and technical; Agenda is strategic and the user's.
- **Agenda is not a task list.** No `[Ready]` / `[Blocked]` rows, no F/T-numbered items, no block anchors. When a section implies next steps, those steps go on the [[DAS Backlog|Backlog]] with a wiki-link back to the Agenda.
- **Agenda has a revisit cadence.** The `## Cadence` section names the interval; a Warden rule may flag an Agenda whose mtime exceeds its stated cadence period.
- **One Agenda per anchor.** No sub-Agendas. When a big-chunk activity splits into sub-activities that each want their own strategic frame, those sub-activities get their own anchors, and each of those gets its own Agenda.

## Relationship to other facets

| Facet | Owner | Time-scale | What it is |
|---|---|---|---|
| Mission (as a list) | User | Life-scale | Life purpose; the ancestor context above every Agenda |
| **Agenda** | User (agent drafts) | Multi-year → quarterly | Strategy / theory-of-victory for this activity |
| [[DAS Roadmap\|Roadmap]] | Agent | Quarterly → months | Milestone execution plan |
| [[DAS PRD\|PRD]] | User + agent | Feature-launch | Product-shaped requirements + scope |
| [[DAS Design Docs\|Design]] | Agent | Architecture | Technical / structural design |
| [[DAS Backlog\|Backlog]] | Agent + user | Weeks → days | Task queue with brackets |
| [[DAS Brief\|Brief]] | Agent-facing | Timeless | Operating instructions for agents working here |

The three nearest neighbours, stated as distinctions:

- **vs Roadmap** — Roadmap is milestone / execution-focused, agent-authored, typically technical, and sequences *how we build it*. Agenda is upstream of that and answers *what we are trying to achieve at this activity's time-horizon, and why*.
- **vs PRD** — a PRD is product-launch-shaped: requirements, user stories, launch scope. An Agenda applies equally to non-product activities — a career track, a personal commitment, a learning program.
- **vs Brief** — a Brief is agent-facing operating instruction ("when you work here, do X"). An Agenda is strategy the agent *reads to align with*, not directives it executes.
- **vs Mission** — Mission is life-scale (why-existential). Mission is itself a valid anchor and would carry its own Agenda at `Mission/Mission Track/Mission Agenda.md`. Agenda is one level down: activity-scale, multi-year to quarterly.

## Audit

`/audit agenda` (future) would flag:

- **missing-h2** — one of the five required H2s absent.
- **h2-order** — required H2s present but out of declared order.
- **cadence-unstated** — `## Cadence` present but names no interval.
- **cadence-stale** — file mtime older than the interval the `## Cadence` section names.
- **work-rows-present** — bracketed workflow rows (`[Ready]`, `[Blocked]`, …) or `^F<n>` block anchors inside the Agenda.
- **wrong-location** — file lives anywhere other than `{slug} Track/`.
- **dispatch-unlinked** — `{slug} Track.md` has no row linking `[[{slug} Agenda]]`.
- **sub-agenda** — more than one `* Agenda.md` under one anchor.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above plus the extracted [[R-agenda]] ruleset.)*

- **This is the Agenda-facet spec, not an Agenda** — don't write live strategy here. The worked instance is [[FEX Agenda]]; keep illustrative content there, not inline.
- **The five required H2s and their order are load-bearing** — `R-agenda-04` / `R-agenda-05` check both, the template stubs them in that order, and `/audit agenda` will key off them. Changing the set or the sequence requires a coordinated edit to `templates/agenda.md`, [[R-agenda]], and every adopting anchor's file in the same pass.
- **`## Cadence` is the one section that cannot become optional** — an Agenda has no execution forcing-function, so the stated interval is the only thing that keeps it honest. Any proposal to soften it should be read as a proposal to let Agendas rot.
- **Guard the Agenda ⟺ Roadmap line** — the recurring drift is milestone lists creeping into `## Approach`. Approach carries the *theory*; sequenced milestones belong in [[DAS Roadmap]], and the individual steps belong in [[DAS Backlog]].
- **Keep the spec body and [[R-agenda]] in sync** — a format change requires the matching `R-agenda-NN` change; keep the `(checked)` / `(sampled)` / `(stated)` markers honest, since they tell the audit script which rules it can mechanize.
- **Elective, and it should stay elective** — the failure mode of a new facet is universal adoption by scaffolding. The § When appropriate gates exist so that `/create anchor` never scaffolds an Agenda by default.
