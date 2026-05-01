# /Crank

The "go" button. One press of `crank` drives a full sweep of Ready work — mint as many items as the agent can, then either exit silently (still finding work) or surface a status view + actionable inbox (fatigued and waiting on you).

DMUX trigger: **`crank`** (prefix-trigger; speaking `crank` stashes `/crank`, parallel to `snip` / `commission` / `fortify` / `groom` / `triage` / `mint`). Punctuation: **`'`** (single apostrophe as the entire message), parallel to `triage`/`"` and `land`/`.`. Slash: `/crank`.


## What it does

`/crank` is an outer-loop orchestrator. Per loop iteration: pick a Ready item, invoke `/mint`, check result, repeat. When the loop exits naturally:

- **If anything got minted**: exit silently. Press `crank` again to continue the loop.
- **If nothing got minted** (no Ready at start, or agent hedged): run `/groom` (extend the runway) + `/triage` (show the inbox), then exit.


## The loop UX

The mental model is: **press `crank` repeatedly until it stops making progress**. The system mints what it can, quietly. When it fatigues, it surfaces the full status view in one shot. You read it, decide what to do, and press `crank` again — or resolve a blocking question first.

Successful presses don't interrupt you with triage; they just say "minted F5, F7, F12. Press again for next." That keeps the cranking-feeling tight.


## Second press

If you press `crank` right after a no-action exit (where it ran groom + triage and stopped), the next press is a **second press**. Three things change:

1. **Lower threshold**: the agent picks *any* Ready item, even if it had hedged on which to choose first time.
2. **Skips `/groom`**: it just ran; running it again wouldn't help.
3. **If still stuck**: the agent names the specific blocker (e.g., "Cannot make progress without input on F14 Q1") rather than spinning into a third no-action loop.

The second press is the user saying "I see what you told me; go anyway." On the third press (if you press past stuck), the cycle resets to first-press behavior.


## Compound

| You say | Effect |
|---|---|
| `crank` | First-press loop. |
| `crank` (right after a no-action exit) | Second-press loop with lowered threshold. |
| `crank` (after stuck-blocker, having resolved a Q) | Fresh first-press loop. |
| `'` (single apostrophe alone) | Same as `crank`. |


## When NOT to use crank

- If iteration has stopped converging (same bug recurs; fixes don't stick) → use `/fortify` instead. Cautious crank with skeptical posture.
- If you want to design a new feature → `/feature`.
- If you want to see the inbox without cranking → `/triage`.
- If you want to wrap up in-flight work and stop → `/land`.
