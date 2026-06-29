---
description: "how the engine runs a rule — the condition, the actions, the runnable interpretation environment, and ruleset activation"
---

# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model. A rule is a **condition** and a set of **actions**. The engine resolves which rules are active for an anchor, dispatches the candidates cheaply (by moment and file), evaluates each candidate's condition, and on a hit performs its actions.

## A rule at a glance

![[Warden Rule Anatomy.svg]]

| Condition  | What it does                                                          |
| ---------- | --------------------------------------------------------------------- |
| `where::`  | which files it runs over — an anchor-relative glob (default `always`) |
| `when::`   | which moment triggers a **live** run — omit → *passive* (audit-time)  |
| `if::`     | the test — a Python expression, or prose for a judgment               |
|            |                                                                       |
| **Action** |                                                                       |
| `tell`     | say something to the agent — a steer (live) or a finding (audit)      |
| `edit`     | write to a file (`file.set_frontmatter`, …) — never-delete floored    |
| `deny`     | block the pending tool (`tool:pre` only)                              |
| `run`      | *(future)* arbitrary effects — deferred, pending a security model     |

## The condition — `where`, `when`, `if`

A rule activates for a target when **all of its present clauses hold**. `where::` and `when::` are **indexes** — matched without running any code, so dispatch is cheap. `if::` is the **computed test**, evaluated only after the indexes have narrowed the candidates.

### `where::` — which files

A path glob, resolved **relative to the anchor that adopts the rule**: `**/*.md` means "every markdown file in this anchor," which is what makes one rule reusable across anchors. **Required for a passive rule**; optional for a live one (the moment supplies the subject). Default `always`. A glob may use the `{ANCHOR}` / `{NAME}` / `{SLUG}` substitution tokens (§ Ambient and variables). Grammar: [[FCT Ruleset]] § Where clause.

### `when::` — which moments

The moment that fires the rule **live**. Omit it and the rule is **passive**: it runs only when `/audit` visits its `where::` files. The moments:

| Moment class           | Refinements                                                            | Fires on                            |
| ---------------------- | ---------------------------------------------------------------------- | ----------------------------------- |
| `tool` — `pre`/`post`  | `Bash`, `Write`, `Edit`, `Read`, `Glob`, `Grep`, `Task`, `WebFetch`, … | `PreToolUse` / `PostToolUse`        |
| `skill` — `pre`/`post` | any skill — `audit`, `query`, `crank`, …                               | skill enter / exit                  |
| `session`              | `start`, `stop`, `compact`                                             | `SessionStart` / `Stop`             |
| `read`/`write`         | `markdown`, `rust`, `python`, `json`, `svg`                            | `PostToolUse` (Write / Edit / Read) |
| `git`                  | `commit`, `push`, `merge`, `pre-commit`                                | Bash-argv / git hook                |
| `prompt`               | `submit`, `stop`                                                       | `UserPromptSubmit` / `Stop`         |
|                        |                                                                        |                                     |

Read a row as a path — `tool` ⊃ `tool:post` ⊃ `tool:post:Bash` — and a shallow moment **prefix-matches** everything under it; `,` is OR (`when:: session:compact, git:commit`). Full grammar and per-class detail: [[Warden Events]].

**What triggers each.** A live rule fires when its `when::` moment occurs (the hook). A passive rule fires only on an **`/audit` pass** — run manually, or wired to a moment (SessionStart, post-commit, a skill post-condition). Nothing watches the filesystem; a file changing on its own triggers nothing.

**Change detection.** Inside an audit pass the **content-hash gates** which files re-run: unchanged files reuse their cached verdict, changed (and never-seen) files re-evaluate. A never-seen anchor has no prior hashes, so all its files run once. An **agent write** fires only live rules, not passive ones (this keeps writes cheap). An **external** edit (Obsidian, `git pull`) fires no hook and is caught at the next audit. **Warden runs no file-change tracker of its own** — an *agent* write is a `write:*` moment for free (the tool hook), and *external* changes ride **git / the audit content-hash**, which already exist. A dedicated filesystem watcher would duplicate those and is heavy, so it stays deferred — and if live external-change reaction is ever needed, the move is to *subscribe* to an existing watcher, not build one. (A machine should carry **one** shared file-change source, not three — Warden never adds a watcher alongside HookAnchor / DMUX; event-storm processing is per-watcher, so redundant trackers waste CPU in bursts.)

