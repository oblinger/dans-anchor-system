---
description: "Harbor's ingest pipeline — pulls media off disk into the catalog."
---

| -[[HBR Ingest]]- | → [[DAS]] → [[FEX]] → [[HBR]] → [HBR Ingest](hook://p/HBR%20Ingest)  |
| --- | --- |
| Anchor | [[HBR Components]] (parent) |
| Related | [[HBR Serve]] (sibling group),  [[HBR Operate]] (sibling group), |
| [[HBR Scanner\|Scanner]]  | walks the watched roots and emits candidate media paths |
| [[HBR Importer\|Importer]]  | probes each file, extracts metadata, writes catalog rows |
| [[HBR Deduper\|Deduper]]  | content-hashes imports and folds duplicates into one entry |
| ... |  |

# HBR Ingest
The ingest pipeline — discovers media on disk and lands it in the catalog, the worked built-out sub-anchor example.
