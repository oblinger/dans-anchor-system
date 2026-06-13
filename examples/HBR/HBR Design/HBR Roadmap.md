---
description: "milestones"
---
# HBR Roadmap
The milestone sequence that takes Harbor from an empty catalog to streaming.

| -[[HBR Roadmap]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[HBR]] → [[HBR Design]] → [HBR Roadmap](hook://p/HBR%20Roadmap)<br>: milestones |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR PRD]],  [[HBR Backlog]],   |

## M1 — Catalog *(done)*
Scanner + Importer + Deduper land media in the SQLite catalog. `harbor scan` works end to end.

## M2 — Direct play *(active)*
Streamer serves catalog entries the client can already play. No transcoding yet.

## M3 — Transcode on demand
Transcoder + Cache kick in when the client can't play the source codec.

## M4 — Operate
Backup on a schedule; Metrics + Alerts make the server observable.
