---
description: deferred work
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Backlog

Low-priority ideas and deferred work. Items graduate to [[CAE Roadmap]] when they're picked up.


## Active

- **F003 — Retry backoff polish** — Tune exponential-backoff caps after user feedback on long retries.


## Ready

- **F001 — Structured logging** — JSON output mode for consumption by log aggregators. Design resolved: single `--log-json` flag, fields documented in [[CAE System Design]].


## Now

- **F004 — Graph dependencies** [Designing] — task B runs only after task A succeeds. Requires DAG scheduling logic, deferred until v2.
- **F006 — Cron syntax extension** [Blocked F004] — extend cron parser to recognize "after F004 succeeds" as a trigger. Cannot start until F004's DAG model lands.
- **F007 — Webhook signing** [Blocked] — pending security review before signing key format is finalized. (Generic blocker; body explains.)


## Next

- **F002 — Web status page** [ ] — optional HTTP server exposing `/status`. Non-goal for v1 but might return.


## Later

- **F005 — Per-user queues** [ ] — multi-tenant mode with quotas. Not on current roadmap.


## Deferred bugs

_None active._
