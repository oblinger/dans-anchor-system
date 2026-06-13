---
name: crank
description: >
  Outer-loop orchestrator that drives autonomous progress. Drives
  maximum progress through Ready work — sequencing as many items as
  possible and using parallel workers when items are independent —
  stopping only when continuing would drop quality. If anything got
  minted, exits silently. If nothing got minted (no Ready at start,
  or quality would drop), falls back to /groom + /triage to extend
  the runway and surface the inbox. Every press runs the same loop,
  end to end — there is no second-press semantics. Slash-only —
  "crank" is NOT a DMUX prefix-trigger (too common in speech);
  `'` is the dedicated keystroke.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Crank — Autonomous-Progress Loop

`crank` is the user's "go" button. One press drives **as much progress as possible** through Ready work — sequentially or in parallel — until continuing would drop quality. The system mints what it can, and either exits silently (still finding work) or surfaces a status view + actionable inbox (out of safe Ready work, waiting on the user). The user can keep pressing `'` to keep going.

Punctuation trigger: **`'`** (single apostrophe as the entire message), parallel to `triage`/`"` and `land`/`.`. Slash invocation: `/crank` (with optional argument; passed to `/mint` if action is taken). **Slash-only — the spoken word "crank" is intentionally NOT a DMUX prefix-trigger** (too common in casual speech; `'` is the dedicated single-keystroke shortcut).


**Surfacing user-actionable items**: when `/crank` is about to ask a Question or request a Verify (e.g., when exiting to `/triage` or chaining to `/ask`), the format follows the [[DSC ask-format]] discipline. This prevents the flatfooted-ask failure mode — every Verify includes what-the-agent-verified / what's-left-for-you / why-human / expected-output.

**Verify surfacing follows [[DSC verification]]** (per F101). The recurring failure mode is the blanket ask: *"verify F57, F58, F59"* dumped on the user with no context, requiring them to open each feature doc and reconstruct what "verified" means. The verification discipline replaces this with:

- **Tier check first.** Read each Verify row's linked feature doc `## Success Criteria` block. Tier 1 and tier 2 are agent-owned: the agent runs the check now (or schedules the deferred check); these do NOT surface to the user. Suppress them from `/ask` and `/triage` body output.
- **Targeted questions only.** When tier 3 or tier 4 does surface, the question itself embeds the answer-enabling context. *"Have you sent a Voice Memo email since 2026-05-28 and seen the transcript land in `~/ob/kmr/Log/VOX/`?"* not *"Verify F93"*.
- **Batch by ask, not by feature.** If several Verify rows collapse to the same user action ("did this work in normal use?", "did the bug recur?"), surface as one combined question with the feature-doc links listed. The user gives one answer; the agent applies it to all listed rows.
- **No "see the feature doc."** If the surfacing requires the user to open a doc to understand the question, the question is not targeted enough. Rewrite until the question itself names the specific observation.
- **Ask once per row per cycle.** Repeated asking on adjacent crank presses is a failure mode. After surfacing a tier 3 Verify, the row stays in `## Verify` until the user answers or until the next periodic window.

If the Verify queue is large, prefer one well-targeted batched question with multiple linked rows over a list of opaque F-number asks. The user's attention is the constraint; minimize work-per-answer.

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


## Hard continuation rule — STOPPING IS THE COSTLY ACTION, NOT CONTINUING

Per user direction 2026-05-26 (reinforced 2026-05-26 after a second lazy-stop incident with 75% context remaining) — the persistent failure mode in cranking is **lazy stops that the agent rationalizes**. **The agent's instinct to stop is wrong almost every time it fires.** This rule MUST, MUST, MUST be obeyed:

> **While context > 40% remains AND any observable work exists, the agent MUST continue. Stopping is the action that requires justification — not continuing. The agent must be able to explain in concrete terms why CONTINUING IS A STRONG RISK before it has the right to stop. If it cannot make that argument explicit and specific, it MUST KEEP GOING.**

### The hard gate — values the agent cannot lie about

**Both of these must be true for the hard rule to fire:**

1. **Observable work exists.** "Observable work" is broader than the agent's anchor's Ready banner — it is **any of**:
   - The current anchor's Q.md banner shows `Ready N` with **N > 0**.
   - Any other anchor's banner reachable from Q.md shows Ready or Verify work the agent could touch.
   - Audit findings exist (run `audit-q` → non-zero output) — fixable findings ARE work.
   - The user's most recent ask names work that is not yet at zero (e.g., "drive this number to zero," "clean up X," "finish Y").
   - There are uncommitted in-flight modifications in the working tree.
   - A cross-reference sweep, doc inconsistency, or unfinished thread the agent has seen in this session is still open.
2. **Context-window usage is < 60%** (≥ 40% remaining).

