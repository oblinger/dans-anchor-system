# RULESET R-ruleset
include::
import:: skills/audit/scripts/audit-plan.py
where:: `sentinel: ^#+ RULESET R-`
description:: Format every ruleset definition obeys — sentinels, header fields, per-rule structure, numbering, includes.

> **Four checkers wired 2026-08-11 ([[Tink Backlog#^T349|T349]]), two refused — and the four were sitting registered, tested, and invoked by nothing.**
>
> `--verify-registry` reports **24 orphan checkers**: registered in the dispatch table, called by no rule. Four of them name rules in *this* set almost verbatim, and this set is inside the closure `/audit doc` resolves — so `-04`, `-05`, `-07` and `-11` read `(checked)` while `_needs_judgment` (a membership test excluding only `tracked`/`retired`/`governing`) sent each one to a **billed LLM call** on every one of the **123 files carrying the `RULESET` sentinel**. Their own comments say what they were for: `chk_all_rules_have_id` records that it sheds a defect *"so that wiring it later does not re-import"* it. Later was never scheduled.
>
> Measured before wiring, over all 123:
>
> | Rule | Checker | Findings |
> |---|---|---|
> | `-04` | `all_rules_have_id` | **0** |
> | `-05` | `rule_numbers_unique` | **0** |
> | `-07` | `checked_rules_have_pattern` | **10** — `R-layering`, `R-ob-observability`, `R-completed-roadmap`, `R-one-path` (×2), `R-interfaces-folder`, `R-svg-jiggle` (×3), and more |
> | `-11` | `ruleset_no_frontmatter` | **0** |
>
> Three of the four find nothing, and that is the argument for wiring them rather than against it: **492 judgments become 492 instant mechanical verdicts, and the 10 real findings stop being invisible behind them.** A rule that is silently judged is not cheaper than one that is checked — it is more expensive and less trustworthy, and it reports the same green.
>
> **`-02` and `-03` are refused, and the measurement is why.** `chk_header_has_field include` fails **16** of 123 — but `_header_block` ends at the first blank line after the H1, and files like [[R-feed]] put a blank line between the H1 and their `include::`. The line is *there*; the checker cannot see it. Wiring that reports 16 files as missing a field they carry. `chk_description_field_line` fails **106 of 123 (86%)** because it demands `description::` be the **second non-blank line**, while `-03` asks only that a header line match it. That is the [[R-anchor-page]]-01 signature exactly — a rule the corpus can satisfy only by mass-editing a hundred files toward no benefit — and the rule text, not the corpus, is the thing that would have to change. Both stay judgments until a checker matches what the rule actually says.
>
> **`-08`, `-09` have no registered checker at all** (include resolution, cycle detection); `-10` and `-12` are `(stated)`. Nothing else in this set is wirable today.

The rules a `# RULESET` definition must satisfy — checked on **every ruleset, wherever it lives**: standalone `R-*.md` files **and** inline `# RULESET` blocks embedded in facet, skill, and discipline specs (e.g. `R-anchor-page` in [[DAS Anchor Page]], `R-markdown` in [[DAS markdown]]). The `where::` is a **content sentinel** — any file with a `# RULESET R-` heading (fence-aware: fenced *example* RULESETs are skipped) — so embedded sets are caught without enumerating their host files. Self-applying: this set obeys its own rules.

### RULE R-ruleset-01 — H1 carries the `RULESET` sentinel (checked)
check:: regex_present ^#+ RULESET R-[a-z0-9-]+$

The set opens with `# RULESET R-<slug>` — the all-caps `RULESET` sentinel plus the set's `R-<slug>` id.

**Check pattern:** the opening heading matches `^#+ RULESET R-[a-z0-9-]+$`.

**Why:** the sentinel is how flatten / lint scripts identify a ruleset unambiguously.

### RULE R-ruleset-02 — `include::` line present under the header (checked)

> **`header_has_field include` NOT wired 2026-08-11 ([[Tink Backlog#^T349|T349]]) — and the reason generalizes past this rule.** The primitive resolves *the header* as the run of lines under the file's **head H1**. This set is scoped by a `sentinel:`, and a sentinel matches wherever the heading occurs — so for the **7 of 123** subjects that carry their ruleset *embedded* in a larger document ([[DAS Ruleset]], `Template Examples`, [[FEX Pin]], [[FEX Bundle]], two Warden rulesets, and [[HA Rules]]), the primitive reads the **host document's** header instead of the ruleset's and reports every one of them missing. All 7 are false, and they are false as a class rather than by accident.
>
> **A head-H1-anchored primitive cannot serve a sentinel-scoped set.** The selector knows which heading it matched; the checker is handed only the file and starts over at the top. Any rule of the form *"the header carries `<field>::`"* in this set inherits the same defect, which is why the refusal is recorded here rather than as a note about one checker.
>
> **The other 9 were real, and all 9 are now fixed** — 2026-08-11, in the same pass, which is why the refusal above is a refusal to *wire* and not a refusal to act. [[R-spine]], [[R-examples]], [[R-dispatch-table]], [[R-progressive]] and `R-files-architecture` carried no `include::` line at all and now carry the empty slot this rule describes. [[R-feed]], [[R-stone]], [[R-rocks]] and [[R-stream]] carried one **below a blank line** — and the blank turned out not to be a disagreement between the grammar and the rule at all, but a defect both agree on: all four had an intact header block displaced one line down by a stray blank under the H1, against ~115 sets that put the first field directly beneath it. Deleting that blank line closed all four, and every set's parsed `where::` and rule count is byte-identical afterward, so nothing was rescoped to make a checker happy.
>
> **The corpus-wide count went 16 → 6, and the 6 that remain are exactly the false class** — [[DAS Ruleset]], `Template Examples`, [[FEX Pin]], [[FEX Bundle]] and the two Warden sets: every one an *embedded* ruleset whose host document's header the primitive reads instead of its own. That the residue is precisely the defect described above, with nothing else mixed into it, is the strongest available evidence that the refusal is about the primitive's anchoring and not about the corpus.
>
> **One thing surfaced while fixing these, was deferred for measurement, and is now closed — [[Tink Backlog#^T535|T535]], 2026-08-11.** [[R-dispatch-table]] declared its selector in **YAML frontmatter** (`where: "file: {anchor}/**/*.md"`), which `parse_ruleset_block` never reads, so both engines carried all **15** of its rules as `where=None` → `always`. The measurement the deferral was for came back **zero for markdown** — anchor-mode scope is `*.md` only, so `always` and the glob select the identical 905 files, and F297's `rows_for` sends non-markdown writes away from [[R-doc]] before these rules are reached — and non-zero for exactly one path: `/audit doc` named at a non-markdown file put all 15 masthead rules in play, **15 of the 31** rule-target pairs, three of them returning a green `check::` verdict about a Python file's masthead. Selector moved to the body; that path now yields 16 pairs and no dispatch rules, and every markdown verdict is byte-identical. The guard beneath it is fixed in the same pass — see `R-ruleset-11` below.

An `include::` Dataview line sits in the header block — present even when empty (the empty line is the include slot).

**Check pattern:** a header line (before the first blank line after the H1) matches `^include::`.

### RULE R-ruleset-03 — `description::` line present (checked)

A one-line `description::` tagline is in the header; its value carries no `::` token.

**Check pattern:** a header line matches `^description:: .+` and the value contains no `::`.

### RULE R-ruleset-04 — every rule heading carries the `RULE` sentinel + id (checked)
check:: all_rules_have_id

Each rule is a heading of the form `<H> RULE R-<slug>-NN[ — name][ (tier)]`.

**Check pattern:** every rule heading matches `^#+ RULE R-[a-z0-9-]+-\d{2}\b`.

### RULE R-ruleset-05 — rule numbers are two-digit, unique, non-recycled (checked)
check:: rule_numbers_unique

`NN` is zero-padded to two digits and unique within the set; retired numbers are never reused.

**Check pattern:** collect every `R-<slug>-NN`; assert each `NN` is `\d{2}` and there are no duplicates within the set.

### RULE R-ruleset-06 — every rule has a tier annotation (checked)
check:: all_rules_have_tier

Each rule title ends with one of the six tiers: `(checked)` / `(sampled)` / `(stated)` / `(tracked)` / `(retired)` / `(governing)`.

**Why this is the load-bearing rule of this ruleset, and not a tidiness one.** A heading whose tier `_RULE_RE` does not admit is **skipped**, and a skipped heading does not terminate the rule above it — so the `check::` line beneath it **folds onto its predecessor**, which then runs a checker that is not its own and reports that verdict as its own. `R-rocks-03` (cardinality) spent its life running `R-rocks-04`'s name-expansion checker and answering *"name is 'R0001' — not an abbreviation, nothing to expand"*: green on every rock group in the vault, never once evaluated. That was the **second** occurrence in the same ruleset — T156 records `(checked, warn)` folding rule 05 onto rule 04 five days earlier.

It recurs because **a malformed tier makes a rule invisible to the very checks that would catch it.** Every other consumer reads *parsed* rules, where the offending heading has already vanished; this rule is the only one that reads raw headings, and it was declared `(checked)` while carrying no `check::` of its own — its implementation `chk_all_rules_have_tier` sat registered and invoked by nothing since T099. Wired 2026-08-11 after [[ATT|Atticus]] traced the chain end to end.

**Two families share the `RULE` sentinel, and only one is in scope.** An audit rule ends in a tier; a **Warden hook rule** ends in `(when:: <moment>)` and carries `mend::` instead of `check::` — 31 of those exist, `audit-plan` does not model them at all, and they cannot fold because the field beneath them is not `check::`. They are exempt, and the exemption is in the checker rather than in prose.

**Check pattern:** every `RULE` heading outside a fence either matches `_RULE_RE` or ends `(when:: …)`.

### RULE R-ruleset-07 — `checked` / `sampled` rules carry a Check pattern (checked)
check:: checked_rules_have_pattern

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
check:: ruleset_no_frontmatter

A standalone `R-<slug>.md` has no YAML frontmatter (an embedded `# RULESET` lives inside a facet page that may carry its own frontmatter).

**Check pattern:** strip any leading `---` frontmatter block, then ask whether the first non-blank line of what remains is `# RULESET R-`; if it is, the file is standalone and the presence of that stripped block is the violation.

> **The Check pattern above was unsatisfiable as originally written, and that is why the rule caught nothing for as long as it existed ([[Tink Backlog#^T535|T535]], 2026-08-11).** It read *"if the file's first non-blank line is `# RULESET`, assert no `---` frontmatter precedes it"* — but nothing can precede a file's first non-blank line, so the guard's own entry condition excluded every violation. `chk_ruleset_no_frontmatter` implemented it literally, judged a frontmatter-bearing file by its opening `---`, and answered `('pass', 'not a standalone ruleset file')` about files named `R-*.md` sitting in `rulesets/`. Deciding kind on the body instead is the repair, and it was measured before landing: across all **122** vault files carrying a `# RULESET R-` block, exactly **one** verdict changes — [[R-fex-manifest]], the worked example of this very format, which carried frontmatter duplicating its own `description::`. Fixed in the same pass, so the rule is back to zero findings honestly rather than vacuously.

### RULE R-ruleset-12 — `where::` uses predefined lowercase tokens + standard globs (stated)

A `where::` value is `always`, a path glob (optionally `file:`-prefixed), `anchor`, or `sentinel: <regex>`. Inside a glob, a `{...}` group is a predefined token only when its content (no comma) is one of the reserved names `{anchor}`, `{slug}`, `{vault}`, `{repo}`; any comma-bearing or non-reserved brace group is glob alternation. The authored line backtick-wraps the whole expression — `` where:: `file:{anchor}/**/*.md` `` — so the glob characters (`*`, `{}`, `!`) render as inline code instead of corrupting the markdown (F172); parsers strip the single surrounding pair, and the bare legacy form is still accepted.

**Check pattern:** for each `where::`, assert the scope kind is one of the four forms (after stripping the surrounding backtick pair); assert every `{...}` group is either a recognized predefined token (content is one of the reserved names) or a valid alternation (comma-bearing or non-reserved).

**Why:** keeps `{anchor}` (substitution) unambiguous from `{a,b}` (alternation) and catches typo'd selectors that would silently match nothing. See § Where clause — the rule selector.
