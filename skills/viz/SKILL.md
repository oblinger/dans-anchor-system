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

User-facing docs (capability matrix, trade-off rationale): [[DAS Viz]].
Trade-off discussions (round-trip experiments, design questions): [[SKA viz discussion]].


## Actions

| Action | What it does | Output | Trigger phrases |
|---|---|---|---|
| `/viz svg` | **Hand-written SVG via the Write tool — default for architecture diagrams and any figure where the agent wants full visual control.** SVG is just XML; the agent authors it directly. The `.svg` file IS the editable source (no companion file needed). Full control over color, font, layout, geometry. | `.svg` source (editable XML) · optional `.png` via `rsvg-convert` | "svg", "hand-write an svg", "architecture diagram", "boxes and arrows with my own look" |
| `/viz diagram` | **Rule-enforced SVG via the [[R-diagram]] ruleset (22 rules, 7 methodologies).** Two modes: create (default — author a new SVG following the rules) and cleanup (when the arg points at an existing SVG — audit + fix violations in-place). Loads R-diagram before any authoring or editing; conformance is the standard for "done." Use when the user names "diagram" specifically or wants the rule-checked variant of `/viz svg`. | `.svg` source · optional `.png` via `rsvg-convert` · audit report (cleanup mode) | "diagram", "viz diagram", "rule-checked diagram", "clean up this diagram", "diagram against the rules" |
| `/viz excalidraw` | Create / update / export Excalidraw diagrams. Hand-drawn aesthetic. The `.excalidraw` source lives next to the export, editable in ExcalidrawZ. | `.excalidraw` source + `.svg` / `.png` export | "draw", "sketchy", "excalidraw", "freeform", "paste into Google Slides" |
| `/viz d2` | D2's specific opinionated look — text → boxes-and-arrows with ELK auto-routing. **Use only when the user asks for D2 specifically**; the D2 aesthetic is distinctive and not a universal default. | `.d2` source + `.svg` | "d2", "elk auto-layout", "D2-style", "ELK-routed" |
| `/viz matplot` | Generate matplotlib charts via `vizcharts.py` (10 chart types: timeline, multi-line, quadrant, scatter, rankings, comparison, stacked bar, donut, waterfall, hex shot). Tufte-grade static output. | `.png` (raster) · `.pdf` (vector) | "chart this", "plot the data", "timeline chart", "bar chart", "quadrant", "waterfall" |
| `/viz mermaid` | Mermaid diagrams from text (flow / sequence / gantt / class / state / ER). Renders natively in GitHub / GitLab / Notion / VS Code preview when embedded as a source block. | `.png` · `.pdf` · `.svg` · or markdown source block | "mermaid", "flow chart", "sequence diagram", "gantt", "state machine", "ER diagram" |
| `/viz dot` | Graphviz DOT — box/arrow graphs, decision trees, org charts, dependency graphs. Stronger layout engine than Mermaid for complex graphs. | `.png` · `.pdf` · `.svg` | "graphviz", "dot diagram", "org chart", "dependency graph", "decision tree" |
| `/viz pptx` (aliases: `/viz ppt`, `/viz powerpoint`) | python-pptx for highly-custom slide-shaped layouts. Fallback when neither Mermaid nor Graphviz expresses the figure cleanly — annotated visualizations, multi-element compositions, mockups. | `.pptx` (editable) · `.png` / `.pdf` via LibreOffice | "custom slide", "annotated layout", "multi-element composition", "mockup with text and image", "powerpoint", "ppt" |
| `/viz docx` | Convert a markdown file to editable `.docx` via pandoc + reference template. Use when you want to polish in Word/Pages before final delivery (export PDF yourself when satisfied). | `.docx` (editable) | "md to docx", "convert markdown to word", "Word doc from this markdown", "polish in Word", "make a docx" |
| `/viz pdf` | Convert a markdown file directly to PDF via pandoc + tectonic. Use for quick share, automated pipeline, or when default typography is fine. | `.pdf` | "md to pdf", "convert markdown to pdf", "quick pdf of this", "render this doc to pdf", "export to pdf" |


## Action files

| Usage | File | Description |
|-------|------|-------------|
| `/viz svg`        | [[viz-svg]]        | Hand-written SVG via Write — default for architecture diagrams |
| `/viz diagram`    | [[viz-diagram]]    | Rule-enforced SVG against [[R-diagram]] — create or cleanup mode |
| `/viz excalidraw` | [[viz-excalidraw]] | Create, update, and export Excalidraw diagrams |
| `/viz d2`         | [[viz-d2]]         | D2 system diagrams via ELK; use when user asks for D2 specifically |
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


## Tool selection — pick the tool, then go

The user usually says the tool. When they don't, walk this list top-down — **the first match wins**. Don't weigh trade-offs in chat; the matrix lives in [[DAS Viz]].

**Constraint-driven rules (check these first — they often dominate):**

