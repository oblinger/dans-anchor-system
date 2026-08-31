---
description: "MUSE backlog — voice-memo pipeline features"
---

| -[[MUSE Backlog]]- | → [[DAS]] → [[SKL]] → [[MUSE]] → [MUSE Backlog](hook://p/MUSE%20Backlog)  |
| --- | --- |
| ... |  |

# MUSE Backlog
<!-- state:backlog nn -->

Voice-memo ingestion + review-and-do pipeline work items.


## Ready

## Now

- **T003 — MUSE ingest is dead under launchd: every drop since 2026-07-21 was quarantined, not transcribed** [Ready] — → [[MUSE003 - MUSE ingest is dead under launchd every drop since 2026-07-21 was|T003]] — reproduce the failure under `_trust` rather than under a login shell — run `/Users/oblinger/bin/_trust muse-sweep` directly and capture the real per-file error, which the current log swallows behind the "repeatedly-failing" skip. Then diff that environment against the working interactive one (PATH, whisper model path, ffmpeg location, TCC-visible paths) and fix the difference at its source. ^T003
    - **The critical fact: the same files ingest fine when run by hand.** `skills/muse/scripts/muse ingest <path>` transcribed six of the eight on the first attempt with no changes to anything. So the fault is NOT in the transcription pipeline — it is in the `_trust muse-sweep` execution path (TCC identity, PATH, or the whisper/ffmpeg binaries resolving differently under launchd). Two files are genuinely dead and are bring-up-era tests: `2026-07-13/15-30-48.m4a` (whisper produced no transcript) and `2026-07-14/15-49-34.m4a` (corrupt — ffmpeg cannot open it).
    - Two follow-ons this exposes, both cheap and both worth doing in the same pass: **(1) the quarantine is silent** — a file that fails 3 times drops out of the log's active line and nothing surfaces, so make repeated failure raise rather than mute; **(2) `ingested 0 new` over many consecutive sweeps with a non-zero candidate count is itself an alarm condition** and nothing watches for it. Sibling of [[MUSE Backlog#^T002|T002]], which covers the FSEvent half of the delivery path — this is a different fault on the same channel.

- **T004 — The sweep cannot report its own death: three silent-failure fixes** [Ready] — → [[MUSE004 - The sweep cannot report its own death three silent-failure fixes|T004]] — three fixes, in order of how loud they make a failure. **(1) The identity gap is the root cause** — the same file succeeds by hand and fails under `_trust muse-sweep`. Capture the real stderr from the failing path (the log records `warning: ingest failed` with no reason) and fix it; `e2e-test.sh` already exercises the correct launchd route and would catch a regression if it ran on a schedule. **(2) `ingested 0 new` across consecutive runs while candidates exist must assert-fail**, not log and exit 0 — that single line was the entire visible surface of a 13-day outage and then of this one. **(3) The 3-strike quarantine must surface** — a permanently-failing file is invisible today; it should reach [[Quick]] or a notification, because a recording that will never be retried is exactly the case a human needs to know about. ^T004

- **T006 — Captures prepend to the top of Quick.md, landing them inside today's list** [Ready] — → [[MUSE006 - Captures prepend to the top of Quick.md, landing them inside today's|T006]] — Find the line in the MUSE capture path that writes to `LST/Quick.md` and change the insertion point from "top of file" to "after the first blank line following the head." Note the file gained an H1 and orientation line on 2026-08-05, so a naive "line 1" insert is now doubly wrong — it would land above the H1. ^T006

- **T007 — `e2e-test.sh` picks its fixture by smallest file size, so it selects muse's own blacklisted recording and fails deterministically** [Ready] — → [[MUSE007 - e2e-test.sh picks its fixture by smallest file size, so it selects|T007]] — Make the fixture choice explicit rather than emergent. Prefer a **pinned, committed** sample beside the script over any `find` over the user's corpus — it removes the dependence on what Dan happens to have dictated, and the metadata-remux trick that defeats SHA dedup works the same on a checked-in file. If the clone-from-corpus approach is kept, at minimum skip anything on muse's repeatedly-failing list and validate the pick before use (`ffprobe` shows ≥1 audio stream and a non-zero duration), failing with a clear message rather than a raw ffmpeg error. Separately, move the litter cleanup from the PASS branch into an `EXIT` trap so a failed run cannot leave files in the user's iCloud folder. ^T007

