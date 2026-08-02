# RULESET R-decisions
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/** Design/**/*.md contains:(?m)^##\s+Decisions\s*$ ; file:{anchor}/**/* Decisions.md`
description:: spec for decisions — a `## Decisions` section (with `### D<N>` records) in any design doc, plus the optional central `{slug} Decisions.md`

Embedded ruleset for the Decisions facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention (and itself the worked shape of the companion convention — prose above, ruleset directly below). Pulled in via the `R-facet` umbrella; active for an anchor through its traits ([[Warden Semantics]] § Rulesets). The rules cover the documentation shape only — Warden computes nothing against the decision content these files carry.

### RULE R-decisions-01 — Decisions live under a `## Decisions` section; the optional central file is `{slug} Decisions.md` (checked)
check:: regex_present (?m)^##\s+Decisions\s*$

The canonical unit is a `## Decisions` H2 section holding `### D<N>` records, placed in the design doc the decision is *about*. The optional per-anchor central file is named `{slug} Decisions.md` (the home for cross-cutting / value-statement decisions) — when present it opens with `# {slug} Decisions` and its records sit directly under it (the file's H1 stands in for the `## Decisions` marker). The `where::` selector matches both: any Design-surface doc carrying a `## Decisions` section, and the central `* Decisions.md` file.

**Check pattern:** the selected doc contains a `## Decisions` H2 (or, for the central file, a `# {slug} Decisions` H1) introducing `### D<N>` records.

**Why:** the `## Decisions` label is what makes decisions findable and aggregatable wherever they live. A decision recorded with no recognizable label is invisible to `/audit decisions` and to the computed decision-set view.

### RULE R-decisions-02 — H1 is `{slug} Decisions` (checked)
check:: h1_present

The first heading is `# {slug} Decisions` — the anchor slug plus the facet word, matching the file name.

**Check pattern:** an H1 line is present; its text is `{slug} Decisions`.

**Why:** the H1 is the rendered title and the anchor of every `~~[[{slug} Decisions]]~~` wiki-link. A missing or off-name H1 breaks navigation.

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

**Why:** other docs cite decisions by id (`shaped by ~~[[{slug} Decisions#D01|D01]]~~`), and rules tie back to them (`implements D<N>`). Recycling a number silently re-points every existing citation at a different decision — a correctness hazard with no error signal.

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
