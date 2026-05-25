---
name: slug-scan
description: Scan for new slugs and sync the index — Discovers anchors with slugs and updates the slug-index. Use when user says: "slug scan", "sync slugs".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Slug Scan — Sync the slug index

Scan for new slugs and add them to the slug index table.

## Step 1: Ensure HookAnchor Is Current

```bash
ha --rescan
```

## Step 2: Find New slugs

```bash
cd "$(ha -p PC)" && python bin/scan_rid.py delta
```

Optional: filter by date with `--since 2025-01-01`

The script outputs table rows ready to paste into slug.md.

## Step 3: Add to slug Index

New rows go to the **top table** (dated project list) in slug.md, in reverse chronological order (newest first).

Location: `~/ob/kmr/SYS/Closet/Tiny IDs/TID/TID.md`

### Table Format
```markdown
| DATE       | slug      | FULL ANCHOR NAME | DESC                                |
| ---------- | -------- | ---------------- | ----------------------------------- |
| 2026-01-16 | [[ODC]]  | double-click     | macOS markdown file handler         |
```

## Step 4: Verify Descriptions

Descriptions come from the anchor marker file (the file matching the folder name):

```markdown
---
desc: Brief description of the project
---
(See [[slug]])
```

Older anchors may use `desc::` inline — migrate to `description:` in frontmatter.

The anchor marker file is authoritative. Update the slug table if it disagrees.

## Rules

- **Never delete slug rows** — only add or update
- **New entries → top table** — not the ROOT slugs hierarchy table
- The ROOT slugs hierarchy can be regenerated with `python bin/scan_rid.py tree`
