---
description: "how the engine runs a rule — the condition, the actions, the runnable interpretation environment, and ruleset activation"
---

> [!todo] Open threads (everything here is in flux — park items so we don't forget)
> - **`run` / `sh` effect helper** — a convenience for arbitrary effects (it's just Python — same trust class as a skill, not a sandbox question); ship after the mediated three. Real policy work is *vetting imported rulesets* (effects off until vetted), argv-form shell to block injection.
> - **The `edit` family** — define the method set (`set_frontmatter`, `replace_section`, …) and the never-delete floor it rides on.
> - **`ask_oracle` + F215** — shape/vocabulary settled; one open question: whether F215's economy gate wants the prompt's *material* as a separate diffable arg (vs one merged prompt).
> - **`git` when an anchor nests a code repo** — `git` follows the subject's repo now; may need an `anchor.repo` / `code.repo` split when both exist.

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

A path glob, resolved **relative to the anchor that adopts the rule**: `**/*.md` means "every markdown file in this anchor," which is what makes one rule reusable across anchors. The explicit `{ANCHOR}/` token is equivalent to a bare glob. **Required for a passive rule**; optional for a live one (the moment supplies the subject). Default `always`. Grammar: [[FCT Ruleset]] § Where clause.

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
| **run** *(future helper)* | the Python body, directly | arbitrary execution — shell, drive Warden / other agents | it's just Python — trusted like a skill; off for imported rules |

**The body form.** A bare-prose body **is** the `tell` (no keyword). For anything more, the body is **Python, marked by backticks** — an inline `` `expr` `` for a one-liner, a bare ` ``` ` fence for several lines (no `python` tag). `file` / `anchor` / `git` / `event` and the verbs are in scope; no `def`. A `description::` field carries the rule's **meaning / goal** — its intent for a reader (the North Star), **not sent on rule fire**; bare prose in body position is the `tell`; `message:: <text>` is sugar for a fixed `tell`; a *fix* is an `edit` that repairs a violation. **Emit nothing → the rule passed.**

> **The one lexical rule: backticks = Python.** A backticked `if::` value, a backticked one-line body, a fenced block — all are Python run by the engine; un-backticked prose is the `tell`. (Subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

**`tell` delivery.** Live, a `tell` is text the hook injects into the agent's context (the F180 steer); under audit it is a finding in the report. Calling `tell` **many times accumulates**: live, the messages are joined newline-separated into one steer block; under audit, each is a separate finding.

**Mediated vs. unmediated.** `tell` / `edit` / `deny` are a closed, small set the engine *applies* (the `edit` never-delete floor, the steer formatting) — conveniences, not a sandbox. Beyond them, the body is just Python (`run` — arbitrary effects); that's gated by trusting the rule's **source**, like a skill, not by the engine.

> **`run` / arbitrary effects — the trust boundary is the *source*, same as a skill.** A Python rule body is real code: it can already do what Python does — exactly like a **skill**, which you also adopt and let run Python. So a rule is **no more or less dangerous than a skill**; the only question is whether you trust where it came from (your own rules are as trusted as your own scripts). The one asterisk is *exposure*, not capability: rules fire **automatically and pervasively**, are **adopted in bulk** (a whole facet's set), and **read like documentation** — so an *imported* effectful rule hides more easily and runs more often than a skill you deliberately invoke. Hence: **vet imported rulesets like you'd vet a skill**, and keep effectful operations off for imported rules until vetted. (The never-delete floor on mediated `edit`s is *accident*-safety, not a security wall — a real Python sandbox is leaky and not worth pretending.)
>
> **Shell is the canonical effect** — `sh(['git', 'add', file.path])`, a Python call (no new syntax; backtick is spent), **argv-form only** so interpolated `ctx` data can't inject. To merely *check* command-derived state, read a **data accessor** (`git.is_dirty`) instead — run once, cached, no subprocess per `if::`. (An expensive shell read in a condition parallels `ask_oracle`: fine on audit, can't-block on the live hot path.)

## The interpretation environment

The **interpretation environment** is the Python scope a rule is *interpreted* in — where both its `if::` test and its body run. The engine pre-populates that scope with: the **injected objects** (`file`, `anchor`, `git`, `event`, `agent` — the matched subject, its repo, and the running agent), the **action verbs** (`tell`, `deny`, `ask_oracle`, `file`'s edits, and `sh`), and the **ambient runtime** (`today`, `now`, plus plain Python). Evaluating an `if::` condition or running a body is just executing Python in this scope — there is no separate interpreter or rule-language to learn, only this object surface:

| In scope | Accessors / calls |
|---|---|
| **`file`** | `.path`, `.name`, `.text`, `.lines`, `.title`, `.frontmatter`, `.section(h)`, `.sections(level)`, `.links` |
| **`anchor`** | `.name`, `.slug`, `.root`, `.traits`, `.get(name)` |
| **`git`** | `.branch`, `.mode`, `.is_dirty`, `.ahead`, `.changed` |
| **`event`** | `.kind`, `.diff`, `.command`, `.tool` |
| **`agent`** | `.state` (`working`/`landed`/`asking`/`idle`), `.skill`, `.is_asking` |
| *ambient* | `today`, `now` (+ plain Python: builtins, `re`, `json`, `datetime`) |
| *verbs* | `tell(msg)`, `deny(reason)`, the `file` edits, `ask_oracle(prompt)→str`, `sh(argv)` — § Verbs |

None of these take a `ctx.` prefix — they are aliased into the scope directly. Each is **computed lazily and cached per pass** — most rules touch only a couple, so the daemon pays for `git` / `agent` / parsed sections only when a rule actually reads them ([[Warden Architecture]] §7).

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

| Call | What it does |
|---|---|
| `tell(msg)` | steer the agent (live) / file a finding (audit) |
| `deny(reason)` | block the pending tool — `tool:pre` only |
| `file.set_frontmatter(k, v)` | **edit** — set a frontmatter key (never-delete floored) |
| `file.replace_section(h, text)` | **edit** — replace a section's body (never-delete floored) |
| `ask_oracle(prompt) → str` | ask a fresh **oracle** (a context-less helper LLM); returns its text — merge material into the prompt yourself |
| `sh(argv)` | run a shell command (an argv **list**); returns its output — an **effect** (`run`), trusted like a skill; argv-form blocks injection |

### Ambient

| Name | What it is |
|---|---|
| `today`, `now` | current date (ISO-serializing on write), current datetime |
| Python | full Python — builtins + stdlib (`re`, `json`, `datetime`, …); it's real code, trusted like a skill (the hot-path interpreter may limit imports for *speed*, not security) |

**How `ask_oracle` executes.** A hook is a synchronous subprocess and cannot block-and-await the agent's model, so `ask_oracle` spawns a **separate headless oracle** that sees only the prompt and returns a string. On the **audit path** (not latency-bound) the pipeline blocks on it and parses the answer — its home. On the **live path** (the ms-budget hot hook) it cannot block, so a live judgment is **delegated to the agent as a steer** instead. The oracle is a **cheaper model** (Sonnet, ≈5× cheaper, ~1¢ per check) reached through Claude Code's *own* access — a sub-agent of the `/audit` turn, the running agent on the live path, or `claude -p` headless — so there's **no API key to set up** (the external API is opt-in, only to dodge subscription usage caps). (Mechanism: [[Warden Architecture]] §7.)

**Oracle idiom.** The oracle is context-less — it sees only the prompt, and the agent sees only what you `tell`. Give the oracle the narrow judgment (e.g. "which are wrong? reply `none` if none"), gate on a sentinel in code, and let the **rule author the directive** the agent sees — don't make the oracle write the steer. *When to use it:* the **agent** when it already has the context and you want it steered now; the **oracle** when the judgment is narrow, repeated, or wants caching and control (per-judgment an oracle can be far lighter — a cheap model on a small slice, cached — than the agent reasoning over its full context every time).

## Rulesets — composition and activation

A **ruleset** is a named bundle of rules ([[Warden Rule]] § The ruleset). Two relations govern which rules are in force, and where.

**Composition — `include::`.** A ruleset may `include::` other rulesets (by name or wiki-link). Resolving a set **flattens** it: its own rules, plus — depth-first, cycles forbidden — the rules of every included set, concatenated into one list. Composition **never renumbers**: an included rule keeps its source-set id (`R-<source>-NN`), so cross-references stay stable. A pure-composition set (`include::` only, no own rules) is an **umbrella**.

**Activation — by the anchor's traits.** A ruleset in the catalog does nothing until an **anchor adopts it**. Adoption is recorded in the anchor's `# {NAME} Decisions` ([[FCT Decisions]]) — and an anchor's **traits/facets *are* its adoptions**: a facet's ruleset is active wherever that facet is present, plus any catalog sets the anchor adopts explicitly (`include::` under Decisions). So the active rule set is per-anchor state, owned by `{NAME} Decisions.md`.

**Co-location is organizational, not semantic.** A ruleset embedded in a facet / discipline / skill spec is there for **authoring locality** and because the rules *are* that artifact's documentation (the *read* leg of dual-use) — location confers **no firing behavior**. What a rule fires or audits over is its `where::`; the common pattern is a **set-level `where::`** on the embedded ruleset (every rule inherits it unless it overrides), scoping the whole set to the facet's artifacts.

**Salient vs. obligating.** Only a `when::` **obligates** — it fires a live steer at that moment. A rule with `where::` and no `when::` is **passive**: a backstop at `/audit`, and readable in place as the spec, but it never nags mid-work. So a facet's dozen rules are *salient* (read, and audited) without forcing action; `when::` is for the few that must guard live.

**`where::` gates activation, so lean broad.** A rule whose `where::` matches no file in the anchor is **inert** — N/A, never fires, never fails. Over-activation therefore costs only a glob check, while under-activation actually drops a guardrail — so erring broad is correct. Activate an anchor's facet rulesets and let `where::` keep the irrelevant ones asleep.

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
- [[Warden Events]] — the `when::` index; [[FCT Ruleset]] — the `where::` index.
- [[FCT Decisions]] — adoption / activation of rulesets by an anchor.
- [[Warden Architecture]] — how the active set is compiled and dispatched (incl. the resident-Python implementation, §7a).
- [[Warden Examples]] — every kind of test + action, as complete rules.
