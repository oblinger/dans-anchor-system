---
description: Warden queries — mechanically rendered from the backlog by triage (Verifications / Ready+Next / Questions). Do not hand-edit; edit the backlog rows.
---

# [U+A]  [[Warden|Warden]]  -  Runnable 3    User 2   |   Now 2    Next 2    Later 6    Verify 0    Icebox 0    {4}

## Questions
- [[F237 — Golden corpus exists in two diverged copies — the drift oracle cannot be trusted|F237]] **(1Q)** ([[F237 — Golden corpus exists in two diverged copies — the drift oracle cannot be trusted]]) — the golden corpus exists at two paths and they have drifted; a run against the stale copy reported five false regressions during F278....
    - Q1 — The corpus lives at both `~/ob/proj/warden/Warden Corpus/` and `dans-anchor-system/warden/Warden Corpus/`. **`engine/` is byte-identical between the two roots** — verified by `diff -rq`, so the code... · *Lean (A) — the corpus's whole job is to lock the verdicts of a specific ruleset revision,...*
- [[Warden Backlog#^T009|T009]] **(1Q)** — Follow-on from T008: adding [[R-naming]] to the R-doc umbrella (= naming checked on every anchored md write) was attempted and reverted — a sweep measured 376...

## Ready
- [[Warden Backlog#^B-QFix|B-QFix]] — **Next:** Fix the next residual below at its source (repoint a renamed link, de-link a retired one, correct the flagged doc), then re-run `/audit q` to clear it — per the 100%-fix discipline.
- [[Warden Backlog#^F236|F236]] — **Next:** Two parts. (1) **Enforcement gap:** R-cards-04 (≤69-char card lines) does NOT fire on markdown save — a live edit to `RR/STAT/stat/stat distributions.md` created an 80-char card TITLE and the Warden...
- [[Warden Backlog#^T018|T018]] — **Next:** Implement the graduated rollout the user described in a 2026-07-18 voice capture (routed here by [[LUMEN]] T001). **(a) Ship at fire-once.** Do not flip full enforcement on: allow a rule to fire exactly once, then go quiet....
