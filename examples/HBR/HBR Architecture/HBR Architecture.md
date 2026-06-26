---
description: "system architecture"
---
# HBR Architecture
How Harbor is built: three pipelines around one shared SQLite catalog.

| -[[HBR Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [HBR Architecture](hook://p/HBR%20Architecture)<br>: Harbor Architecture — system architecture |
| --- | --- |
| Anchor | [[HBR]] (parent) |
| Related | [[HBR Components]],  [[HBR Decisions]],  [[HBR API Design]],   |

## Overview

Harbor is a single Rust binary (a Cargo workspace) over one SQLite **catalog**. Three pipelines — Ingest, Serve, Operate — share that catalog and never call each other directly; they meet only at the catalog. One `harbor.toml` (watched roots, catalog path, listen address) configures all three. A small LAN web app, served by Serve, is the only network surface.

## Architecture diagram

![[HBR Architecture.svg|800]]

*Source: [[HBR Architecture.d2]] — regenerate with `d2 "HBR Architecture.d2" "HBR Architecture.svg"`.* Solid arrows are data flow through the catalog (write rows, read rows, checkpoint, stream); dashed arrows are `harbor.toml` configuration fan-out and Operate's load sampling.

## Subsystems

| SUBSYSTEMS        | Description                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| [[HBR Ingest]]    | *writes rows* — Scanner finds files, Importer probes and records metadata, Deduper folds by hash.   |
| [[HBR Serve]]     | *reads to stream* — Streamer pushes byte ranges, Transcoder re-encodes on a direct-play miss, Cache holds hot segments. |
| [[HBR Operate]]   | *watches the whole* — Backup checkpoints the catalog, Metrics samples load, Alerts fire on thresholds. |
| [HBR Viewer]      | LAN web app served by Serve — Library (poster grid + search) and Player (scrub/volume, Direct\|Transcoding readout). No separate doc yet. |

## Process model

Single process. The `harbor` binary boots all three pipelines as in-process subsystems sharing one open SQLite connection pool; there is no daemon fan-out and no inter-process IPC. Serve owns the listen socket; Ingest and Operate run on internal timers and filesystem watchers within the same process.

## Principles

- **Catalog is the only shared state** — pipelines coordinate exclusively through catalog rows; no pipeline holds a handle to another. (see [[HBR Decisions|D01]].)
- **Direct play first** — Serve streams original bytes whenever the client supports the codec; transcoding is a fallback, never the default path. (see [[HBR Decisions|D02]].)
- **Content hash is identity** — the Deduper folds entries by content hash, so the same rip on two drives is one catalog entry. (see [[HBR Decisions|D03]].)
- **One config file** — every tunable lives in `harbor.toml`; no scattered env vars, no hidden defaults that aren't echoed at startup.
- **No cloud, no telemetry** — Harbor is self-hosted and offline by default; the only outbound surface is the LAN web app it serves.

## Key data structures

The catalog is one SQLite file. Sketch of the load-bearing tables:

- **`media`** — `(id, content_hash, path, container, codec, duration_s, width, height, size_bytes, added_at)`. One row per distinct content hash; the identity row the Deduper folds into.
- **`source`** — `(id, media_id → media.id, path, root, mtime, scanned_at)`. Every on-disk path that resolved to a `media` row; lets duplicates across drives share one `media` entry.
- **`poster`** — `(media_id → media.id, kind, blob_path)`. Extracted artwork the Viewer's Library grid reads.
- **`transcode_cache`** — `(id, media_id → media.id, profile, segment_path, bytes, last_used_at)`. Hot transcoded segments Serve's Cache reuses; pruned by `last_used_at`.
- **`event`** — `(id, ts, pipeline, kind, detail)`. Append-only log Operate's Metrics samples and Alerts thresholds against.

## Design decisions

| #  | Decision | Rationale |
|----|----------|-----------|
| D1 | Single binary, in-process pipelines | A household server should be one thing to install and run; in-process keeps the catalog connection local and avoids IPC. |
| D2 | One open catalog, shared connection pool | The catalog is the sole rendezvous; a shared pool keeps reads (Serve) and writes (Ingest) consistent without a second store. |
| D3 | Byte-range streaming over the original file | Direct play is cheapest and highest fidelity; the Transcoder is invoked only when codec negotiation fails. |
| D4 | Crash recovery via catalog checkpoint | Operate's Backup checkpoints the SQLite catalog (WAL); a crash recovers by reopening the file — US-HBR-5. |

Anchor-wide rulings (SQLite-not-server, direct-play-first, hash-identity) live in [[HBR Decisions]] and are referenced above, not restated.

## See also

- [[HBR Components]] — the grouped module tree (Ingest / Serve / Operate sub-anchors).
- [[HBR API Design]] — the public contract surface.
- [[HBR Decisions]] — durable anchor-wide rulings (D01–D03).
- [[HBR PRD]] — what Harbor is for and the v1 user stories.
