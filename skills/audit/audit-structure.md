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

### 4a. Check Sparse-Linked Anchor (`remotes:`)

If the anchor's `.anchor` declares a `remotes:` list (a Sparse-Linked anchor per [[Anchor Remotes]] — the "docs in the vault, code at `~/ob/proj`, synced via git" pattern), verify the declaration against what is actually on disk. This is a read-only check delegated to the `code` tool (the `remotes:` realization logic has no place in this runbook's ad-hoc checks — it lives with the tool that builds the layout):

```bash
# Path: ob-skills/skills/ob-skills/scripts/code  (the `das` host). Read-only.
ob-skills/skills/ob-skills/scripts/code audit <anchor-path>
```

`code audit` verifies, for the anchor:

- each declared checkout's working tree exists and is a git work tree;
- checkouts that share a `repo` are realized as **worktrees of one clone** (one `.git`, shared objects) — not two independent clones;
- each checkout's **actual sparse cone matches its declared `from`** (no code leaked into a docs checkout, no docs leaked into the code checkout);
- checkouts sharing a `repo` are **complementary** (their `from` subtrees don't overlap);
- the top-level `code:` field equals the `at:` of the code checkout.

It exits `0` when clean, `1` on any drift (printing one finding per problem), and `0` (skip) when the anchor has no `remotes:`. Fold any findings into the findings table in step 8 with action `code reattach <anchor> --apply` (rebuild) or `code link <anchor> --apply` (re-set a drifted sparse cone). **Audit never fixes** — surface the findings only.

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

`{NAME} Docs/{NAME} Dev/{NAME} Files.md` (if present) must follow [[FCT All Files]]. Common mistakes that need to be caught:

| Violation | How to detect | Why wrong |
|-----------|---------------|-----------|
| Body wrapped in a ``` code fence | Grep the file for lines matching `^```` | Wiki-links inside a code fence render as literal text, not clickable links — the whole page becomes dead |
| `cssclass:` (singular) in frontmatter | Grep for `^cssclass:` without the `es` | Obsidian's key is `cssclasses` (plural, list). Singular is silently ignored, so the page doesn't render monospace |
| `cssclasses: monospace` missing entirely | Check frontmatter has `cssclasses:` with a `monospace` entry | Page won't render in fixed-width font; the tree's box-drawing chars will misalign |
| Source files use `→ [[doc]]` arrows | Grep source-file lines for `→ \[\[` | Per [[FCT All Files]], source files use filename-as-link: `[[OBU Lib\|lib.rs]]`. Arrows are only for non-source files pointing to external specs |

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

### 7a. Check Active-work invariant — orphan feature docs

Per `[[SKA workflow]]` § Active-work invariant: every feature doc in `{NAME} Features/` must be reachable from one of `{NAME} Backlog.md`, `{NAME} Roadmap.md`, or `{NAME} Icebox.md`.

For each `*.md` file in `{NAME} Features/`:

1. Compute the wiki-link basename (e.g., `F5 — Backlog` for `F5 — Backlog.md`).
2. Search the three index files for `[[<basename>]]` (allowing alias and `#anchor` suffixes).
3. **Match in any of the three** → invariant holds, no finding.
4. **No match** → orphan. Add a finding: `orphan-feature-doc: {filename} — not linked from backlog/roadmap/icebox`.

For each orphan, the suggested action is **backfill a backlog row in `## Now`** with the F-number from the filename (or assign a new F-number if the file lacks one), bracket = `[Questions]` if the doc has pending Qs in `## Open Questions`, else `[Designing]`. Description = `→ [[<basename>]]`.

Run with `--orphan-sweep` to backfill automatically (one-time migration); without the flag, just flag findings for the user to review.

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

## Mechanical scanner — `cab-audit.py` (migrated from `/lint`, F078)

`cab-audit.py` (formerly `cab-lint.py`) is the standalone static scanner covering the structural checks above plus the module-doc comparison consumed by `/audit docs`. Run it as the mechanical first pass; the workflow steps 2–7 cover the judgment calls the script can't make. The script is **read-only** — its output feeds the findings table (step 8), never direct repairs.

```bash
python3 ~/.claude/skills/audit/scripts/cab-audit.py <anchor-path> [--level 5] [--verbose] [--show-exceptions]
# or, once wired onto $PATH by /install:
cab-audit <anchor-path> --level 3
```

Requires `tree-sitter-analyzer` (`pip install tree-sitter-analyzer`) for source parsing at level 5+. Tests and private items are excluded by default (`--private` / `--pub-only` to adjust). Exit codes: 0 = PASS, 1 = CONCERNS, 2 = FAIL.

### Scan levels

| Level | Name | What it checks |
|-------|------|----------------|
| 1 | Bare Bones | Marker file, anchor page exist |
| 2 | Core | CLAUDE.md, `.anchor` `code:` key resolves (type-specific), README.md, SKILL.md (type-specific) |
| 3 | Structure | Docs folder, Plan folder, Dev folder |
| 4 | Content | `description:` in frontmatter, breadcrumb, dispatch table present |
| 5 | **Default** | Module doc comparison — classes, methods, fields match source code |
| 6 | Links | All markdown files reachable from dispatch tree |
| 7 | Cross-ref | Wiki-links resolve, no broken internal links |
| 8 | Naming | `{NAME}` prefix on all files/folders |
| 9 | Pedantic | Spacing rules, TOC format, column alignment |

### Detect-only rules (per F059)

The scanner and this audit are **detect-only**. Even when a finding implies a clear repair, do NOT take the repair action — that's `/rewire`'s job (or the downstream backlog pull). Three categorical rules:

- **No dispatch-table edits.** "Missing row" / "missing dispatch table" findings are flagged for `/rewire` — never add the row or table inline. Auto-fixing a `dispatch-duplication` finding by adding a third canonical-form table is the DMUX bug (F059 root cause).
- **No file creation.** Missing module docs / missing facet files are flagged — never created here.
- **No moves.** Misplaced files (basename in wrong location) are flagged — never moved here.

### Exceptions file

Per-anchor suppressions live at `.anchor.d/lint/exceptions.md` (directory name retained for now — renaming `.anchor.d/lint/` is deferred per F078 scope). Rows are sorted by module path, then target; both Module and Target columns support **glob patterns** (`*`, `?`) — prefer glob exceptions over per-item entries when a whole category should be excluded.

Row shape (Module | Target | Rule | Reason), e.g. `src/ui/popup.rs | WindowSizeMode | class-undocumented | Private enum, internal only` or `tests/* | | class-undocumented | Test files`.

**No blanket rule suppressions** — an exception with `*` module AND empty target for a content rule is rejected by the tool. Every exception must name either a Module path or a Target; this forces case-by-case judgment instead of sweeping categories under the rug.
