---
name: crank
description: >
  Outer-loop orchestrator that drives autonomous progress. Picks Ready
  items from the current anchor's backlog and invokes /mint per item in
  a loop until natural stopping. If anything got minted, exits silently
  so the user can re-press `crank` to continue the loop. If nothing got
  minted (no Ready at start, or agent hedged), falls back to /groom +
  /triage to extend the runway and surface the inbox. On second press
  (user re-invoking after a no-action exit), lowers the threshold for
  autonomous action and skips the futile /groom; if still stuck, names
  the specific blocker. Use when the user types `/crank`, says `crank`
  (DMUX auto-prefixes), or sends `'` (a single apostrophe) as the
  entire message.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Crank — Autonomous-Progress Loop

`crank` is the user's "go" button. One press drives a full sweep of Ready work; the system mints what it can, and either exits silently (still finding work) or surfaces a status view + actionable inbox (fatigued and waiting on the user). The user can keep pressing `crank` to keep going.

DMUX trigger: **`crank`** (prefix-trigger; speaking `crank` stashes `/crank`, parallel to `snip` / `commission` / `fortify` / `groom` / `triage` / `mint`). Punctuation: **`'`** (single apostrophe as the entire message), parallel to `triage`/`"` and `land`/`.`. Slash invocation: `/crank` (with optional argument; passed to `/mint` if action is taken).


## When to Use

- User types `/crank`, says `crank` (DMUX auto-prefixes), or sends `'` as the entire message.
- User says "keep going", "make progress", "do the next thing", "what's next?".
- After resolving a question or unblocking a feature, when the user wants the system to take it from here.


## Mechanism — outer loop over `/mint`

`crank` is an **orchestrator**, not a worker. Each loop iteration delegates to `/mint`, which handles a single Ready item end-to-end (spec → code → test → review → verify → commit).

```
loop:
  next = pick a Ready item from the backlog
  if next is None:           # nothing Ready
      break to fallback
  result = /mint next
  if result is "blocked" or "failed":
      break to fallback
  # else: minted clean, increment count, continue loop
```

Loop exits on (a) no more Ready items, (b) a mint returns non-success, or (c) any other natural stopping condition the agent recognizes (context fatigue, decision-cost too high, etc.).

One press of `crank` = the full sweep, not a single mint.


## Post-loop branch — did anything get minted?

| Outcome | Path |
|---|---|
| **≥1 successful `/mint`** | Exit silently. Print the one-line success summary. User keeps pressing `crank` to continue the loop; no `/groom` or `/triage` interrupt between mint cycles. |
| **Zero successful `/mint`** | No-action branch: run `/groom`, then `/triage`, then exit. Print the one-line no-action summary. User re-invokes `crank` if they want another sweep over freshly-readied items. |

Both `/groom` and `/triage` are **no-action fallbacks** — they fire only when crank produced zero mints this turn. Successful cranks stay quiet to preserve the loop UX (the user keeps pressing crank; the system keeps minting; only when it fatigues does the system surface a full status view).


## Second-press detection

At invocation, inspect the **prior assistant turn** in the conversation history:

- If the prior turn ran `/crank` and exited via the **no-action branch** (look for the no-action one-line summary marker — see § Output format below), the current invocation is a **second press**.
- Otherwise (prior turn was something else, OR prior crank exited via the successful path), this is a **first press**.

No filesystem state required — the agent has full conversation history.


## Second-press behavior

Three changes from first-press:

1. **Lower the threshold for autonomous action.** If any Ready items exist, pick one and mint — even if the agent had hedged on which first time around. The user's re-press is an explicit "go anyway"; that authority overrides first-press hedging.

2. **Skip `/groom`** in the no-action branch. `/groom` already ran on the prior turn and hasn't earned a re-run; running it again with no new info would just churn the same items. If the lowered-threshold mint still produced no action, go straight to `/triage`.

3. **If still genuinely stuck** after the lowered threshold, surface to the user with one explicit line naming the blocker (e.g., `Cannot make progress without input on F14 Q1 (active-work invariant) or F10 Q1 (glance-step fix approach).`). Do NOT enter a third no-action loop — that would frustrate the user. Naming the specific blocking decision lets the user resolve it and re-invoke crank with the path forward open.


## Output format

After the loop + branch resolves, print one line to chat:

