# CAB Lint Rules Reference

Rules organized by level. Each level includes all rules from lower levels.


## Level 1 — Basic Anchor Structure

**`basic-structure`** — Marker file, anchor page, and type-specific essentials all present.

## Level 2 — Core Files

**`core-files`** — CLAUDE.md (Code), SKILL.md (Skill), Code symlink validity, README.md in repo.

## Level 3 — Docs Structure

**`docs-structure`** — Docs folder exists with dispatch page, Plan folder present, Dev folder present (Code anchors).

**`files-skeleton`** — Files.md exists. Module doc files exist in Dev folder. Dev dispatch page links to each module doc. Files.md links to each module doc. Checks existence and linkage only — not content correctness.

**`folder-docs`** — Every source folder with 2+ source files has a folder doc. Folder docs describe the subsystem, list its modules, and explain how they work together.

## Level 4 — Content Conventions

**`content-conventions`** — Anchor page has `description:` in frontmatter, breadcrumb (`:>>`), and dispatch table (`-[[NAME]]-`).

**`md-format`** — Common markdown formatting bugs that break rendering. Wiki-link vertical bars unescaped in tables, broken table syntax, missing backslash escapes.

## Level 5 — Module Doc Comparison

**`module-classes`** — Every public class/struct in source has an entry in a module doc. Classes in docs still exist in source.

**`module-methods`** — Every public method in source appears in its class's per-class table. Methods in docs still exist in source.

**`module-fields`** — Fields in source appear in per-class tables. Fields in docs still exist in source.

## Level 6 — Link Integrity (planned)

**`doc-reachability`** — Every .md file in Docs is reachable by walking wiki-links from `{NAME} Docs.md`.

## Level 7 — Cross-references (planned)

**`wiki-links`** — All `[[Target]]` links in anchor markdown files resolve to existing files.

## Level 8 — Naming (planned)

**`name-prefix`** — All files and folders inside anchor have `{NAME}` prefix.

## Level 9 — Pedantic (planned)

**`formatting`** — Heading spacing, TOC format, dispatch table column alignment follow MD conventions.


## Visibility Filtering

- Private classes and methods are **skipped by default**
- `--private` includes them
- `--pub-only` restricts to only `pub` items
- Fields are always reported (visibility not available from parser)


## Exceptions

Suppress rules via `.skl/lint/exceptions.md`. Both Module and Target columns support glob patterns.

```markdown
| Module | Target | Rule | Reason |
|--------|--------|------|--------|
| *.js | | * | Config files, not API |
| tests/* | | module-classes | Test files |
| src/ui/popup.rs | WindowSizeMode | module-classes | Private enum |
```

`--show-exceptions` to see what's suppressed.


## Command Line

```bash
python3 ~/ob/kmr/SYS/Bespoke/Skill\ Agent/LINT/cab-lint.py <anchor-path> [options]

Options:
  --level N           Lint level 1-9 (default: 5)
  --type TYPE         Override detected anchor type
  --json              Output as JSON
  --verbose, -v       Show parsing progress
  --show-exceptions   Show suppressed warnings
  --private           Include private items
  --pub-only          Only warn about pub items
```

Exit codes: 0 = PASS, 1 = CONCERNS, 2 = FAIL


# Rule Definitions


## basic-structure

Checks that the anchor folder has its minimum required files:
- **Marker file** — `{FolderName}.md` exists in the folder
- **Anchor page** — A markdown file containing a `description:` in frontmatter (or legacy `desc::` inline) or dispatch table (`-[[NAME]]-`). May be the marker file itself or a separate file.


## core-files

Type-specific required files:
- **Code Anchor**: `CLAUDE.md` at anchor root. `Code` symlink resolves (or `.git` for inline mode). `README.md` in repo.
- **Skill Anchor**: `SKILL.md` with valid YAML frontmatter.


## docs-structure

- `{NAME} Docs/` folder exists with dispatch page (`{NAME} Docs.md`)
- `{NAME} Plan/` subfolder under Docs
- Code Anchors: `{NAME} Dev/` subfolder under Docs


## files-skeleton

Checks that the documentation skeleton exists and is connected — but NOT that the contents are correct (that's level 5):
- `{NAME} Files.md` exists
- Module doc files exist in `{NAME} Dev/` for source modules
- Dev dispatch page (`{NAME} Dev.md`) contains wiki-links to each module doc
- `{NAME} Files.md` contains wiki-links to each module doc
- This is the "linking rule" enforcement — an unlinked module doc is invisible


## content-conventions

Anchor page patterns:
- **`description:`** — one-line description in YAML frontmatter (older anchors may use `desc::` inline — migrate to frontmatter)
- **`:>>`** — breadcrumb navigation
- **`-[[NAME]]-`** — dispatch table header


## md-format

Scans markdown files for common formatting bugs:
- **Unescaped `|` in wiki-links inside tables** — `[[#^1|details]]` breaks the table because `|` is the column separator. Must be `[[#^1\|details]]`. This is the most common formatting bug.
- **Unescaped `|` in display aliases inside tables** — `[[Some Page|Display Name]]` must be `[[Some Page\|Display Name]]` when inside a table row.
- **Table rows with wrong column count** — row has more or fewer `|` separators than the header row.

This check applies to all `.md` files in the anchor, not just the anchor page.


## module-classes

Compares source classes (tree-sitter) against module doc CLASSES tables:
- Source class not in docs → `class-undocumented`
- Doc class not in source → `class-stale-doc`
- Case-insensitive matching (DictaMuxConfig = DictaMUXConfig)
- Private classes skipped by default


## module-methods

Compares source methods against per-class table Methods sections:
- Source method not in doc → `method-undocumented`
- Doc method not in source → `method-stale-doc`
- Private methods skipped by default
- Matched by name within parent class


## module-fields

Compares source fields against per-class table properties:
- Count mismatch → `field-count-mismatch`
- Source field not in doc → `field-undocumented`
- Doc field not in source → `field-stale-doc`
- All fields reported (parser doesn't capture field visibility)


## folder-docs

Every source folder containing 2 or more source files should have a folder doc in `{NAME} Dev/`. The folder doc:
- Is named `{NAME} {FolderName}.md` (e.g., `DMUX Speech.md`)
- Has a MODULES table listing all modules in the folder
- Describes the subsystem: what it does, how modules relate, what API it presents
- See "Folder Docs" section in [[CAB Module Doc]] for full format

Single-file folders are skipped — they don't need a separate folder doc.


## doc-reachability *(Level 6, planned)*

Walk wiki-links from `{NAME} Docs.md`. Every `.md` in Docs should be reachable. Orphaned files reported.


## source-coverage *(Level 6, planned)*

Each source file with public API should have a module doc in `{NAME} Dev/`. Matched by class name.


## dev-linkage *(Level 6, planned)*

Every module doc must be linked from Dev dispatch page and Files tree. **Unlinked docs are invisible** — this is the most common failure.


## wiki-links *(Level 7, planned)*

Every `[[Target]]` wiki-link resolves to an existing vault file. Broken links reported.


## name-prefix *(Level 8, planned)*

All files/folders in anchor prefixed with `{NAME}` (except CLAUDE.md, Code, .skl/).


## formatting *(Level 9, planned)*

Markdown conventions: heading spacing, dispatch table format, TOC indentation.
