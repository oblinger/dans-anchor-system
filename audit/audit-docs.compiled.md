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
For each existing module doc, check every item in the format checklist (Phase 3, section 3.2):
- [ ] Flag format violations as **format-error** with the specific rule broken


# Phase 2: Report

## 2.1 Build fixes table
- [ ] Create a markdown table with columns: File, Issue, Category, Action
- [ ] Categories: missing-from-files, stale-files-entry, missing-from-dev, stale-dev-entry, missing-module-doc, missing-folder-doc, orphan-module-doc, stale-classes, stale-methods, format-error
- [ ] Sort by category, then by file path

## 2.2 Print summary
- [ ] Count issues per category
- [ ] Print total missing module docs, stale docs, format errors, linking gaps
- [ ] If zero issues, print "Docs are clean" and stop


# Phase 3: Fix (only when --fix flag is set)

**CRITICAL: The script is the source of truth for naming and location.** If a doc exists but has the wrong name or is in the wrong folder, rename/move it — no discussion needed. The script's naming convention (snake_case → PascalCase) is the standard. If the script expects `HA Commands.md` and you have `HA Command.md`, rename the file.

For `missing-doc` findings: if the source file genuinely should not have a doc (trivial wrapper, auto-generated, re-exports only), tell the user and propose adding it to `.anchor/audit-docs.yaml` exclusions. Do not silently skip it or create a pointless doc.

## 3.1 Link FIRST — update Files.md and Dev dispatch before creating any docs
- [ ] Add missing source files to `{NAME} Files.md` using the filename-as-link pattern
- [ ] Remove stale entries from `{NAME} Files.md` for deleted files
- [ ] Maintain monospace alignment — use Python to compute display-width-based column alignment
- [ ] Add missing module doc rows to `{NAME} Dev.md` dispatch table
- [ ] Remove stale entries from `{NAME} Dev.md` for deleted modules
- [ ] Group module rows by source folder with bold folder headers

## 3.2 Create missing module docs
For each missing module doc:
- [ ] Read the source file to extract classes, properties, methods, enums
- [ ] Read `~/.claude/skills/CAB/cab-parts/CAB Module Doc.md` reference example (MANDATORY — do this EVERY TIME, do NOT write from memory)
- [ ] Create the doc following the exact format checklist below
- [ ] Verify the doc is already linked from Dev dispatch AND Files.md (done in 3.1)

### Module doc format checklist — COMPLETE

Every module doc must satisfy ALL of the following. An agent must be able to produce a perfect doc from this checklist alone.

#### Document-level structure
- [ ] File is named `{NAME} {PrimaryClassName}.md` (PascalCase class name, not the source filename)
- [ ] File lives under `{NAME} Dev/` in a subfolder mirroring the source tree path

#### Line 1: Breadcrumb
- [ ] Optional breadcrumb line: ` [[Parent Index]] → [[Subsystem]]`
- [ ] One blank line between breadcrumb and H1

#### H1: Module name
- [ ] Format: `# {NAME} {PrimaryClassName}`
- [ ] Uses the `{NAME}` prefix
- [ ] One blank line after H1

#### Brief paragraph
- [ ] 2-4 sentences immediately after H1
- [ ] Describes the module's purpose and role in the system
- [ ] One blank line after the brief

#### CLASSES table
- [ ] Exactly two columns: `CLASSES` and `Description`
- [ ] Header word is `CLASSES` (all caps)
- [ ] Each entry is a wiki-link to the class H2: `[[#TaskScheduler]]`
- [ ] Wiki-link uses the source code PascalCase class name — NOT spaced, NOT all caps
- [ ] One-line description per class
- [ ] Enums have description prefixed with `Enum —` (e.g., `Enum — lifecycle states for a task`)
- [ ] One blank line after the CLASSES table

