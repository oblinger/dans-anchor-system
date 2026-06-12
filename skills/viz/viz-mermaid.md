# /viz mermaid — Mermaid diagrams via mmdc

Generate flow / sequence / gantt / class / state / ER diagrams from text source. Output is `.png` (slide-grade), `.pdf`, or `.svg`.

## Tool

`mmdc` — installed via `npm install -g @mermaid-js/mermaid-cli`. Verify with `mmdc -h`.

## Source format

`.mmd` text file. Example:

```
flowchart LR
  A[User input] --> B[Service]
  B --> C[(Database)]
  C --> D[Response]
```

Claude generates the `.mmd` source from a natural-language description, then runs `mmdc` to render.

## Usage

```bash
# PNG (default, slide-grade 1600×900)
mmdc -i source.mmd -o out.png -w 1600 -H 900

# PDF
mmdc -i source.mmd -o out.pdf

# SVG (vector, infinitely scalable)
mmdc -i source.mmd -o out.svg
```

Default output goes to `~/ob/data/MyDesk/{slug-from-prompt}-{YYYY-MM-DD-HHMM}.png` per the cross-cutting `/viz` default-location convention in [[SKILL]] § Default output.

## Native rendering vs PNG embedding

Mermaid source blocks render natively in GitHub, GitLab, Notion, VS Code preview, and many markdown renderers. For markdown deliverables that will be viewed in those environments, the **source-block path** may be preferred over PNG embedding — smaller file size, editable, accessible.

Decision rule:
- **Markdown going to GitHub/GitLab/Notion/VS Code** → embed as ` ```mermaid ... ``` ` source block.
- **Markdown going to PDF, Google Doc, or plain-text editors** → render to PNG.
- **Slides / docs / print** → render to PNG or PDF.

The agent should advertise both options when invoked and pick by use case.

## Workflow

1. **Determine diagram type** from user intent — flow, sequence, gantt, class, state, ER, etc.
2. **Generate `.mmd` source** as a text file (or inline string).
3. **Decide output format** — embed as source block in markdown, or render to PNG/PDF/SVG.
4. **Render** via `mmdc` with appropriate flags.
5. **Print output path** so the user can find the artifact.

## Verification

```bash
echo 'flowchart LR; A[User] --> B[Service] --> C[(DB)] --> D[Response]' > /tmp/viz-mermaid-test.mmd
mmdc -i /tmp/viz-mermaid-test.mmd -o /tmp/viz-mermaid-test.png -w 1600 -H 900
open /tmp/viz-mermaid-test.png
```
