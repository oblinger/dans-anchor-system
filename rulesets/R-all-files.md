# RULESET R-all-files
include::
where:: `file: **/Docs/**/*Files.md, **/*Dev/**/*Files.md`
description:: Rules every `{slug} Files.md` instance must satisfy — frontmatter, no-code-fence, tree structure, and link format.

### RULE R-all-files-01 — cssclasses monospace in frontmatter (checked)
The instance's YAML frontmatter contains `cssclasses: [monospace]` or a `cssclasses:` block with `monospace` as an entry.
**Check pattern:** frontmatter block contains `cssclasses` with a `monospace` entry.
**Why:** `cssclasses: monospace` is what renders the page in fixed-width font; without it the file tree does not align correctly.

### RULE R-all-files-02 — Tree not wrapped in a code fence (checked)
The file tree (lines containing box-drawing characters `├──`, `└──`, `│`) is plain markdown, not inside a triple-backtick fence.
**Check pattern:** no ` ``` ` fence delimiter appears before tree lines containing `├──` or `└──`.
**Why:** wiki-links inside a code fence become inert text; fencing the tree kills all module-doc navigation.

### RULE R-all-files-03 — Filename-as-link pattern for source files (sampled)
Each source file that has a module doc uses `[[{slug} DocPage\|filename.ext]]` so the filename renders but links to the doc. The `→ [[doc]]` arrow form is used only for non-source files referencing an external spec.
**Check pattern:** source-file links follow `[[Page\|filename.ext]]`; `→ [[...]]` does not appear on source-file lines.
**Why:** the filename-as-link pattern keeps the tree readable while preserving navigation; mixing the arrow form on source files breaks the visual convention.

### RULE R-all-files-04 — Description column alignment is consistent (sampled)
All tree lines that carry a description start their description text at the same rendered display width (within ±2 characters). Alignment is based on rendered width (wiki-links collapse to the alias), not raw source width.
**Check pattern:** sampled description-column offsets are within 2 characters of each other across the tree.
**Why:** the monospace page is only visually useful when columns align; misaligned rows look broken and are flagged `files-misaligned` by `/audit docs`.
