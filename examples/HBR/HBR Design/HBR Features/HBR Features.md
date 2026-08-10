---
description: "feature index — one row per F-numbered feature doc, newest first"
---

| -[[HBR Features]]- | : Harbor Features — feature index<br>→ [[DAS]] → [[examples]] → [[HBR\|HARBOR]] → [[HBR Design\|HARBOR DESIGN]] → [HBR Features](hook://p/HBR%20Features)  |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Backlog]],  [[HBR Roadmap]],   |
| ^^^ | |
| [[F003 — Scheduled Catalog Checkpoint]]  | Periodic SQLite catalog checkpoint so a crash resumes from the last good state |
| [[F002 — On-the-Fly Transcode Session]]  | Per-client transcode pipeline started on a direct-play miss |
| [[F001 — Content-Hash Dedup]]  | Skip files already in the catalog by content hash during ingest |

# HBR Features
The feature index for Harbor — one row per F-numbered feature doc, reverse chronological.

- [[F003 — Scheduled Catalog Checkpoint]] `[Questions]` — periodic SQLite WAL checkpoint so a crash resumes from the last good state (US-HBR-5). → [[HBR Roadmap|M3.0]]
- [[F002 — On-the-Fly Transcode Session]] `[Active]` — per-client transcode pipeline started on a direct-play miss (US-HBR-4). → [[HBR Roadmap|M2.2]]
- [[F001 — Content-Hash Dedup]] `[Done]` — skip files already in the catalog by content hash during ingest (US-HBR-1). → [[HBR Roadmap|M1.2]]
