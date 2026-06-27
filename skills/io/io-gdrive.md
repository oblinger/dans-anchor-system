# /io gdrive — Google Drive

## WEBSHARE upload convention (date-prefix — REQUIRED)

The WEBSHARE public folder is id `1asHv4t89nzMF0nCyz0uL6sneQ4mR2d5z` (link-viewable, not discoverable — share anyone/reader, allowFileDiscovery=false).

**Every file placed in WEBSHARE must have its Drive name begin with `YYYY-MM-DD ` (ISO date, then a space, then the title).** Pick the date as:

1. **Source date first** — if the source file carries a date (a `YYYY-MM-DD` prefix in its filename, an embedded `(YYYY-MM-DD)`, or an explicit "as of" date in the doc), reuse that exact date.
2. **Upload date otherwise** — if the source has no date, use today's date (the day it goes into WEBSHARE).

Strip any redundant trailing date from the title once it's been moved to the front (e.g. `Foo Survey (2026-06-17)` → `2026-06-17 Foo Survey`). This applies to uploads *and* to renaming anything already in the folder that predates this convention.

## Method 1: gsa CLI (preferred)

```bash
gsa search sheets [query]     # Find spreadsheets
gsa search slides [query]     # Find presentations
gsa search docs   [query]     # Find documents
```

Auth: `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`

**Note:** gsa search is type-specific. For a general Drive search, use the Drive API directly (Method 2).

## Method 2: Drive API (Python)

For general file search, upload, download. Use the token refresh pattern from `io-gmail-api.md`.

```python
# Search all files
url = "https://www.googleapis.com/drive/v3/files?q=name+contains+'report'&fields=files(id,name,mimeType)"

# Upload a file (auto-converts to Google format)
metadata = {"name": "My File", "mimeType": "application/vnd.google-apps.spreadsheet"}
# POST to https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart
```

## Method 3: rclone (bulk sync)

For syncing folders, backup, bulk download.

```bash
rclone ls gdrive:                    # List all files
rclone copy gdrive:folder/ ./local/  # Download folder
rclone sync ./local/ gdrive:folder/  # Upload folder
```

## Method 4: browser (ctrl surf)

```bash
ctrl surf "https://drive.google.com"
```
