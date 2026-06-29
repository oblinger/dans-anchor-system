---
description: "F216 — Agent-state model — sensing what the agent is doing"
---

# [[Warden]] · F216 — Agent-state model — sensing what the agent is doing

## Summary

Rules can sense the **agent itself** via the `agent` object in the interpretation environment ([[Warden Semantics]] § The interpretation environment) — `agent.state` (`working` / `landed` / `asking` / `idle`), `agent.skill`, `agent.is_asking`. This lets a rule fire at a turn boundary (`when:: prompt:stop`) and react to *how the turn ended* — e.g. "you're ending the turn with an open question; record it in `queries.md`." F216 designs **how that state is actually determined**, which is non-trivial: it requires reasoning about the agent's recent activity, not reading a single flag.

## Success Criteria

**Tier:** 1 (design) — powers `agent.*` in the environment; rules that read it can't ship until this does.
**Blocks next:** [[F217 — Conversation-content gating]] (which extends observation from *state* to *transcript content*).

**What done looks like.** Given a live agent session, the daemon can answer `agent.state` accurately for the common cases: actively working (a task/skill in flight), landed (a clean turn end), asking (a pending user question, e.g. `/query` ran or `{NAME} queries.md` has open items), idle. `agent.skill` reports the running skill. The classifier is lazy + cached per pass (one read, shared across rules).

**How it will be verified.** Scripted scenarios that drive an agent into each state (mid-task, post-`/land`, post-`/query`, idle), asserting `agent.state` matches; a fixture rule (`R-ex-10`) fires its `tell` only in the `asking` state.

## Design

**Source of truth — prefer the agent's tmux session.** Cleanest access is the agent's **tmux pane** (scrollback + the running command), which exposes the running skill, the last output, and whether control returned to the user. *Assumption to avoid hard-coding:* the design should treat "the agent runs in a known tmux session" as the *common, clean* path but not the *only* one — fall back to other signals (a status file, the skill-runner's events, `{NAME} queries.md` state) where tmux isn't available.

**Signals → state (the non-trivial part).**
- `working` — a skill/task is mid-execution (the skill-runner is active; the pane shows an in-progress command).
- `landed` — `/land` (or a clean `Stop`) just completed; no pending question.
- `asking` — a pending user-facing question exists: `/query` ran this turn, or `{NAME} queries.md` carries open items, or the last agent message ends in a question to the user.
- `idle` — no activity, control with the user, nothing pending.

**Open questions.**
1. tmux dependency — how much do we lean on the pane vs. structured signals? Define the fallback ladder.
2. Where is `agent.skill` emitted from — the harness skill-runner, or sniffed from the pane?
3. Cost — `agent.state` is lazy (computed only when a rule reads it), but the classifier mustn't itself be expensive (no LLM for the common cases).

## Status

**Ready** — design item; flesh out the signal→state classifier and the tmux/fallback ladder.
