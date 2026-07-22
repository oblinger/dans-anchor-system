---
description: "MUSE backlog — voice-memo pipeline features"
---
# MUSE Backlog
<!-- state:backlog kj -->

Voice-memo ingestion + review-and-do pipeline work items.

| -[[MUSE Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [SKL](hook://SKL) → [[MUSE]] → [MUSE Backlog](hook://p/MUSE%20Backlog)  |
| --- | --- |
| ... |  |

## Ready

## Now

## Next

- **T001 — Stamp `addressed: lumen` when a recording is spoken to Lumen** [Ready] ^T001
  - **Next:** At ingest, detect a leading spoken "Lumen" in the transcript (the user already opens such recordings with "I'm sending a message over to the agent" / "Lumen, …") and write `addressed: lumen` into the item's frontmatter. This lets [[DAS Daybreak|Daybreak]] surface only messages addressed to [[LUM|Lumen]] rather than every non-suppressed item past the watermark. Requested by [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]] — MUSE owns ingest, so the change lives here, not in Lumen. **Non-blocking** for Daybreak (it reads all non-suppressed items today); this is noise reduction. Detection should degrade gracefully — a miss just leaves a normal Quick item. Value is `lumen` (current agent name), not the older `luna`.

- **T002 — 2026-07-21 ingest faults — missed recording, duplicate items, refusal titles** [Ready] ^T002
  - **Next:** Fix three faults observed in the 2026-07-21 batch, all rooted in the known iCloud FileProvider materialization gotcha ([[gotcha-icloud-fileprovider-watchpaths]]). **(a) Missed:** `12-49-07.m4a` — the day's largest recording, an addressed "Lumen, …" message — was never ingested; recovered manually by [[LUM|Lumen]] 2026-07-22 via whisper-cli. **(b) Duplicated:** the other 4 captures each ingested twice (A/E, B/F, C/G, D/H) — the first pass recorded the empty-string SHA (`e3b0c44…`, hashed an unmaterialized file), so content-dedup could not match the re-ingest; the user reports items landing in [[Quick]] up to 3x and is deleting them by hand. Move to path-first dedup per the gotcha memory. **(c) Refusal titles:** items D/H briefly carried a full Claude-refusal paragraph as their filename (the titler saw the "glance CNN on my screen" transcript and refused), then were retitled, leaving dead links in [[Quick]]. Titler needs a title-or-fallback guard — never a raw model reply as a filename.

## Later

## Done

- **F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)** [Done] — → [[F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)]] — three-part predicate replaces overall-WPS; 6/6 real-audio test cases pass ^F001
