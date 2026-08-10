---
description: "product requirements"
---

:>> [[DAS]] → [design](hook://design) → [DAS Crank PRD](hook://p/DAS%20Crank%20PRD)
# Crank PRD
The current skill spec lives at [[crank/SKILL\|SKILL.md]]. User docs live at [[DAS Crank]].

**From:** [[F195 — Crank as Skill]] · [[F196 — Crank Posture Enforcement]]

## Overview

`/crank` is the **outer-loop orchestrator** over `/mint`: one press = a full sweep of the Ready queue, not a single mint. It loops — pick a Ready item, `/mint` it, repeat — until no Ready items remain or a mint blocks/fails (F195). It composes the existing skills (`/mint`, `/groom`, `/ask`) into one user-press behavior.

## Goals

- Drive maximum autonomous progress per press — sequence as many Ready items as possible, parallelizing independent ones.
- Surface status + inbox exactly when the loop fatigues, not between mint cycles.
- Make stop-early violations structurally impossible-or-obvious, not merely discouraged (F196).

## Non-Goals

- No runtime/harness enforcement of the posture (deferred — needs docket/Rust work).
- Not generalized to `/mint`, `/code mint`, etc. — crank only.
- No model-selection rules (too speculative without measurement).

## User Stories

- As the user, I press `crank` repeatedly and the system keeps minting Ready work silently until it genuinely cannot continue.
- As the user, when crank stops, I get a one-shot status + actionable inbox via `/groom` + `/ask`.

## Post-sweep branch

Branch on the binary "did anything get minted this turn?":
- **Yes** → exit silently (the hot-loop path; the user keeps pressing to continue).
- **No** → run `/groom` (extend the runway) then `/ask` (surface the inbox), and exit.

The fallbacks fire *only* on the no-action branch — they're the "what to do when crank stops" surface, not always-at-end actions. (F195 also specified a *second-press* lowering of the autonomy threshold keyed off conversation history; this was later simplified away — every press now runs the same loop end-to-end, with no second-press semantics.)

## Posture enforcement (F196 — design, partly unresolved)

The recurring failure mode is agents stopping after one mint "to report progress" despite spec language forbidding it — spec prose alone does not constrain the behavior. F196 proposed *structural* levers to make violations impossible-or-obvious rather than merely discouraged: a mandatory pre-exit stop-reason enum (continue unless the reason is on the list), a parallel-batch scan as the *first* runbook step, silence between mints, anti-patterns hoisted into § Posture, and a lightweight exit self-check. The current SKILL.md carries the strong "lazy is the failure mode" posture; the enum/self-check mechanics from F196 remained open design (its Q1 root-cause diagnosis was never resolved).
