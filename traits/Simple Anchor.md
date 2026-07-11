# Simple Anchor

The minimal CAB trait for lightweight anchor identity — a single anchor page in an organized parent folder, with no `{slug} Docs/`, repo, `CLAUDE.md`, or Inbox unless another trait pulls them in.

Follows [[CAB Base]] with these deltas:

## When to Use

Quick reference pages, topic collections, notes that need an anchor identity but don't warrant a full project structure.

## Deltas from Base

- **Create `{slug} Docs/` only when another trait requires it**
- **Create repository only when another trait requires it** — no `.git/`, no `code:` key in `.anchor` by default
- **Create CLAUDE.md only when another trait requires it**
- **Create Inbox only when another trait requires it**
- Lives within a parent folder that's already organized

## Structure (reduced from base)

```
{Parent}/
├── {CAB Folder}/
│   ├── {CAB Folder}.md          marker file
│   └── {slug}.md                anchor page (content here)
```

If folder name = anchor name, a single `.md` file serves as both marker and content.

## Audit

Type-specific structure checks for Simple Anchors.

### Required files
- Anchor page `{slug}.md` with frontmatter

### Conditional structure
- Create `{slug} Docs/` folder only when another trait requires it (simple anchors are just the anchor page by default)
- Add a `code:` key to `.anchor` only when the anchor gains the `code` trait

# BRIEF

*(Maintainer note — cautions for whoever edits this trait spec. The normative spec is the body above; trait-general rules live in [[CAB Base]].)*

- **Trait contract, not a catalog** — edits here change what `/audit`, `/tidy`, `/create anchor`, and `/migrate` enforce; never list individual Simple-anchor instances (that's slug-index / Atlas / dispatch tables).
- **Inclusion test for a delta** — a bullet belongs under *Deltas from Base* only if it changes a Base requirement *for the Simple case specifically* (suppression of `{slug} Docs/`, repo, `CLAUDE.md`, Inbox); trait-general rules go in [[CAB Base]], cross-trait composition rules in the other trait's spec.
- **Conditional-creation phrasing is load-bearing** — preserve "Create X only when another trait requires it" verbatim so composition with `code`, `paper`, etc. stays mechanical; don't soften to "usually skipped" or "optional."
- **Structure block is normative** — the fenced tree under *Structure (reduced from base)* is the minimal layout an auditor accepts; adding lines expands the contract, remove only when Base changes correspondingly.
- **Cross-refs to sweep on rename** — [[CAB Base]] (parent), [[DAS Traits]] (dispatch), `/audit structure`, `/create anchor`, `/migrate`; don't rename this trait or its deltas in isolation.
