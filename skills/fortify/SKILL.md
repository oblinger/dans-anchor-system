---
name: fortify
description: >
  Skeptical, methodical counterpart to `crank`. With an argument
  ("fortify <task>" or `/fortify <task>`), apply the methodology to that task /
  backlog item / bug. Bare (`/fortify`), apply to whatever's in flight.
  Invoke when normal iteration has stopped converging — the same problem keeps
  coming back, fixes don't stick, tests pass but bugs persist. Distrust the
  logs, the code structure, the tests, and your own conclusions; fortify the
  foundation before continuing. The dictation pipeline auto-prefixes the buffer
  with `/fortify` whenever the word is spoken.
user_invocable: true
---

# Fortify — Cautious Crank

Skeptical, methodical counterpart to `crank` — when normal iteration stops converging, pause to distrust the logs / code / tests / mental model and fortify the foundation before resuming work.

`crank` says: pick the next thing and go.
`fortify` says: stop, distrust your own information, and strengthen the foundation before going on.

Use this skill when normal cranking has stopped working — the same bug keeps reappearing, every fix breaks something else, the tests pass but the system still misbehaves, or the agent's mental model and reality have clearly diverged. The stance is **the obvious read of the situation is probably wrong; fortify what's already here before adding more.**

## Trigger

- Word: **fortify** (in dictation, this auto-prefixes the buffer with `/fortify` — say "fortify <task description>" and on send the buffer becomes `/fortify <task description>`)
- Slash: **`/fortify [task description]`** invoked directly

(There is no single-keystroke punctuation shortcut for fortify. The double-quote `"` shortcut moved to `/triage` 2026-04-30 — triage is a far more frequent action, and the `?` glyph couldn't serve as triage's trigger because the UI already binds it.)

### Two invocation forms

1. **With an argument** — `/fortify <task description>` or "fortify <task description>". The argument names a task, backlog item, bug report, or area of code. Apply the fortify methodology *to that task*. The argument is the work; this skill is the methodology you do it with. Example: "fortify the OBU Files alignment bug" → treat that bug as the work, but enter the skeptical/methodical posture, audit the four suspects, fortify the foundation, then resume crank against that bug.
2. **Bare** — `/fortify` with no argument. Apply the methodology to whatever the agent is *currently* working on. Used when in-flight cranking has stopped converging and the agent should pivot to fortify mode without changing what it's working on.

Both forms run the same runbook (below). The only difference is what the *target* of the fortification is — a named item from the user, or the current in-flight work.

## Posture — distrust four things

When invoked, treat all four of the following as suspect until each is checked:

1. **The information feeding your conclusions** — logs, error messages, observed behavior. They may be incomplete, misleading, or being misread.
2. **The structure of the code under work** — too many implicit assumptions, too much hidden state, too much coupling. Fragility is enabling the bug; the bug is not just one wrong line.
3. **The tests that are passing** — passing tests prove only that *those checks* passed. Coverage shape is suspect; assertion strictness is suspect.
4. **Your own model of the system** — the mental picture is wrong somewhere; that's why the cranks aren't sticking.

Spike teaches "assume your assumptions are wrong" for a single bug. Fortify applies the same posture to the *whole working context*: information sources, code shape, test suite, and mental model — all at once.

## Activities

Each fortify cycle picks the relevant subset of these. Cheap → expensive:

### 1. Re-read existing evidence first

Before adding more logs, check whether the existing logs already answered the question and you missed it. Common misses:

- Wrong log file (different process, different run, stale build)
- Wrong place in the log (reading entries from before/after the actual failure)
- Wrong process attribution (interleaved log lines from multiple processes)
- Right log, but the relevant signal isn't where you expected — read the whole window, not just the suspect span

### 2. Logging discipline — add, then re-read methodically

If existing logs really are insufficient, add logs at the right places:
- Function entry with all relevant arguments
- Branch decisions with the values that drove them
- State mutations (before-and-after)
- Return values

Then reproduce the issue and read the log **line by line**, not just "did it crash." The point is to find where reality first diverges from what you expected.

### 3. Test fortification — coverage and rigor

Treat the existing test suite as untrustworthy in the affected area:

- **Coverage gaps** — list cases that *aren't* tested but should be. Realistic edge cases, error paths, boundary conditions, concurrency, retries.
- **Weak assertions** — find tests that pass without actually verifying the property they claim to verify. ("It didn't crash" is not the same as "the output is correct.")
- **Red-green expansion** — write a batch of failing tests for the gaps. Aim for many failing tests at once, then drive them green together. This is faster than one-test-at-a-time when the foundation is being rebuilt.
- **Tighten existing tests** — strengthen weak assertions to actually check the invariant.

### 4. Code hardening — invariants and explicit checks

