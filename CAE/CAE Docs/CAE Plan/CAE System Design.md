---
description: architecture and design
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE System Design

| TOC |  |
| --- | --- |
| 1 | Overview |
| 2 | Design Principles |
| 3 | Component Diagram |
| 4 | Data Model |
| 5 | Decisions |



## 1 Overview

CAE is a single-process CLI scheduler. At startup it loads pending tasks from a SQLite store, spawns a fixed worker pool, and a scheduler thread that feeds the pool from a priority queue ordered by deadline.



## 2 Design Principles

Principles are stated in [[CAE Rules#Design Principles\|CAE Rules § Design Principles]] — that is the canonical location, and nothing here restates them. This section describes **how** this design applies each one.

- **[[CAE Rules#P01 — One Queue, One Clock\|P01]]** — realized by routing every submission through `TaskScheduler` and injecting `Clock` at construction time. See § 3 and decision D3.
- **[[CAE Rules#P02 — Fail Loudly, No Silent Fallbacks\|P02]]** — surfaced through the `TaskResult::Failed(error, attempts)` variant and the dead-letter list. Centralized retry (D4) is the only retry path.
- **[[CAE Rules#P03 — Deterministic Tests\|P03]]** — realized by the `Clock` trait in `src/clock.rs` and the mockable `TaskStore` boundary.



## 3 Component Diagram

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   CLI       │─────▶│  Scheduler   │─────▶│  Worker Pool │
│  (clap)     │      │  (priority)  │      │  (N threads) │
└─────────────┘      └──────┬───────┘      └──────┬───────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌──────────────┐
                     │ TaskStore    │      │ RetryManager │
                     │ (SQLite)     │      │              │
                     └──────────────┘      └──────────────┘
```



## 4 Data Model

Core entities — see module docs for full API:

| Entity | Module Doc | Purpose |
|--------|------------|---------|
| `Task` | [[CAE Scheduler]] | Submitted unit of work with deadline and retry policy |
| `TaskHandle` | [[CAE Scheduler]] | Async result handle returned by submit |
| `TaskResult` | [[CAE Scheduler]] | Outcome after execution: `Done`, `Failed`, `Cancelled` |



## 5 Decisions

| D | Decision | Rationale |
|---|----------|-----------|
| D1 | SQLite over JSON file for TaskStore | Durability, concurrent reads, no separate daemon |
| D2 | Fixed thread pool, not tokio | Simpler reasoning; tasks are shell commands, not I/O-bound |
| D3 | Single global queue, not per-priority | Preempts starvation via age-based promotion (see R01) |
| D4 | Retry logic in its own module | Centralizes policy; enforced by R04 |
