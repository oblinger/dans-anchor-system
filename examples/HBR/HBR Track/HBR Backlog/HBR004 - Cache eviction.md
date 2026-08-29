---
description: "evict segments least-recently-served once the segment cache dir passes its byte cap, so a long transcode session cannot fill the disk."
---

# [[HBR]] · T004 — Cache eviction
evict segments least-recently-served once the segment cache dir passes its byte cap, so a long transcode session cannot fill the disk.

next:: Add `cache_max_bytes` to `harbor.toml`, then sweep least-recently-served segments on each segment write once the dir exceeds it.

## Summary

evict segments least-recently-served once the segment cache dir passes its byte cap, so a long transcode session cannot fill the disk.

## Status

**Active** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
