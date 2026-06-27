# CAE API Design
description:: programmatic surface of the `cae` Rust crate — types, signatures, error envelope, stability + compatibility commitments. Sibling to

| -[[CAE API Design]]- | : Programmatic Rust-crate surface — types, signatures, error envelope, stability + compatibility.<br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [[CAE Design]] → [CAE API Design](hook://p/CAE%20API%20Design) |
| --- | --- |
| [[CAE PRD]] | parent PRD — user stories drive this design |
| [[CAE UX Design]] | sibling — human CLI surface |
| [[CAE API Doc]] | downstream — per-module reference |
| [[CAB API Design]] | facet spec this doc follows |

**TL;DR.**
- Consumer: Rust code embedding `cae` as a library — typically a daemon or CLI wrapper scheduling tasks programmatically.
- Surface: one `Scheduler` struct with 6 methods (`open`, `submit`, `status`, `cancel`, `list`, `drain`) + `Task` builder.
- Error envelope: a single `CaeError` enum with named variants — `Result<T, CaeError>` everywhere.
- Stability: pre-1.0; minor bumps may break. At 1.0: deprecation honored ≥ 90 days; semver strict.
- Async: opt-in via `async` feature flag (tokio runtime). Sync by default — simpler integration, runtime-agnostic.

**Figure — canonical embed.**

```rust
use cae::{Scheduler, Task, RetryPolicy};
use std::time::{Duration, SystemTime};

let scheduler = Scheduler::open("/var/lib/cae")?;
let id = scheduler.submit(
    Task::new("python backup.py")
        .at(SystemTime::now() + Duration::from_secs(30 * 60))
        .with_retry(RetryPolicy::exponential(3, Duration::from_secs(5)))
)?;
println!("scheduled {id}");
```

## Consumer

A **Rust binary or library** that needs to submit and query deferred shell tasks without shelling out to the `cae` CLI. Two canonical shapes: (a) a long-running daemon (e.g. a deployment controller) that schedules cleanup tasks, (b) a CLI wrapper that wants programmatic access without the parse-output-of-`cae --json` indirection. Both call from sync code by default; an `async` feature flag enables a tokio-compatible variant.

Consumers do NOT include other languages — the C ABI is out of scope; for cross-language consumption the JSON form from [[CAE UX Design]] § Output shapes is the supported surface.

## Surface

The six methods on `Scheduler` cover the same lifecycle the CLI surfaces; the `Task` builder is the construction surface.

| Entry | Signature | Purpose | Source story |
|---|---|---|---|
| `Scheduler::open` | `fn open(path: impl AsRef<Path>) -> Result<Scheduler, CaeError>` | Open or create a task store at the given path. | US-CAE-1, US-CAE-2 |
| `Scheduler::open_with_clock` | `fn open_with_clock(path, clock: impl Clock + 'static) -> Result<Scheduler, CaeError>` | Same, with an injectable clock — for tests and simulated time. | (test-support) |
| `Scheduler::submit` | `fn submit(&self, task: Task) -> Result<TaskId, CaeError>` | Submit a task; returns the assigned ID. | US-CAE-1 |
| `Scheduler::status` | `fn status(&self, id: TaskId) -> Result<TaskState, CaeError>` | Fetch the current state of one task. | US-CAE-2 |
| `Scheduler::list` | `fn list(&self, filter: StateFilter) -> Result<Vec<TaskSummary>, CaeError>` | Enumerate tasks matching a filter; returns lightweight summaries. | US-CAE-2 |
| `Scheduler::cancel` | `fn cancel(&self, id: TaskId) -> Result<(), CaeError>` | Cancel a pending task. Idempotent — cancelling an already-cancelled task is `Ok(())`. | US-CAE-1 |
| `Scheduler::drain` | `fn drain(&self, timeout: Option<Duration>) -> Result<DrainOutcome, CaeError>` | Block until all running tasks finish (or timeout). | (operational) |
| `Task::new` | `fn new(cmd: impl Into<String>) -> Task` | Start building a Task with the given shell command. | US-CAE-1 |
| `Task::at` | `fn at(self, when: SystemTime) -> Task` | Set the scheduled run time. | US-CAE-1 |
| `Task::with_retry` | `fn with_retry(self, policy: RetryPolicy) -> Task` | Set the retry policy. | US-CAE-3 |
| `Task::with_priority` | `fn with_priority(self, priority: Priority) -> Task` | Set scheduling priority. | US-CAE-1 |
| `Task::with_client_token` | `fn with_client_token(self, token: impl Into<String>) -> Task` | Opt into idempotent submission keyed by token (see § Contract semantics). | US-CAE-1 |

All schema-bearing types (`Task`, `TaskState`, `TaskSummary`, `RetryPolicy`, `Priority`, `DrainOutcome`, `TaskId`) live in the `cae::models` module. See [[CAE API Doc]] for per-field documentation; this doc covers *intent*, not reference.

## Contract semantics

| Method | Idempotent? | Side-effects | Concurrency | Deadlines / timeouts |
|---|---|---|---|---|
| `open` | yes (returns the same handle shape) | creates the store file if absent | one `Scheduler` per process per path; cross-process use is unsupported pre-1.0 | none |
| `submit` | **only** when `client_token` is set on the Task; otherwise each call creates a new task | writes to store; assigns ID | safe across threads of one process | none on `submit` itself; the task's `--at` is the scheduled run time |
| `status` | yes; read-only | none | safe | none |
| `list` | yes; read-only | none | safe | filter evaluated eagerly; result is a point-in-time snapshot |
| `cancel` | yes — cancelling an already-cancelled or already-terminal task is `Ok(())` (no-op) | marks task cancelled in store; running tasks finish their current attempt | safe | none |
| `drain` | yes (returns `Completed` if nothing was running) | none on store; blocks the caller | safe to call from one thread | `timeout` is honored to ±100ms; `None` blocks indefinitely |

**Default policy: submit is NOT idempotent by default.** Submitting the same `Task::new("python backup.py").at(t)` twice schedules two tasks. Consumers wanting idempotency must opt in via `with_client_token(token)` — the store dedupes by token within a 24h window (configurable at `open`).

## Error model

One envelope across the entire surface — `Result<T, CaeError>`. Mixing forms (e.g. some methods returning `Result<T, MyError>`, others `Result<T, anyhow::Error>`) is forbidden by [[#RULESET R-api|R-api-05]].

```rust
#[derive(Debug, thiserror::Error)]
pub enum CaeError {
    #[error("cannot open store at {path}: {source}")]
    StoreUnavailable { path: PathBuf, source: std::io::Error },

    #[error("no task with id {id}")]
    TaskNotFound { id: TaskId },

    #[error("invalid time spec: {hint}")]
    InvalidTimeSpec { hint: String },

    #[error("task {id} already running — drain or cancel after current attempt")]
    AlreadyRunning { id: TaskId },

    #[error("task {id} cancelled before completion")]
    Cancelled { id: TaskId },

    #[error("internal error: {0}")]
    Internal(String),
}
```

Variants are **non-exhaustive** — `#[non_exhaustive]` on the enum so adding a variant in a minor release is not a breaking change. Consumers must use a wildcard arm.

Error mapping to CLI exit codes (for `cae` CLI binary that wraps the API): `StoreUnavailable → 74`, `TaskNotFound | InvalidTimeSpec → 64`, `AlreadyRunning → 75`, `Internal → 70`. The mapping lives in the CLI binary, not in the crate; the crate's enum is the source of truth for failure shape.

## Stability + compatibility

**Stability posture: pre-1.0 (`0.x`).** Minor version bumps (`0.4` → `0.5`) may include breaking changes; patch bumps (`0.4.1` → `0.4.2`) do not. Consumers should pin minor (`cae = "0.4"`) and read the CHANGELOG before a minor bump.

**At 1.0 (planned milestone):**

- **Semver strict.** Breaking changes require a major bump.
- **Deprecation horizon: ≥ 90 days.** A surface marked `#[deprecated(since = "1.x")]` is honored until the next major (or 90 days, whichever is longer). Removal lands in the major after the deprecation.
- **Internal vs public:** the `cae::internal` module is explicitly NOT part of the public surface — items there may change in any release. The contract is `pub use` re-exports from the crate root + items in non-`internal` modules.
- **Schema compatibility:** the on-disk task store (`tasks.db`, SQLite) is forward and backward compatible within a major. Migrations are automatic on `open`.

**Non-commitments (callers should not rely on):**

- Internal SQL schema of `tasks.db` (use the API, not the database).
- Exact retry-attempt timing — `RetryPolicy::exponential(n, base)` is the contract; the realized wait may vary ±20% (jitter).
- Log line shapes; CAE's structured logs are for operators, not for parsing.

## Design decisions

| ID | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| D-API1 | Sync API by default; `async` feature flag for tokio | Always-async (forces all callers onto tokio); never-async (excludes async consumers entirely) | Sync default is runtime-agnostic and simpler to integrate; async opt-in serves the tokio-aligned subset without forcing the choice. |
| D-API2 | Typed `CaeError` enum returned as `Result<T, CaeError>` | `Box<dyn Error>`; `anyhow::Result`; per-method error types | One envelope, statically known variants, no dynamic dispatch — consumers can `match` exhaustively and handle each named failure. `#[non_exhaustive]` keeps adding variants non-breaking. |
| D-API3 | Builder pattern for Task (`Task::new(cmd).at(time).with_retry(policy)`) | Struct literal (`Task { cmd, at, retry, ... }`); separate `submit_at` / `submit_with_retry` methods | Builder reads at the call site; defaults stay defaults (no need to spell out all fields); future additions don't break existing builders. |
| D-API4 | `Clock` trait injectable via `open_with_clock` | Real time always; test-only `#[cfg(test)]` clock | Production code uses `open`, tests use `open_with_clock` with `MockClock` — no `#[cfg(test)]` leakage in the public API; clock is a first-class concept. |
| D-API5 | Idempotent submit via opt-in `client_token`, not by default | Always idempotent (forces consumers to think about dedup); never idempotent (forces every retry-aware consumer to roll their own dedup) | Opt-in matches the common case (one-off submits) while letting retry-aware consumers (daemons retrying their own ops) opt in cleanly. |
| D-API6 | `list` returns lightweight `TaskSummary`; detail requires `status` | `list` returns full `Task` (heavyweight); two parallel surfaces | Listing is the high-frequency call (status dashboards); the summary form keeps the response small. Consumers wanting full detail call `status(id)` per row they care about. |
| D-API7 | `cancel` is idempotent (`Ok(())` on already-cancelled / terminal tasks) | Error variant `AlreadyCancelled` | Idempotent cancel matches common usage (defensive cancellation in cleanup paths); consumers that need to distinguish can call `status(id)` first. |
| D-API8 | `#[non_exhaustive]` on `CaeError` enum | Plain enum (adding variants is breaking) | Lets the crate add new failure modes in minor releases without forcing every consumer to bump. Consumers pay a wildcard arm; the crate pays no break-cost. |

## See also

- [[CAE PRD]] — user stories that drive this design.
- [[CAE UX Design]] — sibling facet covering the human CLI surface.
- [[CAE API Doc]] — per-module reference (auto-generated; *what exists*).
- [[CAE Architecture]] — internal organization that backs this surface.
- [[CAB API Design]] — facet spec; embedded [[#RULESET R-api|R-api]] ruleset.
