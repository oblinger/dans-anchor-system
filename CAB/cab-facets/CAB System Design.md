---
description: architecture and system design
---
# CAB System Design

The System Design document (`{NAME} System Design.md`) specifies the technical architecture, component boundaries, data models, and APIs for a software project. It contains the current design — not the history of how it was reached.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK System Design

| TOC |  |
| --- | --- |
| 1 | Architecture Overview |
| 2 | Components |
| 3 | Data Model |
| 4 | Decisions |



## 1 Architecture Overview

Task Runner uses a single-process, multi-threaded architecture. The CLI parses commands and delegates to the Scheduler, which manages a priority queue and a fixed-size thread pool.

```
CLI → Scheduler → PriorityQueue → WorkerPool → TaskResult
                       ↑
                  RetryManager (requeues failed tasks)
```



## 2 Components

| Component | Responsibility | Module |
|-----------|---------------|--------|
| **CLI** | Parse commands, format output | `cli.py` |
| **Scheduler** | Coordinate queue, pool, retries | `scheduler.py` |
| **WorkerPool** | Execute tasks in threads | `worker.py` |
| **RetryManager** | Backoff logic, dead-letter list | `retry.py` |
| **Clock** | Time source (injectable for tests) | `clock.py` |

### Scheduler
The scheduler is the central dispatch engine. It owns the priority queue and worker pool. All task submission, cancellation, and draining flows through the scheduler.

### RetryManager
On task failure, the retry manager computes the next deadline using exponential backoff capped at `3 × task_duration` for short tasks. After `retry_limit` attempts, the task moves to the dead-letter list.



## 3 Data Model

```python
@dataclass
class Task:
    id: str
    command: str
    deadline: datetime
    priority: int = 0
    attempt: int = 0

@dataclass
class TaskResult:
    task_id: str
    exit_code: int
    stdout: str
    duration: float
```



## 4 Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Thread pool over async | Shell subprocesses don't benefit from async; threads are simpler |
| D2 | UTC internally | Avoids timezone bugs; CLI handles local↔UTC conversion |
| D3 | Fixed pool size | Dynamic sizing adds complexity without measurable benefit at target scale |

---



# Format Specification

## Location

`{NAME} System Design.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Document Structure

### TOC
A table of contents at the top linking to major sections.

### Architecture Overview
High-level description of the system with an ASCII diagram showing component relationships and data flow.

### Components
A summary table listing each component, its responsibility, and its source module. Followed by H3 subsections for components that need detailed explanation.

### Data Model
Key data structures shown as code blocks (dataclasses, schemas, or equivalent).

### Decisions
A numbered table recording architectural decisions with rationale. Each decision is a short statement with a one-line justification. Extended analysis belongs in [[CAB Discussion]].

## Lifecycle

- **Create** after the PRD and Open Questions have stabilized enough to design against
- **Update** when architecture changes — this is the current spec, not a historical log
- **Decisions table** grows over time as new architectural choices are made
- **Current spec only** — rationale and alternatives belong in Discussion
