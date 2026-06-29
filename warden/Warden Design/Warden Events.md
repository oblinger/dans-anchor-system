---
description: "the moment catalog a `when::` clause names — the tree, the grammar, the per-class events"
---
# Warden Events

**Every moment Warden can fire on.** A `when::` clause names one of these. Read each row left to right — a **class** (with its `pre` / `post` phase, where it has one), then the **moment** that refines it. Deeper refinements — a specific Bash command, a skill's action — are in the per-class sections below; a path-valued tail (*which* file) lives in the cross-cutting [[FCT Ruleset\|where::]] clause. Tool and event tokens are Claude Code's own; the tree is ours.

| Moment class | Moment (2nd level) | Fires on (Claude Code) |
| --- | --- | --- |
| [[#Tool moments\|tool]] — pre, post | `Bash`, `Write`, `Edit`, `Read`, `Glob`, `Grep`, `Task`, `WebFetch`, `WebSearch` (+ MCP) | `PreToolUse` / `PostToolUse` |
| [[#Skill moments\|skill]] — pre, post | any skill — `audit`, `query`, `crank`, `audit-q`, … | skill-runner enter / exit |
| [[#Session moments\|session]] | `start`, `compact`, `stop` | `SessionStart` / `Stop` |
| [[#Content moments\|write]], [[#Content moments\|read]] | `markdown`, `rust`, `python`, `json`, `svg` | `PostToolUse` (Write/Edit/Read) |
| [[#VCS moments\|git]] | `commit`, `push`, `merge`, `pre-commit` | Bash-argv / git hook |
| [[#Turn moments\|prompt]] | `submit`, `stop` | `UserPromptSubmit` / `Stop` |

**Read a row as a path:** `tool` ⊃ `tool:post` ⊃ `tool:post:Bash` (⊃ `tool:post:Bash:git-commit`). A rule binds at whatever depth it cares about, and a shallower binding **prefix-matches** everything below it. `,` in a `when::` is OR across moments. The Claude-Code event mapping is in [[Warden Architecture]] §6 (hook subsystem). How a moment combines with `where::` / `if::` to fire a rule is **[[Warden Semantics]] § The condition** — this page is only the catalog of moments.

## Overview

The `when::` clause names a **moment** — a point in the agent's life when a rule should fire. Every moment lives in **one unified taxonomy**: a tree in which each node is refined into its children by exactly **one parameter**. `when:: tool` is every tool use; `when:: tool:post` is every moment *after* a tool; `when:: tool:post:Bash` is after a Bash call. A rule names the moment at whatever depth it cares about; a shallow moment matches all its descendants.

This page catalogs the moment classes, the `when::` path grammar, and the matching rules. It is the source of truth the rule compiler ([[Warden Architecture]] §7) indexes against.

> [!info] Why one parameter per level
> Refining by a single parameter per level makes the taxonomy **uniform** (every node has the same shape), **prefix-matchable** (a shorter path is a strict generalization of a longer one), and **extensible** (a new discriminator is one more level under an existing node — never a new top-level concept). Common moments stay shallow (≈2 levels); depth is *available*, not *required*.

## Grammar

```
when     := moment ("," moment)*       ; comma = OR — active at ANY listed moment
moment   := segment (":" segment)*     ; ":" descends one level (one refining parameter)
segment  := literal | glob             ; a level's parameter value (a glob matches siblings)
```

- **`:` refines by one parameter.** Each segment after the class is that level's single discriminator.
- **`,` is OR.** `when:: session:compact, skill:post:audit-q` fires at either moment.
- **A glob segment** matches sibling values at one level: `when:: tool:post:Bash:git-*`.
- **Path-valued tails move to [[FCT Ruleset\|where::]].** When a level's refinement *is a file path*, it is not a `when::` segment — `when:: write:markdown` + `where:: {ANCHOR}/**/*.md` *is* "after writing a markdown file under the anchor." `when::` stays the event; `where::` the place.

## Tool moments

Fire around any tool the agent invokes — the densest group, where "instrument almost every action" lives. Tool names are Claude Code's tool set (`PreToolUse` / `PostToolUse` matchers).

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `tool` | phase | `tool:pre`, `tool:post` | PreToolUse / PostToolUse |
| `tool:pre` / `tool:post` | tool name | `…:Bash`, `…:Write`, `…:Edit`, `…:Read`, `…:Glob`, `…:Grep`, `…:Task`, `…:WebFetch`, `…:WebSearch` (+ MCP tools) | the hook `matcher` |
| `tool:*:Bash` | command head *(optional)* | `…:Bash:git-commit`, `…:Bash:rm`, `…:Bash:npm` | argv parse |
| `tool:*:Task` | subagent type *(optional)* | `…:Task:Explore`, `…:Task:general-purpose` | `subagent_type` input |
| `tool:*:Write` / `…:Edit` / `…:Read` | *(path → [[FCT Ruleset\|where::]])* | — | `file_path` input |

## Skill moments

Fire around a skill executing. Skill names are our own registry; the action sub-level is optional.

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `skill` | phase | `skill:pre`, `skill:post` | skill-runner enter / exit |
| `skill:pre` / `skill:post` | skill name | `…:audit`, `…:query`, `…:crank`, `…:audit-q`, … | the running skill's id |
| `skill:*:<name>` | action *(optional)* | `…:audit:rules`, `…:audit:docs` | the sub-action arg |

## Session moments

Fire on the agent-session lifecycle — **two levels, no deeper**. (Claude Code's `SessionStart` carries a `startup`/`resume`/`clear` source, but almost no rule needs to tell them apart, so it is not part of the taxonomy; a rule that ever does can descend, but it is not enumerated.)

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `session` | phase | `session:start`, `session:compact`, `session:stop` | SessionStart / Stop |

## Content moments

A content-typed *view* of `tool:post:Write` / `…:Read`: refine by the file's **content kind**, then spatially by [[FCT Ruleset\|where::]]. These exist because most rules care about "a markdown file changed," not "the Write tool ran."

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `write` / `read` | content kind | `write:markdown`, `write:rust`, `write:json`, `write:svg`; `read:markdown`, … | PostToolUse(Write/Edit/Read) + extension/sniff |
| `write:<kind>` / `read:<kind>` | *(path → [[FCT Ruleset\|where::]])* | — | `file_path` input |

## VCS moments

Fire on version-control actions (often a refinement of `tool:*:Bash:git-*`, surfaced first-class because so many rules care).

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `git` | op | `git:commit`, `git:push`, `git:merge`, `git:pre-commit` | Bash-argv parse / git hook |

## Turn moments

Fire on the conversational turn boundary.

| Moment | Refines by | Children / leaves | Runtime |
|---|---|---|---|
| `prompt` | phase | `prompt:submit`, `prompt:stop` | UserPromptSubmit / Stop |

## Defaults & legacy compatibility

No "friendly alias" layer — the canonical moment path is the only first-class form. Two narrow conveniences only:

- **Phase default.** A bare `skill:<name>` or `tool:<name>` (no `pre`/`post`) defaults to **`post`** — `skill:audit-q` ≡ `skill:post:audit-q`. This is a default, not a second name.
- **Legacy shims (deprecated).** The already-shipped tokens `compact` → `session:compact` and `markdown-write` → `write:markdown` (from [[F091 — Trigger discipline|F091]] / [[F180 — When-trigger executable rules|F180]]) are accepted for back-compat, and rewritten to canonical form. New rules use the canonical path.

## Matching semantics

1. **Prefix match.** A rule's `when::` matches the fired moment iff it is an **ancestor-or-equal** of it. `when:: tool` matches `tool:post:Bash:git-commit`; `when:: tool:post:Write` matches that moment and any spatial child. Shorter = more general.
2. **Glob within a segment.** A glob matches sibling values at that one level (`git-*` → `git-commit`, `git-push`).
3. **OR across the comma list.** The rule is active if **any** listed moment matches.
4. **Then the rest of the condition.** A moment-match makes the rule a *candidate*; it *fires* only if `where::` matches the target and `if::` holds ([[Warden Semantics]] § The condition).
5. **Unknown moment = inert.** A `when::` naming a moment the runtime never fires is valid but never triggers (forward-compatible — e.g. reserved `git:merge` before a git hook exists).

## Extending the taxonomy

1. **Refine an existing node.** Add the new moment as one more parameter level beneath the deepest existing node it specializes — a new Bash subcommand is `tool:*:Bash:<new>`, never a new class.
2. **New event class** only for a genuinely new runtime hook surface — add a section with its Claude Code source.
3. **State the [[FCT Ruleset\|where::]] cross-cut** — does its leaf refinement become spatial?
4. **No new aliases.** Add a legacy shim only to preserve an already-shipped token.

## Open questions

1. **Content-kind detection cost.** `write:<kind>` needs an extension/sniff per write — extension-only for v1 (cheap), content-sniff reserved for ambiguous cases?
2. **`skill:pre`/`post` emission point.** Skills are runbooks, not processes — the "skill runs" moment must be emitted by the skill-dispatch layer. Where exactly? (Ties to the harness skill-runner.)

## See also

- [[Warden Semantics]] § The condition — how a moment combines with `where::` / `if::` to fire a rule.
- [[Warden Rule]] — the rule / ruleset format these moments live inside.
- [[Warden Architecture]] §6 — the hook subsystem that emits these moments; §7 — how they're indexed for cheap dispatch.
