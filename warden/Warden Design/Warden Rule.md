---
description: "the rule language — the file format for a rule and a ruleset (sentinels, clauses, body, composition)"
---
# Warden Rule

The **file format** of the Warden rule language: what a **rule** is and what a **ruleset** is, as written on disk. A rule is the atomic constraint; a ruleset is a named bundle of rules that travel together. This page defines the format — the sentinels, fields, and composition. How a rule *runs* — the condition, the actions, the interpretation environment — is [[Warden Semantics]]; worked runnable rules are [[Warden Examples]]; the `when::` moment vocabulary is [[Warden Events]] and `where::` is [[FCT Ruleset]] § Where clause.

Worked instances: [[R-diagram]] (a large umbrella), [[CAE Rules]] (an anchor-local set), and the self-applying `R-ruleset` block in [[FCT Ruleset]].

## The rule

![[Warden Rule Example.svg]]

*An example rule.* ✎ [regenerate the figures](warden-rule-figures.py)

A rule is a markdown **heading** whose first token is the all-caps `RULE` sentinel + a permanent identifier — so it is greppable anywhere (`grep -rnE '^#+\s+RULE\s+R-'`), not only inside a ruleset. The heading **names** the rule; the fields and body below it say what it does:

| Part | Form | Notes |
|---|---|---|
| `<H> RULE R-<slug>-NN` | the heading (any H-level; H3 customary) | `RULE` = the all-caps sentinel grep / lint depend on; `R-<slug>-NN` is the permanent id ([[#Naming]]) |
| `— <short name>` | optional, on the heading | a brief human title |
| `description::` | optional, encouraged | the rule's **meaning / goal** — a **queryable** Dataview field (hence one line) stating the rule's intent for anyone (human or LLM) *reading* it, per the North Star. **Not sent on rule fire**. Especially valuable when the body is Python. |
| `where::` · `when::` · `if::` | the **condition** | which files · which moment · the test (§ The condition) |
| **the body** | bare prose, or backticked Python | the **action** — bare prose *is* the `tell`; Python runs the verbs (`tell` / `edit` / `deny` / `sh` / `ask_oracle`). [[Warden Semantics]] § The actions. |
| `**Why:**` · `**Exceptions:**` | optional | rationale / acknowledged exceptions — **freeform prose** (a bold marker, not a queryable `::` field), so they can run long. Not sent on fire. |

Re-evaluation economy rides the condition: an expensive (LLM-judged) rule throttles re-judging with an ordinary `if::` over **`file.diff`** — `if:: file.diff.lines > 5` — gating the body on the size of the change ([[Warden Semantics]] § Re-evaluating an expensive test).

## The ruleset

![[Warden Ruleset Example.svg]]

*An example ruleset* (a set-level `where::` two rules share; the second overrides it). ✎ [regenerate](warden-rule-figures.py)

A ruleset is a `# RULESET R-<slug>` block plus a prescriptive header. The all-caps `RULESET` sentinel identifies the block unambiguously to lint / flatten / compile.

| Header line | Required? | Purpose |
|---|---|---|
| `# RULESET R-<slug>` | yes | sentinel H1 + the set's identifier |
| `include:: …` | yes (may be empty) | composition / adoption (§ Composition); the empty line is the slot |
| `where:: …` | optional | set-level default **place** every rule inherits ([[FCT Ruleset]] § Where clause) |
| `when:: …` | optional | set-level default **moment** every rule inherits ([[Warden Events]]) |
| `description:: …` | yes | one-line (8–15 word) tagline; no `::` in the value |
| prose body | optional | provenance, attribution, factoring history; any length |

`include::` / `where::` / `when::` / `description::` are Obsidian Dataview inline fields (`key:: value`). A single file may carry **multiple** rulesets — each `# RULESET` H1 opens a new scope whose header fields apply until the next H1. Standalone `R-<slug>.md` files are body-only (no YAML frontmatter); an embedded block lives inside a host doc that may have its own frontmatter.

## The condition — `when ∧ where ∧ if`

A rule fires only when the **conjunction** of its present clauses holds. Each is one Dataview key, so a rule round-trips cleanly to flat YAML (for the importer):

| Clause | Binds to | Spec |
|---|---|---|
| `where::` | the **file** it concerns — an anchor-relative glob | [[FCT Ruleset]] § Where clause |
| `when::` | the **moment** it fires at — omit → *passive* (audit-time) | [[Warden Events]] |
| `if::` | the **test** — a **Python expression** over `file` / `anchor` / `git` / `event` (or prose, for an LLM judgment) | [[Warden Semantics]] § The condition |

**Precedence:** a rule's own clause overrides its set's. With **no `where::` and no `when::`** the rule is **ambient** — always loaded into context, not dispatched ([[Warden Semantics]] § Ambient rules). The operational detail (indexes vs. computed test, live vs. passive) is in [[Warden Semantics]].

## The body

The body — what runs when the condition holds — is written one of two ways:

- **Bare prose** — a one-line message or a multi-line paragraph.
- **Backticked Python** — an inline `` `expr` `` for one line, a bare ` ``` ` fence for several. No `def`, no magic function name.

> **Backticks = Python.** A backticked `if::` value, a backticked one-line body, or a fenced block are Python the engine runs; un-backticked prose is sent verbatim. (Subsumes [[F007 — Backtick all where expressions — parser swap|F007]]: backticked = code, so Dataview leaves it alone.)

*What* a body does — the action it performs (`tell` / `edit` / `deny` / `sh` / `ask_oracle`) and the object surface it runs over — is **[[Warden Semantics]]** (§ The actions, § The interpretation environment); every body kind appears as a complete rule in **[[Warden Examples]]**.

## Composition — `include`

A ruleset absorbs others by naming them on `include::` (bare names or `[[wiki-links]]`, mixed). This is the language's single inheritance mechanism.

**Flatten semantics:** read this set's rules → recursively read each included set's rules (**depth-first; cycles forbidden**) → concatenate into one flat list → optionally shadow an included rule by re-declaring its `R-<source>-NN` id. Two invariants:

- **Composition never renumbers.** `R-diagram` including `R-sugiyama` keeps `R-sugiyama-NN` ids — the source set is the rule's identity, so cross-project references stay stable.
- **The acyclic `include::` graph is the containment relation.** Resolving a target's applicable rules is walking `include::` (containment) then the clauses (binding).

**Umbrellas** are pure-composition sets (`include::` only, no own rules): `R-anchor`, `R-doc`, `R-diagram`. Adding a facet's rules to an audit is adding its set to an umbrella's `include::`.

## Where rules live, and adoption

Three homes (detail: [[FCT Ruleset]], [[F133 — Rulesets folder convention + facet embedding|F133]]):

| Home | When |
|---|---|
| **Catalog** — standalone `R-<slug>.md` in `Rulesets/` | cross-cutting, reusable, owner / trait-scoped sets |
| **Embedded** — `# RULESET` inside a facet / skill / discipline spec | rules that *are* the structural spec for an artifact kind |
| **Anchor-local** — `{NAME} Rules.md` | rules truly specific to one anchor |

**Adoption is `include::` under a `# {NAME} Decisions` H1** (vs *composition* under a `# RULESET` H1 — same syntax, different host). An anchor's `{NAME} Decisions.md` lists adopted sets, maps each rule to its local implementation, and records D-records that cite rules via `**Cites:** [[R-…-NN]]`. And an anchor's **traits/facets are themselves adoptions** — a facet's embedded ruleset is active wherever that facet is present (activation semantics: [[Warden Semantics]] § Rulesets). Spec: [[FCT Decisions]].

## Naming

- **Ruleset:** `R-<kebab-slug>` (`R-diagram`, `R-anchor`). The H1 matches the file basename.
- **Rule:** `R-<slug>-NN` — `NN` zero-padded two digits, monotonic-forever within the slug, **never recycled** (a retired number stays retired). Cross-document references use the bare id (`see [[R-testing-04]]`).

## Relationship to FCT Ruleset

[[FCT Ruleset]] is the CAB **facet** — it integrates Warden rules into the anchor system (which anchors author/adopt rulesets, how `/audit` binds them) and currently still carries the prescriptive format text + the self-applying `R-ruleset` block. **`Warden Rule` is the canonical home of the rule *language*** going forward; the end-state is for `FCT Ruleset` to slim to the facet-integration role and reference this page for format. (Migration not yet done — flagged, not unilateral, since the facet is widely referenced.) The `where::` glob grammar still lives authoritatively in `FCT Ruleset § Where clause`; folding it into Warden is part of the same migration.

## See also

- [[Warden Semantics]] — how a rule *runs*: the condition, the actions, the interpretation environment, ruleset activation.
- [[Warden Examples]] — every kind of rule as a complete, runnable example.
- [[Warden Events]] — the `when::` moment catalog; [[FCT Ruleset]] — the `where::` grammar (today's authoritative home).
- [[FCT Decisions]] — adoption + `Cites:`.
- [[Warden Architecture]] / [[Warden Runtime]] — how the format is resolved, compiled, and run.
- [[R-diagram]], [[CAE Rules]] — worked instances.
