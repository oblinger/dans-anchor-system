# Compile: audit-docs

## Output
~/.claude/skills/audit/audit-docs.compiled.md

## Sources

- `~/.claude/skills/CAB/cab-parts/CAB Module Doc.md` — module doc format, CLASSES table, per-class tables, casing rules, spacing, folder docs
- `~/.claude/skills/CAB/cab-parts/CAB Files.md` — Files.md format (monospace, box-drawing tree)
- `~/.claude/skills/CAB/cab-parts/CAB Dev Dispatch.md` — Dev dispatch linking requirements
- `~/.claude/skills/code/code-modules.md` — module creation workflow, verification checklist

## How to Compile

Produce a checklist the agent follows to audit and fix documentation for a code anchor. The checklist has three phases:

**Phase 1: Scan** — use cab-lint to get the source scan, compare source tree to Files.md, identify gaps
**Phase 2: Report** — build the fixes table, post to stat
**Phase 3: Fix (when --fix)** — create missing docs, update stale docs, fix Files.md

For each module doc that needs creating or updating, include the full format checklist from CAB Module Doc (CLASSES table format, ALL CAPS headers, block IDs, per-class tables, enum two-column format, casing rules, spacing rules).

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
