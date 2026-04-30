# Structure — Audit Anchor Structure and Links

Check that all expected files exist, dispatch tables are properly wired with standard rows in the correct order, all wiki-links resolve, and no files are orphaned. **Reports findings only.** Fix work goes into a backlog entry; no files are modified.

## Workflow

### 1. Detect Anchor

Read the anchor page (has `cab-traits:` in frontmatter or `-[[NAME]]-` dispatch table). Determine the slug, anchor traits, and expected structure.

### 2. Check Standard Dispatch Rows

Read the [[CAB slug Page]] reference example. The dispatch table must have the standard rows in this exact order (skipping rows that don't apply to this anchor's traits):

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
- Anchor page: `{NAME}.md` with `cab-traits:` and `description:` in frontmatter, dispatch table
- CLAUDE.md with role header
- `.anchor` file (can be empty — properties derive from folder name)

### 4. Check Type-Specific Structure

Read the trait spec file from `~/.claude/skills/CAB/cab-traits/` for each of this anchor's traits (e.g., `Code Anchor.md`, `Topic Anchor.md`). If a trait spec has an `## Audit` section, run those checks. For multi-trait anchors, run the union of all trait-specific checks. This covers trait-specific files, folders, and conventions.

### 5. Check Link Integrity

Scan all markdown files in the anchor for wiki-links. For each `[[link]]`:
- Does the target file exist?
- If aliased (`[[target|display]]`), does the target exist?
- Flag broken links with file and line number

Also check for orphaned files — files that exist but aren't linked from any dispatch page or other document.

### 6. Check Sub-Dispatch Pages

Each dispatch page must link to all its children. Only check dispatch pages that exist for this anchor's traits:
- Plan dispatch → planning docs it contains
- Dev dispatch → module docs and Files
- User dispatch → user-facing docs
- Docs dispatch → Plan, Dev, User subfolders

### 7. Check Files.md Format

`{NAME} Docs/{NAME} Dev/{NAME} Files.md` (if present) must follow [[CAB Files]]. Common mistakes that need to be caught:

| Violation | How to detect | Why wrong |
|-----------|---------------|-----------|
| Body wrapped in a ``` code fence | Grep the file for lines matching `^```` | Wiki-links inside a code fence render as literal text, not clickable links — the whole page becomes dead |
| `cssclass:` (singular) in frontmatter | Grep for `^cssclass:` without the `es` | Obsidian's key is `cssclasses` (plural, list). Singular is silently ignored, so the page doesn't render monospace |
| `cssclasses: monospace` missing entirely | Check frontmatter has `cssclasses:` with a `monospace` entry | Page won't render in fixed-width font; the tree's box-drawing chars will misalign |
| Source files use `→ [[doc]]` arrows | Grep source-file lines for `→ \[\[` | Per [[CAB Files]], source files use filename-as-link: `[[OBU Lib\|lib.rs]]`. Arrows are only for non-source files pointing to external specs |

```bash
# Quick one-liner to catch the first three. Only checks files that live under
# the anchor's Dev folder — so spec/example files like CAB Files.md in the CAB
# facet docs are not flagged.
python3 -c '
import re, yaml, pathlib
for f in pathlib.Path(".").rglob("* Docs/* Dev/* Files.md"):
    text = f.read_text()
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    meta = yaml.safe_load(fm.group(1)) if fm else {}
    issues = []
    if meta and "cssclass" in meta and "cssclasses" not in meta:
        issues.append("cssclass (singular) — should be cssclasses")
    if not meta or "cssclasses" not in meta:
        issues.append("missing cssclasses: monospace")
    elif "monospace" not in (meta.get("cssclasses") or []):
        issues.append("cssclasses missing monospace entry")
    if re.search(r"^```", text, re.MULTILINE):
        issues.append("body wrapped in code fence — wiki-links will not be clickable")
    for i in issues: print(f"{f}: {i}")
'
```

### 8. Build the Findings Table

Combine all findings from sections 2–7 into a single table:

| # | Item | Action | Command |
|---|------|--------|---------|
| 1 | {NAME} Research.md | Create missing file | `/cab create` or create manually |
| 2 | {NAME} Plan.md:12 → [[{NAME} Roadmap]] | Fix broken link | Remove link or create target file |
| 3 | Dispatch: Research before Dev | Reorder rows | `/code rewire` |
| 4 | old-notes.md | Orphan — not linked from any dispatch | Link or remove |
| 5 | .skl/config.yaml | Missing config | `cab-config init` |

Print this table to the console. **If `dry` substring is in the args**, stop here — print "dry-run — no backlog entry written." Otherwise continue.

### 9. Write the Backlog Entry

Locate the backlog file: `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Read it, find the lowest unused B-number (per [[CAB Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Structure audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit structure`. Sub-bullets are candidate splits if this needs to be broken up.
  - <Item from row 1 of findings table — short, with file:line if available>
  - <Item from row 2 …>
  - …
```

Keep sub-bullet text terse (one line each). Order: missing files first, then broken links, then dispatch-order issues, then orphans, then format violations.

If there are zero findings, do **not** write an entry. Skip to step 10 with a clean status.

### 10. Report

Print a one-line summary:
- With findings: `structure: N findings → B<n>`
- Clean: `structure: clean — no entry written`
- Dry: `structure: N findings (dry-run, no entry written)`

The orchestrator (or single-skill caller) will roll this up into the final stat post.
