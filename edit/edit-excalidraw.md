# edit-excalidraw — Excalidraw Diagrams

Create, update, and export Excalidraw diagrams (`.excalidraw` JSON files). Every change is opened in ExcalidrawZ so the user can see the result.

## Critical Rule: Always Re-Render After Changes

**Every time you create or update a `.excalidraw` file, you MUST open it in ExcalidrawZ so the user can see the result.** ExcalidrawZ does not auto-reload files — you must kill and reopen it:

```bash
pkill -x ExcalidrawZ 2>/dev/null; sleep 0.5
open -a ExcalidrawZ "/path/to/file.excalidraw"
```

This applies to:
- Creating a new diagram
- Editing any element in an existing diagram
- Any Write or Edit to a `.excalidraw` file

Never skip this step. The user cannot see your changes without it.

## Excalidraw File Format

Valid `.excalidraw` JSON:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [ ... ],
  "appState": {"gridSize": null, "viewBackgroundColor": "#ffffff"},
  "files": {}
}
```

## Export Workflow (SVG/PNG)

### Step 1: Convert to SVG and PNG

```bash
python3 ~/.claude/skills/edit/excalidraw_to_svg.py /path/to/file.excalidraw
```

Produces `.svg` and `.png` alongside the source file. If `rsvg-convert` is not installed, PNG is skipped (suggest `brew install librsvg`).

### Step 2: Open in ExcalidrawZ

```bash
pkill -x ExcalidrawZ 2>/dev/null; sleep 0.5
open -a ExcalidrawZ /path/to/file.excalidraw
```

### Step 3: Show in Finder

```bash
open "$(dirname /path/to/file.excalidraw)"
```

### Step 4: Insert into Google Slides (if URL provided)

```bash
python3 ~/.claude/skills/edit/insert_into_slides.py \
  /path/to/file.png \
  "https://docs.google.com/presentation/d/<id>/edit#slide=id.<slide_id>"
```

If the OAuth token is expired, the script will print an error. Use the Google Workspace MCP `google_oauth_get_auth_url` tool to get a fresh auth URL, open it for the user, then retry.

### Output

Report to the user:
- Path to `.excalidraw` file
- Path to `.svg` file
- Path to `.png` file (if converted)
- Google Slides URL (if inserted)
