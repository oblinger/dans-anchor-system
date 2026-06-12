---
description: per-anchor master file for applied decisions — declares which rule sets the anchor adopts (top-of-file include::), maps each adopted rule to its anchor-specific implementation, and records D-numbered project-specific decisions with rationale.
---

# CAB Decisions

The Decisions facet is the **per-anchor master file** for everything the anchor has applied — both *which rule sets it adopts* and *what specific design choices it made for this project*. Lives at `{NAME} Design/{NAME} Architecture/{NAME} Decisions.md` (alongside the architecture entry-point) for anchors with architecture folders, or `{NAME} Design/{NAME} Decisions.md` otherwise.

A **decision** is a specific applied choice with rationale, recorded at the anchor level. A **rule** is a portable constraint, defined in a rule set ([[FCT Rules]]) and reused across many anchors. Decisions reference rules; rules are what get audited.

See [[FCT Rules]] for the companion facet (rule sets + per-anchor optional `{NAME} Rules.md`). See [[Rule Sets]] for the catalog.

## Architecture (per 2026-06-08)

`{NAME} Decisions.md` is the **master adoption + decision record** for an anchor. It has three load-bearing sections in order:

1. **Top-of-file `include::`** — declares which rule sets the anchor adopts. Same Dataview inline-field syntax as inside rule sets, but here the semantics is *adoption* (the anchor commits to following these rules) rather than *composition* (one rule set absorbing another).
2. **`## Adoption implementation map`** — a table that bridges each adopted rule to its anchor-specific implementation. Names the code module, audit script, exception table, etc. for each rule. This is where "we use Sys as our singleton" gets recorded once, instead of being scattered across decision bodies.
3. **`## D-records`** (`## D<N> — Title (status)`) — anchor-specific applied choices with rationale, alternatives, and consequences. Each may carry a `**Cites:**` line referencing specific rules from the adopted sets.

