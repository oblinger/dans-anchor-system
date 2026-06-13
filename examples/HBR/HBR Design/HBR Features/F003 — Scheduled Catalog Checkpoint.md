---
description: Periodic SQLite catalog checkpoint so a crash resumes from the last good state
---

## Open Questions

- **Q1 — checkpoint interval: fixed or write-triggered?** — a fixed clock (e.g. every 5 min) is simple but can lose a burst of ingest writes; a write-count trigger bounds loss but adds bookkeeping. Leaning fixed-interval with the interval set in `harbor.toml`, since v1 ingest is bursty-then-idle and a missed-by-minutes catalog is acceptable. ^F003-Q1

### Resolved

_None yet._

# [[HBR]] · F003 — Scheduled Catalog Checkpoint

## Summary

Operate's Backup stage runs a SQLite WAL checkpoint on a configured schedule so that after an unclean shutdown the next start resumes from the last good catalog state with no manual repair, and in-flight ingests are safely re-queued. This is US-HBR-5 — "restart after a power loss and the catalog is intact."

## Success Criteria

**Tier: Required** (v1 blocker — US-HBR-5 acceptance).

- After an unclean kill mid-ingest, the next `harbor` start opens the catalog without repair.
- Catalog rows committed before the last checkpoint survive the crash.
- In-flight ingests interrupted by the crash are re-queued, not lost or double-applied.

## Interface

```rust
/// Force a WAL checkpoint now (also driven by the configured schedule).
pub fn checkpoint(catalog: &Catalog) -> Result<CheckpointReport>;
```

## Design

Backup holds a handle to the shared catalog and issues `PRAGMA wal_checkpoint(TRUNCATE)` on the schedule from `harbor.toml`. Because all three pipelines meet only at the catalog (per [[HBR Architecture]]), checkpointing is a single-owner concern in Operate — Ingest and Serve are unaffected. Recovery on startup replays the WAL on top of the last checkpoint; an interrupted ingest is detected by an open ingest-job row and re-queued. Checkpoint cadence is governed by Q1.

## Status

Designing — awaiting Q1 (checkpoint interval) resolution.
