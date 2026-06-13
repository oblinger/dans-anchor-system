---
description: "Harbor's ingest pipeline — pulls media off disk into the catalog."
---

# Harbor Ingest
The ingest pipeline — discovers media on disk and lands it in the catalog.

| -[[Harbor Ingest]]- | → [HBR](hook://HBR) → [Harbor Ingest](hook://p/Harbor%20Ingest)<br>: a group container page — the Ingest pipeline's three modules |
| --- | --- |
| Anchor | [[Harbor Components]] (parent) |
| Related | [[Harbor Serve]] (sibling group),  [[Harbor Operate]] (sibling group), |
| [[Harbor Scanner\|Scanner]] | walks the watched roots and emits candidate media paths |
| [[Harbor Importer\|Importer]] | probes each file, extracts metadata, writes catalog rows |
| [[Harbor Deduper\|Deduper]] | content-hashes imports and folds duplicates into one entry |
| ... |  |
