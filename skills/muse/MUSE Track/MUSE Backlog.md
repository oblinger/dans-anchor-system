---
description: "MUSE backlog — voice-memo pipeline features"
---
# MUSE Backlog
<!-- state:backlog 9h -->

Voice-memo ingestion + review-and-do pipeline work items.

| -[[MUSE Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [SKL](hook://SKL) → [[MUSE]] → [MUSE Backlog](hook://p/MUSE%20Backlog)  |
| --- | --- |
| ... |  |

## Ready

## Now

- **T003 — MUSE ingest is dead under launchd: every drop since 2026-07-21 was quarantined, not transcribed** [Ready] — **Found by [[LUMEN]] Daybreak 2026-08-03.** The watch channel went silent for 13 days without any signal reaching the user or Lumen. [muse-ingest.log](~/Library/Logs/muse-ingest.log) shows the same six files quarantined on every 5-minute sweep — `muse: sweep: find returned 66 candidates; ingested 0 new` — after each hit the 3-strike limit. The launchd agent is loaded and exiting 0, so nothing looked broken from the outside; the agent reports success while ingesting nothing, which is why this ran undetected for nearly two weeks. ^T003
  - **Next:** reproduce the failure under `_trust` rather than under a login shell — run `/Users/oblinger/bin/_trust muse-sweep` directly and capture the real per-file error, which the current log swallows behind the "repeatedly-failing" skip. Then diff that environment against the working interactive one (PATH, whisper model path, ffmpeg location, TCC-visible paths) and fix the difference at its source.
    - **The critical fact: the same files ingest fine when run by hand.** `skills/muse/scripts/muse ingest <path>` transcribed six of the eight on the first attempt with no changes to anything. So the fault is NOT in the transcription pipeline — it is in the `_trust muse-sweep` execution path (TCC identity, PATH, or the whisper/ffmpeg binaries resolving differently under launchd). Two files are genuinely dead and are bring-up-era tests: `2026-07-13/15-30-48.m4a` (whisper produced no transcript) and `2026-07-14/15-49-34.m4a` (corrupt — ffmpeg cannot open it).
    - Two follow-ons this exposes, both cheap and both worth doing in the same pass: **(1) the quarantine is silent** — a file that fails 3 times drops out of the log's active line and nothing surfaces, so make repeated failure raise rather than mute; **(2) `ingested 0 new` over many consecutive sweeps with a non-zero candidate count is itself an alarm condition** and nothing watches for it. Sibling of [[MUSE Backlog#^T002|T002]], which covers the FSEvent half of the delivery path — this is a different fault on the same channel.

## Next

- **T001 — Stamp `addressed: lumen` when a recording is spoken to Lumen** [Ready] ^T001
  - **Next:** At ingest, detect a leading spoken "Lumen" in the transcript (the user already opens such recordings with "I'm sending a message over to the agent" / "Lumen, …") and write `addressed: lumen` into the item's frontmatter. This lets [[DAS Daybreak|Daybreak]] surface only messages addressed to [[LUMEN|Lumen]] rather than every non-suppressed item past the watermark. Requested by [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]] — MUSE owns ingest, so the change lives here, not in Lumen. **Non-blocking** for Daybreak (it reads all non-suppressed items today); this is noise reduction. Detection should degrade gracefully — a miss just leaves a normal Quick item. Value is `lumen` (current agent name), not the older `luna`.

- **T002 — 2026-07-21 ingest faults — missed recording, duplicate items, refusal titles** [Ready] ^T002
  - **Next:** Fix three faults observed in the 2026-07-21 batch, all rooted in the same iCloud FileProvider behaviour: an iCloud drop does not raise an FSEvent, so a WatchPaths-only trigger misses it, and re-materializing a file changes its SHA — which is why dedup has to key on path, not content. **(a) Missed:** `12-49-07.m4a` — the day's largest recording, an addressed "Lumen, …" message — was never ingested; recovered manually by [[LUMEN|Lumen]] 2026-07-22 via whisper-cli. Add a `StartInterval` backstop so a missed FSEvent still gets swept. **(b) Duplicated:** the other 4 captures each ingested twice (A/E, B/F, C/G, D/H) — the first pass recorded the empty-string SHA (`e3b0c44…`, hashed an unmaterialized file), so content-dedup could not match the re-ingest; the user reports items landing in [[Quick]] up to 3x and is deleting them by hand. Move to path-first dedup. **(c) Refusal titles:** items D/H briefly carried a full Claude-refusal paragraph as their filename (the titler saw the "glance CNN on my screen" transcript and refused), then were retitled, leaving dead links in [[Quick]]. Titler needs a title-or-fallback guard — never a raw model reply as a filename.

## Later

## Done

- **F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)** [Done] — → [[F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)]] — three-part predicate replaces overall-WPS; 6/6 real-audio test cases pass ^F001
