---
description: per-rule-set or per-anchor rules file — body-only markdown (no frontmatter) defining a named rule set with optional includes; rules are H3-numbered with audit-tier annotation. Companion to CAB Decisions (anchor-specific applied choices cite rules from rule sets). Re-activated 2026-06-08 after the rules-vs-decisions vocabulary split.
---

# CAB Rules

The Rules facet specifies the format for any file that **defines rules** — whether a catalog rule set under `~/.claude/skills/SKL User Docs/SKL/SKL Library/Rule Sets/` or an anchor-local `{NAME} Rules.md` under `{NAME} Design/`.

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. A **rule set** is a named bundle of rules that travel together. Rules are pulled into an anchor by being cited from the anchor's `{NAME} Decisions.md` (anchor-specific applied choices with rationale).

See [[CAB Decisions]] for the companion facet (anchor-level decisions). See [[Rule Sets]] for the catalog.

## History note

This spec was previously deprecated post-F113, when "Principles + Rules" were unified into "Decisions." The 2026-06-08 vocabulary refinement re-split: rules (portable constraints) live in Rule Sets and use this facet; decisions (anchor-specific applied choices) live in `{NAME} Decisions.md` and use [[CAB Decisions]]. Decisions cite rules.

## When this facet applies

**Required reading for:**
- Any file in `SKL Library/Rule Sets/` — both individual rule sets and umbrella sets that include others.
- Any `{NAME} Rules.md` an anchor authors when it has rules too anchor-specific to belong in a shared rule set.

