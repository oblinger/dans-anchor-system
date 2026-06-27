# Compile: audit-docs

## Skill File
~/.claude/skills/audit/audit-docs.md

Write between `<!-- compiled:start -->` and `<!-- compiled:end -->` markers.

## Sources

- `~/.claude/skills/CAB/cab-facets/CAB Module Doc.md` — module doc format, CLASSES table, per-class tables, casing rules, spacing, folder docs
- `~/.claude/skills/CAB/cab-facets/CAB Files.md` — Files.md format (monospace, box-drawing tree)
- `~/.claude/skills/CAB/cab-facets/CAB Dev Dispatch.md` — Dev dispatch linking requirements
- `~/.claude/skills/code/code-modules.md` — module creation workflow, verification checklist

## How to Compile

Produce a checklist the agent follows to audit documentation for a code anchor. The checklist has four phases:

**Phase 1: Scan** — run the audit-docs script, compare source tree to Files.md, identify gaps, validate format
**Phase 2: Report** — build the findings table, print summary
**Phase 3: Write Backlog Entry** — append a single `B<n>` bullet under `## Upcoming` in `{NAME} Backlog.md` with one sub-bullet per finding (skipped when `dry` substring is in args). If sub-bullet count exceeds ~50, split into multiple entries grouped by category cluster.
**Phase 4: Report** — print one-line summary (`docs: N findings → B<n>` / `clean` / `dry-run`).

**Audits never modify documentation files.** All fix work flows into the backlog entry. When describing what's wrong with a doc, link to [[CAB API Doc]] for the canonical format — do not inline the full format checklist in the audit itself.

## Extras

- Wiki-links in tables: escape pipe as `\|`
- Blank line before every table
- Module doc named after primary class, not source filename
- All files and folders carry the `{NAME}` prefix
- CLASSES table entries use `[[#PascalCaseName]]` (source code class name)
- Per-class table header is ALL CAPS WITH SPACES: `TaskScheduler` → `TASK SCHEDULER`
- Per-class header has `([[#^N|details]])` link with block ID
- Properties listed first, then `**Methods**` separator row, then methods
- Enum tables use TWO columns (no Type/Returns)
- Double blank lines between per-class tables
- `# Class Details` H1 with three blank lines before it
- Each class H2: `## ClassName ^N` (PascalCase, block ID matches table)
- `### METHOD DETAILS` in ALL CAPS, three blank lines before it
- Method headings use full signature
- Link every module doc from Dev dispatch AND Files.md BEFORE writing content
- Compare freshness using `git log -1 --format=%ct` on source vs doc
- Folder docs for every source folder with 2+ modules
