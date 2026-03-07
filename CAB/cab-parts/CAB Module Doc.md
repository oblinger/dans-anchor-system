# CAB Module Doc

Module docs describe the classes and interfaces in a software project's source code. Each source module (a file or logical grouping of files) gets its own markdown document. The docs mirror the source tree structure under `{NAME} Dev/`.

Below is a complete module doc for a hypothetical project "TSK" (Task Runner). The file would be named `TSK Scheduler.md` and live at `TSK Dev/execution/TSK Scheduler.md`. Actual module docs follow this structure.

# Reference Example
---
 [[TSK Architecture]] → [[TSK Execution]]

# TSK Scheduler

Orchestrates timed task execution with priority queuing and retry semantics. The Scheduler is the central dispatch engine for deferred work. It accepts tasks with deadlines, assigns them to worker threads from a managed pool, and handles retry logic when tasks fail. All scheduling decisions flow through a single priority queue to prevent starvation.

| PROPERTIES    | Type          | Description                          |
| ------------- | ------------- | ------------------------------------ |
| `queue`       | PriorityQueue | Pending tasks ordered by deadline    |
| `pool_size`   | int           | Number of worker threads             |
| `retry_limit` | int           | Max retries before marking failed    |
| `clock`       | Clock         | Time source (injectable for testing) |

