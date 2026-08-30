---
description: "2026-07-21 ingest faults — missed recording, duplicate items, refusal titles"
---

# [[MUSE]] · T002 — 2026-07-21 ingest faults — missed recording, duplicate items, refusal titles
2026-07-21 ingest faults — missed recording, duplicate items, refusal titles

next:: Fix three faults observed in the 2026-07-21 batch, all rooted in the same iCloud FileProvider behaviour: an iCloud drop does not raise an FSEvent, so a WatchPaths-only trigger misses it, and re-materializing a file changes its SHA — which is why dedup has to key on path, not content. **(a) Missed:** `12-49-07.m4a` — the day's largest recording, an addressed "Lumen, …" message — was never ingested; recovered manually by [[Lumen|Lumen]] 2026-07-22 via whisper-cli. Add a `StartInterval` backstop so a missed FSEvent still gets swept. **(b) Duplicated:** the other 4 captures each ingested twice (A/E, B/F, C/G, D/H) — the first pass recorded the empty-string SHA (`e3b0c44…`, hashed an unmaterialized file), so content-dedup could not match the re-ingest; the user reports items landing in [[Quick]] up to 3x and is deleting them by hand. Move to path-first dedup. **(c) Refusal titles:** items D/H briefly carried a full Claude-refusal paragraph as their filename (the titler saw the "glance CNN on my screen" transcript and refused), then were retitled, leaving dead links in [[Quick]]. Titler needs a title-or-fallback guard — never a raw model reply as a filename.

## Summary

2026-07-21 ingest faults — missed recording, duplicate items, refusal titles

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