**Not required for:**
- `{NAME} Decisions.md` (that's [[CAB Decisions]]).
- Most anchors — most adopt rule sets via decisions and never write their own `{NAME} Rules.md`.

## File shape — body-only, prescriptive structure (2026-06-08)

No YAML frontmatter. Every load-bearing piece is a visible markdown element a reader can see. The format is **prescriptive** — the lines below are required at the positions described. Worked example: [[R-diagram]].

```markdown
# RULESET R-<slug>
include:: [[R-other-set]], [[R-third-set]]
description:: One-line tagline — 8–15 words. Plain prose; no `::` tokens.

Body paragraph: provenance, use-case context, source attribution, history. Plain
prose; any length. This is where longer "what this set is about" content lives.

### R-<slug>-01 — Short rule name (tier)

Declarative statement of what the rule requires or forbids.

**Check pattern:** how `/audit rules` mechanically detects violations of this rule.

**Why:** one or two sentences of rationale or prior-incident context (optional).

**Exceptions:** a table or list of acknowledged exceptions, or absent.

### R-<slug>-02 — Next rule (tier)
...
```

### Required lines (positional, prescriptive)

- **Line 1: H1 with sentinel word `RULESET`.** Exactly `# RULESET R-<slug>`. The all-caps `RULESET` is a sentinel that lint scripts and human readers use to identify "this file is a rule set" definitively — no ambiguity with anchor pages, decision docs, or feature docs that share folder space.
- **Line 2 (immediately under H1): `include::` line** — Dataview inline field. Comma-separated list of rule sets included by this set. May be empty (`include::` with nothing after). **Always present** even when empty — the line's existence tells readers and parsers "this is the include slot." Two forms accepted:
    - **Bare names** — `include:: R-sugiyama, R-c4` — resolved by the flatten script via vault search.
    - **Wiki-links** — `include:: [[R-sugiyama]], [[R-c4]]` — clickable in Obsidian reading view; otherwise equivalent. The flatten script unwraps `[[...]]` before resolving. Wiki-link form is preferred for readability when authoring in Obsidian; bare form is fine for machine-generated files.
    - The two may be mixed within a single line (`include:: R-sugiyama, [[R-c4]]`). Strike-through markers (`~~[[R-foo]]~~`) are an Obsidian rendering artifact and not part of the format; flatten and audit ignore them and resolve the underlying name.
- **Line 3: `description::` line** — Dataview inline field. One-line tagline (8–15 words) of what this rule set covers and when it applies. Required. Plain prose only: **no `::` tokens in the value** (the double-colon is reserved syntax for inline-field keys; mentioning `include::` or `description::` as a noun inside the value will collide with the Dataview parser). The single-line constraint forces tightness.
- **Line 4+ (body paragraph immediately under `description::`):** plain prose paragraph(s) carrying provenance, use-case context, source attribution, history, factoring notes — anything longer than the tagline. Any length. This is the canonical home for the prose that doesn't fit in `description::`; it reads more naturally than `> [!info]` callouts for the standard "what this set is about" content. Callouts remain available for asides (see below).

Both `include::` and `description::` use Obsidian Dataview's inline-field syntax (`key:: value` — takes the rest of the line as the value). The keys render as bold text in Reading view, and Dataview can query them. Queries like "which rule sets include R-sugiyama" work without parsing.

### Multiple rule sets in one file

A file may define multiple rule sets — each `# RULESET R-<slug>` H1 opens a new scope, and its own `include::` / `description::` lines apply only to that scope (until the next H1 or end of file). The flatten / audit scripts walk the file and parse each rule set independently. This is how MUX's `MUX Rules.md` carries two rule sets (`R-state-management` and `R-observability`) in one file.

### Callouts are commentary, not structure

`> [!info]` callouts may appear anywhere in the body but are NOT a defined part of the rule set's structure. They're free-form notes for human readers — context, history, examples, attribution. The audit / flatten scripts ignore them. **Do not use callouts to encode structured fields** (description, include, exceptions, etc.) — those have their own dedicated mechanisms (`description::`, `include::`, the `**Exceptions:**` block).

### Optional / repeatable elements

- **`> [!info]` callouts as comments.** Anywhere in the body. Format: `> [!info] <Title>` followed by `> <body lines>`. Treated as commentary; the auditor and flatten scripts ignore them. Use them for: describing the rule set's purpose (the "Rule Set" callout immediately after `include:` is the customary place), explaining the format to readers learning it, flagging open questions / TBDs, attribution notes (e.g., "Adapted from Sourcetrail 2024 article").
- **H4 zone headers (`#### Zone X — ...`).** Optional presentational grouping for long rule sets. Rule identity is the rule heading (any H-level carrying `RULE R-<slug>-NN`), not the zone — H4 zones are just visual organization. When a rule set is factored into smaller per-methodology sets, zones go away (each sub-set IS what the zones were).

### Rule entries — `<H> RULE R-<slug>-NN` sentinel form (2026-06-10)

Each individual rule is a markdown heading whose first content is the all-caps `RULE` sentinel followed by the rule identifier. This makes rules **greppable anywhere** in the vault, not only inside `# RULESET R-<slug>` files — a vault-wide rule audit is one regex away.

**Format:**

```
<H> RULE R-<slug>-NN[ — <short name>[ (<tier>)]]
```

- **`<H>`** — any heading level (`#` … `######`). H3 is the customary default inside `# RULESET` blocks; H4 is appropriate when nested under a zone H3; H2 / H1 are valid when a rule stands alone in a doc that doesn't carry other H1 / H2 content. **No level is reserved**; choose whatever fits the surrounding structure.
- **`RULE`** — literal all-caps sentinel. Parallel to the `RULESET` sentinel that opens a rule set's H1. The sentinel is the mechanical marker; the slug is the human identifier.
- **`R-<slug>-NN`** — the rule's identifier and unique handle. NN is zero-padded two digits, monotonic-forever within the slug's namespace. Cross-document and cross-vault references use this string directly (`see [[R-testing-04]]`, `cites: [[R-mux-design-02]]`).
- **`— <short name>`** *(optional)* — em-dash separator followed by a brief human-readable title. Recommended in any rule set or any spot where multiple rules cluster; omit only when the slug itself is self-explanatory.
- **`(<tier>)`** *(optional)* — audit tier annotation in parentheses. Recommended whenever the rule's verification posture is known. Omit if the rule is purely informational and not audit-bound.

**Examples — all valid:**

```markdown
### RULE R-testing-01 — File name is `{NAME} Testing.md` (checked)
#### RULE R-mux-design-04 — Workers run as separate processes (stated)
## RULE R-disk-naming-01 — Drive names are uppercase kebab
### RULE R-ad-hoc-01
```

**Regex to find every rule, anywhere in the vault:**

```bash
grep -rnE '^#+\s+RULE\s+R-' --include='*.md' .
```

**Rules can live anywhere a markdown heading can.** Inside `# RULESET R-<slug>` blocks (the canonical home); inside a project's `{NAME} Design/<doc>.md` (implicitly part of that project's design rule set); inside a facet's CAB doc as an embedded RULESET; inside an architecture decision record; inside a discussion doc. The sentinel makes the rule machine-discoverable wherever it lives.

