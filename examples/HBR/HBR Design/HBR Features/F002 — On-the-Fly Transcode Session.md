---
description: Per-client transcode pipeline started on a direct-play miss
---

# [[HBR]] · F002 — On-the-Fly Transcode Session
Starts a per-client HLS transcode when a title cannot direct-play, so playback begins in seconds without the user choosing a format.

## Summary

When the Player reports a codec the client can't direct-play, Serve starts a transcode session: the Transcoder re-encodes the source into a device-compatible HLS profile while the Streamer serves segments as they're produced. Playback starts within a few seconds without the user choosing a format — the library "just works" regardless of source codec. This is US-HBR-4.

## Success Criteria

**Tier: Required** (v1 blocker — US-HBR-4 acceptance).

- A title in an unsupported codec begins playback without a user format choice.
- The Player's Direct|Transcoding readout shows "Transcoding" for the session.
- Tearing down the client connection stops the transcode (no orphaned ffmpeg).

## Interface

```rust
/// Begin (or join) a transcode session for a title at a target profile.
pub fn start_session(media: MediaId, profile: Profile) -> SessionId;

/// Next HLS segment for a session, produced lazily as the encode advances.
pub fn next_segment(session: SessionId, idx: u32) -> Option<Segment>;
```

## Design

On a direct-play miss the Streamer asks Serve to `start_session`; the Transcoder spawns an ffmpeg pipeline emitting HLS segments into the Cache. The Streamer serves the playlist and pulls segments via `next_segment`, blocking only until the requested index is ready. Sessions key on `(MediaId, Profile)` so two clients on the same title and profile share one encode. Serve reads catalog rows but writes none — it touches the catalog only to resolve the source path (per [[HBR Architecture]]). Cache sizing is governed by Q2.

## Status

**Active** (2026-08-01) — the HLS pipeline and session keying are wired; Q2 settled the cache policy on (A) LRU-by-bytes, so the remaining work is the byte-cap sweep (tracked as `T001 — Cache eviction`) plus a time-to-first-segment measurement.

## Resolved

### Q1 — Transcode container: HLS or fragmented MP4? (resolved)
**Choice:** HLS.

Broadest LAN-client support (TVs, mobile browsers) and it segments naturally for the Cache, so the Streamer serves what the Transcoder writes with no repackaging step. Landed in Design § Pipeline.

### Q2 — Segment-cache eviction policy? (resolved 2026-08-01)
**Choice:** (A)

auto-resolved (waste) — a wrong first pick costs one module's rework; the policy is internal to the Cache

> Original Q context:
> - **Q2 — Segment-cache eviction policy?** — when many clients transcode different titles the segment Cache grows without bound; v1 needs a bounded policy before the first long-lived deployment. ^F002-Q2
>   - **(A)** LRU by total bytes — evict least-recently-served segments once the cache dir passes a `cache_max_bytes` cap in `harbor.toml`.
>   - **(B)** Per-session TTL — drop a session's segments a fixed interval after the session ends.
>   - **(C)** Both — a byte cap for the hard ceiling plus a TTL to release idle sessions early.
>   - **Recommendation:** Lean (A). One knob, one invariant (the cache never exceeds its cap), and no per-session bookkeeping; a TTL can be added later if idle sessions turn out to hold the cap hostage.
>   - **Damage:** waste — a wrong first pick costs one module's rework; the policy is internal to the Cache.
