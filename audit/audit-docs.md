# Docs — Audit Documentation Against Source Code

Ensure every source module has a correct module doc, Files.md matches the source tree, and docs stay current. **Reports findings only.** Fix work goes into a backlog entry; no docs are modified.

## Runbook

### 1. Detect anchor, find code path from `.anchor` file or frontmatter

### 2. Execute the compiled checklist below

### 3. Modes

- **`/audit docs`** — scan, report, write backlog entry.
- **`/audit docs dry`** (or `dry-run` anywhere in args) — scan and report only; do not write a backlog entry.
- **`/audit docs recheck`** — ignore freshness, check every doc against source.

<!-- compiled:start source=CAB/compile/targets/audit-docs.md -->

# Phase 1: Scan — RUN THE SCRIPT

## 1.1 Run audit-docs script

```bash
python3 ~/.claude/skills/anchor/scripts/audit-docs.py <anchor-path> --verbose
```

This does ALL the scanning: inventories source files, compares against Files.md, checks Dev dispatch, checks module docs, checks freshness. It outputs a table of findings to stdout and summary counts to stderr.

**Read the entire output.** The script is the source of truth for Phase 1. Do not manually scan — the script already did it.

## 1.2 Parse the script output

The script output is a markdown table with columns: `#`, `File`, `Status`, `Issue`

Status values:
- `missing-entry` — source file not in Files.md
- `stale-entry` — Files.md entry pointing to nonexistent file
- `missing-doc` — no module doc exists for this source file
- `stale` — module doc is behind source (issue shows staleness)
- `unlinked` — module doc exists but not linked from Dev dispatch
- `missing-folder-doc` — directory with 2+ modules has no folder doc
- [ ] Check Files and Architecture rows appear first (fixed rows)
- [ ] Flag any module doc missing from Dev dispatch as **missing-from-dev**
- [ ] Flag any Dev dispatch entry pointing to a nonexistent module doc as **stale-dev-entry**

## 1.4 Compare source tree to module docs
- [ ] List all `{NAME} *.md` files under `{NAME} Dev/`
- [ ] For each source file with public API, check a corresponding module doc exists
- [ ] For each source directory with modules, check a folder doc exists (`{NAME} {FolderName}.md`)
- [ ] Flag missing module docs as **missing-module-doc**
- [ ] Flag missing folder docs as **missing-folder-doc**
- [ ] Flag module docs whose source file no longer exists as **orphan-module-doc**

## 1.5 Check freshness of existing module docs
- [ ] For each existing module doc, compare its CLASSES table entries against the actual classes in source
- [ ] For each existing module doc, compare per-class table properties/methods against source public API
- [ ] Flag docs where classes were added/removed/renamed in source as **stale-classes**
- [ ] Flag docs where methods or properties changed signature as **stale-methods**

## 1.6 Validate module doc format
For each existing module doc, check every item in the [[CAB Module Doc]] format checklist:
- [ ] Flag format violations as **format-error** with the specific rule broken

(See [[CAB Module Doc]] for the canonical checklist — naming, headings, CLASSES table, per-class tables, METHOD DETAILS, casing, spacing, table formatting. The audit *flags* violations; it does not apply the format. Fixes happen later, when the corresponding backlog entry is pulled.)

## 1.7 Check Files.md column alignment

`{NAME} Files.md` renders in monospace via `cssclasses: monospace`. The description column must start at the same display-width column on every line that has a description. Misalignment is a visual bug — the page is supposed to look like a tidy column layout.

Two specific checks:

1. **Description column alignment** — every line with a description starts its description at the same display-width column. Wiki-link expansion must be accounted for: `[[OBU Scheduler|scheduler.rs]]` has raw width ~30 but renders as `scheduler.rs` (12). The pad count is based on *rendered* width, not raw markdown width.

2. **Row 1 convention** — the first tree line (the repo-root directory) does **not** include the literal text "repo root" or similar descriptor. It goes directly to its description, which is conventionally the wiki-link to the rollup (`[[{NAME} Rollup]]`).

Flag misaligned files as **files-misaligned** (with the list of bad rows) and redundant text as **files-row1-redundant**.

```python
# Audit snippet — scans * Docs/* Dev/* Files.md, flags misaligned descriptions and "repo root" on row 1.
import re, pathlib

def display_width(s):
    s = re.sub(r'\[\[([^\]|]+)\\?\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'\1', s)
    return len(s)

for f in pathlib.Path('.').rglob('* Docs/* Dev/* Files.md'):
    text = f.read_text()
    body = re.split(r'^---\n.*?\n---\n', text, maxsplit=1, flags=re.DOTALL)[-1]
    cols = []
    row1_bad = False
    first = True
    for line in body.split('\n'):
        m = re.match(r'^((?:│\s+|\s+)*(?:[├└]── )?)(.*)$', line)
        if not m: continue
        prefix = m.group(1); rest = m.group(2)
        if not rest or rest.startswith('#') or rest.startswith(':>>'): continue
        if first and re.search(r'\brepo (root|route)\b', line, re.I):
            row1_bad = True
        first = False
        sp = re.search(r'  +', rest)
        if not sp: continue
        fn = rest[:sp.start()]
        desc_col = len(prefix) + display_width(fn) + len(sp.group(0))
        cols.append(desc_col)
    if cols and max(cols) - min(cols) > 2:
        print(f'{f}: description column varies ({min(cols)}-{max(cols)})')
    if row1_bad:
        print(f'{f}: row 1 has redundant "repo root" text')
```

