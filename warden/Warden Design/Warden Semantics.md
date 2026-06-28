---
description: "how the engine runs a rule — a rule as IF (condition) THEN (body of actions), expanded into the if and the then"
---
# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model — kept deliberately small: **a rule is `IF` a condition `THEN` a body, and the engine runs the body when the condition holds.** When the body runs over a file it may `report` problems; a rule **passes** on a file when its body reports nothing.

## A rule at a glance

![[Warden Rule Anatomy.svg]]

Every clause a rule can carry — the `IF` clauses are the **condition**, the `THEN` clauses are the **body**:

| Clause               | What it does                                                             |
| -------------------- | ------------------------------------------------------------------------ |
| `where::`            | which files it runs over — **required** (default `always`)               |
| `when::`             | which moment triggers a **live** run — omit → *passive* (audit-time)     |
| `if::`               | an extra state guard (`git-aspect == Commit`, …)                         |
| `check::`            | run a named library **primitive**; report a problem if it finds one      |
| `python` *(code)*    | a `def check(ctx)` block — arbitrary logic; `ctx.report(…)` on a problem |
| *prose* *(judgment)* | the **LLM** reads `ctx` and reports the problems it finds                |
| `message::`          | report a fixed **steer** to the agent (F180's shape)                     |
| `fix=`               | a repair applied on a report (gated by the never-delete floor)           |

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

**What a body can do — the actions.** A body inspects `ctx` and performs zero or more of these. This is the *whole* set of things that can happen:

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — no problem found | — |
| **report** | `ctx.report(msg)` | surface a problem | a **finding** (audit) or a **steer** to the agent (live) — *the moment decides which* |
| **fix** | `ctx.fix(edit)` / `fix=` | apply a repair to the file | the file — gated by the never-delete floor |
| **deny** | `ctx.deny(reason)` | block the pending action | the tool call — only at a `tool:pre` moment |

Because the set is **closed and small**, the body just *calls* the action it wants — there's **no test × action cross-product** and no action language to invent. A bare `check::` implies **report**; `message:: <text>` is sugar for a body whose one action is a fixed report; a rule that also repairs adds a `fix`. **Zero actions = the rule passed.**

**What a body sees** — `ctx` is the file under evaluation: `ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered body also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

> **On the old tiers.** `(checked)` / `(stated)` / `(sampled)` / `(tracked)` are **not** a separate concept — the body already shows whether a script (`check::` / `python`) or the LLM (prose) decides. An optional posture hint at most; nothing in the engine requires it.

## The pipeline

```
on trigger:  a when:: moment fires,  OR  /audit visits an anchor
  for each file T matching the rule's where:::
    if any if:: guard is false:  skip
    if a cached result for (rule, T) is fresh under rerun:::  reuse it
    else:  run the body over ctx(T)  → a list of reports
           cache it by (rule, hash(T)[, model])
    for each report:  deliver it (steer if live, finding if audit);  apply its fix if safe
```

## Re-running an expensive body

A body that calls the LLM costs tokens, so its result is cached by file-content-hash and reused until the file changes. **`rerun:: significant`** relaxes that — re-run only on *significant* change, not every edit ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]). Cheap (script) bodies leave it default (re-run whenever).

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — the `when::` moment; [[FCT Ruleset]] — the `where::` selector.
- [[Warden Architecture]] — how the pipeline is compiled + scheduled.
- [[Warden Examples]] — every kind of action, as a complete rule conforming to this page.
