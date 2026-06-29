---
description: "the rule language — the file format for a rule and a ruleset (sentinels, clauses, tiers, composition)"
---
# Warden Rule

The format of the Warden rule language: what a **rule** is and what a **ruleset** is, as written in a file. A rule is the atomic, audit-checkable constraint; a ruleset is a named bundle of rules that travel together. This page defines both — the sentinels, header fields, rule body, tiers, naming, and composition. The two clause vocabularies a rule binds with — `when::` (the moment) and `where::` (the place) — have their own specs ([[Warden Events]] and [[FCT Ruleset]] § Where clause).

Worked instances: [[R-diagram]] (a large umbrella), [[CAE Rules]] (an anchor-local set), and the self-applying `R-ruleset` block in [[FCT Ruleset]].

## The rule

![[Warden Rule Example.svg]]

*An example rule.* ✎ [regenerate the figures](warden-rule-figures.py)

A rule is a markdown **heading** whose first token is the all-caps `RULE` sentinel + a permanent identifier — so it is greppable anywhere (`grep -rnE '^#+\s+RULE\s+R-'`), not only inside a ruleset. The heading **binds** the rule; the body says **what it checks**. One table, two parts:

| Part | Form / when present | Notes |
|---|---|---|
| `<H> RULE R-<slug>-NN` | the heading (any H-level; H3 customary) | `RULE` = the all-caps sentinel grep / lint depend on |
| `R-<slug>-NN` | the identifier | the rule's permanent handle (see [[#Naming]]) |
| `— <short name>` | optional | brief human title |
| `(<tier>)` | `checked` / `sampled` / `stated` / `tracked` | verification posture (see [[#Tiers and check primitives]]) |
| **Rule body ↓** | | |
| declarative statement | first paragraph | what is required or forbidden |
| `**Check pattern:**` | for `checked` / `sampled` | how a violation is detected (the human spec) |
| `check::` *or* a ```` ```python ```` block | for mechanical `checked` | a named checker **primitive** (`check:: …`), or an embedded `def check(ctx)` Python block for custom logic |
| `when::` / `where::` / `if::` | optional | the rule's own binding clauses, overriding the set's |
| `rerun::` | optional | re-evaluation economy — `always` (default) or `significant` to re-run an expensive rule only on significant change ([[F215 — Re-evaluation economy — the significant-edit gate\|F215]]) |
| `**Why:**` | optional | rationale / prior-incident context |
| `**Exceptions:**` | optional | acknowledged-exception table or list |

## The ruleset

![[Warden Ruleset Example.svg]]

*An example ruleset* (a set-level `where::` that two rules share; the second overrides it). ✎ [regenerate](warden-rule-figures.py)

A ruleset is a `# RULESET R-<slug>` block plus a prescriptive header. The all-caps `RULESET` sentinel identifies the block unambiguously to lint / flatten / compile.

| Header line | Required? | Purpose |
|---|---|---|
| `# RULESET R-<slug>` | yes | sentinel H1 + the set's identifier |
| `include:: …` | yes (may be empty) | composition / adoption (see [[#Composition — include]]); the empty line is the slot |
| `where:: …` | optional | set-level default **place** for every rule ([[FCT Ruleset]] § Where clause) |
| `when:: …` | optional | set-level default **moment** for every rule ([[Warden Events]]) |
| `description:: …` | yes | one-line (8–15 word) tagline; no `::` in the value |
| prose body | optional | provenance, attribution, factoring history; any length |

`include::` / `where::` / `when::` / `description::` are Obsidian Dataview inline fields (`key:: value`). A single file may carry **multiple** rulesets — each `# RULESET` H1 opens a new scope whose header fields apply until the next H1. Standalone `R-<slug>.md` files are body-only (no YAML frontmatter); an embedded block lives inside a host doc that may have its own frontmatter.

## The three clauses — when ∧ where ∧ if

A rule means the **conjunction** of its clauses (full model: [[Warden Events]] § The conjunction model). Each is one key — which is what lets a rule round-trip to flat YAML for the importer.

| Clause | Binds to | Spec |
|---|---|---|
| `when::` | the **moment** it fires at | [[Warden Events]] |
| `where::` | the **place** (file/dir/target) it concerns | [[FCT Ruleset]] § Where clause |
| `if::` | a **condition** that must hold *(declarative form planned)* | [[Warden Events]] § Guards |

**Precedence:** a rule's own clause overrides its set's; absent both, the defaults are `when:: always-passive` (a file check, no event) and `where:: always`.

## The body and check primitives

> **A rule is a *condition* (`when` / `where` / `if`) and a *body* (one or more actions).** The body is the part that runs; an action is a `check::` primitive, a `python` block, LLM **prose**, a `message::`, or a `fix`. The operational model — how the condition triggers and the body emits reports — is **[[Warden Semantics]]**.

The **tier** annotation (`(checked)` / `(stated)` / `(sampled)` / `(tracked)`) that older rules carry is an **optional posture hint, not a separate concept** — the body already shows whether a script (`check::` / `python`) or the LLM (prose) decides. Keep it for at-a-glance readability if you like; nothing in the engine requires it (`checked` = a script body, `stated` = an LLM body). Worked examples of every body kind are in [[Warden Examples]].

A `checked` rule's check is written one of two ways: a named **primitive** via `check::` (e.g. `` check:: regex_present `^#+ RULESET R-` ``), or — when no primitive fits — an embedded ```` ```python ```` `def check(ctx) -> bool` block (the same executable-rule mechanism [[F180 — When-trigger executable rules|F180]] uses for `trigger` / `guard`). **Primitives run on the fast native path; arbitrary Python runs on the slower Python path** — so prefer a primitive when one fits. The prose `**Check pattern:**` stays the human spec. The primitive vocabulary is a **superset of Vale's check-type taxonomy** (existence / substitution / occurrence / … native; spelling / metric / sequence / script via an opt-in Vale adapter) — see [[Warden Integration Strategy]] D8.

**Glob and regex values are backticked** — `` where:: `{ANCHOR}/**/*.md` ``, `` check:: regex_present `^…` `` — the standing convention ([[F007 — Backtick all where expressions — parser swap|F007]]) so the expression never trips the Obsidian renderer; the parser strips the backticks. Tiers are aspirational ladders: a rule starts `stated` and graduates to `checked` once its check exists.

## Composition — include

A ruleset absorbs others by naming them on `include::` (bare names or `[[wiki-links]]`, mixed). This is the language's single inheritance mechanism.

**Flatten semantics:** read this set's rules → recursively read each included set's rules (**depth-first; cycles forbidden**) → concatenate into one flat list → optionally shadow an included rule by re-declaring its `R-<source>-NN` id. Two invariants:

- **Composition never renumbers.** `R-diagram` including `R-sugiyama` keeps `R-sugiyama-NN` ids — the source set is the rule's identity, so cross-project references stay stable.
- **The acyclic `include::` graph is the containment relation.** Resolving a target's applicable rules is walking `include::` (containment) then the clauses (binding).

**Umbrellas** are pure-composition sets (`include::` only, no own rules): `R-anchor`, `R-doc`, `R-diagram`. Adding a facet's rules to an audit is adding its set to an umbrella's `include::`.

## Where rules live, and adoption

Three homes (detail: [[FCT Ruleset]], [[F133 — Rulesets folder convention + facet embedding|F133]]):

| Home | When |
|---|---|
| **Catalog** — standalone `R-<slug>.md` in `Rulesets/` | cross-cutting, reusable, owner/trait-scoped sets |
| **Embedded** — `# RULESET` inside a facet / skill / discipline spec | rules that *are* the structural spec for an artifact kind |
| **Anchor-local** — `{NAME} Rules.md` | rules truly specific to one anchor |

**Adoption is `include::` under a `# {NAME} Decisions` H1** (vs *composition* under a `# RULESET` H1 — same syntax, different host). An anchor's `{NAME} Decisions.md` lists adopted sets on `include::`, maps each rule to its local implementation, and records D-records that cite rules via `**Cites:** [[R-…-NN]]`. Spec: [[FCT Decisions]].

## Naming

- **Ruleset:** `R-<kebab-slug>` (`R-diagram`, `R-anchor`). The H1 matches the file basename.
- **Rule:** `R-<slug>-NN` — `NN` zero-padded two digits, monotonic-forever within the slug, **never recycled** (a retired number stays retired). Cross-document references use the bare id (`see [[R-testing-04]]`).

## Relationship to FCT Ruleset

[[FCT Ruleset]] is the CAB **facet** — it integrates Warden rules into the anchor system (which anchors author/adopt rulesets, how `/audit` binds them) and currently still carries the prescriptive format text + the self-applying `R-ruleset` block. **`Warden Rule` is the canonical home of the rule *language*** going forward; the intended end-state is for `FCT Ruleset` to slim to the facet-integration role and reference this page for format. (Migration not yet done — flagged, not unilateral, since the facet is widely referenced.) The `where::` glob grammar still lives authoritatively in `FCT Ruleset § Where clause`; folding it into Warden is part of the same migration.

## See also

- [[Warden Events]] — the `when::` clause.
- [[FCT Ruleset]] — the CAB facet + the `where::` grammar (today's authoritative home).
- [[FCT Decisions]] — adoption + `Cites:`.
- [[Warden Integration Strategy]] — D8 (check:: as a Vale superset), the importer.
- [[Warden Architecture]] — how the format is resolved, compiled, and run.
- [[R-diagram]], [[CAE Rules]] — worked instances.
