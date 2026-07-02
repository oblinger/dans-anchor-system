# Rulesets Brief

Editing-and-maintenance brief for [[Rulesets]]. Read before adding a new ruleset folder, restructuring the catalog, or auditing what belongs here.

## What this catalog is

Curated, versioned bundles of rules. Each set is a standalone markdown doc bundling related rules that apply to a specific style of anchor, a specific cross-cutting concern, or a CAB-aligned axis (facet / trait / skill). An anchor's traits activate the sets that apply to it ([[Warden Semantics]] § Rulesets); Warden computes only the rules — decisions ([[FCT Decisions]]) are the documentation layer above them.

## Five kinds of sets

- **CAB-aligned umbrellas** — the three primary structural axes paralleling CAB's own categories: [[R-facet]] (per-facet), [[R-trait]] (per-trait), [[R-skill]] (per-skill). Each umbrella's `include::` rolls up rulesets that eventually embed into the corresponding CAB spec file (`CAB Facets/<Facet>.md`, `traits/<Trait>.md`, or `~/.claude/skills/<skill>/SKILL.md`).
- **Cross-cutting / global** — not tied to a specific facet, trait, or skill (`R-arch`, `R-code`, `R-diagram`, `R-doc`, `R-git`, `R-process`, `R-test`). Pulled in when an anchor explicitly opts in. "Cross-cutting" and "global" mean essentially the same thing — global = not within a particular topic area.
- **Trait-scoped** — children of [[R-trait]] (`R-paper`, `R-simple`, `R-skill-anchor`, `R-topic`). Activate when the anchor declares the matching Trait. Migrate into `traits/<Trait>.md` specs as content firms up.
- **Owner-scoped** — pulled in by every anchor a given owner owns, regardless of trait (`R-ob` = Dan's personal set).
- **Folder-file convention** — every `R-<name>/` folder contains an `R-<name>.md` folder-file RULESET (see below).

## Rules vs decisions — the vocabulary distinction

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. Lives in a Ruleset; gets adopted across many anchors. "ASCII forbidden in architecture diagrams." "Must use Helvetica."

A **decision** is a broader, higher-level applied choice with rationale, recorded at the anchor level (a `## Decisions` section in the doc it shapes, or `{NAME} Decisions.md`). "We chose SQLite for TaskStore because of operator-readability." The rationale is what makes it a *decision*; anything directly verifiable is written only as a rule, never duplicated as a decision.

The relationship (doctrine per [[FCT Decisions]], 2026-07-01):

- **Rulesets** (this catalog) bundle rules. Each rule has an audit-tier annotation (`tracked` / `checked` / `sampled` / `stated`).
- **Anchor decisions** record the anchor's broader choices — documentation Warden pays no attention to. Rules that accompany decisions ride in a companion `# RULESET` directly after the Decisions section.
- **Warden / audit** compute only the rules — bound by traits + `where::`, never verified against decision content. A rule implementing a decision links back with a loose `implements D<N>` note.

(Renamed from "Decision Sets" 2026-06-08. The previous naming collapsed the rules-and-decisions distinction; the rename honors both terms.)

## Folder-file convention

Every ruleset folder named `R-<name>/` contains a folder-file `R-<name>.md` that is itself a RULESET. The folder-file's `include::` line rolls up all child rulesets in the folder. Adopting the folder umbrella (e.g., `include:: [[R-code]]`) is equivalent to adopting every child set; cherry-pick individual children for finer control.

## Pull semantics

When an anchor adopts a ruleset:

1. The set is activated for the anchor via its traits (`.anchor`), or pulled onto the `include::` line of the anchor's own companion `# RULESET`.
2. Each rule retains its source-set identity (`R-sugiyama-01` doesn't become `R-mine-23`).
3. The anchor is free to diverge from the source set; divergence is visible in the local copy via D-records.
4. Set updates get pulled when the user runs `/rule refresh <set>` — never silently.

## File format

See [[FCT Ruleset]] for the prescriptive RULESET format (H1 sentinel + `include::` + `description::` + H3 rule entries with tier annotation). The earlier YAML-frontmatter form is legacy; remaining instances ([[R-mac]]) will be migrated per F133.

## How to add a new ruleset

1. Create `Rulesets/R-<name>/R-<name>.md` (with `.anchor` marker).
2. Use the prescriptive RULESET format per [[FCT Ruleset]].
3. Add a row to [[Rulesets]] dispatch table under the appropriate category.
4. If the set should auto-aggregate under R-facet / R-trait / R-skill, also add to that umbrella's `include::`.

## Related

- [[Rulesets]] — the catalog itself.
- [[FCT Ruleset]] — meta-spec for the RULESET format.
- [[FCT Decisions]] — sibling facet for anchor-level recorded choices (rules link back via `implements D<N>`).
- F132, F133 — features tracking the rule-system migration.
