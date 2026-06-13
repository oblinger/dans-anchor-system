---
name: verification
description: Discipline. Four-tier hierarchy for how a feature gets verified, with a blocking-action escape hatch. Cited at feature creation (write Success Criteria sized to the highest applicable tier) and at verification time (do not escalate to tier 4 if a lower tier would work). Owns the structural rule that the verification mechanism is declared up front, not chosen on the fly.
user_invocable: false
---

# Verification Discipline

The four-tier preference ordering (agent-immediate → user-explicit) for how a feature gets verified, declared up front in each feature doc and consulted at verification time so user attention is spent only when no lower tier works.

Verification is *the four-tier preference ordering an agent uses to choose how a feature gets verified — from agent-immediate (best) to user-explicit (last resort).* The single load-bearing rule: pick the highest applicable tier; never escalate to a higher one when a lower one would work. What distinguishes a tier from a feeling:

- **Tier 1 — agent-immediate** — agent runs a check in the same turn the work completes. Runnable command, deterministic observation.
- **Tier 2 — agent-over-time** — agent owns the deferred check (soak test, recurrence watchdog, scheduled re-run). User not involved.
- **Tier 3 — user-passive** — user notices in normal use; signal is obvious if it breaks. Agent may ask once after a week.
- **Tier 4 — user-explicit** — user performs a specific concrete test action they would not otherwise do. Least preferred.
- **Blocking-action escape hatch** — if a concrete next action is strictly gated on verification (filled `Blocks next:` line), tier 1 or 2 is required.
- **Declared up front** — the tier is named in the feature doc's `## Success Criteria` H2 at creation time, not chosen on the fly at verification time.

This is a discipline, not a user-invocable skill — `/feature` cites it at creation time; `/triage`, `/crank`, and `/groom` cite it at verification time.

## Why this exists

The recurring failure mode: a feature is filed, work is done, and the agent surfaces a Verify to the user out of habit. The user is asked to test something. Often the user is asked something that the agent could have checked itself, or that would have surfaced naturally during the user's normal workflow over a few days. The user's attention is the constraint; spending it on unnecessary Verifies is the waste this discipline prevents.

This discipline is the structural answer. Every feature declares its verification tier at creation time, sized as high as the work allows. The agent at verification time consults the tier and refuses to escalate to user-explicit (tier 4) when a lower tier would work.

## The four tiers

Ranked from most preferred to least preferred:

### Tier 1: Agent-immediate

The agent assesses the success criteria entirely on its own, in the same turn the work completes. No user involvement, no waiting.

Examples:
- "Count of `<X> Plan/` folders under `<X> Docs/` is zero." Agent runs `find` and reports the count.
- "audit-q on this anchor produces zero findings of type C13." Agent runs the script and confirms.
- "Function `foo()` returns the expected value for input X." Agent runs the test.

This is the gold standard. If the success criteria can be reduced to a runnable command or a deterministic observation the agent can make right now, choose this tier.

### Tier 2: Agent-over-time

The agent assesses the success criteria entirely on its own, but over an extended period (minutes, hours, days). The agent itself is responsible for the eventual check; the user is not involved.

Examples:
- Soak test: "no crash for 24 hours of normal usage" with a watchdog the agent owns.
- "F092's audit-architecture eventually catches the next anchor that drifts" with the agent re-running on a schedule.
- Recurrence check: "if the bug reappears in the next 7 days, the watchdog will detect and notify."

The agent owns the deferred check. The user is unburdened. If you can write a script that the agent runs later (cron, hook, post-condition), this tier applies.

### Tier 3: User-passive

The user assesses the success criteria in the natural course of their work, without being asked to do anything special. The user notices it working or notices it breaking. Two conditions:

1. **The user must know to be looking for it.** "Watch for X" requires the user to remember they are watching for X. The discipline does not assume the user has perfect recall; a brief reminder may be embedded in the user-facing reporting.
2. **The signal must be obvious.** "If this breaks, the user will obviously notice" qualifies (the broken thing is visible). "The user will notice subtly improved performance" does not qualify (too easy to miss).

A week-later check is acceptable here: the agent asks once, after enough time has passed for the user to have exercised the feature naturally. The question is yes-or-no, and the user answers from their own observation of normal use, not from a special test session.

Examples:
- "VOX email pipeline works." User sends voice memos as part of normal workflow; if it breaks, the audio doesn't get transcribed and the user notices immediately.
- "Pilot agent uses the new POST-COMPACT reload correctly." Visible in the agent's startup output; user sees it (or its absence) every session.

### Tier 4: User-explicit

The user has to perform a specific concrete test action that they would not otherwise have done. The action is named precisely, with steps, expected result.

This tier is least preferred. The user's attention is the cost. Use only when:

