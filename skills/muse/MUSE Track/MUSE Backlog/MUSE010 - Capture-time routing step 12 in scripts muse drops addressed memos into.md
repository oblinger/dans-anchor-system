---
description: "Superseded-and-widened 2026-08-31: step 12 delivers EVERY ingested memo to Sparks (single hardened ingress); the roster-name scan becomes a hint in the drop, not the router."
---

# [[MUSE]] · T010 — Capture-time routing: step 12 in `scripts/muse` delivers every memo to Sparks
Dan ruled 2026-08-21 (ATT T241): route on capture — then widened it 2026-08-31 (ATT T299 / pebble [[Atticus P0017]]): **Sparks is the recipient of ALL MUSE inputs**, the single hardened ingress where injection screening lives. Per-agent fan-out at capture is superseded; Sparks forwards after screening.

next:: open `scripts/muse`, locate step 11 `notify` (~line 797), and write step 12 per the 2026-08-31 spec in the Summary; test with a fixture transcript naming one agent and one naming nobody (both must land in Sparks's Inbox, the first carrying the hint line).

## Summary

**Spec as of 2026-08-31** (supersedes the 2026-08-21 per-agent form; both rulings are Dan's, the second explicitly on top of the first). Add a step 12 immediately after step 11 `notify` (muse:797), inside the per-memo block:

- **Deliver EVERY ingested memo to Sparks**: `state drop Sparks --source muse --tag nudge --topic "<memo title>"` with a **wiki-link to the capture** (never a second copy of its text — copies drift).
- **The roster scan survives as a hint, not a router**: case-insensitive word-boundary scan of the TRANSCRIPT (not the title — the title is generated) for the Staff roster (Ash, Atticus, Boone, Ember, Hermes, Lumen, Munger, Presti, Scout, Tink, Wells, Winnie); on a hit, include a `mentions: <names>` line in the drop body. Sparks screens the item and forwards to the named agent, mints a pebble, or hands back to Dan.
- **A drop failure must NEVER fail the ingest** — log and carry on; the memo landing in the corpus is the load-bearing act.
- Name-match, not LLM — must work with a dead API key.
- `Log/MUSE/` remains the append-only historical record regardless of delivery (no deletions; retirement after a period is a separate, future decision). Whether ingest should STOP prepending to `Quick.md` once Sparks delivery works is Dan's call — see [[MUSE Backlog#^T006|T006]]; do not remove the Quick write in this task.

Folds the 2026-08-08 "deliver via inbox" note and the 2026-08-21 ruling handoff (drained from MUSE Inbox 2026-08-31). Relation to [[MUSE Backlog#^T008|T008]]: T008 stamps provenance; this row delivers — both is coherent. ATT T271 carries a probe watching for this step to exist. The wider vision (injection-defense layer in front of Sparks, real-time command-line tempo) is pebble [[Atticus P0017]] — out of scope here.

## Status

**Ready** — minted from the backlog row by `state` on 2026-08-31 (F614: every task has its doc; the row is its pointer).
