# cab-tlc-scan — Sync the TLC Index

Scan for new TLCs and add them to the TLC index table.

## Step 1: Ensure HookAnchor Is Current

```bash
ha --rescan
```

## Step 2: Find New TLCs

```bash
cd "$(ha -p PC)" && python bin/scan_tlc.py delta
```

Optional: filter by date with `--since 2025-01-01`

The script outputs table rows ready to paste into TLC.md.

## Step 3: Add to TLC Index

New rows go to the **top table** (dated project list) in TLC.md, in reverse chronological order (newest first).

Location: `~/ob/kmr/SYS/Closet/Three Letter Codes/TLC/TLC.md`

### Table Format
```markdown
| DATE       | TLC      | FULL ANCHOR NAME | DESC                                |
| ---------- | -------- | ---------------- | ----------------------------------- |
| 2026-01-16 | [[ODC]]  | double-click     | macOS markdown file handler         |
```

## Step 4: Verify Descriptions

Descriptions come from the anchor marker file (the file matching the folder name):

```markdown
---
desc: Brief description of the project
---
(See [[TLC]])
```

Or inline: `desc:: Brief description`

The anchor marker file is authoritative. Update the TLC table if it disagrees.

## Rules

- **Never delete TLC rows** — only add or update
- **New entries → top table** — not the ROOT TLCs hierarchy table
- The ROOT TLCs hierarchy can be regenerated with `python bin/scan_tlc.py tree`
