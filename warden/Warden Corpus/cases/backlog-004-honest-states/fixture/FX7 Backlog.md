---
description: "fixture — every non-executable state carries its body contract (R-backlog-05/06/07 pass)"
---
# FX7 Backlog

## Now

- **F001 — Chained block** [Blocked F015] —
- **F002 — Named blocker** [Blocked] — waiting on the vendor API to ship OAuth scopes; no local workaround.
- **F003 — Inline questions** [Questions] — pending export-format decision.
  - **Q1 — Which export format?** — CSV or Parquet.
- **F004 — Delegated questions** [Questions] — → [[F004 — Delegated questions]]
- **F005 — Dated wait** [Waiting 2d] — for the nightly reindex to complete; expires 2026-07-08.

## Next

- **F006 — Dated soak** [Watching 7d] — retry-cap fix shipped; non-recurrence by 2026-07-13 proves it held.
  - **Verify:** any double-retry since 2026-07-06? yes/no · *why-user: passive-use observation — a recurrence shows up while using the app, not in a log the agent can read*
