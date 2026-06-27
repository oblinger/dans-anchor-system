---
description: "priority queue engine and worker pool"
---
:>> [[CAE]] → [[CAE Architecture]] → [CAE Scheduler](hook://p/CAE%20Scheduler)

# CAE-Scheduler
Orchestrates timed task execution with priority queuing and retry semantics. The Scheduler is the central dispatch engine for deferred work. It accepts tasks with deadlines, assigns them to worker threads from a managed pool, and handles retry logic when tasks fail. All scheduling decisions flow through a single priority queue to prevent starvation (see [[CAE Decisions#D07 — One Queue, One Clock (checked)\|D07]]).

![[CAE Scheduler.svg|1200]]

*Priority and starvation* is the topic that governs the queue's ordering rule (deadline + aging promotion).

| SECTIONS                                             | Role                                                                                 |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [[#^TaskScheduler\|TaskScheduler]] class             | Priority queue engine that orchestrates deferred task execution                      |
| [[#^PriorityAndStarvation\|Priority and starvation]] | Aging-promotion rule that prevents low-priority tasks from being permanently delayed |
| [[#^TaskHandle\|TaskHandle]] class                   | Async result handle returned by `submit()`                                           |
| [[#^TaskState\|TaskState]] enum                      | Lifecycle states for a task                                                          |
| [[#^SchedulerStatus\|SchedulerStatus]] class         | Immutable snapshot of the scheduler's current state                                  |


## TaskScheduler Class
Priority queue engine that orchestrates deferred task execution. Owns the worker pool, the queue, and the retry policy — callers submit, get a handle back, and either await or cancel. Single instance per process; all timed work flows through it.^TaskScheduler

| TASK SCHEDULER CLASS                                                                       | Description                                      |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| **`queue`**`: PriorityQueue`                                                               | Pending tasks ordered by deadline                |
| **`pool_size`**`: int`                                                                     | Number of worker threads                         |
| **`retry_limit`**`: int`                                                                   | Max retries before marking failed                |
| **`clock`**`: Clock`                                                                       | Time source (injectable for testing)             |
| **Methods**                                                                                |                                                  |
| **[[#^TaskScheduler-submit\|submit]]**`(task: Callable, deadline: datetime) -> TaskHandle` | Enqueue a task with a deadline                   |
| **[[#^TaskScheduler-cancel\|cancel]]**`(handle: TaskHandle) -> bool`                       | Cancel a pending task by handle                  |
| **[[#^TaskScheduler-drain\|drain]]**`(timeout: float = None) -> List[TaskResult]`          | Wait for all pending tasks to complete           |
| **[[#^TaskScheduler-status\|status]]**`() -> SchedulerStatus`                              | Current queue depth, active workers, error count |


## Priority and starvation
Aging-promotion rule layered on top of strict deadline ordering. Without it, low-priority tasks behind a long backlog of higher-priority work would be permanently delayed; with it, every task is guaranteed forward progress proportional to wait time. The rule applies to scheduling decisions only — it does not preempt work already running.^PriorityAndStarvation

- **Deadline ordering** — Tasks pulled from the queue in deadline order; ties broken by submission order.
- **Aging promotion** — Tasks waiting longer than `2 × pool_size` scheduling cycles get promoted ahead of their deadline cohort.
- **Cohort jumping** — Promoted tasks jump to the front of their original cohort, NOT to absolute front of queue.
- **No preemption** — Promotion never interrupts running work; promoted tasks wait for the next available worker slot.
- **Rule reference** — [[CAE Decisions#D07 — One Queue, One Clock (checked)\|D07]] is the discipline that requires all scheduling decisions flow through this single queue.


## TaskHandle Class
Async result handle returned by `submit()`. Represents an in-flight or completed task — callers use it to check state, await the result, or pass back to `cancel()`. Cheap to copy; multiple awaiters on the same handle observe the same result.^TaskHandle

| TASK HANDLE CLASS                                                                               | Description                                   |
| ---------------------------------------------------------------------------------------- | --------------------------------------------- |
| **`task_id`**`: str`                                                                     | Unique identifier for this task               |
| **`state`**`: TaskState`                                                                 | Current state: pending, running, done, failed |
| **Methods**                                                                              |                                               |
| **[[#^TaskHandle-await_result\|await_result]]**`(timeout: float = None) -> TaskResult`   | Block until task completes                    |


## TaskState Enum
Enum representing the lifecycle states of a task. Variants carry the data each state needs to be meaningful — deadline for pending, result for done, error and attempt count for failed.^TaskState

| TASK STATE ENUM                                     | Description                                |
| --------------------------------------------- | ------------------------------------------ |
| **`Pending`**`(deadline: datetime)`           | Waiting in queue, scheduled for `deadline` |
| **`Running`**                                 | Currently executing on a worker thread     |
| **`Done`**`(result: TaskResult)`              | Completed successfully with `result`       |
| **`Failed`**`(error: Exception, attempts: int)` | Failed after `attempts` retries          |
| **`Cancelled`**                               | Cancelled by caller via `cancel()`         |


## SchedulerStatus Class
Immutable snapshot of the scheduler's current state. Returned by `status()` for monitoring and debugging. Safe to share across threads; reflects the scheduler at the instant `status()` was called.^SchedulerStatus

| SCHEDULER STATUS CLASS           | Description                       |
| ------------------------- | --------------------------------- |
| **`queue_depth`**`: int`  | Number of tasks waiting           |
| **`active_workers`**`: int` | Workers currently executing tasks |
| **`error_count`**`: int`  | Total failed tasks since startup  |







# Class Method Details


## TaskScheduler
### Retry semantics
Failed tasks re-enter the queue with an exponential backoff applied to their deadline:

```rust
let new_deadline = original_deadline + base_delay * 2u32.pow(attempt);
```

After `retry_limit` attempts, the task is moved to the dead-letter list and the caller's `TaskHandle` resolves with a `Failed` result. See [[CAE Decisions#D10 — Retries Are Declared, Not Implicit (checked)\|D10]] — all retry logic lives here, not in callers.

### Thread pool sizing
The pool is fixed at construction. Workers pull from the queue in a blocking loop. When `drain()` is called, no new submissions are accepted and the method blocks until the queue empties or the timeout expires.

### `submit(task: Callable, deadline: datetime) -> TaskHandle` ^TaskScheduler-submit
Enqueue a task for execution at or after `deadline`.

*Args:*
- **`task`**: A callable with no arguments. Side effects are the caller's responsibility.
- **`deadline`**: Earliest time the task should run. The scheduler may run it later under load.
- *Returns:* **`TaskHandle`** — can be awaited for the result or passed to `cancel()`.
- *Raises:* **`SchedulerShutdownError`** if called after `drain()` has been invoked.

### `cancel(handle: TaskHandle) -> bool` ^TaskScheduler-cancel
Cancel a pending task by its handle. Returns `false` if the task is already running or completed.

### `drain(timeout: float = None) -> List[TaskResult]` ^TaskScheduler-drain
Block until all pending and in-flight tasks complete.

*Args:*
- **`timeout`**: Max seconds to wait. `None` means wait indefinitely.
- *Returns:* **`List[TaskResult]`** — results for all tasks that completed during the drain.

### `status() -> SchedulerStatus` ^TaskScheduler-status
Return current scheduler state: queue depth, active workers, error count.


## TaskHandle
### `await_result(timeout: float = None) -> TaskResult` ^TaskHandle-await_result
Block until the task completes or timeout expires.

*Args:*
- **`timeout`**: Max seconds to wait. `None` means wait indefinitely.
- *Returns:* **`TaskResult`** with the outcome.
- *Raises:* **`TimeoutError`**: If timeout expires before completion.


## `execution` module API summary

Compact reference for the `execution` module's public surface. Class detail in the per-class H2 sections above; signatures and discussion in the per-method H3s.

| CLASSES              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `TaskScheduler`      | Priority queue engine for deferred task execution |
| `TaskHandle`         | Async result handle returned by submit            |
| `TaskState`          | Enum — lifecycle states for a task                |
| `SchedulerStatus`    | Snapshot of current scheduler state               |

| FUNCTIONS                         | Signature                                          | Purpose                       |
| --------------------------------- | -------------------------------------------------- | ----------------------------- |
| `TaskScheduler::submit`           | `(task, deadline) -> TaskHandle`                   | Enqueue a task                |
| `TaskScheduler::cancel`           | `(handle) -> bool`                                 | Cancel pending task           |
| `TaskScheduler::drain`            | `(timeout) -> List<TaskResult>`                    | Wait for completion           |
| `TaskScheduler::status`           | `() -> SchedulerStatus`                            | Current state snapshot        |

(Moved from `CAE Architecture.md` 2026-06-08 per CAB Architecture facet rule: per-module class/function tables live in the subsystem doc, not the architecture entry-point.)

## See Also

- [[CAE Architecture]] — system-level architecture (Scheduler's place in the broader picture)
- [[CAE API]] — public API surface (schemas, file formats, error types)
- `src/execution/worker.rs` — worker thread lifecycle
- `src/retry.rs` — backoff logic called by the scheduler
- `src/clock.rs` — injectable time source for testing