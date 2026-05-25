---
name: mode
description: >
  Operating-mode discipline. Pre-decides recurring "more thorough vs faster"
  trade-offs so the agent doesn't have to ask each time. Cited by other skills;
  not directly user-invocable.
user_invocable: false
---

# Mode Discipline

A **mode** is a setting that shapes how the agent makes recurring trade-off decisions. Different anchors have different risk profiles — a freshly-built tool with no users tolerates aggressive forward motion; a deployed app with thousands of users needs more caution per change. Mode is the declaration of which posture is appropriate.

User docs: [[SKL Mode]] (framework) and [[SKL Mode Drive]] (the current mode).
Anchor page: [[Mode]]


## The metric — outcome per interaction

The agent optimizes:

> **outcome per interaction**

with this cost structure for the denominator:

- **Heavy weight** — each content-full batch (any session where the user must read, think, and respond).
- **Lighter weight** — each round-trip within a batch (back-and-forth Q&A inside one active session).
- **Lightest weight** — each `/crank` press (no content but still attention).

The numerator is **capability produced** — features shipped, decisions resolved, working code committed, design questions answered, technical debt paid.

The whole posture follows from this metric: **minimize content-full batches first, round-trips within them second, crank presses third.** Tokens are not in the denominator at all.


## Current mode — Drive

The system-wide mode is **Drive** — agent-driven, optimistic, minimum-interruption. Full assertions in [[SKL Mode Drive]]. The load-bearing rules are inlined in `role-pilot.md` POST-COMPACT RELOAD so they prime the agent on every session start.

Drive's core assertions, in clipped agent-facing form:

- **Tokens are NOT the constraint; user-interruption cost and quality ARE.** When in doubt, pick the more complete option unless there's a real risk/performance/deployment-safety issue.
- **Add tests for plausibly-reachable edge cases without asking.**
- **Adjacent cleanup is silent** — fix inline or skip; don't make a question of it.
- **Don't ask about token / PR / commit size.** Right-size for the work; commit on transitions.
- **Sweep cross-references for consistency by default.** Drift is a slow-burn problem.
- **Memory updates on surprise.** Not for routine work.
- **Docs ship with code in the same commit.**
- **DO ask** when there's a genuine safety / performance / deployment-risk / design-direction trade-off OR genuinely ambiguous user intent. Threshold: "real consequence of wrong choice," not "two plausible options exist."
- **Per-turn override:** "just do the simple thing" / "quick fix" / "minimal" → lean mode for that turn. "Be thorough about X" → reaffirms Drive.

The failure mode Drive constrains: asking about every trade-off where the wrong answer doesn't actually hurt anything. That's friction, not collaboration. Decide and move.


## How mode is currently resolved

**v1 (current):** the system-wide mode is declared inline in `role-pilot.md` § POST-COMPACT RELOAD, where it primes the agent every session.

**v2 (eventual, gated on F034 Q3 resolution):** per-anchor mode declared via `mode:` field in `.anchor` config; system-wide default in `~/.claude/CLAUDE.md`. Anchor-specific override wins. A future `/mode` slash command will support inspection (`/mode` reports current) and switching (`/mode set drive` rewrites the declaration).


## Cited by

- `role/role-pilot.md` § POST-COMPACT RELOAD — inlines Drive's load-bearing rules.
- `/crank`, `/mint`, `/feature`, `/ask`, `/groom`, `/code` — should consult mode when making recurring trade-off decisions (per F034 § Affected surfaces).


## Cross-references

- **[[SKL Mode]]** — user-facing framework doc.
- **[[SKL Mode Drive]]** — Drive mode user-facing assertions + canonical agent-facing inline copy.
- **[[F034 — Operating Mode]]** — design discussion (open questions for v2).
- **`role/role-pilot.md`** — the inlined POST-COMPACT copy.
