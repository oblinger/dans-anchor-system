---
description: "how the engine runs a rule — a rule as condition + body (of actions), what a body sees and emits, and the evaluation pipeline"
---
# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model — kept deliberately small: **a rule is a condition and a body, and the engine runs the body when the condition holds.**

## A rule is a condition and a body

A rule is **IF a condition THEN a body** — a production rule:

| Half | Parts | Says |
|---|---|---|
| **Condition** (the *if*) | `when::` · `where::` · `if::` | *when* the rule activates · over *which* files · *only if* a guard holds |
| **Body** (the *then*) | one or more **actions** | *what it does* when the condition holds |

Plus its **name** (`R-<slug>-NN`) and an optional `rerun::` modifier (below). That is the whole rule — there is no separate *evaluator*, *outcome*, *tier*, or *economy* concept; each was extra vocabulary for something the body already does.

When the condition holds for a file, the body runs over it and may **report** problems. A rule **passes** on a file when its body reports nothing.

## The body — actions

The body is one or more **actions**, run in order. An action is one of:

| Action | Written as | What it does |
|---|---|---|
| **check** | `check:: <primitive>` | run a named library checker; report a problem if it finds one |
| **code** | a `python` block — `def check(ctx)` | arbitrary logic: inspect `ctx`, call `ctx.report(msg, fix=…)` on a problem |
| **judgment** | **prose** in the body | the LLM reads `ctx` and reports the problems it finds |
| **message** | `message:: <text>` | report this text unconditionally — a steer to the agent (F180's shape) |
| **fix** | a `fix=` on any report | a repair Warden applies, gated by the never-delete floor |

`python` is the general form; `check::`, `message::`, and prose are the common shapes of it. A judgment that wants to stay cheap puts a `python def prepare(ctx)` action *first* to hand the LLM only the slice it needs — **script-assisted** (two actions: prepare, then judge). A rule can mix actions (e.g. a check plus a custom `message::`).

> **On the old tiers.** `(checked)` / `(stated)` / `(sampled)` / `(tracked)` are **not** a separate concept — the body already shows whether a script (`check::` / `python`) or the LLM (prose) decides, so a tier label just restates it. Dropped from the core model. (Coverage ideas like "sample expensive rules" are a future scheduling policy, not part of a rule's identity.)

## What a body sees and emits

**`ctx`** — the file under evaluation:
`ctx.path` · `ctx.text` · `ctx.lines()` · `ctx.frontmatter` · `ctx.section("## X")` · `ctx.sections(level=N)` · `ctx.anchor` · `ctx.git_aspect`. A `when::`-triggered body also gets the event payload (e.g. `ctx.diff` for a `write:*` moment).

**A report** — `ctx.report("message", fix=optional)`. **Zero reports = the rule passed** on this file. Each report becomes a **steer** to the agent (when the rule fired live) or a **finding** in the report (when it ran under audit); its `fix`, if present and safe, is applied. (A `check::` primitive and LLM prose report through the same channel — they're just bodies that haven't been written out as Python.)

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

Everything else fills in the **body**, the **condition**, and **`rerun::`**.

## Live vs. passive

- A rule with a `when::` fires **live** at that moment — the fast guardrail.
- A rule with **no `when::` is passive** — it runs only when `/audit` visits its `where::` files — the thorough backstop. (Live rules are also re-checked by audit.)
- **`where::` is always required**; `when::` and `if::` are optional. `when::` → [[Warden Trigger Taxonomy]]; `where::` → [[FCT Ruleset]] § Where clause.

## Re-running an expensive body

A body that calls the LLM costs tokens, so its result is cached by file-content-hash and reused until the file changes. **`rerun:: significant`** relaxes that — re-run only on *significant* change, not every edit ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]). Cheap (script) bodies leave it default (re-run whenever).

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — the `when::` moment; [[FCT Ruleset]] — the `where::` selector.
- [[Warden Architecture]] — how the pipeline is compiled + scheduled.
- [[Warden Examples]] — every kind of action, as a complete rule conforming to this page.