- User said "**must be editable in Obsidian**" / "**I want to keep tweaking this in Obsidian**" → `/viz mermaid` (source is the markdown — round-trip is automatic). Fall back to `/viz excalidraw` if the user has the Excalidraw plugin and wants a canvas, not text.
- User said "**clickable on the web**" / "**share on GitHub / Notion**" → `/viz mermaid` for flow/sequence/state; `/viz excalidraw` (SVG export) for sketches; `/viz dot` for graphs (DOT `URL=...` attributes survive).
- User said "**clickable in PowerPoint / Word**" → `/viz pptx` or `/viz docx` (their native hyperlinks travel into the file).
- User said "**Tufte-grade**" / "**chart this data**" / "**plot**" → `/viz matplot`. No interactivity; best aesthetic for quantitative.

**Shape-driven rules (when no interaction-model constraint is stated):**

- "architecture diagram" / "system diagram" / "boxes and arrows" → `/viz svg` (default — hand-written, full control of look). `/viz d2` only when the user names it.
- "draw" / "mockup" / "sketchy" / "freeform" → `/viz excalidraw`.
- "flow chart" / "sequence diagram" / "gantt" / "state machine" / "ER diagram" → `/viz mermaid`.
- "org chart" / "dependency graph" / "decision tree" / "complex graph" (≥30 nodes) → `/viz dot` (Graphviz layout beats Mermaid here).
- "custom slide" / "annotated layout" / "multi-element composition" (none of the above fit) → `/viz pptx`.
- "markdown → editable Word doc" → `/viz docx`.
- "markdown → quick PDF" → `/viz pdf`.

**When the user already named a tool, use that tool.** Don't ask "want PNG or PDF?" — answer with what they asked, note the format in the response, move on. When ambiguous on tool AND no constraint helps, ask which tool — these aren't interchangeable.

(Rationale + the full trade-off matrix: [[DAS Viz]]. Open trade-off discussions: [[SKA viz discussion]].)



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

**Portability fallback** — resolve the output dir in this order: (1) an explicit `--output` / user-given path; (2) `~/ob/data/MyDesk/` **if it exists**; (3) the current working directory. On a fresh machine without the vault, MyDesk won't exist, so artifacts land in the cwd rather than failing — never assume the directory is present.

This convention applies retroactively — `/viz matplot` (which previously dropped to caller-specified paths) should also default to MyDesk when no path is given.


## Output formats

Every action supports a primary output format and one or more secondary formats. The skill should advertise the choice when invoked so the agent picks per use case.

| Tool | Primary | Vector option | Notes |
|---|---|---|---|
| `svg` | `.svg` (hand-written XML — IS the source) | `.png` via `rsvg-convert` | No companion source file; edit the SVG directly. Full control of color/font/layout. |
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


## Engine selection (user environment)

Who **creates** a diagram and who **refines** (cleans up) it are user-configurable via the [[User Environment]] doc (per F182, `## viz` section), so the user picks the engines without editing this skill. Read them at the start of any create flow — both fall back to defaults when unset, so the skill works with no user-env configured.

- **Creation engine** — `anchor-system env viz create_engine` (default `builtin`):
  - `builtin` / unset → use this skill's own per-action engine (the Actions table — svg / d2 / dot / mermaid / …). The normal path.
  - any other value naming an installed skill (e.g. `drawio`) → **hand creation off to that skill**: invoke `/<engine>` with the user's description and let it produce the artifact, skipping the built-in author step.
- **Refinement engine** — `anchor-system env viz refine_engine` (default `svg-jiggle`), applied **after an SVG exists**:
  - `svg-jiggle` → run the built-in deterministic geometric repair: `python3 skills/viz/svg-jiggle.py "<path>.svg" -o "<path>.jiggled.svg" --report` (clears label-over-box / overweighted-head / … per [[R-svg-jiggle]]).
  - any other value naming a skill (e.g. `drawio`) → hand the artifact to that skill's refinement / vision self-check.
  - `none` → skip refinement.

Read with the CLI (`anchor-system env viz <key>`) or, from Python, the importable `user_env.get("viz", "<key>", default=…)` in `skills/anchor-system/scripts/user_env.py`.

## Dispatch

On invocation:

1. Parse the argument to determine the action (svg, diagram, excalidraw, d2, matplot, mermaid, dot, pptx, docx, pdf).
2. **Creation engine (§ Engine selection):** for a create flow, read `viz create_engine`. If it names an external skill, hand creation to `/<engine>` with the user's description and skip to step 5. If `builtin` / unset, continue.
3. Look up the file from the Action Files table above.
4. Read that file from this skill's directory and execute its workflow.
5. **Refinement engine (§ Engine selection):** once an SVG artifact exists, read `viz refine_engine` and apply it — `svg-jiggle` → run `svg-jiggle.py`; a skill name → invoke that skill's refinement; `none` → skip.
6. If no argument or unrecognized argument, show the user-facing Actions table at the top.