**Rule body** (any number of paragraphs immediately following the heading):

- **First paragraph:** declarative statement — what is required or forbidden.
- **`**Check pattern:**` paragraph** — how the rule is mechanically (or semi-mechanically) verified. Required for `(checked)` and `(sampled)` tiers; optional for `(stated)` and `(tracked)`.
- **`**Why:**` paragraph** (optional) — rationale, source attribution, prior-incident context.
- **`**Exceptions:**` block** (optional) — table or list of acknowledged exceptions.

The body ends at the next heading at the same or shallower level.

## Naming convention

- **Rule set name:** `R-<kebab-slug>` (e.g., `R-diagram`, `R-mac-app`, `R-sugiyama`, `R-c4`). The H1 of the file matches the basename of the file (`R-diagram.md` → `# R-diagram`). For well-known external methodologies, use the methodology's name directly (`R-sugiyama` for Sugiyama-style graph drawing, `R-c4` for the C4 model).
- **Rule name within a set:** `R-<slug>-<NN>` with NN zero-padded two digits, monotonic-forever within the set, never recycled. Example: `R-diagram-04` is stable; if rule 04 is deprecated, NN 04 stays retired and new rules append at the next unused number.
- **Composition does NOT renumber.** When `R-diagram` includes `R-sugiyama`, Sugiyama's rules retain their `R-sugiyama-NN` identity. There's no `R-diagram-23` that's "really" `R-sugiyama-01` — the source set is the rule's home and identity.

## Audit-tier annotation (after the rule title)

| Tier | Meaning |
|---|---|
| `(tracked)` | Recorded for awareness; no automated check. |
| `(stated)` | Stated as policy; manual review during code review or audit. |
| `(sampled)` | Random or risk-prioritized sampling by `/audit rules`. |
| `(checked)` | Mechanically checked on every audit pass. |

Tiers are aspirational ladders — a rule may start at `(stated)` and graduate to `(checked)` once the audit logic is written.

## Include composition — semantics

The `include:` line under the H1 names other rule sets that this set absorbs by reference. Example:

```markdown
# RULESET R-diagram
include: R-sugiyama, R-c4, R-wcag-contrast
```

