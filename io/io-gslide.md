# /io gslide — Google Slides

Default scratch deck: `1n-au5qB2y_f-54eEGZ4p8njmdtsZYRgwTpAe-3xkT3k`

## Method 1: python-pptx → upload (preferred for creation)

Best for: flowcharts, diagrams, formatted layouts, anything with shapes.

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
shape.text = "Label"
prs.save('/tmp/output.pptx')
```

Then upload to Drive (auto-converts to Google Slides):
```python
metadata = {"name": "Title", "mimeType": "application/vnd.google-apps.presentation"}
# POST to https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart
```

**Limitation:** Each upload creates a new presentation. Cannot insert into existing decks.

## Method 2: gsa CLI (for reading and simple edits)

```bash
gsa slides read  <id>                    # Extract all text
gsa slides info  <id>                    # Metadata
gsa slides add-slide <id> [layout]       # Add a blank slide
gsa slides update-text <id> <obj> <text> # Replace text in shape
gsa search slides [query]                # Find presentations
```

## Method 3: Slides API (for complex edits to existing decks)

Direct batchUpdate requests — verbose but the only way to add shapes/connectors to existing presentations. Use Python with the token refresh pattern from `io-gmail-api.md`.

## Method 4: browser (ctrl surf)

```bash
ctrl surf "https://docs.google.com/presentation/d/<id>/edit"
```

## Inserting Images

```bash
python3 ~/.claude/skills/edit/insert_into_slides.py \
  /path/to/image.png \
  "https://docs.google.com/presentation/d/<id>/edit#slide=id.<slide_id>"
```
