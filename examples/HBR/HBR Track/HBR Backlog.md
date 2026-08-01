---
description: "work queue"
---
# HBR Backlog
<!-- state:backlog 9v -->
Harbor's work queue — horizon H2s, one row per item, status in brackets.

| -[[HBR Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [[HBR]] → [[HBR Track]] → [HBR Backlog](hook://p/HBR%20Backlog)<br>: work queue |
| --- | --- |
| Anchor | [[HBR Track]] (parent) |
| Related | [[HBR Features]],  [[HBR Roadmap]],   |
| ... | [[HBR Messages]],  [[HBR queries]],  [[HBR Status]],   |

## Active

- **T001 — Cache eviction** [Active] — evict segments least-recently-served once the segment cache dir passes its byte cap, so a long transcode session cannot fill the disk. ^T001
  - **Next:** Add `cache_max_bytes` to `harbor.toml`, then sweep least-recently-served segments on each segment write once the dir exceeds it.

- **F002 — On-the-Fly Transcode Session** [Active] — → [[F002 — On-the-Fly Transcode Session]] · per-client HLS transcode started on a direct-play miss (US-HBR-4). Container settled (HLS); Q2 resolved (A) — LRU by total bytes against a `cache_max_bytes` cap. ^F002
  - **Next:** Land the byte-cap segment eviction Q2 chose (tracked as T001), then measure time-to-first-segment on a 4K source.

## Now

- **F003 — Scheduled Catalog Checkpoint** [Questions] — → [[F003 — Scheduled Catalog Checkpoint]] · periodic SQLite WAL checkpoint so an unclean shutdown resumes from the last good catalog state (US-HBR-5). Q1 — fixed-interval vs write-triggered — is open. ^F003

## Next

- **T002 — Watched-root hot reload** [Ready] — re-scan when a watched root changes, without a restart. ^T002
  - **Next:** Watch the configured roots with an fs-event watcher and re-run the Scanner on the changed subtree only, without restarting the daemon.

## Done

- **F001 — Content-Hash Dedup** [Done] — → ~~[[F001 — Content-Hash Dedup]]~~ · whole-file BLAKE3 dedup on ingest, so re-running ingest on the same library adds nothing (US-HBR-1). ^F001
