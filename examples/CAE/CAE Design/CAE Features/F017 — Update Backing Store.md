---
description: Migrate the queue's persistence layer from in-memory + file-snapshot to a write-ahead-log + SQLite for crash safety. Milestone with three independent sub-items.
---

# [[CAE]] · F017 — Update Backing Store

## Summary

Today the queue lives entirely in memory with periodic JSON snapshots to a file. Crash recovery loses anything between snapshots. Migrate to a write-ahead log (WAL) plus SQLite-backed storage for durable enqueue/dequeue.

This is a **milestone-style feature** with several independent sub-items, organized as a sub-roadmap (per [[CAB Features]] § Roadmap section). Sub-items can be cranked in any order subject to the noted dependencies; the parent F017 stays the unit of feature-level tracking.

## Roadmap

- [x] **F017.1 — WAL append path** — Wrap each enqueue/dequeue in an append to `cae.wal`. Module: `src/store/wal.rs`. Independent of F017.2/F017.3.
- [x] **F017.2 — SQLite schema + migrations** — Define the `tasks` table; add `migrations/0001_init.sql`. Module: `src/store/sqlite.rs`. Independent.
- [ ] **F017.3 — Recovery loader** — On startup, replay the WAL on top of the last SQLite snapshot. Module: `src/store/recovery.rs`. Depends on F017.1 + F017.2 being merged. Will spawn:
    - [ ] [F049 — WAL compaction strategy] — not yet authored; capture when the recovery loader's startup-time bottleneck surfaces during integration testing.
- [ ] **F017.4 — Backpressure on durable enqueue** — defer to post-MVP; spec it when enqueue throughput becomes the load-bearing concern.

**Status:** Core complete — F017.1 + F017.2 merged. F017.3 in progress (recovery loader skeleton drafted); F049 will spin out once a real bottleneck appears; F017.4 deferred.

(F017.1 and F017.2 were parallelizable — different files, no shared state. F017.3 sequences after both. `/crank` picked this up: dispatched F017.1 + F017.2 in parallel, then F017.3 sequentially. Bare-bracketed `[F049 — WAL compaction strategy]` is the placeholder convention for a not-yet-authored spinoff feature per [[CAB Features]] § Roadmap — bare brackets upgrade to `[[F049 — …]]` wiki-links once that doc is created.)

## Status

Implementing — Core sub-items (F017.1, F017.2) merged; F017.3 in progress; F049 deferred; F017.4 deferred. Feature-level Status reflects the Roadmap rollup.
