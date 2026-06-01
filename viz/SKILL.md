---
name: viz
description: >
  Visual drafting — produce visual artifacts (charts, diagrams, mockups, slides).
  Use with an action argument: /viz excalidraw, /viz matplot. Triggered when user says
  "draw", "diagram", "mockup", "chart this", "plot data", "timeline chart", "excalidraw",
  or asks to create/update/export a visual artifact.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Viz — Visual Drafting

Produce visual artifacts. Use with a sub-action specifying the tool, since the choice of tool meaningfully affects the output.

## Actions

| Action | What it does | Output | Trigger phrases |
|---|---|---|---|
| `/viz excalidraw` | Create / update / export Excalidraw diagrams. Hand-drawn aesthetic, ideal for architecture diagrams, flow charts, system mockups. | `.excalidraw` source + `.svg` / `.png` export | "draw", "diagram", "mockup", "excalidraw", "export to svg", "paste into Google Slides" |
| `/viz matplot` | Generate matplotlib charts via `vizcharts.py` (10 chart types: timeline, multi-line, quadrant, scatter, rankings, comparison, stacked bar, donut, waterfall, hex shot). Tufte-grade static output. | `.png` (raster) · `.pdf` (vector) | "chart this", "plot the data", "timeline chart", "bar chart", "quadrant", "waterfall" |
| `/viz mermaid` | Mermaid diagrams from text (flow / sequence / gantt / class / state / ER). Renders natively in GitHub / GitLab / Notion / VS Code preview when embedded as a source block. | `.png` · `.pdf` · `.svg` · or markdown source block | "mermaid", "flow chart", "sequence diagram", "gantt", "state machine", "ER diagram" |
| `/viz dot` | Graphviz DOT — box/arrow graphs, system diagrams, decision trees, org charts, dependency graphs. Stronger layout engine than Mermaid for complex graphs. | `.png` · `.pdf` · `.svg` | "graphviz", "dot diagram", "system diagram", "org chart", "dependency graph", "decision tree" |
| `/viz pptx` (aliases: `/viz ppt`, `/viz powerpoint`) | python-pptx for highly-custom slide-shaped layouts. Fallback when neither Mermaid nor Graphviz expresses the figure cleanly — annotated visualizations, multi-element compositions, mockups. | `.pptx` (editable) · `.png` / `.pdf` via LibreOffice | "custom slide", "annotated layout", "multi-element composition", "mockup with text and image", "powerpoint", "ppt" |
| `/viz docx` | Convert a markdown file to editable `.docx` via pandoc + reference template. Use when you want to polish in Word/Pages before final delivery (export PDF yourself when satisfied). | `.docx` (editable) | "md to docx", "convert markdown to word", "Word doc from this markdown", "polish in Word", "make a docx" |
| `/viz pdf` | Convert a markdown file directly to PDF via pandoc + tectonic. Use for quick share, automated pipeline, or when default typography is fine. | `.pdf` | "md to pdf", "convert markdown to pdf", "quick pdf of this", "render this doc to pdf", "export to pdf" |


## Action files

| Usage | File | Description |
|-------|------|-------------|
| `/viz excalidraw` | [[viz-excalidraw]] | Create, update, and export Excalidraw diagrams |
| `/viz matplot`    | [[viz-matplot]]    | Generate matplotlib charts via vizcharts.py |
| `/viz mermaid`    | [[viz-mermaid]]    | Render Mermaid diagrams via mmdc |
| `/viz dot`        | [[viz-dot]]        | Render Graphviz DOT diagrams |
| `/viz pptx`       | [[viz-pptx]]       | Generate single-slide custom layouts via python-pptx |
| `/viz ppt`        | [[viz-pptx]]       | Alias for `/viz pptx` |
| `/viz powerpoint` | [[viz-pptx]]       | Alias for `/viz pptx` |
| `/viz docx`       | [[viz-docx]]       | Convert markdown to editable .docx via pandoc + reference template |
| `/viz pdf`        | [[viz-pdf]]        | Convert markdown to PDF via pandoc + tectonic |