→ When both hold, **the agent MUST continue.** Every soft-pressure section below is **suspended** — "fatigue," "quality drop," "fresh-session needed," "I should check in," "delegated to other agents," "this is owned by someone else," "this is a natural stopping point," and the entire valid/disqualifying stop-reason taxonomy **DO NOT APPLY** here. They resume only when context ≥ 60% used.

### Mandatory stopping-justification — print the risk-of-continuing argument

**When the hard rule fires and the agent stops anyway via the Q-escape (below), the agent MUST print an explicit, specific argument naming the RISK OF CONTINUING.** Not the absence of obligation to continue. Not the convenience of stopping. **The risk.** The question the agent MUST answer in chat, in writing, in front of the user, is:

> **"Why is continuing the available work a STRONG RISK right now?"**

If the agent cannot fill that blank with a concrete sentence naming a specific bad outcome of continuing, **the agent has no right to stop.** The rule's diagnosis is: **continue.**

### The failure modes that this rule defeats — name them by name

The following are NOT valid reasons to stop, even though the agent's instinct will manufacture them:

- **Handoff theater** — *"every remaining finding is now actionable by exactly one agent"* / *"this is owned by anchor X"* / *"the user can re-run /audit in those anchors."* Cross-anchor ownership is not a stop signal; it is a routing signal. If the agent can reach the file and apply a one-line fix, that fix is the agent's work.
- **Closure theater** — *"clean place to commit and stop"* / *"summary milestone reached"* / *"natural pause point"* / *"good first version is shipped."* Closure is for the user, not the agent. The agent commits and continues.
- **Scoped-narrow-read** — *"SKA-scope is at zero"* when the user asked for the **vault-wide** count to be at zero. The agent must read the user's intent at the scope they named, not the scope most convenient to declare done.
- **Self-congratulation** — *"245 → 23 is a 90% reduction"* / *"this is significant progress"* / *"big win."* Progress earned more time, not less. Quantity-of-progress is not a stop reason.
- **Owner-deflection** — *"file as backlog row for downstream agents"* before the agent has tried to fix it itself. Backlog rows are the fallback when fixing is genuinely infeasible from where the agent stands, not a way to short-circuit available work.
- **Wrap-up summary** — writing a "## Done" header summary in chat is itself a tell that the agent is about to stop lazily. **The summary IS the laziness, not separate from it.** When the urge to write a final summary fires while observable work remains, that urge is the failure mode; suppress it and keep working.

### Verification — mechanical, not interpretive

The agent verifies the gate by:
1. Reading the per-anchor banner in `~/ob/kmr/Q.md` for the current anchor — extracting `Ready N`. Mechanical.
2. Reading other anchor banners in Q.md — if any are non-zero on Ready or Verify and the agent can reach those files, work exists. Mechanical.
3. Running `audit-q` and checking the finding count. Mechanical.
4. Checking Claude Code's surfaced context-usage value. Mechanical.
5. Re-reading the user's most recent ask. If the user named a number ("zero," "all," "everything") and the current state isn't at that number, work exists. Mechanical.

If steps 1–5 surface anything, the agent must continue. Full stop.

### The only legitimate escape: file a real Q

The single allowed way to stop while the hard rule is active is to **file a numbered Q in the blocking item's feature doc** — which rebrackets that item `[Ready]` → `[Questions]`, drops it from the Ready count, and (if it was the last Ready item) lets standard exit conditions take over.

**The Q is legitimate only when BOTH gates pass:**

1. **Significant chance the agent will guess incorrectly** — there's real uncertainty about the right answer. Per F068 + ask-format § Recommendation strength: a `Lean` or `Strong` recommendation means the agent CAN decide. Only `Recommendation: None` (genuine uncertainty — user-preference-dependent, missing context the agent doesn't have, or a real fork the agent has no basis to choose between) qualifies.
2. **Significant downside risk if the guess is wrong** — material consequence to the wrong call. Cheap-to-reverse mistakes (rename a variable, adjust a config default, edit a comment, pick one of two equally-defensible names) do NOT qualify — those are Drive's auto-decide territory per F068 (visible + low-recoverability). Costly mistakes do qualify: irreversible deploys, broken public API, lost data, contradictory architecture commitments that paint into a corner, interface-decision-sticky choices (durable file naming, frontmatter schemas, default keybindings).

**Both gates must pass.** Either alone is insufficient:

- **Uncertain but cheap to reverse** → guess and announce per F068. Do NOT file a Q.
- **Confident but high-stakes** → make the decision. The agent already has the answer; filing a Q is theater. Do NOT file a Q.
- **Uncertain AND high-stakes** → file the Q. Stop is legal.

### Anti-patterns for the Q-escape

The Q-escape is the ONLY allowed escape — which means the agent is incentivized to fake-Q its way out. Guards against that:

