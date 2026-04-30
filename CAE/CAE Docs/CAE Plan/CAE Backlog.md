---
description: deferred work
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Backlog

Low-priority ideas and deferred work. Items graduate to [[CAE Roadmap]] when they're picked up.


## Active

- **F3 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries.


## Ready

- **F1 — Structured logging** — JSON output mode for consumption by log aggregators. Design resolved: single `--log-json` flag, fields documented in [[CAE System Design]].


## Now

- **F4 — Graph dependencies** [Designing] — task B runs only after task A succeeds. Requires DAG scheduling logic, deferred until v2.


## Next

- **F2 — Web status page** [ ] — optional HTTP server exposing `/status`. Non-goal for v1 but might return.


## Later

- **F5 — Per-user queues** [ ] — multi-tenant mode with quotas. Not on current roadmap.


## Deferred bugs

_None active._
