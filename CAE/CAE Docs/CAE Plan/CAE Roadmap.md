---
description: milestones with checkbox tracking
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Roadmap

High-level milestones. Each item is a checkbox that flips when the milestone is delivered. Detailed work lives in [[CAE Backlog]] and individual feature specs.


## M1 — Single-task scheduling

- [x] Submit a task with a deadline
- [x] Run task on a worker thread at or after deadline
- [x] Return `TaskResult` to caller


## M2 — Priority queue and pool sizing

- [x] Multiple pending tasks ordered by deadline
- [x] Fixed-size worker pool with blocking pull
- [ ] Age-based promotion to prevent starvation


## M3 — Retry semantics

- [ ] Declared retry policy per-task
- [ ] Exponential backoff with configurable base
- [ ] Dead-letter list after retry exhaustion


## M4 — Persistence and CLI

- [ ] SQLite TaskStore with schema migrations
- [ ] `example-project submit`, `status`, `cancel`, `drain` subcommands
- [ ] Progress rendering for long-running drains
