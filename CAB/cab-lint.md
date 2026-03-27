# cab-lint — Lint an Anchor

Static analysis of an anchor's structure and contents against its CAB type rules. Checks structural conformance, missing files, dispatch tables, and module doc coverage.

**User docs:** [[LINT User Docs/cab-lint-rules\|Rules Reference]] — complete list of all lint rules by level

## Invocation

```bash
/cab lint                          # lint current anchor at level 5
/cab lint 3                        # lint at level 3 (lighter)
/cab lint 8                        # lint at level 8 (thorough)
/cab lint <path>                   # lint a specific anchor
```

## What It Does

1. **Run the lint script** on the anchor
2. **Read the output** — warnings about missing/stale/incorrect items
3. **For each warning**, decide: fix the doc, or add an exception
4. **Fix** by editing the relevant markdown file (module doc, dispatch table, anchor page)
5. **Exception** by adding a row to `.skl/lint/exceptions.md` if the warning is noise
6. **Re-run** to confirm all warnings are resolved or excepted

## Running the Script

```bash
python3 ~/ob/kmr/SYS/Bespoke/Skill\ Agent/LINT/cab-lint.py <anchor-path> [--level 5] [--verbose] [--show-exceptions]
```

The script lives at `~/ob/kmr/SYS/Bespoke/Skill Agent/LINT/cab-lint.py`. It requires `tree-sitter-analyzer` (`pip install tree-sitter-analyzer`) for source code parsing at level 5+. Tests and private items are excluded by default.

## Lint Levels

| Level | Name | What it checks |
|-------|------|----------------|
| 1 | Bare Bones | Marker file, anchor page exist |
| 2 | Core | CLAUDE.md, Code symlink, README.md, SKILL.md (type-specific) |
| 3 | Structure | Docs folder, Plan folder, Dev folder |
| 4 | Content | `description:` in frontmatter, breadcrumb, dispatch table present |
| 5 | **Default** | Module doc comparison — classes, methods, fields match source code |
| 6 | Links | All markdown files reachable from dispatch tree |
| 7 | Cross-ref | Wiki-links resolve, no broken internal links |
| 8 | Naming | `{NAME}` prefix on all files/folders |
| 9 | Pedantic | Spacing rules, TOC format, column alignment |

## Agent Workflow at Level 5

Level 5 is the default. It scans the source code and compares it to module docs. The agent's job:

**Do not ask the user about priority or ordering.** Fix all warnings — choose whatever order makes sense (e.g., exceptions first, then doc fixes by module). The user wants everything resolved; the order doesn't matter.

### For `class-undocumented` warnings
A class exists in source but has no entry in a module doc.
- **Fix**: Add the class to the appropriate module doc's CLASSES table and create a per-class table with its fields and methods. Follow [[CAB Module Doc]] format.
- **Exception**: If the class is private/internal and documenting it adds noise (e.g., small enum used only internally), add an exception with reason.

### For `method-undocumented` warnings
A method exists in source but isn't in the module doc's per-class table.
- **Fix**: Add the method to the class's per-class table in the Methods section.
- **Exception**: If the method is a trivial accessor/getter/setter, or a private implementation detail, add an exception.

### For `enum-undocumented` warnings
An enum exists in source but has no entry in a module doc.
- **Fix**: Add the enum to the CLASSES table (with `Enum —` prefix in description) and create a two-column enum table listing its variants. See [[CAB Module Doc]] for the enum table format.
- **Exception**: If the enum is a trivial internal state (e.g., `LoadingState { Loading, Loaded, Error }`), add an exception.

### For `field-undocumented` warnings
A field exists in source but isn't in the module doc's per-class table.
- **Fix**: Add the field to the class's per-class table in the properties section.
- **Exception**: Rarely — fields are usually worth documenting.

### For `class-stale-doc` / `method-stale-doc` / `field-stale-doc` warnings
Something is in the doc but no longer in source.
- **Fix**: Remove the stale entry from the module doc.
- **Exception**: Never — stale docs should always be cleaned up.

### For `no-module-docs` or `source-no-module-doc` warnings
Source files exist but no module docs in Dev folder.
- **Fix**: Create module docs following [[CAB Module Doc]] format. Remember the **Linking Rule**: add to Dev dispatch table and Files FIRST, then write the doc.
- **For test files**: Use the test module doc format instead of the standard module doc format:

```markdown
# {NAME} {Module} Tests

{What's being tested and the approach.}

| SCAFFOLDS            | Description                                    |
| -------------------- | ---------------------------------------------- |
| [[#KitchenSink]]     | Full system with realistic data                |

| TEST AREAS                    | Category | Level | Description                    |
| ----------------------------- | -------- | ----- | ------------------------------ |
| Happy path — core loop        | pr       | 2     | End-to-end main flow           |
| Malformed config              | pr       | 3     | Missing fields, bad types      |
| Concurrent access             | demand   | 6     | Race condition on shared state |
```

SCAFFOLDS table lists test fixtures. TEST AREAS table lists what's tested with category (snap/pr/demand/witness) and level (1-9). See [[code-test]] for full details on test categories and levels.

## Exceptions File

Located at `.skl/lint/exceptions.md` in the anchor. Sorted by module path, then target.

```markdown
# Lint Exceptions

| Module | Target | Rule | Reason |
|--------|--------|------|--------|
| *.js | | file-no-module-doc | Config files, not API |
| *.swift | *applicationShould* | method-undocumented | AppKit delegate boilerplate |
| build.rs | | file-no-module-doc | Build script |
| src/bin/* | | class-undocumented | Binary entry points |
| src/ui/popup.rs | WindowSizeMode | class-undocumented | Private enum, internal only |
| tests/* | | class-undocumented | Test files |
```

Both Module and Target columns support **glob patterns** (`*`, `?`). Prefer glob exceptions over per-item exceptions when a whole category should be excluded — this avoids cluttering the file with dozens of individual entries.

### When to add an exception
- The item is **private/internal** and documenting it would clutter the module doc
- The item is a **trivial accessor** (get_x/set_x) that adds no information beyond the field itself
- The item is in a **non-API file** (build scripts, config files, test helpers)
- Documenting it would make the module doc **less useful** for someone trying to understand the code
- A **whole category** of items should be excluded — use a glob pattern

### When NOT to add an exception
- The item is **public API** — always document
- The item has **non-obvious behavior** — always document even if private
- The doc is **stale** — fix it, don't except it

### ⚠️ No blanket rule suppressions

**NEVER** create exceptions with `*` module AND empty target for content rules. These are rejected by the tool:

```markdown
| * | | field-undocumented | ← REJECTED — blanket suppression |
| * | | method-stale-doc   | ← REJECTED — hides real problems |
```

Every exception must specify either a **Module path** (which source file) or a **Target** (which class/method). This forces case-by-case judgment instead of sweeping entire categories under the rug.
- The doc is **stale** — fix it, don't except it

## Output

The script outputs a markdown report:

```
## CAB Lint: Hook Anchor
Type: Code Anchor | Level: 5

### FAIL (1)
  ✗ marker-file — Missing: HookAnchor.md

### CONCERNS (3)
  ⚠ method-undocumented — Method 'SysData.reload_commands' in source but not in module doc
  ...

### PASS (10)
  ✓ anchor-page — Anchor page: HA.md
  ...

**Result: CONCERNS**
(6 suppressed by exceptions)
```

Exit codes: 0 = PASS, 1 = CONCERNS, 2 = FAIL.
