---
description: CAE public API surface — public modules, schemas, file formats, error types. The contract a caller imports against. Sub-document of CAE Architecture per CAB Architecture facet (worked example of {NAME} API.md placement).
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [[CAE Architecture]] → [CAE API](hook://p/CAE%20API)

# CAE API

Public API surface of the `cae_example` crate. Entry point: `src/lib.rs`. Re-exports the public modules so consumers can write `use cae_example::execution::TaskScheduler` without chasing the source tree.

This doc is the **caller's contract** — what the crate exposes, in what shapes, and how the wire formats look. For the internal *structure* (how the codebase is organized — which subsystem talks to which), see [[CAE Architecture]].

## Public modules

| Module                  | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `execution`             | Priority queue scheduler, worker pool, task lifecycle    |
| `retry`                 | Exponential backoff + dead-letter handling               |
| `store`                 | SQLite-backed `TaskStore` for persistence                |
| `clock`                 | Injectable `Clock` trait; production wall-clock impl     |
| `models`                | `Task`, `TaskResult`, `TaskState` structs used throughout |

Per-module class/function tables live in the relevant subsystem doc:

- `execution` API → [[CAE-Scheduler]]
- `retry` / `store` / `clock` / `models` → subsystem docs not yet authored; see [[CAE Architecture#Subsystems|CAE Architecture § Subsystems]] for the placeholder inventory.

## Schemas

The wire/persistence schemas the codebase produces and consumes — part of the public surface anyone integrating against `cae` (importing it as a library, reading its persistence format, consuming a `TaskResult` over IPC) sees.

**Task — submitted unit of work.** YAML/JSON-equivalent shape. Source of truth is `src/models.rs`.

| Field           | Type                  | Required | Description                                     |
| --------------- | --------------------- | -------- | ----------------------------------------------- |
| `id`            | UUID v7               | yes      | Server-assigned at submit                       |
| `command`       | string                | yes      | Opaque command payload, max 64 KiB              |
| `deadline`      | ISO-8601 timestamp    | yes      | When the task should run                        |
| `priority`      | `low` / `normal` / `high` | no   | Default `normal` (per F004)                     |
| `retry_policy`  | `RetryPolicy`         | no       | See below; default `{max_attempts: 3, base_delay: "1s"}` |

**RetryPolicy.**

| Field           | Type                  | Required | Description                                     |
| --------------- | --------------------- | -------- | ----------------------------------------------- |
| `max_attempts`  | int ≥ 1               | yes      | Total attempts including the first              |
| `base_delay`    | duration string       | yes      | First retry delay; subsequent doubled           |
| `dead_letter`   | string (queue name)   | no       | Where to route when exhausted                   |

**TaskResult — outcome shape.** Tagged union (sum type). Discriminator: `kind`.

| `kind`         | Additional fields                              | When                            |
| -------------- | ---------------------------------------------- | ------------------------------- |
| `Done`         | `value: {bytes}`                               | Task ran to completion          |
| `Failed`       | `error: string`, `attempts: int`               | All retries exhausted           |
| `Cancelled`    | (none)                                         | `cancel(handle)` was called     |

Schemas evolve under [[CAE Decisions#D02 — Fail Loudly (sampled)|D02]] — backward-incompatible field changes bump a `schema_version` discriminator (currently `v1`); never silently absorbed.

## File formats

Files the codebase reads or writes that are part of the contract with operators or other tools.

**`tasks.db` — SQLite TaskStore.** Single-file SQLite database written by `store::TaskStore`. Schema lives in `src/store/migrations/`.

| Table        | Columns (key)                                                 | Purpose                          |
| ------------ | ------------------------------------------------------------- | -------------------------------- |
| `tasks`      | `id` (PK), `command`, `deadline`, `priority`, `state`         | Submitted tasks; one row per     |
| `attempts`   | `task_id` (FK), `started_at`, `error`, `attempt_no`           | Per-attempt audit log            |
| `migrations` | `version`, `applied_at`                                       | Schema-version tracking          |

The DB file is consumer-readable; ops can `sqlite3 tasks.db "SELECT * FROM tasks WHERE state='Failed'"` to triage in production. This is intentional — see [[CAE Architecture#Design decisions|CAE Architecture § Design decisions]] D2.

**`cae.toml` — operator configuration.**

| Section          | Keys                                                                       |
| ---------------- | -------------------------------------------------------------------------- |
| `[scheduler]`    | `worker_count`, `queue_capacity`, `default_priority`                       |
| `[storage]`      | `db_path`, `wal_mode`, `vacuum_interval`                                   |
| `[retry]`        | `default_max_attempts`, `default_base_delay`, `dead_letter_queue`          |

Loaded once at startup. Hot-reload not supported; operators restart `cae` to pick up changes.

## Error types

Every public function returns `Result<T, CaeError>`. The error enum is part of the public API.

| Variant                         | When                                                   |
| ------------------------------- | ------------------------------------------------------ |
| `CaeError::QueueFull`           | `submit()` when `queue_capacity` is reached            |
| `CaeError::TaskNotFound(id)`    | `cancel()` or `status_of()` with unknown handle        |
| `CaeError::Storage(io)`         | Underlying SQLite I/O failure (DB locked, disk full)   |
| `CaeError::Schema(version)`     | DB on-disk schema mismatch with built binary           |

Per [[CAE Decisions#D02 — Fail Loudly (sampled)|D02]] all of these propagate to the caller — they never silently substitute a default.

## See also

- [[CAE Architecture]] — internal structure (subsystems, threads, decisions)
- [[CAE-Scheduler]] — Scheduler subsystem (full class/function reference for `execution`)
- [[CAE CLI]] — command-line surface (separate doc in `CAE Design/`)