#### Per-class tables (one per class)
- [ ] Three columns: name, `Type / Returns`, `Description`
- [ ] Top-left header cell: class name in ALL CAPS WITH SPACES between words
  - `TaskScheduler` → `TASK SCHEDULER`
  - `TaskHandle` → `TASK HANDLE`
  - `RetryManager` → `RETRY MANAGER`
- [ ] Top-left header cell includes `([[#^N|details]])` link after the name
  - Format: `| TASK SCHEDULER ([[#^1\|details]]) | Type / Returns | Description |`
  - The `^N` block ID matches the H2 heading in Class Details (^1, ^2, ^3, etc.)
  - Each class gets a unique sequential block ID
- [ ] Properties listed FIRST — name in backticks (e.g., `\`queue\``)
- [ ] Bold separator row: `| **Methods** | | |` — text "Methods" in bold, columns 2-3 empty
- [ ] Methods listed AFTER the separator
- [ ] Method names linked to their METHOD DETAILS heading: `[[#full_signature|short_name]]`
  - Example: `[[#submit(task: Callable, deadline: datetime) -> TaskHandle\|submit(task, deadline)]]`
  - The link target is the full signature; the display text is the short call form
- [ ] Method return type in column 2, one-line description in column 3
- [ ] **Double blank lines** (two empty lines) between per-class tables

#### Enum tables (instead of per-class table, for enums)
- [ ] TWO columns only — no `Type / Returns` column
- [ ] Same ALL CAPS WITH SPACES header as class tables
- [ ] Same `([[#^N|details]])` link pattern
- [ ] Variant names in PLAIN TEXT — not backticks
- [ ] Include parameters in parentheses when variant carries data: `Pending(deadline)`
- [ ] Description column explains the variant
- [ ] **Double blank lines** between this table and adjacent tables

#### Spacing between overview zone tables
- [ ] One blank line between CLASSES table and first per-class table
- [ ] Two blank lines between each per-class/enum table

#### `# Class Details` heading
- [ ] This is an H1 heading: `# Class Details`
- [ ] THREE blank lines before it (separating from the last per-class table)

#### Per-class detail sections (H2)
- [ ] Format: `## TaskScheduler ^1` — PascalCase source name + space + block ID
- [ ] Block ID (`^1`) matches the `details` link in the corresponding per-class table
- [ ] Use exact PascalCase from source: `TaskScheduler`, NOT `Task Scheduler`, NOT `TASK SCHEDULER`
- [ ] TWO blank lines between class detail H2 sections
- [ ] Contains discussion subsections (H3) — design decisions, usage patterns, key concepts
- [ ] Code excerpts only when they clarify an interface that prose cannot

#### `### METHOD DETAILS` subsection
- [ ] ALL CAPS: `### METHOD DETAILS`
- [ ] THREE blank lines before it (separating from discussion above)
- [ ] Appears inside the class detail H2 section, not at top level

#### Individual method headings (H3)
- [ ] Full signature as heading: `### submit(task: Callable, deadline: datetime) -> TaskHandle`
- [ ] Body includes any of: **Args**, **Returns**, **Raises**, **Example** as needed
- [ ] **Args** is a bullet list with param name and description
- [ ] **Returns** describes the return value
- [ ] **Raises** lists exceptions
- [ ] Simple methods needing only a table row description may be omitted from METHOD DETAILS
- [ ] ONE blank line between method H3 sections

#### Simple classes
- [ ] Classes with no methods or minimal discussion: just a one-line description under their H2
- [ ] No METHOD DETAILS section needed for simple classes

#### Optional: Protocol section
- [ ] `## Protocol` heading
- [ ] Python Protocol or equivalent interface definition in a code block

#### Optional: See Also section
- [ ] `## See Also` heading
- [ ] Wiki-links to related module docs with brief relationship notes

