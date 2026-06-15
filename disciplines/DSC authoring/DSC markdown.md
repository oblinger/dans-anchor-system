---
name: markdown
description: Discipline. The "every time you write markdown" rules — both mechanical (rendering correctness — table escapes, fence rules, spacing) and authoring (always-apply quality — wiki-links not bare backticks, named lists, RULE/RULESET sentinels). Cited by every CAB facet, every design sub-skill, every authoring skill. Sibling discipline to [[DSC progressive-disclosure]] (which owns *what goes where in a doc*); markdown owns *how the markdown text itself is written*. Skill counterpart is [[md]] which owns user-invokable utility verbs (/md toc, /md file-tree, etc.).
user_invocable: false
---

# Markdown Discipline

The discipline for **how markdown TEXT is written** — applied to every markdown document in the vault, every time. Sibling to [[DSC progressive-disclosure]] (*what goes where in a doc*) and to the [[md]] skill (*utility verbs that produce or maintain markdown artifacts*).

Two flavors of rule live here, and both apply every time:

- **Mechanical rules** — rendering correctness. Skip these → the doc renders wrong. Examples: escape pipes inside wiki-links inside tables; blank line before / after a table; no wiki-links inside fenced code blocks (they don't render).
- **Authoring rules** — always-apply quality. Skip these → the doc renders but is wrong. Examples: references to other docs MUST be wiki-links not bare backticks; named-list format when content is naming-natured; the `RULE` / `RULESET` sentinel pattern for rule blocks.

The boundary against [[DSC progressive-disclosure]]: this discipline cares about the markdown *text*. Progressive-disclosure cares about the *doc structure* (preface zone, dispatch table patterns, figure placement, TLDR shape). If the question is "how do I write this line of markdown right," it's here; if "where in the doc does this section go," that's progressive-disclosure.


## Mechanical rules — rendering correctness

### Wiki-links inside tables: escape pipes

A wiki-link with an alias inside a table cell needs the pipe escaped: `[[Target\|alias]]`. Unescaped pipes inside table cells terminate the cell early and break the table's column count.

```markdown
| ✓ Correct | [[CAB PRD\|PRD]] |
| ✗ Broken  | [[FCT PRD|PRD]] |
```

### Tables: blank line before and after

A markdown table requires a blank line immediately before its header row and a blank line immediately after its last row. Obsidian's renderer silently produces broken or merged tables without this spacing.

### Fenced code blocks: no markdown inside

Wiki-links, headings, dispatch tables, named-list em-dashes inside ``` ``` ``` blocks **do not render** — they appear as literal text. If you need to *quote* a wiki-link form to show its syntax (e.g., teaching the wiki-link discipline), use single backticks: `` `[[Target|alias]]` ``. If you need to *use* a wiki-link (the reader should be able to click it), put it outside the fence as ordinary markdown.

**Smell test:** if a fenced block contains `[[`, ask whether the reader needs to click that link. If yes → move it outside the fence. If no (it's example syntax) → fine, but verify it renders the way you intended.

### Heading spacing: blank line above each heading

Every heading (`#`, `##`, etc.) has a blank line above it (except the first H1 of a doc). Many renderers tolerate omitting it; Obsidian sometimes silently merges the previous paragraph into the heading.

### Em-dash: `—` (U+2014), not `--`

Named lists and prose use the proper em-dash character `—`. Double-hyphen `--` doesn't auto-convert in Obsidian reading view. (Authorship caveat: when output is for external use where AI-tells matter, drop em-dashes; that's a separate authorship rule per the per-doc preference — see your memory.)

### Dataview inline fields: `key:: value` on its own line, no `::` in the value

A Dataview inline field is `key:: <value>`. The value is the rest of the line and must not contain `::` tokens — those collide with the parser. Keep field values plain prose; if you need to mention `description::` or `include::` in body content, do it in regular markdown paragraphs *below* the field line, not inside the value.

### Body-only convention: no YAML frontmatter where avoidable

Vault-wide preference: docs are body-only with `description::` inline as the second non-blank line, not YAML frontmatter. Frontmatter is invisible in Obsidian read view and drifts silently. Exception: skill SKILL.md files use frontmatter because Claude Code reads it; that's the only legitimate use case.


## Authoring rules — always-apply quality

### References to documents / files: wiki-links, never bare backticks

When a markdown doc *refers to another document, file, or anchor that lives in the vault*, the reference MUST be a wiki-link. Bare backticks like `` `MUX PRD.md` `` are forbidden for references — backticks are reserved for **code identifiers** (function names, file paths in source code, CLI flags, configuration keys), not for vault-internal references.

```markdown
✓ Read [[FCT PRD]] for the canonical recipe.
✓ The state script lives at `~/.claude/skills/workflow/scripts/state`.   ← path to a source file, not a vault doc

✗ Read `CAB PRD.md` for the canonical recipe.                            ← reference to a vault doc; needs wiki-link
✗ The [[state]] script lives at `~/.claude/skills/workflow/scripts/state`. ← over-linking; "state" is not a vault doc here
```

**Why:** wiki-links resolve to actual files (the reader can click), survive doc renames (Obsidian updates links on rename), and participate in the vault's link graph. Bare backticks for vault references are unclickable, don't survive renames, and silently rot. Conversely, wiki-linking code identifiers (file paths in source repos, CLI commands, config keys) creates fake links and pollutes the graph.

**Decision rule:** if a fresh reader could open the referenced thing in Obsidian, it's a wiki-link. If they'd open it in their editor / shell / source tree, it's backticks.

### Wiki-link forms

The standard forms, in order of complexity:

```markdown
[[Name]]                       ← link to doc named "Name"; display text = "Name"
[[Name|alias]]                 ← link to "Name", display "alias"
[[Name#Section]]               ← link to "Name" doc § Section
[[Name#Section|alias]]         ← link to "Name" § Section, display "alias"
[[Name#^block-id|alias]]       ← link to a specific block (paragraph or H6+ with ^block-id)
```

Inside tables, escape the pipe: `[[Name\|alias]]` (per § Mechanical rules above).

### Named-list format when content is naming-natured

A list whose items are *named* (each entry has a recognizable handle / category / concept name) follows the named-list discipline: bolded handle (2-3 words), em-dash, single-line description.

```markdown
- **Drive cluster** — the post-design phase: /mint, /crank, /land, /finalize.
- **Design cluster** — PRD → UX → API → Architecture → Testing → Roadmap.
```

This applies anywhere content is "a list of things with names" — dispatch tables in cells, TLDRs, summary lists. *Not* required for unstructured lists ("first do X, then Y").

### The `RULE` and `RULESET` sentinels for rule blocks

When a markdown doc declares rules (anywhere — embedded in a facet, in a project's Design folder, in a discussion doc):

- A single rule is a markdown heading whose first content is `RULE R-<slug>-<NN>[ — <title>[ (<tier>)]]`. Any H-level works. Greppable: `^#+\s+RULE\s+R-`.
- A bundle of rules opens with `# RULESET R-<slug>` as the H1 of the file (or a `# RULESET R-<slug>` second-H1 inside a facet that embeds the set).

See [[FCT Ruleset]] for the full format.

### Don't restate facet-level rules in per-anchor doc bodies

If a rule is universal (applies to every Log, every PRD, every Testing doc), it lives in the facet (`[[FCT Log]]`, `[[FCT PRD]]`, `[[FCT Testing]]`) and is enforced by the embedded R-set. Per-anchor docs (`Disk Log.md`, `MUX PRD.md`) should NOT restate those rules in their bodies or Briefs — the facet is the source of truth; restating it drifts. (The Brief discipline catches this for per-doc operational content; the facet-level rules are categorically excluded from Briefs.)


## What's NOT in this discipline (boundaries)

- **Layered information presentation** — preface zone, dispatch table patterns (Linear / Matrix / Grouped / List / Compact), TLDR format, figure placement, three levels of progressive disclosure. → [[DSC progressive-disclosure]].
- **User-actionable surface format** — Q-numbering, recommendation strength, à la carte items, resolution-acceptance phrases. → [[DSC ask-format]].
- **Workflow state vocabulary** — `[Ready]` / `[Active]` / `[Verify]` / `[Done]` etc. → [[workflow]].
- **Anchor-specific operational notes** — per-doc operational content that's not facet-rule-restatement. → the Brief discipline (per-doc `Brief.md` sidecars and embedded `# BRIEF` second-H1s).
- **Utility verbs** for generating or rewriting markdown — `/md toc` regen, `/md file-tree` format, `/md dispatch-table` build, `/md cards`, `/md track-changes`. → [[md]] skill.


## Audit

`/audit markdown` (future) would flag the rules captured in `R-markdown` below — wiki-link pipe-escapes in tables, fence-code wiki-link smells, bare-backtick vault references, named-list format violations, RULE-sentinel format compliance, etc.


## See also

- [[md]] — the utility-verb skill (sibling, not parent / child); `/md toc`, `/md file-tree`, `/md dispatch-table`, `/md cards`, `/md track-changes`.
- [[DSC progressive-disclosure]] — sibling discipline; doc-structure rules.
- [[DSC ask-format]] — sibling discipline; user-actionable surface format.
- [[FCT Ruleset]] — meta-spec for the RULE / RULESET sentinel format.
- [[Atlas]] / [[ATL Slugs]] — vault-wide router that wiki-link conventions ultimately serve.


# RULESET R-markdown
include::
where:: file:*.md
description:: Mechanical + authoring rules for every markdown document; cited by every facet and skill that produces markdown.

Embedded ruleset for the markdown discipline. Adoption is implicit — every markdown doc in the vault is subject to these rules, no explicit `include::` needed in `{NAME} Decisions.md`. (The catalog still lists R-markdown as a child of R-facet umbrella for completeness.)

### RULE R-markdown-01 — Escape pipes inside wiki-links inside tables (checked)
check:: md_table_pipe_escape
fix:: md_table_pipe_escape

A wiki-link inside a markdown table cell uses `\|` to escape the alias pipe: `[[Target\|alias]]`. Unescaped `|` terminates the cell early.

**Check pattern:** parse markdown tables; for each cell, find `[[…|…]]` patterns; assert the `|` is escaped as `\|`.

**Why:** the table breaks visibly — column counts go wrong, content disappears.

### RULE R-markdown-02 — Tables have blank line before and after (checked)
check:: md_table_blank_lines
fix:: md_table_blank_lines

A markdown table is preceded and followed by a blank line.

**Check pattern:** for each `^|.*|$` line that starts a table, assert the previous non-blank line is at least 2 lines back (i.e., a blank line intervenes). Symmetric for the last row.

**Why:** Obsidian sometimes silently merges tables into surrounding paragraphs without the spacing.

### RULE R-markdown-03 — No wiki-links or headings inside fenced code blocks (sampled)

Fenced code blocks (``` ``` ```) should not contain renderable markdown elements (`[[wiki-links]]`, `#` headings, `|` table rows) that the reader expects to click or navigate. If quoting wiki-link syntax for illustration, use single backticks: `` `[[Target|alias]]` ``.

**Check pattern:** for each fenced code block, grep for `[[`, `^#+\s+`, or `^|.*|$` rows; flag for review (heuristic — some uses are intentional).

**Why:** they don't render; the reader sees literal `[[Target|alias]]` and can't click. A link-shaped string with no link is worse than no string at all.

### RULE R-markdown-04 — References to vault documents use wiki-links, not backticks (sampled)

If a reference points to a markdown doc, anchor, or vault-internal page, it is a `[[wiki-link]]`. Backticks are reserved for code identifiers (source file paths, function names, CLI flags, config keys).

**Check pattern:** grep for backtick-wrapped strings matching common doc-name shapes (`PRD\.md`, ` Log\.md`, `[A-Z]{2,5} `); flag for review.

**Why:** wiki-links resolve, survive renames, and participate in the link graph; backtick references rot silently. Conversely, wiki-linking code identifiers creates fake links and pollutes the graph.

### RULE R-markdown-05 — Em-dash is `—` (U+2014), not `--` (checked)
check:: md_em_dash
fix:: md_em_dash

Named lists and prose use the em-dash character. Double-hyphen `--` doesn't auto-convert in Obsidian.

**Check pattern:** for named-list bullets, expect the descriptor + ` — ` + body shape; flag bullets matching `^- \*\*[^*]+\*\*: ` or `^- \*\*[^*]+\*\*\s+--\s+`.

**Why:** consistency; the em-dash signals a named-list bullet visually.

### RULE R-markdown-06 — Dataview inline fields have no `::` in the value (checked)
check:: regex_absent ^[a-z][a-z0-9_-]*::[^\n]*::[^\n]*$

For any `^<key>:: <value>` line, the value contains no `::` tokens (which would collide with the Dataview parser).

**Check pattern:** for each `^[a-z][a-z0-9_-]*::` line, assert the rest of the line has no `::`.

**Why:** Dataview misparses on collision; the field value gets truncated or the next field gets eaten.

### RULE R-markdown-07 — Body-only preferred for vault docs (stated)

Vault docs are body-only with `description::` inline as the second non-blank line. YAML frontmatter is reserved for skill SKILL.md files (where Claude Code reads it).

**Check pattern:** for each vault doc, first non-blank line starts with `#`; no `---` block precedes. Skill SKILL.md files exempt.

**Why:** frontmatter is invisible in Obsidian read view; the description belongs visible.

### RULE R-markdown-08 — Wiki-link form for code identifiers is forbidden (sampled)

Source file paths, function names, CLI commands, config keys go in backticks, not wiki-links. The vault link graph is for vault-internal navigation.

**Check pattern:** flag `[[...]]` patterns whose name matches code-identifier shapes (`.*\.(py|rs|js|ts|sh)$`, leading `/`, contains `::` or `()`).

**Why:** fake wiki-links pollute the link graph and unresolved-link reports; backticks are the right vehicle for code references.

### RULE R-markdown-09 — Named list format for naming-natured content (stated)

A list whose items are *named things* uses the bolded-handle + em-dash + single-line description format. Unstructured procedural lists are exempt.

**Check pattern:** heuristic — for bullets matching `^- [A-Z]`, suggest named-list form unless the bullet reads as a step.

**Why:** named lists are visually scannable; the reader's eye anchors on the bolded handle.

### RULE R-markdown-10 — Per-anchor docs don't restate facet-level rules (stated)

A per-anchor doc (e.g., `Disk Log.md`, `MUX PRD.md`) does NOT include a section restating rules that live in the facet spec (e.g., the Log format rules belong in [[FCT Log]], not in every Log file's body or Brief).

**Check pattern:** for any per-anchor doc, grep for `# BRIEF`, `## Convention`, `## Rules`, `## Format`; flag for review if the body contains general format prescriptions.

**Why:** restated rules drift when the facet evolves; the facet is the single source of truth.

### RULE R-markdown-11 — Never put markdown inside a fenced code block (checked)
check:: md_fence_no_markdown

A fenced code block (triple backticks) must NEVER contain markdown intended to be read *as* markdown — `[[wiki-links]]` go inert, and headings, tables, and emphasis do not render. To show what a markdown document looks like, write it as **live markdown** — its own frontmatter and `# H1`, with any commentary placed BEFORE the example's frontmatter so it can't bleed into the example — or link to a real worked instance. Fenced blocks are reserved for literal **non-markdown** content: shell, code, JSON, `key: value` data files, file trees.

**Language-tagged code fences are exempt.** The rule targets fences that are *meant to show rendered markdown* — those are unlabeled ` ``` ` fences or ` ```markdown ` / ` ```md ` fences. A fence carrying a code-language tag (` ```python `, ` ```bash `, ` ```json `, ` ```yaml `, …) is literal source and is **not checked**: its body legitimately contains `[[` (e.g. a regex) or `#` (a comment), and flagging those is a false positive.

**Check pattern:** scan fenced blocks whose info-string is empty or `markdown`/`md`; flag any whose body contains `[[wiki-links]]`, `#`/`##` headings, or pipe-tables that are meant to render. Skip fences with any other language tag (literal code).

**Why:** the whole point of an example is to show the *rendered* form — a fence defeats that (links aren't clickable, structure doesn't render). The user has corrected this repeatedly; it is an absolute rule.

### RULE R-markdown-12 — Figures are embedded images; never mermaid, never text-based diagrams (checked)

A figure is an **embedded image** — an Excalidraw / matplotlib / D2 artifact exported to SVG/PNG and embedded with a page-fill width hint (`![[name.svg|2400]]` — never bare, which renders tiny; see [[FCT Architecture]] § Architecture diagram requirements), with its editable source kept alongside (same basename). **Never use `mermaid` code blocks, and never draw text-based / ASCII figures** (boxes-and-arrows built from characters, pipe-and-dash "diagrams"). This is absolute.

**Check pattern:** flag any ```` ```mermaid ```` fenced block; flag fenced blocks whose body is box-drawing / ASCII-diagram content (`┌ ─ │ └ ├ → ╮` runs, or `+---+` / character-art used as a diagram rather than a literal data table or file tree).

**Why:** a figure must be a real, editable, consistently-rendering artifact; mermaid and ASCII are neither — they render inconsistently across surfaces, can't be edited as diagrams, and read as broken. Diagrams use the Excalidraw-source-alongside-export convention.

### RULE R-markdown-13 — No stray `<tag>`-like angle brackets (checked)
check:: md_angle_brackets_html_or_spaced

An angle bracket is allowed when it is **(a)** inside an inline code span or fenced code block, **(b)** part of a valid HTML construct — an HTML comment `<!-- … -->` or a curated inline tag (`<br>`, `<hr>`, `<ins>`, `<del>`, `<sub>`, `<sup>`, `<kbd>`, `<mark>`, `<u>`, `<wbr>`, `<s>`, `<q>`, `<abbr>`, `<cite>`), or **(c)** a comparison/operator with whitespace on the inner side (`a < b`). What it forbids is a stray **`<identifier>`** — a `<` glued to a tag-name character — which the viewer parses as an unknown HTML element and silently eats the text up to the next `>`. LLMs emit these constantly for placeholders and generics (`<Name>`, `List<int>`). `.html` / `.htm` files are real HTML and are skipped. The right fix needs judgment (backtick, escape `&lt;`/`&gt;`, add spaces, or restructure), so this rule **flags** — it carries no `fix::`.

**Check pattern:** mask code spans / fences, HTML comments, the curated inline tags, and leading blockquote / callout `>`; then flag any surviving `<` immediately followed by `[A-Za-z!/]` (a tag-like opener).

**Why:** a `<word>` construct is read as an HTML tag and dropped, eating the text up to the next `>` — the actual breakage. Valid HTML and whitespace-surrounded comparisons render fine, so only the glued tag-like form is dangerous; flag so the agent fixes with intent.

### RULE R-markdown-14 — No trailing whitespace (checked)
check:: md_trailing_ws
fix:: md_trailing_ws

A line must not end in spaces or tabs. Pure normalization — auto-fixed, since stripping trailing whitespace never removes content.

**Check pattern:** any line where `line != line.rstrip()`.

**Why:** trailing whitespace is invisible noise that pollutes diffs and can create accidental hard-breaks; safe to strip mechanically.

# BRIEF
- **Markdown is a discipline, not a document facet — settled, do not re-litigate.** A `FCT Markdown` facet was created and reverted 2026-06-14. The discriminator: a *document facet* is a pointable structural part of a doc (Brief, Discussion, Ruleset, the ToC table) or the umbrella skeleton ([[FCT Doc Structure]]); markdown is uniform text-correctness applied to *every line, every time*, which is the definition of a discipline. Specializing into structure → facet; staying text-rules-everywhere → discipline. Markdown never becomes structural, so it lives here only.
- **Single source of truth** — the rules live embedded in this file's `# RULESET R-markdown`; [[R-markdown]] is the catalog stub, [[md]] is the utility skill. Don't duplicate the rules into a facet or per-anchor doc (R-markdown-10 forbids the latter).
