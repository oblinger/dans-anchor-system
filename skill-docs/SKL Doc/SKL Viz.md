---
description: "`/viz` produces visual artifacts — diagrams, charts, mockups, slides, formatted docs."
---
# /Viz

`/viz` produces visual artifacts — diagrams, charts, mockups, slides, formatted docs. You always pair it with a sub-action that picks the rendering tool, since each tool has a distinct aesthetic: `/viz excalidraw` for hand-drawn architecture sketches, `/viz matplot` for Tufte-grade data charts (timeline, multi-line, quadrant, scatter, waterfall, hex shot, etc.), `/viz mermaid` for flow / sequence / gantt / state diagrams from text, `/viz dot` for Graphviz dependency graphs and org charts, `/viz pptx` for custom slide-shaped layouts, and `/viz docx` / `/viz pdf` for converting markdown to polished documents.

Trigger phrases: "draw," "diagram," "mockup," "chart this," "plot data," "timeline chart," "excalidraw," or "convert this to PDF." Output lands in `~/ob/data/MyDesk/` by default with a slug-and-timestamp filename, so you can find what you generated across sessions without it scattering through `/tmp`. First-time use on a new machine needs a one-time setup step (install Inter + JetBrains Mono fonts, pandoc + tectonic for docx/pdf, Node for Excalidraw) — see the skill's setup section.


## Capability matrix — viewing, clicking, round-trip editing

The trade-off table for picking a viz approach by its Obsidian + external capabilities. Rows are the approaches; columns are the capabilities. Use this when *"the source must remain editable in Obsidian"* or *"must have clickable regions externally"* is the constraint driving tool selection.

| Approach           | Source format                                            | Render output                                               | Obsidian inline view                                                                                               | Obsidian clickable regions                                                                                         | External clickable regions                                                                           | Round-trip editable from Obsidian                                                                                                       |
| ------------------ | -------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **mermaid**        | ` ```mermaid ` code block in `.md`                       | SVG (auto by Obsidian); `.png` / `.pdf` / `.svg` (via mmdc) | **Yes** — Obsidian renders ` ```mermaid ` blocks natively (core feature)                                           | Partial — `click` directive supports URLs; Obsidian wraps them as external links                                   | **Yes** — GitHub / Notion / VS Code render natively; `click` directive supported on the web          | **Yes** — source IS the markdown; edit the code block, render updates inline                                                            |
| **excalidraw**     | `.excalidraw` JSON                                       | `.svg` / `.png` (via `excalidraw_to_svg.py`)                | **Yes** (with Excalidraw plugin) — `.excalidraw` files render as interactive canvas; SVG embeds render universally | **Yes** (with plugin) — embedded files / elements link to other vault pages; hyperlinks on shapes                  | **Yes** — SVG export wraps clickable elements as `<a>` tags; Excalidraw web has native interactivity | **Yes** (with plugin) — open the file in Obsidian, edit on canvas, save back to the same file                                           |
| **dot** (Graphviz) | `.dot` text                                              | `.svg` / `.png` / `.pdf`                                    | Embed-only — Obsidian shows the rendered SVG/PNG (no native DOT renderer; plugins exist)                           | Partial — SVG `<a>` tags survive embed in some Obsidian configurations                                             | **Yes** — DOT `URL=...` attributes on nodes render as SVG `<a>` regions on the web                   | No — edit the `.dot` text externally, re-render, re-embed                                                                               |
| **matplot**        | `.py` (matplotlib code)                                  | `.png` (raster) · `.pdf` (vector)                           | **Yes** for PNG/PDF (Obsidian embeds raster + renders PDF inline)                                                  | No — raster has no clickable regions; matplotlib PDFs don't ship hyperlinks by default                             | No (PNG); limited for PDF                                                                            | No — source is Python code, not editable from inside Obsidian                                                                           |
| **pptx**           | `.pptx` (binary, opens in PowerPoint / Keynote / Slides) | `.pptx` · `.png` / `.pdf` (via LibreOffice headless)        | No — Obsidian does not render `.pptx`; click-to-open in external app                                               | No                                                                                                                 | **Yes** — PowerPoint hyperlinks on shapes / text travel into the file                                | No — edit externally in PowerPoint / Keynote / Slides                                                                                   |
| **docx**           | `.md` (canonical) → `.docx` via pandoc                   | `.docx` · (export `.pdf` from Word/Pages)                   | No — Obsidian does not render `.docx`; click-to-open in external app                                               | No                                                                                                                 | **Yes** — Word / Pages / Google Docs hyperlinks travel into the file                                 | Partial — re-edit the `.md` source in Obsidian, re-run `/viz docx` to regenerate (round-trips through the source, not the rendered doc) |
| **pdf**            | `.md` (canonical) → `.pdf` via pandoc + tectonic         | `.pdf`                                                      | **Yes** — `![[file.pdf]]` embeds render inline with paging                                                         | No — Obsidian's PDF viewer does not surface hyperlink interactivity (clicks navigate the PDF, not the link target) | **Yes** — PDF readers / browsers honor embedded hyperlinks                                           | Same as docx — re-edit source `.md` in Obsidian, re-run `/viz pdf`                                                                      |


## Reading the matrix

- **Round-trip editable from Obsidian** means: you can open the artifact (or its source) in Obsidian, change it, save, and the rendered view updates without leaving the editor. Mermaid is the cleanest — the source IS the markdown. Excalidraw matches with the plugin. The rest require leaving Obsidian.
- **Obsidian clickable regions** means: an interactive region inside the embedded render that, when clicked, does something useful inside Obsidian (navigate to another note, open a URL). Mermaid `click` and Excalidraw embedded links work; PDF and raster images don't.
- **External clickable regions** means: when the rendered output is shared (web, GitHub, slides), the embedded interactivity travels with it.
- **"Source format"** is what you actually edit; **"render output"** is what's viewed.


## Decision shortcuts

- *Must be editable from inside Obsidian AND have inline view AND survive on GitHub* → **mermaid** is the only approach hitting all three out of the box.
- *Must have rich clickable regions on the web AND inside Obsidian* → **excalidraw** (with the plugin installed) is the strongest.
- *Don't care about Obsidian view; need a deliverable that opens in PowerPoint / Word with interactivity* → **pptx** or **docx**.
- *Tufte-grade quantitative chart with no interactivity needed* → **matplot**.


## Where things go from here

- **Trade-off discussions, design questions, round-trip investigations** → [[SKA viz discussion]] (the open-questions surface for the /viz skill).
- **Agent runbook** (decisive rules the agent reads; not for browsing) → `viz/SKILL.md`.
- **Backlog + planning** → [[SKA viz backlog]] under [[SKA viz]].

This matrix is a living reference — extend rows as new approaches land, and tighten cells as the round-trip experiments resolve.
