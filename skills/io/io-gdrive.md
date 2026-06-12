# /io gdrive — Google Drive

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
