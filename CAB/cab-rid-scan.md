# cab-rid-scan — Sync the RID Index

Scan for new RIDs and add them to the RID index table.

## Step 1: Ensure HookAnchor Is Current

```bash
ha --rescan
```

## Step 2: Find New RIDs

```bash
cd "$(ha -p PC)" && python bin/scan_rid.py delta
```

Optional: filter by date with `--since 2025-01-01`

The script outputs table rows ready to paste into RID.md.

## Step 3: Add to RID Index

New rows go to the **top table** (dated project list) in RID.md, in reverse chronological order (newest first).

Location: `~/ob/kmr/SYS/Closet/Tiny IDs/TID/TID.md`

### Table Format
```markdown
| DATE       | RID      | FULL ANCHOR NAME | DESC                                |
| ---------- | -------- | ---------------- | ----------------------------------- |
| 2026-01-16 | [[ODC]]  | double-click     | macOS markdown file handler         |
```

## Step 4: Verify Descriptions

Descriptions come from the anchor marker file (the file matching the folder name):

```markdown
---
desc: Brief description of the project
---
(See [[RID]])
```

Older anchors may use `desc::` inline — migrate to `description:` in frontmatter.

The anchor marker file is authoritative. Update the RID table if it disagrees.

## Rules

- **Never delete RID rows** — only add or update
- **New entries → top table** — not the ROOT RIDs hierarchy table
- The ROOT RIDs hierarchy can be regenerated with `python bin/scan_rid.py tree`
