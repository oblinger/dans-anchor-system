---
description: per-anchor master file for applied decisions — declares which rulesets the anchor adopts (top-of-file include::), maps each adopted rule to its anchor-specific implementation, and records D-numbered project-specific decisions with rationale.
---

# FCT Decisions
**Audited examples:** [[HBR Decisions]], [[Mini Decisions]], [[CAE Decisions]], [[UCM Decisions]], [[DKT Decisions]]

The per-anchor master file for applied decisions — declares adopted rulesets (`include::`) and records D-numbered design choices with rationale.

| -[[FCT Decisions]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Decisions](hook://p/FCT%20Decisions)<br>: per-anchor master file for applied decisions — adopted rulesets and D-records |
| --- | --- |
| Related | [[FCT Ruleset]],  [[FCT Architecture]],  [[FCT Design Docs]],  [[Rulesets]],   |
| Examples | [[CAE Decisions\|minimal (D-records only, no include::)]],  [[HBR Decisions\|fuller (masthead + durable rulings)]],   |

**TLDR** — `{NAME} Decisions.md` is the single record of what an anchor has committed to: top-of-file `include::` lists adopted rulesets; the `## Adoption implementation map` bridges each rule to its anchor-specific code/script/table; `## D<N>` entries record applied choices with rationale and a `**Cites:**` back-link to the rules they satisfy. One per anchor.

The Decisions facet is the **per-anchor master file** for everything the anchor has applied — both *which rulesets it adopts* and *what specific design choices it made for this project*. Lives at `{NAME} Design/{NAME} Architecture/{NAME} Decisions.md` (alongside the architecture entry-point) for anchors with architecture folders, or `{NAME} Design/{NAME} Decisions.md` otherwise.

A **decision** is a specific applied choice with rationale, recorded at the anchor level. A **rule** is a portable constraint, defined in a ruleset ([[FCT Ruleset]]) and reused across many anchors. Decisions reference rules; rules are what get audited.

See [[FCT Ruleset]] for the companion facet (rulesets + per-anchor optional `{NAME} Rules.md`). See [[Rulesets]] for the catalog.

## Value statements (absorbed from the retired Principles facet)

A decision is not only a concrete applied choice ("we use `Sys` as the singleton clock"). It can also be a **value statement** — the load-bearing *why* behind the codebase's recurring choices ("Fail Loudly — errors propagate, no silent fallbacks"; "One Queue, One Clock — all scheduling flows through a single priority queue and injected clock"). These were formerly their own `{NAME} Principles.md` facet (P-records); per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]] they are now ordinary **D-records** — typically the most foundational and rarely-changing ones (a value-statement change signals a project pivot). Other docs reference them by ID exactly as they reference any decision: System Design and Architecture cite them when explaining a choice (`shaped by [[{NAME} Decisions#D01|D01]]`), and a rule may name the decision it encodes via its `**Cites:**` reciprocity. The separate Principles file is retired — value statements live here.

## Architecture (per 2026-06-08)

`{NAME} Decisions.md` is the **master adoption + decision record** for an anchor. It has three load-bearing sections in order:

1. **Top-of-file `include::`** — declares which rulesets the anchor adopts. Same Dataview inline-field syntax as inside rulesets, but here the semantics is *adoption* (the anchor commits to following these rules) rather than *composition* (one ruleset absorbing another).
2. **`## Adoption implementation map`** — a table that bridges each adopted rule to its anchor-specific implementation. Names the code module, audit script, exception table, etc. for each rule. This is where "we use Sys as our singleton" gets recorded once, instead of being scattered across decision bodies.
3. **`## D-records`** (`## D<N> — Title (status)`) — anchor-specific applied choices with rationale, alternatives, and consequences. Each may carry a `**Cites:**` line referencing specific rules from the adopted sets.

If the anchor has truly anchor-local rules (constraints that don't belong in any shared ruleset), they live in `{NAME} Rules.md` — but most anchors don't need this. [[MUX Rules]] is the worked example of a stub.

## Two forms in the wild

Real instances cluster into two shapes, both valid:

1. **Lean D-record list** (the common case) — a top-of-file `include::` (often empty), a one-line lead-in, then a sequence of D-records. No Adoption implementation map. The maximal worked example [[HBR Decisions]] is this form (three `### D0n` rulings, each a `**Choice.**` body); [[DKT Decisions]] is a fuller variant (`Decision / Why / Consequences` per record). Use this form by default — most anchors only need to record *what they decided and why*.
2. **Master adoption + decision record** (the heavyweight case) — adds the `## Adoption implementation map` table bridging adopted rules to anchor-specific implementation, and D-records carry `**Cites:**` back-links. Reach for this form only when the anchor actively adopts shared rulesets it wants `/audit decisions` to walk. [[CAE Decisions]] is the worked example.

Both forms share the same required spine: top-of-file `include::` (present, may be empty), a `description::` posture line (frontmatter or inline), and D-records as headings. The Adoption implementation map and `**Cites:**` lines are required *only* in the master form (when rulesets are adopted).

**D-record heading level.** Records may be `## D<N>` (when the file groups records under no enclosing H2) or `### D<N>` (when records sit under topical `## ` groupings, as in [[CAE Decisions]], or when the lead-in occupies the H2 level). The audit keys off the `D<N> — Title` token, not the heading depth. Use `D<N>` — the `DEC-<N>` form ([[DKT Decisions]]) is a tolerated legacy variant; new files use `D<N>`.

## File shape

```markdown
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Decisions](hook://p/FCT%20Decisions)

# {NAME} Decisions
include:: R-other-set, R-third-set
description:: per-anchor master file for applied decisions — adopted rulesets and D-records

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

- **Top-of-file `include::`** — list every adopted ruleset. May be empty (`include::` with nothing after). Always present.
- **`description::`** — one-line summary of the anchor's decision posture. In YAML frontmatter or as an inline `description::` line.
- **`## Adoption implementation map`** — table mapping each adopted rule (from the included sets, recursively) to anchor-specific implementation. Required **only in the master form** — i.e. when `include::` adopts at least one ruleset. Omit it in the lean form (empty `include::`).
- **`D<N> — Title (status)` records** — each decision as a heading (`## ` or `### `). D-numbers monotonic-forever, never recycled.

## D-record structure

Each D-record has:

- **H2 title** — `## D<N> — <short title> (<status>)`. Status is one of `checked` (ratified, in force), `open` (under design), `revised` (superseded — link to replacement), `retired` (no longer applies).
- **Optional metadata block** — `**Subsystem:** [[...]]`, `**Ratified:** date via [[F-link]]`, etc.
- **Body** — the decision in prose. Often includes `**Why.**`, `**Alternatives considered.**`, `**Consequences.**` sub-blocks.
- **Optional `**Cites:**` line** — wiki-links to specific rules in adopted sets that this decision applies. Audit walks these to verify the rule is satisfied for this decision.

The `**Cites:**` line is what closes the loop: rules are portable; decisions cite them; audit verifies the cited rules against the anchor's code.

## How `include::` semantics differ between rulesets and decision files

The `include::` syntax is shared:

| Context | Meaning |
| ------- | ------- |
| `# RULESET R-X` followed by `include:: R-Y, R-Z` | **Composition** — R-X absorbs R-Y and R-Z; the flatten script concatenates rules from all three. |
| `# {NAME} Decisions` followed by `include:: R-Y, R-Z` | **Adoption** — the anchor commits to following R-Y and R-Z. Audit walks the included sets and verifies each rule is satisfied via this anchor's implementation map and D-records. |

Same parser, different semantics depending on the H1 context (RULESET vs anchor-decision-file). The audit / flatten scripts know which mode they're in from the H1 sentinel.

## When `{NAME} Rules.md` is still useful

In most cases, `{NAME} Decisions.md` is the only file an anchor needs. `{NAME} Rules.md` exists when:

- The anchor has rules truly specific to itself that don't belong in any shared ruleset. (Rare — usually means the anchor is hosting a future-shared ruleset in-place until it stabilizes.)
- The anchor has a runtime-rewritten exception table that physically lives in the rules folder for tooling reasons (e.g., MUX's `MUX-R04 Exceptions.md` for the OS-bridge-logging audit).

When `{NAME} Rules.md` is just a stub pointer to `{NAME} Decisions.md`, that's fine — the file stays for the folder's sake (because something else in the folder, like the exception table, needs the structural home).

## Trait applicability

**Cardinality: one per anchor.** Each anchor has exactly one `{NAME} Decisions.md` — the single adoption + decision record for that anchor. Available to every anchor; most will have one even if it only carries the `include::` declarations and a few D-records.

## Audit

`/audit decisions` (formerly `/audit rules`; renamed when this facet became the master) flags:
- **broken-include** — top-of-file `include::` references a ruleset that doesn't exist.
- **missing-implementation** — an adopted rule has no row in the Adoption implementation map.
- **orphan-Cites** — a D-record's `**Cites:**` line references a rule that doesn't exist in any adopted set.
- **status-without-content** — D-record header has `(checked)` but body is empty or contradicts the status.

## See also

- [[FCT Ruleset]] — companion facet (rulesets + the optional anchor-local `{NAME} Rules.md`).
- [[Rulesets]] — the catalog.
- [[MUX Decisions]] — worked example. Adopts `R-ob-state-mgt` and `R-ob-observability` via top-of-file `include::`; has 31 D-records covering MuxUX's specific architectural choices.
- [[MUX Rules]] — worked example of a stub `{NAME} Rules.md`.

# RULESET R-decisions
include::
where:: file:{ANCHOR}/**/* Decisions.md
description:: spec for the `{NAME} Decisions.md` design facet — adopted rulesets + D-numbered decision records

Embedded ruleset for the Decisions facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Adopted via the `R-facet` umbrella; an anchor that wants its `{NAME} Decisions.md` audited pulls `R-facet` from its own `{NAME} Decisions.md`. Rules cover the spine common to both forms (lean D-record list + master adoption record); the Adoption-implementation-map and `**Cites:**` rules are stated/sampled so they apply only when the master form is in use.

### RULE R-decisions-01 — File name is `{NAME} Decisions.md` (checked)
check:: regex_present (?m)^#\s+\S

The facet doc is named `{NAME} Decisions.md` and lives under the anchor's Design surface (`{NAME} Design/` or `{NAME} Design/{NAME} Architecture/`). The `where::` glob `file:{ANCHOR}/**/* Decisions.md` is what selects real instances; this rule confirms the selected file is a well-formed markdown doc with an H1.

**Check pattern:** the `where::` selector matches `* Decisions.md`; the file opens with an H1 heading.

**Why:** the canonical name is what every cross-reference and the `/audit decisions` selector depend on. A mis-named file is invisible to the audit.

### RULE R-decisions-02 — H1 is `{NAME} Decisions` (checked)
check:: h1_present

The first heading is `# {NAME} Decisions` — the anchor slug plus the facet word, matching the file name.

**Check pattern:** an H1 line is present; its text is `{NAME} Decisions`.

**Why:** the H1 is the rendered title and the anchor of every `[[{NAME} Decisions]]` wiki-link. A missing or off-name H1 breaks navigation.

### RULE R-decisions-03 — Top-of-file `include::` present (checked)
check:: header_has_field include

The header carries an `include::` line declaring adopted rulesets. It may be empty (`include::` with nothing after) for the lean form, but the line itself is always present — it is the adoption sentinel that distinguishes a decision file's adoption semantics from a ruleset's composition semantics.

**Check pattern:** grep for a line matching `^include::` near the top of the file.

**Why:** the audit / flatten scripts key the dual `include::` semantics off this line's presence under a `# {NAME} Decisions` H1. Without it the file cannot declare (even an empty set of) adoptions and audit cannot walk adopted rulesets.

### RULE R-decisions-04 — At least one D-record present (checked)
check:: regex_present (?m)^#{2,3}\s+(D|DEC-)\d

The file records at least one decision as a `## D<N>` / `### D<N>` heading (the legacy `DEC-<N>` form is tolerated). A decision file with zero records is a stub, not a facet instance.

**Check pattern:** grep for a heading matching `^#{2,3}\s+(D|DEC-)\d`.

**Why:** the whole point of the file is to record decisions; an empty one carries no information and should either gain a record or be removed.

### RULE R-decisions-05 — D-record titles carry a status token (sampled)

Each D-record heading ends with a `(status)` token — one of `(checked)`, `(open)`, `(revised)`, `(retired)`. The status tells a reader whether the decision is in force, under design, superseded, or dead without reading the body.

**Check pattern:** for each `D<N> — Title` heading, assert it ends with `(checked|open|revised|retired)`. The minimal HBR worked example predates this token on its `### D0n` headings — those are grandfathered; new records carry it.

**Why:** status is the single most-queried fact about a decision. Omitting it forces every reader to infer in-force-ness from prose, and makes superseded rulings indistinguishable from live ones.

### RULE R-decisions-06 — D-numbers are monotonic and never recycled (sampled)

D-numbers increase and are never reused. A retired or revised decision keeps its number forever; the replacement gets a fresh number. Numbers may have gaps (a deleted record leaves a hole) but never duplicates.

**Check pattern:** parse all `D<N>` (and `DEC-<N>`) ids; assert no duplicate number within the file.

**Why:** other docs cite decisions by id (`shaped by [[{NAME} Decisions#D01|D01]]`). Recycling a number silently re-points every existing citation at a different decision — a correctness hazard with no error signal.

### RULE R-decisions-07 — Each D-record states its rationale (sampled)

Every D-record body explains *why*, not just *what* — via a `**Why.**` / `**Rationale.**` block or equivalent prose. A bare choice with no rationale is a fact, not a decision record.

**Check pattern:** for each D-record, assert the body contains a `**Why` / `**Rationale` marker or at least one full sentence of justification beyond the choice statement.

**Why:** the rationale is what stops a future reader (or agent) from re-litigating a settled choice. A decision file without rationale decays into a list of assertions nobody dares change because nobody knows why they hold.

### RULE R-decisions-08 — Master form: every adopted rule has an implementation-map row (stated)

When `include::` adopts at least one ruleset (the master form), a `## Adoption implementation map` table is present and maps every adopted rule (resolved recursively through the included sets) to this anchor's specific implementation. Lean-form files (empty `include::`) are N/A.

**Check pattern:** if `include::` is non-empty, locate `## Adoption implementation map`; for each adopted rule id, assert a table row names it. (`/audit decisions` broken-include + missing-implementation checks.)

**Why:** the implementation map is what closes the adoption loop — it records once, per anchor, *how* each portable rule is satisfied here. An adopted rule with no row is an unenforceable claim of compliance.

### RULE R-decisions-09 — `**Cites:**` lines reference existing rules (stated)

Any `**Cites:**` line on a D-record references rules that actually exist in an adopted ruleset (resolved through `include::`). No orphan citations.

**Check pattern:** for each `**Cites:**` wiki-link, assert the referenced `R-<set>-NN` rule exists in some adopted set. (`/audit decisions` orphan-Cites check.)

**Why:** `**Cites:**` is the load-bearing link the audit walks to verify a portable rule against this anchor's code. A citation to a non-existent rule makes that verification silently vacuous.

# BRIEF

- **This is the facet spec for `{NAME} Decisions.md`**, the per-anchor master adoption+decision file — defines the required structure (top-of-file `include::`, `## Adoption implementation map`, `## D<N>` records) and the dual `include::` semantics (composition inside RULESET vs adoption inside an anchor decision file).
- **NOT a list of decisions** — never paste anchor-specific D-records into this spec. Worked examples are referenced as wiki-links ([[MUX Decisions]]); concrete D-records live in their owning anchor.
- **Inclusion test:** content belongs here only if it is a structural rule for *every* anchor's `{NAME} Decisions.md` file (required sections, D-record shape, audit checks, `Cites:` mechanics). Per-anchor policy or ruleset content belongs in [[FCT Ruleset]], an anchor's own `{NAME} Decisions.md`, or a specific ruleset.
- **Load-bearing constraints to preserve:** the top-of-file `include::` is required (may be empty but must be present); D-numbers are monotonic-forever and never recycled; the four audit checks (broken-include, missing-implementation, orphan-Cites, status-without-content) are the contract `/audit decisions` enforces — don't silently drop or rename them without updating the audit script.
- **Naming/linking:** keep the `[[FCT Ruleset]]` ↔ `[[FCT Decisions]]` cross-references intact (this is the companion-facet pairing); `[[Rulesets]]` is the canonical catalog name; status tokens are exactly `checked` / `open` / `revised` / `retired` — don't invent new ones in examples.
- **When the dual-mode `include::` semantics change** (e.g. a third H1 context gains meaning), update both the table in § How `include::` semantics differ and the audit-script behavior in lockstep; the parser keys off the H1 sentinel, so the spec and the tooling must agree.
- **Don't pile cross-facet content here** — markdown rendering rules → [[R-markdown]]; project-wide rules → `CLAUDE.md`; ruleset authoring shape → [[FCT Ruleset]]. This file is strictly the decision-file facet.
