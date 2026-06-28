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
| `where::` | **index** (glob) | which files — **anchor-relative**; required for a *passive* rule, optional for a live one; [[FCT Ruleset]] § Where clause |
| `when::` | **index** (moment) | which live moment — omit → *passive*; [[Warden Trigger Taxonomy]] |
| `if::` | **test** (computed) | the condition — a Python expression, or prose (below) |

**`where::` is anchor-relative.** A glob resolves under whatever anchor *adopts* the rule — `**/*.md` means "every markdown file in this anchor." That's why one rule is reusable across anchors. The explicit `{ANCHOR}/` token is optional (clearer in shared rulesets); a bare glob is equivalent.

**A rule needs at least one of `where::` / `when::` to be *dispatched*** — that's how Warden finds it at the right place/moment. The combinations:

| `where::` | `when::` | what it is |
|---|---|---|
| ✓ | — | **passive** — runs at `/audit` over those files (R-ex-01…04) |
| — | ✓ | **live** at a moment; the subject is the *event* (a command, a session). File data only if the moment is file-bearing (R-ex-06: `tool:pre:Bash` — a command, no file) |
| ✓ | ✓ | **live** at the moment, scoped to the file (R-ex-05) |
| — | — | **ambient** — see below |

**The ambient rule (no `where::`, no `when::`) is legal — and it's the weakest form.** With no dispatch key, Warden can't deliver it at the right moment (its whole superpower), so it falls back to the only option left: **always loaded into the agent's context** — the CLAUDE.md model, where "the LLM just has to remember it," competing for attention with everything else. Use it only for guidance that genuinely can't be pinned to a file or a moment; otherwise add a clause so Warden can do its job. *(Distinct from `where:: always`, which is an explicit "every file" scope that Warden still dispatches — at audit, over everything.)*

**Why `if` stays separate from `when`.** `when`/`where` are *indexical* — clean tokens (`write:markdown`, `*.md`) the compiler matches without execution. `if` is *computed*. Folding `if` into `when` would either uglify the simple `when` clause or mix a dispatch index with computation, so they stay apart.

**The test (`if::`) is a Python expression** — there's **no condition DSL, not even a vocabulary of predicates.** `ctx` exposes the file as **data (nouns)** — `ctx.title`, `ctx.fields`, `ctx.text`, `ctx.sections`, `ctx.command` — and you write the **predicate in plain Python** (`not`, `in`, `re.search`). No `ctx.has`/`ctx.matches`-style verbs baked into the API; the only irreducible primitive is `ctx` itself (the thing under test, like `self`):

```
if:: not ctx.title                     # no H1 title
if:: 'description' not in ctx.fields    # the description field is missing
```

