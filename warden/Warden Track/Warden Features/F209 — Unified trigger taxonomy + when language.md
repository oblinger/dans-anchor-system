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

1. Phase default for bare `skill:<name>` / `tool:<name>` — `post` (F180 current) vs `any`. (Leaning `post`.)
2. Whether `git:*` is first-class or purely derived from `tool:*:Bash:git-*`.
3. The exact emission point for `skill:pre/post` (skills are runbooks, not processes) — ties to the harness skill-runner.

## Status

**Drafted 2026-06-26.** Taxonomy spec authored at [[Warden Events]]; architecture §5 updated to defer to it. Remaining: resolve the open questions and freeze.
