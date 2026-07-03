---
description: "command-line specification — the harbor CLI: a compressed --help figure over the full command reference"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR CLI](hook://p/HBR%20CLI)

# HBR CLI
The command-line specification of `harbor` — one binary driving every Harbor pipeline (Ingest, Scan, Serve, Operate); each command reads `harbor.toml`.

![[HBR CLI Help.svg|1002]]

For a tutorial, see [[HBR Guide]]; for the command *shape*, [[HBR UX Design]]. Every command reads [[#harbor.toml]] for the catalog path, watched roots, and listen address unless a flag overrides it. Only `transcode` (below) needs its own section; the rest are covered by the notes.

## Notes

- **ingest** `<path>` — one-shot import: discovers media, reads metadata, content-hashes, writes a catalog row (skips any hash already present). `--watch` also registers `<path>` as a watched root; `--dry-run` reports without writing. Runs the [[HBR Ingest|Ingest]] pipeline (US-HBR-1).
- **scan** `[<root>]` — delta re-scan of watched roots; removed files are marked **absent**, never deleted. `--full` re-hashes instead of trusting size+mtime; `--prune` drops absent rows (US-HBR-2).
- **watch** — the same delta scan on a loop in the foreground (`serve` runs it internally); `--interval` defaults to config `scan_interval` (300s).
- **serve** — starts the LAN web client + stream/transcode endpoints plus the internal scan loop (US-HBR-3/4). `--listen` defaults to config `listen` (`0.0.0.0:8080`); `--no-transcode` refuses unsupported codecs instead of transcoding.
- **status** — read-only catalog counts, pipeline health, and active streams; `--json` for scripts, `--watch` refreshes in place.
- **backup** — checkpoint the SQLite catalog (`--out`), or `--restore <path>` (refuses while `serve` is running); the [[HBR Operate|Operate]] pipeline checkpoints on schedule (US-HBR-5).

## transcode

Force a transcode of one title to a named profile, or probe whether a profile is supported — for pre-warming the cache or diagnosing playback. The [[HBR Serve|Serve]] pipeline normally invokes this on demand (US-HBR-4).

**Usage:**
```
harbor transcode <title-id> --profile <name> [--probe]
```

**Flags:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--profile` | name | — | Target device profile (e.g. `h264-720p`). Required unless `--probe`. |
| `--probe` | bool | false | Report direct-play vs. transcode for the title without producing output. |

**Exit codes:** `0` complete (or probe playable) · `1` unknown title/profile · `2` catalog unreachable · `3` transcode failed (ffmpeg).

**Example:**
```bash
harbor transcode t-918 --profile h264-720p
# t-918 "Sintel" → h264-720p · cached 84 MB
```

## Exit codes (global)

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

Every command reads a single `harbor.toml` (found via `HARBOR_CONFIG`, else the working directory) — catalog path, watched roots, listen address, backup schedule. See [[HBR Architecture]] for how the three pipelines consume it. Subcommands never prompt; a malformed config exits 64.

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

✂ ──── example notes ──── ✂

*This is a worked `{NAME} CLI.md` example — the `harbor` CLI of the [[HBR]] project world. The help figure is `HBR CLI Help.svg`, rendered from `HBR CLI Help.txt` by `cli-help-svg.py`; edit the `.txt` and regenerate. It demonstrates the facet's load-bearing patterns: a one-line summary under the H1, the compressed SVG help figure, a flag-heavy command (`transcode`) shown compactly in the figure with a full `## transcode` section below, and one-line `## Notes` for the commands that don't need their own section.*