(A value that contains `::` gets **backticked**, per [[F007 — Backtick all where expressions — parser swap|F007]], so Dataview doesn't choke on it.) Or **prose**, when the test needs judgment — the LLM reads `ctx` and decides. (For a computed, per-violation test, skip `if::` and write a body **snippet** that conditions and tells inline — § THEN.) Either way a test yields **findings** (each a message) or a boolean. To make a judgment cheap, narrow it in Python: **`ctx.judge(slice, 'question')`** runs the LLM over just that slice — and a bare-prose judgment is simply the sugar for `ctx.judge(<the whole doc>, <the prose>)`. (No `focus::` clause — the slice is just an argument; `ctx.judge` is an *inspector* that returns findings, and `tell` delivers them.)

## `THEN` — the actions

On a hit, the rule performs zero or more actions. Three are **mediated** — Warden controls exactly what each does, so they're safe even in a rule you didn't write — and one is the **unmediated**, *deferred* escape hatch:

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — the test found no problem | — |
| **tell** | **bare prose** — or `ctx.tell(msg)` | say something to the agent — a problem *or* a directive ("commit now", "don't ask the user") | a **steer** injected into the agent's context (live) · a **finding** in the report (audit) |
| **edit** | a specific method — `ctx.set_frontmatter(…)`, `ctx.replace_section(…)`, … | write to a file — repair, stamp metadata, append a log | the file(s) — gated by the never-delete floor |
| **deny** | `ctx.deny(reason)` | block the pending action | the tool call — `tool:pre` only |
| **run** *(future)* | the Python body, directly | arbitrary execution — run commands, drive Warden / other agents | **deferred** — needs a security model first |

**A bare prose body *is* the tell.** When the action is just "tell the agent this," you write the prose — no keyword (the `tell` payload is the whole point). For anything more, the body is **Python, marked by backticks** — an inline `` `expr` `` for a one-liner, a bare ` ``` ` fence for several lines (**no `python` tag — backticked means Python**). `ctx` is in scope; no `def`, no function name; it calls `ctx.tell` / `ctx.edit` / `ctx.deny`. (`message:: <text>` is the sugar for a fixed prose tell; a *fix* is an `edit` that repairs a violation.) **Emit nothing → the rule passed.**

> **The one lexical rule: backticks = Python.** A backticked `if::` value, a backticked one-line body, a fenced block — all are Python run by the engine; un-backticked prose is the `tell`. (It also subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

**`ctx` splits in two — and the split is load-bearing for readability.** **Inspectors** are read-only **data** — `ctx.text`, `ctx.title`, `ctx.fields`, `ctx.command`, `ctx.section(…)`, even `ctx.judge(slice, q)` (it reads via the LLM) — they *look*, never act (so the LLM reading `ctx.command` knows nothing runs). **Actions** are the only things that *do* — `ctx.tell`, the `ctx.edit`-family (`ctx.set_frontmatter`, `ctx.replace_section`, …), `ctx.deny`. A method name should never blur the two (e.g. `ctx.bash(…)` would wrongly read as "run bash" — inspect `ctx.command` instead).

**What `tell` actually does.** **Live** → text the hook injects into the agent's context (what you'd picture as "printed to the agent" — the F180 steer); **audit** → a finding written into the report the user reads. Same `ctx.tell`; the trigger picks the channel.

**Mediated vs. unmediated.** The three mediated actions (**tell · edit · deny**) are a **closed, small set**, so the body just *calls* the one it wants — **no test × action cross-product, no action language to invent.** `run` is the exception (arbitrary Python = arbitrary code execution, incl. controlling Warden or other agents) and is **deferred** — see [[Warden PRD]] § Security and the open question below.

> **Open — `run`'s trust model.** Your own rules are as trusted as your own scripts, so unbounded effect is arguably fine; an *imported* ruleset carrying effectful Python is a **supply-chain risk** (adopting it runs its code on your moments). Leaning: **ship the mediated three first; add `run` only behind explicit trust, off for imported rules.**

## What's in `ctx`

`ctx` is the one object every test and body receives — **the subject under test**: the file `where::` matched, the moment `when::` fired, and what's parsed from them. It's deliberately small, and every member is a plain noun (data) or verb (action), so a rule reads without a manual.

**Data — the file under test** (present *when a file is in scope* — a `where::` match, or a file-bearing moment like `write:*`; a command-only moment like `tool:pre:Bash` has **no** file data):

| Member | What it is |
|---|---|
| `ctx.path` · `ctx.name` | the file's path · basename |
| `ctx.text` · `ctx.lines` | full text · list of lines |
| `ctx.title` | the H1 title (or `None`) |
| `ctx.frontmatter` · `ctx.fields` | parsed YAML frontmatter · Dataview inline fields (dicts) |
| `ctx.section("## X")` · `ctx.sections(level=N)` | one section · the sections |
| `ctx.links` | the wiki / markdown links |
| `ctx.anchor` · `ctx.traits` | the anchor it lives in · its traits |

**Data — the moment** (from `when::`, on a live run only):

| Member | What it is |
|---|---|
| `ctx.event` | the moment that fired (`write:markdown`, …) |
| `ctx.diff` | what changed (write moments) |
| `ctx.command` | the pending / just-run command (Bash moments) |
| `ctx.tool` | the tool name + input (tool moments) |
| `ctx.git_aspect` · `ctx.today` | the git mode (`Commit`, …) · today's date |

**Actions** (the verbs — § THEN):

| Member | What it does |
|---|---|
| `ctx.tell(msg)` | steer the agent / file a finding |
| `ctx.set_frontmatter(…)` · `ctx.replace_section(…)` · … | the `edit` family |
| `ctx.deny(reason)` | block the pending tool |
| `ctx.judge(slice, question)` | **ask the LLM** — returns findings (the one member that costs tokens) |

- **`ctx.judge` is run by the LLM — as a *separate* model call, never by the hook listening in.** A hook is a synchronous subprocess (event in → output → exit); it can't block-and-await the conversation's model. So `ctx.judge` spawns a **fresh headless sub-agent** given *only* `slice` + `question`, and where it runs differs by path: on the **audit path** (not latency-bound) the pipeline blocks on that sub-call and parses its findings — `ctx.judge`'s real home; on the **live path** (hot hook, ms-budget) it can't block on a model, so the judgment is **delegated to the running agent as a steer** instead. A bare-prose body is just the sugar for `ctx.judge(<whole doc>, <the prose>)`; everything else is plain computation. (Mechanism: [[Warden Architecture]] §7.)
- **Small on purpose.** When a member is missing, reach for `ctx.text` + the Python stdlib — not a new method. The accessors exist only because re-parsing markdown structure by hand would be worse; they expose *data*, never hide a check.
- **Will a reading LLM understand `ctx.sections`?** Yes — they're ordinary nouns it's seen in thousands of APIs; `ctx.sections(level=2)` plainly means "the level-2 sections." That's the dual-use payoff: the names that *run* the rule also let a reader *understand* it.

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