### `if::` — the test

The `if::` test is a **Python expression evaluated in the interpretation environment** (§ below) — the same Python scope a rule's body runs in, holding `file` / `anchor` / `git` / `event`. You write the predicate with ordinary Python operators (`not`, `in`, `re.search`) over those objects, so the condition language *is* Python — nothing to learn beyond the object surface:

```
if:: not file.title                        # no H1 title
if:: 'description' not in file.frontmatter # no description
```

When the test needs **judgment**, write it as **prose** (the LLM reads the `file` and decides) or call **`ask_oracle(f'…{slice}')`** for a narrowed judgment. A test yields **findings** (each a message) or a boolean. For a per-violation test, skip `if::` and write a body snippet that conditions and `tell`s inline (§ The actions).

### Ambient rules — no `where::`, no `when::`

A rule with neither clause has no dispatch key, so Warden cannot place it. It is **ambient**: always loaded into the agent's context (the CLAUDE.md model), **not automatically dispatched** — the weakest form, for guidance that can't be pinned to a file or a moment. (Distinct from `where:: always`, which is an explicit all-files scope that audit still dispatches.)

### Backticking clause values

A `where::` / `when::` / `if::` value is one line, and the parser strips backticks — so they change *nothing* semantically. They are **optional but recommended**: Obsidian/Dataview mangle a bare value containing `*`, `[`, `|`, or `::` (a glob, a regex, a `::`-bearing expression), so backticking — `` where:: `**/*.md` `` — keeps it from rendering wrong or colliding with Dataview. A plain token (`when:: write:markdown`) needs none; backtick anything with special characters ([[F007 — Backtick all where expressions — parser swap|F007]]).

## The actions

On a hit, the body performs zero or more actions. **`tell` / `edit` / `deny`** are the **mediated verbs** — a small, closed set the engine *applies* with controlled effects (the steer formatting, the `edit` never-delete floor). Beyond them the body is just Python — that's `run` (§ below). A body that **emits nothing is a pass**: the rule found no problem.

