---
description: "source tree"
---

| -[[HBR Files]]- | : source tree<br>→ [[DAS]] → [[examples]] → [[HBR\|HARBOR]] → [[HBR Dev Docs\|HARBOR DEV DOCS]] → [HBR Files](hook://p/HBR%20Files)  |
| --- | --- |
| Anchor | [[HBR Dev Docs]] (parent) |
| Related | [[HBR Architecture]],   |
| ... | [[HBR Versions]],   |

# HBR Files
The Cargo workspace layout — one crate per pipeline plus the shared catalog.

```
harbor/
  Cargo.toml          # workspace
  crates/
    catalog/          # SQLite schema + queries (shared by all pipelines)
    ingest/           # Scanner, Importer, Deduper
    serve/            # Streamer, Transcoder, Cache + the HTTP API
    operate/          # Backup, Metrics, Alerts
    cli/              # the `harbor` binary
  harbor.toml         # example config
```

Each pipeline is its own crate; `catalog` is the only crate the others share.