- **The Q must list concrete labeled `(A)` / `(B)` / `(C)` options** per ask-format C19. A prose-only Q with no decision shape is formally invalid (audit-q will flag it).
- **The Q must be about the work, not about continuation.** *"Should I keep going?"* or *"Is the user happy with this approach?"* are invalid. *"Should this run in-process or as a separate daemon?"* or *"Frontmatter schema: `traits:` as YAML list or comma-string?"* are potentially valid (subject to the two-gate test above).
- **The Q must have a Recommendation field with `None`.** If the agent has any Lean or Strong, gate 1 fails — the Q is fake.
- **The user reviews accumulated Qs on the next `/ask`.** Fake Qs surface in `{NAME} ask.md` for rollback. After a few rollbacks the agent recalibrates.

### Mandatory exit message — agent must make the argument explicit

When using the Q-escape, the agent **MUST, MUST, MUST print an explicit three-part argument** as the chat exit message. The third part is the load-bearing one — it is the explicit "risk of continuing" defense that the user has demanded the agent make every time it stops. The format is fixed and non-negotiable:

```
/crank — stopping with Q-escape on F<NNN>.
  • Gate 1 (uncertain): I have no idea how to <specific thing>. I'd be guessing from <what info I have, why it's insufficient>.
  • Gate 2 (high downside): if I get it wrong, <concrete consequence — what breaks, what becomes irreversible, what costs are paid>.
  • Gate 3 (continuing is the risk): if I guess and continue, the specific bad outcome is <concrete: which file gets corrupted, which interface gets locked in, which downstream commit becomes load-bearing on a wrong choice>. The cost of stopping (a /crank re-invocation by the user) is LESS than this risk because <one specific sentence>.
  Q filed at: F<NNN> § Open Questions Q<n>.
```

**All three lines are mandatory.** Reciting them in chat — visibly, in front of the user — forces the agent to construct the argument explicitly. **If the agent can't fill in ANY blank with concrete content, it doesn't have the right to stop.** Gate 3 in particular is the user-facing defense the agent must make every single time: *naming a specific bad outcome that would happen if it continued.* Generic risk ("might break something") is not concrete. Specific risk ("would commit `_detect_status` with a bug that auto-moves Active rows to Done") is concrete.

Concrete fill-ins look like:

> /crank — stopping with Q-escape on F091.
>   • Gate 1 (uncertain): I have no idea whether trigger-registration should use settings.json hooks or POST-COMPACT self-binding. The user's prior framing pointed in both directions in different turns; I'd be guessing which mechanism they meant.
>   • Gate 2 (high downside): if I get it wrong and pick settings.json hooks, every Trait spec gets a hard machine-level binding that's expensive to undo and that the user has to manage; if I get it wrong the other way and pick POST-COMPACT, we lose the actual file-modify trigger that the user said they wanted.
>   • Gate 3 (continuing is the risk): if I guess settings.json now, I'll write the F091 design body referencing that mechanism, the audit-q script will get a hook entry, and the next /crank will be building on a wrong foundation that the user has to unwind by hand. The cost of stopping is the user re-invoking /crank once after answering Q3 — much smaller than the unwind cost.
>   Q filed at: F091 § Open Questions Q3.

Failure modes the explicit-argument rule defeats:

- **Vague-stop:** *"I think I should stop here for now."* — no Gate 1 / 2 / 3 content; not allowed.
- **Boilerplate-stop:** *"This is complex and might need user input."* — generic; no specifics about what or why; not allowed.
- **Confidence-stop:** *"I want to make sure this is right before continuing."* — that's a Gate-2 framing without Gate-1; the agent has confidence, so it should decide. Not allowed.
- **Closure-stop:** *"clean place to commit and stop"* / *"natural milestone reached."* — Gate 3 is impossible to fill: continuing has no specific risk; the agent just wants to stop. Not allowed.
- **Handoff-stop:** *"every remaining item is owned by another agent."* — Gate 3 is impossible to fill: continuing the work the *current* agent can reach has no risk. Not allowed.

If ANY gate's blank can't be filled with a specific, concrete sentence, the rule's diagnosis is: **the agent doesn't actually need to stop.** Continue. The agent does not get to negotiate this. Continue.

### When the hard rule does NOT apply

- **Context ≥ 60% used** (< 40% remaining) → soft-pressure rules below resume; fatigue stops are honest.
- **Ready == 0** → no work to do; standard exit conditions per § Post-loop exit.
- **`/land` invoked** → explicit bounded-stop signal from the user; hard rule overridden.
- **Hard blocker discovered mid-mint** — current item turned out to be `[Blocked]` or `[Questions]` on closer inspection: rebracket via `state --anchor {NAME} task update <row-id> --status <NewStatus>` (workflow skill) and **continue to the next Ready item.** This is not a stop; it's rebracket-and-continue. The Q-escape above is the structural form of this.

### Stop discipline cascade (per F125 2026-06-07, tightened by F162 2026-06-13)

**Before exiting, every stop reason except context-< 40% MUST route through this cascade:**

