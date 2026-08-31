---
description: "Dan ruled 2026-08-21 (ATT T241): route on capture."
---

# [[MUSE]] · T010 — Capture-time routing: step 12 in `scripts/muse` drops addressed memos into agent Inboxes
Dan ruled 2026-08-21 (ATT T241): route on capture.

next:: open `scripts/muse`, locate step 11 `notify` (~line 797), and write step 12 exactly per the spec above; test with a fixture transcript naming one agent and one naming nobody.

## Summary

Dan ruled 2026-08-21 (ATT T241): route on capture. Add a step 12 immediately after step 11 `notify` (muse:797), inside the per-memo block: case-insensitive word-boundary scan of the TRANSCRIPT (not the title) for the Staff roster (Ash, Atticus, Boone, Ember, Hermes, Lumen, Munger, Presti, Scout, Tink, Wells, Winnie); on a hit, `state drop <anchor> --source muse --tag nudge --topic "<memo title>"` with a wiki-link to the capture (not a second copy of its text); no hit → do nothing; a drop failure must NEVER fail the ingest (log and carry on). Name-match, not LLM — must work with a dead API key. Folds the 2026-08-08 "deliver via inbox" note and the 2026-08-21 ruling handoff (both drained from MUSE Inbox 2026-08-31). Relation to [[MUSE Backlog#^T008|T008]]: T008 stamps provenance; this row delivers — both is coherent. ATT T271 carries a probe watching for this step to exist.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-31 (F614: every task has its doc; the row is its pointer).
