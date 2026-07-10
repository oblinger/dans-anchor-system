---
description: "product requirements"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Fortify PRD](hook://p/DAS%20Fortify%20PRD)
# Fortify PRD

The current skill spec lives at [[fortify/SKILL\|SKILL.md]]. User docs live at [[DAS Fortify]].

**From:** [[F200 — Cautious Crank]]

## Overview

`fortify` is the skeptical, methodical counterpart to `crank` — invoked when normal forward iteration keeps failing on the same problem. Where crank says "pick the next thing and go," fortify says "stop, distrust your own information, and fortify the foundation before continuing." It is a *mode of execution* applied to whatever the agent is doing — not a single-bug debug command (that is `/spike`).

## Goals

- Break out of stuck loops by hardening the base (logs, tests, invariants, the agent's own model) rather than piling on more code.

## Non-Goals

- Not a merge with `/spike` (F200 Q2): spike stays diagnostic-only, a sub-step of `/code bugfix`; fortify is corrective and a peer of crank.
- Does not autonomously change application shape (visible behavior / public API / architecture) — those need approval.

## User Stories

- As the user, when cranking isn't sticking, I invoke fortify and the agent distrusts the evidence, fortifies coverage and logging, then resumes on a firmer base.

## Key decisions (F200)

- **Distrust four suspects:** the information (logs/errors), the code structure (fragility enabling the bug), the passing tests (coverage shape + assertion strictness), and the agent's own model of the system.
- **Fortify cheap→expensive:** re-read existing logs → add logging + re-run → write red tests for coverage gaps → tighten weak assertions → pin invariants in code → (with approval) propose simplification/hardening. Then drive red tests green.
- **Principles:** wall-clock cost is irrelevant, *user-interruption* cost is the constraint; batch questions, never trickle; default to "more not less" on coverage/robustness; application-shape changes need approval; prior conclusions are evidence, not truth.
- **Separate from `/spike`** — shared skeptical posture, different next step (spike collects evidence and stops; fortify acts on it).
- **Trigger:** the word `fortify` (and `/fortify`), plus an optional argument form. *(The `"` shortcut once paired with fortify later moved to `/triage`; fortify now has no single-keystroke shortcut.)*
