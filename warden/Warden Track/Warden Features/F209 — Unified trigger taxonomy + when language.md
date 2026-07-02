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
- **Recommendation:** Lean (A) `post` — the pre phase is the dangerous (veto-capable) one and should always be named explicitly.

### Q2 — Is `git:*` first-class or derived? ^F209-Q2

- **(A)** First-class moment family (`git:commit`, `git:push`, …) with its own taxonomy branch.
- **(B)** Purely derived sugar over `tool:*:Bash:git-*` — one taxonomy, git is pattern-matching.
- **Recommendation:** None — (A) reads better in rules and survives non-Bash git surfaces (jj, GUI); (B) keeps the taxonomy minimal. Genuine language-freeze call.

### Q3 — Emission point for `skill:pre/post` ^F209-Q3

Skills are runbooks, not processes — there is no natural process boundary to hook. Where do `skill:pre` / `skill:post` moments get emitted?

- **(A)** The harness Skill-tool invocation (pre = tool call, post = next Stop) — mechanical, but post is approximate.
- **(B)** Explicit emission lines in each SKILL.md runbook (skills self-announce) — precise, but adoption-dependent.
- **(C)** Defer: ship without `skill:pre/post`; add when the harness exposes a skill-runner boundary.
- **Recommendation:** None — depends on how much you trust runbook self-announcement; ties to the harness skill-runner design.

## Status

**Drafted 2026-06-26.** Taxonomy spec authored at [[Warden Events]]; architecture §5 updated to defer to it. Remaining: resolve the open questions and freeze.
