---
name: crank
description: >
  Outer-loop orchestrator that drives autonomous progress. Drives
  maximum progress through Ready work — sequencing as many items as
  possible and using parallel workers when items are independent —
  stopping only when continuing would drop quality. If anything got
  minted, exits silently so the user can re-press `'` to continue the
  loop. If nothing got minted (no Ready at start, or quality would
  drop), falls back to /groom + /triage to extend the runway and
  surface the inbox. Each press runs the same loop, end to end.
  Slash-only — "crank" is NOT a DMUX prefix-trigger
  (too common in speech); `'` is the dedicated keystroke.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Crank — Autonomous-Progress Loop

`crank` is the user's "go" button. One press drives **as much progress as possible** through Ready work — sequentially or in parallel — until continuing would drop quality. The system mints what it can, and either exits silently (still finding work) or surfaces a status view + actionable inbox (out of safe Ready work, waiting on the user). The user can keep pressing `'` to keep going.

Punctuation trigger: **`'`** (single apostrophe as the entire message), parallel to `triage`/`"` and `land`/`.`. Slash invocation: `/crank` (with optional argument; passed to `/mint` if action is taken). **Slash-only — the spoken word "crank" is intentionally NOT a DMUX prefix-trigger** (too common in casual speech; `'` is the dedicated single-keystroke shortcut).


## When to Use

- User types `/crank` or sends `'` as the entire message.
- User says "keep going", "make progress", "do the next thing", "what's next?".
- After resolving a question or unblocking a feature, when the user wants the system to take it from here.


## Posture — maximum progress, quality is the only stop

Crank is **not** a "make a small amount of progress and stop" command. The default posture is the **opposite**:

- **Sequence as many Ready items as you can** in a single press. Don't stop after one mint just because something got done — go to the next Ready item and the next.
- **Parallelize when items are independent.** If two or more Ready items are clearly orthogonal (different files, no shared state, no dependency edge), dispatch them as parallel workers (Task tool, `general-purpose` subagent_type) and reap the results. Single-press throughput beats single-item linearity.
- **Sequential continuation when items aren't independent.** If a chain of Ready items must run in order (B depends on A), still go through the chain — A, then B — without an interrupt between them.
- **The only stopping criterion is quality drop.** Continue until *the next mint* would meaningfully degrade quality. Quality drop signals (any one is sufficient):
  - Spec is genuinely ambiguous and `/mint` would have to guess at intent.
  - Required user input not yet given (item is `[Questions]`, not `[Ready]`).
  - Agent context is fatigued — recall is degrading, the agent is repeating itself, or the next step requires re-reading what was just dropped.
  - Dependency on something that hasn't actually been verified yet (the previous mint claimed Done but Verify hasn't happened).
  - Item is genuinely complex enough that proper attention requires a fresh session — better to surface and let the user decide than to crank a degraded version.

**Lazy is the failure mode**, not a virtue. If the agent is hedging on item N+1 because "I already did N, that's progress" — that's not how crank works. Keep going until quality demands a stop.


## Mechanism — outer loop over `/mint`, with parallelism

`crank` is an **orchestrator**, not a worker. Each unit of work delegates to `/mint`, which handles a single Ready item end-to-end (spec → code → test → review → verify → commit).

The orchestrator has two patterns it can use, and should pick the most aggressive one safely available:

**Parallel dispatch (preferred when applicable).** Scan the Ready queue. If 2+ items are clearly independent (orthogonal files, no shared module being touched, no upstream/downstream dependency between them), dispatch them as parallel workers via the Task tool (`subagent_type: general-purpose`, prompt instructs the worker to invoke `/mint <F-number>`). Wait for all to return; aggregate successes/failures.

**Sequential loop.** When items aren't safely parallelizable (or it's a single item), iterate:

```
while True:
    next = pick the highest-priority safely-mintable Ready item
    if next is None:                     # nothing Ready left
        break to fallback
    result = /mint next
    if result == "success":
        continue                         # keep going; don't pause here
    if result == "blocked" or "failed":
        break to fallback
    if quality_would_drop_on_next(next): # see § Posture
        break to fallback
```

**Mixed strategy is fine.** Dispatch a parallel batch, then continue with sequential items afterward, then dispatch another parallel batch. The point is: don't stop early.

One press of `crank` = the full sweep, not a single mint. **Do not stop after the first successful mint** unless continuing would drop quality.


## Post-loop branch — did anything get minted?

| Outcome | Path |
|---|---|
| **≥1 successful `/mint`** | Exit silently. Print the one-line success summary. User keeps pressing `'` to continue the loop; no `/groom` or `/triage` interrupt between mint cycles. |
| **Zero successful `/mint`** | No-action branch: run `/groom`, then `/triage`, then exit. Print the one-line no-action summary. User re-invokes `crank` if they want another sweep over freshly-readied items. |

Both `/groom` and `/triage` are **no-action fallbacks** — they fire only when crank produced zero mints this turn. Successful cranks stay quiet to preserve the loop UX (the user keeps pressing crank; the system keeps minting; only when it fatigues does the system surface a full status view).

