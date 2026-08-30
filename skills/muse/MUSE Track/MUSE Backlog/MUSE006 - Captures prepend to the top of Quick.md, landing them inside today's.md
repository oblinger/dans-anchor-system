---
description: "Found 2026-08-05 by [[Lumen|Lumen]], who maintains the block MUSE is writing into."
---

# [[MUSE]] · T006 — Captures prepend to the top of Quick.md, landing them inside today's list
Found 2026-08-05 by [[Lumen|Lumen]], who maintains the block MUSE is writing into.

next:: Find the line in the MUSE capture path that writes to `LST/Quick.md` and change the insertion point from "top of file" to "after the first blank line following the head." Note the file gained an H1 and orientation line on 2026-08-05, so a naive "line 1" insert is now doubly wrong — it would land above the H1.

## Summary

Found 2026-08-05 by [[Lumen|Lumen]], who maintains the block MUSE is writing into. **MUSE prepends each capture to the very top of `LST/Quick.md`, and as of 2026-08-05 that top block is no longer neutral space** — Dan asked Lumen to keep a short **today-list** there, his own pre-existing convention restated in voice that day: *"take all the things I was going to do today, put it above the first line break in Quick."* Its rules now live in that file's `# BRIEF` — today-only, nothing standard or recurring, short bullets, Lumen maintains it and Dan strikes things off. **So every MUSE capture now arrives disguised as one of today's tasks.** Two were sitting there when this was found — `MUSE 2026-08-02 A Doctor needs to challenge me more` and `MUSE 2026-08-04 A Testing Voice Memo System` — neither a task, both dated days earlier, and both reading at a glance as things Dan meant to do today. They were swept below the break by hand. **The fix is a write target, not a policy:** insert after the first blank line rather than at the top, so captures land at the head of the standing backlog where they have always belonged and the today block stays Lumen's. Sweeping by hand is documented in [[Quick]]'s BRIEF only until this ships.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
