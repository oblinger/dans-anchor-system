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

The body is one or more **actions**, run in order. An action is one of:

| Action | Written as | What it does |
|---|---|---|
| **check** | `check:: <primitive>` | run a named library checker; report a problem if it finds one |
| **code** | a `python` block — `def check(ctx)` | arbitrary logic: inspect `ctx`, `ctx.report(msg, fix=…)` on a problem |
| **judgment** | **prose** in the body | the LLM reads `ctx` and reports the problems it finds |
| **message** | `message:: <text>` | report this text unconditionally — a steer to the agent (F180's shape) |
| **fix** | a `fix=` on any report | a repair Warden applies, gated by the never-delete floor |

`python` is the general form; `check::`, `message::`, and prose are common shapes of it. A judgment that wants to stay cheap puts a `python def prepare(ctx)` action *first* to hand the LLM only the slice it needs — **script-assisted** (two actions: prepare, then judge). A rule may mix actions.

**What a body sees** — `ctx` is the file under evaluation: `ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered body also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

**What a body emits** — `ctx.report("message", fix=optional)`. **Zero reports = the rule passed.** Each report becomes a **steer** to the agent (when the rule fired live) or a **finding** in the report (under audit); its `fix`, if present and safe, is applied. (A `check::` primitive and LLM prose report through the same channel — they're just bodies not written out as Python.)

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
