---
description: a loop is an ordinary stone plus a workflow and a step — the `loop` script validates, enrolls it on the watch list, advances it on evidence and recalls it when closed; nobody hand-writes a Traffic line
group: folder
---

| -[[DAS Loop]]- | → [[DAS]] → [[FCT]] → [DAS Loop](hook://p/DAS%20Loop)  |
| --- | --- |
| Facet | [[DAS Stone]],  [[DAS Stone Keys\|Keys]],   |
| Examples | [[FEX Loop\|example]],   |
| Related | [[Tink635 - Loop mechanism: a stone that carries a process, so Traffic can run it\|TINK F635]],  [[ASTR Comms]],  [[DAS Template]],  [[TRAFFIC]],   |
| Rules | ~~[[R-loop]]~~,   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Proj]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Loop
Facet spec for a **loop** — a stone whose keys resolve to a workflow, so that a script can say what step it is on, when that step comes due, what observation decides it, and where it goes next. Not a new kind, list or folder: a loop lives on its owner's list and is **enrolled** on the watch list ([[TRAFFIC]]) while active.

**TLDR** — two keys make a stone a loop: `workflow::` (a wiki-link; whatever it points to is the workflow) and `step::` (the current step's name). `entered::` and `lapses::` complete the set. The `loop` script is the only thing that writes `step::`.

**Cardinality:** many — any stone on any list may be a loop; the workflow is a document, not a facet — one per channel as a template ([[DAS Template]]), a page with a `## Workflow` section, or the stone itself by self-link.

## The keys

| Key | Meaning | Required |
|---|---|---|
| `workflow::` | wiki-link to the workflow; recorded on the stone at `start` even when `channel::`'s page supplied it | **yes** |
| `step::` | current step name in the resolved workflow; written only by `loop` | **yes** |
| `entered::` | date `step::` was entered; every relative `when` counts from here | **yes** |
| `lapses::` | one clause on what is lost if the loop fails | **yes** |
| `channel::` | wiki-link to the counterparty (`[[@Cigna]]`); its page may carry a default `workflow::` | no |
| `closed::` | date the loop closed; the reference has left the watch list | written by `close` |
| bindings | whatever the workflow's `requires::` names, as ordinary `key:: value` (`window-open`, `run-out`, `return-id`) | **yes** — per workflow |

`due::`, `done::`, `importance::` stay the watch list's `accepts:` contract ([[ASTR Comms]] § The handoff contract). `tempo::` is written by the step from the workflow's `raise::`, never by hand. Full vocabulary: [[DAS Stone Keys]] § Loop's keys.

## The workflow grammar

A `## Workflow` section — header keys, then one table — the same wherever the link lands.

`requires:: window-open, run-out` — the bindings every instance carries. `raise:: daily` — the `tempo::` while any step is live.

| step | when | probe | hit | miss |
|---|---|---|---|---|
| a lowercase name | the rendezvous | one or more observations, ` · `-separated | next step, or `close` | next step, `owner`, or `dan` |

**`when` — closed vocabulary.** Absolute `2026-09-15` / `2026-09-15 07:00`; symbolic `daybreak`, `22:00`; relative `+7d` from `entered::`; keyed `<key>±Nd` from any date-valued key on the stone (`run-out-3d`, `ordered+3d`, bare `window-open`). One key and one offset, no expressions — a computed edge is written as a binding at mint. Hour floor: the watch is hourly.

**`probe` — four kinds, executable, never prose.** `mail: <notmuch query>` (script-run; hit or unknown). `key: <name>` (script-run; hit when set, miss when provably not). `portal: [[link]] — <what proves it>` (agent-run; `loop due` lists it under *needs an agent check*). `owner:` (judgment; routes to the owning anchor). An `· importance high` annotation may trail the `when` cell or a branch target; it is applied on entering that step.

**Tri-state.** `hit` advances at any time — Dan may act early. `miss` is a proof of absence and takes the miss branch only once the rendezvous has arrived. `unknown` never branches; past the rendezvous it routes to the owner. A step whose miss reaches `dan` must carry a probe that can return `miss`. `miss → dan` is not a rung: the step supplies importance and `due::`; Sparks picks rungs ([[ASTR Comms]] § Picking a rung, take two). **There is no cell for a channel, a rung or a command.**

## The verbs — `skills/workflow/scripts/loop`

| Who | Verb | Does |
|---|---|---|
| owner | `loop start <OWNER[.list]> <ID> --workflow [[link]] [--channel [[@X]]] [--set k=v …]` | validates, writes the keys and the first step, enrolls on TRAFFIC via `stone push`, prints the receipt; a defect is refused with nothing written |
| owner | `loop advance <OWNER> <ID> [--to STEP] --evidence "…"` | the only way `step::` changes; rewrites `entered::`, `tempo::`, importance; appends to `## Log` |
| owner | `loop close <OWNER> <ID> --evidence "…"` | writes `closed::`, logs, recalls from TRAFFIC |
| owner | `loop show <OWNER> <ID>` | resolved workflow, step, rendezvous, probes, both branches |
| watch | `loop due [--all]` | enrolled loops whose rendezvous has arrived — *script-probable* / *needs an agent check* / *owner's judgment* |
| watch | `loop scan [--since TS] [--apply]` | runs every `mail:`/`key:` probe; a report by default, advances only with `--apply` |
| watch | `loop stale` | past rendezvous and still undecided, with the owner to route to |
| check | `loop check <OWNER> <ID>` | the validation `start` runs, on any stone |

The stone is minted first with `stone new` (its `line::` and body are the owner's); `start` turns it into a loop. `LOOP_NOW` pins the clock for fixtures; `--root` scopes the vault, as for `stone`. Guard: `test-f635-loop.py`.

## Who does what

**The owner** (Wells, Hermes, Sonar) writes a workflow once per channel as a template, mints the stone, fills the bindings and the handoff keys, runs `start`, and `advance`s on evidence the scripts cannot see. **Sparks** runs `due` and `scan` hourly from `sparks-watch`, performs the `portal:` checks, `advance`s on what they show, and campaigns when a miss reaches `dan`. **Lumen** selects by `tempo::` as now. **Dan** acts in the world; his acts enter as `key:` probes (`ordered:: 2026-09-05`). **Tink** owns the mechanism.

## Security — deferred, on record

A workflow is a document that makes agents act. The grammar keeps the blast radius small by construction — closed `when` and probe vocabularies, no executable cell — but that is containment, not a defense; anything writable in the vault can author one. Dan, 2026-09-02: *terrible from a security point of view … kick the can down the road.* Held by [[Atticus]] (P0018).

# BRIEF

- **Inclusion test** — a rule belongs here only if it constrains the loop keys, the workflow grammar, or what `loop` refuses. What a *stone* is (files, control file, feeds, push) is [[DAS Stone]]'s; the ladder Sparks climbs on a `dan` miss is [[ASTR Comms]]'; a specific channel's steps belong to its owner's template, never here.
- **The vocabulary is closed on purpose and the script is its single reader.** `when` kinds, probe kinds and branch targets are parsed once in `skills/workflow/scripts/loop`; `activity_view.py traffic` and `sparks-watch` are to import that resolver, never re-parse — the hand-authored Traffic spine drifted from its own field list because two readers parsed it. Adding a kind means the script, `test-f635-loop.py`, and this page in one change.
- **Step names are provisional until the first Cigna cycle runs** — Dan and Atticus's ruling *do not generalise from one cycle*. Do not freeze a step vocabulary into this spec before then.
- **`step::` is machine-written.** A hand edit of `step::` bypasses the log and the check; the fix for a wrong step is `loop advance --to`, not an edit.
- **Security is deferred, not solved** — keep the § Security paragraph until Atticus P0018 replaces it with a defense.
