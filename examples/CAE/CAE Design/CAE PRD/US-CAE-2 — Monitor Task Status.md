# US-CAE-2 — Monitor Task Status
description:: Show task state grouped by pending / running / done / failed

## As a developer, I want to see which tasks are pending, running, and completed so that I can track progress.

## Why

Once tasks are deferred, the developer needs to know what's actually happening — what's queued, what's running, what failed, what completed cleanly. Without this, deferred tasks become a black box: the developer schedules and prays. The status view is the observability surface that makes CAE trustable.

## Acceptance criteria

- `cae status` groups tasks by lifecycle state: `PENDING`, `RUNNING`, `DONE`, `FAILED`.
- Each row shows: task ID, scheduled time, command (truncated if long), state.
- Output is human-readable by default; `--json` produces machine-readable form.
- Counts in each state are summarized at the top of human output (e.g., `PENDING 3 tasks`).

## Edge cases

- What if there are hundreds of tasks? Default to recent (last 50) + a `--all` flag.
- What if a `RUNNING` task is actually stale (CAE crashed mid-run)? Stale-task detection is deferred to a follow-up story; for v1, status shows whatever the DB says.

## Related

- [[CAE Architecture]] — TaskStore + Scheduler subsystems supply the data
- [[CAE Testing]] — e2e test `e2e_monitor_task_status` exercises this story
- [[CAE CLI]] — full `status` command reference (flags, exit codes, output format)
- [[FCT Stories]] — facet spec governing this file's shape
- [[CAE PRD]] — parent PRD
- [[CAE Stories]] — sibling stories index
