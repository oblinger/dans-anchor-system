---
description: "the formal `when::` moment taxonomy — one recursive single-parameter tree"
---

# Warden Trigger Taxonomy

The `when::` clause names a **moment** — a point in the agent's life when a rule should fire. Every moment in the system lives in **one unified taxonomy**: a tree in which each node is refined into its children by exactly **one parameter**. `when:: tool` is every tool use; add one parameter to get `when:: tool:post` (every moment *after* a tool); add another to get `when:: tool:post:Bash` (after a Bash call); add another to get `when:: tool:post:Bash:git-commit`. A rule names the moment at whatever depth it cares about; a shallow moment matches all its descendants.

This page is the formal specification of that taxonomy — the moment classes, the grammar, the matching rules, the friendly aliases, and the way `where::` cross-cuts the tree. It is part of the [[Warden Architecture]] (§5 binding) and the source of truth the rule compiler ([[Warden Architecture]] §7) indexes against.

> [!info] Why one recursive parameter per level
> Keeping refinement to a single parameter per level makes the taxonomy **uniform** (every node has the same shape), **prefix-matchable** (a shorter path is a strict generalization of a longer one), and **extensible** (a new discriminator is just a new level under an existing node — never a new top-level concept). It is the same discipline that makes the `where::` glob namespace tractable.

## The conjunction model — a rule is `when ∧ where ∧ if`

A rule is a standing constraint that means the **conjunction** of its clauses. It fires only when all hold:

| Clause | Dimension | Answers | Spec |
|---|---|---|---|
| `when::` | **moment** (temporal) | *at what moment?* | this page |
| `where::` | **place** (spatial, cross-cutting) | *concerning which file / directory / target?* | [[FCT Ruleset]] § Where clause |
| `if::` *(optional guard)* | **condition** | *and only if …?* | § Guards below |

The author writes the clauses; the **engine decides how to make the conjunction fire** (§ Indexing). The author never specifies the dispatch mechanism — only the truth condition. `where::` is deliberately a *separate* cross-cutting axis rather than more depth in `when::`: the same place-predicate (`{ANCHOR}/**/*.md`) applies under many different moments (write it, read it, audit it), so it factors out.

```
rule  ⟺  fires at  ( moment ∈ when::  ∧  target ∈ where::  ∧  guard(ctx) )
```

## Grammar

```
when        := moment ("," moment)*            ; comma = OR — active at ANY listed moment
moment      := segment (":" segment)*          ; ":" descends one level (one refining parameter)
segment     := literal | glob | "{TOKEN}"      ; a level's parameter value
```

- **`:` is "refine by one parameter."** Each segment after the class is that level's single discriminator.
- **`,` is OR.** `when:: session:compact, skill:post:audit-q` fires at either moment.
- **A glob segment** matches a set of sibling values: `when:: tool:post:Bash:git-*`.
- **Path-valued parameters move to `where::`.** When a level's refining parameter *is a file path or directory* (the leaf of a write / read / cd moment), it is **not** written as a `when::` segment — it is expressed in the cross-cutting `where::` clause. `when:: tool:post:Write` + `where:: {ANCHOR}/**/*.md` *is* "after writing a markdown file under the anchor." This keeps `when::` the event and `where::` the place.

## The moment tree

Each row is a moment node. **Refines by** names the single parameter that produces its children; **Children / leaves** lists representative values; **Runtime source** is the harness event the compiler binds it to; a ✓ in **`where::`** means the next refinement is spatial and belongs in `where::`.

### Group A — Tool moments  `tool:…`

