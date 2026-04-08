# Module Docs

Build the file tree and module docs together. Create `{NAME} Files.md` and per-module documentation under `{NAME} Dev/`.

**MANDATORY: Before writing any module doc, read the [[CAB Module Doc]] reference example in full.** The reference example IS the spec — match it exactly. Do not improvise the format from memory.

## When to Use

After System Design is written. Run when the file structure and module interfaces need to be specified.

## Workflow

### 1. Read the Reference Example

Read `~/.claude/skills/CAB/cab-facets/CAB Module Doc.md` from top to bottom. The reference example at the top shows the exact format. The format specification below it explains every detail. Do this EVERY TIME you create module docs, not just the first time.

### 2. Build the Files Document

Create `{NAME} Files.md` following the CAB Files spec. List every file with one-line descriptions.

**Important:** The Files page is a monospace page (`cssclasses: monospace`), NOT a code block. Read the CAB Files spec before creating or updating.

### 3. Link FIRST, Write SECOND

Before writing ANY module doc content:
- Add its entry to `{NAME} Dev.md` dispatch table
- Add it to `{NAME} Files.md` in the correct location
- Do this for ALL module docs before writing any content

An unlinked module doc is invisible — no one will find it.

### 4. Create Module Docs

For each module, create a doc in `{NAME} Dev/` mirroring the source tree structure.

**Table formatting:** Tables MUST have a blank line before them or they won't render. When placing wiki-links with aliases inside tables, escape the pipe: `[[target\|alias]]` not `[[target|alias]]`. An unescaped `|` breaks the table column.

### 5. Verify Against Checklist

After writing each module doc, verify it against this checklist. Every item must pass.

**Structure checklist:**

- [ ] **CLASSES table** at the top — two columns: `CLASSES` and `Description`
- [ ] Each CLASSES entry uses `[[#PascalCaseName]]` wiki-link (source code class name, not spaced)
- [ ] Enums in CLASSES table prefixed with `Enum —` in description
- [ ] **Per-class table** for each class — header is **ALL CAPS WITH SPACES** (e.g., `TASK SCHEDULER`)
- [ ] Per-class table header has `([[#^N|details]])` link with block ID
- [ ] Per-class table has three columns: name, `Type / Returns`, `Description`
- [ ] Properties listed first in backticks, then `**Methods**` separator row, then methods
- [ ] Methods linked to METHOD DETAILS: `[[#full_signature|short_name]]`
- [ ] **Enum tables** use TWO columns (no Type/Returns) — variant names in plain text, not backticks
- [ ] **Double blank lines** between per-class tables
- [ ] **`# Class Details`** section with H1 (three blank lines before it)
- [ ] Each class gets `## ClassName ^N` heading (PascalCase, block ID matches table link)
- [ ] **`### METHOD DETAILS`** in ALL CAPS (three blank lines before it)
- [ ] Method headings use full signature: `### submit(task: Callable, deadline: datetime) -> TaskHandle`
- [ ] **Double blank lines** between class detail H2 sections

**Casing checklist:**

| Where | Casing |
|-------|--------|
| CLASSES table entries | PascalCase: `[[#TaskScheduler]]` |
| Per-class table header | ALL CAPS + spaces: `TASK SCHEDULER` |
| Class Details H2 | PascalCase: `## TaskScheduler ^1` |
| Method signatures | Exact source code |

### 6. Mark as Proposed

During planning, mark every property, method, class, and struct description with **(proposed)** inline. Remove **(proposed)** from each item once implementation matches the code.

### 7. Cross-Reference

Verify every module referenced in System Design appears in the Files doc, and every file in the Files doc has a corresponding module doc.
