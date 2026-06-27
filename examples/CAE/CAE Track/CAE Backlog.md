---
description: "workflow-state backlog — the irreducible Track core"
---

:>> [[CAE]] → [[CAE Track]]

# CAE Backlog

Low-priority ideas and deferred work. Items graduate to [[CAE Roadmap]] when they're picked up.


## Active

- **F003 — Retry backoff polish** [Active] — Tune exponential-backoff caps after user feedback on long retries.


## Ready

- **F001 — Structured logging** [Ready] — JSON output mode for consumption by log aggregators. Design resolved: single `--log-json` flag, fields documented in [[CAE Architecture#Component diagram|CAE Architecture § Component diagram]].


## Now

- **F004 — Graph dependencies** [Ready] — task B runs only after task A succeeds. Requires DAG scheduling logic, deferred until v2.
## Next

- **F002 — Web status page** [ ] — optional HTTP server exposing `/status`. Non-goal for v1 but might return.


## Later

- **F006 — Cron syntax extension** [Blocked F004] — extend cron parser to recognize "after F004 succeeds" as a trigger. Cannot start until F004's DAG model lands.

- **F007 — Webhook signing** [Blocked] — pending security review before signing key format is finalized. (Generic blocker; body explains.)

- **F005 — Per-user queues** [ ] — multi-tenant mode with quotas. Not on current roadmap.


## Deferred bugs

_None active._