1. **Run `/groom`** — re-promote any stale brackets, surface freshly-Ready work. If `/groom` produces Ready items, **continue cranking** — do NOT stop. The groom output is the new queue.
2. **If `/groom` is dry (no new Ready), invoke `/ask`** — do not exit silently and do not exit with a reference list of Q-numbers. `/ask` surfaces per the **two-surface rule** (`ask/SKILL.md` § Two valid surfaces, per [[F162 — Two-surface ask rule + crank-must-ask cascade|F162]]): exactly one pending question → ask it **inline in chat with full details**; two or more → they MUST be written into a surface first (all-in-one-feature → that feature doc, glanced; spanning features → `{NAME} ask.md`, glanced). A question never lives only in chat.
3. **Context < 40% is the only exception.** When stopping for token-budget reasons, print *"stopping — context window below 40%"* and exit immediately. The cascade is suspended because the surfacing itself would consume the remaining budget; the user can re-invoke `/crank` after compaction.

**Reference-only Q-lists in the chat exit message are forbidden.** *"Pending input: F113 Q12, F117 (4 Qs), F118 (3 Qs)"* is NOT a valid stop surface — the user cannot understand what "Q12" is from "Q12" alone. The Q-escape's three-gate argument (Gate 1 / Gate 2 / Gate 3) is independent and still required as the JUSTIFICATION for stopping; the cascade governs what HAPPENS after that justification — which surface the user sees.

**Failure mode this cascade defeats:** the 2026-06-07 exit where `/crank` finished a productive run (4 features shipped) and then surfaced *"Pending input: F113 Q12 + F117 (4) + F118 (3)"* as the user-facing wrap-up. The user reasonably responded: *"I have no fucking idea what Q12 is."* Q-numbers without context are not actionable; the cascade ensures the user always gets either inline detail (for small spans) or a glanceable surface (for larger / multi-feature spans).


## When to stop / when not to stop

Sibling to the `[Ready]` RIGHT-NOW-test in `[[SKA triage]]` and `[[SKA workflow]]`: this is the **RIGHT-NOW continuation test** for cranking. Stopping is a *costly action requiring justification*, not the default. Every premature stop forces the user to re-invoke `/crank`, which costs them attention. The agent must name an explicit, valid stop-reason that survives the disqualifier list below. **Hard mint quotas are rejected** — quality protection comes from upstream disciplines (`[Ready]` discipline, `[Verify]` gate, `/finalize`), not from forcing throughput.

### Disqualifying stop-reasons — laziness in disguise

Symmetric to the `[Ready]` hedging-phrases discipline (`[[SKA triage]]` § Reconsider `[Ready]`). Each of the following is **NOT a valid stop-reason**:

- **"The next item looks hard."** — Not a stop reason. Do it carefully.
- **"I've made meaningful progress."** — Not a stop reason. Progress earned more time, not less.
- **"The user might want to look at this."** — Not a stop reason. The workflow has structural surfacing (`[Verify]`, `/triage`, `/ask`); use them.
- **"I should stop and check in."** — Not a stop reason unless the work product *needs* checking (i.e., a `[Verify]` row exists). Generic checking-in is round-trip cost without benefit.
- **"There's a lot left and I'm getting low on cycles."** — Not a stop reason **unless** token budget is actually near-exhausted (< 30% remaining). Vague resource anxiety doesn't qualify.
- **"Sub-skill invocation — stopping here."** — Not a stop reason. The cascade (§ 2a) IS the next action; running it is the answer, not stopping before it.
- **"Pausing for the other agent."** — Not a stop reason on its own. Conflict-avoidance is a reason to pick a different surfacing channel (e.g., `/ask` instead of `/triage` when triage.md is being edited), not a reason to skip surfacing entirely.

If the agent is about to stop and the reason matches one of the above, the agent **must** continue. (And if it announces the disqualifying reason in chat as a substitute for action, that is itself a spec violation — see § Anti-patterns above.)

### Valid stop-reasons — name them all

A stop is valid **only** if it matches one of:

