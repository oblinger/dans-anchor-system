---
description: "system architecture"
---
# HBR Architecture
How Harbor is built: three pipelines around one shared SQLite catalog.

| -[[HBR Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[HBR]] → [[HBR Design]] → [HBR Architecture](hook://p/HBR%20Architecture)<br>: system architecture |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Components]],  [[HBR Decisions]],   |

Harbor is a single Rust binary (a Cargo workspace) over one SQLite **catalog**. Three pipelines share that catalog and never call each other directly — they meet at the catalog:

- **[[HBR Ingest|Ingest]]** *writes* rows — Scanner finds files, Importer probes and records metadata, Deduper folds duplicates by content hash.
- **[[HBR Serve|Serve]]** *reads* to stream — Streamer pushes byte ranges, Transcoder re-encodes on a direct-play miss, Cache holds hot segments.
- **[[HBR Operate|Operate]]** *watches* the whole — Backup snapshots the catalog, Metrics samples load, Alerts fire on thresholds.

The catalog is the only shared state. Configuration is one `harbor.toml` (watched roots, catalog path, listen address).