Add defensive scaffolding so impossible states are detected early instead of silently producing wrong output:

- Pin invariants with assertions at key boundaries
- Validate inputs at function entry where it matters
- Replace silent fallbacks with explicit failures
- Add explicit checks for the failure modes the bug exposed

### 5. Application simplification — requires user approval

If the code's *shape* is making problems hard to reason about, propose simplification:

- Collapse two paths into one
- Remove a layer of indirection
- Eliminate implicit state
- Replace clever code with boring code

**Application-shape changes are not autonomous.** Anything that changes how the application or a sub-feature behaves visibly, alters a public API, or reshapes architecture must be cleared with the user before implementation.

### 6. Update the model, then resume cranking

Once the foundation is fortified, re-derive the working hypothesis from the new evidence — do not re-use the old one. Then resume normal `crank` work on the firmer base.

## Principles

1. **Wall-clock cost is irrelevant; user-interruption cost is the constraint.**
   The agent should not minimize compute or reasoning time — it should minimize the number of times the user is pulled into the loop. Take longer; ask less.

2. **Batch open questions, never trickle them.**
   If user input is genuinely needed, gather all questions and surface them in one batch via the /ask skill. Never stop / ask / resume / stop / ask / resume.

3. **Default to "do more, not less."**
   When the choice is between *less* and *more* coverage / robustness / test rigor / hardening, choose *more* without asking. The user does not need to be consulted for "should I add more tests or fewer?" — the answer is always more.

4. **Only escalate on real trade-offs or application-shape changes.**
   Bug fixes, hardening, test expansion, log expansion, invariant pinning: do not require approval. Changes that reshape *how the application behaves* (visible behavior, public API, architectural reshape) require approval. So do choices where one approach is genuinely more robust along one axis and less robust along another — those are real trade-offs and warrant the user's call.

5. **The agent's prior conclusions are evidence, not truth.**
   Be willing to throw out the working hypothesis if the fortified evidence doesn't support it. The point of fortify is that you have already iterated and not converged — your conclusions to date are suspect by construction.

## Runbook

When invoked (`/fortify <task>`, "fortify <task>", or `/fortify` bare):

1. **Identify the target and restate the problem.**
   - If an argument was given, the target is the named task / backlog item / bug. Locate it, read its current state, and restate it.
   - If no argument was given, the target is whatever the agent is currently working on. Restate it.
   In one or two sentences: what has been tried, what hasn't worked, why is normal crank not converging?
2. **Audit the four suspects** — information, structure, tests, model. Pick which need fortifying for *this* problem.
3. **Fortify in cheap-to-expensive order:**
   1. Re-read existing logs more carefully.
   2. Add logging where missing; re-run; re-read line by line.
   3. Identify test coverage gaps; write red tests in a batch.
   4. Identify weak assertions; tighten them.
   5. Add invariant pins / explicit checks in the code itself.
   6. (If warranted) Propose simplification or application-shape change → escalate to user via /ask skill.
4. **Drive the red tests green.** Once the foundation is firmer, resume red-green systematically.
5. **Surface only what needs surfacing.** Batch any open questions; otherwise keep going. Wall-clock is not the constraint — interruptions are.
6. **Resume `crank`** when the foundation is fortified and the working hypothesis has been re-derived from the new evidence.

## Relationship to `/spike`

Fortify and spike share the skeptical posture but differ on what happens next.

| | `/spike` | `fortify` |
|---|---|---|
| **Scope** | One specific bug | Any work that's not converging |
| **Action** | Diagnostic only — no code changes during pin | Corrective — actively changes tests, logs, structure |
| **Goal** | Find the ONE LINE where reality diverges from model | Fortify the foundation so progress resumes |
| **Trigger** | "this bug is weird" | "we keep cranking and nothing sticks" |
| **Owner** | Sub-step of `/code bugfix` | Peer of `crank` |

Spike collects evidence and stops. Fortify uses evidence to actively rewrite the test suite, the logging, and (with approval) the code structure.

If a single bug is the problem, prefer `/spike`. If iteration on the *whole context* is failing, use `fortify`.

## Anti-patterns

- **Fortify-as-procrastination.** Fortify is invoked because cranking failed, not because cranking is uncomfortable. Don't fortify when normal crank would work.
- **Endless fortification.** Fortify has an exit: when the foundation is firm enough that the working hypothesis can be re-derived. Fortifying forever is its own anti-pattern.
- **Fortifying everything.** Fortify the part that's failing — not the rest of the codebase. Scope the audit to the suspect area.
- **Skipping the user-approval gate on application-shape changes.** Hardening and test expansion are autonomous. Restructuring how the app behaves is not.
- **Asking the user mid-fortify.** Fortify minimizes user interruptions. Batch any questions; do not trickle them.