#### Casing rules — summary
- [ ] CLASSES table entries: PascalCase source name → `[[#TaskScheduler]]`
- [ ] Per-class table header: ALL CAPS + spaces → `TASK SCHEDULER`
- [ ] Class Details H2: PascalCase source name → `## TaskScheduler ^1`
- [ ] Method signatures: exact source code casing
- [ ] METHOD DETAILS heading: ALL CAPS → `### METHOD DETAILS`

#### Spacing rules — summary
- [ ] H1 → brief paragraph: 1 blank line
- [ ] Brief → CLASSES table: 1 blank line
- [ ] CLASSES table → first per-class table: 1 blank line
- [ ] Between per-class tables: 2 blank lines
- [ ] Last per-class table → `# Class Details`: 3 blank lines
- [ ] Between class detail H2 sections: 2 blank lines
- [ ] Discussion → `### METHOD DETAILS`: 3 blank lines
- [ ] Between method H3 sections: 1 blank line

#### Table formatting rules
- [ ] Tables MUST have a blank line before them (or they won't render)
- [ ] Wiki-links inside tables: escape the pipe → `[[target\|alias]]` not `[[target|alias]]`

#### Proposed API convention (planning phase only)
- [ ] Mark each property, method, and type description with **(proposed)** inline
- [ ] Remove **(proposed)** once implementation matches the code

## 3.3 Update stale module docs
- [ ] For docs flagged stale-classes: update the CLASSES table to match current source
- [ ] For docs flagged stale-classes: add/remove per-class tables as needed
- [ ] For docs flagged stale-classes: add/remove Class Details H2 sections as needed
- [ ] For docs flagged stale-methods: update per-class table method/property rows
- [ ] For docs flagged stale-methods: update METHOD DETAILS signatures and descriptions
- [ ] After updating, re-verify against the full format checklist above

## 3.4 Create missing folder docs
For each source directory missing a folder doc:
- [ ] Create `{NAME} {FolderName}.md` in the corresponding `{NAME} Dev/{NAME} {folder}/` directory
- [ ] H1: `# {NAME} {FolderName}`
- [ ] 1-2 sentence description of what the subsystem does and why it exists
- [ ] MODULES table with two columns: `MODULES` and `Description`
- [ ] Each entry: `[[{NAME} ModuleA\|ModuleA]]` with one-line description
- [ ] If folder presents a coherent API: add `## Overview` with data flow, entry point, call sequence
- [ ] If folder is just organizational grouping: MODULES table only, no Overview needed
- [ ] Verify folder doc is linked from Dev dispatch and Files.md

## 3.5 Fix format errors
- [ ] For each format-error flagged in Phase 1.6, apply the specific fix
- [ ] Re-verify the corrected doc against the full format checklist


# Phase 4: Verify — MANDATORY after Phase 3

## 4.1 Rerun the script
- [ ] Run `python3 ~/.claude/skills/anchor/scripts/audit-docs.py <anchor-path> --verbose`
- [ ] Check findings count

## 4.2 If findings remain
- [ ] **Naming/location findings:** fix immediately — rename or move the file. No discussion needed.
- [ ] **Missing doc for a real module:** create the doc.
- [ ] **Missing doc for a trivial file:** tell the user, propose adding to `.anchor/audit-docs.yaml` exclusions. Wait for approval.
- [ ] Rerun the script after each round of fixes
- [ ] Repeat until findings = 0 or all remaining findings are user-approved exclusions

## 4.3 Final gate
- [ ] Script reports "Total findings: 0" (or all findings are documented exceptions)
- [ ] Post final result to stat

# Universal Rules

- [ ] Never create a module doc without first linking it from Dev dispatch AND Files.md
- [ ] Always read the CAB Module Doc reference example before writing — every time, not from memory
- [ ] Outdated docs are worse than no docs — delete if the doc cannot be kept current
- [ ] All files and folders carry the `{NAME}` prefix to avoid Obsidian namespace collisions
- [ ] Alignment in Files.md is based on display width, not raw markdown width
- [ ] Use Python to compute alignment when modifying Files.md tree lines
