---
description: "how the engine runs a rule — IF (dispatch indexes + a condition) THEN (actions)"
---
# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model — kept small: **a rule is `IF` a condition `THEN` an action.** The engine dispatches to a rule cheaply (by moment + file), evaluates its condition, and on a hit performs its action(s).

> [!todo] Open threads (everything here is in flux — park items so we don't forget)
> - **Sync `Warden Rule`** (format spec) to this model — it still has `check::`/tiers, and defaults a clause-less rule to `where:: always` (now the **ambient** case).
> - **Sync `Warden Architecture` §7** with the two-path `ask_oracle` mechanism (oracle on audit / steer on live).
> - **`run` action** — trust/security model before it ships (deferred).
> - **The `edit` family** — define the method set (`set_frontmatter`, `replace_section`, …) and the never-delete floor it rides on.
> - **`ask_oracle(prompt) → str`** — settled: **one prompt arg in, a `str` out** (it's an LLM — text in, text out; merge material into the prompt, parse the reply if you need structure). Vocabulary settled too (**the agent** = steered, **the oracle** = the spawned context-less helper). Still open: whether F215's economy gate wants the material as a separate diffable arg after all.
> - **`file.frontmatter`** — confirm merging YAML block + inline `::` fields is what we want.

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

**The test (`if::`) is a Python expression** — there's **no condition DSL, not even a vocabulary of predicates.** it reads the **data nouns** on `file` / `anchor` / `event` (§ *What a rule sees*) — `file.title`, `file.frontmatter`, `file.text`, `file.sections`, `event.command` — and you write the **predicate in plain Python** (`not`, `in`, `re.search`). No `.has`/`.matches` verbs baked into the API:

```
if:: not file.title                        # no H1 title
if:: 'description' not in file.frontmatter # no description
```

(A value that contains `::` gets **backticked**, per [[F007 — Backtick all where expressions — parser swap|F007]], so Dataview doesn't choke on it.) Or **prose**, when the test needs judgment — the LLM reads the `file` and decides. (For a computed, per-violation test, skip `if::` and write a body **snippet** that conditions and tells inline — § THEN.) Either way a test yields **findings** (each a message) or a boolean. To make a judgment cheap, narrow it in Python: **`ask_oracle(f'…{slice}')`** runs a fresh **oracle** over just that slice and returns its prose answer, which you `tell` — and a bare-prose judgment is simply the sugar for `tell(ask_oracle(<the prose + file.text>))`. (No `focus::` clause; you merge the slice into the prompt string.)

## `THEN` — the actions

On a hit, the rule performs zero or more actions. Three are **mediated** — Warden controls exactly what each does, so they're safe even in a rule you didn't write — and one is the **unmediated**, *deferred* escape hatch:

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — the test found no problem | — |
| **tell** | **bare prose** — or `tell(msg)` | say something to the agent — a problem *or* a directive ("commit now", "don't ask the user") | a **steer** injected into the agent's context (live) · a **finding** in the report (audit) |
| **edit** | a method on `file` — `file.set_frontmatter(…)`, `file.replace_section(…)`, … | write to a file — repair, stamp metadata, append a log | the file(s) — gated by the never-delete floor |
| **deny** | `deny(reason)` | block the pending action | the tool call — `tool:pre` only |
| **run** *(future)* | the Python body, directly | arbitrary execution — run commands, drive Warden / other agents | **deferred** — needs a security model first |

**A bare prose body *is* the tell.** When the action is just "tell the agent this," you write the prose — no keyword (the `tell` payload is the whole point). For anything more, the body is **Python, marked by backticks** — an inline `` `expr` `` for a one-liner, a bare ` ``` ` fence for several lines (**no `python` tag — backticked means Python**). `file` / `anchor` / `event` and the verbs are in scope; no `def`, no function name; it calls `tell` / `file.set_frontmatter` / `deny`. (`message:: <text>` is the sugar for a fixed prose tell; a *fix* is an `edit` that repairs a violation.) **Emit nothing → the rule passed.**

> **The one lexical rule: backticks = Python.** A backticked `if::` value, a backticked one-line body, a fenced block — all are Python run by the engine; un-backticked prose is the `tell`. (It also subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

**Data vs. actions — the split is load-bearing for readability.** The **data** is read-only nouns on `file` / `anchor` / `event` — `file.text`, `file.title`, `file.frontmatter`, `event.command`, `file.section(…)` (and `ask_oracle`, which reads *via* a fresh oracle) — they *look*, never change anything. The **actions** are the only things that *do* — `tell`, `deny`, and the `file.set_*` / `file.replace_*` edits. A name should never blur the two (e.g. inspecting `event.command` reads the pending command; nothing *runs* it).

**What `tell` actually does.** **Live** → text the hook injects into the agent's context (what you'd picture as "printed to the agent" — the F180 steer); **audit** → a finding written into the report the user reads. Same `tell`; the trigger picks the channel.

**Calling `tell` many times** (e.g. once per finding in a loop, as R-ex-02 does) **accumulates** — they don't each fire separately. Live, the messages are **joined newline-separated into one steer block**, so the agent sees all of them at once; under audit, each is a **separate finding** (its own row/bullet). Zero `tell`s over the whole body = the rule passed.

**Mediated vs. unmediated.** The three mediated actions (**tell · edit · deny**) are a **closed, small set**, so the body just *calls* the one it wants — **no test × action cross-product, no action language to invent.** `run` is the exception (arbitrary Python = arbitrary code execution, incl. controlling Warden or other agents) and is **deferred** — see [[Warden PRD]] § Security and the open question below.

> **Open — `run`'s trust model.** Your own rules are as trusted as your own scripts, so unbounded effect is arguably fine; an *imported* ruleset carrying effectful Python is a **supply-chain risk** (adopting it runs its code on your moments). Leaning: **ship the mediated three first; add `run` only behind explicit trust, off for imported rules.**

## What a rule sees — `file`, `anchor`, `event`

A rule body runs with **three objects in scope** — the three things the rule matched on — plus the action verbs. No `ctx.` prefix: they're aliased in directly (under the hood they're `ctx.file` / `ctx.anchor` / `ctx.event`, but you write them bare).

**`file`** — the matched file (from `where::`, or a file-bearing moment like `write:*`; a command-only moment like `tool:pre:Bash` has **no** `file`):

| Member | What it is |
|---|---|
| `file.path` · `file.name` | path · basename |
| `file.text` · `file.lines` | full text · list of lines |
| `file.title` | the H1 title (or `None`) |
| `file.frontmatter` | the file's metadata — YAML block **and** Dataview `::` inline fields, merged (as Dataview sees them) |
| `file.section("## X")` · `file.sections(level=N)` | one section · the sections |
| `file.links` | the wiki / markdown links |

**`anchor`** — the anchor the rule is operating in:

| Member | What it is |
|---|---|
| `anchor.name` · `anchor.root` | RID · root path |
| `anchor.traits` | its traits |
| `anchor.branch` · `anchor.git_aspect` | current branch · git mode (`Commit`, …) |

**`event`** — the moment (from `when::`; **live runs only** — absent under `/audit`):

| Member | What it is |
|---|---|
| `event.kind` | the moment that fired (`write:markdown`, …) |
| `event.diff` | what changed (write moments) |
| `event.command` | the pending / just-run command (Bash moments) |
| `event.tool` | the tool name + input (tool moments) |

**The verbs**, bare in scope: the **actions** **`tell(msg)`** · **`deny(reason)`** and the `file.set_*` / `file.replace_*` **edits**; plus **`ask_oracle(prompt) → str`** — *hand a fresh **oracle** (a context-less helper LLM) a prompt, get its text answer back* (a reader, not an action); merge any material into the prompt yourself (`f'…{file.section(…)}'`).

**The environment** — a body is **plain Python**: every builtin (`len`, `any`, `in`, `for`, `str`, …) and a safe stdlib subset (`re`, `json`, `datetime`) are available, no import needed for the common ones. On top of that, Warden injects the three objects, the verbs, and two ambient values:

| Name | What it is |
|---|---|
| `today` | the current **date** — evaluated at run; serializes to ISO (`2026-06-28`) when written to frontmatter |
| `now` | the current **datetime** (timestamp) |

So `file.set_frontmatter('reviewed', today)` writes `reviewed: 2026-06-28`. (Which stdlib modules are reachable is bounded by the sandbox — same trust question as `run`; the reference impl is permissive, the hot-path interpreter restricted.)

- **Three objects, not one bag — and they mirror the clauses.** `where::` → `file`, the adopting anchor → `anchor`, `when::` → `event`. "Event," **not** "action": *action* is the rule's *output* (`tell` / `edit` / `deny`), so reusing the word would muddle the two.
- **`ask_oracle` runs a *separate* LLM — the oracle — never the agent's own model.** A hook is a synchronous subprocess (event in → output → exit); it can't block-and-await the agent's model. So `ask_oracle` spawns a **fresh headless oracle** — *context-less*, it sees only the **prompt** you pass — and returns its answer as a **string** (it's an LLM — text in, text out; merge material into the prompt, and parse the reply yourself if you need structure): on the **audit path** (not latency-bound) the pipeline blocks on it and parses the answer — its real home; on the **live path** (hot hook, ms-budget) it can't block, so the call is **delegated to the agent as a steer** instead. Because the oracle is context-less, the prompt must say *how* to answer so the result is usable; the body then `tell`s the reply. A bare-prose body is the sugar for `tell(ask_oracle(<the prose, with file.text>))`. (Mechanism: [[Warden Architecture]] §7.)
- **Small on purpose.** When a member is missing, reach for `file.text` + the Python stdlib — not a new method. The accessors exist only because re-parsing markdown structure by hand would be worse; they expose *data*, never hide a check.
- **A reading LLM understands these** — ordinary nouns it's seen in thousands of APIs; `file.sections(level=2)` plainly means "the level-2 sections." That's the dual-use payoff: the names that *run* the rule also let a reader *understand* it.

## The pipeline

```
on trigger:  a when:: moment fires,  OR  /audit visits an anchor
  candidates = rules whose where:: (and when::) INDEXES match   # cheap, no code
  for each candidate rule, for each file T it matches:
    if a cached result for (rule, T) is fresh under rerun:::  reuse it
    else:  evaluate if:: over file(T)  → findings (or false)
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
