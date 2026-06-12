---
description: "**Deprecated post-F113**: the Principles facet has been unified into the Decisions facet at `{NAME} Design/{NAME} Decisions.md` with `(sampled)` tier (and `(reviewed)` / `(tracked)` / `(checked)` / `(stated)` as the other tier labels per F113 Q1). This spec is retained as the historical pre-F113 shape; see [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture]] for the new canonical model."
---

> **Deprecated post-F113 (2026-06-07).** Per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]], the Principles facet has been **unified** into the new Decisions facet at `{NAME} Design/{NAME} Decisions.md`. D-numbers replace P-numbers; each D-entry carries an explicit audit-tier label `(tracked)` / `(checked)` / `(sampled)` / `(stated)` per F113 Q1. **Working example:** `~/ob/kmr/SYS/Bespoke/Skill Agent/CAE/CAE Design/CAE Decisions.md` (CAE migrated 2026-06-06; principles D01-D03 sampled, rules D04+ checked). This spec page is kept as the historical pre-F113 shape; new anchors should follow the Decisions model directly.

# CAB Principles

Historical (pre-F113) facet spec for the per-anchor `{NAME} Principles.md` file — the catalog of load-bearing **value statements** (P-numbers) referenced by Rules, System Design, and Architecture.

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Principles.md`


The per-anchor Principles file (`{NAME} Principles.md`) is where the project's load-bearing **value statements** live. Principles are higher-level than Rules: they declare *why* the codebase makes the choices it does, in a few words each, and are referenced by ID from System Design, Architecture, and individual Rules.

A principle has both a **P-number** (`P01`, `P02`, …) for systematic identification and a **short name** (1–3 words, bolded) so it can be referenced naturally in conversation. The name leads the body in bold + em-dash form per the [[CAB Naming Conventions|named-list]] convention — `**One Queue, One Clock** — all scheduling decisions flow through…`. Either form (`P01` or `One Queue, One Clock`) is a valid reference.

Examples: "fail loud, no silent fallbacks," "single source of truth," "deterministic tests."

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Principles.md` — three principles (P01/P02/P03) referenced by R-rules in CAE Rules.


## Why Principles is its own facet (separate from Rules)

The two have different shapes and different roles in the system:

| Aspect | Principles | Rules |
|---|---|---|
| **What it is** | Value statements — the project's stated philosophy | Codified constraints — patterns the code must satisfy |
| **Who reads it** | Anyone making a design or code choice | `/rule check` (automated) + the engineer reviewing exceptions |
| **Identifier** | `P01`, `P02`, … | `R01`, `R02`, … |
| **Has exceptions?** | No — principles aren't checkable | Yes — `EX001`, `EX002`, … with grades |
| **References whom?** | Referenced *by* rules and design docs | References principles ("R01 encodes P02") |
| **Changes when?** | Rarely — principle changes signal a project pivot | Often — rules added/refined as the codebase grows |

Bundling principles inside Rules made the Rules file too long and obscured the layer-above relationship. Splitting clarifies that principles are the *source* and rules are the *enforcement*.


# Reference Example
---

```markdown
---
description: project design principles — the load-bearing value statements
---

# {NAME} Principles

| -[[{NAME} Principles]]- | |
| --- | --- |
| --- | |


The project's stated philosophy. Stated once here. Referenced by ID from System Design, Architecture, and the R-rules in [[{NAME} Rules]]. If the philosophy changes, edit here — nowhere else restates the principle.


## P01 — One Queue, One Clock

**One Queue, One Clock** — all scheduling decisions flow through a single priority queue and a single injected `Clock`. No module constructs its own queue, BTreeMap-over-deadline, or ad-hoc ordering of pending work.

**Why:** parallel scheduling paths diverge under load and make starvation invisible. A single queue and time source give one place to reason about priority, fairness, and test determinism.

**Encoded by:** [[{NAME} Rules#R01\|R01]], [[{NAME} Rules#R02\|R02]]


## P02 — Fail Loudly

**Fail Loudly** — errors propagate. Defaults are declared at the callsite or not at all. Retries are explicit and logged. Task failures reach the caller as errors, not swallowed with a substituted default.

**Why:** silent fallbacks mask broken production. Failure should surface in dev, not after deployment.

**Encoded by:** [[{NAME} Rules#R03\|R03]], [[{NAME} Rules#R04\|R04]]
```

---


# Format Specification

## Location

`{NAME} Principles.md` lives inside `{NAME} Docs/{NAME} Plan/` alongside `{NAME} Rules.md`, `{NAME} PRD.md`, and `{NAME} System Design.md`.

## Trait Applicability

Available to any anchor — code, topic, paper, skill. A skill anchor's principles guide its design (e.g., "every skill ships with a parallel user-doc"); a paper anchor's principles guide its claims; a code anchor's principles guide both architecture and code patterns.

