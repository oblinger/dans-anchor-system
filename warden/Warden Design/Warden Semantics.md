---
description: "how the engine runs a rule — the condition, the actions, the interpretation environment, and ruleset activation"
---

> [!todo] Open threads (everything here is in flux — park items so we don't forget)
> - **Sync `Warden Rule`** (format spec) to this model — it still has `check::`/tiers, and defaults a clause-less rule to `where:: always` (now the **ambient** case).
> - **Sync `Warden Architecture` §7** with the two-path `ask_oracle` mechanism (oracle on audit / steer on live).
> - **`run` action** — trust/security model before it ships (deferred).
> - **The `edit` family** — define the method set (`set_frontmatter`, `replace_section`, …) and the never-delete floor it rides on.
> - **`ask_oracle` + F215** — shape/vocabulary settled; one open question: whether F215's economy gate wants the prompt's *material* as a separate diffable arg (vs one merged prompt).
> - **`git` when an anchor nests a code repo** — `git` follows the subject's repo now; may need an `anchor.repo` / `code.repo` split when both exist.
> - **Live external-edit detection** — agent writes fire `write:*`; external edits (Obsidian, `git pull`) are only caught at the next `/audit`. A filesystem watcher would make them live — heavier, deferred; decide if any rule needs it.

# Warden Semantics

How the Warden engine runs a rule. [[Warden Rule]] is the file format; this is the operational model. A rule is a **condition** and a set of **actions**. The engine resolves which rules are active for an anchor, dispatches the candidates cheaply (by moment and file), evaluates each candidate's condition, and on a hit performs its actions.

## A rule at a glance

![[Warden Rule Anatomy.svg]]

| Clause | What it does |
|---|---|
| **Condition** | |
| `where::` | which files it runs over — an anchor-relative glob (default `always`) |
| `when::` | which moment triggers a **live** run — omit → *passive* (audit-time) |
| `if::` | the test — a Python expression, or prose for a judgment |
| | |
| **Actions** | |
| `tell` | say something to the agent — a steer (live) or a finding (audit) |
| `edit` | write to a file (`file.set_frontmatter`, …) — never-delete floored |
| `deny` | block the pending tool (`tool:pre` only) |
| `run` | *(future)* arbitrary effects — deferred, pending a security model |

A rule also has a **name** (`R-<slug>-NN`, [[Warden Rule]]) and an optional `rerun::` modifier (§ Re-running). A "check" is just an `if::` condition — there is no separate check / evaluator / tier concept.

## The condition — `where`, `when`, `if`

A rule activates for a target when **all of its present clauses hold**. `where::` and `when::` are **indexes** — matched without running any code, so dispatch is cheap. `if::` is the **computed test**, evaluated only after the indexes have narrowed the candidates.

### `where::` — which files

A path glob, resolved **relative to the anchor that adopts the rule**: `**/*.md` means "every markdown file in this anchor," which is what makes one rule reusable across anchors. The explicit `{ANCHOR}/` token is equivalent to a bare glob. **Required for a passive rule**; optional for a live one (the moment supplies the subject). Default `always`. Grammar: [[FCT Ruleset]] § Where clause.

### `when::` — which moment

The moment that fires the rule **live** — a markdown write, a Bash `git commit`, a skill run, session start. Omit it and the rule is **passive**: it runs only when `/audit` visits its `where::` files. Taxonomy: [[Warden Trigger Taxonomy]].

**What triggers each.** A live rule fires when its `when::` moment occurs (the hook). A passive rule fires only on an **`/audit` pass** — run manually, or wired to a moment (SessionStart, post-commit, a skill post-condition). Nothing watches the filesystem; a file changing on its own triggers nothing.

**Change detection.** Inside an audit pass the **content-hash gates** which files re-run: unchanged files reuse their cached verdict, changed (and never-seen) files re-evaluate. A never-seen anchor has no prior hashes, so all its files run once. An **agent write** fires only live rules, not passive ones (this keeps writes cheap). An **external** edit (Obsidian, `git pull`) fires no hook and is caught at the next audit. Live reaction to external edits would need a filesystem watcher (deferred).

### `if::` — the test

A **Python expression** over the data nouns (§ Rule interpretation), written with plain Python — there are no `.has`/`.matches` predicate verbs:

```
if:: not file.title                        # no H1 title
if:: 'description' not in file.frontmatter # no description
```

A value containing `::` is backticked ([[F007 — Backtick all where expressions — parser swap|F007]]) so Dataview doesn't mis-parse it. When the test needs **judgment**, write it as **prose** (the LLM reads the `file` and decides) or call **`ask_oracle(f'…{slice}')`** for a narrowed judgment. A test yields **findings** (each a message) or a boolean. For a per-violation test, skip `if::` and write a body snippet that conditions and `tell`s inline (§ The actions).

### Ambient rules — no `where::`, no `when::`

A rule with neither clause has no dispatch key, so Warden cannot place it. It is **ambient**: always loaded into the agent's context (the CLAUDE.md model), **not automatically dispatched** — the weakest form, for guidance that can't be pinned to a file or a moment. (Distinct from `where:: always`, which is an explicit all-files scope that audit still dispatches.)

## The actions — `tell`, `edit`, `deny`, `run`

On a hit, the body performs zero or more actions. Three are **mediated** (Warden controls exactly what each does); `run` is the **unmediated**, deferred escape hatch.

| Action | Emitted by | What happens | Goes to |
|---|---|---|---|
| *(pass)* | — | nothing — the test found no problem | — |
| **tell** | bare prose, or `tell(msg)` | say something to the agent — a problem or a directive | a **steer** in the agent's context (live) · a **finding** in the report (audit) |
| **edit** | a method on `file` — `file.set_frontmatter(…)`, `file.replace_section(…)`, … | write to a file — repair, stamp metadata, append a log | the file(s) — never-delete floored |
| **deny** | `deny(reason)` | block the pending action | the tool call — `tool:pre` only |
| **run** *(future)* | the Python body, directly | arbitrary execution — commands, drive Warden / other agents | **deferred** — needs a security model first |

**The body form.** A bare-prose body **is** the `tell` (no keyword). For anything more, the body is **Python, marked by backticks** — an inline `` `expr` `` for a one-liner, a bare ` ``` ` fence for several lines (no `python` tag). `file` / `anchor` / `git` / `event` and the verbs are in scope; no `def`. A `description::` field carries the rule's **meaning** — documentation, **never sent**; bare prose in body position is the `tell`; `message:: <text>` is sugar for a fixed `tell`; a *fix* is an `edit` that repairs a violation. **Emit nothing → the rule passed.**

> **The one lexical rule: backticks = Python.** A backticked `if::` value, a backticked one-line body, a fenced block — all are Python run by the engine; un-backticked prose is the `tell`. (Subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

**`tell` delivery.** Live, a `tell` is text the hook injects into the agent's context (the F180 steer); under audit it is a finding in the report. Calling `tell` **many times accumulates**: live, the messages are joined newline-separated into one steer block; under audit, each is a separate finding.

**Mediated vs. unmediated.** `tell` / `edit` / `deny` are a closed, small set the body calls directly. `run` is arbitrary code execution (it can drive Warden or other agents) and is **deferred**.

> **Open — `run`'s trust model.** Your own rules are as trusted as your own scripts; an *imported* ruleset carrying effectful Python is a supply-chain risk (adopting it runs its code on your moments). Leaning: ship the mediated three first; add `run` only behind explicit trust, off for imported rules.

## Rule interpretation

A rule body is plain Python over a handful of injected objects (`file`, `anchor`, `git`, `event`) plus the verbs and the ambient environment. The whole surface, at a glance:

| In scope | Accessors / calls |
|---|---|
| **`file`** | `.path`, `.name`, `.text`, `.lines`, `.title`, `.frontmatter`, `.section(h)`, `.sections(level)`, `.links` |
| **`anchor`** | `.name`, `.slug`, `.root`, `.traits`, `.get(name)` |
| **`git`** | `.branch`, `.mode`, `.is_dirty`, `.ahead` |
| **`event`** | `.kind`, `.diff`, `.command`, `.tool` |
| *ambient* | `today`, `now` (+ plain Python: builtins, `re`, `json`, `datetime`) |
| *verbs* | `tell(msg)`, `deny(reason)`, `ask_oracle(prompt)→str`, and `file.…` (edits — under File) |

`file` / `anchor` / `event` are the three things the rule **matched on** (`where::` → `file`, the adopting anchor → `anchor`, `when::` → `event`); `git` is **derived** (the subject's repo). None take a `ctx.` prefix — they are aliased in directly.

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

**Edit methods** (the `edit` action, floor-gated): `file.set_frontmatter(k, v)`, `file.replace_section(h, text)`, … each writes back to the file. (These are the `file.…` in the verbs row.)

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

*(Open: when an anchor nests its own code repo, "the git" is ambiguous — anchor repo vs code repo. For now it follows the subject.)*

### `event`

The moment (from `when::`; **live runs only** — absent under `/audit`):

| Member | What it is |
|---|---|
| `event.kind` | the moment that fired (`write:markdown`, …) |
| `event.diff` | what changed (write moments) |
| `event.command` | the pending / just-run command (Bash moments) |
| `event.tool` | the tool name + input (tool moments) |

### Verbs and ambient

`tell(msg)` and `deny(reason)` are bare in scope; the `edit` action is methods on `file` (above). `ask_oracle(prompt) → str` hands a fresh **oracle** (a separate, context-less helper LLM) a prompt and returns its text — merge any material into the prompt yourself (`f'…{file.section(…)}'`). Ambient: `today` (current date, ISO-serializing), `now` (current datetime), plus plain-Python builtins and a stdlib subset (`re`, `json`, `datetime`); reachable stdlib is bounded by the sandbox (same trust question as `run`).

**How `ask_oracle` executes.** A hook is a synchronous subprocess and cannot block-and-await the agent's model, so `ask_oracle` spawns a **separate headless oracle** that sees only the prompt and returns a string. On the **audit path** (not latency-bound) the pipeline blocks on it and parses the answer — its home. On the **live path** (the ms-budget hot hook) it cannot block, so a live judgment is **delegated to the agent as a steer** instead. (Mechanism: [[Warden Architecture]] §7.)

**Oracle idiom.** The oracle is context-less — it sees only the prompt, and the agent sees only what you `tell`. Give the oracle the narrow judgment (e.g. "which are wrong? reply `none` if none"), gate on a sentinel in code, and let the **rule author the directive** the agent sees — don't make the oracle write the steer. *When to use it:* the **agent** when it already has the context and you want it steered now; the **oracle** when the judgment is narrow, repeated, or wants caching and control (per-judgment an oracle can be far lighter — a cheap model on a small slice, cached — than the agent reasoning over its full context every time).

## Rulesets — composition and activation

A **ruleset** is a named bundle of rules ([[Warden Rule]] § The ruleset). Two relations govern which rules are in force, and where.

**Composition — `include::`.** A ruleset may `include::` other rulesets (by name or wiki-link). Resolving a set **flattens** it: its own rules, plus — depth-first, cycles forbidden — the rules of every included set, concatenated into one list. Composition **never renumbers**: an included rule keeps its source-set id (`R-<source>-NN`), so cross-references stay stable. A pure-composition set (`include::` only, no own rules) is an **umbrella**.

**Activation — adoption by an anchor.** A ruleset in the catalog does nothing until an **anchor adopts it**. Adoption is an `include::` under the anchor's `# {NAME} Decisions` heading ([[FCT Decisions]]) — the same `include::` mechanism, a different host. So **the active rule set is per-anchor state, owned by `{NAME} Decisions.md`**: that file is the source of truth for "which rules are on, here."

**Two uses of `include::`, by host:** under a `# RULESET` heading it is **composition** (one set built from others); under a `# {NAME} Decisions` heading it is **activation** (an anchor turning a set on). Same syntax, different scope.

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

An `if::` test that calls the oracle costs tokens, so its result is cached by file-content-hash and reused until the file changes. **`rerun:: significant`** relaxes that — re-run only on *significant* change, not every edit ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]). Cheap (primitive) tests leave it default.

## See also

- [[Warden Rule]] — the file format these semantics run over.
- [[Warden Trigger Taxonomy]] — the `when::` index; [[FCT Ruleset]] — the `where::` index.
- [[FCT Decisions]] — adoption / activation of rulesets by an anchor.
- [[Warden Architecture]] — how the active set is compiled and dispatched (incl. the resident-Python implementation, §7a).
- [[Warden Examples]] — every kind of test + action, as complete rules.
