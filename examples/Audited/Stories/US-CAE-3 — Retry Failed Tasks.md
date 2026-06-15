# US-CAE-3 — Retry Failed Tasks
description:: Auto-retry failed tasks with exponential backoff to a cap

## As a developer, I want failed tasks to automatically retry with backoff so that transient failures don't require manual intervention.

## Why

Network blips, locked databases, momentary disk-full conditions — most task failures are transient and resolve on their own within seconds to minutes. Without auto-retry, every transient failure pages the developer. Exponential backoff is the well-known shape: retry once, twice, with exponentially-growing delays, then give up. CAE bakes this in so the developer doesn't have to.

## Acceptance criteria

- Failed tasks are auto-retried with exponential backoff: delay doubles up to a configurable cap.
- Retry policy (max attempts, base delay, cap) is configurable at schedule-time (`--retry-max`, `--retry-base`, `--retry-cap`) and has sensible defaults.
- After `max_attempts` failures, the task moves to the dead-letter list with the final error captured.
- `cae history` shows retried tasks with attempt counts and the final outcome.

## Edge cases

- What if the retry would land in the past (clock skew, paused process)? Run immediately rather than indefinitely deferring.
- What if a task succeeds on retry N but the user has already manually re-scheduled it? Both run; deduplication is out of scope for v1.
- What if `max_attempts` is 0? Don't retry — treat as a single-shot.

## Related

- [[CAE Architecture]] — RetryManager subsystem implements this
- [[CAE Testing]] — e2e test `e2e_failed_task_retries_then_visible` exercises this story; property-based test `prop_retry_delays_monotonic_to_cap` checks the backoff invariant
- [[CAE Decisions]] — D5 "Retry logic in its own module" centralizes the policy
- [[FCT Stories]] — facet spec governing this file's shape
- [[CAE PRD]] — parent PRD
- [[CAE Stories]] — sibling stories index
