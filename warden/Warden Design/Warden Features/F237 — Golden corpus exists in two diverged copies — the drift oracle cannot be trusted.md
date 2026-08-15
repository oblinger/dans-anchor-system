---
description: "the golden corpus lives at both ~/ob/grove/warden and dans-anchor-system/warden; blessing writes to whichever copy you ran, so the two have drifted and a run against the stale one reports false regressions"
---

# [[Warden]] · F237 — Golden corpus exists in two diverged copies — the drift oracle cannot be trusted
Warden's regression oracle is duplicated, the two copies disagree, and running the wrong one manufactures failures that are not real.

## Open Questions
<!-- state:q v8 -->

- **Q1 — Which copy of `Warden Corpus/` is canonical, and how does the other stop existing?** — The corpus lives at both `~/ob/grove/warden/Warden Corpus/` and `dans-anchor-system/warden/Warden Corpus/`. **`engine/` is byte-identical between the two roots** — verified by `diff -rq`, so the code is genuinely in sync and only the corpus has drifted. The drift is total: every case's `case.yaml` and `expected.json` differs, plus several fixtures. Cause is structural rather than accidental — `run-corpus.py --bless` writes `expected.json` beside whichever harness you invoked, so a bless is silently one-sided and the copies separate a little more on every rule change. The standing single-source-of-truth rule already forbids this shape; what it does not settle is direction, and direction interacts with the plan to split Warden into its own repo. ^F237-Q1
  - **(A)** Vault copy canonical; `~/ob/grove/warden/Warden Corpus` becomes a symlink to it. Matches today's reality — the vault copy is the one carrying current blessings, and it is committed alongside the rulesets and checkers whose verdicts it locks, so a rule change and its re-bless land in one commit. Costs the future standalone repo a self-contained corpus.
  - **(B)** `~/ob/grove/warden` canonical; the vault copy becomes the symlink. Matches the destination — Warden is meant to become its own repo, and a published rule engine should ship its own regression corpus. But it is the stale copy today, so adopting it means re-blessing from scratch, and the corpus would then live outside the vault that `warden compile` scans.
  - **(C)** Keep both, add a sync step to `warden compile` (or a `just` recipe) that copies the corpus and fails loudly when they diverge. No repo-layout commitment, and it survives the split either way. It is also the option that keeps two copies alive, which is what produced this bug.
- **Recommendation:** Lean (A) — the corpus's whole job is to lock the verdicts of a specific ruleset revision, so it belongs in the same repo and the same commit as the rules it grades; a corpus that can be blessed out of step with its rules is not an oracle. (B) is where this probably ends up after the repo split, but adopting it while it is the stale copy trades a known-good baseline for a re-derived one. (C) is explicitly the status quo with a guard bolted on. · *why-ask: locking — this picks which repo owns Warden's test surface right before the repo split, and the standalone-repo plan is yours*
- **Damage:** locking — whichever copy is retired stops accumulating history, and the choice pre-commits part of the Warden repo-split layout. Cheap to execute, expensive to reverse once blessings accumulate on the surviving side.

## Summary

Warden's golden corpus is its regression oracle: rule × fixture × blessed-verdict, with `FAIL` meaning a real regression and `STALE-DIFF` meaning expected churn that needs a conscious re-bless. It only works if there is exactly one of it.

There are two, and they disagree.

| | `~/ob/grove/warden/` | `dans-anchor-system/warden/` |
|---|---|---|
| `engine/` | identical | identical |
| `Warden Corpus/` | **stale** — blessed against a pre-T059 ruleset | current |
| Run result 2026-07-30 | 1/14, four `error` verdicts | 14/14 after bless |

**Observed cost, 2026-07-30.** A corpus run during [[TINK Backlog#^F278|F278]] against the `~/ob/grove/warden` copy returned 1/14 with 48 verdict removals, 18 non-`pass` additions, and `R-query-16` flipping `pass` → `fail`. Every one of those was an artifact of the stale copy: its fixtures still carried the pre-F260 banner (`Ready 0    Questions 1`) that [[TINK Backlog#^T059|T059]] had already replaced in the other copy. Read at face value, that output says the change under test broke five rules. It broke none — the canonical copy showed zero removals and only the new rule's verdicts. An oracle that reports confident false regressions is worse than no oracle, because the honest response to it is to distrust the change rather than the tool.

This is the same family as [[F285 — Warden corpus scoping — rules go quiet outside the tree that declares them|F285]]'s two-live-roots finding, and the second time in one session that duplicated Warden state cost real diagnosis time.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** One corpus exists. Running the harness from either path grades the same cases against the same `expected.json`, and a `--bless` from either path is visible from the other.

**How it will be verified.** `diff -rq` across the two `Warden Corpus/` paths reports no differences (or one path is a symlink to the other), then `run-corpus.py` from each path in turn reports the same `N/14` and the same blessed-against hash.

## Design

Settled once Q1 picks a direction; the execution is a delete-and-symlink either way. One constraint applies to all three options: whatever survives must make a one-sided bless impossible, since that — not the initial duplication — is what let the copies drift apart case by case. Under (A) or (B) the symlink enforces it structurally; under (C) the guard has to fail the build rather than warn, or it will be ignored exactly as the divergence was.

## Status

**Questions** (2026-07-30) — found during F278 when the stale copy reported five false regressions. The canonical copy is blessed 14/14 and F278 landed against it; the stale copy was left untouched rather than half-synced, so nothing depends on this being resolved quickly.


**Backlog-row record (moved here 2026-08-15, F332 conversion):** **Migrated from the Warden backlog 2026-08-11** (was `F237` there) at Dan's direction — *"why don't we pull everything from the warden backlog into your backlog … that way we're just managing it directly through you"*. Warden has no separate queue any more; [[Warden Backlog]] is a closed historical record. → [[F237 — Golden corpus exists in two diverged copies — the drift oracle cannot be trusted]] — the golden corpus exists at two paths and they have drifted; a run against the stale copy reported five false regressions during [[TINK Backlog#^F278|F278]]. Q1 picks which copy is canonical (lean A: vault copy, symlink the other).

## Resolved

### The stale copy was reverted, not repaired
**Choice:** `git checkout -- "Warden Corpus"` on `~/ob/grove/warden`, leaving it exactly as committed.

Mid-investigation the stale fixtures were edited toward parity to test the hypothesis that they were the cause. They were, but a half-synced duplicate is worse than a cleanly stale one: it looks current, so the next person to run it gets a subtler wrong answer than the loud 1/14 that made this visible. Alternative considered: finish syncing both copies. Rejected — it treats the duplication as acceptable and re-does the same one-sided bless from the other side, which is the defect.
