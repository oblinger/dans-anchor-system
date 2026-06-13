---
description: "command reference"
---
# HBR CLI
`harbor` is the single binary that runs every Harbor pipeline — one CLI to ingest a library, serve it on the LAN, transcode on demand, and back up the catalog. This page is its complete command reference.

| -[[HBR CLI]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR CLI](hook://p/HBR%20CLI)<br>: command reference |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR UX Design]],  [[HBR API Design]],  [[HBR Architecture]],   |

```
harbor --help                                            # Show this help text
harbor --version                                         # Print version, commit SHA, ffmpeg version
harbor ingest <path> [--watch] [--dry-run]               # Scan a folder, dedup, write catalog rows
harbor scan [<root>] [--full] [--prune]                  # Re-scan watched roots for new/changed files
harbor watch [--root <name>] [--interval <sec>]          # Run the scheduled re-scan loop in foreground
harbor serve [--listen <addr>] [--no-transcode]          # Start the web + stream server (Serve pipeline)
harbor status [--json] [--watch]                         # Catalog counts, pipeline health, active streams
harbor transcode <title-id> --profile <name> [--probe]   # Force a transcode (or probe codec support)
harbor backup [--out <path>] [--restore <path>]          # Checkpoint or restore the SQLite catalog
```

For a tutorial introduction, see [[HBR Guide]]. Per-command detail below: [[#ingest]], [[#scan]], [[#watch]], [[#serve]], [[#status]], [[#transcode]], [[#backup]], [[#version]].

All commands read [[#harbor.toml]] for the catalog path, watched roots, and listen address unless overridden by a flag.


## ingest

One-shot ingest of a directory into the catalog. Discovers video/audio files, reads embedded metadata (title, duration, codec), content-hashes each file, and writes a catalog row — skipping any file whose hash is already present. Implements US-HBR-1. Runs the [[HBR Ingest|Ingest]] pipeline (Scanner → Importer → Deduper).

**Usage:**
```
harbor ingest <path> [--watch] [--dry-run]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--watch` | bool | false | After the initial ingest, register `<path>` as a watched root and keep re-scanning it. |
| `--dry-run` | bool | false | Report what would be imported/deduped without writing catalog rows. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Ingest complete; counts printed on stdout. |
| 1 | Usage error — path missing or unreadable. |
| 2 | Catalog unreachable or locked. |

**Example:**
```bash
harbor ingest /media/movies
# scanned 412 files · imported 47 · deduped 365 · 0 errors
```


## scan

Re-scan the watched roots declared in `harbor.toml` for new or changed files. Processes only deltas; files removed from disk are marked **absent** in the catalog, never deleted. Implements US-HBR-2.

**Usage:**
```
harbor scan [<root>] [--full] [--prune]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `<root>` | name | all roots | Limit the scan to one named root from `harbor.toml`. |
| `--full` | bool | false | Re-hash every file instead of trusting size+mtime. |
| `--prune` | bool | false | Permanently drop catalog rows for files marked absent. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Scan complete. |
| 1 | Usage error — unknown root name. |
| 2 | Catalog unreachable or locked. |

**Example:**
```bash
harbor scan movies
# movies: +3 new · 1 changed · 2 absent
```


## watch

Run the scheduled re-scan loop in the foreground — the same delta scan as `harbor scan`, repeated on an interval. `serve` runs this internally; standalone `watch` is for running the scanner as its own [[HBR Operate|Operate]]-side process.

**Usage:**
```
harbor watch [--root <name>] [--interval <sec>]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--root` | name | all roots | Watch only the named root. |
| `--interval` | int (sec) | config `scan_interval` (300) | Seconds between scans. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Loop exited on SIGINT/SIGTERM. |
| 2 | Catalog unreachable at startup. |


## serve

Start the Harbor server — the LAN web client (Library + Player) and the streaming/transcoding endpoints. Runs the [[HBR Serve|Serve]] pipeline (Streamer / Transcoder / Cache) plus the internal scan loop. Implements US-HBR-3 and US-HBR-4.

**Usage:**
```
harbor serve [--listen <addr>] [--no-transcode]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--listen` | host:port | config `listen` (0.0.0.0:8080) | Address the web + stream server binds. |
| `--no-transcode` | bool | false | Direct-play only; refuse unsupported codecs instead of transcoding. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Server shut down cleanly. |
| 1 | Usage error — bad listen address. |
| 2 | Catalog unreachable, or listen address already in use. |

**Example:**
```bash
harbor serve --listen 0.0.0.0:8080
# catalog: 1,204 titles · listening on http://0.0.0.0:8080
```


## status

Print catalog counts, pipeline health, and active streams. Read-only; composes with scripts via `--json`.

**Usage:**
```
harbor status [--json] [--watch]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--json` | bool | false | Emit JSON instead of the human-readable summary. |
| `--watch` | bool | false | Refresh in place until Ctrl+C. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Status printed; catalog healthy. |
| 2 | Catalog unreachable or last checkpoint failed. |

**Example:**
```bash
harbor status
# catalog: 1,204 titles (movies 612 · shows 540 · music 52) · last backup 2h ago
# serve: up · 2 active streams (1 direct, 1 transcoding) · watch: 3 roots
```


## transcode

Force a transcode of one title to a named profile, or probe whether a profile is supported. Useful for pre-warming the cache or diagnosing playback failures; the [[HBR Serve|Serve]] pipeline normally invokes this on demand (US-HBR-4).

**Usage:**
```
harbor transcode <title-id> --profile <name> [--probe]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--profile` | name | — | Target device profile (e.g. `h264-720p`). Required unless `--probe`. |
| `--probe` | bool | false | Report direct-play vs. transcode for the title without producing output. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Transcode complete (or probe reports playable). |
| 1 | Usage error — unknown title id or profile. |
| 2 | Catalog unreachable. |
| 3 | Transcode failed (ffmpeg error). |

**Example:**
```bash
harbor transcode t-918 --profile h264-720p
# t-918 "Sintel" → h264-720p · cached 84 MB
```


## backup

Checkpoint the SQLite catalog, or restore it from a checkpoint. The [[HBR Operate|Operate]] pipeline checkpoints on the `harbor.toml` schedule; this command forces one or recovers after a crash (US-HBR-5).

**Usage:**
```
harbor backup [--out <path>] [--restore <path>]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--out` | path | config `backup_dir` | Write the checkpoint to this path. |
| `--restore` | path | — | Replace the live catalog from this checkpoint (refuses while `serve` is running). |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Checkpoint written / restore complete. |
| 1 | Usage error — checkpoint path missing or unreadable. |
| 2 | Catalog locked, or `--restore` attempted while the server is running. |

**Example:**
```bash
harbor backup --out /backups/harbor-2026-06-13.db
# checkpoint: 1,204 rows · 38 MB → /backups/harbor-2026-06-13.db
```


## version

Print the build version, the commit SHA it was built from, and the linked `ffmpeg` version the Transcoder shells out to. Read-only; takes no flags.

**Usage:**
```
harbor --version
```

**Example:**
```bash
harbor --version
# harbor 1.0.0 (commit a3f91c2) · ffmpeg 6.1
```


## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success. |
| 1 | Usage error — bad flags, missing args, invalid values. |
| 2 | Runtime error — catalog unreachable/locked, port in use, server-state conflict. |
| 3 | Pipeline error — transcode (ffmpeg) failure. |
| 64 | Configuration error — `harbor.toml` invalid or unparseable. |


## Environment variables

| Variable | Default | Description |
|---|---|---|
| `HARBOR_CONFIG` | `./harbor.toml` | Path to the config file. |
| `HARBOR_CATALOG` | config `catalog` | Override the SQLite catalog path. |
| `HARBOR_LOG` | `info` | Log level — `error`, `warn`, `info`, `debug`, `trace`. |
| `NO_COLOR` | unset | Suppress ANSI color in output. |


## harbor.toml

Every command reads a single `harbor.toml` (found via `HARBOR_CONFIG`, else the working directory). It declares the catalog path, watched roots, listen address, and backup schedule — see [[HBR Architecture]] for how the three pipelines consume it.

```toml
catalog       = "/var/lib/harbor/catalog.db"
listen        = "0.0.0.0:8080"
scan_interval = 300                 # seconds between watch re-scans
backup_dir    = "/var/lib/harbor/backups"
backup_cron   = "0 3 * * *"         # nightly checkpoint

[[root]]
name = "movies"
path = "/media/movies"

[[root]]
name = "music"
path = "/media/music"
```

Subcommands never prompt; they exit non-zero (64 on a malformed config) rather than asking.