Fire around any tool the agent invokes. This is the densest group — it is where "instrument almost every action" lives.

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `tool` | phase | `tool:pre`, `tool:post` | PreToolUse / PostToolUse | |
| `tool:pre` | tool name | `tool:pre:Bash`, `tool:pre:Write`, `tool:pre:Edit`, `tool:pre:Read`, `tool:pre:Task`, `tool:pre:WebFetch`, … | PreToolUse `matcher` | |
| `tool:post` | tool name | `tool:post:Write`, `tool:post:Edit`, `tool:post:Bash`, `tool:post:Read`, `tool:post:Task`, … | PostToolUse `matcher` | |
| `tool:*:Bash` | command head | `…:Bash:git-commit`, `…:Bash:git-push`, `…:Bash:rm`, `…:Bash:npm`, `…:Bash:cd` | argv parse of the command | |
| `tool:*:Write` | target path | *(refinement is spatial)* | tool input `file_path` | ✓ |
| `tool:*:Edit` | target path | *(refinement is spatial)* | tool input `file_path` | ✓ |
| `tool:*:Read` | target path | *(refinement is spatial)* | tool input `file_path` | ✓ |
| `tool:*:Task` | subagent type | `…:Task:Explore`, `…:Task:general-purpose`, … | Task input `subagent_type` | |

### Group B — Skill moments  `skill:…`

Fire around a skill executing. `skill:<name>` (the F180 shipped form) is shorthand for `skill:post:<name>`.

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `skill` | phase | `skill:pre`, `skill:post` | skill-runner enter / exit | |
| `skill:post` | skill name | `skill:post:audit`, `skill:post:query`, `skill:post:crank`, `skill:post:audit-q`, … | the running skill's id | |
| `skill:post:audit` | action | `…:audit:rules`, `…:audit:docs`, `…:audit:structure`, … | the skill's sub-action arg | |

### Group C — Session & context moments  `session:…`

Fire on the agent-session lifecycle.

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `session` | phase | `session:start`, `session:compact`, `session:stop` | SessionStart / Stop | |
| `session:start` | source | `session:start:startup`, `session:start:resume`, `session:start:clear`, `session:start:compact` | SessionStart `matcher` | |

### Group D — Content moments  `write:…` / `read:…`

A content-typed *view* of `tool:post:Write` / `tool:post:Read`: refine by the **content kind** of the file, then (spatially) by where. These exist because most rules care about "a markdown file changed," not "the Write tool ran."

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `write` | content kind | `write:markdown`, `write:rust`, `write:python`, `write:json`, `write:svg` | PostToolUse(Write/Edit) + extension/sniff | |
| `write:markdown` | target path | *(refinement is spatial)* | …+ `file_path` | ✓ |
| `read` | content kind | `read:markdown`, `read:rust`, … | PostToolUse(Read) + extension/sniff | |
| `read:markdown` | target path | *(refinement is spatial)* | …+ `file_path` | ✓ |

### Group E — VCS moments  `git:…`

Fire on version-control actions (often a refinement of `tool:*:Bash:git-*`, surfaced as first-class because so many rules care).

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `git` | op | `git:pre-commit`, `git:commit`, `git:push`, `git:merge` | Bash-argv parse / future git hook | |

### Group F — Turn moments  `prompt:…`

Fire on the conversational turn boundary.

| Moment | Refines by | Children / leaves | Runtime source | `where::` |
|---|---|---|---|---|
| `prompt` | phase | `prompt:submit`, `prompt:stop` | UserPromptSubmit / Stop | |

## Friendly aliases

A small set of **flat aliases** name common moments ergonomically. Aliases are sugar — each expands to a canonical moment path (sometimes plus a `where::` default). The shipped F180/F091 vocabulary is preserved as aliases.

| Alias | Expands to | Notes |
|---|---|---|
| `compact` | `session:compact` | F091 POST-COMPACT reload. |
| `markdown-write` | `write:markdown` | F091 on-write surface; `where::` left to the rule. |
| `markdown-read` | `read:markdown` | F091 v2. |
| `skill:<name>` | `skill:post:<name>` | F180 shipped form. |
| `on-commit` | `git:commit` | |
| `startup` | `session:start:startup` | |

New aliases are added only when a moment is common enough to deserve a flat name; the canonical path always remains valid.

