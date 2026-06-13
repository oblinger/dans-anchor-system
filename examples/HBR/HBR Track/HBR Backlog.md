---
description: "work queue"
---
# HBR Backlog
Harbor's work queue — horizon H2s, one row per item, status in brackets.

| -[[HBR Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Track]] → [HBR Backlog](hook://p/HBR%20Backlog)<br>: work queue |
| --- | --- |
| Anchor | [[HBR Track]] (parent) |
| Related | [[HBR Features]],  [[HBR Roadmap]],   |

## Active
- **F002 — Direct-play streaming** `[Active]` — byte-range session for already-playable files. → [[HBR Features]]

## Now
- **F003 — Transcode fallback** `[Designing]` — choose the output codec when direct play fails; needs a codec-priority ruling.

## Next
- **B1 — Cache eviction** `[Ready]` — evict hot segments least-recently-used once the cache dir passes its cap.

## Later
- **B2 — Watched-root hot reload** `[ ]` — re-scan when a watched root changes, without a restart.