## Scripts

| Script | Usage |
|---|---|
| `excalidraw_to_svg.py` | Convert .excalidraw to SVG/PNG. Run via `python3`. |
| `insert_into_slides.py` | Insert a generated image into a Google Slides deck. |


## Tool selection — when to use what

The user typically knows which tool they want. Each tool produces a visually distinct category of output — pick the tool that matches the artifact, not by trying to disambiguate user intent.

- **Hand-drawn / sketchy / architectural** → `/viz excalidraw`
- **Data-driven / quantitative / Tufte-grade chart** → `/viz matplot`
- **Flow / sequence / gantt / state diagram from text** → `/viz mermaid` (especially if the deliverable is markdown that will render natively in GitHub/Notion/VS Code)
- **Complex graph / org chart / dependency graph** → `/viz dot` (Graphviz layout engine)
- **Custom slide-shaped layout (annotations, multi-element composition, mockup)** → `/viz pptx` (fallback when nothing else fits)
- **Markdown → controlled deliverable (.docx for polishing in Word/Pages, then export PDF)** → `/viz docx`
- **Markdown → quick PDF (no polishing required)** → `/viz pdf`

If the user says something ambiguous, ask which tool — these aren't interchangeable.


## Capability matrix — viewing, clicking, round-trip editing

The trade-off table for picking a viz approach by its Obsidian + external capabilities. Rows are the approaches; columns are the capabilities. Use this when "the source must remain editable in Obsidian" or "must have clickable regions externally" is the constraint driving tool selection.

| Approach | Source format | Render output | Obsidian inline view | Obsidian clickable regions | External clickable regions | Round-trip editable from Obsidian |
|---|---|---|---|---|---|---|
| **mermaid** | ` ```mermaid ` code block in `.md` | SVG (auto by Obsidian); `.png` / `.pdf` / `.svg` (via mmdc) | **Yes** — Obsidian renders ` ```mermaid ` blocks natively (core feature) | Partial — `click` directive supports URLs; Obsidian wraps them as external links | **Yes** — GitHub / Notion / VS Code render natively; `click` directive supported on the web | **Yes** — source IS the markdown; edit the code block, render updates inline |
| **excalidraw** | `.excalidraw` JSON | `.svg` / `.png` (via `excalidraw_to_svg.py`) | **Yes** (with Excalidraw plugin) — `.excalidraw` files render as interactive canvas; SVG embeds render universally | **Yes** (with plugin) — embedded files / elements link to other vault pages; hyperlinks on shapes | **Yes** — SVG export wraps clickable elements as `<a>` tags; Excalidraw web has native interactivity | **Yes** (with plugin) — open the file in Obsidian, edit on canvas, save back to the same file |
| **dot** (Graphviz) | `.dot` text | `.svg` / `.png` / `.pdf` | Embed-only — Obsidian shows the rendered SVG/PNG (no native DOT renderer; plugins exist) | Partial — SVG `<a>` tags survive embed in some Obsidian configurations | **Yes** — DOT `URL=...` attributes on nodes render as SVG `<a>` regions on the web | No — edit the `.dot` text externally, re-render, re-embed |
| **matplot** | `.py` (matplotlib code) | `.png` (raster) · `.pdf` (vector) | **Yes** for PNG/PDF (Obsidian embeds raster + renders PDF inline) | No — raster has no clickable regions; matplotlib PDFs don't ship hyperlinks by default | No (PNG); limited for PDF | No — source is Python code, not editable from inside Obsidian |
| **pptx** | `.pptx` (binary, opens in PowerPoint / Keynote / Slides) | `.pptx` · `.png` / `.pdf` (via LibreOffice headless) | No — Obsidian does not render `.pptx`; click-to-open in external app | No | **Yes** — PowerPoint hyperlinks on shapes / text travel into the file | No — edit externally in PowerPoint / Keynote / Slides |
| **docx** | `.md` (canonical) → `.docx` via pandoc | `.docx` · (export `.pdf` from Word/Pages) | No — Obsidian does not render `.docx`; click-to-open in external app | No | **Yes** — Word / Pages / Google Docs hyperlinks travel into the file | Partial — re-edit the `.md` source in Obsidian, re-run `/viz docx` to regenerate (round-trips through the source, not the rendered doc) |
| **pdf** | `.md` (canonical) → `.pdf` via pandoc + tectonic | `.pdf` | **Yes** — `![[file.pdf]]` embeds render inline with paging | No — Obsidian's PDF viewer does not surface hyperlink interactivity (clicks navigate the PDF, not the link target) | **Yes** — PDF readers / browsers honor embedded hyperlinks | Same as docx — re-edit source `.md` in Obsidian, re-run `/viz pdf` |

