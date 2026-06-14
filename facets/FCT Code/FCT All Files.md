---
description: the repo's complete source file tree, every file linked to its module doc (monospace)
---
# FCT All Files
The All Files facet — a fixed-width file-tree page linking every source file to its module doc.

| -[[FCT All Files]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Code]] → [FCT All Files](hook://p/FCT%20All%20Files)<br>: the repo's complete source file tree, every file linked to its module doc (monospace) |
| --- | --- |
| Related | [[FCT Interface]],  [[FCT Module]],  [[FCT Architecture]],  [[FCT Dev]],   |

**TLDR** — A `{NAME} Files.md` page renders the full repo tree in monospace (via `cssclasses: monospace`) with each source file as a wiki-link to its module doc. Cardinality: one per anchor. The no-code-fence rule is load-bearing: wrapping the tree in triple-backticks kills wiki-links. Filenames ARE the links; the `→ [[doc]]` arrow form is reserved for non-source files.

**Cardinality: one per anchor** — each code anchor has exactly one Files page.

**Location:** `{NAME} Docs/{NAME} Dev/{NAME} Files.md`

**Working example (copy this, not the snippet below):** `~/.claude/skills/CAE/CAE Docs/CAE Dev/CAE Files.md`

## Critical — Do Not Wrap the Tree in a Code Fence

The body of this file is **plain markdown**, not a code block. The `cssclasses: monospace` frontmatter is what makes the page render in fixed-width font — not triple-backticks. If you wrap the tree in ```` ``` ```` fences:

- Wiki-links inside become literal text (not clickable)
- The whole page becomes a dead zone
- This is the most common mistake; `/audit structure` specifically looks for it

There is **no code fence** around the tree. The file looks like this:

```
---
cssclasses:
  - monospace
description: ...
---

# {NAME} Files

| -[[{NAME} Files]]- |  |
| --- | --- |
| --- | |

File tree for the {repo-name} repository with descriptions.


{repo-name}/
├── Cargo.toml                         Workspace config + dependencies
├── [[FCT Claude|CLAUDE.md]]                          Claude Code configuration
│
├── src/                               Library crate
│   ├── [[{NAME} Lib|lib.rs]]                         Crate root
│   └── [[{NAME} Scheduler|scheduler.rs]]              Priority queue engine
│
└── tests/                             Integration tests
    └── scheduler.rs                   Scheduler integration tests
```

The ``` ``` fences above are showing you the *content* of the file. **Your file does not start or end with triple-backticks.** It starts with `---` (YAML frontmatter opener) and ends with the last tree line.

---



# Format Specification

## Structure
Every Files page has:
1. Frontmatter: `cssclasses: monospace` — renders the entire page in fixed-width font
2. H1 heading: `# {NAME} Files`
-[[{NAME} Files]]- \| \|` + standard separator)
4. Description line: "File tree for the {repo-name} repository with descriptions."
5. Two blank lines before the tree
6. Tree starting with `{repo-name}/`

The dispatch table is a markdown table — it still renders correctly under `cssclasses: monospace` and doesn't conflict with the no-code-fence rule (the tree is what must not be fenced, not the dispatch table).

## Tree Format
- One line per file or directory
- Box-drawing characters for structure (`├──`, `└──`, `│`)
- Blank lines with `│` continuation to separate logical groups
- Directories end with `/` and may have descriptions
- See `/md file-tree` for full box-drawing and indentation rules

## Linking — Filenames ARE the Links

Every source file and directory that has a module doc is linked by making the filename itself a wiki-link. The filename in the tree doubles as the navigation link — there is no separate arrow or reference. This is the primary linking pattern in the Files tree.

**Format:** `[[{NAME} DocPage|filename.ext]]` — renders as `filename.ext` but links to the module doc.

| What | Format | Renders as |
|------|--------|------------|
| Source file | `[[CAE Scheduler\|scheduler.rs]]` | `scheduler.rs` (links to CAE Scheduler doc) |
| Directory | `[[CAE engine\|engine/]]` | `engine/` (links to module aggregator doc) |
| Standard file | `[[CAB Claude\|CLAUDE.md]]` | `CLAUDE.md` (links to CAB spec) |

Files without a module doc (tests, config files, etc.) use plain filenames — no link.

**Do NOT use `→ [[doc]]` arrows for source file doc links.** The `→` arrow pattern is only for non-source files that reference an external spec (e.g., `justfile → [[CAB Repository Structure]]`). Source files use the filename-as-link pattern instead.

## Row 1 — Repo Root

The first tree line is the repo root directory (`repo-name/`). Do **not** add descriptor text like "repo root" — the reader knows which line is row 1. Row 1's description slot goes directly to `[[{NAME} Interface]]`:

```
repo-name/                                [[{NAME} Interface]]
```

`/audit docs` flags `repo root` / `repo route` text on row 1 as **files-row1-redundant**.

The Interface (see [[FCT Interface]]) is the **required top-level human-authored layer contract** for the anchor — every code anchor has one. Files row 1 links to it so a reader entering the file tree starts at the layer contract, not the deepest implementation file.

## Alignment

- **Every description starts at the same display-width column.** Pick a target (42 works well in practice; whatever fits the deepest `{tree-prefix}{filename}` position plus some breathing room) and make every line with a description hit that column exactly.
- Alignment is based on **rendered display width**, not raw markdown width. Wiki-links collapse: `[[CAE-Scheduler|scheduler.rs]]` is 30 chars in source but renders as `scheduler.rs` (12). Pad spaces in the source so that *rendered* descriptions align.
- `/audit docs` flags inconsistent alignment (range > 2 chars across rows) as **files-misaligned**. Fix with a Python reformat pass — see audit-docs § 1.7 for the snippet.
- Tree lines *without* descriptions (single-word directories like `├── .git/`) don't participate in alignment — they're fine as-is.

## Maintenance
Update the Files page when the repository structure changes significantly — new modules added, packages reorganized, or major files renamed. It does not need to track every individual file change.

# RULESET R-all-files
include::
where:: file: **/Docs/**/*Files.md, **/*Dev/**/*Files.md
description:: Rules every `{NAME} Files.md` instance must satisfy — frontmatter, no-code-fence, tree structure, and link format.

### RULE R-all-files-01 — cssclasses monospace in frontmatter (checked)
The instance's YAML frontmatter contains `cssclasses: [monospace]` or a `cssclasses:` block with `monospace` as an entry.
**Check pattern:** frontmatter block contains `cssclasses` with a `monospace` entry.
**Why:** `cssclasses: monospace` is what renders the page in fixed-width font; without it the file tree does not align correctly.

### RULE R-all-files-02 — Tree not wrapped in a code fence (checked)
The file tree (lines containing box-drawing characters `├──`, `└──`, `│`) is plain markdown, not inside a triple-backtick fence.
**Check pattern:** no ` ``` ` fence delimiter appears before tree lines containing `├──` or `└──`.
**Why:** wiki-links inside a code fence become inert text; fencing the tree kills all module-doc navigation.

### RULE R-all-files-03 — Filename-as-link pattern for source files (sampled)
Each source file that has a module doc uses `[[{NAME} DocPage\|filename.ext]]` so the filename renders but links to the doc. The `→ [[doc]]` arrow form is used only for non-source files referencing an external spec.
**Check pattern:** source-file links follow `[[Page\|filename.ext]]`; `→ [[...]]` does not appear on source-file lines.
**Why:** the filename-as-link pattern keeps the tree readable while preserving navigation; mixing the arrow form on source files breaks the visual convention.

### RULE R-all-files-04 — Description column alignment is consistent (sampled)
All tree lines that carry a description start their description text at the same rendered display width (within ±2 characters). Alignment is based on rendered width (wiki-links collapse to the alias), not raw source width.
**Check pattern:** sampled description-column offsets are within 2 characters of each other across the tree.
**Why:** the monospace page is only visually useful when columns align; misaligned rows look broken and are flagged `files-misaligned` by `/audit docs`.

# BRIEF

- **This is the facet spec for `{NAME} Files.md`** — it defines the format every anchor's Files page must follow; instances (CAE Files, etc.) cite this page as authority.
- **Scope is the format rule itself**, not any particular anchor's tree — never paste a specific anchor's file tree here; the working example lives at the linked `CAE Files.md` path and is the canonical copy-from source.
- **The no-code-fence rule is load-bearing** — the `cssclasses: monospace` frontmatter renders the page in fixed-width; wrapping the tree in triple-backticks kills wiki-links and is `/audit structure`'s most-flagged mistake. Keep the § Critical section prominent.
- **Filename-as-link is the linking pattern** — `[[Doc Page|filename.ext]]`; the `→ [[doc]]` arrow form is reserved for non-source files referencing an external spec, never source-file doc links.
- **Row 1 is the repo root linking to `{NAME} Interface`** — no "repo root" descriptor text; `/audit docs` flags it as `files-row1-redundant`.
- **Alignment is by rendered display width**, not raw markdown width — wiki-links collapse on render; pad source spaces so rendered descriptions hit the same column.
- **Audit-rule names belong here** (`files-row1-redundant`, `files-misaligned`) — they are the contract between this spec and `/audit docs`; renaming them silently breaks the audit.
