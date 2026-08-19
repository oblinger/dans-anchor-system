# /io gdrive — Google Drive
Access card for Google Drive — ranked methods for search, upload, and download, plus the conventions (GShare naming, multi-account `/u/N/` selection) that govern them.

## GShare upload convention (date-prefix — REQUIRED)

The share folder is **`Oblio/GShare`**, id `1asHv4t89nzMF0nCyz0uL6sneQ4mR2d5z` — renamed from `WEBSHARE` on 2026-08-19, same id. **The folder is private (owner-only) and must stay that way**; access is granted per FILE (`anyone`/`reader`/`allowFileDiscovery=false`). Sharing the folder would grant permission to LIST it, and an inherited permission cannot be removed from a child — so a shared folder would expose every document as one browsable index. See the `gshare` skill § Decisions.

**Every file placed in GShare must have its Drive name begin with `YYYY-MM-DD ` (ISO date, then a space, then the title).** Pick the date as:

1. **Source date first** — if the source file carries a date (a `YYYY-MM-DD` prefix in its filename, an embedded `(YYYY-MM-DD)`, or an explicit "as of" date in the doc), reuse that exact date.
2. **Upload date otherwise** — if the source has no date, use today's date (the day it goes into GShare).

Strip any redundant trailing date from the title once it's been moved to the front (e.g. `Foo Survey (2026-06-17)` → `2026-06-17 Foo Survey`). This applies to uploads *and* to renaming anything already in the folder that predates this convention.

## Selecting which Google account (`/u/N/` in the URL)

When a browser or session is signed into more than one Google account, the account used is chosen by the **`/u/N/` index in the URL path** — `https://drive.google.com/drive/u/0/…`, `…/u/1/…`, and so on (the same `/u/N/` segment also works for Docs, Sheets, and Slides URLs). `N` is the account's **position in that browser's sign-in list, 0-based**, assigned by login order. It is **per-browser, not global** — the same account can be `/u/0` in one browser and `/u/2` in another — and it can **shift** when accounts are added or removed. So to act as a specific account reliably, **put its index in the URL** rather than trusting whichever account the page opens with, and **detect the right index** by loading `/drive/u/0/`, `/u/1/`, … and reading back the signed-in email before you rely on it.

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
