# US-CAE-1 — Schedule a Task
description:: Schedule a deferred shell task with absolute or relative time

## As a developer, I want to schedule a shell command to run at a specific time so that I can defer work to off-peak hours.

## Why

Developers run resource-heavy commands (backups, batch jobs, data migrations) that they want to defer to off-peak hours. Ad-hoc cron jobs and shell scripts make this work but are scattered, untestable, and forget when systems reboot. CAE consolidates the deferred-task surface into one CLI with persistence.

## Acceptance criteria

- `cae schedule "<cmd>" --at "<time>"` accepts both absolute (`2026-03-01 02:00`) and relative offsets (`+30m`, `+2h`).
- The task persists across CAE restarts (recovered from the SQLite store on next start).
- A successful `schedule` returns a task ID the user can pass to `cae cancel` / `cae status`.
- Priority can be specified at schedule-time (`--priority high|normal|low`).

## Edge cases

- What if the specified time is in the past? Fail with a named error, not silent skip.
- What if the queue is full? CAE has no queue cap in v1 (scope; reconsidered if SQLite exhausts).
- What if the same `<cmd>` is scheduled twice at the same time? Both land; idempotency is the user's job.

## Related

- [[CAE Architecture]] — Scheduler + TaskStore subsystems implement this
- [[CAE Testing]] — e2e test `e2e_schedule_a_task` exercises this story
- [[CAE CLI]] — full `schedule` command reference (flags, exit codes)
- [[FCT Stories]] — facet spec governing this file's shape
- [[CAE PRD]] — parent PRD
- [[CAE Stories]] — sibling stories index
