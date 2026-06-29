---
description: decisions are recorded where they belong — a `## Decisions` section (the recognizable label) in the design doc the decision is about, holding `### D<N>` records. A per-anchor `{NAME} Decisions.md` is OPTIONAL — the home for cross-cutting / value-statement decisions and ruleset adoption only. The "decision set" is a computed view over all `## Decisions` sections (a label, not an activation), never a mandatory single file.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Decisions](hook://p/FCT%20Decisions)

# FCT Decisions
**Audited examples:** [[HBR Decisions]], [[Mini Decisions]], [[CAE Decisions]], [[UCM Decisions]], [[DKT Decisions]]

| Table of Contents |  |
|---|---|
| **[[#Where decisions live — distributed by default]]** |  |
| **[[#Value statements (absorbed from the retired Principles facet)]]** |  |
| **[[#Architecture (per 2026-06-08)]]** |  |
| **[[#Two forms in the wild]]** |  |
| **[[#File shape]]** |  |
| **[[#Required structure]]** |  |
| **[[#D-record structure]]** |  |
| **[[#How `include::` semantics differ between rulesets and decision files]]** |  |
| **[[#When `{NAME} Rules.md` is still useful]]** |  |
| **[[#Trait applicability]]** |  |
| **[[#Audit]]** |  |
| **[[#See also]]** |  |
|    [[#RULE R-decisions-01 — Decisions live under a `## Decisions` section; the optional central file is `{NAME} Decisions.md` (checked)]] |  |
|    [[#RULE R-decisions-02 — H1 is `{NAME} Decisions` (checked)]] |  |
|    [[#RULE R-decisions-03 — Top-of-file `include::` present (checked)]] |  |
|    [[#RULE R-decisions-04 — At least one D-record present, always at H3 (checked)]] |  |
|    [[#RULE R-decisions-05 — D-record titles carry a status token (sampled)]] |  |
|    [[#RULE R-decisions-06 — D-numbers are monotonic and never recycled (sampled)]] |  |
|    [[#RULE R-decisions-07 — Each D-record states its rationale (sampled)]] |  |
|    [[#RULE R-decisions-08 — Master form: every adopted rule has an implementation-map row (stated)]] |  |
|    [[#RULE R-decisions-09 — `**Cites:**` lines reference existing rules (stated)]] |  |

The per-anchor master file for applied decisions — declares adopted rulesets (`include::`) and records D-numbered design choices with rationale.

**Related:** [[FCT Ruleset]],  [[FCT Architecture]],  [[FCT Design Docs]],  [[Rulesets]]
**Examples:** [[Mini Architecture#Decisions\|distributed — decision in the doc it shapes (new model)]],  [[Mini Decisions\|optional central — cross-cutting value only]],  [[CAE Decisions\|legacy central master (D-records + include::)]],  [[HBR Decisions\|legacy central (durable rulings)]]

**TLDR** — A decision is recorded under a **`## Decisions` section** (the recognizable label) in the design doc it shapes, as `### D<N> — Title (status)` records with rationale. The decision *set* is the computed sweep of those sections — not a file. A central `{NAME} Decisions.md` is **OPTIONAL**: the home for cross-cutting / value decisions and (master form) ruleset adoption via top-of-file `include::` + an `## Adoption implementation map`.

The Decisions facet defines the **`### D<N>` record shape and its `## Decisions` label**, used wherever decisions live — distributed in the design docs they shape (the default) and, for cross-cutting decisions + ruleset adoption, in the optional central `{NAME} Decisions.md` (at `{NAME} Design/{NAME} Architecture/` or `{NAME} Design/`). It records both *which rulesets the anchor adopts* (central master form) and *what specific choices it made* (everywhere).

A **decision** is a specific applied choice with rationale, recorded at the anchor level. A **rule** is a portable constraint, defined in a ruleset ([[FCT Ruleset]]) and reused across many anchors. Decisions reference rules; rules are what get audited.

See [[FCT Ruleset]] for the companion facet (rulesets + per-anchor optional `{NAME} Rules.md`). See [[Rulesets]] for the catalog.

## Where decisions live — distributed by default

A decision is *about* something — an architecture choice, an API shape, a tradeoff. **It is recorded where that something is designed**, not exiled to a central file. The unit is a **`## Decisions` section** — the recognizable label ("this section is decisions") — placed in whatever design doc the decision belongs to, holding one or more `### D<N>` records:

- An **architecture** decision → a `## Decisions` section in `{NAME} Architecture.md`.
- A **PRD / product** decision → a `## Decisions` section in the PRD.
- A decision local to one **feature** → that feature doc's `## Decisions` (the same record shape as its bottom `## Resolved`).
- A **cross-cutting / value-statement** decision (Fail-loudly; one-clock) that belongs to no single doc → the **optional** `{NAME} Decisions.md`.

This mirrors rulesets, with the load-bearing difference: **rulesets are *activated* (the engine runs them; `where::` binds them); decisions are *records* — not activated, just labeled.** A "decision set" therefore needs no activation machinery — it needs a recognizable marker so it can be *found and gathered*. The `## Decisions` H2 (with its `### D<N>` headers) is that marker. You can put **just one** record under it, or many.

**The "decision set" is a computed view, not a file.** Because every decision carries the `## Decisions` / `### D<N>` label, a sweep gathers them all into one view on demand — exactly how `Q.md` aggregates questions that physically live in feature docs. Source of truth is distributed (next to what it decides); the aggregate is derived (`/audit decisions` and any "walk all decisions" tool sweep the label, not a single file).

**`{NAME} Decisions.md` is now OPTIONAL.** It is the home for cross-cutting / value-statement decisions and — in the master form — ruleset adoption + the implementation map. It is **not** the forced container for every decision. When every decision has a natural home in a design doc, the anchor has **no** central Decisions file at all (file existence is a trait — omit it). The sections below describe that optional central form; the `### D<N>` record shape they define is identical wherever a `## Decisions` section lives.

## Value statements (absorbed from the retired Principles facet)

A decision is not only a concrete applied choice ("we use `Sys` as the singleton clock"). It can also be a **value statement** — the load-bearing *why* behind the codebase's recurring choices ("Fail Loudly — errors propagate, no silent fallbacks"; "One Queue, One Clock — all scheduling flows through a single priority queue and injected clock"). These were formerly their own `{NAME} Principles.md` facet (P-records); per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]] they are now ordinary **D-records** — typically the most foundational and rarely-changing ones (a value-statement change signals a project pivot). Other docs reference them by ID exactly as they reference any decision: System Design and Architecture cite them when explaining a choice (`shaped by ~~[[{NAME} Decisions#D01|D01]]~~`), and a rule may name the decision it encodes via its `**Cites:**` reciprocity. The separate Principles file is retired — value statements live here.

## Architecture (per 2026-06-08)

`{NAME} Decisions.md` is the **master adoption + decision record** for an anchor. It has three load-bearing sections in order:

1. **Top-of-file `include::`** — declares which rulesets the anchor adopts. Same Dataview inline-field syntax as inside rulesets, but here the semantics is *adoption* (the anchor commits to following these rules) rather than *composition* (one ruleset absorbing another).
2. **`## Adoption implementation map`** — a table that bridges each adopted rule to its anchor-specific implementation. Names the code module, audit script, exception table, etc. for each rule. This is where "we use Sys as our singleton" gets recorded once, instead of being scattered across decision bodies.
3. **`### D-records`** (`### D<N> — Title (status)`) — anchor-specific applied choices with rationale, alternatives, and consequences. Each may carry a `**Cites:**` line referencing specific rules from the adopted sets.

If the anchor has truly anchor-local rules (constraints that don't belong in any shared ruleset), they live in `{NAME} Rules.md` — but most anchors don't need this. [[MUX Rules]] is the worked example of a stub.

## Two forms in the wild

Real instances cluster into two shapes, both valid:

1. **Lean D-record list** (the common case) — a top-of-file `include::` (often empty), a one-line lead-in, then a sequence of D-records. No Adoption implementation map. The maximal worked example [[HBR Decisions]] is this form (three `### D0n` rulings, each a `**Choice.**` body); [[DKT Decisions]] is a fuller variant (`Decision / Why / Consequences` per record). Use this form by default — most anchors only need to record *what they decided and why*.
2. **Master adoption + decision record** (the heavyweight case) — adds the `## Adoption implementation map` table bridging adopted rules to anchor-specific implementation, and D-records carry `**Cites:**` back-links. Reach for this form only when the anchor actively adopts shared rulesets it wants `/audit decisions` to walk. [[CAE Decisions]] is the worked example.

Both forms share the same required spine: top-of-file `include::` (present, may be empty), a `description::` posture line (frontmatter or inline), and D-records as headings. The Adoption implementation map and `**Cites:**` lines are required *only* in the master form (when rulesets are adopted).

**D-record heading level — always `### D<N>` (H3).** Decision records are always H3, in every file, whether or not the file groups them. `## ` (H2) is reserved for *optional topical grouping* (e.g. `## Values`, `## Parser`) — each group then holds its `### D<N>` records — and for the structural sections (`## Adoption implementation map`, `## See also`). A flat file simply carries its `### D<N>` records directly under the lead-in (`# {NAME} Decisions` → `### D<N>`, intentionally skipping H2, which stays reserved for grouping). This keeps every decision at one uniform depth across all files while leaving the H2 level free for structure. The audit enforces H3 (R-decisions-04). Use the `D<N>` token; the `DEC-<N>` form ([[DKT Decisions]]) is a tolerated legacy token variant.

## File shape

The form is identical wherever a `## Decisions` section lives — see the **real worked instances** rather than a fenced fake copy:

- **Distributed form (primary):** [[Mini Architecture#Decisions]] — a `## Decisions` H2 inside the doc it shapes, holding `### D<N> — Title (status)` records, each cross-linking the value it serves.
- **Optional central form:** [[Mini Decisions]] — `# {NAME} Decisions` + `include::` + cross-cutting `### D<N>` records only. The fuller master variant [[CAE Decisions]] adds a `## Adoption implementation map` table and `**Cites:**` back-links when the anchor adopts shared rulesets.

Each `### D<N>` record carries: the H3 heading `### D<N> — <title> (<status>)`; optional `**Subsystem:** [[…]]` / `**Ratified:** date via [[F-link]]` metadata; a body with `**Why.**` (required), optional `**Alternatives considered.**` and `**Consequences.**`; and — master form only — an optional `**Cites:** [[R-set-NN]]` line bridging to an adopted rule.

## Required structure

- **Top-of-file `include::`** — list every adopted ruleset. May be empty (`include::` with nothing after). Always present.
- **`description::`** — one-line summary of the anchor's decision posture. In YAML frontmatter or as an inline `description::` line.
- **`## Adoption implementation map`** — table mapping each adopted rule (from the included sets, recursively) to anchor-specific implementation. Required **only in the master form** — i.e. when `include::` adopts at least one ruleset. Omit it in the lean form (empty `include::`).
- **`D<N> — Title (status)` records** — each decision as an `### ` (H3) heading. D-numbers monotonic-forever, never recycled.

## D-record structure

Each D-record has:

- **H3 heading** — `### D<N> — <short title> (<status>)`. Status is one of `checked` (ratified, in force), `open` (under design), `revised` (superseded — link to replacement), `retired` (no longer applies).
- **Optional metadata block** — `**Subsystem:** ~~[[...]]~~`, `**Ratified:** date via ~~[[F-link]]~~`, etc.
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

**Cardinality: distributed.** A `## Decisions` section may appear in **any** design doc under the anchor's Design surface (Architecture, PRD, System Design, Interface, a feature doc's design) — wherever a decision belongs. The central `{NAME} Decisions.md` is **optional and at most one** per anchor: present only when the anchor has cross-cutting / value-statement decisions, or adopts shared rulesets (the master form). An anchor whose every decision has a natural home in a design doc has **no** central Decisions file. Available to every anchor; required of none.

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
where:: file:{ANCHOR}/** Design/**/*.md contains:(?m)^##\s+Decisions\s*$ ; file:{ANCHOR}/**/* Decisions.md
description:: spec for decisions — a `## Decisions` section (with `### D<N>` records) in any design doc, plus the optional central `{NAME} Decisions.md`

Embedded ruleset for the Decisions facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Adopted via the `R-facet` umbrella; an anchor that wants its `{NAME} Decisions.md` audited pulls `R-facet` from its own `{NAME} Decisions.md`. Rules cover the spine common to both forms (lean D-record list + master adoption record); the Adoption-implementation-map and `**Cites:**` rules are stated/sampled so they apply only when the master form is in use.

### RULE R-decisions-01 — Decisions live under a `## Decisions` section; the optional central file is `{NAME} Decisions.md` (checked)
check:: regex_present (?m)^##\s+Decisions\s*$

The canonical unit is a `## Decisions` H2 section holding `### D<N>` records, placed in the design doc the decision is *about*. The optional per-anchor central file is named `{NAME} Decisions.md` (the home for cross-cutting / value-statement decisions + ruleset adoption) — when present it opens with `# {NAME} Decisions` and its records sit directly under it (the file's H1 stands in for the `## Decisions` marker). The `where::` selector matches both: any Design-surface doc carrying a `## Decisions` section, and the central `* Decisions.md` file.

**Check pattern:** the selected doc contains a `## Decisions` H2 (or, for the central file, a `# {NAME} Decisions` H1) introducing `### D<N>` records.

**Why:** the `## Decisions` label is what makes decisions findable and aggregatable wherever they live. A decision recorded with no recognizable label is invisible to `/audit decisions` and to the computed decision-set view.

### RULE R-decisions-02 — H1 is `{NAME} Decisions` (checked)
check:: h1_present

The first heading is `# {NAME} Decisions` — the anchor slug plus the facet word, matching the file name.

**Check pattern:** an H1 line is present; its text is `{NAME} Decisions`.

**Why:** the H1 is the rendered title and the anchor of every `~~[[{NAME} Decisions]]~~` wiki-link. A missing or off-name H1 breaks navigation.

### RULE R-decisions-03 — Top-of-file `include::` present (checked)
check:: header_has_field include

The header carries an `include::` line declaring adopted rulesets. It may be empty (`include::` with nothing after) for the lean form, but the line itself is always present — it is the adoption sentinel that distinguishes a decision file's adoption semantics from a ruleset's composition semantics.

**Check pattern:** grep for a line matching `^include::` near the top of the file.

**Why:** the audit / flatten scripts key the dual `include::` semantics off this line's presence under a `# {NAME} Decisions` H1. Without it the file cannot declare (even an empty set of) adoptions and audit cannot walk adopted rulesets.

### RULE R-decisions-04 — At least one D-record present, always at H3 (checked)
check:: regex_present (?m)^###\s+(D|DEC-)\d

The file records at least one decision as a `### D<N>` heading (**H3 — the standard, uniform depth for every decision**; the `DEC-<N>` token is tolerated as legacy). An `## D<N>` (H2) record is non-standard and fails this check — demote it to `### `. `## ` is reserved for optional topical grouping and structural sections, never for the decision records themselves. A decision file with zero records is a stub, not a facet instance.

**Check pattern:** grep for a heading matching `^###\s+(D|DEC-)\d`.

**Why:** decisions live at one uniform depth (H3) across every file so the eye, the audit, and any "walk all D-records" tooling never have to reconcile mixed depths; H2 stays free for grouping. The whole point of the file is to record decisions; an empty one carries no information and should either gain a record or be removed.

### RULE R-decisions-05 — D-record titles carry a status token (sampled)

Each D-record heading ends with a `(status)` token — one of `(checked)`, `(open)`, `(revised)`, `(retired)`. The status tells a reader whether the decision is in force, under design, superseded, or dead without reading the body.

**Check pattern:** for each `D<N> — Title` heading, assert it ends with `(checked|open|revised|retired)`. The minimal HBR worked example predates this token on its `### D0n` headings — those are grandfathered; new records carry it.

**Why:** status is the single most-queried fact about a decision. Omitting it forces every reader to infer in-force-ness from prose, and makes superseded rulings indistinguishable from live ones.

### RULE R-decisions-06 — D-numbers are monotonic and never recycled (sampled)

D-numbers increase and are never reused. A retired or revised decision keeps its number forever; the replacement gets a fresh number. Numbers may have gaps (a deleted record leaves a hole) but never duplicates.

**Check pattern:** parse all `D<N>` (and `DEC-<N>`) ids; assert no duplicate number within the file.

**Why:** other docs cite decisions by id (`shaped by ~~[[{NAME} Decisions#D01|D01]]~~`). Recycling a number silently re-points every existing citation at a different decision — a correctness hazard with no error signal.

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
