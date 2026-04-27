---
description: system architecture
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Dev]]

# CAE Architecture

System-level design overview. For requirements and decisions, see [[CAE System Design]]. For module-level interfaces, see the module docs linked below.


## Process model

CAE is a single-process CLI tool. A command invocation either:

- **Short-lived** — submit, cancel, status: opens the store, performs the operation, exits.
- **Long-lived** — drain, run: spawns the scheduler thread and worker pool, processes pending tasks until the queue drains or the user interrupts.

There is no daemon, no background process, and no IPC. All coordination happens through the SQLite store.


## Thread layout

```
┌─────────────────────────────────────────────────────┐
│  Main thread                                         │
│    - parses CLI args                                 │
│    - opens TaskStore                                 │
│    - drives the scheduler for long-lived commands    │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│  Scheduler thread  (src/execution/scheduler.rs)      │
│    - holds the priority queue                        │
│    - feeds ready tasks to worker pool                │
│    - handles retry re-enqueue                        │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│  Worker pool  (src/execution/worker.rs)              │
│    - N worker threads                                │
│    - each pulls from a shared channel                │
│    - executes the shell command and reports back     │
└─────────────────────────────────────────────────────┘
```


## Modules

- [[CAE Scheduler\|src/execution/scheduler.rs]] — priority queue and dispatch logic
- `src/execution/worker.rs` — worker thread lifecycle (not yet documented)
- `src/retry.rs` — exponential backoff, centralized per [[CAE Rules#R04 — Retries Are Declared, Not Implicit\|R04]]
- `src/store.rs` — SQLite-backed TaskStore (not yet documented)
- `src/clock.rs` — injectable Clock trait, per [[CAE Rules#R02 — No sleep() in Production Paths\|R02]]


## Design principle traceability

Principles live in [[CAE Rules#Design Principles\|CAE Rules § Design Principles]] — the canonical source. Each principle's `Encoded by:` line lists the R-rules that enforce it. `/audit rules` scans the code against those rules.

If a new principle is added, the rule(s) that encode it go in the same edit — otherwise the principle is aspirational, not enforced.