When an auditor flattens this rule set:
1. Read this set's rules.
2. Recursively read each included set's rules (depth-first; cycles forbidden).
3. Concatenate into one flat list. Rules retain their source-set identity (`R-sugiyama-01` doesn't become `R-diagram-23`).
4. Optionally deduplicate or apply local overrides — the umbrella set can shadow an included rule by re-declaring it with the same `R-<source>-NN` name and an updated body.

A script `flatten-rule-set.py` (under [[Rule Sets]] tooling, to be written per F132) implements the recursive walk. `/audit rules` reads its flat output. The script is what makes audit walks easy — agents get a single fixed list to check against rather than chasing includes through multiple files.

## How decisions cite rules

In `{NAME} Decisions.md`, each decision body ends with a `Cites:` line listing the rules it applies:

```markdown
### D1 — Architecture diagram authored in SVG with arrows + labels.

We chose hand-written SVG over D2 or Excalidraw to keep full control of palette, font, and arrow style consistent with the project's existing diagram aesthetic. Every arrow carries an italic-blue verb label.

**Cites:** [[R-c4-01]] (every arrow labeled), [[R-wcag-contrast-01]] (contrast ≥4.5:1), [[R-wcag-contrast-02]] (color is not the sole communicator).
```

Audit walks decisions, collects every `Cites:` reference, flattens through includes, and verifies each cited rule.

## Trait applicability

Available to any anchor that needs to author or adopt rules. Most anchors won't author a `{NAME} Rules.md` — they adopt rule sets via decisions. The facet exists to spec the format for the rare case AND for the rule-set catalog.

## Audit

`/audit rules` flags:
- **rule-id-collision** — two rules with the same `R-<slug>-NN` identifier within the same rule set.
- **broken-include** — a `## Includes` wiki-link resolves to nothing.
- **include-cycle** — A includes B includes A (any cycle).
- **missing-tier** — H3 rule header has no `(tier)` annotation.
- **missing-check-pattern** — `(checked)`- or `(sampled)`-tier rule has no `**Check pattern:**` block.
- **orphan-rule-citation** — `{NAME} Decisions.md` `Cites:` references a rule that doesn't exist in any adopted rule set.

## See also

- [[CAB Decisions]] — companion facet (anchor-level applied choices).
- [[Rule Sets]] — the catalog of cross-cutting, owner-scoped, and trait-scoped rule sets.
- [[R-diagram]] — worked example (22 diagram-validation rules in 5 zones, from the 2026-06-08 survey).
- [[CAE Rules]] — worked example of `{NAME} Rules.md` (anchor-local; adopts `R-diagram`).

# BRIEF

- **This file is the prescriptive spec for the Rules facet** — the authoritative format definition for any rule-set file (`R-<slug>.md` in `Rule Sets/`) and any anchor-local `{NAME} Rules.md`. Editors of either kind of file consult this page before authoring.
- **Not a catalog of rules** — never inline actual rules here. Individual rule sets live under `~/.claude/skills/SKL User Docs/SKL/SKL Library/Rule Sets/`; the catalog is [[Rule Sets]]. This page only specifies *how* such files are shaped.
- **Not the decisions spec** — anchor-level applied choices belong in [[CAB Decisions]]. Keep the two facets cleanly separated; cross-reference but do not merge. Rules are portable constraints; decisions are anchor-specific applications that cite rules.
- **Load-bearing sentinels** — the all-caps `RULESET` (in the H1) and `RULE` (in rule headings) are mechanical markers grep / lint / flatten scripts depend on. Never lowercase or rename them; never invent alternates. The `include::` / `description::` lines are Dataview inline fields — preserve the exact `::` double-colon syntax and positional ordering (H1, then `include::`, then `description::`, then body).
- **Inclusion test for new content here:** does this clarify the *file format* (lines, sentinels, naming, audit ties, composition semantics)? If yes, add it. If it's *content of a specific rule set* — put it in the rule set. If it's *project-wide markdown* — link to [[R-markdown]]. If it's *brief-writing rules* — link to [[CAB Brief]].
- **When the format evolves**, bump the dated parenthetical in the affected section header (e.g. `## File shape — body-only, prescriptive structure (2026-06-08)`), update the worked examples ([[R-diagram]], [[CAE Rules]]), and check the `/audit rules` checks list at the bottom for new lint cases.
- **Don't restructure the H2 ordering** — the spec flows History note → When this facet applies → File shape → Naming → Audit tiers → Include composition → How decisions cite rules → Trait applicability → Audit → See also. Auditors and downstream skills locate sections by this order.
