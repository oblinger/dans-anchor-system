---
description: "**From [[ATT|Atticus]] 2026-08-05.** Six recordings failed ingest and four were permanently quarantined, one from the previous day, while `com.oblinger.muse-ingest` logged `find returned 68 candidates; ingested 0 new` every five minutes …"
---

# [[MUSE]] · T004 — The sweep cannot report its own death: three silent-failure fixes
**From [[ATT|Atticus]] 2026-08-05.** Six recordings failed ingest and four were permanently quarantined, one from the previous day, while `com.oblinger.muse-ingest` logged `find returned 68 candidates; ingested 0 new` every five minutes …

next:: three fixes, in order of how loud they make a failure. **(1) The identity gap is the root cause** — the same file succeeds by hand and fails under `_trust muse-sweep`. Capture the real stderr from the failing path (the log records `warning: ingest failed` with no reason) and fix it; `e2e-test.sh` already exercises the correct launchd route and would catch a regression if it ran on a schedule. **(2) `ingested 0 new` across consecutive runs while candidates exist must assert-fail**, not log and exit 0 — that single line was the entire visible surface of a 13-day outage and then of this one. **(3) The 3-strike quarantine must surface** — a permanently-failing file is invisible today; it should reach [[Quick]] or a notification, because a recording that will never be retried is exactly the case a human needs to know about.

## Summary

**From [[ATT|Atticus]] 2026-08-05.** Six recordings failed ingest and four were permanently quarantined, one from the previous day, while `com.oblinger.muse-ingest` logged `find returned 68 candidates; ingested 0 new` every five minutes and exited 0 forever. Nothing anywhere treated that as a failure. Two of the four — `2026-08-04/10-08-55` and `2026-08-02/15-48-48` — **ingested cleanly on the first hand-run of `muse ingest`**, so the content was fine and only the launchd/`_trust` execution context was not. The 2026-08-04 file is Dan testing this very pathway (*"just to see if it is going to work"*); it was eaten. Both are now recovered. The other two are genuinely dead: 646 bytes with no speech, and 76 MB that ffmpeg rejects as invalid data.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
