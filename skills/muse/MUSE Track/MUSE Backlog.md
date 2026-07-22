---
description: "MUSE backlog — voice-memo pipeline features"
---
# MUSE Backlog
<!-- state:backlog 8o -->

Voice-memo ingestion + review-and-do pipeline work items.

| -[[MUSE Backlog]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [SKL](hook://SKL) → [[MUSE]] → [MUSE Backlog](hook://p/MUSE%20Backlog) |
| --- | --- |
| ... |  |

## Ready

## Now

## Next

- **T001 — Stamp `addressed: lumen` when a recording is spoken to Lumen** [Ready] ^T001
  - **Next:** At ingest, detect a leading spoken "Lumen" in the transcript (the user already opens such recordings with "I'm sending a message over to the agent" / "Lumen, …") and write `addressed: lumen` into the item's frontmatter. This lets [[DAS Daybreak|Daybreak]] surface only messages addressed to [[LUM|Lumen]] rather than every non-suppressed item past the watermark. Requested by [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]] — MUSE owns ingest, so the change lives here, not in Lumen. **Non-blocking** for Daybreak (it reads all non-suppressed items today); this is noise reduction. Detection should degrade gracefully — a miss just leaves a normal Quick item. Value is `lumen` (current agent name), not the older `luna`.

## Later

## Done

- **F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)** [Done] — → [[F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)]] — three-part predicate replaces overall-WPS; 6/6 real-audio test cases pass ^F001