**The body form.** A bare-prose body **is** the `tell` (no keyword). For anything more, the body is **Python, marked by backticks** — an inline `` `expr` `` for a one-liner, a bare ` ``` ` fence for several lines (no `python` tag). `file` / `anchor` / `git` / `event` and the verbs are in scope; no `def`. A `description::` field carries the rule's **meaning / goal** — its intent for a reader (the North Star), **not sent on rule fire**; bare prose in body position is the `tell`; `message:: <text>` is sugar for a fixed `tell`; a *fix* is an `edit` that repairs a violation. **Emit nothing → the rule passed.**

> **The one lexical rule: backticks = Python.** A backticked `if::` value, a backticked one-line body, a fenced block — all are Python run by the engine; un-backticked prose is the `tell`. (Subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

### `tell`

`tell(msg)` — or a bare-prose body, which *is* a `tell`. Says something to the agent: a problem or a directive. Live, it is a **steer** the hook injects into the agent's context (the F180 steer); under audit, a **finding** in the report. Calling it **many times accumulates** — joined newline-separated into one steer (live), or separate findings (audit).

### `edit`

Methods on `file` — `file.set_frontmatter(…)`, `file.replace_section(…)`, … — write to the file: repair, stamp metadata, append a log. Each is **never-delete floored** (adds or replaces within a named region, never wipes content it didn't target). A *fix* is just an `edit` that repairs a violation.

### `deny`

`deny(reason)` — block the pending action. Only at a **`tool:pre`** moment (a command, not a file).

### `run`

Not a verb — there is **no `run()` to call**. A Python body *runs directly*, so beyond the mediated verbs it can do anything Python can: call a function, open a file, or shell out with **`sh(argv)`** (argv-form, so interpolated data can't inject). "`run`" just names *arbitrary Python in a body*. To merely *read* command-derived state, prefer a data accessor (`git.is_dirty`) over a subprocess per `if::`; an expensive `sh` read in a condition parallels `ask_oracle` — fine at audit, can't block the live hot path.

> **A rule is code — trust the source, same as a skill.** Any Python a rule runs — an `if::` test *or* a body — is real code that can do what Python does, exactly like a **skill** you adopt and let run. So a rule is **no more or less dangerous than a skill**; the only question is whether you trust where it came from. The asterisk is *exposure*, not capability: rules fire **automatically and pervasively**, are **adopted in bulk**, and **read like documentation** — so an *imported* effectful rule hides more easily than a skill you deliberately invoke. Hence: **vet imported rulesets like a skill**, and keep effects off for imported rules until vetted. (The `edit` never-delete floor is *accident*-safety, not a security wall.)

## The interpretation environment

The **interpretation environment** is the Python scope a rule is *interpreted* in — where both its `if::` test and its body run. The engine pre-populates that scope with: the **injected objects** (`file`, `anchor`, `git`, `event`, `agent` — the matched subject, its repo, and the running agent), the **action verbs** (`tell`, `deny`, `ask_oracle`, `file`'s edits, and `sh`), and the **ambient runtime** (`today`, `now`, plus plain Python). Evaluating an `if::` condition or running a body is just executing Python in this scope — there is no separate interpreter or rule-language to learn, only this object surface:

| In scope | Accessors / calls |
|---|---|
| **`file`** | `.path`, `.name`, `.text`, `.lines`, `.title`, `.frontmatter`, `.section(h)`, `.sections(level)`, `.links` |
| **`anchor`** | `.name`, `.slug`, `.root`, `.traits`, `.get(name)` |
| **`git`** | `.branch`, `.mode`, `.is_dirty`, `.ahead`, `.changed` |
| **`event`** | `.kind`, `.diff`, `.command`, `.tool` |
| **`agent`** | `.state` (`working`/`landed`/`asking`/`idle`), `.skill`, `.is_asking` |
| *verbs* | `tell(msg)`, `deny(reason)`, the `file` edits, `ask_oracle(prompt)→str`, `sh(argv)` — § Verbs |
| *ambient* | `today`, `now` (+ plain Python: builtins, `re`, `json`, `datetime`) |
| *variables* | `{ANCHOR}`, `{NAME}`, `{SLUG}` — `where::` substitutions (§ Ambient and variables) |

None of these take a `ctx.` prefix — they are aliased into the scope directly. Each is **computed lazily and cached per pass** — most rules touch only a couple, so the daemon pays for `git` / `agent` / parsed sections only when a rule actually reads them ([[Warden Architecture]] §7).

**Naming convention.** Accessor names are **snake_case** for multi-word identifiers (`is_dirty`, `set_frontmatter`, `replace_section`); single domain words stay one word (`frontmatter` — as in the `python-frontmatter` library — `sections`, `links`). The all-caps brace form (`{NAME}`) is reserved for the `where::` substitution variables.

### `file`

Binds to the matched file (from `where::`, or a file-bearing moment like `write:*`):

| Member | What it is |
|---|---|
| `file.path`, `file.name` | path, basename |
| `file.text`, `file.lines` | full text, list of lines |
| `file.title` | the H1 title (or `None`) |
| `file.frontmatter` | the file's metadata — YAML block **and** Dataview `::` inline fields, merged |
| `file.section("## X")`, `file.sections(level=N)` | one section, the sections |
| `file.links` | the wiki / markdown links |

(`file`'s **edit** operations — `set_frontmatter`, `replace_section`, … — are *actions*, listed under § Verbs.)

### `anchor`

| Member | What it is |
|---|---|
| `anchor.name`, `anchor.slug` | RID, kebab slug |
| `anchor.root`, `anchor.traits` | root path, its traits |
| `anchor.get(name)` | any other anchor field, by name |

### `git`

The repository of the rule's **subject**, auto-resolved to the nearest enclosing `.git` (the `file`'s repo, or the command's working dir for a Bash moment):

| Member | What it is |
|---|---|
| `git.branch` | current branch (`main`, …) |
| `git.mode` | the anchor's git workflow mode — `Commit` (commit freely), review/PR, … (from Decisions) |
| `git.is_dirty`, `git.ahead` | uncommitted changes?, commits ahead of upstream |
| `git.changed` | paths changed since the last commit (a list) |

*(Open: when an anchor nests its own code repo, "the git" is ambiguous — anchor repo vs code repo. For now it follows the subject.)*

### `event`

The moment (from `when::`; **live runs only** — absent under `/audit`):

| Member | What it is |
|---|---|
| `event.kind` | the moment that fired (`write:markdown`, …) |
| `event.diff` | what changed (write moments) |
| `event.command` | the pending / just-run command (Bash moments) |
| `event.tool` | the tool name + input (tool moments) |

### `agent`

The running agent's state — sense it at a return / lifecycle moment (`when:: prompt:stop`, `session:*`) to react to *how a turn ended*:

| Member | What it is |
|---|---|
| `agent.state` | `working` (mid-task), `landed` (finished clean), `asking` (waiting on a user answer), `idle` |
| `agent.skill` | the skill running now — `land`, `query`, `crank`, … (or `None`) |
| `agent.is_asking` | a user question is pending (sugar for `state == 'asking'`) |

**Trigger vs. sense — for both agent-state and file-change.** The agent's turn boundary is a *moment* (`prompt:submit` / `prompt:stop`, [[Warden Events]]); its *state* is **sensed** here in `if::`. A **file change** has the same shape: an agent write is the `write:*` *moment* (trigger), `event.diff` is what changed (sense), and repo-wide change is sensed via `git.is_dirty` / `git.changed`. Warden *senses* change from git / the audit content-hash; it doesn't watch the filesystem (§ `when::` Change detection).

### Verbs

The callable operations — the actions a body emits (`tell` / `edit` / `deny`), plus the `ask_oracle` reader:

| VERBS                           | What it does                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `tell(msg)`                     | steer the agent (live) / file a finding (audit)                                                                                      |
| `deny(reason)`                  | block the pending tool — `tool:pre` only                                                                                             |
| `ask_oracle(prompt) → str`      | ask a fresh **oracle** (a context-less helper LLM); returns its text — merge material into the prompt yourself                       |
| `sh(argv)`                      | run a shell command (an argv **list**); returns its output — an **effect** (`run`), trusted like a skill; argv-form blocks injection |
| `file.replace_section(h, text)` | **edit** — replace a section's body (never-delete floored)                                                                           |
| `file.set_frontmatter(k, v)`    | **edit** — set a frontmatter key (never-delete floored)                                                                              |

### Ambient and variables

Both are always in scope, no setup. **Ambient values** are the plain runtime; **variables** are the all-caps anchor substitutions used in a `where::` glob.

| Name | What it is |
|---|---|
| `today`, `now` | current date (ISO-serializing on write), current datetime |
| Python | full Python — builtins + stdlib (`re`, `json`, `datetime`, …); it's real code, trusted like a skill (the hot-path interpreter may limit imports for *speed*, not security) |
| `{ANCHOR}` · `{NAME}` · `{SLUG}` | the adopting anchor's root path · name · kebab slug |

The **variables** are *substitution tokens*, not Python values: in a `where::` glob they expand to the adopting anchor's values when the rule binds to that anchor — `where:: {ANCHOR}/**/{NAME} Backlog.md`. They are the where-clause counterpart of the `anchor.*` accessors — use the brace form (`{NAME}`) in `where::`, the dotted form (`anchor.name`) in an `if::` or a body.

**How `ask_oracle` executes.** A hook is a synchronous subprocess and cannot block-and-await the agent's model, so `ask_oracle` spawns a **separate headless oracle** that sees only the prompt and returns a string. On the **audit path** (not latency-bound) the pipeline blocks on it and parses the answer — its home. On the **live path** (the ms-budget hot hook) it cannot block, so a live judgment is **delegated to the agent as a steer** instead. The oracle is a **cheaper model** (Sonnet, ≈5× cheaper, ~1¢ per check) reached through Claude Code's *own* access — a sub-agent of the `/audit` turn, the running agent on the live path, or `claude -p` headless — so there's **no API key to set up** (the external API is opt-in, only to dodge subscription usage caps). (Mechanism: [[Warden Architecture]] §7.)

**Oracle idiom.** The oracle is context-less — it sees only the prompt, and the agent sees only what you `tell`. Give the oracle the narrow judgment (e.g. "which are wrong? reply `none` if none"), gate on a sentinel in code, and let the **rule author the directive** the agent sees — don't make the oracle write the steer. *When to use it:* the **agent** when it already has the context and you want it steered now; the **oracle** when the judgment is narrow, repeated, or wants caching and control (per-judgment an oracle can be far lighter — a cheap model on a small slice, cached — than the agent reasoning over its full context every time).

## Rulesets — composition, inheritance, activation

A **ruleset** is a named bundle of rules ([[Warden Rule]] § The ruleset).

**Composition — `include::`.** A ruleset `include::`s other rulesets (by name or wiki-link) and thereby contains **all of their rules, recursively** — depth-first, cycles forbidden. Composition **never renumbers**: an included rule keeps its source-set id (`R-<source>-NN`), so cross-references stay stable. A pure-composition set (`include::` only, no own rules) is an **umbrella**.

**Clause inheritance.** A ruleset may carry a set-level `where::` / `when::` / `if::`; its rules **inherit** them (recursively through `include::`), and a rule's own clause **overrides and disregards** the set's. That is all there is to clauses at the set level — a convenience for stating a default once, not new behavior.

**Activation.** A ruleset does nothing until an **anchor adopts it**, recorded in `# {NAME} Decisions` ([[FCT Decisions]]) — where an anchor's **traits/facets *are* its adoptions** (a facet's ruleset is active wherever the facet is present), plus any sets it adopts explicitly. **Activating a ruleset activates all its rules** (its `include::` children with it). The active set is per-anchor state in `{NAME} Decisions.md`.

