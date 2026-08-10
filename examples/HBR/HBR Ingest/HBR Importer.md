---
description: "probes each file, extracts metadata, writes catalog rows"
---

| -[[HBR Importer]]- | : a leaf component — the ingest importer<br>→ [[DAS]] → [[examples]] → [[HBR\|HARBOR]] → [[HBR Ingest\|HARBOR INGEST]] → [HBR Importer](hook://p/HBR%20Importer) |
| --- | --- |
| Anchor | [[HBR Ingest]] (parent) |
| Related | [[HBR Scanner]] (prior stage),  [[HBR Deduper]] (next stage), |
| ... |  |

# HBR Importer
The second stage of ingest — turns a candidate path into a catalog entry with metadata.

The Importer pulls each candidate path off the import queue and probes it with the media toolkit to read container, codec, duration, and embedded tags. It normalizes that metadata into the catalog schema and writes a row, attaching the file to any matching title or series. Files that fail to probe are quarantined with a reason code rather than silently dropped, so the operator can review what was rejected.
