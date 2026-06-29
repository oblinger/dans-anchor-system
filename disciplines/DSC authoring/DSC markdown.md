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

### Python comments in fenced code blocks: fullwidth `＃` (U+FF03)

Obsidian's folding engine treats a `#` at the **start of a line inside a fenced code block** as a markdown heading, which breaks heading folds at every Python comment. Workaround: use the fullwidth number sign `＃` (U+FF03) for Python comments shown inside Obsidian code blocks:

```python
def activate(entity):
    ＃ check energy threshold before activation
    if entity.energy > MIN_ENERGY:
        entity.state = "active"
```

This applies **only** to comments in fenced code blocks within Obsidian markdown — actual source `.py` files use a normal `#`. Don't "normalize" the `＃` back to `#`.

### Figure spaces (U+2007): non-collapsing indentation

Figure spaces (U+2007) do not collapse the way regular spaces do in markdown renderers, so they indent file-tree diagrams and TOC tables (the [[md-file-tree]] / [[md-toc]] forms). Two load-bearing consequences:

- **The Edit tool cannot match figure spaces** — any edit to a line containing U+2007 must go through Python via Bash (or the `/md` regeneration scripts), never a literal Edit match. (This is why anchor TOC rows are never hand-edited.)
- Insert them programmatically: `fig = '\u2007'` (Python escape for the code point).


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
where:: `**/*.md`
description:: Mechanical + authoring rules for every markdown document; cited by every facet and skill that produces markdown.

Embedded ruleset for the markdown discipline. Adoption is implicit — every markdown doc in the vault is subject to these rules, no explicit include:: needed in {NAME} Decisions.md. (The catalog still lists R-markdown as a child of the R-facet umbrella for completeness.) The rules are written in the [[Warden Semantics|Warden]] language: a `description::` of what the rule means, a `where::` / `when::` / `if::` condition, and a body that is either a bare-prose **tell** or backticked Python. Checks reusable across rules call shared `md.*` helpers (the markdown-checker library these rules ship with).

### RULE R-markdown-01 — Escape pipes inside wiki-links inside tables
description:: A wiki-link in a table cell escapes its alias pipe — [[Target\|alias]] — so the cell doesn't terminate early.
when:: write:markdown
if:: `md.unescaped_table_pipe(file)`
A wiki-link in a table cell has an unescaped `|` — write it `\|` so the cell keeps its column count.

**Why:** the table breaks visibly — column counts go wrong, content disappears.

### RULE R-markdown-02 — Tables have blank line before and after
description:: A markdown table is preceded and followed by a blank line so Obsidian renders it.
when:: write:markdown
if:: `md.table_missing_blank_line(file)`
A table is touching the line above or below it — add a blank line on each side so Obsidian doesn't merge it into the surrounding paragraph.

### RULE R-markdown-03 — No wiki-links or headings inside fenced code blocks
description:: A fenced block holding renderable markdown ([[links]], headings, tables) the reader expects to click is a smell.
if:: `md.fence_holds_renderable_markdown(file)`
A fenced code block contains a `[[wiki-link]]`, heading, or table the reader would expect to click or navigate — they render as inert literal text. If you're quoting syntax for illustration, use single backticks; if the reader should click it, move it outside the fence.

**Why:** a link-shaped string with no link is worse than no string at all.

