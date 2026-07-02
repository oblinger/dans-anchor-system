---
description: CAE system architecture — entry-point doc for the {NAME} Architecture/ folder anchor. Worked example of the CAB Architecture facet (section spine, visual-only diagrams, subsystem dispatch with link convention, API content lives elsewhere).
---
# CAE Architecture
CAE system architecture — a single-process CLI task scheduler over a SQLite-backed store.

| -[[CAE Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Architecture](hook://p/CAE%20Architecture)<br>: CAE system architecture |
| --- | --- |
| Related | [[CAE Decisions]],  [[CAE Rules]],  [[CAE API]],   |

## Overview

CAE is a single-process CLI scheduler. A submitted task carries a deadline, a retry policy, and an opaque command payload; the scheduler enqueues it in a SQLite-backed priority store, dispatches to a fixed worker pool when ready, and routes failures through a centralized retry manager. No daemon, no IPC — every coordination decision flows through the SQLite store.

## Architecture diagram

![[CAE Architecture.png]]

CLI submits tasks to the **Scheduler**, which dispatches to the **Worker Pool**, persists state in **TaskStore**, and consults **RetryManager** on failure. The injectable **Clock** (not shown — passed by reference at construction) is the time source every component reads from.

## Subsystems

| SUBSYSTEMS         | Description                                                                       |
| ------------------ | -------------------------------------------------------------------------------- |
| [[CAE-Scheduler]]  | priority queue engine + worker dispatch. Source: `src/execution/scheduler.rs`.    |
| [CAE-Store]        | SQLite-backed task persistence; load/save/mark-done. (subsystem doc not yet authored) |
| [CAE-Retry]        | exponential backoff + dead-letter handling; centralized retry policy. (no doc yet) |
| [CAE-Clock]        | injectable `Clock` trait; production `WallClock` + test `TestClock`. (no doc yet) |

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
| D4   | Single global queue, not per-priority   | Preempts starvation via age-based promotion                              |
| D5   | Retry logic in its own module           | Centralizes policy                                                        |

## See also

- [[CAE API]] — public API surface
- [[CAE-Scheduler]] — Scheduler subsystem (full class/function reference for `execution`)
- [[CAE Decisions]] — anchor-level applied choices
- [[CAE Rules]] — adopted rulesets (currently R-diagram)
- [[R-diagram]] — the ruleset the diagrams above are audited against
- [[CAE PRD]] — product requirements
