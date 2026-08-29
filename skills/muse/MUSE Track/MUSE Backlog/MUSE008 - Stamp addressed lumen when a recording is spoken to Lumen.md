---
description: "Stamp `addressed: lumen` when a recording is spoken to Lumen"
---

# [[MUSE]] · T008 — Stamp `addressed: lumen` when a recording is spoken to Lumen
Stamp `addressed: lumen` when a recording is spoken to Lumen

next:: At ingest, detect a leading spoken "Lumen" in the transcript (the user already opens such recordings with "I'm sending a message over to the agent" / "Lumen, …") and write `addressed: lumen` into the item's frontmatter. This lets [[DAS Daybreak|Daybreak]] surface only messages addressed to [[LUMEN|Lumen]] rather than every non-suppressed item past the watermark. Requested by [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]] — MUSE owns ingest, so the change lives here, not in Lumen. **Non-blocking** for Daybreak (it reads all non-suppressed items today); this is noise reduction. Detection should degrade gracefully — a miss just leaves a normal Quick item. Value is `lumen` (current agent name), not the older `luna`.

## Summary

Stamp `addressed: lumen` when a recording is spoken to Lumen

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
