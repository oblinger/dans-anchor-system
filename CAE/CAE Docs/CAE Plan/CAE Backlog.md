---
description: deferred work
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Backlog

Low-priority ideas and deferred work. Items graduate to [[CAE Roadmap]] when they're picked up.


## In Progress

- **Q3 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries.


## Ready

- **Q1 — Structured logging** — JSON output mode for consumption by log aggregators. Design resolved: single `--log-json` flag, fields documented in [[CAE System Design]].


## Upcoming

- **Q4 — Graph dependencies** — task B runs only after task A succeeds. Requires DAG scheduling logic, deferred until v2.
- **Q5 — Per-user queues** — multi-tenant mode with quotas. Not on current roadmap.
- **Q2 — Web status page** — optional HTTP server exposing `/status`. Non-goal for v1 but might return.


## Deferred bugs

_None active._
