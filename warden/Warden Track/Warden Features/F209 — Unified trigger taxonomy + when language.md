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

## Open Questions

### Q1 — Phase default for bare `skill:<name>` / `tool:<name>` ^F209-Q1

When a rule names a moment without a phase, which phase does it bind to?

- **(A)** `post` — matches F180's current behavior; steer-after is the common case.
- **(B)** `any` — bare form fires at both pre and post; explicit phase narrows.
- **Recommendation:** Lean (A) `post` — the pre phase is the dangerous (veto-capable) one and should always be named explicitly. *(Skill half settled by Q3's resolution 2026-07-02: skills are `pre` in v1, so this now reduces to the **tool** bare-phase default.)*

### Q2 — Is `git:*` first-class or derived? ^F209-Q2

- **(A)** First-class moment family (`git:commit`, `git:push`, …) with its own taxonomy branch.
- **(B)** Purely derived sugar over `tool:*:Bash:git-*` — one taxonomy, git is pattern-matching.
- **Recommendation:** None — (A) reads better in rules and survives non-Bash git surfaces (jj, GUI); (B) keeps the taxonomy minimal. Genuine language-freeze call.

## Resolved

### Q3 — Emission point for `skill:pre/post` — RESOLVED (user, 2026-07-02): pre now, post later ^F209-Q3

**Decision: ship `skill:pre` soon; defer `skill:post` and all its end-of-work machinery to a later version (V2/V3), so the first system gets delivered end-to-end and used in real rules before we take on post's complexity.**

- **`skill:pre` ships soon** (near-term roadmap). Emitted mechanically from the **Skill-tool invocation** — the precise, cooperation-free signal (option (A)'s pre half). A skill *starting* is a real tool call the `PreToolUse` hook already sees.
- **`skill:post` is deferred to a later version.** The "when did a runbook finish?" problem has no clean mechanical answer (the Skill tool returns the instant the runbook is *injected*, i.e. at the start of the work, not the end), and solving it well is not worth blocking v1.
- **v1 phase collapse for skills** — since only `pre` is on the near-term roadmap, a bare `skill:X` **and** an explicit `skill:post:X` both resolve to `skill:pre:X`. Specifying `post` is **accepted, not an error — it is simply treated as `pre`** for now, and separates once post lands. (Settles the skill half of [[#Q1 — Phase default for bare `skill:<name>` / `tool:<name>`|Q1]]; the tool bare-phase default there stays open.)
- **When `skill:post` does land (V2/V3), it ships as a ladder of increasingly-precise approximations** — none blocking, adopted in order:
  1. **Agent-stop catchall** — post-actions run when the agent stops. The universal floor, always available (option (A)'s post half).
  2. **Agreed "done" sentinel** — a single mutually-agreed phrase the agent/skill emits to mark end-of-work; skills add it to their runbooks. More accurate than the stop-catchall — a disciplined form of option (B), via *one agreed marker* rather than ad-hoc per-skill emission lines.
  3. **Phrase registry** — alternatively/additionally, a registry of per-skill end-phrases. Later still.
  4. **Next-moment inference** — a following tool use / hook implies the previous work finished. **Caveat:** recursive / nested tool use breaks this (an inner tool call is not the outer one ending), so it may be unusable as a reliable signal — flagged uncertain, to be validated if/when post is built.
- **Priority principle:** deliver the first system tested end-to-end and in real rule use *before* handling post's complexity.

## Status

**Drafted 2026-06-26.** Taxonomy spec authored at [[Warden Events]]; architecture §5 updated to defer to it. **Q3 resolved 2026-07-02** (user): `skill:pre` soon, `skill:post` deferred to V2/V3 with an approximation ladder; v1 collapses `skill:post`→`skill:pre`. **2 questions remain** for the freeze — Q1 (tool bare-phase default) and Q2 (`git:*` first-class vs derived).
