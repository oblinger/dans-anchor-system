---
description: Periodic SQLite catalog checkpoint so a crash resumes from the last good state
---

# [[HBR]] · F003 — Scheduled Catalog Checkpoint
Runs a scheduled SQLite WAL checkpoint so an unclean shutdown resumes from the last good catalog state with no manual repair.

## Open Questions
<!-- state:q 5n -->

- **Q1 — Checkpoint trigger: fixed interval or write-count?** — the WAL checkpoint bounds how much ingest work an unclean shutdown can lose, and the trigger choice sets the `harbor.toml` surface v1 ships with. ^F003-Q1
  - **(A)** Fixed interval — checkpoint every N minutes, N set in `harbor.toml`. Simple and predictable, but a burst of ingest writes inside one window is all at risk.
  - **(B)** Write-count trigger — checkpoint every N catalog writes. Bounds worst-case loss in units the user cares about (files), at the cost of a write counter in the Backup stage.
  - **(C)** Both — whichever fires first, so an idle catalog still checkpoints and a burst still bounds its loss.
- **Recommendation:** Lean (A) for v1. Ingest is bursty-then-idle, so a catalog missed by minutes is acceptable, and the config surface stays one key. · *why-ask: locking: the trigger names the `harbor.toml` key v1 ships, and changing it after release is a config migration rather than an internal edit*
  - **Damage:** locking — the trigger names the `harbor.toml` key v1 ships, and changing it after release is a config migration rather than an internal edit.

### Resolved

_None yet._


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
