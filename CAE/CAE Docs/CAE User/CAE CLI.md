---
description: command reference — every command, flag, exit code
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE User]]

# CAE CLI

```
example-project --help                                                            # Show this help text
example-project --version                                                         # Print version
example-project submit --deadline <time> [--retry N] [--priority 0-9] -- <cmd>    # Enqueue a task at the deadline
example-project status [--json] [--filter <state>]                                # Show task states and queue depth
example-project cancel <task-id>                                                  # Cancel a pending task by ID
example-project drain [--timeout <sec>]                                           # Wait for all pending tasks to complete
example-project pause                                                             # Stop dispatching new tasks (maintenance window)
example-project resume                                                            # Resume dispatching
```

For a tutorial introduction, see [[CAE User Guide]]. Per-command detail below: [[#submit]], [[#status]], [[#cancel]], [[#drain]], [[#pause]], [[#resume]].


## submit

Enqueue a task for execution at or after a deadline.

**Usage:**
```
example-project submit --deadline <ISO-8601> [--retry <N>] [--priority <0-9>] -- <command> [args...]
```

**Flags:**

| Flag           | Type        | Default | Description                                             |
|----------------|-------------|---------|---------------------------------------------------------|
| `--deadline`   | ISO-8601    | —       | Earliest time the task should run. Required.            |
| `--retry`      | int         | 3       | Max retries before the task is marked failed.           |
| `--priority`   | 0–9         | 5       | Higher = runs sooner among same-deadline set.           |

**Exit codes:**

| Code | Meaning                                         |
|------|-------------------------------------------------|
| 0    | Task enqueued; task ID printed on stdout.       |
| 1    | Usage error (missing required flag, bad time). |
| 2    | Scheduler unreachable or shutdown.              |

**Example:**
```bash
example-project submit --deadline 2026-04-21T15:00:00 --retry 5 -- ./build.sh
# → t-4f2
```


## status

Print current scheduler state and task list.

**Usage:**
```
example-project status [--json] [--filter <state>]
```

**Flags:**

| Flag          | Type                         | Default | Description                                 |
|---------------|------------------------------|---------|---------------------------------------------|
| `--json`      | bool                         | false   | Emit JSON instead of the default table.     |
| `--filter`    | pending\|running\|done\|failed | (all)  | Show only tasks in the given state.         |

**Example:**
```bash
example-project status --filter running
# ID       STATE      DEADLINE              COMMAND
# t-4f2    running    2026-04-21 15:00:00   ./build.sh
```


## cancel

Cancel a pending task by ID. Has no effect on running or completed tasks.

**Usage:**
```
example-project cancel <task-id>
```

**Exit codes:**

| Code | Meaning                                   |
|------|-------------------------------------------|
| 0    | Task cancelled.                           |
| 1    | No such task ID, or task not cancellable. |


## drain

Block until all pending and in-flight tasks complete, or until the timeout expires.

**Usage:**
```
example-project drain [--timeout <seconds>]
```

**Flags:**

| Flag          | Type    | Default | Description                                                |
|---------------|---------|---------|------------------------------------------------------------|
| `--timeout`   | int     | (none)  | Max seconds to wait. Omit to wait indefinitely.            |

**Exit codes:**

| Code | Meaning                                            |
|------|----------------------------------------------------|
| 0    | All tasks completed.                               |
| 2    | Timeout expired with tasks still pending.          |


## pause

Stop dispatching new tasks from the queue. In-flight tasks continue to completion. Idempotent.

**Usage:**
```
example-project pause
```

See [[F001 — Scheduler Pause]] for the feature design.


## resume

Resume dispatching. Idempotent on an already-running scheduler.

**Usage:**
```
example-project resume
```


## Environment Variables

| Variable             | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `CAE_CONFIG`         | Path to an alternate config file. Default: `~/.example-project/config`. |
| `CAE_DB`             | Path to the SQLite task store. Default: `~/.example-project/tasks.db`.  |
| `NO_COLOR`           | Suppress ANSI color in output (set to any value).                       |


## Global Exit Codes

| Code | Meaning                                                   |
|------|-----------------------------------------------------------|
| 0    | Success.                                                  |
| 1    | Usage error — bad flags, missing args, invalid values.    |
| 2    | Runtime error — scheduler down, DB locked, permission.    |
| 64   | Configuration error — invalid config file.                |
