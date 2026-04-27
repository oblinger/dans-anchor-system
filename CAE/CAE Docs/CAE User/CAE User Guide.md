---
description: getting started and usage
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE User]]

# CAE User Guide

End-user documentation for CAE Example. Covers installation, basic usage, and the most common task lifecycle.


## Installation

```bash
cargo install example-project
```

Requires Rust 1.75 or newer. No external service needed — CAE stores state in `~/.example-project/tasks.db`.


## Quick start

Submit a task to run at a specific time:

```bash
example-project submit \
  --deadline "2026-04-21T15:00:00" \
  --retry 3 \
  -- ./build.sh
```

Check status:

```bash
example-project status
```

Sample output:

```
ID       STATE      DEADLINE              COMMAND
t-4f2    running    2026-04-21 15:00:00   ./build.sh
t-4f3    pending    2026-04-21 16:00:00   ./deploy.sh
```

Cancel a pending task:

```bash
example-project cancel t-4f3
```

Block until all tasks complete:

```bash
example-project drain
```


## Task lifecycle

Every task moves through a deterministic sequence of states:

```
pending → running → done        (success)
                  → failed      (after retries exhausted)
pending → cancelled             (cancel() while still pending)
```

- **pending** — queued, waiting for its deadline and a free worker
- **running** — currently executing on a worker thread
- **done** — completed successfully; result available via `status`
- **failed** — all retries exhausted; moved to dead-letter list
- **cancelled** — cancelled by caller before it started running


## Where state lives

CAE stores its state in a SQLite database at `~/.example-project/tasks.db`. Back it up or delete it like any other SQLite file. The schema is self-migrating on startup.


## See also

- [[CAE Architecture]] — technical architecture overview
- Project repository — `https://github.com/example/example-project`
