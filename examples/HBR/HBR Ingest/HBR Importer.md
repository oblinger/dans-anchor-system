---
description: "probes each file, extracts metadata, writes catalog rows"
---

# HBR Importer
The second stage of ingest — turns a candidate path into a catalog entry with metadata.

| -[[HBR Importer]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Ingest]] → [HBR Importer](hook://p/HBR%20Importer)<br>: a leaf component — the ingest importer |
| --- | --- |
| Anchor | [[HBR Ingest]] (parent) |
| Related | [[HBR Scanner]] (prior stage),  [[HBR Deduper]] (next stage), |

The Importer pulls each candidate path off the import queue and probes it with the media toolkit to read container, codec, duration, and embedded tags. It normalizes that metadata into the catalog schema and writes a row, attaching the file to any matching title or series. Files that fail to probe are quarantined with a reason code rather than silently dropped, so the operator can review what was rejected.
