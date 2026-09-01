---
description: "Superseded-and-widened 2026-08-31: step 12 delivers EVERY ingested memo to Sparks (single hardened ingress); the roster-name scan becomes a hint in the drop, not the router."
---

# [[MUSE]] · T010 — Capture-time routing: step 12 in `scripts/muse` delivers every memo to Sparks
Dan ruled 2026-08-21 (ATT T241): route on capture — then widened it 2026-08-31 (ATT T299 / pebble [[Atticus P0017]]): **Sparks is the recipient of ALL MUSE inputs**, the single hardened ingress where injection screening lives. Per-agent fan-out at capture is superseded; Sparks forwards after screening.

next:: none — shipped and fixture-verified 2026-08-31; the next real memo is the natural exercise.

## Summary

**Spec as of 2026-08-31** (supersedes the 2026-08-21 per-agent form; both rulings are Dan's, the second explicitly on top of the first). Add a step 12 immediately after step 11 `notify` (muse:797), inside the per-memo block:

- **Deliver EVERY ingested memo to Sparks**: `state drop Sparks --source muse --tag nudge --topic "<memo title>"` with a **wiki-link to the capture** (never a second copy of its text — copies drift).
- **The roster scan survives as a hint, not a router**: case-insensitive word-boundary scan of the TRANSCRIPT (not the title — the title is generated) for the Staff roster (Ash, Atticus, Boone, Ember, Hermes, Lumen, Munger, Presti, Scout, Tink, Wells, Winnie); on a hit, include a `mentions: <names>` line in the drop body. Sparks screens the item and forwards to the named agent, mints a pebble, or hands back to Dan.
- **A drop failure must NEVER fail the ingest** — log and carry on; the memo landing in the corpus is the load-bearing act.
- Name-match, not LLM — must work with a dead API key.
- `Log/MUSE/` remains the append-only historical record regardless of delivery (no deletions; retirement after a period is a separate, future decision). Whether ingest should STOP prepending to `Quick.md` once Sparks delivery works is Dan's call — see [[MUSE Backlog#^T006|T006]]; do not remove the Quick write in this task.

Folds the 2026-08-08 "deliver via inbox" note and the 2026-08-21 ruling handoff (drained from MUSE Inbox 2026-08-31). Relation to [[MUSE Backlog#^T008|T008]]: T008 stamps provenance; this row delivers — both is coherent. ATT T271 carries a probe watching for this step to exist. The wider vision (injection-defense layer in front of Sparks, real-time command-line tempo) is pebble [[Atticus P0017]] — out of scope here.

## Status

**Done** — shipped 2026-08-31 by Atticus as commit 93acef5c: `deliver_to_sparks()` + the step-12 call after `notify`, MUSE_STATE_CLI resolved relative to the script. Fixture-tested live: one transcript naming Lumen and one naming nobody both landed in [[Sparks Inbox]] (the first with `mentions: Lumen`), then tagged DONE as fixtures. Naturally exercised by the next real dictation; ATT T241's probe now finds the step.
