# RULESET R-ruleset
include::
where:: `sentinel: ^#+ RULESET R-`
description:: Format every ruleset definition obeys — sentinels, header fields, per-rule structure, numbering, includes.

The rules a `# RULESET` definition must satisfy — checked on **every ruleset, wherever it lives**: standalone `R-*.md` files **and** inline `# RULESET` blocks embedded in facet, skill, and discipline specs (e.g. `R-anchor-page` in [[DAS Anchor Page]], `R-markdown` in [[DAS markdown]]). The `where::` is a **content sentinel** — any file with a `# RULESET R-` heading (fence-aware: fenced *example* RULESETs are skipped) — so embedded sets are caught without enumerating their host files. Self-applying: this set obeys its own rules.

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

### RULE R-ruleset-12 — `where::` uses predefined lowercase tokens + standard globs (stated)

A `where::` value is `always`, a path glob (optionally `file:`-prefixed), `anchor`, or `sentinel: <regex>`. Inside a glob, a `{...}` group is a predefined token only when its content (no comma) is one of the reserved names `{anchor}`, `{slug}`, `{vault}`, `{repo}`; any comma-bearing or non-reserved brace group is glob alternation. The authored line backtick-wraps the whole expression — `` where:: `file:{anchor}/**/*.md` `` — so the glob characters (`*`, `{}`, `!`) render as inline code instead of corrupting the markdown (F172); parsers strip the single surrounding pair, and the bare legacy form is still accepted.

**Check pattern:** for each `where::`, assert the scope kind is one of the four forms (after stripping the surrounding backtick pair); assert every `{...}` group is either a recognized predefined token (content is one of the reserved names) or a valid alternation (comma-bearing or non-reserved).

**Why:** keeps `{anchor}` (substitution) unambiguous from `{a,b}` (alternation) and catches typo'd selectors that would silently match nothing. See § Where clause — the rule selector.
