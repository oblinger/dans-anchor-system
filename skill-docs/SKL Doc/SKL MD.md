---
description: How to format markdown — file trees, TOC tables, dispatch tables, cards, named lists
---

# SKL MD Guide (Skill: [[md/SKILL]])

The MD skill defines standard markdown formatting conventions used across all documents in the system. It covers structural patterns (file trees, tables of contents, dispatch tables) and inline conventions (named lists, heading spacing, date formats).

These conventions matter because the agent generates and edits markdown constantly. Consistent formatting makes documents machine-parseable and visually predictable. When you ask the agent to create a TOC, draw a file tree, or format a dispatch table, it follows these specs exactly.

The skill also includes a Python script (`md-toc.py`) that auto-generates TOC tables from document headings, which is critical for anchor pages and large documents.

## Commands

| Command | Description |
|---------|-------------|
| `/md file-tree` | File tree diagram format — 4 forms with box-drawing characters |
| `/md toc` | Table of contents format — 3 forms + auto-generation |
| `/md dispatch-table` | Dense link table + dispatch pages for navigation hubs |
| `/md cards` | Cards format — cheat sheets, summary cards, detail cards |
| `/md track-changes` | Inline diff HTML for tracking markdown edits |

## Key Concepts

- **Heading spacing** — H1/H2 get three blank lines before and one after. H3 and below get no blank line after. Lists follow headings with no blank line between
- **Named lists** — Bullet items with a bold ALL CAPS name, em-dash, and description. Used for defining terms and listing standard entries
- **File trees** — Use box-drawing characters (not ASCII). Four forms available depending on detail level
- **TOC generation** — Run `uv run ~/.claude/skills/md/md-toc.py <file.md>` to regenerate. Use `--dry-run` to preview
- **Dispatch tables** — Dense tables linking to sub-files, used as navigation hubs in anchor pages and skill files
- **Table formatting** — Always blank lines before and after tables. Escape pipes in cell content
- **Date format** — Always `YYYY-MM-DD` (ISO 8601). Dated sections use reverse chronological order
