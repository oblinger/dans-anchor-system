---
mission: <one-line mission for the agent>
# status_doc: <vault-relative override path>  # optional; default MY/Bridge agents/<host> agent.md
# heartbeat: agent-managed                     # optional; agent picks within standard ranges
# role: <cwd override>                         # optional; default invoker's cwd
---

# Brief — <task name>

| Field | Value |
|---|---|
| Mission | <one-line mission> |
| Status doc | [[MY/Bridge agents/<host> agent\|<host> agent status]] |
| Heartbeat | agent-managed |
| Started | <YYYY-MM-DD> |

## Mission

<One or two paragraphs explaining the task end-to-end. What done looks like, what success means, who cares.>

## Current state (snapshot at brief-write time — verify before acting)

- <Bullet what's already done.>
- <Bullet what's queued.>
- <Bullet known anomalies or partial progress.>

## Files

| Path | Purpose |
|---|---|
| `<path>` | <what it is> |
| `<path>` | <what it is> |

## Hard rules

- <Don't-do rules — specific things the agent must not do. E.g. "Don't remount drive X." "Don't auto-process Y; user batches it.">
- <Rules about destructive vs additive ops.>
- <Rules about user-involvement boundaries.>

## Status doc protocol

You maintain `~/ob/kmr/MY/Bridge agents/<host> agent.md`. Standard shape:

- H1 + dim italic `*Updated <ISO>. See [[<feature plan>]].*`
- Three one-line headlines at top — one per phase or workstream — `<emoji> <phase> <verb> — <X/Y> · <key info> · ETA <when>`. Emoji vocabulary: `🟢 progressing` / `🟡 slow` / `⏸ paused` / `🟠 stalled` / `🔴 attention` / `✅ complete`.
- `## ATTENTION` H2 immediately under the headlines **only when** user input is needed. Format: `**Recommended action:** … · **Why:** … · **Decision needed from you:** … · **If we wait:** …`.
- `## Now` — one short line, current activity.
- Detail sections below the fold (target lists, events, anomalies, decisions, next).

## Escalation protocol

When something *demands* the user's attention before the next scheduled heartbeat (not just "this target failed" — that's logged), write a `## ATTENTION` H2 at the top of the status doc with the decision-enabling format above. The user sees it on their next glance.

Things that warrant ATTENTION (not exhaustive):
- Hard-blocker discovered (mount disappears, source disk dies, methodology mismatch with plan).
- Cascading anomaly (>N failures in a row suggesting a wrong assumption upstream).
- Decision genuinely outside this brief — needs user judgment.

Routine failures (timeouts, expected-slow targets, single mismatches) → logged in status doc detail sections, no ATTENTION.

## Heartbeat

Arm a `ScheduleWakeup` heartbeat. Standard ranges:

- 60-300s during setup / first targets / after restarts
- 1200-1800s during steady-state (20-30 min)
- 30-600s during final wind-down

Every heartbeat: verify ground-truth progress (results file advancing, log mtime moving, process alive), regenerate the status doc, console-print `WORKING — <one-line current state>`. If no progress between two heartbeats → flag `🟠 stalled` in the headline, investigate.

**Heartbeat is non-optional while there's active work in flight.** Only stop heartbeating when everything is done or everything is so locked up there's nothing to verify (and the status doc says so).

## First thing to do right now

1. Read this brief in full (done if you're seeing this).
2. Read the linked plan doc end-to-end.
3. Probe initial state — confirm files exist, mounts are healthy, prior progress is where it should be.
4. Write the first `~/ob/kmr/MY/Bridge agents/<host> agent.md` snapshot.
5. Arm the heartbeat.
6. Begin executing.

Go.
