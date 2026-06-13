---
description: "build order — milestones from ingest through serve to operate"
---
# HBR Roadmap
**Related**: [[HBR]], [[HBR PRD]], [[HBR Architecture]], [[HBR Features]]

Build order for Harbor v1: stand up **Ingest** first (a catalog with nothing to read is useless), then **Serve** (direct-play, then transcode), then **Operate** (make it survive a crash). Each milestone maps to one pipeline in [[HBR Architecture]].

# [x] Milestone 1 — Ingest

**Status**: Complete — Scanner + Importer + Deduper landed; `harbor ingest <path>` writes deduped catalog rows. Satisfies [[HBR Stories#^US-HBR-1|US-HBR-1]] and [[HBR Stories#^US-HBR-2|US-HBR-2]].

Stand up the catalog and the write path: discover media on disk, probe metadata, fold duplicates by content hash.

## [x] M1.0 — Catalog & config

The SQLite catalog and `harbor.toml` everything else reads from.

### [x] M1.0.1 — Define the SQLite catalog schema (titles, files, hashes)
The single shared-state store. One `files` row per content-hash; `titles` rows reference files.

### [x] M1.0.2 — Parse `harbor.toml` (watched roots, catalog path, listen address)
Reject a config missing a catalog path; default the listen address to `0.0.0.0:8080`.

### [x] M1.0.3 — Open/create the catalog on startup, run pending migrations

**Reference Docs**: [[HBR Architecture]], [[HBR Decisions]]

### .

## [x] M1.1 — Scanner

Walk watched roots and emit candidate media files.

### [x] M1.1.1 — Recursively walk watched roots, filter to video/audio extensions
### [x] M1.1.2 — Skip files unchanged since last scan (mtime + size short-circuit)
### [x] M1.1.3 — Mark on-disk-absent files absent in the catalog (never delete from disk)

### .

## [x] M1.2 — Importer & Deduper

Probe each candidate, record metadata, fold duplicates.

### [x] M1.2.1 — Probe embedded metadata (title, duration, codec) via ffprobe
### [x] M1.2.2 — Compute content hash; skip files whose hash is already present
### [x] M1.2.3 — Write/update catalog rows in a single transaction per file

**Tests**: re-running `harbor ingest` on the same path adds zero rows (idempotency).

### .

# [ ] Milestone 2 — Serve

**Status**: In progress — direct-play (M2.1) complete; transcode (M2.2) underway. Targets [[HBR Stories#^US-HBR-3|US-HBR-3]] and [[HBR Stories#^US-HBR-4|US-HBR-4]].

Read the catalog to stream it: the LAN web app, direct-play first, then on-demand transcode for unsupported codecs.

## [x] M2.1 — Direct-play

Serve the catalog and stream byte ranges to devices that support the source codec.

### [x] M2.1.1 — Serve the Library screen (poster grid + search + type filter)
Read titles from the catalog; render the poster grid described in [[HBR UX Design]].

### [x] M2.1.2 — Stream byte ranges to the Player (HTTP range requests)
Honor `Range` headers so scrub/seek works without buffering the whole file.

### [x] M2.1.3 — Player reports the Direct readout when source codec is supported

**Reference Docs**: [[HBR UX Design]], [[HBR API Design]]

### .

## [-] M2.2 — Transcode

Re-encode on a direct-play miss so any title plays on any device.

### [x] M2.2.1 — Detect direct-play miss from the client's codec capability report
### [x] M2.2.2 — Spawn an ffmpeg transcode to a device-compatible profile
### [ ] M2.2.3 — Cache hot transcoded segments; reuse across seeks
### [ ] M2.2.4 — Player shows the Transcoding readout while re-encoding

**Tests**: tests/serve/test_transcode.rs (codec-miss → playback starts without a format prompt)

### .

# [-] Milestone 3 — Operate

**Status**: In progress — Backup checkpoint loop landed (M3.0, 2/3 sub-items); recovery re-queue and Metrics/Alerts pending. Targets [[HBR Stories#^US-HBR-5|US-HBR-5]].

Make Harbor survive unattended operation: checkpoint the catalog, sample load, fire alerts.

## [-] M3.0 — Backup

Checkpoint the catalog on a schedule and recover cleanly after an unclean shutdown.

### [x] M3.0.1 — Checkpoint the SQLite catalog (WAL) on the configured schedule
### [x] M3.0.2 — On startup after an unclean shutdown, resume from the last checkpoint
### [ ] M3.0.3 — Re-queue in-flight ingests interrupted by the crash

**Reference Docs**: [[HBR Decisions]]
**Acceptance**: power-loss mid-ingest → next start has an intact catalog, no manual repair.

### .

## [ ] M3.1 — Metrics & Alerts

Sample load and fire alerts on thresholds.

### [ ] M3.1.1 — Sample stream count, transcode count, and catalog size periodically
### [ ] M3.1.2 — Fire an alert when concurrent transcodes exceed the configured ceiling

### .
