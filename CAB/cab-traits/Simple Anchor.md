# Simple Anchor

Follows [[cab-base]] with these deltas:

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