## Matching semantics

1. **Prefix match.** A rule's `when::` moment matches the fired moment iff it is an **ancestor-or-equal** of it. `when:: tool` matches `tool:post:Bash:git-commit`; `when:: tool:post:Write` matches that exact moment and any spatial child. A shorter path is strictly more general.
2. **Glob within a segment.** A glob segment matches sibling values at that one level only (`git-*` matches `git-commit`, `git-push`).
3. **OR across the comma list.** The rule is active if **any** listed moment matches.
4. **Conjunction with `where::` / `if::`.** Moment-match makes the rule *candidate*; it *fires* only if `where::` matches the target and every `if::` guard returns true.
5. **Unknown moment = inert.** A `when::` naming a moment the runtime never fires is valid but never triggers (forward-compatible; e.g. reserved `git:merge` before a git hook exists).

## Guards — the optional conditional  `if::`

The common conditions are already covered by `when::` (the moment) and `where::` (the place). For anything else, a rule may carry one or more **guards** — a predicate that must hold for the rule to fire. Two forms, kept deliberately small:

- **Declarative guard** — `if:: <key> <op> <value>` over a fixed context vocabulary (`git-aspect`, `mode`, `trait`, `facet`): e.g. `if:: git-aspect == Commit`, `if:: trait has Code`. These compile to fast table lookups.
- **Code guard** — a fenced Python `def guard(ctx) -> bool` for the rare arbitrary condition. The same `ctx` the executable `trigger(ctx)` sees ([[F180 — When-trigger executable rules|F180]]).

Multiple `if::` lines AND together. A guard is just a conjunct of the rule's truth condition — semantically identical to folding the condition into `when::`, but kept separate so the moment taxonomy stays about *moments* and the guard stays about *state*.

## Indexing — the author writes truth, the engine picks dispatch

A rule states *what is true*; the **rule compiler** ([[Warden Architecture]] §7) decides *how to make it fire cheaply*. For each rule it chooses an **index key** — usually the `when::` moment (so the runtime hook for that moment dispatches straight to the rule), but sometimes the `where::` place (when a rule is `when:: always` but only concerns one rare file, indexing by path is cheaper). Whichever key it picks, the *other* clauses become the residual check run at fire time:

- indexed **by when** → at the moment, check `where::` + guards.
- indexed **by where** → on touching the place, check the moment + guards.

Either way the firing semantics are identical — the conjunction. The choice is a pure optimization the author never sees. This is what lets "almost every tool use is instrumented" stay cheap: most moments dispatch to a tiny, pre-compiled set of rules.

## Extending the taxonomy

To add a trigger:

1. **Find the deepest existing node** the new moment refines, and add it as one more parameter level beneath it. Never invent a parallel top-level concept if it is a refinement of an existing one (a new Bash subcommand is `tool:*:Bash:<new>`, not a new class).
2. If it is a genuinely new event class (a new runtime hook surface), add a new **Group** row with its runtime source.
3. Add an **alias** only if it will be named often.
4. State its `where::` cross-cut (does its leaf refinement become spatial?).

## Open questions

1. **`tool:pre` veto semantics.** PreToolUse hooks can *block* a tool. Do `tool:pre` rules return a steer message only, or may a guard deny the tool? (Leaning: a distinguished `deny` return, gated by the `aow-safety` floor.)
2. **Content-kind detection cost.** `write:<kind>` needs extension/sniff per write — is extension-only enough for v1 (cheap), with content-sniff reserved for ambiguous cases?
3. **`skill:pre`/`post` instrumentation point.** Skills are markdown runbooks, not processes — the "skill runs" moment must be emitted by the skill-dispatch layer. Where exactly does that fire? (Ties to the harness skill-runner.)
4. **Phase default.** Should bare `skill:<name>` / `tool:<name>` default to `post` (current F180 behavior) or `any`? (Leaning: `post`.)
