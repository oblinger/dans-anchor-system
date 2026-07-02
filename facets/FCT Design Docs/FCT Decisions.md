---
description: decisions are documentation — recorded under a `## Decisions` section in the design doc they shape; Warden never computes against them. Anything directly checkable is a rule, living in the companion `# RULESET` directly after the Decisions section; rules link back with an implements-D<N> note.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Decisions](hook://p/FCT%20Decisions)

# FCT Decisions
**Audited examples:** [[HBR Decisions]], [[Mini Decisions]], [[CAE Decisions]], [[UCM Decisions]], [[DKT Decisions]]

| Table of Contents |  |
|---|---|
| **[[#Decisions vs rules — the doctrine (2026-07-01)]]** |  |
| **[[#Form — the Decisions section]]** |  |
| **[[#Where decisions live — distributed by default]]** |  |
| **[[#Value statements (absorbed from the retired Principles facet)]]** |  |
| **[[#Companion ruleset — rules ride in the same file]]** |  |
| **[[#Implementation linkage — on the rule's side]]** |  |
| **[[#D-record structure]]** |  |
| **[[#The optional central file]]** |  |
| **[[#When `{NAME} Rules.md` is still useful]]** |  |
| **[[#Trait applicability]]** |  |
| **[[#Audit]]** |  |
| **[[#History]]** |  |
| **[[#See also]]** |  |
|   [[#RULE R-decisions-01 — Decisions live under a `## Decisions` section; the optional central file is `{NAME} Decisions.md` (checked)]] |  |
|   [[#RULE R-decisions-02 — H1 is `{NAME} Decisions` (checked)]] |  |
|   [[#RULE R-decisions-03 — retired 2026-07-01 (tracked)]] |  |
|   [[#RULE R-decisions-04 — At least one D-record present, always at H3 (checked)]] |  |
|   [[#RULE R-decisions-05 — D-record titles carry a status token (sampled)]] |  |
|   [[#RULE R-decisions-06 — D-numbers are monotonic and never recycled (sampled)]] |  |
|   [[#RULE R-decisions-07 — Each D-record states its rationale (sampled)]] |  |
|   [[#RULE R-decisions-08 — retired 2026-07-01 (tracked)]] |  |
|   [[#RULE R-decisions-09 — retired 2026-07-01 (tracked)]] |  |
|   [[#RULE R-decisions-10 — Companion ruleset sits directly after the Decisions section (sampled)]] |  |
|   [[#RULE R-decisions-11 — No decision duplicates a rule (stated)]] |  |

The facet for recorded decisions — the documentation layer that sits above Warden's rules.

**Related:** [[FCT Ruleset]],  [[FCT Architecture]],  [[FCT Design Docs]],  [[Rulesets]]
**Examples:** [[Mini Architecture#Decisions\|distributed — decision in the doc it shapes]],  [[Mini Decisions\|optional central — cross-cutting value only]],  [[CAE Decisions\|legacy central master (pre-doctrine include:: + implementation map)]],  [[HBR Decisions\|legacy central (durable rulings)]]

**TLDR** — A Decisions surface is simply an **H2 header `## Decisions`** followed by the list of decisions made — `### D<N> — Title (status)` records with rationale — placed in the design doc the decisions shape. Decisions constrain and guide the way rules do, **but Warden pays no attention to them**: they are documentation, never computed against. Anything directly verifiable is written **only as a rule**, in the companion `# RULESET` that by convention sits **directly after the Decisions section** under the same (or a clearly related) name; a rule ties itself back to the decision it implements with a loose `implements D<N>` note.

A **decision** is a broader, higher-level choice with rationale, recorded where it belongs. A **rule** is a lower-level, directly verifiable constraint, defined in a ruleset ([[FCT Ruleset]]) and computed by Warden. Decisions are for readers; rules are for the engine.

See [[FCT Ruleset]] for the companion facet (rulesets + Warden computation). See [[Rulesets]] for the catalog.

## Decisions vs rules — the doctrine (2026-07-01)

User-ratified 2026-07-01 (F221). Four load-bearing points:

- **Decisions guide; Warden ignores them.** A decision constrains and guides exactly as a rule does — but the rule engine pays **no** attention to decisions. They are documentation: visible to the user and to any agent reading the doc, never parsed, bound, or verified by Warden. Rules ([[Warden Rule]]) are the computed layer.
- **Granularity picks the representation.** Decisions are the broader, higher-level choices; rules are the lower-level, directly verifiable / computable things. The test: if it can be mechanically checked (a `where::`/`if::` over files), write it as a **rule**; if it is a stance, a tradeoff, an architecture choice, record it as a **decision**.
- **Don't repeat yourself.** If something can be expressed as a rule, it is NOT also written as a decision — it lives only in the companion ruleset (which sits directly after the Decisions section, so it is still "in the decisions file"). No decision duplicates a rule.
- **Linkage lives on the rule's side.** One decision is often implemented by several rules; each such rule ties itself back with an `implements D<N>` note. Loose coupling — a readable note, not a formal join the engine resolves.

## Form — the Decisions section

A Decisions surface is simply an **H2 header `## Decisions`** followed by the list of the decisions made. Each decision on the list is a `### D<N> — <title> (<status>)` record (shape in § D-record structure). That is the whole form — no header fields, no computed lines; Warden reads nothing here. In the central `{NAME} Decisions.md` the `# {NAME} Decisions` H1 stands in for the `## Decisions` marker and the records sit directly under it.

## Where decisions live — distributed by default

A decision is *about* something — an architecture choice, an API shape, a tradeoff. **It is recorded where that something is designed**, not exiled to a central file. The unit is the **`## Decisions` section** — the recognizable label ("this section is decisions") — placed in whatever design doc the decision belongs to, holding one or more `### D<N>` records:

- An **architecture** decision → a `## Decisions` section in `{NAME} Architecture.md`.
- A **PRD / product** decision → a `## Decisions` section in the PRD.
- A decision local to one **feature** → that feature doc's `## Decisions` (the same record shape as its bottom `## Resolved`).
- A **cross-cutting / value-statement** decision (Fail-loudly; one-clock) that belongs to no single doc → the **optional** `{NAME} Decisions.md`.

This mirrors rulesets, with the load-bearing difference: **rulesets are *computed* (Warden runs them; `where::` binds them); decisions are *records* — never computed, just labeled.** A "decision set" therefore needs no activation machinery — it needs a recognizable marker so it can be *found and gathered*. The `## Decisions` H2 (with its `### D<N>` headers) is that marker. You can put **just one** record under it, or many.

**The "decision set" is a computed view, not a file.** Because every decision carries the `## Decisions` / `### D<N>` label, a sweep gathers them all into one view on demand — exactly how `Q.md` aggregates questions that physically live in feature docs. Source of truth is distributed (next to what it decides); the aggregate is derived (`/audit decisions` and any "walk all decisions" tool sweep the label, not a single file). Aggregation is the only tooling that touches decisions — Warden never verifies anything against their content.

**`{NAME} Decisions.md` is OPTIONAL.** It is the home for cross-cutting / value-statement decisions (and, per the companion convention below, often hosts the anchor's own ruleset). It is **not** the forced container for every decision. When every decision has a natural home in a design doc, the anchor has **no** central Decisions file at all (file existence is a trait — omit it). The `### D<N>` record shape is identical wherever a `## Decisions` section lives.

## Value statements (absorbed from the retired Principles facet)

A decision is not only a concrete applied choice ("we use `Sys` as the singleton clock"). It can also be a **value statement** — the load-bearing *why* behind the codebase's recurring choices ("Fail Loudly — errors propagate, no silent fallbacks"; "One Queue, One Clock — all scheduling flows through a single priority queue and injected clock"). These were formerly their own `{NAME} Principles.md` facet (P-records); per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]] they are now ordinary **D-records** — typically the most foundational and rarely-changing ones (a value-statement change signals a project pivot). Other docs reference them by ID exactly as they reference any decision: System Design and Architecture cite them when explaining a choice (`shaped by ~~[[{NAME} Decisions#D01|D01]]~~`), and a rule names the decision it encodes on its own side (`implements D<N>` — § Implementation linkage). The separate Principles file is retired — value statements live here.

## Companion ruleset — rules ride in the same file

When rules accompany decisions, the corresponding **`# RULESET` goes in the same file, directly after the Decisions section**, and by convention carries **the same (or a clearly related) name** as the Decisions section — a `{NAME} Decisions.md` hosts `# RULESET R-<name>`; a topical `## Parser decisions` section pairs with `# RULESET R-<name>-parser`. Two consequences:

- **One file, two layers.** The reader sees the *why* (the decisions) immediately above the *what is enforced* (the rules). Warden sees only the `# RULESET` block — the sentinel is what it parses; everything above it is invisible to the engine.
- **DRY has a home.** A directly checkable constraint goes in the companion ruleset and only there; the decisions list above it stays at the higher altitude. This is also where truly anchor-local rules live — the companion set covers most of what a separate `{NAME} Rules.md` used to.

Mechanically this is the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention put to per-anchor work — the same way a facet spec carries its own `# RULESET` block. This very file is the worked shape: the facet's prose above, `# RULESET R-decisions` below.

## Implementation linkage — on the rule's side

One decision may be implemented by several rules. That linkage is indicated **on the rules' side**: a rule that exists to enforce a decision carries a short note tying it back — `implements D07` in its body or `**Why:**` line, with a wiki-link when the decision lives in another file (`implements ~~[[{NAME} Decisions#D07|D07]]~~`). This is **loose coupling, not a formal join**: Warden neither resolves nor verifies the note; it exists so a reader arriving at a rule can walk back to the choice that motivated it. The decision record itself stays plain prose — the linkage is recorded on the rule and read from the rule.

## D-record structure

Each D-record has:

- **H3 heading** — `### D<N> — <short title> (<status>)`. Status is one of `checked` (ratified, in force), `open` (under design), `revised` (superseded — link to replacement), `retired` (no longer applies).
- **Optional metadata block** — `**Subsystem:** ~~[[...]]~~`, `**Ratified:** date via ~~[[F-link]]~~`, etc.
- **Body** — the decision in prose. Often includes `**Why.**`, `**Alternatives considered.**`, `**Consequences.**` sub-blocks.

**D-record heading level — always `### D<N>` (H3).** Decision records are always H3, in every file, whether or not the file groups them. `## ` (H2) is reserved for *optional topical grouping* (e.g. `## Values`, `## Parser`) — each group then holds its `### D<N>` records — and for structural sections (`## See also`). A flat central file simply carries its `### D<N>` records directly under the lead-in (`# {NAME} Decisions` → `### D<N>`, intentionally skipping H2, which stays reserved for grouping). This keeps every decision at one uniform depth across all files while leaving the H2 level free for structure. The audit enforces H3 (R-decisions-04). Use the `D<N>` token; the `DEC-<N>` form ([[DKT Decisions]]) is a tolerated legacy token variant.

**D-numbers are monotonic-forever, never recycled.** A retired or revised decision keeps its number; the replacement gets a fresh one (R-decisions-06).

## The optional central file

`{NAME} Decisions.md` (at `{NAME} Design/{NAME} Architecture/` or `{NAME} Design/`) holds the decisions that belong to no single design doc — cross-cutting rulings and value statements — plus, by the companion convention, the anchor's own `# RULESET` when it has one. Its spine:

- **`# {NAME} Decisions`** H1 (stands in for the `## Decisions` marker).
- **`description::`** — one-line summary of the anchor's decision posture, in YAML frontmatter or as an inline line.
- **`### D<N>` records** directly under the lead-in.
- **Optional companion `# RULESET R-<name>`** directly after the records.

Worked instances: [[Mini Decisions]] (lean central — cross-cutting records only); [[HBR Decisions]] (durable rulings); [[Mini Architecture#Decisions]] (the distributed form). [[CAE Decisions]] is the **legacy master form** — its top-of-file adoption `include::`, `## Adoption implementation map`, and `**Cites:**` lines predate the 2026-07-01 doctrine (§ History) and are not authored in new files.

## When `{NAME} Rules.md` is still useful

With the companion convention, anchor-local rules default to the `# RULESET` directly after the anchor's Decisions section. `{NAME} Rules.md` remains for the structural cases:

- A **runtime-rewritten artifact** needs a physical home in the rules folder for tooling reasons (e.g., MUX's `MUX-R04 Exceptions.md` exception table for the OS-bridge-logging audit).
- The anchor is **hosting a future-shared ruleset in place** until it stabilizes and moves to the catalog.

When `{NAME} Rules.md` is just a stub pointer to the decisions file, that's fine — the file stays for the folder's sake (because something else in the folder, like the exception table, needs the structural home).

## Trait applicability

**Cardinality: distributed.** A `## Decisions` section may appear in **any** design doc under the anchor's Design surface (Architecture, PRD, System Design, Interface, a feature doc's design) — wherever a decision belongs. The central `{NAME} Decisions.md` is **optional and at most one** per anchor: present only when the anchor has cross-cutting / value-statement decisions (it then also hosts the companion ruleset, if the anchor has one). An anchor whose every decision has a natural home in a design doc has **no** central Decisions file. Available to every anchor; required of none.

## Audit

`/audit decisions` checks the **documentation shape only** — it never verifies code or rules against a decision's content (constraint verification is Warden's job, over rulesets). Flags:

- **missing-label** — D-records with no recognizable `## Decisions` marker (or central-file H1) above them.
- **status-without-content** — D-record header has `(checked)` but body is empty or contradicts the status.
- **companion-drift** — a `# RULESET` paired with a Decisions section that does not sit directly after it, or whose name is unrelated (R-decisions-10).
- **decision-duplicates-rule** — a D-record restating a companion/active rule's constraint (R-decisions-11).

## History

- **F113** — the Principles facet was unified into Decisions; value statements became ordinary D-records.
- **2026-06-08** — the decisions/rules vocabulary re-split (rules portable, decisions applied). The central file gained the "master form": adoption `include::`, an `## Adoption implementation map`, and decision-side `**Cites:**` lines. [[CAE Decisions]] is the surviving worked example of that form.
- **2026-07-01 — the doctrine (F221, user-ratified).** Decisions are documentation; Warden computes only rulesets. The master form's machinery is retired: ruleset activation is by anchor traits ([[Warden Semantics]] § Rulesets), the implementation map's job moved into the rules themselves, and linkage moved to the rule side (`implements D<N>`). Accompanying rules ride in a companion `# RULESET` directly after the Decisions section.

## See also

- [[FCT Ruleset]] — companion facet: the ruleset format and how Warden computes rules.
- [[Warden Rule]] / [[Warden Semantics]] — the rule language and its activation semantics.
- [[Rulesets]] — the catalog.
- [[Mini Decisions]], [[Mini Architecture#Decisions]] — worked examples of the two current forms.
- [[MUX Decisions]] — worked example of a large central file (31 D-records; its top-of-file `include::` predates the 2026-07-01 doctrine).
- [[MUX Rules]] — worked example of a stub `{NAME} Rules.md`.

# RULESET R-decisions
include::
where:: file:{ANCHOR}/** Design/**/*.md contains:(?m)^##\s+Decisions\s*$ ; file:{ANCHOR}/**/* Decisions.md
description:: spec for decisions — a `## Decisions` section (with `### D<N>` records) in any design doc, plus the optional central `{NAME} Decisions.md`

Embedded ruleset for the Decisions facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention (and itself the worked shape of the companion convention — prose above, ruleset directly below). Pulled in via the `R-facet` umbrella; active for an anchor through its traits ([[Warden Semantics]] § Rulesets). The rules cover the documentation shape only — Warden computes nothing against the decision content these files carry.

### RULE R-decisions-01 — Decisions live under a `## Decisions` section; the optional central file is `{NAME} Decisions.md` (checked)
check:: regex_present (?m)^##\s+Decisions\s*$

The canonical unit is a `## Decisions` H2 section holding `### D<N>` records, placed in the design doc the decision is *about*. The optional per-anchor central file is named `{NAME} Decisions.md` (the home for cross-cutting / value-statement decisions) — when present it opens with `# {NAME} Decisions` and its records sit directly under it (the file's H1 stands in for the `## Decisions` marker). The `where::` selector matches both: any Design-surface doc carrying a `## Decisions` section, and the central `* Decisions.md` file.

**Check pattern:** the selected doc contains a `## Decisions` H2 (or, for the central file, a `# {NAME} Decisions` H1) introducing `### D<N>` records.

**Why:** the `## Decisions` label is what makes decisions findable and aggregatable wherever they live. A decision recorded with no recognizable label is invisible to `/audit decisions` and to the computed decision-set view.

### RULE R-decisions-02 — H1 is `{NAME} Decisions` (checked)
check:: h1_present

The first heading is `# {NAME} Decisions` — the anchor slug plus the facet word, matching the file name.

**Check pattern:** an H1 line is present; its text is `{NAME} Decisions`.

**Why:** the H1 is the rendered title and the anchor of every `~~[[{NAME} Decisions]]~~` wiki-link. A missing or off-name H1 breaks navigation.

### RULE R-decisions-03 — retired 2026-07-01 (tracked)

Was: *top-of-file `include::` present.* Retired by the Decisions↔Rules doctrine (F221): a decisions surface carries no computed fields — Warden reads only `# RULESET` blocks, and ruleset activation is by anchor traits ([[Warden Semantics]] § Rulesets). The number stays retired per the never-recycle invariant.

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

**Why:** other docs cite decisions by id (`shaped by ~~[[{NAME} Decisions#D01|D01]]~~`), and rules tie back to them (`implements D<N>`). Recycling a number silently re-points every existing citation at a different decision — a correctness hazard with no error signal.

### RULE R-decisions-07 — Each D-record states its rationale (sampled)

Every D-record body explains *why*, not just *what* — via a `**Why.**` / `**Rationale.**` block or equivalent prose. A bare choice with no rationale is a fact, not a decision record.

**Check pattern:** for each D-record, assert the body contains a `**Why` / `**Rationale` marker or at least one full sentence of justification beyond the choice statement.

**Why:** the rationale is what stops a future reader (or agent) from re-litigating a settled choice. A decision file without rationale decays into a list of assertions nobody dares change because nobody knows why they hold.

### RULE R-decisions-08 — retired 2026-07-01 (tracked)

Was: *master form — every adopted rule has an implementation-map row.* Retired with the master form by the Decisions↔Rules doctrine (F221): how a constraint is satisfied lives with the rule itself, not in a decision-side table. The number stays retired per the never-recycle invariant.

### RULE R-decisions-09 — retired 2026-07-01 (tracked)

Was: *`**Cites:**` lines reference existing rules.* Retired by the Decisions↔Rules doctrine (F221): decision→rule citation is replaced by rule-side linkage — a rule notes the decision it implements (`implements D<N>`, loose coupling, unverified by the engine). The number stays retired per the never-recycle invariant.

### RULE R-decisions-10 — Companion ruleset sits directly after the Decisions section (sampled)

When a file pairs rules with its decisions, its `# RULESET R-<slug>` block begins **directly after the Decisions section** — nothing but the decisions list between the `## Decisions` header (or central-file H1 lead-in) and the sentinel — and the set's slug carries the same (or a clearly related) name as the Decisions section or file.

**Check pattern:** in a file containing both a Decisions surface and a `# RULESET` sentinel, assert no unrelated H1/H2 content zone intervenes between the last D-record and the sentinel; judge slug relatedness by name overlap with the section/file name.

**Why:** the pairing is the point — the reader sees *why* immediately above *what is enforced*, and DRY has a defined home. A ruleset drifting elsewhere in the file breaks the "still in the decisions file" guarantee.

### RULE R-decisions-11 — No decision duplicates a rule (stated)

If something can be expressed as a rule, it is written **only** as a rule, in the companion ruleset; the decisions list stays at the higher altitude (broader choices, stances, tradeoffs). A rule enforcing a decision links back with an `implements D<N>` note on the rule's side.

**Check pattern:** flag D-records whose body restates a companion or active rule's constraint near-verbatim.

**Why:** duplication forks the source of truth — the rule evolves under Warden while the decision copy silently drifts, and readers can no longer tell which wording is in force.

# BRIEF

- **This is the facet spec for decisions** — the documentation layer above Warden's rules. Core doctrine (user-ratified 2026-07-01, F221): decisions guide like rules but **Warden never computes against them**; form is `## Decisions` + the list of `### D<N>` records; anything directly checkable is a rule only (DRY); accompanying rules ride in a companion `# RULESET` directly after the Decisions section under a same-or-related name; linkage is rule-side (`implements D<N>`, loose).
- **NOT a list of decisions** — never paste anchor-specific D-records into this spec. Worked examples are referenced as wiki-links ([[Mini Decisions]], [[MUX Decisions]]); concrete D-records live in their owning anchor.
- **Inclusion test:** content belongs here only if it is a structural convention for *every* anchor's decisions (the section form, D-record shape, companion-ruleset placement, audit checks). Ruleset format and Warden computation belong in [[FCT Ruleset]] / [[Warden Rule]]; per-anchor decision content belongs in the owning anchor.
- **Load-bearing constraints to preserve:** D-numbers are monotonic-forever and never recycled; status tokens are exactly `checked` / `open` / `revised` / `retired`; rule numbers R-decisions-03/08/09 stay retired (never reassign them); the companion `# RULESET` sits directly after the Decisions section; the implements-linkage lives only on the rule side — don't reintroduce decision-side `**Cites:**` lines or adoption `include::`.
- **Naming/linking:** keep the [[FCT Ruleset]] ↔ [[FCT Decisions]] cross-references intact (this is the companion-facet pairing); [[Rulesets]] is the canonical catalog name.
- **Don't pile cross-facet content here** — markdown rendering rules → [[R-markdown]]; project-wide rules → `CLAUDE.md`; ruleset authoring shape → [[FCT Ruleset]]. This file is strictly the decisions facet.