**Reading the matrix:**

- **Round-trip editable from Obsidian** means: the user can open the artifact (or its source) in Obsidian, change it, save, and the rendered view updates without leaving the editor. Mermaid is the cleanest — the source IS the markdown. Excalidraw matches with the plugin. The rest require leaving Obsidian.
- **Obsidian clickable regions** means: an interactive region inside the embedded render that, when clicked, does something useful inside Obsidian (navigate to another note, open a URL). Mermaid `click` and Excalidraw embedded links work; PDF and raster images don't.
- **External clickable regions** means: when the rendered output is shared (web, GitHub, slides), the embedded interactivity travels with it.
- **"Source format"** is what you actually edit; **"render output"** is what's viewed.

**Decision shortcuts:**

- *Must be editable from inside Obsidian AND have inline view AND survive on GitHub* → **mermaid** is the only approach hitting all three out of the box.
- *Must have rich clickable regions on the web AND inside Obsidian* → **excalidraw** (with the plugin installed) is the strongest.
- *Don't care about Obsidian view; need a deliverable that opens in PowerPoint / Word with interactivity* → **pptx** or **docx**.
- *Tufte-grade quantitative chart with no interactivity needed* → **matplot**.

(This matrix is a living reference — extend rows as new approaches land, and tighten cells as the round-trip experiment results land from the parallel investigation.)


## Default output

When invoked without an explicit output path, all `/viz` actions land artifacts in **`~/ob/data/MyDesk/`** with filename pattern:

```
{slug-from-prompt}-{YYYY-MM-DD-HHMM}.{ext}
```

Examples:
- `arr-growth-apollo-2026-05-08-1543.png`
- `system-diagram-2026-05-08-1547.pdf`
- `quadrant-effort-impact-2026-05-08-1551.png`

If the user gives an explicit output path, honor it instead. The MyDesk default keeps generated artifacts findable across sessions instead of scattered through `/tmp/` or working dirs.

This convention applies retroactively — `/viz matplot` (which previously dropped to caller-specified paths) should also default to MyDesk when no path is given.


## Output formats

Every action supports a primary output format and one or more secondary formats. The skill should advertise the choice when invoked so the agent picks per use case.

| Tool | Primary | Vector option | Notes |
|---|---|---|---|
| `excalidraw` | `.excalidraw` source + `.svg` | `.svg` (native) · `.png` | Source is editable in Excalidraw web; SVG is small and infinitely scalable |
| `matplot` | `.png` | `.pdf` (vector) | `--pdf` flag for vector-quality embedding in print/PDF deliverables |
| `mermaid` | `.png` (1600×900 slide-grade) | `.pdf` · `.svg` · markdown source block | For markdown deliverables on GitHub/Notion/VS Code, prefer source-block embedding over PNG |
| `dot` | `.png` | `.pdf` · `.svg` | SVG for crisp scaling on web / docs |
| `pptx` | `.pptx` (editable in Slides/Keynote/PowerPoint) | `.png` · `.pdf` via LibreOffice headless | LibreOffice install: `brew install --cask libreoffice` (~600 MB one-time) |
| `docx` | `.docx` (editable in Word/Pages/Google Docs) | — | `--reference-doc=template.docx` controls styling (fonts/headings/margins); polish in Word/Pages and export PDF from there |
| `pdf` | `.pdf` (vector, via tectonic) | — | YAML metadata block in the markdown controls fonts/margins; for deep style control fall back to `/viz docx` → polish → export |