| METHODS                                                                                               | Returns          | Description                                      |
| ----------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------ |
| [[#submit(task: Callable, deadline: datetime) -> TaskHandle\|submit(task, deadline)]]                 | TaskHandle       | Enqueue a task with a deadline                   |
| [[#cancel(handle: TaskHandle) -> bool\|cancel(handle)]]                                              | bool             | Cancel a pending task by handle                  |
| [[#drain(timeout: float = None) -> List[TaskResult]\|drain(timeout)]]                                | List[TaskResult] | Wait for all pending tasks to complete           |
| [[#status() -> SchedulerStatus\|status()]]                                                           | SchedulerStatus  | Current queue depth, active workers, error count |

## Discussion

### Priority and Starvation
Tasks are ordered by deadline. To prevent old low-priority tasks from starving, the scheduler promotes any task that has waited longer than `2 × pool_size` scheduling cycles. Promoted tasks jump to the front of their deadline cohort but do not preempt running work.

### Retry Semantics
Failed tasks re-enter the queue with an exponential backoff applied to their deadline:

```python
new_deadline = original_deadline + base_delay * (2 ** attempt)
```

After `retry_limit` attempts, the task is moved to the dead-letter list and the caller's `TaskHandle` resolves with a `FailedResult`.

### Thread Pool Sizing
The pool is fixed at construction. Workers pull from the queue in a blocking loop. When `drain()` is called, no new submissions are accepted and the method blocks until the queue empties or the timeout expires.

## Method Details

### submit(task: Callable, deadline: datetime) -> TaskHandle

Enqueue a task for execution at or after `deadline`.

**Args:**
- `task`: A callable with no arguments. Side effects are the caller's responsibility.
- `deadline`: Earliest time the task should run. The scheduler may run it later under load.

**Returns:** A `TaskHandle` that can be awaited for the result or passed to `cancel()`.

**Raises:**
- `SchedulerShutdownError`: If called after `drain()` has been invoked.

### cancel(handle: TaskHandle) -> bool

Cancel a pending task by its handle. Returns `False` if the task is already running or completed.

### drain(timeout: float = None) -> List[TaskResult]

Block until all pending and in-flight tasks complete.

**Args:**
- `timeout`: Max seconds to wait. `None` means wait indefinitely.

**Returns:** Results for all tasks that completed during the drain.

### status() -> SchedulerStatus

Return current scheduler state: queue depth, active workers, error count.

## Protocol
```python
from typing import Protocol, Callable, List, Optional
from datetime import datetime

class Scheduler(Protocol):
    """Task scheduling engine."""

    @property
    def pool_size(self) -> int:
        """Number of worker threads."""
        ...

    def submit(self, task: Callable, deadline: datetime) -> TaskHandle:
        """Enqueue a task with a deadline."""
        ...

    def cancel(self, handle: TaskHandle) -> bool:
        """Cancel a pending task. Returns False if already running."""
        ...

    def drain(self, timeout: Optional[float] = None) -> List[TaskResult]:
        """Wait for all tasks to complete."""
        ...

    def status(self) -> SchedulerStatus:
        """Current scheduler state."""
        ...
```

## See Also
- [[TSK Worker]] - Thread pool worker lifecycle
- [[TSK TaskHandle]] - Async result handle
- [[TSK Clock]] - Injectable time source for testing

---



# Format Specification

The structure above is the canonical format for module docs. This section describes the rules.

## Location

Module docs live under `{NAME} Dev/` in a subfolder structure that mirrors the source tree:

```
{NAME} Docs/
└── {NAME} Dev/
    ├── {NAME} Dev.md                  Dispatch page (links Files + all module aggregators)
    ├── {NAME} Architecture.md         System-level design
    ├── {NAME} bio/                    ← mirrors src/bio/
    │   ├── {NAME} bio.md              Module doc for the folder
    │   ├── {NAME} Simulator.md
    │   ├── {NAME} State.md
    │   └── {NAME} Chemistry.md
    ├── {NAME} agent/                  ← mirrors src/agent/
    │   ├── {NAME} agent.md
    │   ├── {NAME} Session.md
    │   └── {NAME} Trace.md
    └── {NAME} infra/                  ← mirrors src/infra/
        ├── {NAME} infra.md
        └── {NAME} Entity.md
```

All files and folders carry the `{NAME}` prefix to avoid collisions in the shared Obsidian namespace.

## Document Structure

### Top Matter
1. **Breadcrumb** — Optional navigation line: ` [[Parent Index]] → [[Subsystem]]`
2. **H1** — The class or module name (e.g., `# Scheduler`)
3. **Brief** — One-sentence description immediately after H1, no blank line

### Module Summary Table
When a module contains more than 3 classes or structs, start with a summary table listing all types:

| TYPES | Description |
|-------|-------------|
| `Scheduler` | Priority queue engine for deferred work |
| `TaskHandle` | Async result handle returned by submit |
| `TaskResult` | Outcome of a completed or failed task |

This orients readers before the per-class detail sections.

### Overview Section
- Short paragraph (2–4 sentences) on purpose and role
- **Properties table** — `| PROPERTIES | Type | Description |`
- **Methods table** — `| METHODS | Returns | Description |`
- No headings above the tables — the tables have their own header rows
- Method names in the table link to their Method Details heading using `[[#method_name]]` so readers can jump to the full description

### Proposed API Convention
During planning, module docs describe the *proposed* design before code exists. Mark each property, method, and type description with **(proposed)** inline — e.g., `Priority queue engine **(proposed)**`. Remove **(proposed)** from each item once the implementation matches. This makes module docs the living spec: during planning they show what will be built; during execution they converge toward what exists.

### Discussion Section
- Design decisions, usage patterns, important concepts
- H3 subsections as needed
- Code excerpts only when they clarify an interface that prose cannot

### Method Details Section
- One H3 per method that needs more than a table row can convey
- H3 heading is the full signature (e.g., `### submit(task: Callable, deadline: datetime) -> TaskHandle`)
- In the methods table, link to the heading using `[[#heading|display]]` syntax: `[[#submit(task: Callable, deadline: datetime) -> TaskHandle|submit(task, deadline)]]`
- Body includes **Args**, **Returns**, **Raises**, **Example** as needed

### Protocol Section
- Python Protocol (or equivalent interface definition) showing the public API
- This is the contract — implementations must satisfy it

### See Also Section
- Wiki-links to related module docs
- Brief note on how they relate

## Lifecycle

Module docs are **living documents** — they must stay current with the code:

- **Create** when a new module is added
- **Update** when the public interface or architecture changes
- **Outdated docs are worse than no docs** — if a module doc can't be kept current, delete it
