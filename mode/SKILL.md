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


## Modes-as-flat-list (per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]])

Modes are **compositional traits**, not points on a single axis. A pilot runs with one or more modes active at the same time; compatibility is documented here (not enforced by an axis schema). The default pair is **Drive + Git Standard** — Drive shapes how the agent makes trade-off decisions; Git Standard shapes how the agent handles git boundaries within those decisions. They are orthogonal and compose cleanly.

Available modes (the flat list):

| Mode | What it shapes | Doc |
|---|---|---|
| **Drive** | Trade-off posture — agent-driven, optimistic, minimum-interruption | § Drive (below); [[SKL Mode Drive]] |
| **Cautious** | Counterpart to Drive — invoked via `/fortify` for distrust-the-foundation work | [[SKA fortify]] |
| **Git Standard** | Git boundaries — commit on logical breaks, terse messages, never auto-push | § Git Standard (below) |
| **Git PR** | Git boundaries — every state-touching commit gated through PR review | [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] — design |

**Compatibility:** Drive and Cautious are mutually exclusive (you're in one or the other). Git Standard and Git PR are mutually exclusive (a pilot has exactly one git-handling mode active at a time). Drive composes with either Git mode; Cautious composes with either Git mode. The default for new anchors is **Drive + Git Standard**.

## Current mode — Drive

Drive shapes the trade-off posture: agent-driven, optimistic, minimum-interruption. Full assertions in [[SKL Mode Drive]]. The load-bearing rules are inlined in `role-pilot.md` POST-COMPACT RELOAD so they prime the agent on every session start.

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


## Git Standard mode (per [[F085]])

Git Standard shapes how the agent handles git boundaries inside a mint or skill execution. **Default for new anchors; default for SKA.** Paired with Drive in the canonical setup.

**Three load-bearing rules:**

1. **Commit at logical boundaries** — without prompting the user. A boundary is one of (hybrid per F085 Q1):
   - **Per-skill-exit** — when a skill finishes its main work (e.g., `/feature` finishes commissioning, `/mint` finishes implementation, `/groom` finishes the sweep).
   - **Per-state-transition** — when a backlog item flips state (`[Active]` → `[Verify]`, `[Verify]` → `[Done]`, `[Ready]` → `[Active]`).
   - **Per-judgment-collapse** — when two or three rapid sequential edits naturally belong together (don't fragment into trivial commits; use judgment to bundle).
   The agent does NOT ask "should I commit now?" — commit is the default at any of these moments.
2. **Terse commit messages** — short subject line, no boilerplate (no "Generated by Claude" / "Co-Authored-By" unless the user has explicitly opted in elsewhere). Body adds context when the change is substantial; tiny edits get subject-only commits.
3. **Never auto-push** — the agent commits freely but does NOT push to remotes unless the user explicitly says so. Auto-push is the irreversible action that the [[F068 — Assume-and-announce discipline (Drive mode)|F068]] gate protects against; auto-commit is fully reversible (rewrite history locally).

**Composition with `/pr-flow` (per F085 Q2):** Git Standard yields to Git PR semantics **only during** an active `/pr-flow` invocation. Outside of `/pr-flow`, Git Standard is in effect; inside `/pr-flow`, the PR-mode rules (state-touching commits gated through PR review) take over until `/pr-flow` exits.

**Why no auto-push (per F085 Q3):** push is visible to others, hard to reverse, and crosses the F068 irreversibility threshold ("invisible OR high recoverability cost OR irreversible — always ASK"). Commit-only auto-behavior keeps the user in control of when work becomes public.

**Agent-facing summary** (the same load-bearing rules in clipped form for inclusion in `role-pilot.md` POST-COMPACT RELOAD):

- Commit at logical boundaries without asking — skill-exit, state-transition, judgment-collapsed rapid edits.
- Terse subject-only when small; add body when substantial. No boilerplate.
- Never auto-push — ask explicitly before any `git push`.
- Inside `/pr-flow` → defer to PR mode rules until /pr-flow exits.


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