**Format size tradeoff** — PNG is universal but file size grows with resolution; PDF is usually smaller for vector-source tools and is print-quality; SVG is smallest for simple figures and infinitely scalable. Don't blindly default to ultra-high-resolution PNG.

**Generic PNG → PDF fallback** — for any image already on disk, `convert input.png output.pdf` works (ImageMagick — `brew install imagemagick`).


## Setup (new machine)

When this skill lands on a fresh machine, an agent should run the following one-time setup before invoking any sub-action. After this, both `/viz excalidraw` and `/viz matplot` produce polished output.

### 1. Python dependencies (`/viz matplot`)

```bash
pip install matplotlib numpy adjustText
```

(`adjustText` provides label collision avoidance for scatter / quadrant charts.)

### 2. Fonts (`/viz matplot`)

Two fonts are needed for Tufte-grade output:

- **Inter** — primary text font (Regular, SemiBold, Bold). Sans-serif, optimized for UI.
- **JetBrains Mono** — tabular numerics (used in numeric chart labels). Monospace.

**macOS (preferred — Homebrew):**
```bash
brew install --cask font-inter font-jetbrains-mono
```

**Other OS / no Homebrew:** download Inter from [rsms.me/inter](https://rsms.me/inter) and JetBrains Mono from [jetbrains.com/mono](https://www.jetbrains.com/lp/mono/), unzip, drop the `.otf` / `.ttf` files into `~/Library/Fonts/` (macOS), `~/.fonts/` (Linux), or the OS font folder.

If neither font is installed, vizcharts.py auto-falls back to Helvetica Neue (preinstalled on macOS) and finally to matplotlib's default DejaVu Sans. Charts still render; they just don't have the same polish.

### 3. Excalidraw (`/viz excalidraw`)

The `excalidraw_to_svg.py` script uses the [`@excalidraw/excalidraw` npm package](https://www.npmjs.com/package/@excalidraw/excalidraw) via Node. Install Node.js (e.g. `brew install node`) and ensure `npx` is available — the script runs the converter via `npx @excalidraw/mermaid-to-excalidraw` (or similar) on demand.

### 4. Pandoc + tectonic (`/viz docx`, `/viz pdf`)

```bash
brew install pandoc tectonic
```

`pandoc` is the universal document converter. `tectonic` is a modern Rust-based LaTeX engine used for high-quality PDF output (~200 MB vs MacTeX's ~4 GB).

A reference template ships at `~/.claude/skills/viz/template.docx` — pandoc clones its styles on every `--reference-doc` invocation. To customize styling project-wide, copy the template, modify in Word/Pages, and pass `--template <path>` to `/viz docx`.

### 5. Verify

Run the matplot smoke test:

```bash
cd ~/.claude/skills/viz
python3 -c "
import vizcharts as vc
print('Detected font:', vc.DEFAULT_FONT_FAMILY)
print('Themes:', list(vc.THEMES.keys()))
data = {'labels': ['Q1','Q2','Q3','Q4'], 'series': [{'name':'A','values':[1,2,3,4]}]}
vc.chart_multi_line(data, '/tmp/viz-smoke.png', {'theme':'neutral','title':'Smoke test'})
print('Rendered: /tmp/viz-smoke.png')
"
open /tmp/viz-smoke.png
```

Expected output: `Detected font: Inter` (if Inter is installed); `Themes: ['light', 'dark', 'neutral']`; a clean chart in `/tmp/viz-smoke.png` with brand-neutral deep-blue accent (not Northwind red).

If `Detected font:` shows `DejaVu Sans` instead of `Inter`, fonts didn't install correctly — re-run step 2.


## Dispatch

On invocation:

1. Parse the argument to determine the action (excalidraw, matplot, mermaid, dot, pptx, docx, pdf).
2. Look up the file from the Action Files table above.
3. Read that file from this skill's directory and execute its workflow.
4. If no argument or unrecognized argument, show the user-facing Actions table at the top.
