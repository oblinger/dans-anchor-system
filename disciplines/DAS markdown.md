---
name: markdown
description: Discipline. The "every time you write markdown" rules — both mechanical (rendering correctness — table escapes, fence rules, spacing) and authoring (always-apply quality — wiki-links not bare backticks, definition lists, RULE/RULESET sentinels). Cited by every DAS facet, every design sub-skill, every authoring skill. Sibling discipline to [[DAS progressive-disclosure]] (which owns *what goes where in a doc*); markdown owns *how the markdown text itself is written*. Skill counterpart is [[md]] which owns user-invokable utility verbs (/md toc, /md file-tree, etc.).
user_invocable: false
---

# Markdown Discipline

The discipline for **how markdown TEXT is written** — applied to every markdown document in the vault, every time. Sibling to [[DAS progressive-disclosure]] (*what goes where in a doc*) and to the [[md]] skill (*utility verbs that produce or maintain markdown artifacts*).

Two flavors of rule live here, and both apply every time:

- **Mechanical rules** — rendering correctness. Skip these → the doc renders wrong. Examples: escape pipes inside wiki-links inside tables; blank line before / after a table; no wiki-links inside fenced code blocks (they don't render).
- **Authoring rules** — always-apply quality. Skip these → the doc renders but is wrong. Examples: references to other docs MUST be wiki-links not bare backticks; definition-list format when content is naming-natured; the `RULE` / `RULESET` sentinel pattern for rule blocks.

The boundary against [[DAS progressive-disclosure]]: this discipline cares about the markdown *text*. Progressive-disclosure cares about the *doc structure* (preface zone, dispatch table patterns, figure placement, TLDR shape). If the question is "how do I write this line of markdown right," it's here; if "where in the doc does this section go," that's progressive-disclosure.


## Progressive disclosure — the opening every non-trivial page uses

The one structural rule an author reaches for constantly: **any non-trivial page** (one with substructure — at least one page beneath it — or more than ~2 pages of its own content) opens in a fixed order —

**[breadcrumb] → H1 → one-line summary → [figure] → [table] → [Overview] → body**

— the breadcrumb appears only on a non-anchor page with no dispatch table (an anchor's breadcrumb lives in its dispatch masthead), and there is **no blank line** between breadcrumb, H1, and summary. This is *doc structure*, so its normative home is the sibling disciplines, not here: see [[DAS Doc Structure]] (the document skeleton + `R-doc-structure` ruleset) and [[DAS progressive-disclosure]] (the layered-presentation discipline). The pointer is kept here because the opening format is the first thing an author needs when writing any page.


## Mechanical rules — rendering correctness

### Wiki-links inside tables: escape pipes

A wiki-link with an alias inside a table cell needs the pipe escaped: `[[Target\|alias]]`. Unescaped pipes inside table cells terminate the cell early and break the table's column count.

```markdown
| ✓ Correct | [[DAS PRD\|PRD]] |
| ✗ Broken  | [[DAS PRD|PRD]] |
```

### Tables: blank line before and after

A markdown table requires a blank line immediately before its header row and a blank line immediately after its last row. Obsidian's renderer silently produces broken or merged tables without this spacing.

### Fenced code blocks: no markdown inside

Wiki-links, headings, dispatch tables, definition-list em-dashes inside ``` ``` ``` blocks **do not render** — they appear as literal text. If you need to *quote* a wiki-link form to show its syntax (e.g., teaching the wiki-link discipline), use single backticks: `` `[[Target|alias]]` ``. If you need to *use* a wiki-link (the reader should be able to click it), put it outside the fence as ordinary markdown.

**Smell test:** if a fenced block contains `[[`, ask whether the reader needs to click that link. If yes → move it outside the fence. If no (it's example syntax) → fine, but verify it renders the way you intended.

### Heading spacing: blank line above each heading

Every heading (`#`, `##`, etc.) has a blank line above it (except the first H1 of a doc). Many renderers tolerate omitting it; Obsidian sometimes silently merges the previous paragraph into the heading.

### Em-dash: `—` (U+2014), not `--`

Definition lists and prose use the proper em-dash character `—`. Double-hyphen `--` doesn't auto-convert in Obsidian reading view. (Authorship caveat: when output is for external use where AI-tells matter, drop em-dashes; that's a separate authorship rule per the per-doc preference — see your memory.)

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
✓ Read [[DAS PRD]] for the canonical recipe.
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

### Definition-list format when content is naming-natured

A list whose items are *named* (each entry has a recognizable handle / category / concept name) follows the definition-list discipline: bolded handle (2-3 words), em-dash, single-line description.

```markdown
- **Drive cluster** — the post-design phase: /mint, /crank, /land, /finalize.
- **Design cluster** — PRD → UX → API → Architecture → Testing → Roadmap.
```

This applies anywhere content is "a list of things with names" — dispatch tables in cells, TLDRs, summary lists. *Not* required for unstructured lists ("first do X, then Y").

### The `RULE` and `RULESET` sentinels for rule blocks

When a markdown doc declares rules (anywhere — embedded in a facet, in a project's Design folder, in a discussion doc):

- A single rule is a markdown heading whose first content is `RULE R-<slug>-<NN>[ — <title>[ (<tier>)]]`. Any H-level works. Greppable: `^#+\s+RULE\s+R-`.
- A bundle of rules opens with `# RULESET R-<slug>` as the H1 of the file (or a `# RULESET R-<slug>` second-H1 inside a facet that embeds the set).

See [[DAS Ruleset]] for the full format.

### Don't restate facet-level rules in per-anchor doc bodies

If a rule is universal (applies to every Log, every PRD, every Testing doc), it lives in the facet (`[[DAS Log]]`, `[[DAS PRD]]`, `[[DAS Testing]]`) and is enforced by the embedded R-set. Per-anchor docs (`Disk Log.md`, `MUX PRD.md`) should NOT restate those rules in their bodies or Briefs — the facet is the source of truth; restating it drifts. (The Brief discipline catches this for per-doc operational content; the facet-level rules are categorically excluded from Briefs.)


## What's NOT in this discipline (boundaries)

- **Layered information presentation** — preface zone, dispatch table patterns (Linear / Matrix / Grouped / List / Compact), TLDR format, figure placement, three levels of progressive disclosure. → [[DAS progressive-disclosure]].
- **User-actionable surface format** — Q-numbering, recommendation strength, à la carte items, resolution-acceptance phrases. → [[DAS ask-format]].
- **Workflow state vocabulary** — `[Ready]` / `[Active]` / `[Verify]` / `[Done]` etc. → [[workflow]].
- **Anchor-specific operational notes** — per-doc operational content that's not facet-rule-restatement. → the Brief discipline (per-doc `Brief.md` sidecars and embedded `# BRIEF` second-H1s).
- **Utility verbs** for generating or rewriting markdown — `/md toc` regen, `/md file-tree` format, `/md dispatch-table` build, `/md cards`, `/md track-changes`. → [[md]] skill.


## Audit

`/audit markdown` (future) would flag the rules captured in `R-markdown` below — wiki-link pipe-escapes in tables, fence-code wiki-link smells, bare-backtick vault references, definition-list format violations, RULE-sentinel format compliance, etc.


## See also

- [[md]] — the utility-verb skill (sibling, not parent / child); `/md toc`, `/md file-tree`, `/md dispatch-table`, `/md cards`, `/md track-changes`.
- [[DAS progressive-disclosure]] — sibling discipline; doc-structure rules.
- [[DAS ask-format]] — sibling discipline; user-actionable surface format.
- [[DAS Ruleset]] — meta-spec for the RULE / RULESET sentinel format.
- [[Atlas]] / [[ATL Slugs]] — vault-wide router that wiki-link conventions ultimately serve.


# BRIEF
*(Maintainer note — editing the markdown discipline.)*

- **Markdown is a discipline, not a document facet — settled, do not re-litigate.** A `FCT Markdown` facet was created and reverted 2026-06-14. Discriminator: a *document facet* is a pointable structural part of a doc; markdown is uniform text-correctness on *every line, every time* — the definition of a discipline. It never becomes structural, so it lives here only.
- **Single source of truth:** the rules are embedded in this file's `# RULESET R-markdown`; [[R-markdown]] is the catalog stub, [[md]] the utility skill. Don't duplicate them into a facet or per-anchor doc (R-markdown-10 forbids the latter).
