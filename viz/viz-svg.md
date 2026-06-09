# viz-svg — Hand-written SVG diagrams

Author SVG figures directly via the `Write` tool. SVG is XML — the agent writes the file, no rendering pipeline required, no companion source format. The `.svg` file IS the editable source; subsequent revisions edit the SVG directly.

**This is the default for architecture diagrams** (and any figure where the agent wants full visual control over color, font, layout, and geometry). Reach for `/viz excalidraw` when the user wants a hand-drawn aesthetic, `/viz d2` only when the user names D2 specifically.

## When to use

- Architecture diagrams — boxes, arrows, labels, color-coded subsystems
- Component / data-flow / sequence sketches where the agent wants to control every pixel
- Diagrams that don't fit Mermaid's syntax cleanly and don't need ELK auto-layout
- Quick one-off figures where a 30-line SVG is cheaper than spinning up another tool

## When NOT to use

- **Charts from data** — use `/viz matplot` (proper data visualization library)
- **Mermaid-shaped diagrams** (flow / sequence / gantt / state / ER) — use `/viz mermaid` when source-block embedding matters
- **User asked for Excalidraw / D2 / Graphviz specifically** — honor the ask

## Workflow

1. **Author the SVG** with the `Write` tool. Hand-write the XML. No Python heredoc unless there's real parameterization (≥10 boxes, computed coordinates, data-driven figure).
2. **Embed in markdown** via `![[Name.svg]]` (Obsidian) or `![](Name.svg)` (vanilla markdown).
3. **(Optional) Generate PNG** for Obsidian-cache-friendliness or for tools that don't render SVG:
   ```bash
   rsvg-convert -w 1800 "Name.svg" -o "Name.png"
   ```
4. **No companion source file needed.** The SVG itself is the source. When the user asks for changes, edit the SVG directly.

## SVG template — arrows with proper arrowheads

The most common architecture-diagram pattern: boxes + arrows. Use a `<defs>` arrowhead marker so every arrow renders consistently:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 480" width="1800" height="960"
     style="background:white" font-family="Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polygon points="0,0 10,5 0,10" fill="#1e1e1e"/>
    </marker>
  </defs>

  <!-- Boxes (rounded rects, color-coded by role) -->
  <rect x="40" y="100" width="220" height="120" rx="10"
        fill="#fff3f3" stroke="#1e1e1e" stroke-width="2"/>
  <text x="150" y="155" font-size="24" text-anchor="middle" font-weight="600">CLI</text>

  <rect x="340" y="100" width="220" height="120" rx="10"
        fill="#bac8ff" stroke="#1e1e1e" stroke-width="2"/>
  <text x="450" y="155" font-size="24" text-anchor="middle" font-weight="600">Scheduler</text>

  <!-- Arrow + label -->
  <line x1="260" y1="160" x2="340" y2="160"
        stroke="#1e1e1e" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="300" y="148" font-size="14" fill="#1971c2"
        text-anchor="middle" font-style="italic">submit</text>
</svg>
```

## Style guidelines for architecture-grade SVG

- **Font:** `Helvetica, Arial, sans-serif` for clean body text. Avoid the default browser SVG font (Times-y).
- **Box colors (light, role-coded palette):**
  - Input / boundary: `#fff3f3` (pale red)
  - Compute / core: `#bac8ff` (medium blue)
  - Storage / persistence: `#fff9db` (pale yellow)
  - Policy / cross-cutting: `#ebfbee` (pale green)
- **Stroke:** `#1e1e1e` (near-black) at width `2` for box borders, `3` for arrows.
- **Box rounding:** `rx="10"` for soft architectural blocks.
- **Arrowheads:** define one `<marker id="arrowhead">` in `<defs>` and `marker-end="url(#arrowhead)"` on every arrow.
- **Arrow labels:** italic blue (`fill="#1971c2"`, `font-style="italic"`), small (font-size 14), placed slightly above the arrow.
- **viewBox:** `0 0 900 480` is a reasonable default for a 3-column, 2-row architecture; scale by changing `width`/`height` attributes (the `viewBox` is the logical canvas; `width`/`height` are the rendered pixel dims).

## File-location convention

The SVG lives next to the markdown that embeds it:

```
{Name}/{Name}.md
{Name}/{Name}.svg                 ← embedded as ![[Name.svg]] or via Obsidian basename resolution
{Name}/{Name}.png                 ← optional, generated from the SVG
```

Per the `feedback_figure_source_alongside_output` memory and `.gitignore` allow-list: architecture-folder SVG / PNG are versioned automatically.

## When Python heredoc IS justified

Reach for Python only when the figure has real parameterization:

- More than ~10 elements with shared structure
- Computed coordinates (e.g., box-A-center → box-B-center for arrows)
- Data-driven (boxes generated from a list of subsystems)

In those cases, store the Python script next to the SVG with the same basename: `Name.py` → `Name.svg` (per the figure-source-alongside-output convention). The .gitignore allows `*.py` inside Architecture folders.

For 5 boxes and 5 arrows, hand-write the SVG. Python is over-engineering at that scale.

## Failure mode to avoid

**Don't use `excalidraw_to_svg.py` to render arrow-bearing diagrams** — the converter silently drops `arrow` elements. This was discovered 2026-06-08 (CAE Architecture diagram). The fix is to either hand-write the SVG (this skill) or open the `.excalidraw` in ExcalidrawZ and export from there.

## See also

- [[viz-excalidraw]] — for hand-drawn aesthetic
- [[viz-d2]] — for D2's specific ELK-auto-routed look (only when user asks)
- [[viz-mermaid]] — for source-block-friendly Mermaid diagrams
- `feedback_figure_source_alongside_output` memory — source-alongside-output convention
- `feedback_no_ascii_in_architecture_diagrams` memory — ASCII forbidden in arch docs
