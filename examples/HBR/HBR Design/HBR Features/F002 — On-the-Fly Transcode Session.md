---
description: Per-client transcode pipeline started on a direct-play miss
---

## Open Questions

- **Q2 — segment cache eviction policy?** — when many clients transcode different titles, the segment Cache can grow without bound. Options: (a) LRU by total bytes, (b) per-session TTL, (c) both. Leaning (a) with a configurable cap in `harbor.toml`; need user input on whether per-session TTL is worth the extra bookkeeping. ^F002-Q2

### Resolved

- **Q1 — transcode container: HLS or fragmented MP4?** — **Resolution:** HLS. Broadest LAN-client support (TVs, mobile browsers) and it segments naturally for the Cache. Landed in Design § Pipeline.

# [[HBR]] · F002 — On-the-Fly Transcode Session

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

Designing — awaiting Q2 (cache eviction) resolution.
