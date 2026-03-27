---
name: io
description: >
  External system I/O — read from and write to external applications and services.
  Google Workspace: Sheets, Slides, Drive search, Google Docs.
  Cloud storage: Dropbox, iCloud.
  Productivity: Notion, Obsidian plugins, Apple Notes.
  Web: GitHub, websites, APIs.
  File formats: CSV, Excel, PDF, JSON, YAML.
  Email: read and search via Apple Mail (no OAuth needed).
  Use when the user says: "put this in sheets", "export to notion", "save to dropbox",
  "import from google docs", "read the spreadsheet", "update the slides",
  "upload to drive", "sync with notion", "export as PDF", "read my email",
  "search mail for", "find that email from".
  Subcommands: /io sheets, /io slides, /io docs, /io drive, /io notion, /io dropbox, /io export, /io import.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
user_invocable: true
---

# IO — External System I/O

Read from and write to external applications and services. The gateway between the local vault/repo and the outside world.

## Actions

| Usage | File | Description |
|-------|------|-------------|
| `/io sheets` | [[io-sheets]] | Read/write Google Sheets via gsa CLI |
| `/io slides` | [[io-slides]] | Read/write Google Slides via gsa CLI |
| `/io docs` | [[io-docs]] | Read/write Google Docs via gsa CLI |
| `/io drive` | [[io-drive]] | Search Google Drive |
| `/io notion` | (TBD) | Read/write Notion pages and databases |
| `/io dropbox` | (TBD) | Sync files with Dropbox |
| `/io email` | [[io-email]] | Read and search email via Apple Mail (no OAuth needed) |
| `/io sync` | [[io-sync]] | Sync files with Google Drive, Dropbox via rclone |
| `/io export` | (TBD) | Export to PDF, Excel, CSV |
| `/io import` | (TBD) | Import from external formats |

## Google Workspace (via gsa CLI)

The `gsa` command handles Google Sheets, Slides, and Drive. Auth uses existing OAuth credentials at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`.

```bash
gsa sheets read <id> [range]       # Read cells as JSON
gsa sheets write <id> <range> <json>  # Write cells
gsa sheets append <id> <range> <json> # Append rows
gsa sheets info <id>               # Sheet metadata
gsa slides read <id>               # Extract all text
gsa slides info <id>               # Presentation metadata
gsa search sheets [query]          # Find spreadsheets
gsa search slides [query]          # Find presentations
```

IDs accept full Google URLs or bare document IDs.

## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file and execute its workflow
4. If no argument, show the Actions table above
