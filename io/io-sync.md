# Sync — File Sync with External Storage

Sync files between a local anchor folder and an external storage service (Google Drive, Dropbox, etc.) using rclone.

## Setup (one-time)

### 1. Configure rclone remote

```bash
rclone config
```

Follow prompts to create a remote. Use rclone's built-in client ID (default) for Google Drive to avoid the 7-day token expiry.

Common remote names:
- `gdrive` — personal Google Drive
- `gdrive-work` — work Google Workspace account
- `dropbox` — Dropbox

### 2. Verify connection

```bash
rclone lsd gdrive:/            # list top-level folders
rclone ls gdrive:/Projects/    # list files in a folder
```

## Actions

### Push (local → remote)

Copy local files to remote storage:

```bash
rclone sync <local-path> <remote>:<remote-path> --dry-run   # preview
rclone sync <local-path> <remote>:<remote-path>              # execute
```

### Pull (remote → local)

Copy remote files to local:

```bash
rclone sync <remote>:<remote-path> <local-path> --dry-run
rclone sync <remote>:<remote-path> <local-path>
```

### Bisync (bidirectional)

```bash
rclone bisync <local-path> <remote>:<remote-path> --resync   # first time only
rclone bisync <local-path> <remote>:<remote-path>             # subsequent runs
```

## Key Questions for Any Sync Operation

Before setting up sync, answer:

| Question | Options |
|----------|---------|
| **Which remote?** | gdrive, gdrive-work, dropbox |
| **Which direction?** | push (local→remote), pull (remote→local), bisync |
| **Which files?** | Entire anchor, just Docs/, specific files |
| **Exclude?** | .skl/, CLAUDE.md, .git/, build artifacts |
| **One-time or standing?** | One-time copy vs recurring sync |
| **Format conversion?** | Google Docs → docx, Sheets → xlsx (default) |

## Per-Anchor Sync Config

For standing relationships, create `.skl/sync/config.yaml` in the anchor:

```yaml
remote: gdrive
folder: /Projects/{Anchor Name}
direction: push
include:
  - "{NAME} Docs/**"
  - "{NAME}.md"
exclude:
  - ".skl/**"
  - "CLAUDE.md"
  - ".git/**"
  - "Code/**"
```

Then sync with:
```bash
rclone sync . <remote>:<folder> --include-from .skl/sync/include.txt --exclude-from .skl/sync/exclude.txt
```

## Common Patterns

### Push anchor planning docs to team Drive

```bash
rclone sync "./SVW Docs" gdrive:"/Projects/Northwind Workflow/Docs" \
  --exclude "CLAUDE.md" --exclude ".skl/**"
```

### Pull team changes back

```bash
rclone sync gdrive:"/Projects/Northwind Workflow/Docs" "./SVW Docs" --dry-run
# Review, then remove --dry-run
```

### Export Google Sheets as CSV locally

```bash
rclone copy gdrive:"/Spreadsheets/data.xlsx" ./data/ --drive-export-formats csv
```

## Notes

- Always use `--dry-run` first for sync operations
- `rclone sync` is destructive — it makes the destination match the source (deletes extra files). Use `rclone copy` to only add files without deleting.
- Google Docs/Sheets/Slides get converted to Office formats by default. Use `--drive-export-formats` to control.
- rclone stores config at `~/.config/rclone/rclone.conf`
