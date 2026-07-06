---
description: "the unified map: rules, rulesets, `include::` composition, dispatch, the hook subsystem, and the compiler/audit engine"
---

# Warden Architecture

The rule system is how a portable, audit-checkable constraint is **defined** (the `RULE` / `RULESET` primitives), **composed** (`include::` containment), **placed** in the vault and **adopted** by an anchor, **bound** to the contexts (`where::`) and events (`when::`) that should trigger it, and finally **run** by two consumers — the on-demand audit/rule engine and the always-on hook subsystem — over one shared corpus. This page is the structural overview that ties those subsystems together; each subsystem's prescriptive spec lives in the facet or feature doc cited in its section.

> [!info] Scope
> This is the architecture *of the rule language and its runtime*. The prescriptive file-format spec is [[FCT Ruleset]]; the per-audit execution pipeline is [[Audit Architecture]] and [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]. This page is the connective tissue: it names the subsystems, shows how they fit, and points at the source of truth for each.

## Rule system — define · compose · run

![[Warden Architecture.svg|1100]]

[↗ Open figure](Warden%20Architecture.svg) · [✎ Edit source](Warden%20Architecture.d2)

### Figure index

| Grouping | What it covers | Spec |
|---|---|---|
| **DEFINE** — a rule on disk | `RULE` / `RULESET` sentinels; the **condition** (`where` · `when` · `if`); the **actions** (`tell` · `edit` · `deny` · `run`); `description::`. | [[Warden Rule]] |
| **COMPOSE & ADOPT** | `include::` depth-first flatten + umbrellas; three homes (catalog · embedded · anchor-local); adoption via anchor **[[traits]]** (`.anchor`); `where::` keeps unmatched rules asleep. | [[Warden Rule]] · [[FCT Decisions]] |
| **RUN** — the engine | resident **daemon** + tiny notifier; **dispatch** by `where`/`when` indexes; **interpret** `if` + body over `file`·`anchor`·`git`·`event`·`agent`; **consumers** (live hooks · `/audit`); the **oracle**. | [[Warden Semantics]] · [[Warden Runtime]] |

---

## 1 · Definition — the Rule and the Ruleset

Two primitives, both spec'd prescriptively in [[FCT Ruleset]]. Worked instances: [[R-diagram]] (large umbrella), [[FEX Rules]] (anchor-local), and the self-applying `# RULESET R-ruleset` embedded in [[FCT Ruleset]] itself.

### The Rule — the atomic unit

A rule is a markdown **heading** whose first token is the all-caps `RULE` sentinel + an immutable identifier — greppable anywhere in the vault (`grep -rnE '^#+\s+RULE\s+R-'`), not just inside ruleset files. The heading **names** the rule; the fields and body below say what it does. Full format: [[Warden Rule]].