**MANDATORY on the zero-mint path:** if `minted_count == 0` (counting *this* invocation, not prior turns), the agent **MUST** invoke `/groom` and then `/triage` and print the no-action summary. There is no "name the blockers and exit" shortcut — that was second-press logic and was removed. If `/mint` couldn't run because every Ready item needs user input, that's still zero mints → /groom + /triage. Naming blockers without running /triage is a spec violation. The /triage output IS how the user learns what's blocked; bypassing it leaves them guessing.

**Each press runs the same loop, end to end.** No state is carried between presses. Re-invoking after a no-action exit just scans the Ready queue again — if anything changed in the meantime (the user resolved a question, a worker finished), the next press picks it up naturally; if nothing changed, the same fallback fires.


## Output format

After the loop + branch resolves, print one line to chat:

| Path | One-liner |
|---|---|
| Successful (≥1 mint) | `/crank — minted N items: F<a>, F<b>, ... Loop exited cleanly; press again for the next sweep.` |
| No-action | `/crank — no Ready work this turn. Ran /groom (extended runway: M items promoted) + /triage (K items waiting on you). Press again to take action.` |


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
- The Ready queue lives in `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md` § Ready (workflow-state H2) and items with `[Ready]` bracket in horizon H2s (per `[[backlog-horizons]]`). `/mint` knows how to find Ready items; crank just delegates.

### 2. Plan the sweep

Look at the Ready queue (items under `## Ready` in the backlog plus items with `[Ready]` bracket in horizon H2s). Decide:

- **Parallel-dispatchable batch?** Find groups of 2+ items that are clearly independent (different feature areas, different files, no upstream/downstream link). Dispatch each batch concurrently via the Task tool — one worker per item, prompt = "invoke `/mint <F-number>` and report success/blocker/quality-drop."
- **Sequential chain?** Items with linear dependencies (B needs A done first) get processed in order: mint A, then B, then C. Don't insert a stop between them.
- **Mixed strategy is encouraged.** Parallel batch + sequential follow-up + another parallel batch is fine.

### 3. Mint loop (sequential portion)

```
minted_count = 0
minted_ids = []
while True:
    next = pick the highest-priority safely-mintable Ready item
    if next is None:
        break  # no more Ready
    if quality_would_drop_on(next):
        # See § Posture for the criteria. Don't stop on hedging or
        # "feels like enough"; only stop on actual quality concerns.
        break
    result = invoke /mint <next>
    if result == "success":
        minted_count += 1
        minted_ids.append(next)
        continue              # keep going; no pause after a successful mint
    if result in ("blocked", "failed"):
        break                 # natural stopping point
```

Crank is the orchestrator; `/mint` is the worker. Don't reimplement /mint logic here — invoke it. **The default is to continue past every successful mint** until the queue is empty or the next item would drop quality.

### 4. Post-sweep branch

Aggregate parallel-batch results and sequential-loop results into one count.

If `minted_count >= 1`:
- Print: `/crank — minted N items: <list>. Loop exited cleanly; press again for the next sweep.`
- Exit.

Else (zero successful mints this turn):
- Invoke `/groom` as a **sub-skill** (no auto-`/triage` from groom; see `groom/SKILL.md` § Top-level vs sub-skill).
- Then explicitly invoke `/triage`.
- Print the no-action summary including counts. Exit.

### 5. Print the one-liner

Use one of the two formats from § Output format above.


## What `/crank` does NOT do

- Doesn't reimplement `/mint` — always delegates.
- Doesn't take destructive actions outside what `/mint` / `/groom` / `/triage` would take.
- Doesn't ask the user mid-loop — questions surface via `/triage` after the loop, not inline.
- Doesn't run `/triage` after a successful crank — only on the no-action branch, to preserve the loop UX.
- **Doesn't stop after a single successful mint just to "report progress."** Keep going until the queue is empty or the next item would drop quality. Stopping early is the failure mode.
- **Doesn't name blockers and exit without running /triage.** If zero items were minted this turn, the spec is `/groom` → `/triage` → no-action summary. Naming the blockers in chat without surfacing /triage's full state is a spec violation (and was second-press behavior, which has been removed).


## Idempotence

Each `/crank` invocation is single-pass and self-contained. Pressing crank again just runs the same loop — same Ready scan, same parallel-or-sequential dispatch, same no-action fallback if the queue is empty. There's no state carried between presses; if anything changed (user resolved a question, items got promoted), the next press picks it up naturally.


## Cross-references

- **`/mint`** — the inner-loop worker; crank invokes it per Ready item.
- **`/groom`** — fallback when no minting happened; extends the runway by promoting backlog items.
- **`/triage`** — fallback when no minting happened; surfaces the inbox + status to the user.
- **`/fortify`** — skeptical counterpart to `crank`; invoke when normal cranking has stopped converging (same bug recurs, fixes don't stick).
- **`[[CAB Backlog]]`** — Ready definition; F-numbering; `[Ready]` bracket conventions.
- **`[[workflow]]`** — state graph; `[Ready]` → `[Active]` → `[Verify]` → `[Done]` transitions that `/mint` drives per item.
