---
description: "**Waiting on: [[MUSE Backlog#^T004|T004]] landing, and the 2026-08-19 date.** **From Dan 2026-08-05:** *'Muse is always popping up dialogue boxes on my screen."
---

# [[MUSE]] · T005 — Retire the per-ingest success notification (on or after 2026-08-19)
**Waiting on: [[MUSE Backlog#^T004|T004]] landing, and the 2026-08-19 date.** **From Dan 2026-08-05:** *"Muse is always popping up dialogue boxes on my screen.

next:: on or after **2026-08-19**, delete the `notify` call at line 662 — keep the `notify()` helper itself, because the failure path should be using it. Ask Dan first whether he wants silence outright or a weekly digest instead.

## Summary

**Waiting on: [[MUSE Backlog#^T004|T004]] landing, and the 2026-08-19 date.** **From Dan 2026-08-05:** *"Muse is always popping up dialogue boxes on my screen. It just tells me that it ran. I guess maybe we can leave it go for a little bit until those are really working. But maybe in 2 weeks we should remove those, that way they're not always out there."* One banner fires per successfully ingested recording — `muse` line 662, `notify "MUSE $ymd $letter: $title"`, with the `Tink` sound. It exists as reassurance while the pipeline was unproven, and Dan has now had enough of it.

- **Do not remove this before the failure path is loud.** Right now the banner is the **only** user-visible evidence the pipeline works at all; every log line reads like success regardless, which is exactly how the 13-day outage and the 2026-08-05 quarantine both survived. Removing the sole positive signal while the negative signal is still silent makes the estate strictly blinder. Dan's own framing already anticipates this — *"until those are really working."* T004 lands first, then this.

## Status

**Waiting 2026-08-19** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
