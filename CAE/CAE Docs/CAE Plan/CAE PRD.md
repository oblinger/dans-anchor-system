---
description: product requirements
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE PRD

| TOC |  |
| --- | --- |
| 1 | Overview |
| 2 | Design Workflow |
| 3 | Goals & Non-Goals |
| 4 | User Stories |



## 1 Overview

CAE Example is a CLI tool for scheduling and running deferred shell tasks with priority queuing and retry semantics. It replaces ad-hoc cron jobs and shell scripts with a unified, testable scheduling engine.



## 2 Design Workflow

| Step | Document | Purpose |
|------|----------|---------|
| 1 | CAE PRD.md | Clarify requirements and scope |
| 2 | [[CAE Open Questions]] | Surface and resolve unknowns |
| 3 | [[CAE System Design]] | Design technical architecture |
| 4 | [[CAE Rules]] | Encode design principles as auditable rules |



## 3 Goals & Non-Goals

### Goals
- Schedule tasks with deadlines and priority ordering
- Retry failed tasks with configurable backoff
- Provide clear CLI output for task status and history

### Non-Goals
- GUI interface (CLI only for v1)
- Distributed scheduling across multiple machines
- Sub-second task granularity



## 4 User Stories

### US-1: Schedule a Task
As a developer, I want to schedule a shell command to run at a specific time so that I can defer work to off-peak hours.

### US-2: Monitor Task Status
As a developer, I want to see which tasks are pending, running, and completed so that I can track progress.

### US-3: Retry Failed Tasks
As a developer, I want failed tasks to automatically retry with backoff so that transient failures don't require manual intervention.
