# Excalidraw Examples — Reference

Complete working examples for creating `.excalidraw` files. Load this when creating diagrams.


## Minimal Complete File

A valid `.excalidraw` file with a title, a box, and an arrow:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "type": "text",
      "id": "title_1",
      "x": 50,
      "y": 30,
      "width": 300,
      "height": 35,
      "text": "My Diagram",
      "fontSize": 28,
      "fontFamily": 1,
      "textAlign": "left",
      "verticalAlign": "top",
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "link": null,
      "locked": false,
      "containerId": null,
      "originalText": "My Diagram",
      "autoResize": true,
      "lineHeight": 1.25,
      "isDeleted": false,
      "seed": 100001,
      "version": 2,
      "versionNonce": 100001,
      "updated": 1700000000000,
      "index": "a0"
    },
    {
      "type": "rectangle",
      "id": "box_1",
      "x": 50,
      "y": 100,
      "width": 150,
      "height": 80,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#edf2ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "groupIds": [],
      "frameId": null,
      "roundness": {"type": 3},
      "boundElements": [],
      "link": null,
      "locked": false,
      "isDeleted": false,
      "seed": 100002,
      "version": 2,
      "versionNonce": 100002,
      "updated": 1700000000000,
      "index": "a1"
    },
    {
      "type": "rectangle",
      "id": "box_2",
      "x": 350,
      "y": 100,
      "width": 150,
      "height": 80,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#e7f5ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "groupIds": [],
      "frameId": null,
      "roundness": {"type": 3},
      "boundElements": [],
      "link": null,
      "locked": false,
      "isDeleted": false,
      "seed": 100003,
      "version": 2,
      "versionNonce": 100003,
      "updated": 1700000000000,
      "index": "a2"
    },
    {
      "type": "arrow",
      "id": "arrow_1",
      "x": 200,
      "y": 140,
      "width": 150,
      "height": 0,
      "points": [[0, 0], [150, 0]],
      "strokeColor": "#868e96",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "angle": 0,
      "groupIds": [],
      "frameId": null,
      "roundness": {"type": 2},
      "boundElements": [],
      "link": null,
      "locked": false,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "startBinding": null,
      "endBinding": null,
      "lastCommittedPoint": null,
      "isDeleted": false,
      "seed": 100004,
      "version": 2,
      "versionNonce": 100004,
      "updated": 1700000000000,
      "index": "a3"
    }
  ],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```


## Element Types Reference

### Text
```json
{
  "type": "text",
  "id": "unique_id",
  "x": 50, "y": 30,
  "width": 300, "height": 35,
  "text": "Display text",
  "originalText": "Display text",
  "fontSize": 28,
  "fontFamily": 1,
  "textAlign": "left",
  "verticalAlign": "top",
  "lineHeight": 1.25,
  "autoResize": true,
  "containerId": null
}
```
- `fontFamily`: 1 = Virgil (hand-drawn), 2 = Helvetica, 3 = Cascadia (monospace)
- `fontSize`: common sizes — 14 (small), 20 (body), 28 (heading), 36 (title)
- **Text clipping fix**: `width` must be wide enough for the longest line. Use `max_line_length * fontSize * 0.62` as a minimum. For `height`, use `num_lines * fontSize * 1.35`. If text is clipped, the width/height are too small.

### Rectangle
```json
{
  "type": "rectangle",
  "id": "unique_id",
  "x": 100, "y": 100,
  "width": 150, "height": 80,
  "backgroundColor": "#edf2ff",
  "roundness": {"type": 3}
}
```
- `roundness`: `null` = sharp corners, `{"type": 3}` = rounded corners
- Common background colors: `"#edf2ff"` (blue), `"#e7f5ff"` (light blue), `"#fff3f3"` (red), `"#ebfbee"` (green), `"#fff9db"` (yellow), `"transparent"`

### Ellipse
```json
{
  "type": "ellipse",
  "id": "unique_id",
  "x": 100, "y": 100,
  "width": 30, "height": 30,
  "backgroundColor": "#fff3f3",
  "roundness": {"type": 2}
}
```

### Arrow
```json
{
  "type": "arrow",
  "id": "unique_id",
  "x": 200, "y": 140,
  "width": 150, "height": 0,
  "points": [[0, 0], [150, 0]],
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "startBinding": null,
  "endBinding": null,
  "lastCommittedPoint": null
}
```
- `points`: relative to x,y. `[[0,0], [150,0]]` = horizontal right. `[[0,0], [0,100]]` = vertical down. `[[0,0], [100,50]]` = diagonal.
- `endArrowhead`: `"arrow"` = arrowhead, `null` = plain line
- `startArrowhead`: same options for the start end


## Required Properties on All Elements

Every element MUST have ALL of these properties or ExcalidrawZ will reject the file:

```json
{
  "type": "...",
  "id": "unique_string",
  "x": 0, "y": 0,
  "width": 100, "height": 100,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "angle": 0,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "boundElements": [],
  "link": null,
  "locked": false,
  "isDeleted": false,
  "seed": 12345,
  "version": 2,
  "versionNonce": 12345,
  "updated": 1700000000000,
  "index": "a0"
}
```

**Do not omit any property.** ExcalidrawZ silently fails or crashes on missing properties. Copy the full template and modify values.

- `id`: unique per element. Use descriptive names like `"title_1"`, `"box_input"`, `"arrow_to_output"`.
- `seed`, `versionNonce`: random integers. Use different values per element.
- `index`: ordering. Use `"a0"`, `"a1"`, `"a2"`, etc.
- `updated`: Unix timestamp in milliseconds.