| Path | One-liner |
|---|---|
| Successful (≥1 mint, first or second press) | `/crank — minted N items: F<a>, F<b>, ... Loop exited cleanly; press again for the next sweep.` |
| No-action, first press | `/crank — no Ready work this turn. Ran /groom (extended runway: M items promoted) + /triage (K items waiting on you). Press again to take action.` |
| No-action, second press, picked something | `/crank — second press, picked F<n> and minted. Loop exited; press again for next.` |
| No-action, second press, still stuck | `/crank — second press, still stuck. Cannot make progress without input on F<n> Q<m>. Resolve to unblock.` |

The first-press no-action message is the marker for the second-press detector — it includes the literal phrase "no Ready work this turn" so the next-turn agent can identify it unambiguously.


## Runbook

### 1. Detect press (first vs second)

Read the prior assistant turn (conversation history). Look for the literal phrase `"no Ready work this turn"` or `"second press, still stuck"` in any of its content:

- **Found** → this is a second press; apply second-press behavior throughout.
- **Not found** → this is a first press.

### 2. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
- The Ready queue lives in `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md` § Ready (workflow-state H2) and items with `[Ready]` bracket in horizon H2s (per `[[backlog-horizons]]`). `/mint` knows how to find Ready items; crank just delegates.

### 3. Mint loop

```
minted_count = 0
minted_ids = []
while True:
    # First-press: pick the highest-priority Ready item.
    # Second-press: lower the threshold — pick any Ready item, even if hedged.
    next = pick a Ready item
    if next is None:
        break  # no more Ready
    result = invoke /mint <next>
    if result is "success":
        minted_count += 1
        minted_ids.append(next)
        continue
    if result is "blocked" or "failed":
        break  # natural stopping point
    if any other "I should stop here" signal:
        break
```

Crank is the orchestrator; `/mint` is the worker. Don't reimplement /mint logic here — invoke it.

### 4. Post-loop branch

If `minted_count >= 1`:
- Print: `/crank — minted N items: <list>. Loop exited cleanly; press again for the next sweep.`
- Exit.

Else (zero successful mints this turn):
- **First press**: invoke `/groom`, then `/triage`. Print the no-action summary including counts. Exit.
- **Second press**:
  - If the lowered-threshold loop in step 3 produced a mint, fall through to the success branch above.
  - Else, skip `/groom`, but still consider running `/triage` once more to refresh the inbox. Then print the still-stuck summary naming the specific blocker (look at the Triage file for the top pending item; reference its F-number + Q-number). Exit.

### 5. Print the one-liner

Use one of the four formats from § Output format above. The wording matters — the first-press no-action format is the marker that triggers second-press behavior next turn. Don't paraphrase.


## What `/crank` does NOT do

- Doesn't reimplement `/mint` — always delegates.
- Doesn't take destructive actions outside what `/mint` / `/groom` / `/triage` would take.
- Doesn't loop forever — at most two presses worth of attempts before naming the blocker.
- Doesn't ask the user mid-loop — questions surface via `/triage` after the loop, not inline.
- Doesn't run `/triage` after a successful crank — only on the no-action branch, to preserve the loop UX.


## Idempotence

Each `/crank` invocation is single-pass. Pressing crank twice in a row produces:
- First press: mint or fall back.
- Second press: lowered-threshold mint or stuck-with-named-blocker.
- Third press (if user keeps pressing past stuck): treated as a fresh first press; the second-press detector only fires when the immediately-prior turn was a no-action exit. Once the user has resolved the blocker (or ignored the stuck signal), the next crank starts the normal first-press cycle again.


## Cross-references

- **`/mint`** — the inner-loop worker; crank invokes it per Ready item.
- **`/groom`** — fallback when no minting happened; extends the runway by promoting backlog items.
- **`/triage`** — fallback when no minting happened; surfaces the inbox + status to the user.
- **`/fortify`** — skeptical counterpart to `crank`; invoke when normal cranking has stopped converging (same bug recurs, fixes don't stick).
- **`[[CAB Backlog]]`** — Ready definition; F-numbering; `[Ready]` bracket conventions.
- **`[[workflow]]`** — state graph; `[Ready]` → `[Active]` → `[Verify]` → `[Done]` transitions that `/mint` drives per item.
