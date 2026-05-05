---
description: Pause the scheduler for maintenance windows
---

## Open Questions

- **Q2 — in-flight tasks on pause?** — when `pause()` is called, what happens to tasks currently executing on worker threads? Options: (a) let them finish then pause, (b) cancel them and re-enqueue on resume, (c) raise an error if any are in-flight. Leaning (a) but need user input on whether (b) is worth the complexity for hard-stop scenarios.

### Resolved

- **Q1 — pause scope: global or per-queue?** — **Resolution:** global only. CAE has a single queue by design ([[CAE Rules#P01 — One Queue, One Clock\|P01]]), so per-queue pause would contradict the principle. Incorporated into Design § API.



# [[CAE]] · F001 — Scheduler Pause

## Summary

Add a `pause()` / `resume()` pair to `TaskScheduler` so operators can halt new task dispatch during maintenance windows (deploys, database migrations) without tearing down the scheduler. Paused state persists across `status()` calls and is observable via `SchedulerStatus.paused: bool`.

## Interface

```rust
impl TaskScheduler {
    /// Stop dispatching new tasks. In-flight tasks continue to completion.
    /// Idempotent — calling pause on a paused scheduler is a no-op.
    pub fn pause(&self);

    /// Resume dispatching. Idempotent on an already-running scheduler.
    pub fn resume(&self);
}
```

Extended `SchedulerStatus`:

```rust
pub struct SchedulerStatus {
    pub queue_depth: usize,
    pub active_workers: usize,
    pub error_count: u64,
    pub paused: bool,   // NEW
}
```

## Requirements

- `pause()` prevents new tasks from being pulled from the queue
- In-flight tasks run to completion normally (pending Q2 resolution for the cancel variant)
- `submit()` still accepts new tasks while paused — they queue up, waiting for resume
- `status().paused` reflects current state
- Resume is non-blocking and returns immediately; workers pick up queued tasks as usual

## Design

A single `AtomicBool` on the scheduler, checked by the dispatch loop before each queue pull. No worker-thread state change needed — workers block on an empty channel when paused, same as when the queue is empty. `pause()` flips the bool to `true`; the dispatch loop stops enqueuing into the worker channel; `resume()` flips it back.

Integration with tests: deterministic via [[CAE Rules#P03 — Deterministic Tests\|P03]] — tests use `TestClock` to drive the dispatch loop one tick at a time, verifying that pause is honored at the first post-pause tick.

## Status

Designing — awaiting Q2 resolution.
