# CAB Markdown Formatting

Standard formatting conventions used throughout all anchor documents. Also available as the `/md` Claude Code skill — see [[md/SKILL]].


## Vertical Spacing
Headings should visually associate with the content that follows, not the content before:
- **H1, H2** — Three blank lines before, one blank line after
- **H3 AND BELOW** — No blank line after the heading
- **LISTS** — No blank line between a heading/text and the list that follows it

Example of correct spacing:
```markdown
Some preceding content here.



## Section Title

First paragraph of this section.

### Subsection
- List item 1
- List item 2

More text here.
```


## Named List
A bullet list where each item has a bold ALL CAPS name followed by a double dash and description:
- **NAME** — Description of what this item is or does

Used for: defining terms, listing standard entries, describing fields.


## Dated Sections
Example of a file with **dated sections** (used by Inbox, Features, Backlog):
```
## 2026-01-12 — Topic or Feature Name

Content for this entry...

## 2026-01-10 — Earlier Topic

Earlier content...
```
Sections are listed in reverse chronological order (newest first).


## Date Format
Standard date format is `YYYY-MM-DD` (ISO 8601):
- **IN HEADINGS** — Use as prefix: `## 2026-01-12 — Topic Name`
- **IN FILENAMES** — Use as prefix for archived items: `2026-01-12 Old Project Name`
- **IN TEXT** — Use consistently for all dates

This format ensures:
- Chronological sorting when viewing alphabetically
- Unambiguous interpretation (no month/day confusion)


## Python Comments in Code Blocks
Obsidian's folding engine has a persistent bug where `#` characters at the start of lines inside code blocks are treated as markdown headers. This causes heading folds to break at Python comment lines.

**Workaround** — Use the Unicode fullwidth number sign `＃` (U+FF03) in place of `#` for Python comments inside code blocks:
```python
def activate(entity):
    ＃ Check energy threshold before activation
    if entity.energy > MIN_ENERGY:
        entity.state = "active"
```
This only applies to comments in **code blocks within Obsidian markdown**. Actual source code files are unaffected.


## File Tree Diagrams

File trees use Unicode box-drawing characters with four forms described in [[CAB File Tree Format]]. The key rules:

- **Box-drawing characters** — `├` (branch), `└` (last branch), `│` (continuation), `─` (connector)
- **Indentation** — 3 figure spaces (U+2007) per nesting level in Forms 1–3. Regular spaces in Form 4 (whole-page monospace).
- **Links outside backticks** — Wiki-links go after the backtick span (Forms 1–2) or in the Name column (Form 3). In Form 4 (monospace page), links work inline.
- **Descriptions on the right** — Each tree entry can have a brief purpose description aligned on the right side.

### Forms
- **Form 1: Large Inline** — HTML `<span>` with larger font for the tree portion
- **Form 2: Inline** — Backtick spans at normal size
- **Form 3: Table** — Markdown table with Structure, Name, Description columns
- **Form 4: Whole-Page Monospace** — `cssclasses: monospace` in frontmatter; no backticks needed, wiki-links work inline. See [[CAB All Files]] for an example.

### Figure Spaces
Figure spaces (U+2007) do not collapse in markdown renderers like regular spaces do. Insert programmatically:
```python
fig = '\u2007'  # figure space
line = f'│{fig}{fig}{fig}├── filename'
```

Claude Code's Edit tool cannot distinguish figure spaces from regular spaces. Use Python via Bash for edits to lines containing figure spaces.


## Table of Contents

Tables of contents use numbered, linked entries with indentation. Three forms described in [[CAB TOC Format]]. The key rules:

- **Top-level at left margin** — H2-level entries are bold, no indentation
- **Sub-entries indented** — 3 figure spaces per level
- **Every entry is a link** — Wiki-links (`[[#heading]]`) or markdown anchor links
- **Descriptions optional** — Brief phrase after an em-dash

### cab-toc Script
The `cab-toc.py` script auto-generates a TOC from H2/H3 headings:
```bash
cab-toc.py <file.md>           # Replace existing TOC table in-place
cab-toc.py <file.md> --dry-run # Print TOC to stdout
```

The script locates the first table whose header contains "Table of Contents" and replaces it. Extra columns (descriptions, notes) are preserved by matching on heading title. If no TOC table exists, it prints to stdout.

The TOC uses Form 3 (Table) with wiki-links: `[[#heading text]]`.


# BRIEF

- **This file is the formatting spec** — the canonical reference for vertical spacing, named lists, dated sections, date format, Python-comment workaround, file-tree forms, and TOC forms across all anchor documents. Edit here when a vault-wide formatting convention changes; cite from other facets via wiki-link rather than restating.
- **Inclusion test** — a rule belongs here only if it applies to *plain markdown authoring* across many anchor documents (spacing, link shape, table conventions, glyph choices). Anchor-specific or facet-specific shape rules (e.g. "every Backlog has horizons", "every Rules file is a RULESET") belong in the relevant `CAB <Facet>.md`, not here.
- **NOT for** — rendering quirks of one tool, one-off authoring tips, project-wide policy (`CLAUDE.md`), or operational rules for editing one specific source file (those are sidecar Briefs per [[FCT Brief]]).
- **Load-bearing details** — figure spaces (U+2007) in file trees and TOCs are invisible but mechanical: the Edit tool cannot match them, so edits to those lines must go through Python via Bash. The fullwidth `＃` (U+FF03) workaround for Python comments in fenced code blocks is similarly load-bearing — don't "normalize" it back to `#`.
- **Linking convention** — sub-form details (File Tree Forms 1–4, TOC forms) live in dedicated files ([[CAB File Tree Format]], [[CAB TOC Format]]); this page summarizes the key rules and links out. Keep that split — don't inline the full sub-specs here.
- **Companion skill** — the `/md` skill ([[md/SKILL]]) is the executable counterpart. When a new utility verb lands in `/md` (e.g. a new TOC generator flag), update the corresponding section here so the spec and the tool agree.
- **Don't pile** unrelated content here — when in doubt, ask whether the rule is about *markdown text itself* (belongs here) versus *what goes where in a doc* (belongs in [[progressive-disclosure]]) versus *a specific facet's shape* (belongs in that facet's CAB file).
