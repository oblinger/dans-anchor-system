---
description: "The \"go\" button."
---
# /Crank

The "go" button. One press of `/crank` (or `'`) drives **as much progress as possible** through Ready work — sequencing items and using parallel workers when items are independent. Stops only when continuing would drop quality.

Punctuation trigger: **`'`** (single apostrophe as the entire message), parallel to `triage`/`"` and `land`/`.`. Slash: `/crank`. **Slash-only — "crank" is NOT a DMUX prefix-trigger** (too common in casual speech; `'` is the dedicated keystroke).


## What it does

`/crank` is an outer-loop orchestrator. It scans the Ready queue and:

- **Dispatches parallel workers** when 2+ items are independent (different files / no shared state / no dependency edge).
- **Sequences** the rest — mint A, then B, then C — without pausing between them.
- **Continues past every successful mint.** Stopping after one mint is the failure mode, not a virtue.

When the loop exits:
- **If anything got minted**: exit silently. Press `'` again to continue the loop.
- **If nothing got minted** (no Ready at start, or quality would drop on every candidate): run `/groom` (extend the runway) + `/triage` (show the inbox), then exit.


## What stops crank

Quality is the only stop signal. Crank halts when continuing would meaningfully degrade the output:

- Spec is genuinely ambiguous and `/mint` would have to guess at intent.
- Required user input not yet given (item is `[Questions]`, not `[Ready]`).
- Agent context is fatigued — recall is degrading or the next step needs re-reading what was just dropped.
- Dependency on something that hasn't actually been verified yet.
- Item is genuinely complex enough that proper attention requires a fresh session.

"Feels like enough" and "I want to report progress" are **not** quality drops.


## The loop UX

The mental model is: **press `'` repeatedly until it stops making progress**. The system mints what it can, quietly. When it fatigues, it surfaces the full status view in one shot. You read it, decide what to do, and press `'` again — or resolve a blocking question first.

Successful presses don't interrupt you with triage; they just say "minted F5, F7, F12. Press again for next." That keeps the cranking-feeling tight.


## When NOT to use crank

- If iteration has stopped converging (same bug recurs; fixes don't stick) → use `/fortify` instead. Cautious crank with skeptical posture.
- If you want to design a new feature → `/feature`.
- If you want to see the inbox without cranking → `/triage`.
- If you want to wrap up in-flight work and stop → `/land`.
