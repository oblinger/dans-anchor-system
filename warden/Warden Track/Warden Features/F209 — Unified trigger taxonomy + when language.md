---
description: "F209 — Unified trigger taxonomy + `when::` language"
---

# [[Warden]] · F209 — Unified trigger taxonomy + `when::` language

## Summary

Today's triggers are a flat, ad-hoc set (`compact`, `markdown-write`, `skill:<name>`) spread across F180 (`when::`) and F091 (`.anchor` trait declarations). F209 replaces that with **one unified taxonomy**: a tree of agent *moments* where each node is refined into its children by exactly one parameter (`tool` → `tool:post` → `tool:post:Bash` → `tool:post:Bash:git-commit`). A rule's `when::` names a moment at any depth; a shallow moment prefix-matches all descendants. The full spec is [[Warden Events]]; this feature is the work to finalize it and make it the single source for triggers.

## Success Criteria

**Tier:** 1 (design + spec)
**Blocks next:** [[F210 — Conjunction binding + indexing|F210]], [[F211 — Rule compiler and installer|F211]]

**What done looks like.** The taxonomy spec is frozen: the moment groups (tool / skill / session / content / git / prompt), the grammar (`:` descends one parameter, `,` = OR), prefix-match semantics, and the alias table are complete and reviewed. Every existing trigger surface maps to a canonical moment path.

**How it will be verified.** A mapping table shows `compact → session:compact`, `markdown-write → write:markdown`, `skill:audit-q → skill:post:audit-q` with no orphans. A handful of real rules are re-expressed in the new `when::` and parse under the grammar.

## Design

See [[Warden Events]] for the full tables. Key decisions this feature locks:

- **Single refining parameter per level** — uniform shape, prefix-matchable, additive extension.
- **Path-valued refinements move to `where::`** — `when::` stays about the event class; the file/dir it concerns is the cross-cutting `where::` (see [[F210 — Conjunction binding + indexing|F210]]).
- **Aliases are sugar** — flat friendly names expand to canonical paths; the shipped F180/F091 vocabulary survives as aliases.
- **Unknown moment = inert** — forward-compatible reserved moments are valid but never fire.

## Resolved

### Q1 — Phase default for bare moments — RESOLVED (user accepted the Lean, 2026-07-02): tool → `post`, skill → `pre` ^F209-Q1

A bare `tool:<name>` (no phase) binds to **`post`** — the veto-capable `pre` is the dangerous one and is always named explicitly. A bare `skill:<name>` binds to **`pre`** in v1 (per Q3 — `post` is deferred). So `tool:Bash` ≡ `tool:post:Bash` and `skill:audit-q` ≡ `skill:pre:audit-q`. Defaults, not second names.

### Q2 — `git:*` first-class or derived? — RESOLVED (user, 2026-07-02): (A) first-class ^F209-Q2

**git is a first-class moment family** — `git`, `git:commit`, `git:push`, `git:merge`, `git:pre-commit` — with its own taxonomy branch ([[Warden Events]] § VCS moments). Rationale (user): the moments are still **lazily computed under the hood** (derived from Bash-argv parse / git hooks — *"it's all lazy, so it's just code"*), but surfacing git first-class makes rules **much easier to write** — `when:: git:commit` beats `when:: tool:post:Bash:git-commit` — and survives non-Bash git surfaces (jj, GUI). First-class *surface*, derived *implementation*.

### Q3 — Emission point for `skill:pre/post` — RESOLVED (user, 2026-07-02): pre now, post later ^F209-Q3

**Decision: ship `skill:pre` soon; defer `skill:post` and all its end-of-work machinery to a later version (V2/V3), so the first system gets delivered end-to-end and used in real rules before we take on post's complexity.**

- **`skill:pre` ships soon** (near-term roadmap). Emitted mechanically from the **Skill-tool invocation** — the precise, cooperation-free signal (option (A)'s pre half). A skill *starting* is a real tool call the `PreToolUse` hook already sees.
- **`skill:post` is deferred to a later version.** The "when did a runbook finish?" problem has no clean mechanical answer (the Skill tool returns the instant the runbook is *injected*, i.e. at the start of the work, not the end), and solving it well is not worth blocking v1.
- **v1 phase collapse for skills** — since only `pre` is on the near-term roadmap, a bare `skill:X` **and** an explicit `skill:post:X` both resolve to `skill:pre:X`. Specifying `post` is **accepted, not an error — it is simply treated as `pre`** for now, and separates once post lands. (Settles the skill half of Q1 above; the tool bare-phase default resolved to `post`.)
- **When `skill:post` does land (V2/V3), it ships as a ladder of increasingly-precise approximations** — none blocking, adopted in order:
  1. **Agent-stop catchall** — post-actions run when the agent stops. The universal floor, always available (option (A)'s post half).
  2. **Agreed "done" sentinel** — a single mutually-agreed phrase the agent/skill emits to mark end-of-work; skills add it to their runbooks. More accurate than the stop-catchall — a disciplined form of option (B), via *one agreed marker* rather than ad-hoc per-skill emission lines.
  3. **Phrase registry** — alternatively/additionally, a registry of per-skill end-phrases. Later still.
  4. **Next-moment inference** — a following tool use / hook implies the previous work finished. **Caveat:** recursive / nested tool use breaks this (an inner tool call is not the outer one ending), so it may be unusable as a reliable signal — flagged uncertain, to be validated if/when post is built.
- **Priority principle:** deliver the first system tested end-to-end and in real rule use *before* handling post's complexity.

## Status

**Drafted 2026-06-26.** Taxonomy spec authored at [[Warden Events]]; architecture §5 updated to defer to it. **All questions resolved 2026-07-02** (user): Q1 phase default (`tool`→`post`, `skill`→`pre`), Q2 `git:*` first-class, Q3 `skill:pre` now / `skill:post` V2/V3. **F209 is designed and ready to freeze** — the M0 language freeze now waits only on [[F210 — Conjunction binding + indexing|F210]] (2 questions). When F210 resolves, freeze both together.
