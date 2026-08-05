---
description: "worked System Design for the FEX scheduler — the four-section current-spec shape the DAS System Design facet specifies"
---

# FEX System Design
The scheduler's current technical architecture in the four sections [[DAS System Design]] requires — Architecture Overview, Components, Data Model, Decisions — and nothing else.

| -[[FEX System Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [FEX System Design](hook://p/FEX%20System%20Design)  |
| --- | --- |
| Related | [[DAS System Design]],   |

**A constructed exemplar, not a quoted instance.** Every other file in this folder is abridged from something real. This one is not, and the reason is worth stating plainly: **no System Design document in the vault currently matches this facet's declared structure.** The two mature instances carry `Components / Data Flow / Configuration / Key Design Constraints` and fifteen free-form H2s respectively. So this file shows what the spec *asks for*; whether the spec is what it should ask for is open — see [[TINK Backlog#^T116|T116]].

The system described is the [[FEX Scheduler]] world, the same one [[FEX Architecture]] decomposes. Architecture answers *what the subsystems are and why*; this document answers *what the current build is* — the component-to-module map, the data shapes, and the rulings in force.

## Architecture Overview

A single-process, multi-threaded CLI scheduler. The CLI parses commands and delegates to the Scheduler, which owns a priority queue and a fixed-size worker pool. Failures route through a central RetryManager rather than being handled at the worker; time is read from an injectable Clock so tests never sleep.

The component decomposition and its rationale live in [[FEX Architecture]] — including the figure. This section states the shape, not the argument for it.

## Components

| Component | Responsibility | Module |
|-----------|---------------|--------|
| **CLI** | Parse commands, format output | `cli.rs` |
| **Scheduler** | Coordinate queue, pool, and retries | `scheduler.rs` |
| **PriorityQueue** | Order ready tasks by deadline, then priority | `queue.rs` |
| **WorkerPool** | Execute tasks on a fixed thread set | `worker.rs` |
| **RetryManager** | Backoff policy, dead-letter routing | `retry.rs` |
| **TaskStore** | SQLite persistence; load, save, mark-done | `store.rs` |
| **Clock** | Time source, injectable for tests | `clock.rs` |

### Scheduler

Owns the run loop. Pops from PriorityQueue when a worker slot frees, hands the task to WorkerPool, and on failure passes the task to RetryManager rather than deciding retry policy itself. Holds no timer of its own — every deadline comparison reads Clock.

### RetryManager

Exponential backoff with a per-task attempt ceiling. A task that exhausts its attempts moves to the dead-letter list and is never requeued; nothing else in the system may resurrect it.

## Data Model

The store is one SQLite file. The load-bearing shapes:

- **`task`** — `(id, payload, priority, deadline_ms, attempts, state, created_at)`. `state` is one of `pending | running | done | dead`.
- **`attempt`** — `(id, task_id → task.id, started_at, finished_at, exit_code, error)`. One row per execution, so a dead-lettered task carries its full failure history.
- **`TaskHandle`** — the caller-facing value returned by submit; carries the task id and nothing else, so a stale handle cannot read stale state.

## Decisions

| # | Decision | Why |
|---|----------|-----|
| D01 | All coordination flows through the SQLite store | No IPC, no shared in-memory state between components; the store is the single point of truth and the only thing that must be locked. |
| D02 | `Clock` is injected, never read from the OS directly | A deadline-ordered scheduler is otherwise untestable without real sleeping; the test clock makes ordering assertions deterministic. |
| D03 | Retry policy is centralized in RetryManager | Per-worker retry produces divergent backoff behaviour that cannot be reasoned about or changed in one place. |
| D04 | Dead-lettering is terminal | An automatic resurrection path turns a persistent failure into an infinite one; requeueing a dead task is an explicit operator action. |

# BRIEF

- **This file demonstrates the facet's declared shape, and that shape is under review.** Do not cite it as evidence that the four-section structure is settled — it was written to *show* the spec, and the spec currently matches no real instance. If [[DAS System Design]] is re-derived from instances or folded into [[DAS Architecture]], this file follows it or retires with it.
- **Keep it to the four H2s.** The value of the exemplar is that it is exactly what the spec asks for. Adding a fifth section makes it stop demonstrating anything.
- **Current spec only.** No changelog, no history section, no deliberation — rationale belongs in [[DAS Discussion]], the decision *log* in [[DAS Decisions]]. The Decisions table here records what is in force, one line each.
- **World consistency:** this is the [[FEX Scheduler]] / [[FEX Architecture]] system. Component and module names must agree with those files; when they drift, they are wrong here, since Architecture is the decomposition of record.
