---
description: "how the engine runs a rule — IF (dispatch indexes + a condition) THEN (actions)"
---
# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model — kept small: **a rule is `IF` a condition `THEN` an action.** The engine dispatches to a rule cheaply (by moment + file), evaluates its condition, and on a hit performs its action(s).

## A rule at a glance

![[Warden Rule Anatomy.svg]]

| Clause | Part | What it does |
|---|---|---|
| `where::` | `IF` · index | which files it runs over — a glob (default `always`) |
| `when::` | `IF` · index | which moment triggers a **live** run — omit → *passive* (audit-time) |
| `if::` | `IF` · test | the condition — a primitive (`regex_present …`), Python, or LLM prose; yields the findings to act on |
| `tell` | `THEN` | say something to the agent — a problem *or* a directive (a steer live / a finding under audit) |
| `edit` | `THEN` | write to a file — repair, log, stamp, drop data (never-delete floored) |
| `deny` | `THEN` | block the pending tool (`tool:pre` only) |
| `run` | `THEN` · *future* | arbitrary effects — **deferred** (a security model first; see [[Warden PRD]]) |

Plus its **name** (`R-<slug>-NN`) and an optional `rerun::` modifier. There is no separate *check*, *evaluator*, *tier*, *outcome*, or *economy* concept — **a check is just an `if::` condition.**

## `IF` — the condition

Three clauses, **two kinds**. `where::` and `when::` are **indexes** — the compiler uses them to pick candidate rules *without running any code* (a glob match, a moment-path match); that's what keeps "instrument almost everything" cheap. `if::` is the **test** — the computed predicate, evaluated only after dispatch has narrowed the field.

| Clause | Kind | |
|---|---|---|
| `where::` | **index** (glob) | which files — required (default `always`), **anchor-relative**; [[FCT Ruleset]] § Where clause |
| `when::` | **index** (moment) | which live moment — omit → *passive*; [[Warden Trigger Taxonomy]] |
| `if::` | **test** (computed) | the condition — a Python expression, or prose (below) |

**`where::` is anchor-relative.** A glob resolves under whatever anchor *adopts* the rule — `**/*.md` means "every markdown file in this anchor." That's why one rule is reusable across anchors. The explicit `{ANCHOR}/` token is optional (clearer in shared rulesets); a bare glob is equivalent.

**Live vs. passive** — a `when::` makes the rule fire **live** at that moment (the fast guardrail); with **no `when::` it is passive**, run only when `/audit` visits its `where::` files (the backstop).

**Why `if` stays separate from `when`.** `when`/`where` are *indexical* — clean tokens (`write:markdown`, `*.md`) the compiler matches without execution. `if` is *computed*. Folding `if` into `when` would either uglify the simple `when` clause or mix a dispatch index with computation, so they stay apart.

**The test (`if::`) is a Python expression** — there's **no condition DSL**. The common predicates are read-only **`ctx` inspectors**, so a check reads as plain Python:

```
if:: not ctx.has(r'^# ')        # a primitive check, written as Python
```

(A value that itself contains `::` — like a regex for `description::` — is **backticked**, per [[F007 — Backtick all where expressions — parser swap|F007]], so Dataview doesn't choke on it.) Or **prose**, when the test needs judgment — the LLM reads `ctx` and decides. (For a computed, per-violation test, skip `if::` and write a body **snippet** that conditions and tells inline — § THEN.) Either way a test yields **findings** (each a message) or a boolean. A `focus:: <expr>` clause hands the LLM just a slice before it judges — **script-assisted**.

## `THEN` — the actions

On a hit, the rule performs zero or more actions. Three are **mediated** — Warden controls exactly what each does, so they're safe even in a rule you didn't write — and one is the **unmediated**, *deferred* escape hatch:

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — the test found no problem | — |
| **tell** | **bare prose** — or `ctx.tell(msg)` | say something to the agent — a problem *or* a directive ("commit now", "don't ask the user") | a **steer** injected into the agent's context (live) · a **finding** in the report (audit) |
| **edit** | `ctx.edit(path, change)` | write to a file — repair the target, append a log, drop data elsewhere | the file(s) — gated by the never-delete floor |
| **deny** | `ctx.deny(reason)` | block the pending action | the tool call — `tool:pre` only |
| **run** *(future)* | the Python body, directly | arbitrary execution — run commands, drive Warden / other agents | **deferred** — needs a security model first |

**A bare prose body *is* the tell.** When the action is just "tell the agent this," you write the prose — no keyword (the `tell` payload is the whole point). For anything more, the body is a **bare Python snippet** — `ctx` is in scope, no `def`, no magic function name — and it calls `ctx.tell` / `ctx.edit` / `ctx.deny`. (`message:: <text>` is the sugar for a fixed prose tell; a *fix* is an `edit` that repairs a violation.) **Emit nothing → the rule passed.**

**`ctx` splits in two — and the split is load-bearing for readability.** **Inspectors** are read-only — `ctx.text`, `ctx.command`, `ctx.has(regex)`, `ctx.section(…)` — they *look*, never act (so the LLM reading `ctx.command` knows nothing runs). **Actions** are the only things that *do* — `ctx.tell` / `ctx.edit` / `ctx.deny`. A method name should never blur the two (e.g. `ctx.bash(…)` would wrongly read as "run bash" — inspect `ctx.command` instead).

**What `tell` actually does.** **Live** → text the hook injects into the agent's context (what you'd picture as "printed to the agent" — the F180 steer); **audit** → a finding written into the report the user reads. Same `ctx.tell`; the trigger picks the channel.

**Mediated vs. unmediated.** The three mediated actions (**tell · edit · deny**) are a **closed, small set**, so the body just *calls* the one it wants — **no test × action cross-product, no action language to invent.** `run` is the exception (arbitrary Python = arbitrary code execution, incl. controlling Warden or other agents) and is **deferred** — see [[Warden PRD]] § Security and the open question below.

> **Open — `run`'s trust model.** Your own rules are as trusted as your own scripts, so unbounded effect is arguably fine; an *imported* ruleset carrying effectful Python is a **supply-chain risk** (adopting it runs its code on your moments). Leaning: **ship the mediated three first; add `run` only behind explicit trust, off for imported rules.**

**What a body sees** — `ctx`: `ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered test also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

## The pipeline

```
on trigger:  a when:: moment fires,  OR  /audit visits an anchor
  candidates = rules whose where:: (and when::) INDEXES match   # cheap, no code
  for each candidate rule, for each file T it matches:
    if a cached result for (rule, T) is fresh under rerun:::  reuse it
    else:  evaluate if:: over ctx(T)  → findings (or false)
           cache it by (rule, hash(T)[, model])
    for each finding:  perform the action(s) — tell / edit / deny
```

## Re-running an expensive test

An `if::` test that calls the LLM costs tokens, so its result is cached by file-content-hash and reused until the file changes. **`rerun:: significant`** relaxes that — re-run only on *significant* change, not every edit ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]). Cheap (primitive) tests leave it default.

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — the `when::` index; [[FCT Ruleset]] — the `where::` index.
- [[Warden Architecture]] — how dispatch is compiled (incl. the resident-Python implementation, §7a).
- [[Warden Examples]] — every kind of test + action, as complete rules.
