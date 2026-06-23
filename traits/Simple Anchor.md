# Simple Anchor

The minimal CAB trait for lightweight anchor identity — a single anchor page in an organized parent folder, with no `{NAME} Docs/`, repo, `CLAUDE.md`, or Inbox unless another trait pulls them in.

Follows [[CAB Base]] with these deltas:

## When to Use

Quick reference pages, topic collections, notes that need an anchor identity but don't warrant a full project structure.

## Deltas from Base

- **Create `{NAME} Docs/` only when another trait requires it**
- **Create repository only when another trait requires it** — no `.git/`, no `code:` key in `.anchor` by default
- **Create CLAUDE.md only when another trait requires it**
- **Create Inbox only when another trait requires it**
- Lives within a parent folder that's already organized

## Structure (reduced from base)

```
{Parent}/
├── {CAB Folder}/
│   ├── {CAB Folder}.md          marker file
│   └── {NAME}.md                anchor page (content here)
```

If folder name = anchor name, a single `.md` file serves as both marker and content.

## Audit

Type-specific structure checks for Simple Anchors.

### Required files
- Anchor page `{NAME}.md` with frontmatter

### Conditional structure
- Create `{NAME} Docs/` folder only when another trait requires it (simple anchors are just the anchor page by default)
- Add a `code:` key to `.anchor` only when the anchor gains the `code` trait

# BRIEF

- **This file is the Simple trait spec** — it defines what a Simple anchor IS as a CAB trait, expressed as deltas from [[CAB Base]]. Edits here change the trait contract that `/audit`, `/tidy`, `/create anchor`, and `/migrate` enforce.
- **NOT a catalog of simple-anchor instances** — don't list anchors that happen to be Simple here; instance discovery belongs to slug-index / Atlas / dispatch tables.
- **Inclusion test for a delta** — a bullet belongs in *Deltas from Base* only if it changes a Base requirement *for the Simple case specifically* (suppression of `{NAME} Docs/`, repo, `CLAUDE.md`, Inbox). Trait-general rules go in [[CAB Base]]; cross-trait composition rules belong in the relevant other trait spec, not here.
- **Conditional-creation phrasing is load-bearing** — "Create X only when another trait requires it" is the Simple-trait pattern; preserve that exact phrasing so composition with `code`, `paper`, etc. stays mechanical. Don't soften to "usually skipped" or "optional."
- **Structure block is normative** — the fenced tree under *Structure (reduced from base)* is the minimal layout an auditor accepts. Adding lines there expands the contract; remove only when Base changes correspondingly.
- **Cross-references to keep aligned** — [[CAB Base]] (parent), [[TRT]] (dispatch), `/audit structure`, `/create anchor`, `/migrate`. Renaming this trait or its deltas requires sweeping those surfaces; don't rename in isolation.
