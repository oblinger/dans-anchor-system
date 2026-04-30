---
description: How to read from and write to external services — Google Workspace, email, file sync
---

# SKL IO Guide (Skill: [[io/SKILL]])

The IO skill is the gateway between the local system and external services. It covers Google Workspace (Sheets, Slides, Docs via the `gsa` CLI), email (read/search via Apple Mail AppleScript), and file sync (Google Drive and Dropbox via rclone).

The primary tool is `gsa` (Google Suite Access), which handles all Google Workspace operations through a single CLI. It uses OAuth credentials already stored locally — no server process needed. For email, the skill uses AppleScript to read and search Apple Mail directly, avoiding OAuth complexity entirely.

When you say things like "put this in sheets", "read the spreadsheet", "update the slides", or "search my email for", the agent routes to the appropriate IO action.

## Commands

| Command | Description |
|---------|-------------|
| `/io sheets` | Read/write Google Sheets via `gsa` |
| `/io slides` | Read/write Google Slides via `gsa` |
| `/io docs` | Read/write Google Docs via `gsa` |
| `/io drive` | Search Google Drive |
| `/io email` | Read and search email via Apple Mail |
| `/io sync` | Sync files with Google Drive or Dropbox via rclone |

## Key `gsa` Commands

```bash
gsa sheets read <id> [range]          # Read cells as JSON
gsa sheets write <id> <range> <json>  # Write cells
gsa sheets append <id> <range> <json> # Append rows
gsa sheets info <id>                  # Sheet metadata
gsa slides read <id>                  # Extract all text
gsa slides info <id>                  # Presentation metadata
gsa search sheets [query]             # Find spreadsheets
gsa search slides [query]             # Find presentations
```

## Key Concepts

- **`gsa` accepts URLs or IDs** — You can pass a full Google URL or just the document ID
- **Auth is pre-configured** — OAuth credentials at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`
- **Email uses AppleScript** — No OAuth setup needed for email; reads directly from Apple Mail
- **rclone for sync** — File sync with cloud storage uses rclone, which must be configured separately
- **Google Cloud project** — `oblio-claude-access` with Drive, Docs, Sheets, and Slides APIs enabled
