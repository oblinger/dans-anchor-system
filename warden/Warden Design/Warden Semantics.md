---
description: "Warden's operational semantics — how the engine turns a rule into a verdict (the evaluation pipeline, the evaluator, tiers, binding, outcome)"
---
# Warden Semantics

How the Warden engine actually *runs* a rule. [[Warden Rule]] is the file format; this page is the **operational** spec — the precise lifecycle of an evaluation, so a rule (and the [[Warden Examples]]) describes something a real engine could execute. Kept deliberately small: one pipeline, one evaluator abstraction, four tiers.

## A rule, completely

A complete rule is five things — three of them answer *whether to evaluate*, one answers *the verdict*, one answers *what to do about it*:

| Part | Field(s) | Answers |
|---|---|---|
| **Identity** | `R-<slug>-NN (tier)` | which rule, and its posture |
| **Binding** | `when::` · `where::` · `if::` | *when* it's evaluated · against *which* target · *only if* a guard holds |
| **Evaluator** | `check::` · `def check` · prose | how a verdict is produced from a target |
| **Outcome** | a message · optional `fix::` | what happens on fail |
| **Economy** | the tier · `rerun::` | how thoroughly / how often it runs |

A rule with only an evaluator and no `where::` is **incomplete** — it doesn't say what it runs against. Every rule binds.

## The evaluation pipeline

Warden evaluates one `(rule, target)` pair at a time. The trigger is either a **live moment** (the rule has a `when::`) or an **audit pass** (no `when::` → the rule is *passive*, run when `/audit` visits). Then the loop is the same:

```
on trigger:  a when:: moment fires,  OR  /audit visits an anchor
  targets = files matching the rule's where::          # which files
  for T in targets:
    if not every if:: guard holds for T:  continue      # guard
    if a cached verdict for (rule, T) is still fresh
       under the rule's rerun:: policy:  reuse it        # economy
    else:
       verdict = evaluate(rule, ctx(T))                  # the evaluator
       cache verdict keyed by (rule, hash(T)[, model])
    if verdict is Fail:
       emit verdict.message      # a steer (live) or a finding (audit)
       if the rule has fix:: and the fix is safe:  apply it
```

Everything else on this page just fills in **`evaluate`**, **`where::`/`when::`**, and **`rerun::`**.

## The evaluator — one abstraction, three ways to write it

Whatever its kind, **every rule defines one function `evaluate(ctx) → Verdict`**. The kinds are just three ways to write that function:

| Written as… | The evaluator is… | Runs on |
|---|---|---|
| `check:: <name> <args>` | a named **primitive** from the checker library | the fast native path |
| a ` ```python ` block `def check(ctx) -> Verdict` | **arbitrary Python** | the Python path |
| **prose** in the rule body | the **LLM** — the prose is its prompt; it reads `ctx` and judges | the agent |

A fourth is a *composition*, not a new kind: a ` ```python ` `def prepare(ctx) -> str` whose output is fed to the LLM prose — **script-assisted** (cheap Python narrows what the model has to read).

**`ctx`** — what an evaluator receives for a target `T`:

`ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered rule also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

**`Verdict`** — `Pass()` or `Fail("message")`. A primitive may return a bare bool (`True` = pass). The LLM returns pass/fail + a one-line reason that *becomes* the message.

## Tier = which evaluator class, run how often

This is the part that was muddled. The **tier** in the heading is not a separate thing from the evaluator — it is shorthand for *which class of evaluator, and how often it runs*:

| Tier | Evaluator class | Coverage |
|---|---|---|
| `checked` | a **script** — primitive *or* python (deterministic) | every pass, verdict-cached |
| `stated` | the **LLM** (judgment) | every pass, batched + cached |
| `sampled` | script where possible, else LLM | a risk-prioritized subset |
| `tracked` | **none** | recorded for awareness, never run |

So the tier and the body agree *by construction*: `(checked)` + a `check::` line is a primitive; `(checked)` + a `python` block is python; `(stated)` + prose is the LLM. **Writing `(checked · python)` was redundant** — `checked` already says "a script decides it," and the `python` block already says which script form. The heading carries only the tier; the body reveals the evaluator.

## Binding — live vs. passive

- **`where::`** — the target set. **Required** (default `always`). [[FCT Ruleset]] § Where clause.
- **`when::`** — the moment that triggers a *live* evaluation ([[Warden Trigger Taxonomy]]). **Omit it → the rule is passive**, evaluated only when `/audit` visits its `where::` targets. A live rule is *also* checked by audit (audit is the always-correct backstop; live firing is the fast guardrail).
- **`if::`** — an extra state guard ([[Warden Trigger Taxonomy]] § Guards).

## Outcome · caching · economy

- **Outcome.** `Fail` emits a **message** — a *steer to the agent* when the rule fired on a live `when::` moment, a *finding in the report* when it ran under audit — and, if the rule carries a `fix::`, applies the fix (gated by the never-delete floor, [[Warden Integration Strategy]] D5).
- **Caching.** Every verdict is cached by `(rule, target-content-hash[, model])`; an unchanged target reuses it (zero re-work).
- **`rerun::`.** Relaxes that cache invalidation for *expensive* (LLM) evaluators — re-evaluate only on *significant* change rather than any change ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]).

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — `when::`; [[FCT Ruleset]] — `where::`.
- [[Warden Architecture]] — how the pipeline is compiled + scheduled.
- [[Warden Examples]] — every kind, as a complete rule that conforms to this page.
