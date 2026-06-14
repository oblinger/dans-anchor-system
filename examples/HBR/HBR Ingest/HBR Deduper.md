---
description: "a leaf component — the ingest deduper"
---

# HBR Deduper
The final stage of ingest — collapses duplicate files into a single catalog entry.

| -[[HBR Deduper]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Ingest]] → [HBR Deduper](hook://p/HBR%20Deduper)<br>: a leaf component — the ingest deduper |
| --- | --- |
| Anchor | [[HBR Ingest]] (parent) |
| Related | [[HBR Scanner]] (prior stage),  [[HBR Importer]] (prior stage), |

The Deduper computes a content hash over each freshly-imported file and looks it up against the catalog's hash index. When it finds a match, it folds the new file in as an alternate source of the existing entry rather than creating a second title, preserving whichever copy has the higher bitrate as primary. This keeps the library clean when the same media arrives twice from different roots or in different containers.
