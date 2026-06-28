---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, six complete rules. A rule is **`IF` a condition `THEN` an action** — and these show every shape: a plain-prose tell, a Python test, an LLM judgment, a script-assisted judgment, an `edit`, and a `deny`. How the engine runs them is [[Warden Semantics]]; this is the tour.

![[Warden Examples Ruleset.svg]]

*The example ruleset.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## How to read these rules

Every rule binds with `where::` (which files) and optionally `when::` (which moment); then a condition and an action. Two facts ([[Warden Semantics]] has the pipeline):

- **A bare prose body *is* the tell.** When the action is just "tell the agent this," you don't write `tell` — the prose *is* the message (R-ex-01, R-ex-03). `edit` and `deny` (and an explicit `tell`) are calls in **backticked Python** — `tell` / `deny` bare, `file.set_frontmatter(…)` for an edit.
- **A rule sees three objects** — `file` (the matched file), `anchor` (its project), `event` (the live moment) — plus the verbs `tell` / `deny` / `ask_oracle`. Read members as `file.text`, `event.command`, `anchor.branch`.
- **Backticks = Python.** A backticked `if::`, an inline one-line body (`` `file.set_frontmatter(…)` ``, R-ex-05), or a bare ` ``` ` fence (R-ex-02/04/06) — all are Python the engine runs; **no `python` tag**. Un-backticked prose is the `tell`.
- **No `when::` means passive.** R-ex-01…04 run when **`/audit`** visits their files; R-ex-05/06 declare a `when::` and fire **live**.
- **`where::` is anchor-relative.** `**/*.md` means "every markdown file *in the anchor that adopts this rule*" — no `{ANCHOR}/` needed; that's why one rule is reusable across anchors.
- **No condition DSL.** `if::` is plain Python over the `file` / `anchor` / `event` data (`file.frontmatter`, `event.command`, `file.section`) — read-only nouns; only `tell` / `deny` / `file.set_*` act.

## 01 · A prose tell

![[Warden Example prose.svg]]

The whole body is one line of prose — *that's the tell.* `if::` is a one-line Python condition — `'description' not in file.frontmatter` — plain Python (`in`, `not`) over the **`file`** metadata, with no invented predicate verbs. When it holds, the prose lands in front of the agent. This is the common shape, and it doubles as documentation: read it and you know the convention, no engine required.

## 02 · A Python test (tells per finding)

![[Warden Example python.svg]]

When a regex won't do, the body is a bare `python` **snippet** (no `def`, no magic name — `file` / `anchor` / `event` are in scope): it walks every H2 section and `tell(...)`s each empty one — one finding, with its own message, per violation. `tell` is the same action as a prose body; here it's called from code because the message is computed.

## 03 · An LLM judgment

![[Warden Example judgment.svg]]

Also just prose — but prose that states an *expectation* ("Summary should reflect Design"). The LLM reads the `file`, judges, and tells what drifted. Same shape as R-ex-01; the difference is the LLM evaluates it rather than a primitive. (Judgments cost tokens, so Warden caches the verdict until the file changes.)

## 04 · Script-assisted

![[Warden Example script-assisted.svg]]

The expensive part of a judgment is reading the whole file. So narrow it: `ask_oracle(question, file.section('## Open Questions'))` hands a fresh **oracle** (a context-less helper LLM) just that slice and returns a list — assigned to `resolved`, so the loop is obvious. The body then **shapes** each into a `tell` the agent can act on (you control the message, not the oracle). No `focus` clause — the slice is just an argument; it's the same call a bare-prose judgment desugars to over the whole `file`. **Python narrows, the oracle answers, the body phrases the steer.**

## 05 · An `edit`

![[Warden Example edit.svg]]

Not every rule tells — some just *do*. On every write to an architecture doc this one stamps a reviewed-date via `file.set_frontmatter('reviewed', today)` and says nothing. Edits are **methods on `file`** (`set_frontmatter`, `replace_section`, …) — each a flavor of the `edit` action, not a whole-file replace — readable as code and floor-gated against content loss. A "fix" is just an `edit` that repairs a violation.

## 06 · A `deny`

![[Warden Example deny.svg]]

The one rule that *blocks*. On `when:: tool:pre:Bash` it inspects `event.command` and `deny(...)`s a force-push to main before it runs — the veto. `deny` only makes sense at a `tool:pre` moment (a command, not a file, so `where::` doesn't apply).

> [!info] Status — `ask_oracle`, `edit`, `deny`, and `rerun::` are *designed, not all built*
> The prose-tell and `python`-tell shapes (F180's executable rules) are the established core. The `ask_oracle` narrowing, the `edit`/`deny` actions, and the `rerun:: significant` gate are on the [[Warden Roadmap]] (M7 for the economy gate, [[F215 — Re-evaluation economy — the significant-edit gate|F215]]). The `run` (arbitrary-effect) action is **deferred** pending a security model.

## Rule of thumb

Write the **tell as plain prose** — it's the payload, and it's the documentation. Reach for `python` only when the message is computed, the test is beyond a regex, or the action is an `edit`/`deny`. Bind with `where::`; add `when::` only when it should fire live.
