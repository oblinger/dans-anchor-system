---
description: "worked examples — every kind of test and action, as complete rules (start here)"
---
# Warden Examples

One worked ruleset, six complete rules. A rule is **`IF` a condition `THEN` an action** — and these show every shape: a plain-prose tell, a Python test, an LLM judgment, a script-assisted judgment, an `edit`, and a `deny`. How the engine runs them is [[Warden Semantics]]; this is the tour.

![[Warden Examples Ruleset.svg]]

*The example ruleset.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How to read these rules

Every rule binds with `where::` (which files) and optionally `when::` (which moment); then a condition and an action. Two facts ([[Warden Semantics]] has the pipeline):

- **A bare prose body *is* the tell.** When the action is just "tell the agent this," you don't write `tell` — the prose *is* the message (R-ex-01, R-ex-03). `edit` and `deny` (and an explicit `tell`) are `ctx.*` calls inside a `python` body — readable code the agent can follow.
- **No `when::` means passive.** R-ex-01…04 run when **`/audit`** visits their files; R-ex-05/06 declare a `when::` and fire **live**.

## 01 · A prose tell

![[Warden Example prose.svg]]

The whole body is one line of prose — *that's the tell.* `if:: absent` is the condition (a fast primitive), and when it holds the prose lands in front of the agent. This is the common shape, and it doubles as documentation: read it and you know the convention, no engine required.

## 02 · A Python test (tells per finding)

![[Warden Example python.svg]]

When a regex won't do, the body is `python`: `def check(ctx)` walks every H2 section and `ctx.tell(...)`s each empty one — one finding, with its own message, per violation. `ctx.tell` is the same action as a prose body; here it's called from code because the message is computed.

## 03 · An LLM judgment

![[Warden Example judgment.svg]]

Also just prose — but prose that states an *expectation* ("Summary should reflect Design"). The LLM reads `ctx`, judges, and tells what drifted. Same shape as R-ex-01; the difference is the LLM evaluates it rather than a primitive. (Judgments cost tokens, so Warden caches the verdict until the file changes.)

## 04 · Script-assisted

![[Warden Example script-assisted.svg]]

The expensive part of a judgment is reading the whole file. A cheap `def focus(ctx)` hands the LLM only the slice it needs (`## Open Questions`); the prose then judges *that*. **Python narrows, the LLM judges** — the cheapest way to do a judgment.

## 05 · An `edit`

![[Warden Example edit.svg]]

Not every rule tells — some just *do*. On every write to an architecture doc this one stamps a reviewed-date via `ctx.edit(...)` and says nothing. `edit` is a `ctx.*` call (readable as code, floor-gated against content loss); a "fix" is just an `edit` that repairs a violation.

## 06 · A `deny`

![[Warden Example deny.svg]]

The one rule that *blocks*. On `when:: tool:pre:Bash` it inspects the pending command and `ctx.deny(...)`s a force-push to main before it runs — the veto. `deny` only makes sense at a `tool:pre` moment (a command, not a file, so `where::` doesn't apply).

> [!info] Status — script-assisted `focus()`, `edit`, `deny`, and `rerun::` are *designed, not all built*
> The prose-tell and `python`-tell shapes (F180's executable rules) are the established core. The `focus()` hand-off, the `edit`/`deny` actions, and the `rerun:: significant` gate are on the [[Warden Roadmap]] (M7 for the economy gate, [[F215 — Re-evaluation economy — the significant-edit gate|F215]]). The `run` (arbitrary-effect) action is **deferred** pending a security model.

## Rule of thumb

Write the **tell as plain prose** — it's the payload, and it's the documentation. Reach for `python` only when the message is computed, the test is beyond a regex, or the action is an `edit`/`deny`. Bind with `where::`; add `when::` only when it should fire live.
