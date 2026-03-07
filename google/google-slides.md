# google-slides — Google Slides

Read and modify presentations using the `gsa` CLI tool.

## Commands

```bash
gsa slides read  <id>                    # Extract all text from slides
gsa slides info  <id>                    # Presentation metadata
gsa slides add-slide <id> [layout]       # Add a blank slide
gsa slides update-text <id> <obj> <text> # Replace text in a shape
gsa search slides [query]                # Find presentations (newest first)
```

## IDs

The `<id>` argument accepts either:
- A full Google URL: `https://docs.google.com/presentation/d/1abc.../edit`
- A bare document ID: `1abc...`

## Examples

```bash
# Read all text from a presentation
gsa slides read 1abc...xyz

# Get slide metadata
gsa slides info 1abc...xyz

# Search for slides by name
gsa search slides "quarterly review"

# Add a blank slide
gsa slides add-slide 1abc...xyz

# Replace text in a shape
gsa slides update-text 1abc...xyz <object_id> "New text content"
```

## Inserting Images

To insert an image (e.g., an Excalidraw export) into a slide, use the script from the `/edit` skill:

```bash
python3 ~/.claude/skills/edit/insert_into_slides.py \
  /path/to/image.png \
  "https://docs.google.com/presentation/d/<id>/edit#slide=id.<slide_id>"
```