If the anchor has truly anchor-local rules (constraints that don't belong in any shared rule set), they live in `{NAME} Rules.md` — but most anchors don't need this. [[MUX Rules]] is the worked example of a stub.

## File shape

```markdown
:>> [[NAME]] → [NAME Decisions](hook://...)

# {NAME} Decisions
include:: R-other-set, R-third-set
description:: Master file for {NAME}'s applied decisions...

> [!info] Architecture
> One-paragraph commentary about how this file is organized.


## Adoption implementation map

| Rule | {NAME} implementation |
| ---- | ---------------------- |
| `R-other-set-01` | path/to/specific/code; audit script; exception table |
| `R-other-set-02` | ... |
| `R-third-set-01` | ... |


## D-records context note (optional)

Any brief notes about how D-records are numbered, what the status field means, etc.


## D01 — Decision title (checked)
**Subsystem:** [[NAME-Subsystem]]
**Ratified:** date / via [[F-link]]

Body of the decision — what was decided and why.

**Why.** Rationale.

**Alternatives considered.**
- *Alternative A*. Rejected because...
- *Alternative B*. Deferred because...

**Consequences.** Downstream effects.

**Cites:** [[R-other-set-01]] (relevant rule from an adopted set)

## D02 — ...
```

## Required structure

- **Top-of-file `include::`** — list every adopted rule set. May be empty (`include::` with nothing after). Always present.
- **Top-of-file `description::`** — one-line summary of the anchor's decision posture.
- **`## Adoption implementation map`** — table mapping each adopted rule (from the included sets, recursively) to anchor-specific implementation. Required when any rule set is adopted.
- **`## D<N> — Title (status)`** — each decision as an H2. D-numbers monotonic-forever, never recycled.

## D-record structure

Each D-record has:

- **H2 title** — `## D<N> — <short title> (<status>)`. Status is one of `checked` (ratified, in force), `open` (under design), `revised` (superseded — link to replacement), `retired` (no longer applies).
- **Optional metadata block** — `**Subsystem:** [[...]]`, `**Ratified:** date via [[F-link]]`, etc.
- **Body** — the decision in prose. Often includes `**Why.**`, `**Alternatives considered.**`, `**Consequences.**` sub-blocks.
- **Optional `**Cites:**` line** — wiki-links to specific rules in adopted sets that this decision applies. Audit walks these to verify the rule is satisfied for this decision.

The `**Cites:**` line is what closes the loop: rules are portable; decisions cite them; audit verifies the cited rules against the anchor's code.

## How `include::` semantics differ between rule sets and decision files

The `include::` syntax is shared:

| Context | Meaning |
| ------- | ------- |
| `# RULESET R-X` followed by `include:: R-Y, R-Z` | **Composition** — R-X absorbs R-Y and R-Z; the flatten script concatenates rules from all three. |
| `# {NAME} Decisions` followed by `include:: R-Y, R-Z` | **Adoption** — the anchor commits to following R-Y and R-Z. Audit walks the included sets and verifies each rule is satisfied via this anchor's implementation map and D-records. |

Same parser, different semantics depending on the H1 context (RULESET vs anchor-decision-file). The audit / flatten scripts know which mode they're in from the H1 sentinel.

## When `{NAME} Rules.md` is still useful

In most cases, `{NAME} Decisions.md` is the only file an anchor needs. `{NAME} Rules.md` exists when:

- The anchor has rules truly specific to itself that don't belong in any shared rule set. (Rare — usually means the anchor is hosting a future-shared rule set in-place until it stabilizes.)
- The anchor has a runtime-rewritten exception table that physically lives in the rules folder for tooling reasons (e.g., MUX's `MUX-R04 Exceptions.md` for the OS-bridge-logging audit).

When `{NAME} Rules.md` is just a stub pointer to `{NAME} Decisions.md`, that's fine — the file stays for the folder's sake (because something else in the folder, like the exception table, needs the structural home).

## Trait applicability

Available to every anchor. Most anchors will have a `{NAME} Decisions.md` even if it only carries the `include::` declarations and a few D-records.

## Audit

`/audit decisions` (formerly `/audit rules`; renamed when this facet became the master) flags:
- **broken-include** — top-of-file `include::` references a rule set that doesn't exist.
- **missing-implementation** — an adopted rule has no row in the Adoption implementation map.
- **orphan-Cites** — a D-record's `**Cites:**` line references a rule that doesn't exist in any adopted set.
- **status-without-content** — D-record header has `(checked)` but body is empty or contradicts the status.

## See also

- [[FCT Rules]] — companion facet (rule sets + the optional anchor-local `{NAME} Rules.md`).
- [[Rule Sets]] — the catalog.
- [[MUX Decisions]] — worked example. Adopts `R-ob-state-mgt` and `R-ob-observability` via top-of-file `include::`; has 31 D-records covering MuxUX's specific architectural choices.
- [[MUX Rules]] — worked example of a stub `{NAME} Rules.md`.

# BRIEF

- **This is the facet spec for `{NAME} Decisions.md`**, the per-anchor master adoption+decision file — defines the required structure (top-of-file `include::`, `## Adoption implementation map`, `## D<N>` records) and the dual `include::` semantics (composition inside RULESET vs adoption inside an anchor decision file).
- **NOT a list of decisions** — never paste anchor-specific D-records into this spec. Worked examples are referenced as wiki-links ([[MUX Decisions]]); concrete D-records live in their owning anchor.
- **Inclusion test:** content belongs here only if it is a structural rule for *every* anchor's `{NAME} Decisions.md` file (required sections, D-record shape, audit checks, `Cites:` mechanics). Per-anchor policy or rule-set content belongs in [[FCT Rules]], an anchor's own `{NAME} Decisions.md`, or a specific rule set.
- **Load-bearing constraints to preserve:** the top-of-file `include::` is required (may be empty but must be present); D-numbers are monotonic-forever and never recycled; the four audit checks (broken-include, missing-implementation, orphan-Cites, status-without-content) are the contract `/audit decisions` enforces — don't silently drop or rename them without updating the audit script.
- **Naming/linking:** keep the `[[FCT Rules]]` ↔ `[[FCT Decisions]]` cross-references intact (this is the companion-facet pairing); `[[Rule Sets]]` is the canonical catalog name; status tokens are exactly `checked` / `open` / `revised` / `retired` — don't invent new ones in examples.
- **When the dual-mode `include::` semantics change** (e.g. a third H1 context gains meaning), update both the table in § How `include::` semantics differ and the audit-script behavior in lockstep; the parser keys off the H1 sentinel, so the spec and the tooling must agree.
- **Don't pile cross-facet content here** — markdown rendering rules → [[R-markdown]]; project-wide rules → `CLAUDE.md`; rule-set authoring shape → [[FCT Rules]]. This file is strictly the decision-file facet.
