---
description: priority queue engine and worker pool
---
:>> [[CAE]] → [[CAE Docs]] → [[CAE Dev]] → [[CAE Architecture]]

# CAE Scheduler

Orchestrates timed task execution with priority queuing and retry semantics. The Scheduler is the central dispatch engine for deferred work. It accepts tasks with deadlines, assigns them to worker threads from a managed pool, and handles retry logic when tasks fail. All scheduling decisions flow through a single priority queue to prevent starvation (see [[CAE Rules#R01 — One Queue, One Clock\|R01]]).

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


| TASK STATE ([[#^3\|details]])                                                          | Description                                      |
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

```rust
let new_deadline = original_deadline + base_delay * 2u32.pow(attempt);
```

After `retry_limit` attempts, the task is moved to the dead-letter list and the caller's `TaskHandle` resolves with a `Failed` result. See [[CAE Rules#R04 — Retries Are Declared, Not Implicit\|R04]] — all retry logic lives here, not in callers.

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

Cancel a pending task by its handle. Returns `false` if the task is already running or completed.

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


## See Also

- `src/execution/worker.rs` — worker thread lifecycle
- `src/retry.rs` — backoff logic called by the scheduler
- `src/clock.rs` — injectable time source for testing
