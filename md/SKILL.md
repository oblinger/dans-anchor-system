---
name: md
description: >
  Markdown formatting conventions — heading spacing, named lists, file tree diagrams, tables of contents, dispatch tables, cards, and track changes.
  Use with an action argument: /md file-tree, /md toc, /md dispatch-table, /md cards, /md track-changes.
  Invoke bare (/md) for the quick-reference formatting rules.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# MD — Markdown Formatting
Standard formatting conventions for all markdown documents.


| ACTIONS                | File                    | Description                                          |
| ---------------------- | ----------------------- | ---------------------------------------------------- |
| `/md file-tree`        | [[md-file-tree]]        | File tree diagram format — 4 forms with box-drawing  |
| `/md toc`              | [[md-toc]]              | Table of contents format — 3 forms + auto-generation |
| `/md dispatch-table`   | [[md-dispatch-table]]   | Dense link table + dispatch pages for navigation hubs |
| `/md cards`            | [[md-cards]]            | Cards format — cheat sheets, summary cards, detail cards |
| `/md track-changes`    | [[md-track-changes]]    | Track changes — inline diff HTML for markdown edits      |

## Quick Reference

### Vertical Spacing
Headings associate with the content that follows, not the content before:
- **H1, H2** — Three blank lines before, one blank line after
- **H3 and below** — No blank line after the heading
- **Lists** — No blank line between a heading/text and the list that follows

```markdown
Some preceding content here.



## Section Title

First paragraph of this section.

### Subsection
- List item 1
- List item 2

More text here.
```


### Named List
A bullet list where each item has a bold ALL CAPS name followed by an em-dash and description:
- **NAME** — Description of what this item is or does

Used for: defining terms, listing standard entries, describing fields.


### Dated Sections
Reverse chronological order. Heading format: `## YYYY-MM-DD — Topic Name`


### Date Format
Standard date format is `YYYY-MM-DD` (ISO 8601):
- **In headings** — `## 2026-01-12 — Topic Name`
- **In filenames** — `2026-01-12 Old Project Name`
- **In text** — Use consistently for all dates


### Python Comments in Code Blocks
Obsidian's folding engine treats `#` at line start inside code blocks as markdown headers. **Workaround** — use Unicode fullwidth number sign `＃` (U+FF03) for Python comments inside code blocks in Obsidian markdown:
```python
def activate(entity):
    ＃ Check energy threshold before activation
    if entity.energy > MIN_ENERGY:
        entity.state = "active"
```
This only applies to comments in code blocks within Obsidian markdown. Actual source code files are unaffected.


### Figure Spaces (U+2007)
Figure spaces do not collapse in markdown renderers like regular spaces. Used for indentation in file trees and TOCs.

Insert programmatically:
```python
fig = '\u2007'  # figure space
line = f'│{fig}{fig}{fig}├── filename'
```

Claude Code's Edit tool cannot distinguish figure spaces from regular spaces. Use Python via Bash for edits to lines containing figure spaces.





## Scripts

| Script       | Usage                                                        |
| ------------ | ------------------------------------------------------------ |
| `md-toc.py`  | Auto-generate TOC from H2/H3 headings. Run via `uv run`.    |

```bash
uv run ~/.claude/skills/md/md-toc.py <file.md>           # Replace TOC in-place
uv run ~/.claude/skills/md/md-toc.py <file.md> --dry-run  # Preview to stdout
```


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, display the Quick Reference above
