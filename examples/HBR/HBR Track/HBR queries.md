---
description: HBR queries — mechanically rendered from the backlog (Blockers / Ready+Next / Questions / Blocked / Verifications / Other), and copied verbatim into Q.md. Do not hand-edit; edit the backlog rows.
---

# [U+A]  [[HBR|HBR]]  -  Ready 3    User 1   |   Now 1    Next 1    Later 0   |   Parked 0    Waiting 0    Icebox 0

## Ready
- [[HBR Backlog#^T001|T001]] — **Next:** Add `cache_max_bytes` to `harbor.toml`, then sweep least-recently-served segments on each segment write once the dir exceeds it.
- [[F002 — On-the-Fly Transcode Session]] — **Next:** Land the byte-cap segment eviction Q2 chose (tracked as T001), then measure time-to-first-segment on a 4K source.
- [[HBR Backlog#^T002|T002]] — **Next:** Watch the configured roots with an fs-event watcher and re-run the Scanner on the changed subtree only, without restarting the daemon.

## Questions
- [[F003 — Scheduled Catalog Checkpoint|F003]] **(1Q)** ([[F003 — Scheduled Catalog Checkpoint]]) — · periodic SQLite WAL checkpoint so an unclean shutdown resumes from the last good catalog state (US-HBR-5). Q1 — fixed-interval vs write-triggered — is open.
    - Q1 — Checkpoint trigger: fixed interval or write-count? the WAL checkpoint bounds how much ingest work an unclean shutdown can lose, and the trigger choice sets the `harbor.toml` surface v1 ships with. · **(A)** Fixed interval · **(B)** Write-count trigger · **(C)** Both · *Lean (A) for v1....*
