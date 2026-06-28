---
description: "how the engine runs a rule — a rule as IF (condition) THEN (body of actions), expanded into the if and the then"
---
# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model — kept deliberately small: **a rule is `IF` a condition `THEN` a body, and the engine runs the body when the condition holds.** When the body runs over a file it may `tell` the agent, `edit` a file, or `deny` an action; a rule **passes** when its body does none of these.

## A rule at a glance

![[Warden Rule Anatomy.svg]]

Every clause a rule can carry — the `IF` clauses are the **condition**, the `THEN` clauses are the **body**:

| Clause               | What it does                                                             |
| -------------------- | ------------------------------------------------------------------------ |
| `where::`            | which files it runs over — **required** (default `always`)               |
| `when::`             | which moment triggers a **live** run — omit → *passive* (audit-time)     |
| `if::`               | an extra state guard (`git-aspect == Commit`, …)                         |
| `check::`            | run a named library **primitive**; `tell` on a problem      |
| `python` *(code)*    | a `def check(ctx)` block — arbitrary logic; emits actions (`tell`/`edit`/…) |
| *prose* *(judgment)* | the **LLM** reads `ctx` and `tell`s what's wrong                |
| `message::`          | sugar for a fixed `tell` — a steer/directive (F180's shape)                     |
| `fix=`               | an `edit` that repairs a violation (never-delete floored)           |

Plus its **name** (`R-<slug>-NN`) and an optional `rerun::` modifier (below). That is the whole rule — there's no separate *evaluator*, *outcome*, *tier*, or *economy* concept; each was extra vocabulary for what these clauses already do. The two sections below expand each half.

## `IF` — the condition

The rule activates for a file when **all three** hold:

| Clause | Says | Required? |
|---|---|---|
| `where::` | which files it runs over | **yes** (default `always`) — [[FCT Ruleset]] § Where clause |
| `when::` | which moment triggers a *live* run | no — omit it and the rule is *passive* ([[Warden Trigger Taxonomy]]) |
| `if::` | an extra state guard (`git-aspect == Commit`, …) | no — [[Warden Trigger Taxonomy]] § Guards |

**Live vs. passive.** A rule **with** a `when::` fires **live** at that moment — the fast guardrail. A rule with **no `when::` is passive** — it runs only when **`/audit`** visits its `where::` files — the thorough backstop. (Live rules are also re-checked by audit.) `where::` is always required; `when::` and `if::` are optional.

## `THEN` — the body

The body says **what to do when the condition holds**. Two separate questions: *how the test/logic is written*, and *what it can actually do about a problem*. The second is a **small closed set** — which is exactly what keeps "test" and "action" from exploding into a cross-product.

**How the body is written** — one form, or a mix:

| Form | Written as | |
|---|---|---|
| **check** | `check:: <primitive>` | a named library check — fast, native |
| **code** | a `python` block — `def check(ctx)` | arbitrary logic |
| **judgment** | **prose** in the body | the LLM reads `ctx` and decides |

`python` is the general form; `check::` is a native-library shorthand for a common check; **script-assisted** = a `python def prepare(ctx)` then prose (cheap Python narrows what the LLM reads).

**What a body can do — the actions.** A body inspects `ctx` and performs zero or more actions. Three are **mediated** — Warden controls exactly what each does, so they're safe even in a rule you didn't write — and one is the **unmediated** escape hatch:

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — no problem found | — |
| **tell** | `ctx.tell(msg)` | say something to the agent — a problem *or* a directive ("commit now", "don't ask the user") | a **steer** injected into the agent's context (live) · a **finding** in the report (audit) |
| **edit** | `ctx.edit(path, change)` | write to a file — repair the target, append a log, drop data elsewhere | the file(s) — gated by the never-delete floor |
| **deny** | `ctx.deny(reason)` | block the pending action | the tool call — `tool:pre` only |
| **run** *(effect)* | the Python body, directly | arbitrary execution — run commands, spawn processes, drive Warden / other agents | **unmediated** — see below |

**`tell` is more than "report".** It isn't only "X is wrong" — a live `tell` can *direct* the agent (F180's steers do exactly this). Mechanically: **live** → text the hook injects into the agent's context (what you'd picture as "printed to the agent"); **audit** → a finding written into the report the user reads. Same `ctx.tell` call; the trigger picks the channel. (`message:: <text>` is sugar for a body whose one action is a fixed `tell`.)

**`edit` is more than "fix".** A `fix` is just an `edit` that *repairs a found violation* — but the same action writes a log line, stamps metadata, or drops data in another file. One action covers all mediated file writes (each floor-gated against content loss).

**Mediated vs. unmediated — and the cross-product.** The three mediated actions (**tell · edit · deny**) are a **closed, small set**, so the body just *calls* the one it wants — a bare `check::` implies a **tell**; a rule that changes a file uses an **edit** — **no test × action cross-product, no action language to invent.** The **run** action is the exception: the body is arbitrary Python, so it can do *anything*, including controlling Warden or other agents (the orchestration story) — which makes such a rule equal to arbitrary code execution. **Emit nothing → the rule passed.**

> **Open — is `run` allowed, and is the body sandboxed?** Your own rules are as trusted as your own scripts, so unbounded effect is arguably fine; but an *imported* ruleset carrying effectful Python is a **supply-chain risk** — adopting it runs its code on your moments. Leaning: **v1 = mediated actions only (`tell` / `edit` / `deny`); `run`/effect gated behind explicit trust and off for imported rules** (ties to [[Warden Integration Strategy]]).

**What a body sees** — `ctx` is the file under evaluation: `ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered body also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

> **On the old tiers.** `(checked)` / `(stated)` / `(sampled)` / `(tracked)` are **not** a separate concept — the body already shows whether a script (`check::` / `python`) or the LLM (prose) decides. An optional posture hint at most; nothing in the engine requires it.

## The pipeline

```
on trigger:  a when:: moment fires,  OR  /audit visits an anchor
  for each file T matching the rule's where:::
    if any if:: guard is false:  skip
    if a cached result for (rule, T) is fresh under rerun:::  reuse it
    else:  run the body over ctx(T)  → the actions it emits
           cache it by (rule, hash(T)[, model])
    carry out each action:  tell → steer (live) / finding (audit);   edit → apply if floor-safe;
                            deny → block the tool;   run → execute (if trusted)
```

## Re-running an expensive body

A body that calls the LLM costs tokens, so its result is cached by file-content-hash and reused until the file changes. **`rerun:: significant`** relaxes that — re-run only on *significant* change, not every edit ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]). Cheap (script) bodies leave it default (re-run whenever).

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — the `when::` moment; [[FCT Ruleset]] — the `where::` selector.
- [[Warden Architecture]] — how the pipeline is compiled + scheduled.
- [[Warden Examples]] — every kind of action, as a complete rule conforming to this page.