For a fresh anchor with no declared philosophy yet, the file is a placeholder; principles get added when the team commits to a recurring trade-off resolution.

## Section Structure

Per F060 the file opens with YAML frontmatter + `# {NAME} Principles` H1 + dispatch-table placeholder (`\| -[[{NAME} Principles]]- \| \|` + standard separator). The body is one H2 per principle in source order:

```markdown
# {NAME} Principles

| -[[{NAME} Principles]]- | |
| --- | --- |
| --- | |


## P{NN} — {Short Name}

**{Short Name}** — {one-paragraph statement of the principle, leading with the name in bold + em-dash, named-list style}.

**Why:** {one or two sentences of rationale}

**Encoded by:** {comma-separated wiki-links to R-rules in {NAME} Rules.md, if any}
```

## Identifier — both P-number and short name

Each principle has two identifiers, both first-class:

- **P-number** (`P01`, `P02`, …) — for systematic / programmatic reference. Stable forever once assigned.
- **Short name** (1–3 words, Title Case) — for natural-language reference. Appears bolded as the lede of the principle's body, and as the second half of the H2 (`## P01 — One Queue, One Clock`).

Both forms are valid wiki-link targets. Prefer the **name** in design discussion ("we're committing to *Fail Loudly* here") and the **number** in mechanical contexts (`(encodes P01)` in a Rule heading, audit reports, etc.).

## P-number conventions

- Two-digit zero-padded: `P01`, `P02`, … through `P99`. (If a project ever exceeds 99 principles, that's a sign the file has lost focus — split or prune before extending.)
- P-numbers never change once assigned. Renaming a principle's *short name* is fine (the name is the human-readable label and may be tightened over time), but the P-number stays.
- A principle can be deprecated without deletion — mark its body with `**Deprecated YYYY-MM-DD:** {reason}` and leave the H2 in place. Other docs that referenced `P03` keep working.

## Encoded-By Field

When one or more rules in `{NAME} Rules.md` enforce a principle, list them under `**Encoded by:**` with wiki-links. Auditing checks consistency: each rule that names `(encodes P{NN})` in its heading should appear in the encoded-by list of `P{NN}`, and vice versa.

If no rule encodes a principle yet, the field reads `**Encoded by:** _None yet._` — that's a real signal: the principle is aspirational, not enforced.

## Cross-References from Other Docs

Other anchor docs reference principles by ID:

- **System Design** — calls out principles when explaining a design choice ("the dispatch model is shaped by [[{NAME} Principles#P01|P01]]").
- **Architecture** — same.
- **Rules** — each R-rule heading optionally includes `(encodes [[{NAME} Principles#P{NN}|P{NN}]])`.
- **Feature docs** — when a feature design defers a trade-off to "the project's principle on X," it links the principle.

The wiki-link target uses the H2 anchor `{NAME} Principles#P{NN}` so cross-referencing lands at the specific principle, not the top of the file.

## Lifecycle

- **Create** the file when the project commits to its first recurring trade-off (often during PRD authoring, or when the first R-rule needs justification).
- **Update** sparingly — adding a principle is a real commitment; removing one is a project pivot.
- **Audit** — `/audit rules` checks the encoded-by reciprocity (every R-rule's `encodes P<NN>` claim matches the principle's encoded-by list).

# BRIEF

- **This is a deprecated facet spec, retained for history.** Per F113 (2026-06-07), Principles unified into the Decisions facet at `{NAME} Design/{NAME} Decisions.md` with the `(sampled)` tier label. Do NOT remove the deprecation banner or YAML `description`; new anchors are pointed at [[CAB Decisions]] instead.
- **Edits here only clarify the pre-F113 shape**, never add new conventions. If a rule has evolved post-F113, edit [[CAB Decisions]] and (if needed) leave a "see Decisions for current model" pointer here — do not back-port new behavior into this spec.
- **Inclusion test for body content**: does the rule describe how the *historical* `{NAME} Principles.md` file was structured (P-number conventions, encoded-by reciprocity, lifecycle, cross-ref pattern)? If yes, it belongs. Anything about the unified Decisions model, the `(sampled)` tier, or D-numbers belongs in [[CAB Decisions]], not here.
- **Identifiers and link targets are load-bearing** — `P01`-style two-digit zero-padded P-numbers, the `{NAME} Principles#P{NN}` wiki-link anchor pattern, and the dual identifier (number + short name) are all referenced by other docs and audits; do not rename or restructure them.
- **The Reference Example block is normative** for the pre-F113 form — keep its frontmatter, dispatch-table placeholder, H2-per-principle shape, and **Encoded by:** field intact so downstream readers can still see what the old format looked like.
- **Do not pile general "principles vs rules" philosophy here** — that distinction is now owned by [[CAB Decisions]] (one facet, tiered by audit posture). This page only documents the old split.
