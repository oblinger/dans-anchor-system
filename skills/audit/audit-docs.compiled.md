# /audit docs — compiled checklist

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
For each existing module doc, check every item in the [[CAB API Doc]] format checklist:
- [ ] Flag format violations as **format-error** with the specific rule broken

(See [[CAB API Doc]] for the canonical checklist — naming, headings, CLASSES table, per-class tables, METHOD DETAILS, casing, spacing, table formatting. The audit *flags* violations; it does not apply the format. Fixes happen later, when the corresponding backlog entry is pulled.)

## 1.7 Check Files.md column alignment

`{NAME} Files.md` renders in monospace via `cssclasses: monospace`. The description column must start at the same display-width column on every line that has a description.

Two specific checks:

1. **Description column alignment** — every line with a description starts its description at the same display-width column. Wiki-link expansion must be accounted for: `[[OBU Scheduler|scheduler.rs]]` has raw width ~30 but renders as `scheduler.rs` (12). The pad count is based on *rendered* width.
2. **Row 1 convention** — the first tree line (the repo-root directory) does **not** include the literal text "repo root" or similar descriptor.

Flag misaligned files as **files-misaligned** and redundant text as **files-row1-redundant**.

## 1.8 Check Interface (code-trait anchors only)

The Interface (see [[CAB Interface]]) is the **required top-level human-authored layer contract** for the codebase. It must exist and be reachable from two places:

- [ ] `{NAME} Docs/{NAME} User/{NAME} Interface.md` exists. Flag absence as **missing-interface**.
- [ ] `{NAME} Files.md` row 1 contains `→ [[{NAME} Interface]]`. Flag absence as **interface-not-linked-from-files**.
- [ ] `{NAME} User.md` dispatch table contains a row linking to `[[{NAME} Interface]]`. Flag absence as **interface-not-linked-from-dispatch**.
- [ ] Interface file contains `## Public Modules` and at least one structural section. Flag missing sections as **interface-incomplete-structure**.
- [ ] Interface lists every top-level public module that exists in source. Flag missing modules as **interface-module-missing**.
- [ ] Interface line count ≤ 500. Flag overflow as **interface-too-large**.
- [ ] Legacy `{NAME} Rollup.md` (predecessor to Interface — F062): flag as **legacy-rollup-needs-migration**. Do not auto-rename.


# Phase 2: Report

## 2.1 Build findings table
- [ ] Markdown table with columns: File, Issue, Category, Suggested Fix
- [ ] Sort by category, then by file path

## 2.2 Print summary
- [ ] Count issues per category
- [ ] If zero issues, print "Docs are clean" and skip Phase 3 entirely


# Phase 3: Write Backlog Entry

If `dry` substring is in the args: print "dry-run — no backlog entry written" and stop.

Otherwise, locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Read it, find the lowest unused B-number (per [[CAB Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Docs audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit docs`. Sub-bullets are candidate splits if this needs to be broken up.
  - <category>: <file or path> — <short issue>
  - …
```

**Sub-bullet ordering** (group by category, in priority):
1. `missing-interface`, `interface-incomplete-structure`, `legacy-rollup-needs-migration`
2. `missing-from-files`, `stale-files-entry`, `files-misaligned`, `files-row1-redundant`
3. `missing-from-dev`, `stale-dev-entry`, `interface-not-linked-from-files`, `interface-not-linked-from-dispatch`
4. `missing-module-doc`, `missing-folder-doc`
5. `orphan-module-doc`
6. `stale-classes`, `stale-methods`, `format-error`, `interface-module-missing`, `interface-too-large`

Within each category, sort by file path. One line per sub-bullet.

If sub-bullet count exceeds ~50, split into multiple entries by category cluster.


# Phase 4: Report

Print one-line summary:
- With findings: `docs: <N> findings → B<n>` (or `B<n>..B<m>` if split)
- Clean: `docs: clean — no entry written`
- Dry: `docs: <N> findings (dry-run, no entry written)`


# Universal Rules

- [ ] Audits never modify documentation files.
- [ ] All findings flow into a backlog entry under `## Upcoming` (unless `dry`).
- [ ] Use [[CAB API Doc]] as the canonical reference when describing what's wrong with a doc.
- [ ] B-number assignment: lowest unused integer in the file (gap-fill).