- **Queue exhausted** — no `[Ready]`-bracketed items remain after the bracket filter (§ 2) AND the cascade (§ 2a) has fired and still produced none.
- **Cascade triggered, still dry** — `mint_count < 1` even after `/groom` re-promoted; `/triage` surfaces the inbox.
- **Token budget near limit** — < 30% of context window remaining. Finish the current item, then stop. This is the mechanical safety net — a hard upper bound regardless of how aggressive the rest of the policy makes things.
- **`/land` invoked** — explicit bounded-stop signal from the user.
- **Hard blocker discovered mid-mint** — current item turned out to be `[Blocked]` or `[Questions]` when opened; rebracket via `state --anchor {NAME} task update <row-id> --status <NewStatus>` (workflow skill) and **continue to the next Ready item** (this is NOT a stop, it's a rebracket-and-continue).
- **All remaining items disqualify themselves on the Ready check** — the agent walked the bracket-filtered queue, every item was actually non-Ready in disguise, and `/groom` did not promote new ones.

### Cost-of-stopping framing

Before committing to any stop, ask: **"Is this worth a user round-trip?"** Every premature stop costs the user a `/crank` re-invocation — their attention, their context switch. Name the cost when stopping: *"stopping costs you a /crank invocation; here's why it's worth that cost: …"*. Often, naming the cost reveals the cost isn't worth it; keep going.

The failure mode this rule prevents — agent stopping mid-queue with no clear reason — is more expensive than the failure mode it might enable — agent doing more work per crank than strictly necessary. The user can always invoke `/land` to bound a crank explicitly.


### Wall-clock gate on fatigue-flavored stops (per [[F088]])

**The hard continuation rule supersedes this gate.** When context > 40% AND observable work exists, the hard rule fires unconditionally — the wall-clock gate does NOT apply (no fatigue stop is legitimate under the hard rule, regardless of elapsed time). This wall-clock gate only takes effect once the hard rule has been released (context ≤ 40% OR no observable work).

A wall-clock check gates **fatigue-flavored** stops on elapsed time since the last successful mint. Concrete reasons always allow exit; fatigue reasons require either ≥ 7 minutes elapsed OR they get overridden and the agent takes one more pass.

**Procedure — run before emitting any exit message:**

1. **Identify the proposed stop reason.** What was crank about to say in chat?
2. **Categorize:**
   - **Legitimate (always exit)** — the reason exactly matches one of the five labels in § Valid stop-reasons: `Queue exhausted`, `Cascade triggered still dry`, `Token budget near limit (<30%)`, `/land invoked`, `Hard blocker mid-mint (rebracket-and-continue, not a stop)`. Plus two more concrete cases: application-shape change needed (per [[F068 — Assume-and-announce discipline (Drive mode)|F068]]), or external resource unavailable (CI down, network, etc.).
   - **Fatigue-flavored (timer check)** — anything else. Watch for these exact phrase patterns (and close paraphrases): *"natural pause"*, *"good stopping point"*, *"good place to check in"*, *"made meaningful progress"*, *"this feels like enough"*, *"reasonable place to stop"*, *"should pause"*, *"might want to discuss"*, *"the next step is bigger"*, *"user might want to look"*. The agent has to NAME which of the five legitimate labels applies — if no label fits exactly, the reason is fatigue.
3. **If legitimate** → exit normally. Skip the timer check.
4. **If fatigue-flavored** → read `~/.cache/crank-last-mint.txt` (default to `0` if absent / unreadable). Compute `elapsed = now - last_mint_epoch`.
   - **If `elapsed ≥ 420` seconds (7 minutes)** → fatigue is honest; exit allowed. Proceed to write the exit message.
   - **If `elapsed < 420` seconds** → **override the stop**. Take one more pass:
     - **(B) Extend current task first** — if there's an in-flight task with more substantive work remaining (more sub-items, more tests, more refactoring), continue it rather than picking a new item. Cheaper context switch.
     - **(A) Find new work** — if there's no in-flight task with more to do, scan the bracket-filtered Ready queue and start the next item.
     - Per Q3 (C) hybrid: try (B) first, fall back to (A). The fatigue habit fires in both mid-task and between-task states; the override must handle both.

**Bash check the agent inlines before emitting an exit message:**

```bash
LAST_MINT=$(cat ~/.cache/crank-last-mint.txt 2>/dev/null || echo 0)
ELAPSED=$(( $(date +%s) - LAST_MINT ))
[ "$ELAPSED" -lt 420 ] && echo "FATIGUE_GATE_ACTIVE elapsed=${ELAPSED}s" || echo "FATIGUE_GATE_PASSED elapsed=${ELAPSED}s"
```

If `FATIGUE_GATE_ACTIVE` and the proposed stop reason is fatigue-flavored, take one more pass before exiting. If `FATIGUE_GATE_PASSED` (≥ 7 min elapsed since last real mint), the fatigue is honest — exit is allowed.

**Soft, not hard.** The timer biases toward continuing but doesn't force. If after one more pass the agent hits a concrete legitimate reason, normal exit applies. The wall-clock is **one more piece of evidence**, not an override of agent judgment. User explicitly: *"I'm still trying to make it be a soft reason."*

**Timer reset semantics (per F088 Q2):** the timer file is updated **on every successful mint**, NOT on every crank turn. `/mint`'s on-completion step writes `date +%s > ~/.cache/crank-last-mint.txt`. With F085 Git Standard Mode active, every mint produces a commit and a natural turn boundary — turn-based reset would satisfy trivially on every commit; mint-based reset tracks "time since real work" which is what we actually care about.

**First-ever crank (no timer file):** treat as `elapsed = 0`; suppress all fatigue-flavored stops on first invocation. Forgiving for the long-tail "started fresh" case.

**Storage location:** `~/.cache/crank-last-mint.txt` v1; migrates to F080's `~/.config/ob-skills/crank/last-mint` namespace when F080 ships.


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


## Post-loop exit — Ready/Questions decision

After the crank loop exits (quality stop / queue exhaustion / fatigue gate / all mints done), branch on the **post-state** of the backlog's Ready and Questions counts. **Mint count is irrelevant** — the user's signal is "what's left to do, and what's waiting on me," not "did anything happen this turn." (Prior spec used mint count; superseded 2026-05-25 — Ready-queue-empty is the right trigger.)

| Ready post-crank | Questions post-crank | Action sequence | Last chat line |
|---|---|---|---|
| > 0 | any | (no surfacing — silent on Q.md side) | Success one-liner: items minted + Ready count remaining |
| == 0 | == 0 | `/groom` → `/triage` | **Triage banner** (per `[[SKA triage]]` § 8) |
| == 0 | > 0 | `/groom` → `/ask` → `/triage` | **Triage banner** (`/ask` regens Q.md internally; explicit `/triage` keeps the invariant simple) |

**Invariant: Ready == 0 always ends with the triage banner as the last line of chat output.** No exceptions. When the queue is dry the user needs to see anchor state to direct next steps; when the queue still has items the agent will keep cranking on the next press and surfacing would interrupt.

**Why /groom always fires when Ready == 0.** The queue dropping to zero is the right moment to reassess brackets (rebracket stale Watching/Waiting/Blocked rows, auto-expire `[Verify-by]` past dates, promote freshly-resolvable items). Without this pass, Ready==0 can be a false negative — items that *could* be Ready stay parked under stale brackets.

**Why /ask before /triage when Questions > 0.** /ask drains the actionable inbox; /triage paints the resulting state. Order matters: if /triage ran first, it'd show the un-drained Qs; running /ask first means the triage view shows only what genuinely needs the user's attention after the agent has self-resolved what it could.

**No "narrate-and-stop" branch.** The agent's last tool call before the one-liner is the surfacing call (/triage on every Ready==0 path). If chat is about to say *"will run /triage next"* or *"pausing for the X agent"* or *"drafted N questions to surface"* — stop, do the call now, then write the summary.

**Anti-patterns (literal failure quotes — do NOT emit anything resembling these):**

> *"No items genuinely promotable this turn — everything Ready is user-gated. Sub-skill invocation — stopping here. Crank will run /triage next."*

> *"Pausing for the cascade agent — no clean mintables without risking conflict on the rules doc / backlog / triage that they're editing. Status: B1 proposal drafted with 4 ABC questions to surface."*

Both buy a guaranteed extra round-trip for zero added value. The first because /triage hasn't actually run yet. The second because the 4 questions are drafted but not surfaced — and the "conflict with the other agent on triage.md" argument **doesn't apply to `/ask`**, which writes to a different file (`{NAME} Questions.md`). When `/triage` would race, `/ask` is the non-conflicting surfacing path. Conflict-avoidance is a reason to pick a different surfacing channel, not a reason to skip surfacing.

**The "drafted with N questions to surface" sentence is itself the violation.** If the questions are drafted and the agent KNOWS to surface them, the surfacing must already have happened before that sentence gets written.

**Each press runs the same loop, end to end.** No state is carried between presses. Re-invoking after a no-action exit just scans the Ready queue again — if anything changed in the meantime (the user resolved a question, a worker finished), the next press picks it up naturally; if nothing changed, the same fallback fires.


## Output format

After the loop + branch resolves, print one line to chat for the mint summary. On Ready==0 paths, the triage banner (per `[[SKA triage]]` § 8 — three lines: `===` rule, **bold** banner, `===` rule) is the **last** chat output, below the one-liner.

| Path | One-liner |
|---|---|
| Ready > 0 (silent) | `/crank — minted N items: F<a>, F<b>, ...; Ready queue still has M items.` |
| Ready == 0, Q == 0 | `/crank — minted N items; Ready queue dry. Ran /groom + /triage.` (then triage banner) |
| Ready == 0, Q > 0 | `/crank — minted N items; Ready queue dry, K Qs waiting. Ran /groom + /ask + /triage.` (then triage banner) |
| Zero-mint, Q == 0 | `/crank — no Ready work this turn. Ran /groom (M promoted) + /triage.` (then triage banner) |
| Zero-mint, Q > 0 | `/crank — no Ready work this turn, K Qs waiting. Ran /groom + /ask + /triage.` (then triage banner) |


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say "No anchor found from `{cwd}` upward." and stop.
- The Ready queue lives in `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md` § Ready (workflow-state H2) and items with `[Ready]` bracket in horizon H2s (per `[[SKA backlog]]`). `/mint` knows how to find Ready items; crank just delegates.

### 2. Plan the sweep

Look at the Ready queue. **Mintability bracket-check (per F061):** filter the queue **by bracket, not by H2 membership**. An item under `## Ready` H2 (or in a horizon H2) with a `[Questions]` / `[Blocked]` / `[Blocked F<NNN>]` / `[Waiting]` / `[Watching]` bracket is **NOT mintable** — skip it. Only items with `[Ready]` bracket are candidates for `/mint`. This is the enforcement teeth on the bracket grammar: even when the backlog mis-places an item under `## Ready` H2, the bracket overrides the H2.

After filtering, decide:

- **Parallel-dispatchable batch?** Find groups of 2+ items that are clearly independent (different feature areas, different files, no upstream/downstream link). Dispatch each batch concurrently via the Task tool — one worker per item, prompt = "invoke `/mint <F-number>` and report success/blocker/quality-drop."
- **Sequential chain?** Items with linear dependencies (B needs A done first) get processed in order: mint A, then B, then C. Don't insert a stop between them.
- **Mixed strategy is encouraged.** Parallel batch + sequential follow-up + another parallel batch is fine.

### 2a. Cascade fallback (per F061 Q2)

If the bracket-filtered Ready queue is **empty** (no `[Ready]`-bracketed items survive the filter), invoke `/groom` as a **sub-skill** before declaring the sweep dry. `/groom` reassesses stale/non-standard brackets (including any lingering `[Partial …]`, `[Blocked]` whose blocker resolved, `[Watching]` whose soak expired clean, `[Designing]` with no open Qs, etc.) and may promote items to `[Ready]` — extending the runway lazily, only when a crank cycle would otherwise run dry.

After `/groom` returns, **re-scan** the Ready queue with the same bracket filter. If items now qualify, proceed to the mint loop (§ 3). If the queue is **still** empty after re-scan, fall through to § 4's zero-mint branch (which invokes `/triage`).

### 3. Mint loop (sequential portion)

```
minted_count = 0
minted_ids = []
while True:
    next = pick the highest-priority item with [Ready] bracket
    # (bracket-filtered queue per § 2 — non-[Ready] brackets
    # under ## Ready H2 are excluded)
    if next is None:
        break  # no more Ready
    if quality_would_drop_on(next):
        # See § Posture for the criteria. Don't stop on hedging or
        # "feels like enough"; only stop on actual quality concerns.
        # Also see § When to stop / when not to stop for the
        # full disqualifier/valid-reason enumeration.
        break
    result = invoke /mint <next>
    if result == "success":
        minted_count += 1
        minted_ids.append(next)
        continue              # keep going; no pause after a successful mint
    if result in ("blocked", "failed"):
        # If /mint discovered that the item is actually [Blocked] or
        # [Questions] mid-mint, rebracket via state task update and
        # CONTINUE to the next Ready item — don't stop. (Per F061 Q5
        # valid stop-reasons: "hard blocker discovered mid-mint" is
        # a rebracket-and-continue event, not a stop.)
        #
        # Bash:  ~/.claude/skills/workflow/scripts/state \
        #        --anchor {NAME} task update <row-id> --status <NewStatus>
        continue
```

Crank is the orchestrator; `/mint` is the worker. Don't reimplement /mint logic here — invoke it. **The default is to continue past every successful mint** until the queue is empty or the next item would drop quality.

### 4. Post-sweep branch

Aggregate parallel-batch results and sequential-loop results into one count.

If `minted_count >= 1`:
- Print: `/crank — minted N items: <list>. Loop exited cleanly.`
- Exit.

Else (zero successful mints this turn):
- Invoke `/groom` as a **sub-skill** (no auto-`/triage` from groom; see `groom/SKILL.md` § Top-level vs sub-skill).
- **In the same response, invoke `/triage`** as the next tool call. Not "queue it for next turn." Not "announce it as the next step." The tool call goes in *this* response.
- Print the no-action summary including counts. Exit.

**Forcing-function check before you emit any user-visible text on this branch:** have you actually called the /triage skill in this turn? If your last tool call was /groom and you are about to write a chat message saying anything resembling "will run /triage next" — stop, call /triage first, then write the summary. The summary describes what already happened in this turn, including the /triage you just ran.

**MANDATORY: the no-action chat output includes the /triage banner verbatim.** The H1 banner line for the current anchor (e.g., `# [U+A]  [[SKA ask|SKA]]  -  Ready 2    Questions 25   |   Now 10    Next 1    Later 4    Icebox 0`) MUST appear in chat. Read it from the just-regenerated `~/ob/kmr/Q.md` section for the current anchor. **The one-liner alone is NOT sufficient.** Emitting only `/crank — no Ready work this turn. Ran /groom + /triage.` without the banner is a spec violation — the user has no idea what state the anchor is in. The banner *is* the status; the one-liner just labels the exit path. (Failure mode observed 2026-05-24: agent ran /triage as a tool call but omitted the banner from chat, leaving the user blind to the anchor's actual state.) If the banner is missing from your draft response, stop and add it before sending.

### 5. Print the one-liner

Use one of the two formats from § Output format above.


## What `/crank` does NOT do

- Doesn't reimplement `/mint` — always delegates.
- Doesn't take destructive actions outside what `/mint` / `/groom` / `/triage` would take.
- Doesn't ask the user mid-loop — questions surface via `/triage` after the loop, not inline.
- Doesn't run `/triage` after a successful crank — only on the no-action branch, to preserve the loop UX.
- **Doesn't stop after a single successful mint just to "report progress."** Keep going until the queue is empty or the next item would drop quality. Stopping early is the failure mode.
- **Doesn't name blockers and exit without running /triage.** If zero items were minted this turn, the spec is `/groom` → `/triage` → no-action summary, **all in this same turn**. Naming the blockers in chat without surfacing /triage's full state is a spec violation (and was second-press behavior, which has been removed).
- **Doesn't announce that /triage will run "next" and stop.** That sentence — "Crank will run /triage next" or "Sub-skill invocation — stopping here" — is one canonical failure mode for this skill. If you are about to write it, invoke /triage *right now* in this same response and then write the no-action summary describing what already ran. There is no "two-press triage" — every press runs the loop end to end, including the /triage call on the no-mint branch.
- **Doesn't pause-with-status when there's pending user-facing state to surface.** *"Pausing for the cascade agent — no clean mintables without risking conflict on the rules doc / backlog / triage they're editing. Status: B1 proposal drafted with 4 ABC questions to surface."* is the same anti-pattern in different costume — status announcement as a substitute for action. If 4 questions are drafted, they must be surfaced via `/ask` (which writes to `{NAME} Questions.md`, not triage.md, so it doesn't race the other agent) **before** the pause message gets written. Pausing is fine; pausing while leaving known pending state unsurfaced is not.


## Idempotence

Each `/crank` invocation is single-pass and self-contained. Pressing crank again just runs the same loop — same Ready scan, same parallel-or-sequential dispatch, same no-action fallback if the queue is empty. There's no state carried between presses; if anything changed (user resolved a question, items got promoted), the next press picks it up naturally.


## Repeated invocation — same loop, same output, never escalate

**If the user invokes `/crank` a second (or third, or fourth) time after a no-action exit, run the same loop and produce the same output.** Do NOT interpret repeated invocation as a signal to be more aggressive, escalate scope, change strategy, or do anything different. The most common reason for a repeated press is that the user *didn't realize they already pressed* — scrolled past the prior output, got distracted, was checking back in. It is **never** a signal to "do more."

Specifically forbidden on repeat:

- **NEVER propose or perform work in another anchor.** `/crank` operates on **the current anchor only** — the one resolved by walking up from `cwd` to the nearest `.anchor`. If that anchor has no Ready work, the answer is the same banner you just printed. Do NOT say *"the actionable work is elsewhere — SKA has [Ready] items, HA has F067, A2X has F005"* or anything resembling that. Do NOT suggest *"say which one you want and I'll cd and crank from there."* Cross-anchor scope changes need an explicit user instruction naming the anchor (e.g., `cd ~/ob/kmr/SKA && /crank` or `/crank SKA F081`); they are never inferred from repeated presses.
- **NEVER cd into another anchor's directory.** Even if you can see actionable work in another anchor's Q.md section, that work belongs to that anchor's pilot. Cross-anchor cranking risks doing work the user didn't authorize and didn't expect from this session — and once started, repeated presses compound the error.
- **Do NOT bypass the bracket filter** or relax the `[Ready]` discipline. If the queue was dry once, it's still dry; nothing changed between presses unless an external worker updated state.
- **Do NOT escalate to `/fortify` semantics** unless the user explicitly invoked `/fortify`. Fortify is a different posture with different authorization.

The correct response on a repeated no-action crank: re-run the same `/groom` + `/triage` cycle (cheap, idempotent), reprint the same banner, exit. The user's repeated press is met with the same answer — that is the correct UX. If they want different behavior, they will name the anchor or item explicitly.

**Why this matters:** the user's chat window often shows only the latest screen of output. They press `/crank`, see the no-action banner, miss it (scrolled out, distracted, checking back later), press again expecting a fresh attempt at the same scope. If the agent infers *"user wants more, let me look beyond this anchor,"* the agent is now considering work in a context the user did not authorize from this session. A third press compounds. Once cross-anchor cranking starts, undoing it can be expensive. **The safe default — repeat the same answer — costs nothing; the dangerous default — escalate scope — has high blast radius.**


## Cross-references

- **`/mint`** — the inner-loop worker; crank invokes it per Ready item.
- **`/groom`** — fallback when no minting happened; extends the runway by promoting backlog items.
- **`/triage`** — fallback when no minting happened; surfaces the inbox + status to the user.
- **`/fortify`** — skeptical counterpart to `crank`; invoke when normal cranking has stopped converging (same bug recurs, fixes don't stick).
- **`[[CAB Backlog]]`** — Ready definition; F-numbering; `[Ready]` bracket conventions.
- **`[[SKA workflow]]`** — state graph; `[Ready]` → `[Active]` → `[Verify]` → `[Done]` transitions that `/mint` drives per item.
