# Rule Sets Brief

Editing-and-maintenance brief for [[Rulesets]]. Read before adding a new rule set folder, restructuring the catalog, or auditing what belongs here.

## What this catalog is

Curated, versioned bundles of rules. Each set is a standalone markdown doc bundling related rules that apply to a specific style of anchor, a specific cross-cutting concern, or a CAB-aligned axis (facet / trait / skill). When an anchor adopts a set, the set's rules are referenced from `{NAME} Decisions.md` as adopted constraints; the decision body explains why.

## Five kinds of sets

- **CAB-aligned umbrellas** — the three primary structural axes paralleling CAB's own categories: [[R-facet]] (per-facet), [[R-trait]] (per-trait), [[R-skill]] (per-skill). Each umbrella's `includes::` rolls up rule sets that eventually embed into the corresponding CAB spec file (`CAB Facets/<Facet>.md`, `CAB Traits/<Trait>.md`, or `~/.claude/skills/<skill>/SKILL.md`).
- **Cross-cutting / global** — not tied to a specific facet, trait, or skill (`R-arch`, `R-code`, `R-diagram`, `R-doc`, `R-git`, `R-process`, `R-test`). Pulled in when an anchor explicitly opts in. "Cross-cutting" and "global" mean essentially the same thing — global = not within a particular topic area.
- **Trait-scoped** — children of [[R-trait]] (`R-paper`, `R-simple`, `R-skill-anchor`, `R-topic`). Activate when the anchor declares the matching Trait. Migrate into `CAB Traits/<Trait>.md` specs as content firms up.
- **Owner-scoped** — pulled in by every anchor a given owner owns, regardless of trait (`R-ob` = Dan's personal set).
- **Folder-file convention** — every `R-<name>/` folder contains an `R-<name>.md` folder-file RULESET (see below).

## Rules vs decisions — the vocabulary distinction

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. Lives in a Rule Set; gets adopted across many anchors. "ASCII forbidden in architecture diagrams." "Must use Helvetica."

A **decision** is a specific applied choice with rationale, recorded at the anchor level in `{NAME} Decisions.md`. "We chose SQLite for TaskStore because of operator-readability." A decision cites the rule(s) it applies; the rationale is what makes it a *decision* and not just a rule citation.

The relationship:

- **Rule Sets** (this catalog) bundle rules. Each rule has an audit-tier annotation (`tracked` / `checked` / `sampled` / `stated`).
- **Anchor Decisions** (`{NAME} Decisions.md`) record the anchor's specific applied choices.
- **Audit** walks the decisions in an anchor's `{NAME} Decisions.md`, collects every referenced rule, and verifies each rule is satisfied. The rules are what get checked; the decisions are how the anchor declares which rules apply here and why.

(Renamed from "Decision Sets" 2026-06-08. The previous naming collapsed the rules-and-decisions distinction; the rename honors both terms.)

## Folder-file convention

Every rule-set folder named `R-<name>/` contains a folder-file `R-<name>.md` that is itself a RULESET. The folder-file's `includes::` line rolls up all child rule sets in the folder. Adopting the folder umbrella (e.g., `include:: [[R-code]]`) is equivalent to adopting every child set; cherry-pick individual children for finer control.

## Pull semantics

When an anchor adopts a rule set:

1. The set's rules are referenced from the anchor's `{NAME} Decisions.md` as a top-of-file `include::` line.
2. Each rule retains its source-set identity (`R-sugiyama-01` doesn't become `R-mine-23`).
3. The anchor is free to diverge from the source set; divergence is visible in the local copy via D-records.
4. Set updates get pulled when the user runs `/rule refresh <set>` — never silently.

## File format

See [[FCT Ruleset]] for the prescriptive RULESET format (H1 sentinel + `include::` + `description::` + H3 rule entries with tier annotation). The earlier YAML-frontmatter form is legacy; remaining instances ([[R-mac]]) will be migrated per F133.

## How to add a new rule set

1. Create `Rule Sets/R-<name>/R-<name>.md` (with `.anchor` marker).
2. Use the prescriptive RULESET format per [[FCT Ruleset]].
3. Add a row to [[Rulesets]] dispatch table under the appropriate category.
4. If the set should auto-aggregate under R-facet / R-trait / R-skill, also add to that umbrella's `includes::`.

## Related

- [[Rulesets]] — the catalog itself.
- [[FCT Ruleset]] — meta-spec for the RULESET format.
- [[FCT Decisions]] — sibling facet for anchor-level applied choices that cite rules.
- F132, F133 — features tracking the rule-system migration.
