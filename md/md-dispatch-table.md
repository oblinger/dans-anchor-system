# Dispatch Table

A dense table of outgoing links organized by category, used as a central navigation hub. The top-left cell names the table (usually the project or system name). The left column lists categories or sections. The right column packs multiple wiki-links per row.

```markdown
| **Project Name** |                                              |
| ---------------- | -------------------------------------------- |
| Docs             | [[PRD]], [[System Design]], [[Roadmap]]      |
| Modules          | [[Core]], [[Config]], [[Agent]], [[Health]]   |
| User             | [[User Guide]], [[Examples]]                 |
| External         | [repo-name](repo-name/), [[CHANGELOG]]       |
```

**Table formatting:** Tables MUST have a blank line before them or they won't render. Escape the pipe in wiki-link aliases inside tables: `[[target\|alias]]` not `[[target|alias]]`. An unescaped `|` breaks the table column.

## Key Properties
- **Top-left cell** — bold, names the dispatch target (project, skill, system)
- **Left column** — category labels, optionally wiki-links themselves
- **Right column** — comma-separated wiki-links, packed densely
- **Rows can overflow** — use multiple rows for the same category (leave left cell empty on continuation rows)
- **Strikethrough** — `~~[[Dead Link]]~~` marks known-broken or deprecated links

## Dispatch Page

A **dispatch page** is a markdown page whose primary content is a dispatch table. Common uses:
- **Anchor pages** — the folder file for a complex anchor is often a dispatch page with 50–100+ links
- **Docs folder files** — `{NAME} Docs.md` dispatches to all planning and reference documents
- **Skill pages** — `SKILL.md` dispatches to action files and reference sub-folders

The goal is a single memorable location where a user can find any link in the system. One page, many destinations.

## Coverage Rule

A dispatch table should link to **everything** under its folder, either directly or indirectly. If a sub-item is itself a dispatch page that links to its own contents, a single link to that dispatch page is sufficient — you don't need to link to the items it dispatches to. The test: starting from the dispatch table, can a reader reach every file in the folder tree within one or two clicks?
