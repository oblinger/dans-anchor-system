---
description: "CAE system architecture — worked example of the DAS Architecture facet"
---
# FEX Architecture
CAE is a single-process CLI scheduler. A submitted task carries a deadline, a retry policy, and an opaque command payload; the scheduler enqueues it in a SQLite-backed priority store, dispatches to a fixed worker pool when ready, and routes failures through a centralized retry manager. No daemon, no IPC — every coordination decision flows through the SQLite store.

![[CAE Architecture.png]]

CLI submits tasks to the **Scheduler**, which dispatches to the **Worker Pool**, persists state in **TaskStore**, and consults **RetryManager** on failure. The injectable **Clock** (not shown — passed by reference at construction) is the time source every component reads from.

| -[[FEX Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [FEX Architecture](hook://p/FEX%20Architecture)<br>: CAE system architecture — worked example of the DAS Architecture facet |
| --- | --- |
| [[FEX Scheduler]] | priority queue engine + worker dispatch. Source: `src/execution/scheduler.rs`. |
| [CAE-Store] | SQLite-backed task persistence; load/save/mark-done. (subsystem doc not yet authored) |
| [CAE-Retry] | exponential backoff + dead-letter handling; centralized retry policy. (no doc yet) |
| [CAE-Clock] | injectable `Clock` trait; production `WallClock` + test `TestClock`. (no doc yet) |
| --- | |
| [[_{{DISK_LABEL}} Template]] |  |
| [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]] |  |
| [[Bridges]] | example list-dispatch collection (≤ 15 members) |
| [[CAE Architecture]] | CAE system architecture — entry-point doc for the {slug} Architecture/ folder anchor. Worked example of the CAB Architecture facet (section spine, visual-only diagrams, subsystem dispatch with link convention, API content lives elsewhere). |
| [[CAE Decisions]] | load-bearing rules & invariants |
| [[CAE PRD]] | product requirements for the CAE Example CLI scheduler |
| [[CAE Stories]] | three user stories — index for US-CAE-1..3 (folder-form per ~~ |
| [[CAE Testing]] | testing strategy + proposed-tests overview (worked example of |
| [[Clarifier]] | example project anchor — a designed software project |
| [[CSE]] | Common Skill Example — reference anchor — a fully-wired example of a DAS skill anchor |
| [[DAS Examples]] | the example gallery — fictional worlds + a per-kind map |
| [[Devtools]] | example grouped-dispatch collection (> 15 members) |
| [[Decisions/DKT Decisions]] | Durable architectural decisions + rationale — standard/API split, Rust+Python common docs, anchor-crate separation |
| [[PRD/DMUX PRD]] | product requirements — focus-free voice dictation hub for macOS |
| [[Espresso]] | Espresso — example topic collection (≤ 15 members) — notes on pulling espresso |
| [[FEX API Design]] | programmatic surface of the `cae` Rust crate — types, signatures, error envelope, stability + compatibility commitments. Sibling to |
| [[FEX Completed Roadmap]] | companion to CAE Roadmap; preserved migrated milestones with their structure; newest-on-top. |
| [[FEX CSE]] |  |
| [[FEX Decisions Details]] |  |
| [[FEX Dispatch Examples]] | live worked examples of each dispatch-table structure |
| [[FEX Facet]] | canonical facet exemplar |
| [[FEX Figure Page]] | the figure-bearing anchor-page layout |
| [[FEX Files]] | repository file tree (audit-generated) |
| [[FEX Grouped Dispatch]] | canonical grouped-dispatch exemplar |
| [[FEX Icebox]] | cold-storage / someday-maybe |
| [[FEX Inbox]] | raw input to process |
| [[FEX List Dispatch]] | canonical list-dispatch exemplar |
| [[FEX Minimal Facet]] | the leanest complete file set for a facet, with a live instance |
| [[FEX Minimal Skill]] | the leanest complete file set for a skill, with a live instance |
| [[FEX Project Root]] | canonical project-root exemplar |
| [[FEX queries]] | CAE queries — mechanically rendered from the backlog by `queries-render.py` (Verifications / Ready+Next / Questions). Do not hand-edit; edit the backlog rows. |
| [[FEX Repo]] | **FEX Repo** — a fake skills repository tying the loose examples together: a skill ( |
| [[FEX Roadmap]] | sequencing-design — milestones + ordering (moved from Track 2026-06-10) |
| [[FEX Skill]] | canonical skill exemplar |
| [[FEX Stories]] | three user stories — index for US-CAE-1..3 (folder-form per |
| [[Forum Stories]] | User stories for the Forum debate platform. |
| [[Architecture/HA Architecture]] | HookAnchor system architecture — top-level decomposition into subsystems. |
| [[HBR]] | **Common Anchor Example** — the fully-wired worked-example anchor (PRD / UX / API / Architecture / Decisions / Testing / Roadmap / Features), cited by the DAS facet specs as the **minimal** reference instance. Relocated here from `CAB/` 2026-06-27. |
| [[Architecture/HBR Architecture]] | system architecture |
| [[Decisions/HBR Decisions]] | durable rulings |
| [[PRD/HBR PRD]] | product requirements |
| [[HBR PRD User Stories]] | audited excerpt — the inline `## User Stories` section of HBR PRD (inline-subsection form, US-HBR-1..5) |
| [[Testing/HBR Testing]] | test strategy + proposed-tests overview |
| [[HWP]] | a short whitepaper on the Harbor media server — the worked Paper anchor example |
| [[Knots]] | **Knots** — a tiny **Topic** anchor: a no-code evergreen knowledge hub routing to sub-topics ( |
| [[Mini]] | tiny example project — the MINIMAL design-docs world for F178 |
| [[Decisions/Mini Decisions]] | durable rulings for Mini |
| [[PRD/Mini PRD]] | product requirements — what Mini does and the one story it must deliver |
| [[Testing/Mini Testing]] | test strategy + proposed tests |
| [[Architecture/MUX Architecture]] | top-level architecture facet — subsystem decomposition with bidirectional module links |
| [[Architecture/OBU Architecture]] | system architecture |
| [[PRD/OBU PRD]] | product requirements — ob-utils shared utilities library, one spec across languages |
| [[SKA Bridge Testing]] | SKA Bridge Testing — strategy + proposed-tests overview |
| [[Snap]] |  |
| [[Testing/MUX Testing]] | MUX Testing — strategy + proposed-tests overview |
| [[Decisions/UCM Decisions]] | architectural and implementation decisions for UCM |
| [[US-CAE-1 — Schedule a Task]] | Schedule a deferred shell task with absolute or relative time |
| [[US-CAE-3 — Retry Failed Tasks]] | Auto-retry failed tasks with exponential backoff to a cap |
| [[Viz Bench]] | figure-drafting techniques compared across a fixed reference set |


> [!note] DAS Architecture convention
> Real subsystem docs use `[[double-bracket]]` wiki-links; placeholders for subsystems whose docs aren't authored use `[single-bracket]` plain text — visible inventory without polluting Obsidian's link graph. See [[DAS Architecture]] § Subsystem dispatch table.

For the public API surface (schemas, file formats, error types), see [[FEX API]].

## Module grouping

The five public modules fall into two coherent areas:

- **Scheduling core** — `execution` + `models`. The submit-run-drain pipeline; callers import here.
- **Infrastructure (internal)** — `retry` + `store` + `clock`. Plumbing; callers rarely touch directly.

Per-module class/function tables live in [[FEX Scheduler]] (`execution` module) and [[FEX API]] (others, as subsystem docs are authored).

## Process model

A `cae` command invocation is either:

- **Short-lived** — `submit`, `cancel`, `status`: open the store, perform the operation, exit.
- **Long-lived** — `drain`, `run`: spawn the scheduler thread + worker pool, process pending tasks until the queue drains or the user interrupts.

## Thread layout

![[CAE Threads.png]]

## Design decisions

Tactical decisions specific to this architecture. Project-wide *principles* live in [[FEX Decisions]] and are referenced here, not restated.

| D    | Decision                                | Rationale                                                                |
| ---- | --------------------------------------- | ------------------------------------------------------------------------ |
| D1   | SQLite over JSON file for TaskStore     | Durability, concurrent reads, no separate daemon                          |
| D2   | Persistence is operator-readable        | `sqlite3 tasks.db` for production triage; no proprietary format           |
| D3   | Fixed thread pool, not tokio            | Simpler reasoning; tasks are shell commands, not I/O-bound                |
| D4   | Single global queue, not per-priority   | Preempts starvation via age-based promotion (see R01)                     |
| D5   | Retry logic in its own module           | Centralizes policy; enforced by R04                                       |

## Design principles application

How the project-wide principles in [[FEX Decisions|CAE Decisions § Principles]] are realized in this architecture:

- **[[FEX Decisions#D01 — One Queue, One Clock (sampled)|D01]]** — realized by routing every submission through `TaskScheduler` and injecting `Clock` at construction.
- **[[FEX Decisions#D09 — Fail Loudly, No Silent Fallbacks (checked)|D09]]** — surfaced through `TaskResult::Failed(error, attempts)` and the dead-letter list; centralized retry (D5) is the only retry path.
- **[[FEX Decisions#D03 — Deterministic Tests (sampled)|D03]]** — realized by the `Clock` trait and the mockable `TaskStore` boundary.

Each principle's `Encoded by:` line in [[FEX Decisions]] lists the R-rules that enforce it; `/audit rules` scans the code against those rules.

## See also

- [[FEX API]] — public API surface
- [[FEX Scheduler]] — Scheduler subsystem (full class/function reference for `execution`)
- [[FEX Decisions]] — anchor-level applied choices (D11 cites R-diagram rules for the diagrams above)
- [[FEX Rules]] — adopted rulesets (currently R-diagram)
- [[R-diagram]] — the ruleset the diagrams above are audited against (structural / aesthetic / semantic / accessibility / hygiene)
- [[HBR PRD]] — product requirements
- [[HBR CLI]] — command-line surface (in `CAE Design/`)