- No agent-checkable signal exists (the success criteria is genuinely outside the agent's ability to observe).
- And user-passive (tier 3) does not apply (the signal would not be obvious during normal use).
- And the verification cannot wait (see blocking-action escape hatch below).

Examples (only if no lower tier works):
- "User: open the app, click the Verify button, confirm the modal shows the correct text." Specific, concrete, but requires a special action.
- "User: confirm the migrated docs in the SVP repo look right by browsing the four-bucket structure." Requires a focused review session.

If a feature lands at tier 4, the agent should challenge itself: is there really no lower-tier path? Often a hook, a script, a passive signal, or a "just notice it next time you use X" reframing exists. Tier 4 is the escape hatch, not the default.

## The blocking-action escape hatch

Tier preference is reversed when verification is **blocking** another action that absolutely cannot begin until the current verification is complete. In that case, the agent needs a fast check (tier 1 or tier 2), even if a passive observation would have been acceptable otherwise.

The escape only fires when:

- A concrete next action is named (another F-number, a release, a deploy, a downstream feature that already has its dependency declared).
- That next action is **strictly blocked** until this verification is complete. "Nice to have" is not enough. "Would be more confident" is not enough. The blocked action genuinely cannot begin (would corrupt state, would build on a wrong foundation, would lock in an irreversible choice).

If the escape fires, the success criteria must be tier 1 or tier 2 so the next action can begin without an arbitrary user-attention delay.

If the escape does not fire (no strict downstream block), the normal preference holds: prefer tier 1, fall back to 2, fall back to 3, only escalate to 4 when 3 genuinely does not apply.

## The Success Criteria block in a feature doc

The discipline manifests as a `## Success Criteria` H2 in every feature doc, written at creation time, placed near the top (after Summary, before Design). Format:

```markdown
## Success Criteria

**Tier:** 1 (agent-immediate) | 2 (agent-over-time) | 3 (user-passive) | 4 (user-explicit)
**Blocks next:** none, OR [[F<n>]] (link to the action this verification gates)

**What done looks like.** One or two sentences describing the falsifiable end-state.

**How it will be verified.** The specific check, sized to the tier.
- Tier 1: a runnable command, a deterministic observation. Cite the command.
- Tier 2: the eventual check the agent owns. Cite the hook, script, or schedule.
- Tier 3: what the user is watching for in normal use, and when the agent will ask if they need to.
- Tier 4: the specific action steps the user must perform, with expected result.
```

The tier label is the structural teeth. The agent has to justify any tier above 1 (why is this not agent-checkable?). The Blocks-next pointer is the escape hatch: if filled, lower tiers (1 or 2) are required because the next action cannot begin until verification is complete.

## How `/feature` consults this

At feature-doc creation, `/feature` includes the four-tier summary in its runbook so the agent has the preference order in mind. The agent then writes the `## Success Criteria` block as part of the doc, picking the highest applicable tier and declaring it.

If the agent is about to write tier 4 with no Blocks-next, the agent should pause and reconsider: could a passive signal work? Could the user notice this in normal use? Often the answer is yes, and the right tier is 3.

The full discipline lives here; `/feature` carries a short summary inline so the agent does not need a separate file read at creation.

## How `/ask` and `/triage` consult this

When the agent is about to surface a Verify row to the user (in `{NAME} ask.md` or in the triage banner), the agent reads the linked feature doc's `## Success Criteria` block. The tier is the agent's guidance:

- **Tier 1 or 2:** the verification is the agent's job. The agent runs the check and updates the row, either to `[Done]` (verification passed) or to `[Active]` (verification failed, work to do). Should not surface to the user.
- **Tier 3:** prefer passive observation. Add a brief note in the ask page reminding the user what to watch for; do not block on an explicit answer. The agent may ask once after enough time has passed (typically a week), and the question is yes-or-no based on observation, not a special test.
- **Tier 4:** the verification genuinely requires a user action. Surface in the ask page as a User Verification with the specific steps.

If a Verify row has tier 4 declared, the agent should still challenge itself when surfacing: has enough time passed since work completion that a passive signal might have arrived? Could the verification be downgraded from explicit to passive at this point? If so, drop the surfacing.

## How to surface a Verify to the user (the asking discipline)

When a Verify genuinely needs to reach the user (tier 3 with the periodic-ask trigger, or tier 4), the surfacing must minimize the work the user does to answer. The recurring failure mode is the blanket ask: *"verify F57, F58, F59"*. The user does not remember what F57 is, has to open the feature doc, has to read pages of design rationale, has to mentally reconstruct what "verified" even means in that context, and then has to decide if they have the information to say yes or no. The cost is multiplied by every Verify in the batch.

**Before any user-facing Verify is surfaced, re-check the tier.** Tier 3 and Tier 4 are valid only when the verification GENUINELY requires the user's eyes — UI judgment, observation in a system the agent can't reach (an app on the user's device, a UI rendering, a sensation), or human-judgment-about-aesthetics. They are NOT valid when the verification reduces to "open file X and look for Y" AND the agent has Read access to X AND no human judgment is required — that's Tier 1 (agent-immediate) and the agent runs the check itself. Misclassifying a Tier-1 file-content check as Tier 3 "the user will see this in normal use" or Tier 4 "the user explicitly checks" is the failure mode named in `[[DSC ask-format]]` § Rule 6. The agent doing the Read and surfacing the verified result is the discipline; surfacing the verification *action* when the check is mechanical is round-trip cost with no human signal.

The discipline:

### Targeted questions, not feature references

A question to the user is targeted when the question itself carries the answer-enabling context. *"Verify F57"* is not a question; it is a pointer to a question. *"Have you sent a Voice Memo email since 2026-05-28 and seen the transcript land in `~/ob/kmr/Log/VOX/`?"* is a question. The user can answer it from their own memory without opening anything.

When surfacing a tier 3 or tier 4 Verify, the agent constructs the question by reading the feature doc's Success Criteria block and rephrasing the falsifiable claim into a yes-or-no question that embeds the specific signal the user is looking for. The F-number reference is appended for traceability, not as the question itself.

Good shape:
```
Did <specific observable thing> happen during <recent natural window>? ([[F<n>]])
```

Bad shape:
```
Please verify F<n>, F<m>, F<o>.
```

### Batch by ask, not by feature

Several Verifies often collapse to the same user action: *"did this work in normal use?"*, *"did this not recur?"*, *"is the folder organized the way you intended?"*. Group those into one combined question whose answer covers all the rows.

When the same observation answers multiple Verifies, surface as a single batched question with the feature-doc links listed as the items being verified. The user gives one answer and the agent applies it to all listed rows.

Bad shape (separate, each demands separate cognition):
```
1. Verify F57: <opaque title>
2. Verify F58: <opaque title>
3. Verify F59: <opaque title>
```

Good shape (one question, three rows resolved):
```
Have you used <feature area> in the last week without seeing <breakage signal>?
Yes/No covers: [[F57]], [[F58]], [[F59]].
```

### Minimum information, maximum context-portability

The question must be answerable without opening any documents. If the agent finds itself writing *"see the feature doc for details"*, the question is not yet targeted enough. Rewrite it until the question itself names the specific observation.

If the verification genuinely requires the user to perform an action (tier 4), the action steps go inline in the surfacing, not as a link. The user reads the question once and either does the action or postpones. Either way they are not chasing a doc-read.

### Default to silence on tier 1 / 2

Tier 1 and tier 2 Verifies are agent-owned. They do not appear in the user-facing surfacing at all (per `/ask` and `/triage` consultation above). The user does not see a question and the agent runs the check at its appropriate moment. The "did the agent forget?" failure mode is caught by the next `/audit q` pass surfacing any tier-1-or-2 Verifies that have stayed in `## Verify` past a soak period (separate enforcement; not blocking on F101).

### Frequency: ask once per row per cycle, not every cycle

A tier 3 Verify periodically reaches the user once enough time has passed that the passive signal should have arrived. The agent asks once per row per cycle, not on every `/ask` or `/triage` invocation. After asking, the row stays in `## Verify` until the user answers (or until the next periodic window). Repeated asking in adjacent crank cycles is itself a failure mode.

## Anti-patterns this discipline prevents

- **Tier-4-by-default.** The agent surfaces every Verify to the user as an explicit ask because that is the easy code path. Wastes user attention. The new discipline requires explicit tier choice at creation, surfacing the failure of imagination.
- **Tier 1 escalated to tier 4 at verification time.** Work completed; agent could check by running a one-line command; instead asks the user to confirm. The new discipline points at the success criteria's declared tier; the agent has no permission to escalate.
- **Blocking-action-without-escape.** A downstream feature is genuinely blocked by this verification, but the agent left the verification at tier 3 (week-later passive ask). The blocked feature stalls. The escape hatch forces the success criteria to tier 1 or 2 when Blocks-next is filled.
- **Vague success criteria.** "The feature works as designed" is not a falsifiable claim. The discipline requires a specific end-state and a specific check.

## Cross-references

- `[[feature]]` — at creation, writes the `## Success Criteria` block with tier declared.
- `[[ask]]` — at verification time, consults tier before surfacing a Verify to the user.
- `[[triage]]` — at verification time, consults tier when displaying Verify rows in the banner.
- `[[F098]]` — the Completion block discipline (Done time enumeration); the Verification sub-section in Completion records what was actually checked, referring back to this discipline.
- `[[workflow]]` — owns the state graph; Verify-state semantics inherit from this discipline's tier system.