**Resolution.** For a given anchor, the engine computes the **active rule set** = flatten(the anchor's adopted rulesets), with every rule's `where::`/`when::` resolved relative to that anchor's root. At a moment or audit, only the active rules for the relevant anchor are considered — then narrowed by the `where::`/`when::` indexes and evaluated by `if::`. The compiler/installer ([[Warden Architecture]]) precompiles this active set into the per-moment dispatch so the hot path stays cheap; editing `Decisions.md` recompiles it.

## The pipeline

```
for the anchor in scope:
  active = flatten(adopted rulesets)              # from {NAME} Decisions.md
on trigger:  a when:: moment fires,  OR  /audit visits the anchor
  candidates = active rules whose where::/when:: INDEXES match    # cheap, no code
  for each candidate, for each file T it matches:
    if a cached verdict for (rule, T) is fresh under rerun:::  reuse it
    else:  evaluate if:: over file(T)  → findings (or false);  cache by (rule, hash(T)[, model])
    for each finding:  perform the action(s) — tell / edit / deny
```

## Re-running an expensive test

An `if::` test that calls the oracle costs tokens, so its verdict is **cached by file-content-hash** and reused until the file changes. This re-evaluation policy is **automatic by body cost**: a cheap (Python/primitive) test re-runs on *any* change; an **expensive (LLM) test defaults to re-running only on a *significant* change** — re-judging on every keystroke is waste. `rerun::` is the explicit **override** for the rare case, not something you normally write.

This is a *third* temporal axis, distinct from the condition: `when::` is *which moment*, `if::` is *whether it fires now*, re-evaluation is *recompute vs. reuse the cached verdict* — keyed to the rule's own last-pass cache, so it can't fold into `if` / `when` (significance is per-rule, not a property of the write). Conceptually it's the script-assisted gate (a cheap "significant?" check guarding the expensive judgment). ([[F215 — Re-evaluation economy — the significant-edit gate|F215]].)

## Open Questions

1. **The `edit` family.** What is the full set of `file` edit methods (beyond `set_frontmatter` / `replace_section`), and how does the never-delete floor apply to each?
2. **`ask_oracle` material (F215).** Does the re-evaluation economy gate want the prompt's *material* as a **separate, diffable argument** (so the engine can tell when only the question changed vs. the content), or is one merged prompt string enough?
3. **`git` in a nested repo.** When an anchor nests its own code repo (the vault repo *and* a project repo under one anchor), `git` follows the rule's subject — but does that need an explicit **`anchor.repo` / `code.repo`** split when both exist?

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Events]] — the `when::` index; [[FCT Ruleset]] — the `where::` index.
- [[FCT Decisions]] — adoption / activation of rulesets by an anchor.
- [[Warden Architecture]] — how the active set is compiled and dispatched (incl. the resident-Python implementation, §7a).
- [[Warden Examples]] — every kind of test + action, as complete rules.
