---
description: Crate-wide public surface — everything cae-example exposes
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Dev]]

# CAE Rollup

Entry point (`src/lib.rs`). Re-exports the public modules so consumers can write `use cae_example::execution::TaskScheduler` without chasing the source tree.

This page is also the **canonical whole-codebase overview** — every public type and top-level function appears in a table below. For per-module prose and discussion, drill into the module docs linked in each section.

Source: `src/lib.rs`

## Public Modules

| Module                  | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `execution`             | Priority queue scheduler, worker pool, task lifecycle    |
| `retry`                 | Exponential backoff + dead-letter handling               |
| `store`                 | SQLite-backed `TaskStore` for persistence                |
| `clock`                 | Injectable `Clock` trait; production wall-clock impl     |
| `models`                | `Task`, `TaskResult`, `TaskState` structs used throughout |

## How They Group

Five modules fall into three coherent areas. Callers typically import from `execution` (for scheduling) plus `models` (for task types); the other three are infrastructure.

### Group 1 — Scheduling core

The submit-run-drain pipeline. A caller lives here.

| Module        | Role                                                |
| ------------- | --------------------------------------------------- |
| `execution`   | `TaskScheduler`, `Worker`, feeds tasks to the pool  |
| `models`      | Task/result types exchanged across the boundary     |

### Group 2 — Infrastructure (internal)

Plumbing; callers rarely touch these directly.

| Module        | Role                                                |
| ------------- | --------------------------------------------------- |
| `retry`       | Backoff policy; used only by `execution`            |
| `store`       | Task persistence; used by `execution` at startup    |
| `clock`       | Time source injected into `execution`               |

### Group 3 — (none — all infra is in Group 2)

---

## execution — Scheduler and worker pool

See [[CAE Scheduler]] for detail.

| CLASSES              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `TaskScheduler`      | Priority queue engine for deferred task execution |
| `TaskHandle`         | Async result handle returned by submit            |
| `TaskState`          | Enum — lifecycle states for a task                |
| `SchedulerStatus`    | Snapshot of current scheduler state               |

| FUNCTIONS                         | Signature                                          | Purpose                       |
| --------------------------------- | -------------------------------------------------- | ----------------------------- |
| `TaskScheduler::submit`           | `(task, deadline) -> TaskHandle`                   | Enqueue a task                |
| `TaskScheduler::cancel`           | `(handle) -> bool`                                 | Cancel pending task           |
| `TaskScheduler::drain`            | `(timeout) -> List<TaskResult>`                    | Wait for completion           |
| `TaskScheduler::status`           | `() -> SchedulerStatus`                            | Current state snapshot        |

---

## retry — Exponential backoff

Centralized retry policy. All retries flow through this module; see [[CAE Rules#R04 — Retries Are Declared, Not Implicit\|R04]].

| CLASSES         | Description                                          |
| --------------- | ---------------------------------------------------- |
| `RetryPolicy`   | Declared policy — `{max_attempts, base_delay}`       |

| FUNCTIONS               | Signature                                          | Purpose                          |
| ----------------------- | -------------------------------------------------- | -------------------------------- |
| `RetryPolicy::next_at`  | `(attempt, original_deadline) -> Instant`          | Next deadline after a failure    |
| `RetryPolicy::exhausted`| `(attempt) -> bool`                                | True when attempt >= max         |

---

## store — SQLite TaskStore

Task persistence. Not yet documented in a module doc — the rollup holds the summary until it exists.

| CLASSES       | Description                                      |
| ------------- | ------------------------------------------------ |
| `TaskStore`   | SQLite-backed store; load, save, mark-done       |

---

## clock — Injectable time source

Used by `execution` to keep tests deterministic. See [[CAE Rules#P03 — Deterministic Tests\|P03]].

| CLASSES          | Description                                      |
| ---------------- | ------------------------------------------------ |
| `Clock` (trait)  | `now() -> Instant`                               |
| `WallClock`      | Production impl; delegates to `std::time`        |
| `TestClock`      | Mock used in tests; time advanced explicitly     |

---

## models — Task types

Shared types used across every module.

| CLASSES           | Description                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| `Task`            | Submitted unit of work; carries deadline, retry policy, command                    |
| `TaskResult`      | Enum — `Done(value)`, `Failed(error, attempts)`, `Cancelled`                       |
| `TaskState`       | Enum — `Pending`, `Running`, `Done`, `Failed`, `Cancelled`                         |

---

## See Also

- [[CAE Architecture]] — thread model and dependency graph
- [[CAE Files]] — source tree with per-file links
- [[CAE System Design]] — decisions D1–D4 that shape the above
