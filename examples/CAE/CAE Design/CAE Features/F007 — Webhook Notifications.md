---
description: HTTP POST notifications fired on task completion so external systems can react without polling
---

# [[CAE]] · F007 — Webhook Notifications

## Summary

When a task completes (success or failure), POST a JSON payload to a configured URL. Lets external systems react event-driven instead of polling `cae list`.

## Configuration

- Per-scheduler default: `webhook_url` in `Scheduler::new` config.
- Per-task override: optional `webhook_url` field on `Task`.

## Payload (v1)

```json
{
  "task_id": "tsk_{base32}",
  "status": "ok" | "error",
  "started_at": "2026-05-03T14:21:33Z",
  "ended_at":   "2026-05-03T14:21:48Z",
  "duration_ms": 14982,
  "error_message": null
}
```

`Content-Type: application/json`. Retry on non-2xx with exponential backoff (3 attempts, capped at 30s — same backoff curve as F3).

## Verify

Implementation lands behind `--feature=webhook`. Trigger a test job against a controlled URL and confirm:

1. POST fires within 1s of task completion.
2. JSON payload matches the schema above (snake_case keys; ISO-8601 timestamps).
3. Retry behavior: stop after 3 attempts; record last attempt timestamp in scheduler logs.

(Verify-plan text — when this row sits under `## Now` in `CAE Triage.md` with `[Verify]` bracket, the description is this triple-step plan.)

## Status

Verify — implementation merged in commit `{sha}`; awaiting user confirmation against the verify plan above.
