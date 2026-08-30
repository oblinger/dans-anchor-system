---
description: "**Found by [[Lumen]] Daybreak 2026-08-03.** The watch channel went silent for 13 days without any signal reaching the user or Lumen."
---

# [[MUSE]] · T003 — MUSE ingest is dead under launchd: every drop since 2026-07-21 was quarantined, not transcribed
**Found by [[Lumen]] Daybreak 2026-08-03.** The watch channel went silent for 13 days without any signal reaching the user or Lumen.

next:: reproduce the failure under `_trust` rather than under a login shell — run `/Users/oblinger/bin/_trust muse-sweep` directly and capture the real per-file error, which the current log swallows behind the "repeatedly-failing" skip. Then diff that environment against the working interactive one (PATH, whisper model path, ffmpeg location, TCC-visible paths) and fix the difference at its source.

## Summary

**Found by [[Lumen]] Daybreak 2026-08-03.** The watch channel went silent for 13 days without any signal reaching the user or Lumen. [muse-ingest.log](~/Library/Logs/muse-ingest.log) shows the same six files quarantined on every 5-minute sweep — `muse: sweep: find returned 66 candidates; ingested 0 new` — after each hit the 3-strike limit. The launchd agent is loaded and exiting 0, so nothing looked broken from the outside; the agent reports success while ingesting nothing, which is why this ran undetected for nearly two weeks.

- **The critical fact: the same files ingest fine when run by hand.** `skills/muse/scripts/muse ingest <path>` transcribed six of the eight on the first attempt with no changes to anything. So the fault is NOT in the transcription pipeline — it is in the `_trust muse-sweep` execution path (TCC identity, PATH, or the whisper/ffmpeg binaries resolving differently under launchd). Two files are genuinely dead and are bring-up-era tests: `2026-07-13/15-30-48.m4a` (whisper produced no transcript) and `2026-07-14/15-49-34.m4a` (corrupt — ffmpeg cannot open it).
- Two follow-ons this exposes, both cheap and both worth doing in the same pass: **(1) the quarantine is silent** — a file that fails 3 times drops out of the log's active line and nothing surfaces, so make repeated failure raise rather than mute; **(2) `ingested 0 new` over many consecutive sweeps with a non-zero candidate count is itself an alarm condition** and nothing watches for it. Sibling of [[MUSE Backlog#^T002|T002]], which covers the FSEvent half of the delivery path — this is a different fault on the same channel.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
