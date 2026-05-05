---
description: Migrate the queue's persistence layer from in-memory + file-snapshot to a write-ahead-log + SQLite for crash safety. Milestone with three independent sub-items.
---

# [[CAE]] · F017 — Update Backing Store

## Summary

Today the queue lives entirely in memory with periodic JSON snapshots to a file. Crash recovery loses anything between snapshots. Migrate to a write-ahead log (WAL) plus SQLite-backed storage for durable enqueue/dequeue.

This is a **milestone-style feature** with three independent Ready sub-items that can be cranked in any order:

## Sub-items

- **F017.1 — WAL append path** — Wrap each enqueue/dequeue in an append to `cae.wal`. Module: `src/store/wal.rs`. Independent of F017.2/F017.3.
- **F017.2 — SQLite schema + migrations** — Define the `tasks` table; add `migrations/0001_init.sql`. Module: `src/store/sqlite.rs`. Independent.
- **F017.3 — Recovery loader** — On startup, replay the WAL on top of the last SQLite snapshot. Module: `src/store/recovery.rs`. Depends on F017.1 and F017.2 being merged.

(F017.1 and F017.2 are clearly parallelizable — different files, no shared state. F017.3 sequences after both. `/crank` should pick this up: dispatch F017.1 + F017.2 in parallel, then F017.3 sequentially.)

## Status

Ready — design locked, sub-items independently mintable. Mint count = 3.
