---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, ten complete rules. A rule is **`IF` a condition `THEN` an action** — and these show every shape: a prose tell, a Python test, an LLM judgment, a script-assisted judgment, an `edit`, a `deny`, a shell (`sh`) condition, a Python `run`, a shell `run`, and sensing `agent` state. How the engine runs them is [[Warden Semantics]]; this is the tour.

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

When a regex won't do, the body is a bare `python` **snippet** (no `def`, no magic name — `file` / `anchor` / `git` / `event` are in scope): it walks every H2 section and `tell(...)`s each empty one — one finding, with its own message, per violation. Note the **`description::`** field: the rule's *meaning / goal* — **not sent on rule fire**, but the rule's intent for a reader, so a Python rule still reads as a sentence (the dual-use / North-Star promise; same field rulesets carry). The `tell()` calls are what actually reach the agent.

## 03 · An LLM judgment

![[Warden Example judgment.svg]]

Also just prose — but prose that states an *expectation* ("Summary should reflect Design"). The LLM reads the `file`, judges, and tells what drifted. Same shape as R-ex-01; the difference is the LLM evaluates it. **No `when::` is deliberate**: an LLM judgment is expensive, so it runs **passively at `/audit`**, re-checked only when the file's content changed (the verdict is cached until then). Firing it live on every write would be the wrong trade — `when::` + `rerun:: significant` is how you'd opt into live, throttled.

## 04 · Script-assisted

![[Warden Example script-assisted.svg]]

The crux of using an oracle: it's **context-less** — it sees only your prompt, the agent sees only what *you* `tell`. So don't make the oracle write the steer; give it the **narrow** job (identify *which* are answered elsewhere, reply `"none"` if none) and let the **rule** author the directive ("close or move to Resolved"). Code gates on the `"none"` sentinel — so the agent gets a consistent, controlled instruction, and a clean pass when there's nothing to say. **LLM for the judgment, code for the control flow and the directive** — the general idiom for using the oracle well.

## 05 · An `edit`

![[Warden Example edit.svg]]

Not every rule tells — some just *do*. On every write to an architecture doc this one stamps a reviewed-date via `file.set_frontmatter('reviewed', today)` and says nothing. Edits are **methods on `file`** (`set_frontmatter`, `replace_section`, …) — each a flavor of the `edit` action, not a whole-file replace — readable as code and floor-gated against content loss. A "fix" is just an `edit` that repairs a violation.

## 06 · A `deny`

![[Warden Example deny.svg]]

The one rule that *blocks*. On `when:: tool:pre:Bash` it inspects `event.command` and the **`git`** object (auto-resolved to the command's repo) and `deny(...)`s a force-push to main before it runs — the veto. `deny` only makes sense at a `tool:pre` moment (a command, not a file, so `where::` doesn't apply).

## 07 · `sh` in a condition

![[Warden Example sh-cond.svg]]

A condition can shell out: `if:: sh(['markdownlint', file.path])` runs the linter and is truthy when it reports anything (→ the prose `tell` fires). No `when::` on purpose — a subprocess is expensive, so it belongs at audit, like an oracle judgment. **argv-form** (a list) means `file.path` can't inject a shell command. For a *cheap* state check, prefer a data accessor (`git.is_dirty`); `sh` is for when there's no accessor.

## 08 · A Python `run`

![[Warden Example run-python.svg]]

Beyond the mediated verbs, a body is just Python — a **`run`**. This one appends to an audit log with plain `open(...).write(...)`. Arbitrary effects are the **same trust class as a skill** (it's your code), so the `description::` line carries the meaning and the Python carries the doing.

## 09 · A shell `run`

![[Warden Example run-shell.svg]]

The shell flavor of a `run`: `sh(['black', '-q', file.path])` formats the file in place on every write. Same trust as a skill; argv-form blocks injection. (`sh` returns output too, so the same call serves a condition — § 07.)

## 10 · Sensing agent state

![[Warden Example agent-state.svg]]

Rules can sense the **agent** itself. On `when:: prompt:stop` (the agent returns) this checks `agent.state == 'asking'` and nudges it to record the open question. `agent.state` (`working` / `landed` / `asking` / `idle`) is *sensed* in `if::`; the turn boundary is the *moment*. Same trigger-vs-sense split as a file change (the `write:*` moment vs `event.diff`).

> [!info] Status — designed, not all built
> The prose-tell and `python`-tell shapes (F180's executable rules) are the established core. The `ask_oracle` narrowing, the `edit` / `deny` actions, `sh` / `run` effects, the `agent` object, and the `rerun:: significant` gate are designed but not all built ([[Warden Roadmap]]; economy gate = M7, [[F215 — Re-evaluation economy — the significant-edit gate|F215]]). `run` / `sh` effects are real Python — the **same trust class as a skill** (vet imported rulesets), not a sandbox question.

## Rule of thumb

Write the **tell as plain prose** — it's the payload, and it's the documentation. Reach for `python` only when the message is computed, the test is beyond a regex, or the action is an `edit`/`deny`. Bind with `where::`; add `when::` only when it should fire live.
