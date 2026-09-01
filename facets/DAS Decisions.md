---
description: decisions are documentation — recorded under a `## Decisions` section in the design doc they shape; Warden never computes against them. Anything directly checkable is a rule, living in the companion `# RULESET` directly after the Decisions section; rules link back with an implements-D{N} note.
---

| -[[DAS Decisions]]- | → [[DAS]] → [[FCT]] → [DAS Decisions](hook://p/DAS%20Decisions)  |
| --- | --- |
| Related | [[DAS Ruleset]],  [[DAS Architecture]],  [[DAS Design Docs]],  [[DAS Rulesets]],   |
| Examples | [[Mini Architecture#Decisions\|distributed — decision in the doc it shapes]],  [[Mini Decisions\|optional central — cross-cutting value only]],  [[FEX Decisions\|legacy central master (pre-doctrine include:: + implementation map)]],  [[HBR Decisions\|legacy central (durable rulings)]],   |
| Rules | [[R-decisions]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Proj]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Decisions
**Worked examples:** [[HBR Decisions]], [[Mini Decisions]], [[FEX Decisions]] 

The facet for recorded decisions — the documentation layer that sits above Warden's rules.

**TLDR** — A Decisions surface is simply an **H2 header `## Decisions`** followed by the list of decisions made — `### D<N> — Title (status)` records with rationale — placed in the design doc the decisions shape. Decisions constrain and guide the way rules do, **but Warden pays no attention to them**: they are documentation, never computed against. Anything directly verifiable is written **only as a rule**, in the companion `# RULESET` that by convention sits **directly after the Decisions section** under the same (or a clearly related) name; a rule ties itself back to the decision it implements with a loose `implements D<N>` note.

A **decision** is a broader, higher-level choice with rationale, recorded where it belongs. A **rule** is a lower-level, directly verifiable constraint, defined in a ruleset ([[DAS Ruleset]]) and computed by Warden. Decisions are for readers; rules are for the engine.

See [[DAS Ruleset]] for the companion facet (rulesets + Warden computation). See [[DAS Rulesets]] for the catalog.

## Decisions vs rules — the doctrine (2026-07-01)

User-ratified 2026-07-01 (F221). Four load-bearing points:

- **Decisions guide; Warden ignores them.** A decision constrains and guides exactly as a rule does — but the rule engine pays **no** attention to decisions. They are documentation: visible to the user and to any agent reading the doc, never parsed, bound, or verified by Warden. Rules ([[Warden Rule]]) are the computed layer.
- **Granularity picks the representation.** Decisions are the broader, higher-level choices; rules are the lower-level, directly verifiable / computable things. The test: if it can be mechanically checked (a `where::`/`if::` over files), write it as a **rule**; if it is a stance, a tradeoff, an architecture choice, record it as a **decision**.
- **Don't repeat yourself.** If something can be expressed as a rule, it is NOT also written as a decision — it lives only in the companion ruleset (which sits directly after the Decisions section, so it is still "in the decisions file"). No decision duplicates a rule.
- **Linkage lives on the rule's side.** One decision is often implemented by several rules; each such rule ties itself back with an `implements D<N>` note. Loose coupling — a readable note, not a formal join the engine resolves.

## Form — the Decisions section

A Decisions surface is simply an **H2 header `## Decisions`** followed by the list of the decisions made. Each decision on the list is a `### D<N> — <title> (<status>)` record (shape in § D-record structure). That is the whole form — no header fields, no computed lines; Warden reads nothing here. In the central `{slug} Decisions.md` the `# {slug} Decisions` H1 stands in for the `## Decisions` marker and the records sit directly under it.

## Where decisions live — distributed by default

A decision is *about* something — an architecture choice, an API shape, a tradeoff. **It is recorded where that something is designed**, not exiled to a central file. The unit is the **`## Decisions` section** — the recognizable label ("this section is decisions") — placed in whatever design doc the decision belongs to, holding one or more `### D<N>` records:

- An **architecture** decision → a `## Decisions` section in `{slug} Architecture.md`.
- A **PRD / product** decision → a `## Decisions` section in the PRD.
- A decision local to one **feature** → that feature doc's `## Decisions` (the same record shape as its bottom `## Resolved`).
- A **cross-cutting / value-statement** decision (Fail-loudly; one-clock) that belongs to no single doc → the **optional** `{slug} Decisions.md`.

This mirrors rulesets, with the load-bearing difference: **rulesets are *computed* (Warden runs them; `where::` binds them); decisions are *records* — never computed, just labeled.** A "decision set" therefore needs no activation machinery — it needs a recognizable marker so it can be *found and gathered*. The `## Decisions` H2 (with its `### D<N>` headers) is that marker. You can put **just one** record under it, or many.

**The "decision set" is a computed view, not a file.** Because every decision carries the `## Decisions` / `### D<N>` label, a sweep gathers them all into one view on demand — exactly how `Q.md` aggregates questions that physically live in feature docs. Source of truth is distributed (next to what it decides); the aggregate is derived (`/audit decisions` and any "walk all decisions" tool sweep the label, not a single file). Aggregation is the only tooling that touches decisions — Warden never verifies anything against their content.

**`{slug} Decisions.md` is OPTIONAL.** It is the home for cross-cutting / value-statement decisions (and, per the companion convention below, often hosts the anchor's own ruleset). It is **not** the forced container for every decision. When every decision has a natural home in a design doc, the anchor has **no** central Decisions file at all (file existence is a trait — omit it). The `### D<N>` record shape is identical wherever a `## Decisions` section lives.

## Retirement-fold — feature decisions promoted on close-out

A decision made inside a feature starts life in that feature doc's `## Resolved` (the same `### D<N>`-shaped record). While the feature is live that is its correct home — the feature/backlog item is the sole live venue for its own decisions ([[F247 — state is the sole write-path — doc-state ties to its backlog task and cascades to the queue|F247]]). But a feature is *transient*: on retirement its doc is finalized and archived, and its `## Resolved` archive would carry the decision's history off with it.

**Retirement-fold** (per [[F249 — Fold resolved decisions into durable spec docs on retirement|F249]]) closes that gap. At close-out ([[finalize]] § 3a), every `## Resolved` decision that shaped a *durable* doc is **promoted** into that doc's `## Decisions` section as a `### D<N>` record — placed by the same distributed-by-layer rule above (the doc the decision shaped), carrying a `folded from [[F<n>]] on retirement` provenance line, minting a fresh monotonic D-number. Decisions that shaped only the feature's own build stay with the archived feature doc. Placement is per-decision by layer, not per-feature: one feature's decisions may fold into several docs, because they genuinely belong at different layers.

The promotion is the *why-we-decided* sibling of the OpenSpec C-entry spec-delta fold (the *what-the-system-does*); both run in finalize's close-out, so the eventual OpenSpec change-migration reuses this fold rather than re-inventing it.

## Value statements (absorbed from the retired Principles facet)

A decision is not only a concrete applied choice ("we use `Sys` as the singleton clock"). It can also be a **value statement** — the load-bearing *why* behind the codebase's recurring choices ("Fail Loudly — errors propagate, no silent fallbacks"; "One Queue, One Clock — all scheduling flows through a single priority queue and injected clock"). These were formerly their own `{slug} Principles.md` facet (P-records); per [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]] they are now ordinary **D-records** — typically the most foundational and rarely-changing ones (a value-statement change signals a project pivot). Other docs reference them by ID exactly as they reference any decision: System Design and Architecture cite them when explaining a choice (`shaped by ~~[[{slug} Decisions#D01|D01]]~~`), and a rule names the decision it encodes on its own side (`implements D<N>` — § Implementation linkage). The separate Principles file is retired — value statements live here.

## Companion ruleset — rules ride in the same file

When rules accompany decisions, the corresponding **`# RULESET` goes in the same file, directly after the Decisions section**, and by convention carries **the same (or a clearly related) name** as the Decisions section — a `{slug} Decisions.md` hosts `# RULESET R-<name>`; a topical `## Parser decisions` section pairs with `# RULESET R-<name>-parser`. Two consequences:

- **One file, two layers.** The reader sees the *why* (the decisions) immediately above the *what is enforced* (the rules). Warden sees only the `# RULESET` block — the sentinel is what it parses; everything above it is invisible to the engine.
- **DRY has a home.** A directly checkable constraint goes in the companion ruleset and only there; the decisions list above it stays at the higher altitude. This is also where truly anchor-local rules live — the companion set covers most of what a separate `{slug} Rules.md` used to.

Mechanically this is the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention put to per-anchor work — the same way a facet spec carries its own `# RULESET` block. This very file is the worked shape: the facet's prose above, `# RULESET R-decisions` below.

> [!note] The companion form is for **corpus-resident docs only** — an out-of-corpus anchor's ruleset lives in `rulesets/apps/` (ruled by Dan, 2026-09-01 — [[Tink Backlog#^T362|T362]] Q1)
> Warden's `corpus_root()` resolves to `dans-anchor-system` and nothing else; `warden compile` walks only that root, and an anchor's `.anchor` `rules:` key is never read by the engine. That is **deliberate, not a gap**. Warden is a privileged surface — its rules gate every tool call and its hook output steers agents — while the vault deliberately has no provenance (commons: no attribution, machine sweeps) and carries foreign content (fetched pages, transcripts, inbox drops). Auto-discovering rules from anchors would let anything written anywhere on the filesystem become enforcement policy — an injection channel. So rule sources stay ONE enumerated, git-tracked directory with a single deliberate admission step (`warden compile`). Stated plainly so nobody "improves" this back to auto-discovery: the closed corpus defends against accidental pickup and drive-by content, not against a determined attacker with shell access — nothing at this layer can.
>
> **The out-of-corpus form:** the anchor's ruleset lives at **`rulesets/apps/R-<slug>.md`** in the corpus repo (a Warden-controlled folder, one file per project anchor); the anchor's Decisions/Rules doc **links** to it — never a parallel copy (single source of truth); it activates via the matching **trait** in the anchor's `.anchor` (`R-ha` → trait `ha`, the same name-derivation `warden compile` already applies to every ruleset). Give the rules a real `where::`/moment binding so they bite only on that anchor's tree — [[R-mac]]'s bare `always` is the cautionary case. The one-file "why above, what-below" reading is genuinely given up for these anchors; that is the price of the closed corpus, paid knowingly.
>
> **Verified, not inferred** ([[Atticus|Atticus]] 2026-08-11): [[HA Rules]] declared `rules: HA Track/HA Rules.md` and authored `# RULESET R-ha` in place; a fresh `warden compile` reported *617 rules from 122 rulesets* with **zero** `R-ha-*` in the IR. A `# RULESET` outside the corpus parses as prose — it reads as enforcement and enforces nothing. First movers under the ruling: `R-ha` ([[HA Rules]]) and `R-cat` ([[CAT Decisions]]).

**Two adjacent limits worth knowing before writing any code rule**, from the same pass: a `where::` file glob **cannot reach a `.rs` file** — `audit-plan.py`'s `enumerate_scope` is `.md`-only in anchor mode (`target.rglob("*.md")`) and is rooted at the anchor folder rather than the `code:` tree, so `R-ob-cmd-proc`'s `` `file:{anchor}/**/*.rs` `` selects nothing anywhere and never appears in a plan (measured: 94 rules over `prj/Hook Anchor`, 0 with a `.rs` target). Code rules must bind to the **`when:: write:rust`** moment instead, which the hook derives from the written file's extension and which therefore reaches source wherever it lives.

## Implementation linkage — on the rule's side

One decision may be implemented by several rules. That linkage is indicated **on the rules' side**: a rule that exists to enforce a decision carries a short note tying it back — `implements D07` in its body or `**Why:**` line, with a wiki-link when the decision lives in another file (`implements ~~[[{slug} Decisions#D07|D07]]~~`). This is **loose coupling, not a formal join**: Warden neither resolves nor verifies the note; it exists so a reader arriving at a rule can walk back to the choice that motivated it. The decision record itself stays plain prose — the linkage is recorded on the rule and read from the rule.

## D-record structure

Each D-record has:

- **H3 heading** — `### D<N> — <short title> (<status>)`. Status is one of `checked` (ratified, in force), `open` (under design), `revised` (superseded — link to replacement), `retired` (no longer applies).
- **Optional metadata block** — `**Subsystem:** ~~[[...]]~~`, `**Ratified:** date via ~~[[F-link]]~~`, etc.
- **Body** — the decision in prose. Often includes `**Why.**`, `**Alternatives considered.**`, `**Consequences.**` sub-blocks.

**D-record heading level — always `### D<N>` (H3).** Decision records are always H3, in every file, whether or not the file groups them. `## ` (H2) is reserved for *optional topical grouping* (e.g. `## Values`, `## Parser`) — each group then holds its `### D<N>` records — and for structural sections (`## See also`). A flat central file simply carries its `### D<N>` records directly under the lead-in (`# {slug} Decisions` → `### D<N>`, intentionally skipping H2, which stays reserved for grouping). This keeps every decision at one uniform depth across all files while leaving the H2 level free for structure. The audit enforces H3 (R-decisions-04). Use the `D<N>` token; the `DEC-<N>` form ([[DKT Decisions]]) is a tolerated legacy token variant.

**D-numbers are monotonic-forever, never recycled.** A retired or revised decision keeps its number; the replacement gets a fresh one (R-decisions-06).

## The optional central file

`{slug} Decisions.md` (at `{slug} Design/{slug} Architecture/` or `{slug} Design/`) holds the decisions that belong to no single design doc — cross-cutting rulings and value statements — plus, by the companion convention, the anchor's own `# RULESET` when it has one. Its spine:

- **`# {slug} Decisions`** H1 (stands in for the `## Decisions` marker).
- **`description::`** — one-line summary of the anchor's decision posture, in YAML frontmatter or as an inline line.
- **`### D<N>` records** directly under the lead-in.
- **Optional companion `# RULESET R-<name>`** directly after the records.

Worked instances: [[Mini Decisions]] (lean central — cross-cutting records only); [[HBR Decisions]] (durable rulings); [[Mini Architecture#Decisions]] (the distributed form). [[FEX Decisions]] is the **legacy master form** — its top-of-file adoption `include::`, `## Adoption implementation map`, and `**Cites:**` lines predate the 2026-07-01 doctrine (§ History) and are not authored in new files.

## When `{slug} Rules.md` is still useful

With the companion convention, anchor-local rules default to the `# RULESET` directly after the anchor's Decisions section. `{slug} Rules.md` remains for the structural cases:

- A **runtime-rewritten artifact** needs a physical home in the rules folder for tooling reasons (e.g., MUX's `MUX-R04 Exceptions.md` exception table for the OS-bridge-logging audit).
- The anchor is **hosting a future-shared ruleset in place** until it stabilizes and moves to the catalog.

When `{slug} Rules.md` is just a stub pointer to the decisions file, that's fine — the file stays for the folder's sake (because something else in the folder, like the exception table, needs the structural home).

## Trait applicability

**Cardinality: distributed.** A `## Decisions` section may appear in **any** design doc under the anchor's Design surface (Architecture, PRD, System Design, Interface, a feature doc's design) — wherever a decision belongs. The central `{slug} Decisions.md` is **optional and at most one** per anchor: present only when the anchor has cross-cutting / value-statement decisions (it then also hosts the companion ruleset, if the anchor has one). An anchor whose every decision has a natural home in a design doc has **no** central Decisions file. Available to every anchor; required of none.

## Audit

`/audit decisions` checks the **documentation shape only** — it never verifies code or rules against a decision's content (constraint verification is Warden's job, over rulesets). Flags:

- **missing-label** — D-records with no recognizable `## Decisions` marker (or central-file H1) above them.
- **status-without-content** — D-record header has `(checked)` but body is empty or contradicts the status.
- **companion-drift** — a `# RULESET` paired with a Decisions section that does not sit directly after it, or whose name is unrelated (R-decisions-10).
- **decision-duplicates-rule** — a D-record restating a companion/active rule's constraint (R-decisions-11).

## History

- **F113** — the Principles facet was unified into Decisions; value statements became ordinary D-records.
- **2026-06-08** — the decisions/rules vocabulary re-split (rules portable, decisions applied). The central file gained the "master form": adoption `include::`, an `## Adoption implementation map`, and decision-side `**Cites:**` lines. [[FEX Decisions]] is the surviving worked example of that form.
- **2026-07-01 — the doctrine (F221, user-ratified).** Decisions are documentation; Warden computes only rulesets. The master form's machinery is retired: ruleset activation is by anchor traits ([[Warden Semantics]] § Rulesets), the implementation map's job moved into the rules themselves, and linkage moved to the rule side (`implements D<N>`). Accompanying rules ride in a companion `# RULESET` directly after the Decisions section.

## See also

- [[DAS Ruleset]] — companion facet: the ruleset format and how Warden computes rules.
- [[Warden Rule]] / [[Warden Semantics]] — the rule language and its activation semantics.
- [[DAS Rulesets]] — the catalog.
- [[Mini Decisions]], [[Mini Architecture#Decisions]] — worked examples of the two current forms.
- [[MUX Decisions]] — worked example of a large central file (31 D-records; its top-of-file `include::` predates the 2026-07-01 doctrine).
- [[MUX Rules]] — worked example of a stub `{slug} Rules.md`.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec — the doctrine, the `## Decisions` + `### D<N>` form, D-record shape, companion-ruleset placement, audit checks — is the body + embedded `R-decisions` RULESET above; design rationale is the 2026-07-01 doctrine (F221) and [[F113 — Decisions facet — unify Principles + Rules; relocate Architecture|F113]].)*

- **NOT a list of decisions** — never paste anchor-specific D-records here; worked examples are referenced as wiki-links ([[Mini Decisions]], [[MUX Decisions]]), and concrete D-records live in their owning anchor.
- **Inclusion test** — content belongs only if it is a structural convention for *every* anchor's decisions (section form, D-record shape, companion-ruleset placement, audit checks); ruleset format + Warden computation → [[DAS Ruleset]] / [[Warden Rule]]; per-anchor decision content → the owning anchor; markdown rendering rules → [[R-markdown]]; project-wide rules → `CLAUDE.md`.
- **Don't regress** — rule numbers R-decisions-03/08/09 stay retired (never reassign, per the never-recycle invariant); don't reintroduce decision-side `**Cites:**` lines or adoption `include::` (retired with the master form by F221).
- **Cross-reference integrity** — keep the [[DAS Ruleset]] ↔ [[DAS Decisions]] companion-facet pairing intact; [[DAS Rulesets]] is the canonical catalog name.
