---
description: "CAE system architecture — worked example of the FCT Architecture facet"
---
# FEX Architecture
CAE is a single-process CLI scheduler. A submitted task carries a deadline, a retry policy, and an opaque command payload; the scheduler enqueues it in a SQLite-backed priority store, dispatches to a fixed worker pool when ready, and routes failures through a centralized retry manager. No daemon, no IPC — every coordination decision flows through the SQLite store.

![[CAE Architecture.png]]

CLI submits tasks to the **Scheduler**, which dispatches to the **Worker Pool**, persists state in **TaskStore**, and consults **RetryManager** on failure. The injectable **Clock** (not shown — passed by reference at construction) is the time source every component reads from.

| -[[FEX Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[DAS Design Docs]] → [FEX Architecture](hook://p/FEX%20Architecture)<br>: CAE system architecture — worked example of the FCT Architecture facet |
| --- | --- |
| [[FEX Scheduler]] | priority queue engine + worker dispatch. Source: `src/execution/scheduler.rs`. |
| [CAE-Store] | SQLite-backed task persistence; load/save/mark-done. (subsystem doc not yet authored) |
| [CAE-Retry] | exponential backoff + dead-letter handling; centralized retry policy. (no doc yet) |
| [CAE-Clock] | injectable `Clock` trait; production `WallClock` + test `TestClock`. (no doc yet) |
| --- | |
| [[DAS Common Testing Types]] | standard test-kind catalogue — generic strategy per kind, linked from each project's Testing tests-table |
| [[DAS API Design]] | facet spec for {slug} API Design.md — the programmatic (code-to-code or sub-skill) user surface |
| [[DAS CLI]] | The command-line specification facet — the full command surface for an anchor that ships a CLI, opened by a compressed `--help` figure (an SVG); a design-pipeline doc downstream of UX Design |
| [[DAS Completed Roadmap]] | completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap |
| [[DAS Decisions]] | decisions are documentation — recorded under a `## Decisions` section in the design doc they shape; Warden never computes against them. Anything directly checkable is a rule, living in the companion `# RULESET` directly after the Decisions section; rules link back with an implements-D<N> note. |
| [[DAS Design]] | design facet — the {slug} Design/ folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required) |
| [[DAS Files Architecture]] | the top-down design of a system's module & content structure — the file-tree architecture doc kind |
| [[DAS PRD]] | facet spec for {slug} PRD.md — the anchor's product requirements document |
| [[DAS Roadmap]] | facet spec for the project sequencing-design doc — milestones, shapes, and numbering |
| [[DAS Stories]] | facet spec for user stories as first-class siblings of a PRD — inline-bullet form for small PRDs, extracted-folder form for large ones |
| [[DAS System Design]] | the current technical-architecture document for a software project anchor |
| [[DAS Testing]] | testing facet — the project's testing strategy (kinds, amounts, responsibilities) followed by an overview of the actual tests proposed, consistent with that strategy. Low-level test specs live in module docs, not here. |
| [[DAS UX Design]] | facet spec for `{slug} UX Design.md` — the human user-facing surface (CLI commands, screens, organization, naming, output shapes, error voice) |
| [[FEX API Design]] | programmatic surface of the `cae` Rust crate — types, signatures, error envelope, stability + compatibility commitments. Sibling to |
| [[FEX Completed Roadmap]] | companion to CAE Roadmap; preserved migrated milestones with their structure; newest-on-top. |
| [[FEX Decisions Details]] |  |
| [[FEX Roadmap]] | sequencing-design — milestones + ordering (moved from Track 2026-06-10) |
| [[FEX Stories]] | three user stories — index for US-CAE-1..3 (folder-form per |
| [[FCT Design Docs/DAS US-CAE-1 — Schedule a Task]] | Schedule a deferred shell task with absolute or relative time |
| [[DAS US-CAE-2 — Monitor Task Status]] | Show task state grouped by pending / running / done / failed |
| [[DAS US-CAE-3 — Retry Failed Tasks]] | Auto-retry failed tasks with exponential backoff to a cap |


> [!note] FCT Architecture convention
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
