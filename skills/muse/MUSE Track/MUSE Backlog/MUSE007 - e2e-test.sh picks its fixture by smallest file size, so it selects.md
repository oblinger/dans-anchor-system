---
description: "Found 2026-08-06 by [[Tink]] running the muse suite for [[Tink Backlog#^T346|TINK T346]]."
---

# [[MUSE]] · T007 — `e2e-test.sh` picks its fixture by smallest file size, so it selects muse's own blacklisted recording and fails deterministically
Found 2026-08-06 by [[Tink]] running the muse suite for [[Tink Backlog#^T346|TINK T346]].

next:: Make the fixture choice explicit rather than emergent. Prefer a **pinned, committed** sample beside the script over any `find` over the user's corpus — it removes the dependence on what Dan happens to have dictated, and the metadata-remux trick that defeats SHA dedup works the same on a checked-in file. If the clone-from-corpus approach is kept, at minimum skip anything on muse's repeatedly-failing list and validate the pick before use (`ffprobe` shows ≥1 audio stream and a non-zero duration), failing with a clear message rather than a raw ffmpeg error. Separately, move the litter cleanup from the PASS branch into an `EXIT` trap so a failed run cannot leave files in the user's iCloud folder.

## Summary

Found 2026-08-06 by [[Tink]] running the muse suite for [[Tink Backlog#^T346|TINK T346]]. `e2e-test.sh:80` chooses its source audio with `find … -exec stat -f '%z %N' | sort -n | head -1` — **the smallest m4a anywhere under the JPR tree**. On this machine that is `Documents/2026-07-13/15-30-48.m4a` at **646 bytes**, which is one of the two files muse itself has already given up on: the same run logs `sweep: skipping repeatedly-failing file (3 fails)` against it. So the test hands ffmpeg a file with no usable audio stream, `-c:a copy` produces `Output file does not contain any stream`, and the run fails at transcription with `_transcribe: ffmpeg conversion failed`. **Not a flake — a monotone.** "Smallest" and "most degenerate" are the same ordering in a corpus of voice memos, so as broken recordings accumulate the selector converges on them and stays there; the test was passing earlier only because no sufficiently-broken file had landed yet. The comment above the selector explains why cloning beats synthesizing (macOS `say` yields 0.01 s audio on this machine) and that reasoning is sound — it is the *choice of clone source* that is wrong. **Two more things worth knowing before touching it.** (1) The failure path leaves litter **in the user's live iCloud folder**: the run writes `e2etest<epoch>.m4a` into `Documents/<today>/` and the on-PASS cleanup at step 7 never runs, so every failed run leaves a file (and possibly a new dated folder) in Just-Press-Record. One such artifact from this investigation was removed by hand; check for `e2etest*` before assuming the tree is clean. (2) A **passing** run is a live-system operation by design — it drops audio into the real JPR directory, kicks the real launchd agent, and prepends to the real [[Quick]] — so it is not safe to loop for flake-hunting the way the other three muse tests are. The 25-sweep repeat run for T108 deliberately excluded it for that reason.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-28 (F614: every task has its doc; the row is its pointer).
