---
description: "the unified map: rules, rulesets, `include::` containment, the `when ∧ where ∧ if` binding, the hook subsystem, and the compiler/audit engine"
---

# Warden Architecture

The rule system is how a portable, audit-checkable constraint is **defined** (the `RULE` / `RULESET` primitives), **composed** (`include::` containment), **placed** in the vault and **adopted** by an anchor, **bound** to the contexts (`where::`) and events (`when::`) that should trigger it, and finally **run** by two consumers — the on-demand audit/rule engine and the always-on hook subsystem — over one shared corpus. This page is the structural overview that ties those subsystems together; each subsystem's prescriptive spec lives in the facet or feature doc cited in its section.

> [!info] Scope
> This is the architecture *of the rule language and its runtime*. The prescriptive file-format spec is [[FCT Ruleset]]; the per-audit execution pipeline is [[Audit Architecture]] and [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]. This page is the connective tissue: it names the subsystems, shows how they fit, and points at the source of truth for each.

## Rule system — the four layers

![[Warden Architecture.svg|1100]]

[↗ Open figure](Warden%20Architecture.svg) · [Index ↓](#figure-index) · [✎ Edit source](Warden%20Architecture.d2)

### Figure index

| Layer | Subsystem | What it is |
|---|---|---|
| **1 · Definition** | The Rule | The atomic, greppable primitive: `RULE R-<slug>-NN (tier)` + body. → [§1](#1--definition--the-rule-and-the-ruleset) |
| | The Ruleset | A named bundle: `# RULESET R-<slug>` + `include:: / where:: / when:: / description::` header. → [§1](#1--definition--the-rule-and-the-ruleset) |
| **2 · Composition & placement** | Containment | `include::` DAG; umbrellas (`R-anchor`, `R-doc`, `R-diagram`); depth-first flatten; no-renumber. → [§2](#2--containment-and-inheritance--include) |
| | Three homes | Catalog `R-<slug>.md` · embedded `# RULESET` in a facet/skill/discipline · anchor-local `{NAME} Rules.md`. → [§3](#3--placement-and-association--where-rules-live) |
| | Adoption | An anchor's `{NAME} Decisions.md` `include::`s a ruleset and cites rules. → [§3](#3--placement-and-association--where-rules-live) |
| **3 · Binding** | conjunction `when ∧ where ∧ if` | A rule fires only when all clauses hold; the engine picks the dispatch. → §4 |
| | `where::` | The **place** selector (spatial, cross-cutting): `always` / `file:<glob>` / `anchor` / `sentinel:<regex>`. → §4 |
| | `when::` | The **moment** trigger (temporal): the unified taxonomy → [[Warden Trigger Taxonomy]]. → §5 |
| | `if::` | The optional **guard** (condition): declarative or Python. → §5 |
| **4 · Execution** | Compiler / installer | Indexes active rules onto runtime moments; pre-compiles per-moment modules (implicit path). → §7a |
| | On-demand audit | `audit-plan.py` — Resolve → Run → Judge → Fix, three caches (explicit path). → §7b |
| | Hook subsystem | `settings.json` hooks deliver the moments. → §6 |

---

## 1 · Definition — the Rule and the Ruleset

Two primitives, both spec'd prescriptively in [[FCT Ruleset]]. Worked instances: [[R-diagram]] (large umbrella), [[CAE Rules]] (anchor-local), and the self-applying `# RULESET R-ruleset` embedded in [[FCT Ruleset]] itself.

### The Rule — the atomic unit

A rule is a markdown **heading** whose first token is the all-caps `RULE` sentinel, followed by an immutable identifier. The sentinel makes every rule greppable anywhere in the vault (`grep -rnE '^#+\s+RULE\s+R-'`), not just inside ruleset files.

| Part | Form | Notes |
|---|---|---|
| Heading | `<H> RULE R-<slug>-NN` | Any heading level; H3 is customary inside a `# RULESET` block. |
| Name | `— <short name>` | Optional em-dash title. |
| Tier | `(tracked)` / `(stated)` / `(sampled)` / `(checked)` | The verification posture — see table below. |
| Body — statement | first paragraph | Declarative: what is required or forbidden. |
| Body — `Check pattern:` | a `**Check pattern:**` paragraph | How a violation is detected. Required for `checked` / `sampled`. |
| Body — `Why:` | a `**Why:**` paragraph | Optional rationale / prior-incident context. |
| Body — `Exceptions:` | a `**Exceptions:**` block | Optional acknowledged-exception table or list. |

The **identifier `R-<slug>-NN`** is the rule's permanent handle: `NN` is zero-padded, two-digit, monotonic-forever within the slug's namespace, and **never recycled**. Cross-document references use the bare string (`see [[R-testing-04]]`).

**Audit tiers** declare how a rule is verified — they are the mechanical-vs-judgment split the engine rides on (§7):

| Tier | Verified by |
|---|---|
| `tracked` | nobody — recorded for awareness only. |
| `stated` | the **agent** — judgment, batched + cached. |
| `sampled` | script where possible, else agent (risk-prioritized). |
| `checked` | a **script** — deterministic, content-hash cached. |

A `checked` rule additionally carries a machine-ref `check::` field naming a checker primitive (`regex_present`, `frontmatter_has`, …); the prose `Check pattern:` stays the human spec. Tiers are aspirational ladders — a rule starts `stated` and graduates to `checked` once the checker is written.

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

Rules live with the spec that owns them. There are **three homes**, plus a fourth file (`{NAME} Decisions.md`) where an anchor *adopts* them. Folder convention + facet-embedding: [[F133 — Rulesets folder convention + facet embedding|F133]].

```
ob-skills/library/Rulesets/          ← (1) the shared catalog, organized per-domain
├── Rulesets.md                          catalog index (see Rulesets in §Sources)
├── Diagram/R-diagram.md                 standalone R-<slug>.md (folder-file convention)
├── R-anchor/R-anchor.md                 umbrella
└── R-ob/R-ob-state-mgt.md               owner-scoped set

ob-skills/facets/.../FCT Testing.md   ← (2) embedded # RULESET R-testing inside a facet spec
ob-skills/skills/.../<skill> spec     ← (2) embedded set inside a skill/discipline spec

{NAME}/{NAME} Design/{NAME} Rules.md  ← (3) anchor-local rules too specific to share (rare)
{NAME}/{NAME} Design/{NAME} Decisions.md ← adoption surface (below)
```

| Home | When used | Example |
|---|---|---|
| **Catalog** — standalone `R-<slug>.md` | cross-cutting, reusable, owner- or trait-scoped rulesets | [[R-diagram]] |
| **Embedded** — `# RULESET` inside a facet / skill / discipline spec | rules that *are* the structural spec for an artifact kind | `R-ruleset` in [[FCT Ruleset]]; `R-testing` in `FCT Testing` |
| **Anchor-local** — `{NAME} Rules.md` | rules truly specific to one anchor | [[CAE Rules]] |

**Association with facets and skills** is the embedded home: each CAB facet, skill, and discipline spec carries its own `# RULESET R-<facet>` block, and the `R-anchor` / `R-doc` umbrellas aggregate them. That is how "the rules of the facets an anchor has" (the F001 phrase) is computed — facet presence is mostly folder/file presence, and each present facet contributes its embedded set.

**Adoption vs composition — same syntax, different host H1.** `include::` means *compose* under a `# RULESET` H1 and *adopt* under a `# {NAME} Decisions` H1 (spec: [[FCT Decisions]]):

| Host H1 | `include:: R-Y, R-Z` means |
|---|---|
| `# RULESET R-X` | **composition** — R-X absorbs R-Y and R-Z (§2). |
| `# {NAME} Decisions` | **adoption** — the anchor commits to following R-Y and R-Z. |

An adopting anchor's `{NAME} Decisions.md` then (a) lists its adopted sets on `include::`, (b) maps each adopted rule to its local implementation in an `## Adoption implementation map` table, and (c) records anchor-specific D-records that cite rules via a `**Cites:** [[R-…-NN]]` line. Audit walks the decisions, collects every `Cites:`, flattens through `include::`, and verifies each cited rule. Rules are portable constraints; decisions are the anchor-specific applications that cite them.

---

## 4 · Binding — the conjunction `when ∧ where ∧ if`

A rule is a standing constraint that means the **conjunction** of its clauses; it fires only when all hold. The author writes the truth condition; the engine (§7) decides how to make it fire cheaply.

| Clause | Dimension | Answers | Spec |
|---|---|---|---|
| `when::` | **moment** (temporal) | *at what moment?* | §5 + [[Warden Trigger Taxonomy]] |
| `where::` | **place** (spatial, cross-cutting) | *concerning which file / directory / target?* | this section + [[FCT Ruleset]] § Where clause |
| `if::` *(optional guard)* | **condition** | *and only if …?* | §5 (guards) + [[Warden Trigger Taxonomy]] |

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

**Predefined tokens** are `{ALL-CAPS}` in braces, substituted per adopting anchor: `{ANCHOR}` (the anchor's root directory) and `{NAME}` (its name string). `{VAULT}` and `{REPO}` are reserved. The ALL-CAPS rule is what keeps `{ANCHOR}` (substitution) unambiguous from `{svg,png}` (glob alternation).

**Glob syntax** is gitignore/picomatch flavor: `*` `**` `?` `[a-z]` `{a,b}` alternation, trailing `/` for dirs, leading `!` for negation; `where::` takes a comma-separated **union** of positive patterns minus negated ones.

**Precedence** binds the open-ended set down to one effective context per rule: a rule's own `where::` > its set's `where::` > the built-in `always`. A non-universal set should declare an explicit `where::` rather than silently relying on `always` (`R-ruleset-10`).

> The richer trigger-axis taxonomy this generalizes toward — path / basename / folder / tool / trait / facet / mode / sibling-exists / always — is designed in [[F006 — Rule triggering — when the agent attends to rules|F006]]. `where::` is the shipped subset.

---

## 5 · The `when::` trigger — the moment taxonomy

`when::` answers *at what moment does this rule fire?* Every moment in the system lives in **one unified taxonomy** — a tree in which each node is refined into its children by exactly **one parameter**: `tool` → `tool:post` → `tool:post:Bash` → `tool:post:Bash:git-commit`. A rule names the moment at whatever depth it cares about; a shallow moment matches all its descendants. The full grammar, the dense per-group moment tables, the aliases, and the matching rules are the dedicated spec: **[[Warden Trigger Taxonomy]]**. Design lineage: [[F180 — When-trigger executable rules|F180]] (the `when::` clause + executables, shipped 2026-06-25), [[F091 — Trigger discipline|F091]] (the `compact` / `markdown-write` surfaces), [[F006 — Rule triggering — when the agent attends to rules|F006]] (the trigger-axis exploration).

**Moment groups** (each a recursive single-parameter subtree — see [[Warden Trigger Taxonomy]] for the full tables):

| Group | Root → refinement | Representative leaves | Friendly alias |
|---|---|---|---|
| Tool | `tool` → phase → name → arg | `tool:post:Write`, `tool:pre:Bash:rm` | — |
| Skill | `skill` → phase → name → action | `skill:post:audit-q`, `skill:post:audit:rules` | `skill:<name>` |
| Session | `session` → phase → source | `session:compact`, `session:start:startup` | `compact` |
| Content | `write`/`read` → kind → *(where)* | `write:markdown`, `read:rust` | `markdown-write` |
| VCS | `git` → op | `git:commit`, `git:push` | `on-commit` |
| Turn | `prompt` → phase | `prompt:submit`, `prompt:stop` | — |

The taxonomy is **open-ended and extensible**: a new trigger is one more parameter level beneath the deepest existing node (a new Bash subcommand is `tool:*:Bash:<new>`, never a new top-level concept), and only common moments earn a flat alias. Where a moment's next refinement is *spatial* (which file written/read), that refinement moves out to the cross-cutting `where::` clause (§4) — `when:: write:markdown` + `where:: {ANCHOR}/**/*.md`.

**Active rules carry an executable.** A passive rule (no `when::`) is a file check evaluated when the audit visits. An active rule fires *at* its moment and may carry a fenced Python `def trigger(ctx) -> list[str]` returning **agent-directed steer messages** (not user-facing findings) — the F180 shape:

```python
def trigger(ctx) -> list[str]:
    # ctx exposes: anchor name + path, Git aspect (PR / Commit / NoGit from
    # .anchor traits), and relevant content (e.g. ctx.queries_text).
    # Returned strings STEER THE AGENT; they do not bother the user.
    ...
```

First live rule: `R-query-14` (push/commit interception in `FCT Query`) fires on `when:: skill:audit-q`; `audit-q.py` discovers and **autofires** `when:: skill:audit-q` rules on every run (`--when <event>` / `--list-when`).

**Guards (`if::`) — the optional conditional.** When the moment (`when::`) and the place (`where::`) don't capture the firing condition, a rule adds one or more `if::` guards — declarative (`if:: git-aspect == Commit`, `if:: trait has Code`) compiling to table lookups, or a Python `def guard(ctx) -> bool` for the rare arbitrary case. Multiple guards AND together; a guard is just another conjunct of the rule's truth condition (§4).

---

## 6 · The hook subsystem

The hook subsystem is the runtime that *delivers events* to the rule corpus — the always-on guardrail half of "two consumers, one corpus." It is configured declaratively in `~/.claude/settings.json`; no install step. Component overview: [[Audit Architecture]] § Distillation → hook.

```json
"hooks": {
  "PreToolUse":  [{ "matcher": "Bash",              "hooks": ["bash-guard.sh"] }],
  "PostToolUse": [{ "matcher": "Read",              "hooks": ["maintain-hook.sh"] },
                  { "matcher": "Write|Edit|MultiEdit","hooks": ["audit-on-write.sh"] }],
  "SessionStart":[{ "matcher": "compact|startup",   "hooks": ["load-role-hook.sh"] }],
  "Stop":        [{                                 "hooks": ["messages-stop-hook.sh"] }]
}
```

| Hook event | Script | Role in the rule system |
|---|---|---|
| `PreToolUse` (Bash) | `bash-guard.sh` | Safety gate — blocks dangerous commands before they run. |
| `PostToolUse` (Write/Edit) | `audit-on-write.sh` | The `markdown-write` surface: runs `audit-plan --mode doc --on-write` over the written `.md`, applies only mechanical fixes, surfaces the rest. Throttled; pinned to the **Online** automation level. |
| `PostToolUse` (Read) | `maintain-hook.sh` | 30-second-throttled background maintenance kick; non-blocking. |
| `SessionStart` (compact/startup) | `load-role-hook.sh` | The `compact` surface: reloads the role's POST-COMPACT block into context. |
| `Stop` | `messages-stop-hook.sh` | Surfaces anchor Messages on pause. |

**Distillation → fast module.** The on-demand engine and the on-write hook run the *same* rule corpus through two triggers. To keep the write-time path fast, `/distill` merges the applicable rule bodies into one compiled module under `~/.config/ob-skills/hooks/`, and `audit-on-write.sh` runs that module on every write rather than re-resolving the whole DAG.

**Safety floor.** `aow-safety.py` gates every auto-fix: a repair that would drop a letter or digit is reverted to a flag — the mechanical floor under the never-delete invariant ([[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]]). The on-write hook only ever applies corrupting-character-safe fixers; structural fixers are withheld from the always-on path.

---

## 7 · The execution engine — compiler/installer + audit pipeline

The engine has **two faces over one corpus**: a **rule compiler/installer** that makes active (`when::`) rules fire *implicitly* at runtime moments, and the **on-demand audit pipeline** that runs *explicitly* over a target. Both consume the same rules; most rules run implicitly, the audit is the thorough explicit backstop.

### 7a · The rule compiler / installer (implicit path)

Conceptually a **compiler**, not an interpreter: it takes the rules active in an environment and *installs* them so they trigger, rather than re-resolving on every event.

1. **Resolve the active set.** Active rulesets are known at the **anchor level** — an anchor adopts sets via `{NAME} Decisions.md` (§3). The installer resolves, per anchor, the flattened union of adopted + structurally-present sets.
2. **Index each rule.** It picks an **index key** per rule — usually the `when::` moment (so the runtime hook for that moment dispatches straight to it), sometimes the `where::` place (a `when:: always` rule that touches one rare file indexes cheaper by path). The author never chooses this; the firing semantics (the conjunction, §4) are identical either way.
3. **Pre-compile to a fast per-moment module.** All rules sharing a moment compile into one module: a generalization of today's `/distill`. At fire time the runtime hook (§6) for that moment runs the module, which checks the residual `where::` + `if::` conjuncts and runs each rule's `trigger`/`check`.

This is the path the **performance budget** rides on — it instruments nearly every tool use and action, so the per-moment module must be tiny and fast (see [[Warden PRD]] § Performance; reference impl in Python, performance impl in Rust per the roadmap).

### 7b · The on-demand audit pipeline (explicit path)

The thorough backstop — `Resolve → Run → Judge → Fix`, mechanical-by-script and judgment-by-agent, cached so re-audits are cheap. Full design + ship status: [[F001 — Rule-driven audit engine — resolve, run, judge|F001]]; pipeline detail: [[Audit Architecture]].

1. **Resolve** (`audit-plan.py`, pure compute, cached) — detect the target's facets → flatten the union of their sets through `include::` (§2) → bind each rule to concrete targets via `where::` (§4). A selector that matches nothing ⇒ the rule is **N/A** (skipped, never failed). Output: a `(rule-id, tier, target, checker)` worklist.
2. **Run** mechanical (`checked`) rules by script, verdict-cached by `(rule-id, rule-body-hash, target-content-hash)`.
3. **Judge** the residue (`stated`, unscriptable `sampled`) by agent, batched, same cache key + `model-id`.
4. **Fix** at the automation level appropriate to the trigger (Informational / Online / Standard / Aggressive — a mask on which fixers may apply).

**Scheduling** picks iteration order by job: **file-major** for a single anchor (walk files, run each file's matched rules) and **rule-major** for a batch/vault sweep (one set in context over many homogeneous files — better cache locality). Same match set both ways.

**Three caches** make batch re-audits near-free: the flattened-rules cache (shared across anchors), the verdict cache (the big batch win), and the anchor-manifest/plan cache (skip re-resolve when the tree and rules are unchanged).

**Surfaces.** `/audit anchor` resolves `R-anchor`; `/audit doc` resolves `R-doc`. The `/rule` skill family — `check` / `triage` / `fix` / `sync` / `consider` / `discover` / `curate` — manages the project-local rules-file lifecycle (exception tables, grades, cross-project discovery) and feeds the same corpus.

---

## Invariants

- **Sentinels are load-bearing.** The all-caps `RULESET` and `RULE` are mechanical markers grep/lint/flatten depend on — never lowercase, rename, or invent alternates.
- **Identifiers are forever.** `R-<slug>-NN` numbers are zero-padded, unique within the slug, monotonic, never recycled; composition never renumbers.
- **A rule is a conjunction.** It fires iff `when::` (moment) ∧ `where::` (place) ∧ every `if::` (guard) hold. The author writes the truth condition; the compiler picks the dispatch (index by-when or by-where) — firing semantics are identical either way.
- **One unified moment taxonomy.** Every trigger is a node in the single tree of [[Warden Trigger Taxonomy]], refined one parameter per level; new triggers extend an existing node, never add a parallel concept.
- **Never wipe authored content.** Auto-fix is gated by `aow-safety.py`; the never-delete floor holds on every automated path.
- **One corpus, two paths.** The implicit compiler/installer (runtime moments) and the explicit audit pipeline run the *same* rules through one `when::`/`where::`/`if::` vocabulary; they differ only in trigger and automation level.

## Sources

| Subsystem | Source of truth |
|---|---|
| `when::` moment taxonomy + conjunction model | [[Warden Trigger Taxonomy]] |
| Prior art + integration/dependency policy | [[Warden Survey]], [[Warden Integration Strategy]] |
| Rule + Ruleset format, `where::` | [[FCT Ruleset]] |
| Adoption, Decisions, Cites | [[FCT Decisions]] |
| Catalog + folder convention + facet embedding | [[Rulesets]], [[F133 — Rulesets folder convention + facet embedding\|F133]] |
| Rules-vs-decisions split, flatten tooling | [[F132 — Rules Migration\|F132]] |
| `when::` clause + executable rules | [[F180 — When-trigger executable rules\|F180]] |
| Trigger discipline (`compact` / `markdown-write`) | [[F091 — Trigger discipline\|F091]] |
| Trigger-axis taxonomy (open-ended contexts) | [[F006 — Rule triggering — when the agent attends to rules\|F006]] |
| Execution engine (Resolve→Run→Judge→Fix, caches) | [[F001 — Rule-driven audit engine — resolve, run, judge\|F001]], [[Audit Architecture]] |
| On-write hook + safety guard | [[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]] |
| Standard rulesets (historical first design) | [[F017 — Standard Rule Sets\|F017]] |
