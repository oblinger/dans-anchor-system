---
description: "Harbor's scanner — walks watched roots and emits candidate media paths."
---

# Harbor Scanner
The first stage of ingest — discovers media files under the watched library roots.

| -[[Harbor Scanner]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[Harbor]] → [[Harbor Components]] → [[Harbor Ingest]] → [Harbor Scanner](hook://p/Harbor%20Scanner)<br>: a leaf component — the ingest scanner |
| --- | --- |
| Anchor | [[Harbor Ingest]] (parent) |
| Related | [[Harbor Importer]] (next stage),  [[Harbor Deduper]] (next stage),   |

The Scanner walks each configured library root, honoring ignore globs and the last-scan watermark so unchanged trees are skipped cheaply. Files matching the media extensions are emitted as candidate paths onto the import queue, while everything else is dropped. It runs both on a timer and on filesystem-watch events, so newly-dropped files are picked up within seconds rather than waiting for the next full sweep.
