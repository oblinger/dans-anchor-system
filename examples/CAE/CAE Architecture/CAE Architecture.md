---
description: CAE system architecture — entry-point doc for the {NAME} Architecture/ folder anchor. Worked example of the CAB Architecture facet (section spine, visual-only diagrams, subsystem dispatch with link convention, API content lives elsewhere).
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Architecture](hook://p/CAE%20Architecture)

# CAE Architecture
CAE is a single-process CLI scheduler. A submitted task carries a deadline, a retry policy, and an opaque command payload; the scheduler enqueues it in a SQLite-backed priority store, dispatches to a fixed worker pool when ready, and routes failures through a centralized retry manager. No daemon, no IPC — every coordination decision flows through the SQLite store.

![[CAE Architecture.png]]

CLI submits tasks to the **Scheduler**, which dispatches to the **Worker Pool**, persists state in **TaskStore**, and consults **RetryManager** on failure. The injectable **Clock** (not shown — passed by reference at construction) is the time source every component reads from.

| -[[CAE Architecture]]- |  |
| --- | --- |
| [[CAE-Scheduler]] | priority queue engine + worker dispatch. Source: `src/execution/scheduler.rs`. |
| [CAE-Store] | SQLite-backed task persistence; load/save/mark-done. (subsystem doc not yet authored) |
| [CAE-Retry] | exponential backoff + dead-letter handling; centralized retry policy. (no doc yet) |
| [CAE-Clock] | injectable `Clock` trait; production `WallClock` + test `TestClock`. (no doc yet) |
| --- | |


> [!note] CAB Architecture convention
> Real subsystem docs use `[[double-bracket]]` wiki-links; placeholders for subsystems whose docs aren't authored use `[single-bracket]` plain text — visible inventory without polluting Obsidian's link graph. See [[CAB Architecture]] § Subsystem dispatch table.

For the public API surface (schemas, file formats, error types), see [[CAE API]].

## Module grouping

The five public modules fall into two coherent areas:

- **Scheduling core** — `execution` + `models`. The submit-run-drain pipeline; callers import here.
- **Infrastructure (internal)** — `retry` + `store` + `clock`. Plumbing; callers rarely touch directly.

Per-module class/function tables live in [[CAE-Scheduler]] (`execution` module) and [[CAE API]] (others, as subsystem docs are authored).

## Process model

A `cae` command invocation is either:

- **Short-lived** — `submit`, `cancel`, `status`: open the store, perform the operation, exit.
- **Long-lived** — `drain`, `run`: spawn the scheduler thread + worker pool, process pending tasks until the queue drains or the user interrupts.

## Thread layout

![[CAE Threads.png]]

## Design decisions

Tactical decisions specific to this architecture. Project-wide *principles* live in [[CAE Decisions]] and are referenced here, not restated.

| D    | Decision                                | Rationale                                                                |
| ---- | --------------------------------------- | ------------------------------------------------------------------------ |
| D1   | SQLite over JSON file for TaskStore     | Durability, concurrent reads, no separate daemon                          |
| D2   | Persistence is operator-readable        | `sqlite3 tasks.db` for production triage; no proprietary format           |
| D3   | Fixed thread pool, not tokio            | Simpler reasoning; tasks are shell commands, not I/O-bound                |
| D4   | Single global queue, not per-priority   | Preempts starvation via age-based promotion (see R01)                     |
| D5   | Retry logic in its own module           | Centralizes policy; enforced by R04                                       |

## Design principles application

How the project-wide principles in [[CAE Decisions|CAE Decisions § Principles]] are realized in this architecture:

- **[[CAE Decisions#D01 — One Queue, One Clock (sampled)|D01]]** — realized by routing every submission through `TaskScheduler` and injecting `Clock` at construction.
- **[[CAE Decisions#D09 — Fail Loudly, No Silent Fallbacks (checked)|D09]]** — surfaced through `TaskResult::Failed(error, attempts)` and the dead-letter list; centralized retry (D5) is the only retry path.
- **[[CAE Decisions#D03 — Deterministic Tests (sampled)|D03]]** — realized by the `Clock` trait and the mockable `TaskStore` boundary.

Each principle's `Encoded by:` line in [[CAE Decisions]] lists the R-rules that enforce it; `/audit rules` scans the code against those rules.

## See also

- [[CAE API]] — public API surface
- [[CAE-Scheduler]] — Scheduler subsystem (full class/function reference for `execution`)
- [[CAE Decisions]] — anchor-level applied choices (D11 cites R-diagram rules for the diagrams above)
- [[CAE Rules]] — adopted rulesets (currently R-diagram)
- [[R-diagram]] — the ruleset the diagrams above are audited against (structural / aesthetic / semantic / accessibility / hygiene)
- [[CAE PRD]] — product requirements
- [[CAE CLI]] — command-line surface (in `CAE Design/`)
