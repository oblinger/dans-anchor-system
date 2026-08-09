---
description: "worked System Design for the FEX scheduler — a detailed technical spec sitting under FEX Architecture, with rulings kept in their own file"
---

# FEX System Design
The scheduler's current technical design — modules, flows, data shapes — sitting one level below [[FEX Architecture]], with its rulings kept in a Decisions file rather than a section here.

| -[[FEX System Design]]- | → [[DAS]] → [[examples]] → [FEX System Design](hook://p/FEX%20System%20Design)  |
| --- | --- |
| Related | [[DAS System Design]],   |

**A constructed exemplar, not a quoted instance.** Every other file in this folder is abridged from something real; this one is composed, because the [[FEX Scheduler]] world has no live System Design to quote. What it demonstrates is the *kind* of document, not a required outline — [[DAS System Design]] has no fixed section spine, and the sections below are named after this system rather than copied from a template. A real one about a different system would name different sections.

The system described is the [[FEX Scheduler]] world, the same one [[FEX Architecture]] decomposes. Architecture answers *what the subsystems are and why*, at a high level; this document answers *how the current build is put together* — the module map, the data shapes, the flows.

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

## Where the rulings are

The invariants this design rests on — coordination flows only through the SQLite store, `Clock` is injected rather than read from the OS, retry policy is centralized, dead-lettering is terminal — are recorded in [[FEX Decisions]], not here.

That split is the facet's rule (`R-fct-system-design-05`), and it is what keeps this document readable: a design doc that also carries the decision log becomes the second place a reader has to check for a ruling, and anything reading the decision log misses the ones inlined here. This section exists to point, and to demonstrate that pointing is the shape.

# BRIEF

- **Don't read the section list as a template.** [[DAS System Design]] requires no fixed spine — these sections are named after the scheduler, and a System Design for a different system should be named after that one. The facet carried a four-H2 requirement until 2026-08-05, when it was re-derived from instances ([[TINK Backlog#^Q004|Q004]]) after measuring that it matched none of the 14 in the vault.
- **No `## Decisions` section here — that is checked** (`R-fct-system-design-05`). If a ruling needs recording while editing this file, it goes to [[FEX Decisions]].
- **Current spec only.** No changelog, no history, no deliberation — rationale belongs in [[DAS Discussion]], rulings in [[FEX Decisions]].
- **World consistency:** this is the [[FEX Scheduler]] / [[FEX Architecture]] system. Component and module names must agree with those files; when they drift, they are wrong here, since Architecture is the decomposition of record.
