# google-slides — Google Slides

Create and edit Google Slides presentations.

## Default Scratch Deck

When creating new slides without a specific target, use this deck:

**Scratch AI:** `1n-au5qB2y_f-54eEGZ4p8njmdtsZYRgwTpAe-3xkT3k`
https://docs.google.com/presentation/d/1n-au5qB2y_f-54eEGZ4p8njmdtsZYRgwTpAe-3xkT3k/edit

If the user provides a different presentation URL or ID, use that instead.

## Two Approaches

### 1. Google Slides API (gsa) — for simple edits

Best for: reading text, adding text to existing shapes, simple slides.

```bash
gsa slides read  <id>                    # Extract all text from slides
gsa slides info  <id>                    # Presentation metadata
gsa slides add-slide <id> [layout]       # Add a blank slide
gsa slides update-text <id> <obj> <text> # Replace text in a shape
gsa search slides [query]                # Find presentations (newest first)
```

### 2. python-pptx → upload — for creating slides with diagrams

Best for: flowcharts, diagrams, formatted layouts, anything with shapes and connectors. Much cleaner API than raw Slides JSON.

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR_TYPE
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
shape.text = "Label"
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x33, 0x66, 0xCC)
prs.save('/tmp/output.pptx')
```

Then upload to Drive (converts to Google Slides automatically):

```python
# Multipart upload with mimeType conversion
metadata = {"name": "Slide Title", "mimeType": "application/vnd.google-apps.presentation"}
# POST to https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart
```

**Limitation:** Each upload creates a new presentation. Cannot insert slides into an existing deck programmatically. For adding to existing decks, use the Slides API (approach 1).

## Inserting Images

To insert an image (e.g., an Excalidraw export) into a slide:

```bash
python3 ~/.claude/skills/edit/insert_into_slides.py \
  /path/to/image.png \
  "https://docs.google.com/presentation/d/<id>/edit#slide=id.<slide_id>"
```

## IDs

The `<id>` argument accepts either:
- A full Google URL: `https://docs.google.com/presentation/d/1abc.../edit`
- A bare document ID: `1abc...`
