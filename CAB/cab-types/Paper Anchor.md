# Paper Anchor

A Paper Anchor follows the [[Common Anchor Blueprint]] with these specializations:

## What Makes It a Paper Anchor

Paper Anchors are for iterative document revision with Claude. Long documents are split into sections for focused revision, then merged back together. The anchor page contains a **version table** that tracks document versions and section revisions.

## When to Use

Academic papers, whitepapers, long-form documents that go through multiple revision cycles.

## Specializations

- **Version table** — tracks document versions and per-section revisions on the anchor page
- **Section-based editing** — paper split into sections (s1, s2, ...) for focused work
- **Track changes** — section revisions stored as HTML with insertions/deletions
- **Paper Flow** — specialized review and merge workflow (see below)

## Structure

```
{Paper Name}/
├── {Paper Name}.md                  marker file → (See [[{NAME}]])
├── {NAME}.md                        anchor page (link table + version table)
├── {NAME} YYYY-MM-DD.md             merged version (one per version date)
├── {NAME} YYYY-MM-DD s1.html        section 1 revisions (track changes)
├── {NAME} YYYY-MM-DD s2.html        section 2 revisions
├── ...
└── {NAME} Research/                 optional: research materials
```

## Version Table

The version table is the core of the Paper Anchor. It lives on the anchor page.

```markdown
| Version              | Markup                                   | Notes |
| -------------------- | ---------------------------------------- | ----- |
| [[{NAME} YYYY-MM-DD]]| s1 s2 s3 ...                            |       |
| [[{NAME} YYYY-MM-DD]]| (original)                              | s1: Intro, s2: Methods, ... |
```

### Row Organization
- **Row 1 (top)** — working row: where current edits go
- **Row 2** — source row: the version being revised
- **Reverse chronological order** — newest versions at top

### Markup Column
- Unedited sections: just text (`s1`)
- Edited sections: link to HTML with track changes (`[[{NAME} YYYY-MM-DD s1.html|s1]]✓`)
- `✓` indicates the section revision is complete

## Section Philosophy

Claude works best on coherent, manageable chunks. Splitting into sections allows focused attention, smaller context, and incremental progress.

- **Guideline**: Aim for sections that are coherent logical units (roughly 1-2 pages each)
- **Numbering**: Sequential (`s1`, `s2`, `s3`); insert without renumbering (`s2b`)
- **Invisible markers**: Use `<!-- s3 -->` to subdivide without visible headings

## Paper Flow

### Paper Flow Review
**Trigger:** User says "paper flow review"

1. Claude reads from row 2 (source version)
2. User specifies a section: "let's work on section 2"
3. Claude creates/updates `{NAME} {DATE} s{N}.html` with track changes
4. Revisions are relative to the source (row 2), not to previous revisions in row 1
5. The same revision file is updated across multiple sessions

### Paper Flow Merge
**Trigger:** User says "paper flow merge"

1. Claude takes all section revisions from row 1
2. For sections without revisions, pull content from row 2
3. Merge all sections into a single markdown document
4. If current date matches existing version: overwrite
5. If new date: create new file, add to Version column

## Setup Checklist

1. Create folder with paper name
2. Create marker: `{Paper Name}.md` → `(See [[{NAME}]])`
3. Create anchor page: `{NAME}.md` with link table and version table
4. Add original document as first version (row 2)
5. Decide on section structure and add descriptions in Notes column
6. Create empty row 1 for revisions
7. Register HookAnchor commands (`ha -d`)
8. Register TLC in the [[TLC]] index
