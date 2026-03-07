# Simple Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Quick reference pages, topic collections, notes that need an anchor identity but don't warrant a full project structure.

## Deltas from Base

- **No `{NAME} Docs/`** — no planning docs subfolder
- **No repository** — no `.git/`, no `Code` symlink
- **No CLAUDE.md**
- **No Inbox**
- Lives within a parent folder that's already version-controlled

## Structure (reduced from base)

```
{Parent}/
├── {CAB Folder}/
│   ├── {CAB Folder}.md          marker file
│   └── {NAME}.md                   anchor page (content here)
```

If folder name = anchor name, a single `.md` file serves as both marker and content.