## 1.8 Check rollup (code-trait anchors only)

The rollup (see [[CAB Rollup]]) is the whole-codebase API overview. It must exist and be reachable from two places:

- [ ] `{NAME} Docs/{NAME} Dev/{NAME} Rollup.md` exists. Flag absence as **missing-rollup**.
- [ ] `{NAME} Files.md` row 1 (the repo-root directory row) contains `→ [[{NAME} Rollup]]`. Flag absence as **rollup-not-linked-from-files**.
- [ ] `{NAME} Dev.md` dispatch page contains a row linking to `[[{NAME} Rollup]]`. Flag absence as **rollup-not-linked-from-dispatch**.
- [ ] Rollup file contains `## Public Modules` and `## How They Group` sections. Flag missing sections as **rollup-incomplete-structure**.
- [ ] Rollup lists every top-level public module that exists in source. Flag missing modules as **rollup-module-missing**.
- [ ] Rollup line count ≤ 500. Flag overflow as **rollup-too-large** — suggest splitting into `{NAME} {Subsystem} Rollup.md` files.

For linked-mode code anchors where the repo is elsewhere, also check the **repo root** has a visible reference to the rollup so repo-only readers can find it.


# Phase 2: Report

## 2.1 Build findings table
- [ ] Create a markdown table with columns: File, Issue, Category, Suggested Fix
- [ ] Categories: missing-from-files, stale-files-entry, missing-from-dev, stale-dev-entry, missing-module-doc, missing-folder-doc, orphan-module-doc, stale-classes, stale-methods, format-error, files-misaligned, files-row1-redundant, missing-rollup, rollup-not-linked-from-files, rollup-not-linked-from-dispatch, rollup-incomplete-structure, rollup-module-missing, rollup-too-large
- [ ] Sort by category, then by file path

## 2.2 Print summary
- [ ] Count issues per category
- [ ] Print total missing module docs, stale docs, format errors, linking gaps
- [ ] If zero issues, print "Docs are clean" and skip Phase 3 entirely


# Phase 3: Write Backlog Entry

If `dry` substring is in the args: print "dry-run — no backlog entry written" and stop.

Otherwise, locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Read it, find the lowest unused B-number (per [[CAB Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Docs audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit docs`. Sub-bullets are candidate splits if this needs to be broken up.
  - <category>: <file or path> — <short issue>
  - …
```

**Sub-bullet ordering.** Group by category, in this priority order (each category becomes a contiguous block of sub-bullets):

1. `missing-rollup`, `rollup-incomplete-structure` — the rollup is foundational; missing rollup blocks several other findings from being meaningful.
2. `missing-from-files`, `stale-files-entry`, `files-misaligned`, `files-row1-redundant` — Files.md is the top-of-tree index; fix it first.
3. `missing-from-dev`, `stale-dev-entry`, `rollup-not-linked-from-files`, `rollup-not-linked-from-dispatch` — linking gaps.
4. `missing-module-doc`, `missing-folder-doc` — content gaps.
5. `orphan-module-doc` — cleanup.
6. `stale-classes`, `stale-methods`, `format-error`, `rollup-module-missing`, `rollup-too-large` — content drift.

Within each category, sort by file path. Keep each sub-bullet to one line.

If sub-bullet count would exceed ~50, split into multiple backlog entries by category (one entry per category cluster) — too many sub-bullets in one entry defeats the "this is a unit of work" purpose. The orchestrator will allocate consecutive B-numbers in this case.

# Phase 4: Report

Print a one-line summary:
- With findings: `docs: <N> findings → B<n>` (or `B<n>..B<m>` if split)
- Clean: `docs: clean — no entry written`
- Dry: `docs: <N> findings (dry-run, no entry written)`

The orchestrator (or single-skill caller) will roll this up into the final stat post.

# Universal Rules

- [ ] Audits never modify documentation files.
- [ ] All findings flow into a backlog entry under `## Upcoming` (unless `dry`).
- [ ] Use [[CAB Module Doc]] as the canonical reference when describing what's wrong with a doc — link to the spec, don't inline the format.
- [ ] B-number assignment: lowest unused integer in the file (gap-fill).

<!-- compiled:end -->
