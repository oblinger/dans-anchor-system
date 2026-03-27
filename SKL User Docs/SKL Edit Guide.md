---
description: How to create and export visual content — Excalidraw diagrams, SVG, PNG, Google Slides
---

# SKL Edit Guide (Skill: [[edit/SKILL]])

The Edit skill handles visual content creation, primarily through Excalidraw diagrams. The agent can create `.excalidraw` files programmatically by writing the JSON format directly, then export them to SVG or PNG for use in documents and presentations.

The typical workflow is: describe what you want in a diagram, the agent creates or updates an Excalidraw file, exports it to SVG/PNG, and optionally inserts it into Google Slides. This is useful for architecture diagrams, flowcharts, mockups, and any visual that needs to live alongside project documentation.

## Commands

| Command | Description |
|---------|-------------|
| `/edit excalidraw` | Create, update, or export an Excalidraw diagram |

## Key Concepts

- **Excalidraw JSON** — The agent writes `.excalidraw` files directly as JSON, placing shapes, text, and arrows programmatically
- **SVG/PNG export** — `excalidraw_to_svg.py` converts `.excalidraw` files to SVG or PNG format
- **Google Slides insertion** — `insert_into_slides.py` pushes a PNG into a specific Google Slides page via the API
- **Trigger words** — Saying "excalidraw", "draw", "diagram", or "mockup" invokes this skill
- **Iterative editing** — You can ask the agent to modify existing diagrams by updating the JSON and re-exporting
