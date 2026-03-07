---
name: edit
description: >
  Visual editing skills — diagrams, mockups, and visual content creation.
  Use with an action argument: /edit excalidraw.
  Triggered when user says "excalidraw", "draw", "diagram", "mockup", "export excalidraw",
  "save to slides", "excalidraw to SVG", "paste into Google Slides",
  or asks to create/update/export a diagram.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Edit — Visual Editing
Visual content creation and editing tools.

| ACTIONS             | File                | Description                                         |
| ------------------- | ------------------- | --------------------------------------------------- |
| `/edit excalidraw`  | [[edit-excalidraw]] | Create, update, and export Excalidraw diagrams      |


## Scripts

| Script                    | Usage                                                   |
| ------------------------- | ------------------------------------------------------- |
| `excalidraw_to_svg.py`    | Convert .excalidraw to SVG/PNG. Run via `python3`.      |
| `insert_into_slides.py`   | Insert PNG into a Google Slides page via API.           |


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the actions table above
