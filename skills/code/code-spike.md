# Spike — Root Cause Diagnosis

Spike the bug. 4 escalating levels from standard debug to aggressive assumption elimination.

Invoked automatically by [[code-bugfix]] after the red test is written. Can also be invoked directly: `/code spike` or "spike that bug."

## Levels

| Level | Trigger | What you do |
|-------|---------|-------------|
| **1 — Standard** | First attempt | Reproduce → Isolate → Read → State cause → Fix |
| **2 — Instrumented** | First fix failed, or async/heuristic code | Add logging BEFORE fixing. Triangulate with multiple evidence sources. |
| **3 — Aggressive** | Second fix failed | Assume your assumptions are wrong. Systematic elimination. Divide and conquer. |
| **4 — Full spike** | Third fix failed | Full stop. Review architecture. Check the "wrong assumptions" list. Discuss with user. |

Auto-escalate: start at level 1, move up if the fix doesn't work. Start at level 2 immediately if the bug involves async, timing, heuristics, or external dependencies.

## When to Use

- Called from `/code bugfix` (the normal path)
- Directly when you know something is wrong but can't figure out why
- When the bug doesn't make sense — "this shouldn't be possible"
- When logging shows what you expect but the system still fails

## The Pin Mindset

**Stop making changes. Start gathering evidence.**

You are not trying to fix the bug. You are trying to find ONE LINE where reality diverges from your mental model. Once you find that line, the fix is usually obvious. Until you find it, every fix is a guess.

**Assume your assumptions are wrong.** You believe you know what's happening. You're wrong about something. The question is: what are you wrong about?

## Strategy 1: Divide and Conquer

Cut the problem space in half repeatedly:
1. Identify the full path from input to wrong output
2. Find the midpoint — add a log/assert there
3. Is the value correct at the midpoint?
   - Yes → the bug is in the second half
   - No → the bug is in the first half
4. Repeat until you're looking at ONE line

This is binary search applied to debugging. It converges in log2(n) steps.

## Strategy 2: Pervasive Systematic Logging

When you can't divide and conquer (too many interacting paths), instrument EVERYTHING in the suspect area:
- Log every function entry with all arguments
- Log every branch decision with the values that caused it
- Log every return value
- Log every state mutation

Then reproduce the bug and read the log line by line. Where does reality first diverge from what you expected? THAT is where the bug is.

## Strategy 3: Pin and Verify

When you think you know what a value is, **pin it** — add an assertion that crashes if you're wrong. If the assertion doesn't fire, your assumption is correct and you can move on. If it fires, you've found where reality diverges.

```python
assert config.timeout == 30, f"Expected 30, got {config.timeout}"
assert len(items) > 0, "Items was empty — shouldn't be possible here"
```

Pin every assumption until you find the one that's wrong.

## Strategy 4: Fresh Eyes

After 3 pin attempts, step back completely:
- Re-read the bug report from scratch
- Re-read the code path without assumptions
- Ask: "What if the problem isn't where I'm looking at all?"
- Ask: "What if the function I trust is the one that's broken?"

## Common Wrong Assumptions

Things you believe are true but might not be. Check these when you're stuck:

### You're looking at the wrong thing
- **Wrong log file** — the log you're reading is from a different run, a different process, or an old build
- **Wrong build** — the code running is not the code you just edited. Build cache, stale binary, deployment didn't complete
- **Wrong place in the log** — you're reading a log entry from before/after the actual failure, not the failure itself
- **Wrong process** — the log entries are interleaved from multiple processes/threads and you're attributing lines to the wrong one

### The code isn't doing what you think
- **Fallback triggered** — a function has a try/catch or default value and is silently returning something other than what you expect
- **Heuristic edge case** — a threshold, timeout, or scoring function has an edge case you're hitting
- **Cache stale** — you're getting a cached value, not a freshly computed one
- **Early return** — the function returned before reaching the logic you're looking at
- **Different overload** — a different version of the function is being called (wrong module, wrong import, method shadowing)

### The data isn't what you think
- **Value changed after logging** — you logged the value, but something mutated it between the log line and the use
- **Deep copy vs reference** — you're looking at a copy that's correct, but the original was modified
- **Encoding/serialization** — the value looks right in the log but has invisible characters, wrong encoding, or precision loss
- **Null/nil/undefined vs empty** — the value is "empty" but in a different way than you assumed (nil vs empty string vs "null" string)

### Timing and ordering
- **Race condition** — two things happening concurrently and the order isn't what you assumed
- **Callback fired early/late** — an async callback executed before/after the state was ready
- **Event ordering** — events arrived in a different order than expected
- **Retry/reconnect** — something failed, retried, and succeeded with different state

### Environment
- **Different config** — running with a different config file than you think
- **Permissions** — silently denied, returning empty results instead of an error
- **Network/external** — an external service returned something unexpected and the error was swallowed
- **OS version** — API behavior changed between OS versions

## Process

1. **State your assumptions** — write down everything you believe is true about the bug
2. **Rank by confidence** — which assumptions are you least sure about?
3. **Pin the least confident** — add logging/assertions to verify or disprove
4. **Reproduce** — run the scenario
5. **Read the evidence** — did anything surprise you?
6. **Update your model** — adjust your understanding based on evidence
7. **Repeat** — until you find the ONE thing that's wrong
8. **Fix** — now you can fix it because you KNOW what's wrong

## Rules

- **DO NOT make code changes to fix the bug during pin.** Only add logging, assertions, and diagnostic output. If you change the code, you change the behavior, and your evidence becomes meaningless.
- **DO NOT remove logging until the bug is fixed and verified.** The logging is your evidence. Keep it until you're done.
- **DO trust the evidence over your intuition.** If the log says X is 7, then X is 7. Don't rationalize why X should be 5.
- **DO question your logging.** Is the log line actually printing what you think? Is the variable name correct? Are you logging before or after the mutation?