- **T009 — A successfully-ingested recording sat in `.muse.failures`, and the false alarm survived three morning briefings** [Ready] — → [[MUSE009 - A successfully-ingested recording sat in.muse.failures, and the false|T009]] — Make ingest success remove the file's row from `.muse.failures` — and, because that write can itself be missed, have whatever reports `muse.ingest` cross-check each failure entry against the existing MUSE items by `source_audio` before calling a file abandoned, so a disagreement between the two records surfaces as a disagreement rather than as a loss. ^T009

- **T010 — Capture-time routing: step 12 in `scripts/muse` drops addressed memos into agent Inboxes** [Ready] — → [[MUSE010 - Capture-time routing step 12 in scripts muse drops addressed memos into|T010]] — open `scripts/muse`, locate step 11 `notify` (~line 797), and write step 12 exactly per the spec above; test with a fixture transcript naming one agent and one naming nobody. ^T010

## Next

- **T008 — Stamp `addressed: lumen` when a recording is spoken to Lumen** [Ready] — → [[MUSE008 - Stamp addressed lumen when a recording is spoken to Lumen|T008]] — At ingest, detect a leading spoken "Lumen" in the transcript (the user already opens such recordings with "I'm sending a message over to the agent" / "Lumen, …") and write `addressed: lumen` into the item's frontmatter. This lets [[DAS Daybreak|Daybreak]] surface only messages addressed to [[Lumen|Lumen]] rather than every non-suppressed item past the watermark. Requested by [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]] — MUSE owns ingest, so the change lives here, not in Lumen. **Non-blocking** for Daybreak (it reads all non-suppressed items today); this is noise reduction. Detection should degrade gracefully — a miss just leaves a normal Quick item. Value is `lumen` (current agent name), not the older `luna`. ^T008

- **T002 — 2026-07-21 ingest faults — missed recording, duplicate items, refusal titles** [Ready] — → [[MUSE002 - 2026-07-21 ingest faults - missed recording, duplicate items, refusal|T002]] — Fix three faults observed in the 2026-07-21 batch, all rooted in the same iCloud FileProvider behaviour: an iCloud drop does not raise an FSEvent, so a WatchPaths-only trigger misses it, and re-materializing a file changes its SHA — which is why dedup has to key on path, not content. **(a) Missed:** `12-49-07.m4a` — the day's largest recording, an addressed "Lumen, …" message — was never ingested; recovered manually by [[Lumen|Lumen]] 2026-07-22 via whisper-cli. Add a `StartInterval` backstop so a missed FSEvent still gets swept. **(b) Duplicated:** the other 4 captures each ingested twice (A/E, B/F, C/G, D/H) — the first pass recorded the empty-string SHA (`e3b0c44…`, hashed an unmaterialized file), so content-dedup could not match the re-ingest; the user reports items landing in [[Quick]] up to 3x and is deleting them by hand. Move to path-first dedup. **(c) Refusal titles:** items D/H briefly carried a full Claude-refusal paragraph as their filename (the titler saw the "glance CNN on my screen" transcript and refused), then were retitled, leaving dead links in [[Quick]]. Titler needs a title-or-fallback guard — never a raw model reply as a filename. ^T002

## Later

- **T005 — Retire the per-ingest success notification (on or after 2026-08-19)** [Waiting 2026-08-19] — → [[MUSE005 - Retire the per-ingest success notification (on or after 2026-08-19)|T005]] — on or after **2026-08-19**, delete the `notify` call at line 662 — keep the `notify()` helper itself, because the failure path should be using it. Ask Dan first whether he wants silence outright or a weekly digest instead. ^T005
    - **Do not remove this before the failure path is loud.** Right now the banner is the **only** user-visible evidence the pipeline works at all; every log line reads like success regardless, which is exactly how the 13-day outage and the 2026-08-05 quarantine both survived. Removing the sole positive signal while the negative signal is still silent makes the estate strictly blinder. Dan's own framing already anticipates this — *"until those are really working."* T004 lands first, then this.

## Done

- **F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)** [Done] — → [[F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)]] — three-part predicate replaces overall-WPS; 6/6 real-audio test cases pass ^F001
