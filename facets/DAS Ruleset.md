---
description: "the Ruleset facet — what a ruleset is and the format every ruleset file (a standalone `R-<slug>` or an anchor-local {slug} Rules.md) must take"
---

# DAS Ruleset
A named, reusable bundle of audit-checkable rules — and the spec for how to write one.

| -[[DAS Ruleset]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT]] → [DAS Ruleset](hook://p/DAS%20Ruleset)  |
| --- | --- |
| Related | [[DAS Facet]],  [[DAS Skill]],  [[DAS Decisions]] (companion),  [[DAS Rulesets]] (the catalog),  [[DAS Primitives]], |
| Rules | [[R-ruleset]],   |
| Examples | [[R-fex-manifest\|small, standalone]],  [[R-diagram\|large, standalone]],  [[FEX Rules\|anchor-local Rules.md]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |


**TLDR**
- **What it is** — a named bundle of portable, audit-checkable rules (`# RULESET R-<slug>`), or an anchor-local `{slug} Rules.md`.
- **Required form** — `RULESET` / `RULE` sentinels; `include::` + `description::` header; `### RULE R-<slug>-NN (tier)` entries with a `**Check pattern:**`.
- **How it's used** — activated for an anchor via its traits, composed via `include::`; computed by Warden (`/audit rules` + live hooks).
- **Detection** — file-existence + the `# RULESET R-` content sentinel (catches embedded rulesets too); cardinality **many**.

## Overview
The Ruleset facet specifies the format for any file that **defines rules** — whether a catalog ruleset under `rulesets/R-<name>.md` at the dans-anchor-system repo root or an anchor-local `{slug} Rules.md` under `{slug} Design/`.

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. A **ruleset** is a named bundle of rules that travel together. Rules bind to an anchor by **activation** — the anchor's traits pull in rulesets ([[Warden Semantics]] § Rulesets) — and to files via `where::`.

See [[DAS Decisions]] for the companion facet (anchor-level decisions). See [[DAS Rulesets]] for the catalog. The rules a ruleset file must itself satisfy are **[[R-ruleset]]** — this facet's required, self-applying ruleset, in the rulesets folder like every other set.

## History note

This spec was previously deprecated post-F113, when "Principles + Rules" were unified into "Decisions." The 2026-06-08 vocabulary refinement re-split: rules (portable constraints) live in Rulesets and use this facet; decisions (anchor-specific applied choices) live in `{slug} Decisions.md` and use [[DAS Decisions]]. The 2026-07-01 doctrine sets the current relationship — see § Relationship to decisions.

## When this facet applies

**Required reading for:**
- Any file in `SKL Library/Rulesets/` — both individual rulesets and umbrella sets that include others.
- Any `{slug} Rules.md` an anchor authors when it has rules too anchor-specific to belong in a shared ruleset.

**Not required for:**
- `{slug} Decisions.md` (that's [[DAS Decisions]]) — though a companion `# RULESET` embedded there follows this facet like any other.
- Most anchors — their rules arrive via trait activation and they never write their own `{slug} Rules.md`.

## File shape — body-only, prescriptive structure (2026-06-08)

No YAML frontmatter. Every load-bearing piece is a visible markdown element a reader can see. The format is **prescriptive** — the lines below are required at the positions described. Worked example: [[R-diagram]].

```markdown
# RULESET R-<slug>
include:: ~~[[R-other-set]]~~, ~~[[R-third-set]]~~
description:: the Ruleset primitive — what a ruleset is and how to write one

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

- **Line 1: H1 with sentinel word `RULESET`.** Exactly `# RULESET R-<slug>`. The all-caps `RULESET` is a sentinel that lint scripts and human readers use to identify "this file is a ruleset" definitively — no ambiguity with anchor pages, decision docs, or feature docs that share folder space.
- **Line 2 (immediately under H1): `include::` line** — Dataview inline field. Comma-separated list of rulesets included by this set. May be empty (`include::` with nothing after). **Always present** even when empty — the line's existence tells readers and parsers "this is the include slot." Two forms accepted:
    - **Bare names** — `include:: R-sugiyama, R-c4` — resolved by the flatten script via vault search.
    - **Wiki-links** — `include:: [[R-sugiyama]], [[R-c4]]` — clickable in Obsidian reading view; otherwise equivalent. The flatten script unwraps `~~[[...]]~~` before resolving. Wiki-link form is preferred for readability when authoring in Obsidian; bare form is fine for machine-generated files.
    - The two may be mixed within a single line (`include:: R-sugiyama, [[R-c4]]`). Strike-through markers (`~~[[R-foo]]~~`) are an Obsidian rendering artifact and not part of the format; flatten and audit ignore them and resolve the underlying name.
- **`import::` line (required iff any rule in the set names a `check::` or `fix::`; sits just under `include::`) — the Python that supplies this set's checker implementations.** Corpus-root-relative paths, one per line or comma/space-separated on one: `import:: skills/audit/scripts/audit-plan.py`. This is what lets a corpus be *handed* to the engine — before F289 the implementations lived at a path compiled into the engine, so a consumer could write `check:: my_thing` and had nowhere on disk to put `my_thing`. Paths are corpus-root-relative, not file-relative: rulesets live in `rulesets/` and checkers in `skills/`, so every file-relative import would open with `../` and break the moment a ruleset moved. Execution uses **one merged environment** — `check::` refs are global names against a flat registry, and per-ruleset environments would misdescribe that — but `warden compile` still verifies each set's refs against **its own** declared imports and warns on one that resolves only through a neighbour's, because that is the ref that breaks when the set is extracted into a new corpus. A name defined by two imported modules warns and first wins. `import::` is deliberately a distinct key from `include::`: one flattens rules into a trait, the other executes code, and a reader should not have to inspect a file extension to tell which. Spec: [[F289 — Checker registration — check refs must be corpus-supplied, not a hardcoded path|F289]].
- **`where::` line (optional — F161; sits between `include::` and `description::`): the set-level selector.** Names which files this set's rules apply to — the default for any rule without its own `where::`. A glob (with the anchor-root token `{anchor}`), or `always` / `anchor` / `sentinel: <regex>`. **Full syntax — the predefined `{anchor}` / `{slug}` tokens, glob rules, precedence, and exhaustive examples — is in § Where clause — the rule selector below.** Consumed by the audit engine ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]) to bind rules to targets; dogfooded in `# RULESET R-ruleset` below.
- **`confirm::` line (optional — F314; set-level or rule-level): who may accept a deviation from this rule.** The only value is `user`, and it means the agent may not write an exception row for this rule on its own say-so — it asks first, and records the grade it is given. Enforced through the grade column, which is the user's act: an ungraded (`?`) row against a `confirm:: user` rule **fails** the anchor's exception table until the grade arrives, so the proposal cannot sit there quietly as a permanent "pending". Precedence is `where::`'s — a rule's own `confirm::` > the set's > none. Reach for it where exceptions should be rare and each one deserves a conversation (the spine rules `R-spine-01/-03/-04`); leave it off where the agent proposing freely is the point. Full semantics: [[R-exception-discipline]] -09.
- **Line 3: `description::` line** — Dataview inline field. One-line tagline (8–15 words) of what this ruleset covers and when it applies. Required. Plain prose only: **no `::` tokens in the value** (the double-colon is reserved syntax for inline-field keys; mentioning `include::` or `description::` as a noun inside the value will collide with the Dataview parser). The single-line constraint forces tightness.
- **Line 4+ (body paragraph immediately under `description::`):** plain prose paragraph(s) carrying provenance, use-case context, source attribution, history, factoring notes — anything longer than the tagline. Any length. This is the canonical home for the prose that doesn't fit in `description::`; it reads more naturally than `> [!info]` callouts for the standard "what this set is about" content. Callouts remain available for asides (see below).

Both `include::` and `description::` use Obsidian Dataview's inline-field syntax (`key:: value` — takes the rest of the line as the value). The keys render as bold text in Reading view, and Dataview can query them. Queries like "which rulesets include R-sugiyama" work without parsing.

### Multiple rulesets in one file

A file may define multiple rulesets — each `# RULESET R-<slug>` H1 opens a new scope, and its own `include::` / `description::` lines apply only to that scope (until the next H1 or end of file). The flatten / audit scripts walk the file and parse each ruleset independently. This is how MUX's `MUX Rules.md` carries two rulesets (`R-state-management` and `R-observability`) in one file.

### Callouts are commentary, not structure

`> [!info]` callouts may appear anywhere in the body but are NOT a defined part of the ruleset's structure. They're free-form notes for human readers — context, history, examples, attribution. The audit / flatten scripts ignore them. **Do not use callouts to encode structured fields** (description, include, exceptions, etc.) — those have their own dedicated mechanisms (`description::`, `include::`, the `**Exceptions:**` block).

### Optional / repeatable elements

- **`> [!info]` callouts as comments.** Anywhere in the body. Format: `> [!info] <Title>` followed by `> <body lines>`. Treated as commentary; the auditor and flatten scripts ignore them. Use them for: describing the ruleset's purpose (the "Ruleset" callout immediately after `include:` is the customary place), explaining the format to readers learning it, flagging open questions / TBDs, attribution notes (e.g., "Adapted from Sourcetrail 2024 article").
- **H4 zone headers (`#### Zone X — ...`).** Optional presentational grouping for long rulesets. Rule identity is the rule heading (any H-level carrying `RULE R-<slug>-NN`), not the zone — H4 zones are just visual organization. When a ruleset is factored into smaller per-methodology sets, zones go away (each sub-set IS what the zones were).

### Rule entries — `<H> RULE R-<slug>-NN` sentinel form (2026-06-10)

Each individual rule is a markdown heading whose first content is the all-caps `RULE` sentinel followed by the rule identifier. This makes rules **greppable anywhere** in the vault, not only inside `# RULESET R-<slug>` files — a vault-wide rule audit is one regex away.

**Format:**

```
<H> RULE R-<slug>-NN[ — <short name>[ (<tier>)]]
```

- **`<H>`** — any heading level (`#` … `######`). H3 is the customary default inside `# RULESET` blocks; H4 is appropriate when nested under a zone H3; H2 / H1 are valid when a rule stands alone in a doc that doesn't carry other H1 / H2 content. **No level is reserved**; choose whatever fits the surrounding structure.
- **`RULE`** — literal all-caps sentinel. Parallel to the `RULESET` sentinel that opens a ruleset's H1. The sentinel is the mechanical marker; the slug is the human identifier.
- **`R-<slug>-NN`** — the rule's identifier and unique handle. NN is zero-padded two digits, monotonic-forever within the slug's namespace. Cross-document and cross-vault references use this string directly (`see ~~[[R-testing-04]]~~`, `cites: ~~[[R-mux-design-02]]~~`).
- **`— <short name>`** *(optional)* — em-dash separator followed by a brief human-readable title. Recommended in any ruleset or any spot where multiple rules cluster; omit only when the slug itself is self-explanatory.
- **`(<tier>)`** *(optional)* — audit tier annotation in parentheses. Recommended whenever the rule's verification posture is known. Omit if the rule is purely informational and not audit-bound.

**Examples — all valid:**

```markdown
### RULE R-testing-01 — File name is `{slug} Testing.md` (checked)
#### RULE R-mux-design-04 — Workers run as separate processes (stated)
## RULE R-disk-naming-01 — Drive names are uppercase kebab
### RULE R-ad-hoc-01
```

**Regex to find every rule, anywhere in the vault:**

```bash
grep -rnE '^#+\s+RULE\s+R-' --include='*.md' .
```

**Rules can live anywhere a markdown heading can**, but the canonical home is a standalone `rulesets/R-<slug>.md` file (repo-level sets migrated there 2026-07-13; the owning facet/discipline links the set from its masthead `Rules` row). The sentinel still catches a `# RULESET` block wherever it lives — a project's `{slug} Design/<doc>.md`, an architecture decision record, a discussion doc — so anchor-local and in-flight sets remain machine-discoverable.

**Rule body** (any number of paragraphs immediately following the heading):

- **First paragraph:** declarative statement — what is required or forbidden.
- **`**Check pattern:**` paragraph** — how the rule is mechanically (or semi-mechanically) verified. Required for `(checked)` and `(sampled)` tiers; optional for `(stated)` and `(tracked)`.
- **`**Why:**` paragraph** (optional) — rationale, source attribution, prior-incident context.
- **`**Exceptions:**` block** (optional) — table or list of acknowledged exceptions.

The body ends at the next heading at the same or shallower level.

## Where clause — the rule selector (`where::`)

Every rule applies to some set of targets. The `where::` selector names that set, so the audit engine ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]) can bind each rule to the files (or the anchor) it governs instead of running every rule against everything.

**Two levels, with precedence.**
- **Set-level** — a `where::` line in the header (between `include::` and `description::`) is the default for every rule in the set.
- **Rule-level** — a `where::` line as the first field in a rule's body (above `**Check pattern:**`) overrides the set default for that one rule.
- **Precedence:** a rule's own `where::` > the set's `where::` > the built-in default `always`.

A set whose rules are *not* universal should declare an explicit `where::` rather than silently relying on `always` (per `R-ruleset-10`).

**Authored form — backtick-wrap the whole expression (F172).** A selector is full of markdown-active characters (`*`, `{}`, `!`, `:`), so the canonical authored line wraps the entire value — prefix included — in a single pair of backticks: `` where:: `file:{anchor}/**/* PRD.md` ``. It renders as inline code and never corrupts the page. Parsers (`warden compile`, `audit-plan`) strip exactly one surrounding pair before reading the selector; the bare legacy form is accepted unchanged. The tables below document the selector **values** — each is authored inside the backtick wrap.

**Scope kinds.** The value after `where::` is one of:

| Form | Binds the rule to |
|---|---|
| `always` | every file the audit visits. The default when no `where::` is in force. |
| `<glob>` or `file: <glob>` | every file whose path matches the glob. `file:` is the default reading of a bare glob, so `where:: {anchor}/**/*.md` ≡ `where:: file: {anchor}/**/*.md`. |
| `anchor` | the anchor as a whole — a once-per-anchor structural / tree check (e.g. "the anchor has exactly one Backlog"), not a per-file check. |
| `sentinel: <regex>` | any file containing a line matching the regex, **regardless of path**. A path-independent content match — how `R-ruleset` (below) catches every ruleset, including ones embedded in facet / skill / discipline specs. |

**Path globs are anchor-relative; `{anchor}` names the root.** A path glob is matched against each candidate file's path, resolved **relative to the adopting anchor's root**. The predefined token `{anchor}` names that root explicitly:

- `{anchor}/Docs/**/*.md` — every markdown file under the anchor's `Docs/`.
- A **bare** glob (no leading token, no leading `/`) is equivalent — also anchor-relative — but the explicit `{anchor}/` form is **recommended** in shared rulesets so the base is unmistakable.

**Predefined tokens are reserved lowercase names in curly braces.** A small, fixed set of lowercase names is reserved for substitutions the audit engine fills in per adopting anchor:

| Token | Substitutes |
|---|---|
| `{anchor}` | the adopting anchor's root **directory** (a path) |
| `{slug}` | the adopting anchor's **name** string (e.g. `CAE`) — the same `{slug}` used in filenames like `{slug} Backlog.md` |

`{vault}` (the kmr root) and `{repo}` (a code anchor's repository root) are **reserved** for future use. The four reserved names are `{anchor}`, `{slug}`, `{vault}`, `{repo}` — all lowercase; ALL-CAPS is reserved strictly for `{{FILL_IN}}` user-supplied fields (double-brace), never for these engine tokens. Any new predefined token joins this reserved lowercase set.

**Glob syntax** (gitignore / picomatch flavor):

| Pattern | Matches |
|---|---|
| `*` | any run of characters except `/` |
| `**` | any run *including* `/` — crosses directory boundaries |
| `?` | exactly one character (not `/`) |
| `[abc]`, `[a-z]` | one character from the set / range |
| `{a,b,c}` | **alternation** — any one of the comma-separated alternatives (lower / mixed case — *not* a predefined token) |
| trailing `/` | directories only (e.g. `{anchor}/Docs/*/`) |
| leading `!` | **negation** — exclude matches (gitignore-style); a later pattern can re-include |

**Disambiguation — `{anchor}` token vs `{a,b}` alternation.** A brace group is a **predefined token** iff its entire content (no comma) is exactly one of the four reserved names `{anchor}`, `{slug}`, `{vault}`, `{repo}`. Otherwise it is **glob alternation** — any brace group containing a comma (`{svg,png}`, `{PRD,Roadmap}`) or a single non-reserved word is matched literally / as alternation, never substituted. Membership in the reserved set — not letter case — is what keeps `{slug}` (substitution) unambiguous from `{svg,png}` (alternation) in the same syntax.

**Multiple globs and exclusions.** `where::` takes a comma-separated list; the rule applies to the **union** of the positive patterns minus the negated ones — `where:: {anchor}/**/*.md, !{anchor}/**/Closet/**`.

### Exhaustive examples

Each row is a complete `where::` value:

| `where::` value | The rule runs against |
|---|---|
| *(omitted)* | every file — falls through to `always` |
| `always` | every file the audit visits |
| `anchor` | once per anchor — a structural / tree check, not per-file |
| `{anchor}/{slug}.md` | exactly the anchor page |
| `{anchor}/*.md` | markdown files in the anchor **root only** (non-recursive) |
| `{anchor}/**/*.md` | every markdown file anywhere under the anchor |
| `{anchor}/Docs/**` | everything (any type) under `Docs/`, recursively |
| `{anchor}/Docs/*/` | the immediate **sub-folders** of `Docs/` (trailing `/` = dirs) |
| `{anchor}/**/{slug} Backlog.md` | the backlog file wherever it sits in the tree |
| `{anchor}/**/{slug} {PRD,Roadmap}.md` | the PRD **and** the Roadmap — `{slug}` token + `{PRD,Roadmap}` alternation in one glob |
| `{anchor}/**/F[0-9][0-9][0-9] — *.md` | feature docs (zero-padded `F<NNN>` prefix) |
| `{anchor}/**/*.{svg,png}` | all SVG and PNG files (brace alternation) |
| `{anchor}/src/**/*.rs` | Rust sources under the code repo's `src/` |
| `{anchor}/**/*.md, !{anchor}/**/Yore/**` | all markdown **except** anything archived under a `Yore/` folder |
| `**/*.md` | anchor-relative bare glob — identical to `{anchor}/**/*.md` (explicit form preferred) |
| `file: {anchor}/**/*.md` | the explicit `file:` form — identical to the bare-glob row above |
| `sentinel: ^#+ RULESET R-` | any file containing a `# RULESET R-` line, **anywhere** — path-independent (catches embedded rulesets) |
| `{vault}/**/*.md` | *(reserved)* vault-wide, once `{vault}` is defined |

### Set default + rule override — worked shape

A set declares a default `where::`; a single rule overrides it. Literal ruleset syntax:

```
# RULESET R-sample
include::
where:: `{anchor}/**/{slug} Backlog.md`
description:: Structure every {slug} Backlog.md obeys.

### RULE R-sample-01 — Rows carry a status bracket (checked)
(no own where:: — inherits the set's: runs on the backlog file)
**Check pattern:** ...

### RULE R-sample-07 — Anchor has exactly one backlog (checked)
where:: `anchor`
(overrides the set default — a once-per-anchor structural check, not a per-file one)
**Check pattern:** ...
```

## Naming convention

- **Ruleset name:** `R-<kebab-slug>` (e.g., `R-diagram`, `R-mac-app`, `R-sugiyama`, `R-c4`). The H1 of the file matches the basename of the file (`R-diagram.md` → `# R-diagram`). For well-known external methodologies, use the methodology's name directly (`R-sugiyama` for Sugiyama-style graph drawing, `R-c4` for the C4 model).
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

The `include:` line under the H1 names other rulesets that this set absorbs by reference. Example:

```markdown
# RULESET R-diagram
include: R-sugiyama, R-c4, R-wcag-contrast
```

When an auditor flattens this ruleset:
1. Read this set's rules.
2. Recursively read each included set's rules (depth-first; cycles forbidden).
3. Concatenate into one flat list. Rules retain their source-set identity (`R-sugiyama-01` doesn't become `R-diagram-23`).
4. Optionally deduplicate or apply local overrides — the umbrella set can shadow an included rule by re-declaring it with the same `R-<source>-NN` name and an updated body.

A script `flatten-ruleset.py` (under [[DAS Rulesets]] tooling, to be written per F132) implements the recursive walk. `/audit rules` reads its flat output. The script is what makes audit walks easy — agents get a single fixed list to check against rather than chasing includes through multiple files.

## Relationship to decisions

Decisions ([[DAS Decisions]]) are the documentation layer above rules — broader recorded choices that guide agents and readers, but **Warden pays no attention to them**: it computes only rules. The coupling is loose and lives on the rule side — a rule that implements a decision notes it (`implements D<N>`), and anything directly checkable is written only as a rule (by convention in a companion `# RULESET` directly after a `## Decisions` section), never duplicated as a decision.

## Trait applicability

Available to any anchor that needs to author or adopt rules. Most anchors won't author a `{slug} Rules.md` — their rules arrive via trait activation, and anchor-local rules ride as a companion `# RULESET` in the decisions file ([[DAS Decisions]] § Companion ruleset). The facet exists to spec the format for the rare case AND for the ruleset catalog.

## Audit

`/audit rules` flags:
- **rule-id-collision** — two rules with the same `R-<slug>-NN` identifier within the same ruleset.
- **broken-include** — a `## Includes` wiki-link resolves to nothing.
- **include-cycle** — A includes B includes A (any cycle).
- **missing-tier** — H3 rule header has no `(tier)` annotation.
- **missing-check-pattern** — `(checked)`- or `(sampled)`-tier rule has no `**Check pattern:**` block.

## See also

- [[DAS Decisions]] — companion facet (anchor-level applied choices).
- [[DAS Rulesets]] — the catalog of cross-cutting, owner-scoped, and trait-scoped rulesets.
- [[R-diagram]] — worked example (22 diagram-validation rules in 5 zones, from the 2026-06-08 survey).
- [[FEX Rules]] — worked example of `{slug} Rules.md` (anchor-local; adopts `R-diagram`).

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative format is the body plus the self-applying `# RULESET R-ruleset` above; worked examples are [[R-diagram]] / [[FEX Rules]].)*

- **Spec, not a catalog** — never inline actual rules here; individual rulesets live under `rulesets/` and the catalog is [[DAS Rulesets]]. This page specifies only *how* ruleset files are shaped. (Renamed from `FCT Rules` 2026-06-13 — singular `Ruleset` for the kind, parallel to [[DAS Facet]]; [[DAS Rulesets]] stays the plural catalog.)
- **Inclusion test for new content:** does it clarify the *file format* (lines, sentinels, naming, audit ties, composition semantics)? If yes, add it. Content of a *specific* ruleset → put it in that ruleset. Project-wide markdown → link [[R-markdown]]. Brief-writing rules → link [[DAS Brief]].
- **When the format evolves:** bump the dated parenthetical in the affected section header (e.g. `## File shape … (2026-06-08)`), update the worked examples ([[R-diagram]], [[FEX Rules]]), and check the § Audit lint list for new cases.
- **Don't restructure the H2 ordering** (History note → When this facet applies → File shape → Where clause → Naming → Audit tiers → Include composition → Relationship to decisions → Trait applicability → Audit → See also) — auditors and downstream skills locate sections by this order.
