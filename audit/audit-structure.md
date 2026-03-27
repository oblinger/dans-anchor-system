# Structure — Verify Anchor Structure and Links

Check that all expected files exist, dispatch tables are properly wired with standard rows in the correct order, all wiki-links resolve, and no files are orphaned.

## Workflow

### 1. Detect Anchor

Read the anchor page (has `cab-type:` in frontmatter or `-[[NAME]]-` dispatch table). Determine the RID, anchor type, and expected structure.

### 2. Check Standard Dispatch Rows

Read the [[CAB Anchor Page]] reference example. The dispatch table must have the standard rows in this exact order (skipping rows that don't apply to this type):

1. External
2. User
3. Plan
4. Execute
5. Dev
6. Research

Project-specific rows go after the standard rows. Flag any standard row that is out of order or missing when it should exist for this type.

### 3. Check Common File Existence

These files are expected for ALL anchor types:

- Marker file: `{FolderName}.md`
- Anchor page: `{NAME}.md` with `cab-type:` and `description:` in frontmatter, dispatch table
- CLAUDE.md with role header
- `.skl/config.yaml` with rid and type

### 4. Check Type-Specific Structure

Read the type spec file from `~/.claude/skills/CAB/cab-types/` for this anchor's type (e.g., `Code Anchor.md`, `Topic Anchor.md`). If the type spec has an `## Audit` section, run those checks. This covers type-specific files, folders, and conventions.

### 5. Check Link Integrity

Scan all markdown files in the anchor for wiki-links. For each `[[link]]`:
- Does the target file exist?
- If aliased (`[[target|display]]`), does the target exist?
- Flag broken links with file and line number

Also check for orphaned files — files that exist but aren't linked from any dispatch page or other document.

### 6. Check Sub-Dispatch Pages

Each dispatch page must link to all its children. Only check dispatch pages that exist for this anchor type:
- Plan dispatch → planning docs it contains
- Dev dispatch → module docs and Files
- User dispatch → user-facing docs
- Docs dispatch → Plan, Dev, User subfolders

### 7. Build the Fixes Table

Combine all findings into a single table:

| # | Item | Action | Command |
|---|------|--------|---------|
| 1 | {NAME} Research.md | Create missing file | `/cab create` or create manually |
| 2 | {NAME} Plan.md:12 → [[{NAME} Roadmap]] | Fix broken link | Remove link or create target file |
| 3 | Dispatch: Research before Dev | Reorder rows | `/code rewire` |
| 4 | old-notes.md | Orphan — not linked from any dispatch | Link or remove |
| 5 | .skl/config.yaml | Missing config | `cab-config init` |

### 8. Post to Stat

```bash
skl-stat add "[[{NAME}]]" "Review" "Structure audit: N fixes needed" --output
```

Write the fixes table to the output file.
