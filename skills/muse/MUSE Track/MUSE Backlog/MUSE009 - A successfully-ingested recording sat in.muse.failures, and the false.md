---
description: "Found 2026-08-28."
---

# [[MUSE]] · T009 — A successfully-ingested recording sat in `.muse.failures`, and the false alarm survived three morning briefings
Found 2026-08-28.

next:: Make ingest success remove the file's row from `.muse.failures` — and, because that write can itself be missed, have whatever reports `muse.ingest` cross-check each failure entry against the existing MUSE items by `source_audio` before calling a file abandoned, so a disagreement between the two records surfaces as a disagreement rather than as a loss.

## Summary

Found 2026-08-28. `Log/MUSE/.muse.failures` carried `124 7045179 …/2026-08-19/16-51-19.m4a` — three strikes, never retried, reported by `muse.ingest` as a permanently abandoned 14-minute recording. **It had already been ingested successfully.** [[Log Muse|MUSE 2026-08-19 A]] names that exact path as its `source_audio`, and its `word_count: 1353` matches an independent local re-transcription word for word. So the audio was transcribed, titled, filed, and acted on — [[Scout]] ran the survey it asked for, and it is at `Topic/Search/Survey/2026-08-19 Recording a meeting on the iPhone and getting it to the laptop/` — while the ledger went on reporting it as lost. **The cost was not the file, it was the three mornings.** [[Lumen|Lumen]] surfaced it as a live decision in the [[Lumen Day|briefing]] on 8/26, 8/27 and 8/28 asking Dan to choose between recovering it and writing it off, and on the third morning he wrote it off — a decision taken about a thing that was never missing. **The failure ledger and the ingest record disagreed and nothing compared them.** The stale line was removed by hand on 2026-08-28 (backup at `.muse.failures.bak-2026-08-28`), which clears the symptom and not the defect. Filed by Lumen.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