### RULE R-markdown-04 — References to vault documents use wiki-links, not backticks
description:: A reference to a vault doc / anchor / page is a [[wiki-link]]; backticks are reserved for code identifiers.
if:: `re.search(r'`[^`]+\.md`', file.text) or re.search(r'`[A-Z]{2,5} [A-Z][a-z]', file.text)`
A backtick-wrapped string looks like a reference to a vault document. If a reader could open it in Obsidian, make it a [[wiki-link]] — backticks are for code identifiers (source paths, function names, CLI flags, config keys), which rot silently when used for vault references.

### RULE R-markdown-05 — Em-dash is `—` (U+2014), not `--`
description:: Named lists and prose use the em-dash character; double-hyphen does not auto-convert in Obsidian.
when:: write:markdown
if:: `re.search(r'^- \*\*[^*]+\*\*\s+--\s', file.text, re.M)`
A named-list bullet uses `--` where it wants an em-dash — replace it with ` — ` so the bullet reads right in Obsidian's reading view.

### RULE R-markdown-06 — Dataview inline fields have no `::` in the value
description:: For any key:: value line, the value carries no further :: token, which would collide with the Dataview parser.
when:: write:markdown
if:: `re.search(r'^[a-z][a-z0-9_-]*::[^\n]*::', file.text, re.M)`
A `key:: value` inline field has a second `::` in its value — Dataview will misparse it (the value truncates or the next field is eaten). Move any mention of a field name into a regular paragraph below the field line.

### RULE R-markdown-07 — Body-only preferred for vault docs
description:: Vault docs are body-only with description:: inline as the second line; YAML frontmatter is reserved for SKILL.md.
if:: `file.text.startswith('---') and file.name != 'SKILL.md'`
This vault doc opens with YAML frontmatter — prefer the body-only form with a visible `description::` inline as the second non-blank line. Frontmatter is invisible in Obsidian read view and drifts silently; only SKILL.md (read by Claude Code) needs it.

### RULE R-markdown-08 — Wiki-link form for code identifiers is forbidden
description:: Source paths, function names, CLI commands, and config keys go in backticks, never wiki-links.
if:: `any(re.search(r'\.(py|rs|js|ts|sh)$|^/|\(\)', l) for l in file.links)`
A `[[wiki-link]]` names a code identifier (a source path, a function, a CLI command) — that fabricates a link and pollutes the vault graph. Put code identifiers in backticks; keep wiki-links for vault-internal navigation.

### RULE R-markdown-09 — Named list format for naming-natured content
description:: A list of named things uses the bolded-handle + em-dash + single-line-description form; procedural lists are exempt.
The lists in this doc whose items are *named things* (each has a recognizable handle or concept name) should use the named-list form — a bolded 2–3 word handle, an em-dash, then a one-line description. Plain procedural lists ("first X, then Y") are exempt. Point out any naming-natured list that isn't in this form.

### RULE R-markdown-10 — Per-anchor docs don't restate facet-level rules
description:: A per-anchor doc does not restate rules that live in a facet spec; the facet is the single source of truth.
where:: `{ANCHOR}/**/{NAME} *.md`
This per-anchor doc looks like it restates universal format rules that belong in a facet (a Log's format rules live in [[FCT Log]], a PRD's in [[FCT PRD]]) — restated rules drift when the facet evolves. Drop the restatement and rely on the facet's embedded ruleset.

### RULE R-markdown-11 — Never put markdown inside a fenced code block
description:: A fence meant to show rendered markdown ([[links]], headings, tables) defeats itself; show live markdown or link a real instance.
if:: `md.fence_shows_rendered_markdown(file)`
A fenced code block (unlabeled or `markdown`/`md`-tagged) contains markdown meant to be *read as markdown* — `[[wiki-links]]` go inert and headings, tables, and emphasis don't render. Show the example as **live markdown** (its own `# H1`, with commentary BEFORE it so it can't bleed in) or link a real worked instance. Language-tagged fences (`python`, `bash`, `json`, …) are literal source and are not flagged.

**Why:** the whole point of an example is to show the *rendered* form. The user has corrected this repeatedly; it is absolute.

### RULE R-markdown-12 — Figures are embedded images; never mermaid, never text-based diagrams
description:: A figure is an exported image embedded with a width hint; mermaid blocks and ASCII box-art are forbidden.
if:: `md.mermaid_or_ascii_diagram(file)`
This doc draws a diagram as a `mermaid` block or ASCII box-art (`┌ ─ │ └ → ╮` runs, `+---+` character art used as a figure). A figure must be a real editable artifact — an Excalidraw / D2 / matplotlib export embedded with a page-fill width hint (`![[name.svg|2400]]`), source kept alongside. Redraw it that way.

### RULE R-markdown-13 — No stray `<tag>`-like angle brackets
description:: A bare <identifier> glued to a tag-name character is parsed as an unknown HTML element and eats text up to the next >.
if:: `md.stray_angle_tag(file)`
A stray `<identifier>` (a `<` glued to a tag-name character, e.g. `<Name>` or `List<int>`) is read as an unknown HTML element and silently eats the text up to the next `>`. Fix it with intent — backtick it, escape as `&lt;`/`&gt;`, add spaces (`a < b`), or restructure. Inline code, real HTML constructs, and whitespace-surrounded comparisons are fine; `.html` files are skipped.

### RULE R-markdown-14 — No trailing whitespace
description:: A line must not end in spaces or tabs; stripping trailing whitespace never removes content, so it is safe to normalize.
when:: write:markdown
if:: `any(l != l.rstrip() for l in file.lines)`
A line ends in trailing whitespace — invisible noise that pollutes diffs and can create accidental hard-breaks. Strip it.

# BRIEF
*(Maintainer note — editing the markdown discipline.)*

- **Markdown is a discipline, not a document facet — settled, do not re-litigate.** A `FCT Markdown` facet was created and reverted 2026-06-14. Discriminator: a *document facet* is a pointable structural part of a doc; markdown is uniform text-correctness on *every line, every time* — the definition of a discipline. It never becomes structural, so it lives here only.
- **Single source of truth:** the rules are embedded in this file's `# RULESET R-markdown`; [[R-markdown]] is the catalog stub, [[md]] the utility skill. Don't duplicate them into a facet or per-anchor doc (R-markdown-10 forbids the latter).