| Part | Form | Notes |
|---|---|---|
| Heading | `<H> RULE R-<slug>-NN — name` | the `RULE` sentinel + the permanent id; H3 customary inside a `# RULESET`. |
| `description::` | a queryable one-liner | the rule's **meaning** — never sent on fire. |
| condition | `where::` · `when::` · `if::` | the conjunction — which files · at what moment · and only if. Full section: [[#4 · The condition — the conjunction when ∧ where ∧ if\|§4 The condition]]; specs: [[FCT Ruleset]] § Where clause · [[Warden Events]] · [[Warden Semantics]] § The condition. |
| body | bare prose, or backticked Python | the **action** — prose *is* the `tell`; Python runs `tell` / `edit` / `deny` / `run` ([[Warden Semantics]]). |
| `**Why:**` · `**Exceptions:**` | optional | rationale · exceptions. (Re-eval economy rides an `if::` over `file.diff`.) |

The **identifier `R-<slug>-NN`** is permanent: `NN` zero-padded, two-digit, monotonic within the slug, never recycled. Cross-document references use the bare id (`see [[R-testing-04]]`).

**Mechanical vs. judgment is read off the body.** A **Python** body decides by script — deterministic, content-hash cached; a **prose** body that states an expectation is an **LLM judgment** — batched, cached, re-run only on significant change. The engine rides exactly this split (§7).

### The Ruleset — the named bundle

A ruleset is a `# RULESET R-<slug>` block plus a prescriptive header. The all-caps `RULESET` sentinel identifies the file/block unambiguously to lint, flatten, and audit scripts.

| Header line | Required? | Purpose |
|---|---|---|
| `# RULESET R-<slug>` | yes | Sentinel H1 + the set's identifier. |
| `include:: …` | yes (may be empty) | Composition / adoption (§2). The empty line is the include slot. |
| `where:: …` | optional | Set-level default **context** for every rule (§4). |
| `when:: …` | optional | Set-level default **event** for every rule (§5). |
| `description:: …` | yes | One-line (8–15 word) tagline; no `::` in the value. |
| prose body | optional | Provenance, source attribution, factoring history; any length. |

`include::` and `description::` are Obsidian Dataview inline fields (`key:: value`). A single file may carry **multiple** rulesets — each `# RULESET` H1 opens a new scope whose header fields apply until the next H1. Standalone `R-<slug>.md` files are body-only (no YAML frontmatter); embedded blocks live inside a host doc that may have its own frontmatter.

---

## 2 · Containment and inheritance — `include::`

A ruleset absorbs other rulesets by naming them on its `include::` line (bare names or `[[wiki-links]]`, mixed freely). This is the system's single inheritance mechanism. Spec: [[FCT Ruleset]] § Include composition; migration history: [[F132 — Rules Migration|F132]].

**Flatten semantics** (what `flatten-ruleset.py` / `audit-plan.py` do):

1. Read this set's own rules.
2. Recursively read each included set's rules — **depth-first; cycles forbidden**.
3. Concatenate into one flat list.
4. Optionally shadow an included rule by re-declaring it with the same `R-<source>-NN` id and an updated body.

Two invariants make composition safe:

- **Composition does NOT renumber.** When `R-diagram` includes `R-sugiyama`, Sugiyama's rules keep their `R-sugiyama-NN` identity inside the flattened list — there is no `R-diagram-23` that is "really" `R-sugiyama-01`. The source set is the rule's home and identity, so cross-project exception references stay stable.
- **The acyclic include graph is the containment relation.** Resolving a target to its applicable rules is just walking `include::` (containment) and then `where::` (binding, §4).

**Umbrellas** are rulesets that are pure composition — `include::` only, no rules of their own:

| Umbrella | Composes | Resolved by |
|---|---|---|
| [[R-anchor]] | every anchor-level facet's set + `R-doc` | `/audit anchor` |
| `R-doc` | the doc-level facet sets (markdown, file-association, brief, …) | `/audit doc` |
| [[R-diagram]] | 7 methodology sub-sets (Sugiyama, C4, WCAG, Tufte, …) → 22 rules | adopted by diagram-authoring anchors |

Adding a facet's rules to an audit is just adding its set to an umbrella's `include::`.

---

## 3 · Placement and association — where rules live

Rules live with the spec that owns them. There are **three homes** — and an anchor's `{NAME} Decisions.md` may host the anchor-local one as a companion `# RULESET` directly after its decisions ([[FCT Decisions]]). Folder convention + facet-embedding: [[F133 — Rulesets folder convention + facet embedding|F133]].

```
ob-skills/library/Rulesets/          ← (1) the shared catalog, organized per-domain
├── Rulesets.md                          catalog index (see Rulesets in §Sources)
├── Diagram/R-diagram.md                 standalone R-<slug>.md (folder-file convention)
├── R-anchor/R-anchor.md                 umbrella
└── R-ob/R-ob-state-mgt.md               owner-scoped set

ob-skills/facets/.../FCT Testing.md   ← (2) embedded # RULESET R-testing inside a facet spec
ob-skills/skills/.../<skill> spec     ← (2) embedded set inside a skill/discipline spec

{NAME}/{NAME} Design/{NAME} Rules.md  ← (3) anchor-local rules too specific to share (rare)
{NAME}/{NAME} Design/{NAME} Decisions.md ← decisions (documentation; may host a companion # RULESET)
```

| Home | When used | Example |
|---|---|---|
| **Catalog** — standalone `R-<slug>.md` | cross-cutting, reusable, owner- or trait-scoped rulesets | [[R-diagram]] |
| **Embedded** — `# RULESET` inside a facet / skill / discipline spec | rules that *are* the structural spec for an artifact kind | `R-ruleset` in [[FCT Ruleset]]; `R-testing` in `FCT Testing` |
| **Anchor-local** — `{NAME} Rules.md` | rules truly specific to one anchor | [[FEX Rules]] |

**Association with facets and skills** is the embedded home: each CAB facet, skill, and discipline spec carries its own `# RULESET R-<facet>` block, and the `R-anchor` / `R-doc` umbrellas aggregate them. That is how "the rules of the facets an anchor has" (the F001 phrase) is computed — facet presence is mostly folder/file presence, and each present facet contributes its embedded set.

**`include::` is composition — one semantics.** Under a `# RULESET` H1, `include:: R-Y, R-Z` means the set absorbs R-Y and R-Z (§2). Per-anchor **adoption is by traits**: the anchor's `.anchor` trait list activates rulesets, recursively ([[Warden Semantics]] § Rulesets). Decisions (`{NAME} Decisions.md`, spec: [[FCT Decisions]]) are **documentation Warden never computes against** — the broader recorded choices above the rules. Anything directly checkable is written only as a rule (by convention in the companion `# RULESET` directly after the `## Decisions` section), and a rule ties itself back to the decision it implements with a loose `implements D<N>` note.

---

## 4 · The condition — the conjunction when ∧ where ∧ if

A rule is a standing constraint that means the **conjunction** of its clauses; it fires only when all hold. The author writes the truth condition; the engine (§7) decides how to make it fire cheaply.

| Clause | Dimension | Answers | Spec |
|---|---|---|---|
| `when::` | **moment** (temporal) | *at what moment?* | §5 + [[Warden Events]] |
| `where::` | **place** (spatial, cross-cutting) | *concerning which file / directory / target?* | this section + [[FCT Ruleset]] § Where clause |
| `if::` | **test** (computed) | *and only if …?* — a **Python expression** (or prose, for an LLM judgment) | [[Warden Semantics]] § The condition |

`where::` is a deliberately **separate cross-cutting axis** rather than more depth in `when::`: the same place-predicate (`{ANCHOR}/**/*.md`) recurs under many moments (write it, read it, audit it), so it factors out. A passive file-check rule (today's default) is just one with no `when::` — it is evaluated whenever the audit visits, with `where::` doing all the binding.

### `where::` — the place selector

`where::` answers *which targets?* — the spatial cross-cut. Full grammar + exhaustive examples: [[FCT Ruleset]] § Where clause.

**Four scope kinds:**

| Form | Binds the rule to |
|---|---|
| `always` | every file the audit visits (the default when no `where::` is in force). |
| `file: <glob>` *(or bare `<glob>`)* | every file whose path matches the glob. |
| `anchor` | the anchor as a whole — a once-per-anchor structural / tree check. |
| `sentinel: <regex>` | any file containing a matching line, **regardless of path** — how `R-ruleset` catches every embedded ruleset. |

**Substitution variables** are `{ALL-CAPS}` in braces, expanded per adopting anchor: `{ANCHOR}` (root directory), `{NAME}` (name), `{SLUG}` (kebab slug) — the where-clause counterpart of `anchor.*` ([[Warden Semantics]] § Ambient and variables). The ALL-CAPS rule keeps `{ANCHOR}` (substitution) unambiguous from `{svg,png}` (glob alternation).

**Glob syntax** is gitignore/picomatch flavor: `*` `**` `?` `[a-z]` `{a,b}` alternation, trailing `/` for dirs, leading `!` for negation; `where::` takes a comma-separated **union** of positive patterns minus negated ones.

**Precedence** binds the open-ended set down to one effective context per rule: a rule's own `where::` > its set's `where::` > the built-in `always`. A non-universal set should declare an explicit `where::` rather than silently relying on `always` (`R-ruleset-10`).

> The richer trigger-axis taxonomy this generalizes toward — path / basename / folder / tool / trait / facet / mode / sibling-exists / always — is designed in [[F006 — Rule triggering — when the agent attends to rules|F006]]. `where::` is the shipped subset.

---

## 5 · The `when::` trigger — the moment taxonomy

`when::` answers *at what moment does this rule fire?* Every moment in the system lives in **one unified taxonomy** — a tree in which each node is refined into its children by exactly **one parameter**: `tool` → `tool:post` → `tool:post:Bash` → `tool:post:Bash:git-commit`. A rule names the moment at whatever depth it cares about; a shallow moment matches all its descendants. The full grammar, the dense per-group moment tables, the aliases, and the matching rules are the dedicated spec: **[[Warden Events]]**. Design lineage: [[F180 — When-trigger executable rules|F180]] (the `when::` clause + executables, shipped 2026-06-25), [[F091 — Trigger discipline|F091]] (the `compact` / `markdown-write` surfaces), [[F006 — Rule triggering — when the agent attends to rules|F006]] (the trigger-axis exploration).

**Moment groups** (each a recursive single-parameter subtree — see [[Warden Events]] for the full tables):

| Group | Root → refinement | Representative leaves | Friendly alias |
|---|---|---|---|
| Tool | `tool` → phase → name → arg | `tool:post:Write`, `tool:pre:Bash:rm` | — |
| Skill | `skill` → phase → name → action | `skill:post:audit-q`, `skill:post:audit:rules` | `skill:<name>` |
| Session | `session` → phase → source | `session:compact`, `session:start:startup` | `compact` |
| Content | `write`/`read` → kind → *(where)* | `write:markdown`, `read:rust` | `markdown-write` |
| VCS | `git` → op | `git:commit`, `git:push` | `on-commit` |
| Turn | `prompt` → phase | `prompt:submit`, `prompt:stop` | — |

The taxonomy is **open-ended and extensible**: a new trigger is one more parameter level beneath the deepest existing node (a new Bash subcommand is `tool:*:Bash:<new>`, never a new top-level concept), and only common moments earn a flat alias. Where a moment's next refinement is *spatial* (which file written/read), that refinement moves out to the cross-cutting `where::` clause (§4) — `when:: write:markdown` + `where:: {ANCHOR}/**/*.md`.

**Active rules carry a body that runs.** A passive rule (no `when::`) is evaluated when the audit visits. An active rule fires *at* its moment and runs its **body** — bare prose (the `tell` — an agent-directed steer, not a user-facing finding) or **backticked Python** (the `tell` / `edit` / `deny` / `run` verbs over the interpretation environment; no `def`, no magic name — [[Warden Semantics]]). Lineage: [[F180 — When-trigger executable rules|F180]] shipped the first executable shape (a fenced `def trigger(ctx) → list[str]`); the current model generalizes it to prose / backticked-Python bodies.

First live rule: `R-query-14` (push/commit interception in `FCT Query`) fires on `when:: skill:audit-q`; `audit-q.py` discovers and **autofires** `when:: skill:audit-q` rules on every run (`--when <event>` / `--list-when`).

**The `if::` test.** When `when::` (moment) and `where::` (place) don't capture the firing condition, a rule adds an `if::` — a **Python expression** over `file` / `anchor` / `git` / `event` (or prose, for an LLM judgment). It is the computed conjunct of the rule's truth condition (§4): cheap data-accessor tests (`git.is_dirty`) ride the live path, expensive ones (`ask_oracle`, `sh`) run at audit.

---

## 6 · The hook subsystem

The hook subsystem is the runtime that *delivers events* to the rule corpus — the always-on guardrail half of "two consumers, one corpus." `warden install --rust` writes the entries into `~/.claude/settings.json` (idempotent; `warden uninstall` reverses; `warden off` is the instant global kill). Every Warden entry invokes the same binary — `warden-rs hook` — which maps the event to its moment(s) and dispatches (§7a).

| Hook event · matcher | Handler | Moments delivered |
|---|---|---|
| `SessionStart` (all) | `warden-rs hook` | `session:start` / `session:compact` |
| `UserPromptSubmit` | `warden-rs hook` | `prompt:submit` |
| `PostToolUse` `Write\|Edit` | `warden-rs hook` | `tool:post:Write` / `tool:post:Edit`, `write:markdown` (+ the audit-on-write doc-fire) |
| `PreToolUse` `Skill` | `warden-rs hook` | `skill:pre:<name>` |
| `PreToolUse` `Bash\|Edit\|Write` | `warden-rs hook` | `tool:pre:<Tool>` — **the F131 veto surface**: a `deny` action here becomes `permissionDecision: deny` (fail-open everywhere else). Added 2026-07-06 — the arch/process adoption audit found the deny rules compiled but unreachable in real sessions. |
| `PreToolUse` `Bash` | `bash-guard.sh` *(bespoke)* | Pattern safety gate predating Warden; complements, never duplicated into, rule bodies. |
| `PostToolUse` `Read` / `SessionStart` / `Stop` / `PostToolUse` `WebFetch` | `maintain-hook.sh` / `load-role-hook.sh` / `messages-stop-hook.sh` / `webfetch-authwall-hook.sh` *(bespoke)* | Non-rule surfaces (background maintenance, role reload, Messages surfacing, authwall routing) — candidates for future rule migration. |

The bespoke `audit-on-write.sh` surface was **retired 2026-07-06** ([[F229 — Retire bespoke vault-wide hooks — M4 completion|F229]]): audit-on-write now rides Warden's own `write:markdown` doc-fire, base-implied on every anchor via [[anchor-base]].

**Anchor governance per moment (F229 A′).** A moment whose event carries an anchored file (`write:`/`read:`, file-bearing tool moments like `tool:pre:Edit`, the doc-fire) is governed by the **file's anchor** — the file's anchor owns the file, wherever the session sits. Everything else (Bash, session, prompt moments) is governed by the session's **cwd anchor**. Traits do not cascade into nested anchors; the nearest `.anchor` wins.

**Safety floor.** The doc-fire delegates fixer execution to `audit-plan.execute_on_write` — same fixer registry, same never-delete floor (a repair that would drop a letter or digit is reverted to a flag), same fix→re-check→message fallthrough ([[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]] lineage, M4a parity).

---

## 7 · The execution engine — compiler/installer + audit pipeline

The engine has **two faces over one corpus**: a **rule compiler/installer** that makes active (`when::`) rules fire *implicitly* at runtime moments, and the **on-demand audit pipeline** that runs *explicitly* over a target. Both consume the same rules; most rules run implicitly, the audit is the thorough explicit backstop.

### 7a · The rule compiler / installer (implicit path)

Conceptually a **compiler**, not an interpreter: it takes the rules active in an environment and *installs* them so they trigger, rather than re-resolving on every event.

1. **Resolve the active set.** Active rulesets are known at the **anchor level** — an anchor's `.anchor` traits activate sets ([[Warden Semantics]] § Rulesets). The installer resolves, per anchor, the flattened union of trait-activated + structurally-present sets.
2. **Index each rule.** It picks an **index key** per rule — usually the `when::` moment (so the runtime hook for that moment dispatches straight to it), sometimes the `where::` place (a `when:: always` rule that touches one rare file indexes cheaper by path). The author never chooses this; the firing semantics (the conjunction, §4) are identical either way.
3. **Pre-compile to an *indexed* per-moment dispatch.** All rules sharing a moment compile into one pre-built function, reached by an **index lookup** (moment → function), so fire time is *one call* — never a linear scan of the rule list (a scan is the last-resort fallback only). The function checks the residual `where::` + `if::` conjuncts and runs each rule's body.

This is the path the **performance budget** rides on — it instruments nearly every tool use and action (see [[Warden PRD]] § Performance).

#### The committed design — a resident daemon + a tiny notifier

*(Full detail — the daemon, the pluggable OS-selected notifiers, dual-mode file tracking, agent tracking, the oracle, and the cost picture — is [[Warden Runtime]].)* The hot path is a **stateful resident Python daemon** plus a **non-Python notifier**:

- **The daemon** is a long-running Python process holding the compiled, **indexed** rule set and **cached / lazy `ctx` state** in memory. Because it stays warm, evaluating a moment is a single pre-compiled function call over already-loaded rules — **sub-millisecond, and constant in total rule count**. It never pays interpreter startup. Its **lifecycle is the real complexity this buys**: it warm-starts lazily on the first hook (the first call pays the load+compile), **fails open** if it is down or still warming — never blocking the agent — and **recompiles** the affected index when a rule or `.anchor` changes (itself just a `write:*` moment it subscribes to).
- **The notifier** is what Claude Code's hook actually spawns: a tiny **non-Python** signaler whose only job is to tell the daemon a moment occurred (and, for a `tool:pre` veto, get the verdict back). It must avoid Python's ~30–80 ms startup. Two forms, both fast:
  - **Non-blocking** (a write, `tool:post`, a turn boundary): a one-line shell hook — `printf '%s' "$EVENT" >> warden.fifo` — `sh` boot + a FIFO write, **~1–3 ms** — and the daemon drains the FIFO **off the agent's critical path**.
  - **Blocking** (`tool:pre` veto): a request/response round-trip over a Unix socket (`nc -U`, or a tiny native binary), **~2–4 ms**, only on the rare veto moments.
- **Lazy `ctx`.** Most objects (`git`, `agent`, a file's parsed sections) aren't touched by most rules, so the daemon computes each **on first access and caches it per pass** — one `git` call, one content-hash, one `agent.state` read, shared across every rule that pass, regardless of rule count.
- **The pure-Python reference** ([[F212 — Python reference implementation|F212]]) runs the same logic cold and in-process — correct, not fast; the behavioral oracle the live dispatcher is differential-tested against on every commit. **The live dispatcher is the Rust binary** ([[F213 — Rust performance implementation + ms budget|F213]], both phases shipped 2026-07-05): `warden-rs hook` owns selection natively and crosses Python bodies to the resident daemon over the socket, re-interleaved into exact reference fire order — benched ~3.0 ms no-fire / ~3.7 ms Python-body-firing vs the Python hook's ~24 ms.
- **The oracle is a cheaper model, via Claude Code's *own* access — no API key.** An `if::` judgment / `ask_oracle` uses **Sonnet** (≈5× cheaper than the main agent; ~1¢/check) through whichever Claude-Code path the moment already has: a **sub-agent** of the `/audit` turn (the Task tool) on the audit path, the **running agent** (delegation) on the live path, or `claude -p` **headless** for an agent-less call. All ride the subscription — this is the same internal "one agent judges another" orchestration the product already does. The **external Sonnet API is opt-in** (for users who want to dodge subscription usage caps), not required — no key dance for the default path.

### 7b · The on-demand audit pipeline (explicit path)

The thorough backstop — `Resolve → Run → Judge → Fix`, mechanical-by-script and judgment-by-agent, cached so re-audits are cheap. Full design + ship status: [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]; pipeline detail: [[Audit Architecture]].

1. **Resolve** (`audit-plan.py`, pure compute, cached) — detect the target's facets → flatten the union of their sets through `include::` (§2) → bind each rule to concrete targets via `where::` (§4). A selector that matches nothing ⇒ the rule is **N/A** (skipped, never failed). Output: a `(rule-id, target, body-kind)` worklist.
2. **Run** the **Python-bodied** rules by script, verdict-cached by `(rule-id, rule-body-hash, target-content-hash)`.
3. **Judge** the **prose-bodied** (LLM-judged) rules by agent, batched, same cache key + `model-id`.
4. **Fix** at the automation level appropriate to the trigger (Informational / Online / Standard / Aggressive — a mask on which fixers may apply).

**Scheduling** picks iteration order by job: **file-major** for a single anchor (walk files, run each file's matched rules) and **rule-major** for a batch/vault sweep (one set in context over many homogeneous files — better cache locality). Same match set both ways.

**Three caches** make batch re-audits near-free: the flattened-rules cache (shared across anchors), the verdict cache (the big batch win), and the anchor-manifest/plan cache (skip re-resolve when the tree and rules are unchanged).

**Surfaces.** `/audit anchor` resolves `R-anchor`; `/audit doc` resolves `R-doc`. The `/rule` skill family — `check` / `triage` / `fix` / `sync` / `consider` / `discover` / `curate` — manages the project-local rules-file lifecycle (exception tables, grades, cross-project discovery) and feeds the same corpus.

### 7c · The interpretation environment — the lazy `ctx` services

Both fire paths (7a live, 7b audit) evaluate rule bodies against this environment. Bodies and `if::` guards run over a **lazy `ctx`**: every object is computed on first access and cached per pass, and **reads never raise** (a missing transcript, a git-less dir, an unreadable file degrade to empty values, never a blocked hook). Three shipped services extend the base `file`·`anchor`·`git`·`event` views:

| Service | Module | What it provides |
|---|---|---|
| **Agent state** ([[F216 — Agent-state model — sensing what the agent is doing\|F216]]) | `warden_agent.py` | `ctx.agent` — the mechanical classifier (liveness → in-flight → turn-end → decay ladder): `state`, `skill`, `is_asking`, `state_seconds`, `open_tasks`. Session registry + bounded moment ledger live in the daemon; history rebuilds from the transcript tail. |
| **Turn content + oracle** ([[F217 — Conversation-content gating — rules on what was said\|F217]]) | daemon + `warden_fire` | `agent.turn` / `agent.response` lazy views (capped head+tail) and `ask_oracle` (blocking, prompt-hash cached, fail-silent). Two loop-prevention walls: oracle sessions are moment-silent, and the daemon dedups once per `(rule, session, turn)`. |
| **Re-eval economy** ([[F215 — Re-evaluation economy — the significant-edit gate\|F215]]) | `warden_reval.py` | per-`(rule, file)` last-evaluated store (atomic writes) + `FileView`/`DiffView`, so `file.diff`-guarded rules re-judge only on significant change; sub-threshold edits accumulate until they jointly cross the gate. |

The compiler marks rules `file_bearing` / `turn_bearing` so both fire paths can wholesale-skip the services a moment's rules never read.


---

## 8 · Built modules — the subsystem → module map

What actually shipped, one row per source module, every module owned by exactly one subsystem (R-ownership-03; added by the 2026-07-06 adoption audit — this section is the map the audit found missing). Code lives at `warden/engine/` (Python) and `warden/rs/` (Rust crate `warden-rs`).

| Subsystem | Module | Role |
|---|---|---|
| Scan | `engine/warden_scan.py` | vault walk → ruleset file index + content hash (the recompile-cache key) |
| Compile | `engine/warden_compile.py` | rules → IR (`~/.warden/rules-ir.json`) + emitted `rules_all.py`; `include::` flatten; `ANCHOR_BASE_TRAITS`; `declared_traits` snapshot |
| Fire | `engine/warden_fire.py` | moment dispatcher — indexed dispatch, active-set gating, `effective_traits`, lazy `ctx` build, `DENY:` sentinel |
| Reference loop | `engine/warden_engine.py` | lazy scan→compile→fire in one process — the behavioral oracle |
| Doc-fire | `engine/warden_docfire.py` | the audit-on-write path — matches doc rules to the written file, delegates check+fix to `audit-plan.execute_on_write` |
| Live hook (reference) | `engine/warden_hook.py` | Python dispatcher: event→moments, per-moment anchor governance, `emit()` deny/steer split — the differential target |
| Resident interpreter | `engine/warden_daemon.py` | warm preloaded IR + rule bodies on a Unix socket; auto-reload, idle-exit, session registry + moment ledger |
| Agent state | `engine/warden_agent.py` | the mechanical agent-state classifier behind lazy `ctx.agent` |
| Re-eval economy | `engine/warden_reval.py` | per-(rule, file) last-evaluated store + `FileView`/`DiffView` — the significant-edit gate (F215) |
| CLI | `engine/warden` | `on · off · compile · install · uninstall · status · daemon · fire` |
| Rust selection | `rs/src/lib.rs` | IR consumer — fire-plan computation byte-identical to the reference |
| Rust live dispatcher | `rs/src/hook.rs` | the installed hook: kill switch, moments, anchor/traits, daemon IPC for Python bodies, deny-aware `emit` |
| Test regime | `engine/test_warden_*.py`, `rs` `cargo test`, `Warden Corpus/` | the five layers of §The testing regime |

## 9 · Activation and governance — which rules are in force where

Load-bearing policy with real failure modes (the 2026-07-06 veto-surface audit found all three of its layers misconfigured at once), promoted from adoption footnotes to a subsystem-rank section by the same audit.

- **Adoption is by traits.** An anchor's `.anchor` `traits:` list activates rulesets (trait key = ruleset name minus `R-`); umbrella traits pull their whole `include::` closure (§2). Nothing is auto-adopted.
- **[[anchor-base]] is implicit everywhere.** Every anchor carries `anchor-base` plus its compiled members (`ir.base_traits` — today `audit-on-write`, `ob-remote-ops`) by construction; the vault-root anchor (`~/ob/kmr/.anchor`) catches otherwise-unowned paths, so "un-anchored vault file" is not an escape.
- **Governance is per moment (F229 A′).** Any moment whose event carries an anchored file — `write:`/`read:`, file-bearing tool moments like `tool:pre:Edit`, the doc-fire — is governed by the **file's anchor** (the file's anchor owns the file, wherever the session sits); Bash/session/prompt moments are governed by the session's **cwd anchor**.
- **Nearest `.anchor` wins — no cascade.** A nested sub-anchor *shadows* its parent's adoption entirely. Consequence: guard rules must be adopted where the guarded files actually live (a Track sub-anchor, not just the project root) — see [[Warden Interface]] § Non-guarantees.
- **The kill switch outranks everything.** `warden off` silences every layer above instantly; there is no per-anchor or per-trait opt-out yet (future `-trait` negation, per [[anchor-base]]).

## Invariants

- **Sentinels are load-bearing.** The all-caps `RULESET` and `RULE` are mechanical markers grep/lint/flatten depend on — never lowercase, rename, or invent alternates.
- **Identifiers are forever.** `R-<slug>-NN` numbers are zero-padded, unique within the slug, monotonic, never recycled; composition never renumbers.
- **A rule is a conjunction.** It fires iff `when::` (moment) ∧ `where::` (place) ∧ its `if::` (test) hold. The author writes the truth condition; the compiler picks the dispatch (index by-when or by-where) — firing semantics are identical either way.
- **One unified moment taxonomy.** Every trigger is a node in the single tree of [[Warden Events]], refined one parameter per level; new triggers extend an existing node, never add a parallel concept.
- **Never wipe authored content.** Auto-fix is gated by `aow-safety.py`; the never-delete floor holds on every automated path.
- **One corpus, two paths.** The implicit compiler/installer (runtime moments) and the explicit audit pipeline run the *same* rules through one `when::`/`where::`/`if::` vocabulary; they differ only in trigger and automation level.

## Sources

| Subsystem | Source of truth |
|---|---|
| `when::` moment taxonomy + conjunction model | [[Warden Events]] |
| Prior art + integration/dependency policy | [[Warden Survey]], [[Warden Integration Strategy]] |
| Rule + Ruleset format, `where::` | [[FCT Ruleset]] |
| Decisions doctrine (documentation layer, companion ruleset, `implements D<N>`) | [[FCT Decisions]] |
| Catalog + folder convention + facet embedding | [[Rulesets]], [[F133 — Rulesets folder convention + facet embedding\|F133]] |
| Rules-vs-decisions split, flatten tooling | [[F132 — Rules Migration\|F132]] |
| `when::` clause + executable rules | [[F180 — When-trigger executable rules\|F180]] |
| Trigger discipline (`compact` / `markdown-write`) | [[F091 — Trigger discipline\|F091]] |
| Trigger-axis taxonomy (open-ended contexts) | [[F006 — Rule triggering — when the agent attends to rules\|F006]] |
| Execution engine (Resolve→Run→Judge→Fix, caches) | [[F001 — Rule-driven audit engine — resolve, run, judge\|F001]], [[Audit Architecture]] |
| On-write hook + safety guard | [[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]] |
| Standard rulesets (historical first design) | [[F017 — Standard Rule Sets\|F017]] |

## Changes since [[2026-07-06 Warden Architecture]]

*(Snapshot taken at the start of the 2026-07-06 `/architect update` run; greenfield input: [[2026-07-06 Warden Architecture (greenfield)]].)*

- **Added § 7c — The interpretation environment**: the lazy `ctx` services (agent-state F216, turn content + oracle F217, re-eval economy F215) were shipped subsystem-weight code the doc treated as scattered footnotes; now one table with the reads-never-raise discipline and the `file_bearing`/`turn_bearing` skip marks.
- **Added § 9 — Activation and governance**: traits, anchor-base, per-moment file-vs-cwd governance, nearest-wins shadowing, and the kill switch, promoted to subsystem rank (the greenfield draft's strongest delta — this policy layer had three simultaneous misconfigurations at the 2026-07-06 audit).
- **Proposed but not adopted**: the greenfield draft's seven-subsystem restructure of the whole doc (Corpus & Language / Compiler / Live Dispatch / Resident Interpreter / Interpretation Environment / Doc-Fire Bridge / Activation & Governance). The live doc's define→compose→run pedagogy kept; the draft remains in `Versions/` as the alternative decomposition.
