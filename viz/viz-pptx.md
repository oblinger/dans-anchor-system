# /viz pptx — Custom slide layouts via python-pptx

Generate highly-custom slide-shaped layouts (single-slide PPTX) — used as a **fallback** when neither Mermaid nor Graphviz expresses the figure cleanly. Examples: custom annotated visualizations, multi-element compositions, mockups, before-vs-after panels.

## Tool

`python-pptx` Python library — installed via `pip3 install python-pptx`. Verify with `python3 -c "import pptx; print(pptx.__version__)"`.

## Source format

A Python script that programmatically builds the slide. Claude generates the script from a natural-language description.

## Usage

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.33)   # 16:9 widescreen
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout

# Add title text box
title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
tf = title_box.text_frame
tf.text = "Title"
tf.paragraphs[0].font.size = Pt(32)
tf.paragraphs[0].font.bold = True

# Add custom shapes / text / images as needed...

prs.save('/path/to/out.pptx')
```

Default output goes to `~/ob/data/MyDesk/{slug-from-prompt}-{YYYY-MM-DD-HHMM}.pptx` per the cross-cutting `/viz` default-location convention.

## PNG / PDF export

`python-pptx` writes only `.pptx`. To export PNG or PDF for embedding in markdown / docs, use LibreOffice headless:

```bash
# PNG (one image per slide)
libreoffice --headless --convert-to png input.pptx --outdir ~/ob/data/MyDesk/

# PDF
libreoffice --headless --convert-to pdf input.pptx --outdir ~/ob/data/MyDesk/
```

LibreOffice install (one-time, ~600 MB): `brew install --cask libreoffice`.

## When to use

Use `pptx` only when neither Mermaid nor Graphviz can produce the desired output:
- **Multi-element annotated layouts** — custom callouts, sidebar text, image + chart combinations.
- **Mockups and slide-shaped one-pagers**.
- **Compositions** that need pixel-level placement control.
- **Output is `.pptx`** — directly editable in PowerPoint / Keynote / Google Slides if user wants to refine.

For diagrams: prefer Mermaid (`/viz mermaid`) or Graphviz (`/viz dot`).
For data charts: prefer matplotlib (`/viz matplot`).

## Workflow

1. **Confirm pptx is the right tool** — is this genuinely a custom layout that the simpler tools can't express?
2. **Generate Python script** that builds the slide.
3. **Run** to produce `.pptx`.
4. **Optionally export** to PNG or PDF via LibreOffice.
5. **Print output path** for both source `.pptx` and any rendered PNG/PDF.

## Verification

```bash
python3 -c "
from pptx import Presentation
from pptx.util import Inches, Pt
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])
tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(2))
tb.text_frame.text = 'viz pptx smoke test — 2026-05-08'
tb.text_frame.paragraphs[0].font.size = Pt(36)
prs.save('/tmp/viz-pptx-test.pptx')
print('Saved: /tmp/viz-pptx-test.pptx')
"
open /tmp/viz-pptx-test.pptx
```
