---
description: "CAE system architecture — worked example of the DAS Architecture facet"
---

| -[[FEX Architecture]]- | : CAE system architecture — worked example of the DAS Architecture facet<br>→ [[DAS]] → [[FEX]] → [FEX Architecture](hook://p/FEX%20Architecture)  |
| --- | --- |
| [[FEX Scheduler\|Scheduler]]  | priority queue engine + worker dispatch. Source: `src/execution/scheduler.rs`. |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[BRDG]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DVT]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Dispatch Examples\|Dispatch Examples]],  [[FEX Empty\|Empty]],  [[FEX Facet\|Facet]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Minimal Facet\|Minimal Facet]],  [[FEX Minimal Skill\|Minimal Skill]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Skill\|Skill]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR]],  [[HBR PRD User Stories]],  [[HHOP]],  [[HRUN]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# FEX Architecture
CAE is a single-process CLI task scheduler — one queue, one clock, SQLite-backed.

| Card |  |
| --- | --- |
| **[CAE-Store]** | SQLite-backed task persistence; load/save/mark-done. (subsystem doc not yet authored) |
| **[CAE-Retry]** | exponential backoff + dead-letter handling; centralized retry policy. (no doc yet) |
| **[CAE-Clock]** | injectable `Clock` trait; production `WallClock` + test `TestClock`. (no doc yet) |


![[FEX Architecture.svg|2400]]

| Part | Role | Module |
|---|---|---|
| [[FEX Empty\|CLI]] | `submit` · `cancel` · `status` · `drain` · `run` — short-lived commands read the store directly | — |
| [[FEX Scheduler\|Scheduler]] | the single global priority queue with age-based promotion; dispatches when a task is ready | `execution` |
| [[FEX Empty\|Worker Pool]] | fixed threads (`w1…wN`), not tokio, running the task's command payload | `execution` |
| [[FEX Empty\|TaskStore]] | SQLite persistence — load, save, mark-done; operator-readable | `store` |
| [[FEX Empty\|RetryManager]] | exponential backoff, reschedule, dead-letter after `retry_limit` | `retry` |
| [[FEX Empty\|Clock]] | the injectable time source every component reads — `WallClock` in production, `TestClock` in tests (passed by reference, not drawn) | `clock` |

## Overview

A submitted task carries a deadline, a retry policy, and an opaque command payload; the scheduler enqueues it in the SQLite-backed priority store, dispatches to the fixed worker pool when ready, and routes failures through the centralized retry manager. No daemon, no network — a `cae` invocation is either a short-lived store operation or a long-lived drain. CLI submits to the **Scheduler**, which dispatches to the **Worker Pool**, persists state in **TaskStore**, and consults **RetryManager** on failure; the **Clock** is the one time source.

> [!note] DAS Architecture convention
> Real subsystem docs use `[[double-bracket]]` wiki-links; in the **spine**, placeholders for subsystems whose docs aren't authored use `[single-bracket]` plain text — visible inventory without polluting Obsidian's link graph. See [[DAS Architecture]] § Subsystem dispatch table. In the **parts table under the figure** this example uses pretend links to [[FEX Empty]] instead, so each row is clickable without minting a page.

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

![[FEX Threads.svg|2400]]

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
