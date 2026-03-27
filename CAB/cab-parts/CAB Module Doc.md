# CAB Module Doc

Module docs describe the classes and interfaces in a software project's source code. Each source module (a file or logical grouping of files) gets its own markdown document. The docs mirror the source tree structure under `{NAME} Dev/`.

Below is a complete module doc for a hypothetical project "TSK" (Task Runner). The file would be named `TSK Scheduler.md` and live at `TSK Docs/TSK Dev/TSK execution/TSK Scheduler.md`. Actual module docs follow this structure.

# Reference Example
---
 [[TSK Architecture]] → [[TSK Execution]]

# TSK Scheduler

Orchestrates timed task execution with priority queuing and retry semantics. The Scheduler is the central dispatch engine for deferred work. It accepts tasks with deadlines, assigns them to worker threads from a managed pool, and handles retry logic when tasks fail. All scheduling decisions flow through a single priority queue to prevent starvation.

| CLASSES                | Description                                       |
| ---------------------- | ------------------------------------------------- |
| [[#TaskScheduler]]     | Priority queue engine for deferred task execution |
| [[#TaskHandle]]        | Async result handle returned by submit            |
| [[#TaskState]]         | Enum — lifecycle states for a task                |
| [[#SchedulerStatus]]   | Snapshot of current scheduler state               |

| TASK SCHEDULER ([[#^1\|details]])                                                      | Type / Returns    | Description                                      |
| -------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------ |
| `queue`                                                                                | PriorityQueue     | Pending tasks ordered by deadline                |
| `pool_size`                                                                            | int               | Number of worker threads                         |
| `retry_limit`                                                                          | int               | Max retries before marking failed                |
| `clock`                                                                                | Clock             | Time source (injectable for testing)             |
| **Methods**                                                                            |                   |                                                  |
| [[#submit(task: Callable, deadline: datetime) -> TaskHandle\|submit(task, deadline)]]  | TaskHandle        | Enqueue a task with a deadline                   |
| [[#cancel(handle: TaskHandle) -> bool\|cancel(handle)]]                                | bool              | Cancel a pending task by handle                  |
| [[#drain(timeout: float = None) -> List[TaskResult]\|drain(timeout)]]                  | List[TaskResult]  | Wait for all pending tasks to complete           |
| [[#status() -> SchedulerStatus\|status()]]                                             | SchedulerStatus   | Current queue depth, active workers, error count |


| TASK HANDLE ([[#^2\|details]])                                                         | Type / Returns    | Description                                      |
| -------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------ |
| `task_id`                                                                              | str               | Unique identifier for this task                  |
| `state`                                                                                | TaskState         | Current state: pending, running, done, failed    |
| **Methods**                                                                            |                   |                                                  |
| [[#await_result(timeout: float = None) -> TaskResult\|await_result(timeout)]]          | TaskResult        | Block until task completes                       |


| TASK STATE ([[#^3\|details]])                                                           | Description                                      |
| -------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Pending(deadline)                                                                      | Waiting in queue, scheduled for `deadline`       |
| Running                                                                                | Currently executing on a worker thread           |
| Done(result)                                                                           | Completed successfully with `result`             |
| Failed(error, attempts)                                                                | Failed after `attempts` retries                  |
| Cancelled                                                                              | Cancelled by caller via `cancel()`               |


| SCHEDULER STATUS ([[#^4\|details]])                                                    | Type / Returns    | Description                                      |
| -------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------ |
| `queue_depth`                                                                          | int               | Number of tasks waiting                          |
| `active_workers`                                                                       | int               | Workers currently executing tasks                |
| `error_count`                                                                          | int               | Total failed tasks since startup                 |



# Class Details


## TaskScheduler ^1

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



### METHOD DETAILS

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


## TaskHandle ^2

Returned by `submit()`. Represents an in-flight or completed task.



### METHOD DETAILS

### await_result(timeout: float = None) -> TaskResult

Block until the task completes or timeout expires.

**Args:**
- `timeout`: Max seconds to wait. `None` means wait indefinitely.

**Returns:** `TaskResult` with the outcome.

**Raises:**
- `TimeoutError`: If timeout expires before completion.


## TaskState ^3

Enum — lifecycle states for a task. See per-class table above for variant descriptions.


## SchedulerStatus ^4

Immutable snapshot of the scheduler's current state. Returned by `status()`.


## Protocol
```python
from typing import Protocol, Callable, List, Optional
from datetime import datetime

class TaskScheduler(Protocol):
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

The structure above is the canonical format for module docs. This section describes the precise rules for agents to follow.

## Location — Mirroring the Source Tree

Module docs live under `{NAME} Dev/` in a subfolder structure that **mirrors the repository's source tree**. Every source directory that contains modules gets a parallel documentation directory.

```
Repository (source)                    Documentation (vault)
─────────────────                      ────────────────────
src/                                   {NAME} Docs/{NAME} Dev/
├── execution/                         ├── {NAME} execution/
│   ├── scheduler.py                   │   ├── {NAME} Scheduler.md
│   └── worker.py                      │   └── {NAME} Worker.md
├── agent/                             ├── {NAME} agent/
│   ├── session.py                     │   ├── {NAME} Session.md
│   └── trace.py                       │   └── {NAME} Trace.md
└── infra/                             └── {NAME} infra/
    └── entity.py                          └── {NAME} Entity.md
```

### Mirroring Rules
- Every source directory gets a parallel `{NAME} {dir}/` folder in Dev
- Every source file with public API gets a `{NAME} {ClassName}.md` doc
- The doc file is named after the **primary class** in the source file, not the filename
- All files and folders carry the `{NAME}` prefix to avoid Obsidian namespace collisions
- Each doc subfolder can have a `{NAME} {dir}.md` dispatch page listing its module docs

### Full Dev Tree

```
{NAME} Docs/
└── {NAME} Dev/
    ├── {NAME} Dev.md                  Dispatch table — links to all module docs
    ├── {NAME} Architecture.md         System-level design
    ├── {NAME} Files.md                Repository file tree with descriptions
    ├── {NAME} execution/              ← mirrors src/execution/
    │   ├── {NAME} Scheduler.md        Module doc for TaskScheduler
    │   └── {NAME} Worker.md           Module doc for Worker
    └── {NAME} agent/                  ← mirrors src/agent/
        ├── {NAME} Session.md
        └── {NAME} Trace.md
```


## Document Structure — Precise Layout

The module doc has two main zones: the **overview zone** (everything at a glance) and the **class details zone** (deep dive per class).

### 1. Overview Zone

Everything the reader needs to understand the module without scrolling past the tables.

#### Line 1: Breadcrumb
Optional navigation: ` [[Parent Index]] → [[Subsystem]]`

#### H1: Module Name
`# {NAME} Scheduler` — the module name, prefixed with `{NAME}`. One blank line after.

#### Brief
One paragraph (2-4 sentences) immediately after H1. Describes the module's purpose and role.

#### CLASSES Table
One blank line after the brief. Two columns: `CLASSES` and `Description`.

- Each entry is a wiki-link to the class's H2 heading: `[[#TaskScheduler]]`
- Use the **source code class name** in PascalCase: `TaskScheduler`, not `Task Scheduler`
- One-line description per class

```markdown
| CLASSES              | Description                                       |
| -------------------- | ------------------------------------------------- |
| [[#TaskScheduler]]   | Priority queue engine for deferred task execution |
| [[#TaskHandle]]      | Async result handle returned by submit            |
```

#### Per-Class Tables
One table per class. **Double blank lines** between tables. Three columns.

**Header cell (top-left):** The class name in ALL CAPS with spaces between words, followed by a small `(details)` link using a block ID:

```markdown
| TASK SCHEDULER ([[#^1\|details]]) | Type / Returns | Description |
```

- ALL CAPS with spaces: `TaskScheduler` → `TASK SCHEDULER`, `TaskHandle` → `TASK HANDLE`
- The `([[#^1\|details]])` link targets the block ID on the H2 heading: `## TaskScheduler ^1`
- This links to just that one line, not the entire section
- Each class gets a unique block ID: `^1`, `^2`, `^3`, etc.

**Table body:**
- **Properties** listed first — name in backticks, type, description
- **`**Methods**`** — bold separator row, columns 2-3 left empty
- **Methods** listed after separator — name linked to METHOD DETAILS heading via `[[#full_signature\|short_name]]`, return type, description

```markdown
| TASK SCHEDULER ([[#^1\|details]])  | Type / Returns | Description                       |
| ---------------------------------- | -------------- | --------------------------------- |
| `queue`                            | PriorityQueue  | Pending tasks ordered by deadline |
| `pool_size`                        | int            | Number of worker threads          |
| **Methods**                        |                |                                   |
| [[#submit\|submit]]               | TaskHandle     | Enqueue a task with a deadline    |
| [[#cancel\|cancel]]               | bool           | Cancel a pending task by handle   |
```

#### Enum Tables
Enums use a **two-column** table instead of three — no Type/Returns column. Each row is a variant with its description. Include parameters in the variant name if the enum has associated data.

```markdown
| TASK STATE ([[#^3\|details]])      | Description                                |
| ---------------------------------- | ------------------------------------------ |
| Pending(deadline)                  | Waiting in queue, scheduled for `deadline` |
| Running                            | Currently executing on a worker thread     |
| Done(result)                       | Completed successfully with `result`       |
| Failed(error, attempts)            | Failed after `attempts` retries            |
| Cancelled                          | Cancelled by caller via `cancel()`         |
```

- Same ALL CAPS header with `(details)` link as struct/class tables
- Variant names in plain text (not backticks) — they're conceptual names, not code identifiers
- Parameters in parentheses when the variant carries data
- In the CLASSES table, prefix the description with `Enum —` to distinguish from structs: `Enum — lifecycle states for a task`


### 2. Class Details Zone

#### `# Class Details` (H1)
Three blank lines before this heading (standard H1 spacing). Contains all per-class detail sections.

#### Per-Class Section (H2)
Each class gets an H2 heading with the **source code class name** (PascalCase) and a block ID:

```markdown
## TaskScheduler ^1
```

- Use the exact PascalCase from source code: `TaskScheduler`, not `Task Scheduler` or `TASK SCHEDULER`
- The block ID (`^1`) matches the `details` link in the per-class table above
- **Two blank lines** between class sections (before each H2)

Contains:
- **Discussion subsections (H3)** — design decisions, usage patterns, important concepts
- **Code excerpts** — only when they clarify an interface that prose cannot

#### METHOD DETAILS (H3, ALL CAPS)
**Three blank lines** before `### METHOD DETAILS` to visually separate it from the discussion above.

Each method gets its own H3 heading with the **full signature**:

```markdown
### submit(task: Callable, deadline: datetime) -> TaskHandle
```

Body includes any of: **Args**, **Returns**, **Raises**, **Example** as needed. Simple methods that need no more than a table row can be omitted from METHOD DETAILS.

Simple classes (no methods or minimal discussion) can have just a one-line description under their H2, with no METHOD DETAILS section.


### 3. Optional Sections

#### Protocol Section (`## Protocol`)
Python Protocol or equivalent interface definition showing the public API contract.

#### See Also Section (`## See Also`)
Wiki-links to related module docs with brief notes on how they relate.


## Folder Docs

Every source folder that contains modules should have a **folder doc** — a module doc for the folder itself. Named `{NAME} {FolderName}.md` (e.g., `DMUX Speech.md`, `HA core.md`).

### Purpose

The folder doc describes the folder as a **coherent subsystem**: what it does, how the modules within it relate, and what API it presents to the rest of the system. This is often the most valuable documentation because it captures the architectural thinking that individual module docs can't.

### Structure

```markdown
# {NAME} {FolderName}

{1-2 sentences: what this subsystem does and why it exists.}

| MODULES                     | Description                          |
| --------------------------- | ------------------------------------ |
| [[{NAME} ModuleA\|ModuleA]] | What ModuleA does                    |
| [[{NAME} ModuleB\|ModuleB]] | What ModuleB does                    |
| [[{NAME} ModuleC\|ModuleC]] | What ModuleC does                    |

## Overview

{How the modules work together. Data flow, responsibilities, key interactions.
This is the high-value content — the folder-level architecture that you can't
see by reading individual module docs.}
```

### When the Folder IS an API

When the folder presents a coherent API (e.g., a Rust `mod.rs` that re-exports selected items, or a Swift folder that together implements a subsystem like "Speech"), the folder doc should describe:
- What the API offers to callers outside this folder
- Which module is the entry point
- The typical call sequence

### When the Folder is Just a Grouping

When the folder is just organizational (e.g., `utils/`), the folder doc is just the MODULES table with one-line descriptions. No need for an Overview section.

### Location

Folder docs live alongside the module docs they describe:

```
{NAME} Dev/
├── {NAME} core/
│   ├── {NAME} core.md              ← folder doc
│   ├── {NAME} Command.md           module doc
│   └── {NAME} Config.md            module doc
```

### Linking

Folder docs appear in:
- The **Dev dispatch table** as a row (often with its child modules listed inline)
- The **Files tree** as a wiki-link on the folder line


## Spacing Summary

| Between | Blank Lines |
|---------|-------------|
| H1 and brief paragraph | 1 (standard) |
| Brief and CLASSES table | 1 |
| CLASSES table and first per-class table | 1 |
| Between per-class tables | 2 |
| Last per-class table and `# Class Details` | 3 (standard H1) |
| Between class detail H2 sections | 2 |
| Discussion and `### METHOD DETAILS` | 3 |
| Between method H3 sections | 1 |


## Name Casing Summary

| Where | Casing | Example |
|-------|--------|---------|
| CLASSES table entries | PascalCase (source code) | `[[#TaskScheduler]]` |
| Per-class table header | ALL CAPS with spaces | `TASK SCHEDULER` |
| Class Details H2 heading | PascalCase (source code) | `## TaskScheduler ^1` |
| Method signatures | Exact source code | `submit(task, deadline)` |


## Proposed API Convention

During planning, module docs describe the *proposed* design before code exists. Mark each property, method, and type description with **(proposed)** inline — e.g., `Priority queue engine **(proposed)**`. Remove **(proposed)** from each item once the implementation matches.


## Linking Rule — CRITICAL

**Before writing a module doc, first add its entry to `{NAME} Dev.md` and `{NAME} Files.md`.** Do the linking first so you don't forget. An unlinked module doc is invisible — no one will find it.

- Add a row to the **Dev dispatch table** (`{NAME} Dev.md`) with a wiki-link and one-line description
- Add the file to the **Files tree** (`{NAME} Files.md`) in the correct location
- When creating multiple module docs in a batch, link ALL of them before writing any content. Then verify the Dev dispatch table has an entry for every module doc in the Dev folder.


## Lifecycle

Module docs are **living documents** — they must stay current with the code:

- **Create** when a new module is added — link to Dev and Files FIRST
- **Update** when the public interface or architecture changes
- **Outdated docs are worse than no docs** — if a module doc can't be kept current, delete it
