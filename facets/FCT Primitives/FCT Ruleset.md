---
description: "the Ruleset facet — what a ruleset is and the format every ruleset file (a standalone `R-<slug>` or an anchor-local {NAME} Rules.md) must take"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Primitives]] → [FCT Ruleset](hook://p/FCT%20Ruleset)

# FCT Ruleset
A named, reusable bundle of audit-checkable rules — and the spec for how to write one.

**Related:** [[FCT Facet]],  [[FCT Skill]],  [[FCT Decisions]] (companion),  [[Rulesets]] (the catalog),  [[FCT Primitives]]
**Examples:** [[R-fex-manifest\|small, standalone]],  [[R-diagram\|large, standalone]],  [[CAE Rules\|anchor-local Rules.md]]

**TLDR**
- **What it is** — a named bundle of portable, audit-checkable rules (`# RULESET R-<slug>`), or an anchor-local `{NAME} Rules.md`.
- **Required form** — `RULESET` / `RULE` sentinels; `include::` + `description::` header; `### RULE R-<slug>-NN (tier)` entries with a `**Check pattern:**`.
- **How it's used** — adopted by being cited from an anchor's `{NAME} Decisions.md`; checked by `/audit rules`.
- **Detection** — file-existence + the `# RULESET R-` content sentinel (catches embedded rulesets too); cardinality **many**.

## Overview
The Ruleset facet specifies the format for any file that **defines rules** — whether a catalog ruleset under `~/.claude/skills/SKL User Docs/SKL/SKL Library/Rulesets/` or an anchor-local `{NAME} Rules.md` under `{NAME} Design/`.

A **rule** is a standing constraint or guideline — portable, reusable, audit-checkable. A **ruleset** is a named bundle of rules that travel together. Rules are pulled into an anchor by being cited from the anchor's `{NAME} Decisions.md` (anchor-specific applied choices with rationale).

See [[FCT Decisions]] for the companion facet (anchor-level decisions). See [[Rulesets]] for the catalog. The rules a ruleset file must itself satisfy are the embedded **`# RULESET R-ruleset`** below — this facet's required, self-applying ruleset.

## History note

This spec was previously deprecated post-F113, when "Principles + Rules" were unified into "Decisions." The 2026-06-08 vocabulary refinement re-split: rules (portable constraints) live in Rulesets and use this facet; decisions (anchor-specific applied choices) live in `{NAME} Decisions.md` and use [[FCT Decisions]]. Decisions cite rules.

## When this facet applies

**Required reading for:**
- Any file in `SKL Library/Rulesets/` — both individual rulesets and umbrella sets that include others.
- Any `{NAME} Rules.md` an anchor authors when it has rules too anchor-specific to belong in a shared ruleset.

**Not required for:**
- `{NAME} Decisions.md` (that's [[FCT Decisions]]).
- Most anchors — most adopt rulesets via decisions and never write their own `{NAME} Rules.md`.

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
- **`where::` line (optional — F161; sits between `include::` and `description::`): the set-level selector.** Names which files this set's rules apply to — the default for any rule without its own `where::`. A glob (with the anchor-root token `{ANCHOR}`), or `always` / `anchor` / `sentinel: <regex>`. **Full syntax — the predefined `{ANCHOR}` / `{NAME}` tokens, glob rules, precedence, and exhaustive examples — is in § Where clause — the rule selector below.** Consumed by the audit engine ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]) to bind rules to targets; dogfooded in `# RULESET R-ruleset` below.
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
### RULE R-testing-01 — File name is `{NAME} Testing.md` (checked)
#### RULE R-mux-design-04 — Workers run as separate processes (stated)
## RULE R-disk-naming-01 — Drive names are uppercase kebab
### RULE R-ad-hoc-01
```

**Regex to find every rule, anywhere in the vault:**

```bash
grep -rnE '^#+\s+RULE\s+R-' --include='*.md' .
```

**Rules can live anywhere a markdown heading can.** Inside `# RULESET R-<slug>` blocks (the canonical home); inside a project's `{NAME} Design/<doc>.md` (implicitly part of that project's design ruleset); inside a facet's CAB doc as an embedded RULESET; inside an architecture decision record; inside a discussion doc. The sentinel makes the rule machine-discoverable wherever it lives.

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

**Scope kinds.** The value after `where::` is one of:

| Form | Binds the rule to |
|---|---|
| `always` | every file the audit visits. The default when no `where::` is in force. |
| `<glob>` or `file: <glob>` | every file whose path matches the glob. `file:` is the default reading of a bare glob, so `where:: {ANCHOR}/**/*.md` ≡ `where:: file: {ANCHOR}/**/*.md`. |
| `anchor` | the anchor as a whole — a once-per-anchor structural / tree check (e.g. "the anchor has exactly one Backlog"), not a per-file check. |
| `sentinel: <regex>` | any file containing a line matching the regex, **regardless of path**. A path-independent content match — how `R-ruleset` (below) catches every ruleset, including ones embedded in facet / skill / discipline specs. |

**Path globs are anchor-relative; `{ANCHOR}` names the root.** A path glob is matched against each candidate file's path, resolved **relative to the adopting anchor's root**. The predefined token `{ANCHOR}` names that root explicitly:

- `{ANCHOR}/Docs/**/*.md` — every markdown file under the anchor's `Docs/`.
- A **bare** glob (no leading token, no leading `/`) is equivalent — also anchor-relative — but the explicit `{ANCHOR}/` form is **recommended** in shared rulesets so the base is unmistakable.

**Predefined tokens are `{ALL-CAPS}` in curly braces.** The all-caps-in-braces namespace is reserved for substitutions the audit engine fills in per adopting anchor:

| Token | Substitutes |
|---|---|
| `{ANCHOR}` | the adopting anchor's root **directory** (a path) |
| `{NAME}` | the adopting anchor's **name** string (e.g. `CAE`) — the same `{NAME}` used in filenames like `{NAME} Backlog.md` |

`{VAULT}` (the kmr root) and `{REPO}` (a code anchor's repository root) are **reserved** for future use. Any new predefined token must be ALL-CAPS, to stay clear of glob alternation (below).

**Glob syntax** (gitignore / picomatch flavor):

| Pattern | Matches |
|---|---|
| `*` | any run of characters except `/` |
| `**` | any run *including* `/` — crosses directory boundaries |
| `?` | exactly one character (not `/`) |
| `[abc]`, `[a-z]` | one character from the set / range |
| `{a,b,c}` | **alternation** — any one of the comma-separated alternatives (lower / mixed case — *not* a predefined token) |
| trailing `/` | directories only (e.g. `{ANCHOR}/Docs/*/`) |
| leading `!` | **negation** — exclude matches (gitignore-style); a later pattern can re-include |

**Disambiguation — `{ANCHOR}` token vs `{a,b}` alternation.** A brace group is a **predefined token** iff its entire content is a single reserved ALL-CAPS identifier (`{ANCHOR}`, `{NAME}`). Otherwise it is **glob alternation** (`{svg,png}`, `{PRD,Roadmap}` — "Roadmap" is mixed-case, so the group is alternation, not a token). This is the whole reason the predefined tokens are ALL-CAPS: it keeps `{ANCHOR}` (substitution) unambiguous from `{svg,png}` (alternation) in the same syntax.

**Multiple globs and exclusions.** `where::` takes a comma-separated list; the rule applies to the **union** of the positive patterns minus the negated ones — `where:: {ANCHOR}/**/*.md, !{ANCHOR}/**/Closet/**`.

### Exhaustive examples

Each row is a complete `where::` value:

| `where::` value | The rule runs against |
|---|---|
| *(omitted)* | every file — falls through to `always` |
| `always` | every file the audit visits |
| `anchor` | once per anchor — a structural / tree check, not per-file |
| `{ANCHOR}/{NAME}.md` | exactly the anchor page |
| `{ANCHOR}/*.md` | markdown files in the anchor **root only** (non-recursive) |
| `{ANCHOR}/**/*.md` | every markdown file anywhere under the anchor |
| `{ANCHOR}/Docs/**` | everything (any type) under `Docs/`, recursively |
| `{ANCHOR}/Docs/*/` | the immediate **sub-folders** of `Docs/` (trailing `/` = dirs) |
| `{ANCHOR}/**/{NAME} Backlog.md` | the backlog file wherever it sits in the tree |
| `{ANCHOR}/**/{NAME} {PRD,Roadmap}.md` | the PRD **and** the Roadmap — `{NAME}` token + `{PRD,Roadmap}` alternation in one glob |
| `{ANCHOR}/**/F[0-9][0-9][0-9] — *.md` | feature docs (zero-padded `F<NNN>` prefix) |
| `{ANCHOR}/**/*.{svg,png}` | all SVG and PNG files (brace alternation) |
| `{ANCHOR}/src/**/*.rs` | Rust sources under the code repo's `src/` |
| `{ANCHOR}/**/*.md, !{ANCHOR}/**/Yore/**` | all markdown **except** anything archived under a `Yore/` folder |
| `**/*.md` | anchor-relative bare glob — identical to `{ANCHOR}/**/*.md` (explicit form preferred) |
| `file: {ANCHOR}/**/*.md` | the explicit `file:` form — identical to the bare-glob row above |
| `sentinel: ^#+ RULESET R-` | any file containing a `# RULESET R-` line, **anywhere** — path-independent (catches embedded rulesets) |
| `{VAULT}/**/*.md` | *(reserved)* vault-wide, once `{VAULT}` is defined |

### Set default + rule override — worked shape

A set declares a default `where::`; a single rule overrides it. Literal ruleset syntax:

```
# RULESET R-backlog
include::
where:: {ANCHOR}/**/{NAME} Backlog.md
description:: Structure every {NAME} Backlog.md obeys.

### RULE R-backlog-01 — Rows carry a status bracket (checked)
(no own where:: — inherits the set's: runs on the backlog file)
**Check pattern:** ...

### RULE R-backlog-07 — Anchor has exactly one backlog (checked)
where:: anchor
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

A script `flatten-ruleset.py` (under [[Rulesets]] tooling, to be written per F132) implements the recursive walk. `/audit rules` reads its flat output. The script is what makes audit walks easy — agents get a single fixed list to check against rather than chasing includes through multiple files.

## How decisions cite rules

In `{NAME} Decisions.md`, each decision body ends with a `Cites:` line listing the rules it applies:

```markdown
### D1 — Architecture diagram authored in SVG with arrows + labels.

We chose hand-written SVG over D2 or Excalidraw to keep full control of palette, font, and arrow style consistent with the project's existing diagram aesthetic. Every arrow carries an italic-blue verb label.

**Cites:** ~~[[R-c4-01]]~~ (every arrow labeled), ~~[[R-wcag-contrast-01]]~~ (contrast ≥4.5:1), ~~[[R-wcag-contrast-02]]~~ (color is not the sole communicator).
```

Audit walks decisions, collects every `Cites:` reference, flattens through includes, and verifies each cited rule.

## Trait applicability

Available to any anchor that needs to author or adopt rules. Most anchors won't author a `{NAME} Rules.md` — they adopt rulesets via decisions. The facet exists to spec the format for the rare case AND for the ruleset catalog.

## Audit

`/audit rules` flags:
- **rule-id-collision** — two rules with the same `R-<slug>-NN` identifier within the same ruleset.
- **broken-include** — a `## Includes` wiki-link resolves to nothing.
- **include-cycle** — A includes B includes A (any cycle).
- **missing-tier** — H3 rule header has no `(tier)` annotation.
- **missing-check-pattern** — `(checked)`- or `(sampled)`-tier rule has no `**Check pattern:**` block.
- **orphan-rule-citation** — `{NAME} Decisions.md` `Cites:` references a rule that doesn't exist in any adopted ruleset.

## See also

- [[FCT Decisions]] — companion facet (anchor-level applied choices).
- [[Rulesets]] — the catalog of cross-cutting, owner-scoped, and trait-scoped rulesets.
- [[R-diagram]] — worked example (22 diagram-validation rules in 5 zones, from the 2026-06-08 survey).
- [[CAE Rules]] — worked example of `{NAME} Rules.md` (anchor-local; adopts `R-diagram`).

# RULESET R-ruleset
include::
where:: sentinel: ^#+ RULESET R-
description:: Format every ruleset definition obeys — sentinels, header fields, per-rule structure, numbering, includes.

The rules a `# RULESET` definition must satisfy — checked on **every ruleset, wherever it lives**: standalone `R-*.md` files **and** inline `# RULESET` blocks embedded in facet, skill, and discipline specs (e.g. `R-anchor-page` in [[FCT Anchor Page]], `R-markdown` in [[DSC markdown]]). The `where::` is a **content sentinel** — any file with a `# RULESET R-` heading (fence-aware: fenced *example* RULESETs are skipped) — so embedded sets are caught without enumerating their host files. Self-applying: this set obeys its own rules.

### RULE R-ruleset-01 — H1 carries the `RULESET` sentinel (checked)
check:: regex_present ^#+ RULESET R-[a-z0-9-]+$

The set opens with `# RULESET R-<slug>` — the all-caps `RULESET` sentinel plus the set's `R-<slug>` id.

**Check pattern:** the opening heading matches `^#+ RULESET R-[a-z0-9-]+$`.

**Why:** the sentinel is how flatten / lint scripts identify a ruleset unambiguously.

### RULE R-ruleset-02 — `include::` line present under the header (checked)

An `include::` Dataview line sits in the header block — present even when empty (the empty line is the include slot).

**Check pattern:** a header line (before the first blank line after the H1) matches `^include::`.

### RULE R-ruleset-03 — `description::` line present (checked)

A one-line `description::` tagline is in the header; its value carries no `::` token.

**Check pattern:** a header line matches `^description:: .+` and the value contains no `::`.

### RULE R-ruleset-04 — every rule heading carries the `RULE` sentinel + id (checked)

Each rule is a heading of the form `<H> RULE R-<slug>-NN[ — name][ (tier)]`.

**Check pattern:** every rule heading matches `^#+ RULE R-[a-z0-9-]+-\d{2}\b`.

### RULE R-ruleset-05 — rule numbers are two-digit, unique, non-recycled (checked)

`NN` is zero-padded to two digits and unique within the set; retired numbers are never reused.

**Check pattern:** collect every `R-<slug>-NN`; assert each `NN` is `\d{2}` and there are no duplicates within the set.

### RULE R-ruleset-06 — every rule has a tier annotation (checked)

Each rule title ends with `(tracked)` / `(stated)` / `(sampled)` / `(checked)`.

**Check pattern:** each `RULE` heading matches `\((tracked|stated|sampled|checked)\)\s*$`.

### RULE R-ruleset-07 — `checked` / `sampled` rules carry a Check pattern (checked)

A `(checked)` or `(sampled)` rule has a `**Check pattern:**` block in its body.

**Check pattern:** for each such rule, the body up to the next heading contains `**Check pattern:**`.

### RULE R-ruleset-08 — includes resolve (checked)

Every name / wiki-link in `include::` resolves to an existing ruleset.

**Check pattern:** resolve each `include::` target by vault search; flag any that miss.

### RULE R-ruleset-09 — no include cycle (checked)

The `include::` graph is acyclic.

**Check pattern:** depth-first walk the include graph from this set; flag any back-edge.

### RULE R-ruleset-10 — every rule resolves a selector (stated)

Each rule has an effective `where::` — its own, else the set's, else the `always` default. A set whose rules are *not* universal declares an explicit `where::` rather than silently relying on `always`.

**Check pattern:** for each rule, confirm an own-or-inherited `where::`; warn when a file-specific set has none (it would default to `always` and run on every file).

### RULE R-ruleset-11 — standalone ruleset files are body-only (checked)

A standalone `R-<slug>.md` has no YAML frontmatter (an embedded `# RULESET` lives inside a facet page that may carry its own frontmatter).

**Check pattern:** if the file's first non-blank line is `# RULESET`, assert no `---` frontmatter precedes it.

### RULE R-ruleset-12 — `where::` uses predefined `{ALL-CAPS}` tokens + standard globs (stated)

A `where::` value is `always`, a path glob (optionally `file:`-prefixed), `anchor`, or `sentinel: <regex>`. Inside a glob, a `{...}` group is a predefined token only when its content is a reserved ALL-CAPS identifier (`{ANCHOR}`, `{NAME}`); lower / mixed-case brace groups are glob alternation.

**Check pattern:** for each `where::`, assert the scope kind is one of the four forms; assert every `{...}` group is either a recognized predefined token or a valid alternation (lower / mixed case).

**Why:** keeps `{ANCHOR}` (substitution) unambiguous from `{a,b}` (alternation) and catches typo'd selectors that would silently match nothing. See § Where clause — the rule selector.

# BRIEF

- **This file is the prescriptive spec for the Ruleset facet** — the authoritative format definition for any ruleset file (`R-<slug>.md` in `Rulesets/`) and any anchor-local `{NAME} Rules.md`. Editors of either kind of file consult this page before authoring. (Renamed from `FCT Rules` 2026-06-13 — singular `Ruleset` for the kind, parallel to [[FCT Facet]]; [[Rulesets]] remains the plural catalog.)
- **Not a catalog of rules** — never inline actual rules here. Individual rulesets live under `~/.claude/skills/SKL User Docs/SKL/SKL Library/Rulesets/`; the catalog is [[Rulesets]]. This page only specifies *how* such files are shaped.
- **Not the decisions spec** — anchor-level applied choices belong in [[FCT Decisions]]. Keep the two facets cleanly separated; cross-reference but do not merge. Rules are portable constraints; decisions are anchor-specific applications that cite rules.
- **Load-bearing sentinels** — the all-caps `RULESET` (in the H1) and `RULE` (in rule headings) are mechanical markers grep / lint / flatten scripts depend on. Never lowercase or rename them; never invent alternates. The `include::` / `description::` lines are Dataview inline fields — preserve the exact `::` double-colon syntax and positional ordering (H1, then `include::`, then `description::`, then body).
- **Inclusion test for new content here:** does this clarify the *file format* (lines, sentinels, naming, audit ties, composition semantics)? If yes, add it. If it's *content of a specific ruleset* — put it in the ruleset. If it's *project-wide markdown* — link to [[R-markdown]]. If it's *brief-writing rules* — link to [[FCT Brief]].
- **When the format evolves**, bump the dated parenthetical in the affected section header (e.g. `## File shape — body-only, prescriptive structure (2026-06-08)`), update the worked examples ([[R-diagram]], [[CAE Rules]]), and check the `/audit rules` checks list at the bottom for new lint cases.
- **Don't restructure the H2 ordering** — the spec flows History note → When this facet applies → File shape → Where clause → Naming → Audit tiers → Include composition → How decisions cite rules → Trait applicability → Audit → See also. Auditors and downstream skills locate sections by this order.
