---
description: "`/land` — bounded crank."
---
# /Land

`/land` — bounded crank. Finish **every** activity that is currently in flight, commit, clean up, report done, and stop.

Usually only one item is open and land closes it. When the session has gotten distracted and several items are open, land closes all of them in one invocation. Backlog items, roadmap entries, and feature docs without started work are **out of scope** — land does not promote them.

Unlike `/crank`, land does **not** pick up new work after the in-flight items close. It is the "wrap up everything that's open and put it down" command.

## Triggers

- **`/land`** — explicit invocation
- **`.`** (a single period as the entire message) — punctuation trigger, paralleling `'` for crank and `"` for fortify

The plain word *land* is **not** a trigger — it is a common English word the user uses in sentences. Only the slash form, the explicit `/land`, or the bare period invokes this skill. There is no DMUX prefix wiring.

## Behavior

1. **Enumerates the in-flight items** — every activity that has uncommitted edits, runtime state, or recent agent attention. Lists them back to you in one line each so you can correct scope before commit.
2. **Lands each one in turn** — finish the work (code, tests, docs that match implementation), commit, push, verify clean. One full cycle per item.
3. **Reports done in one block** — one line per landed activity, ending with `Nothing more to do.` Then stops.
4. **Does not check the backlog. Does not promote not-yet-started items. Does not pick a next task.**

## How land relates to its neighbors

| Command | Trigger | Behavior |
|---|---|---|
| `/crank` | `'` | Keep going indefinitely; finish current thread, then pick up new work |
| `/fortify` | `"` | Skeptical crank — distrust the foundation and shore it up before continuing |
| `/land` | `.` | **Bounded crank — finish the current thread, then stop** |
| `/finalize` | — | End-of-feature ceremony (verify, commit, update docs/stat, archive). Land delegates to finalize when the activity *is* a feature wrap-up. |

## Agent specification

Full runbook for the agent: [`~/.claude/skills/land/SKILL.md`](../../land/SKILL.md)
