#!/usr/bin/env python3
"""Convert an .excalidraw JSON file to SVG and PNG.

Usage: python3 excalidraw_to_svg.py input.excalidraw

Outputs <name>.svg and <name>.png alongside the input file.
Handles: rectangles, polygons (multi-point lines), simple lines (solid/dashed),
text (with rotation, multi-line, font families).

Key: Bounding box uses actual point positions for lines (not width/height)
to avoid phantom whitespace from negative-dy lines.
"""

import json
import math
import os
import shutil
import subprocess
import sys


def esc(s):
    """Escape text for SVG XML."""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("'", "&apos;").replace('"', "&quot;"))


def to_svg(elems, pad=12):
    """Convert Excalidraw elements to an SVG string."""
    all_x, all_y = [], []
    for el in elems:
        if "points" in el:
            # Lines/polygons: use actual point positions (handles negative dy)
            for p in el["points"]:
                all_x.append(el["x"] + p[0])
                all_y.append(el["y"] + p[1])
        else:
            all_x.extend([el["x"], el["x"] + el.get("width", 0)])
            all_y.extend([el["y"], el["y"] + el.get("height", 0)])

    if not all_x:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'

    min_x, max_x = min(all_x) - pad, max(all_x) + pad
    min_y, max_y = min(all_y) - pad, max(all_y) + pad
    vw, vh = max_x - min_x, max_y - min_y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {vw} {vh}" '
        f'width="{int(vw * 2)}" height="{int(vh * 2)}" style="background:white">',
    ]

    for el in elems:
        t = el["type"]

        if t == "rectangle":
            bg = el["backgroundColor"]
            fill = bg if bg != "transparent" else "none"
            rx = 6 if el.get("roundness") else 0
            parts.append(
                f'<rect x="{el["x"]}" y="{el["y"]}" width="{el["width"]}" '
                f'height="{el["height"]}" fill="{fill}" stroke="{el["strokeColor"]}" '
                f'stroke-width="{el["strokeWidth"]}" rx="{rx}"/>')

        elif t == "line":
            pts = el["points"]
            ox, oy = el["x"], el["y"]
            bg = el["backgroundColor"]
            fill = bg if bg != "transparent" else "none"
            dash = ' stroke-dasharray="10 7"' if el.get("strokeStyle") == "dashed" else ""

            if len(pts) > 2:
                # Polygon (closed multi-point line)
                d = f'M {ox + pts[0][0]:.1f} {oy + pts[0][1]:.1f}'
                for p in pts[1:]:
                    d += f' L {ox + p[0]:.1f} {oy + p[1]:.1f}'
                d += ' Z'
                parts.append(
                    f'<path d="{d}" fill="{fill}" stroke="{el["strokeColor"]}" '
                    f'stroke-width="{el["strokeWidth"]}"{dash} stroke-linejoin="round"/>')
            else:
                # Simple 2-point line
                parts.append(
                    f'<line x1="{ox + pts[0][0]:.1f}" y1="{oy + pts[0][1]:.1f}" '
                    f'x2="{ox + pts[1][0]:.1f}" y2="{oy + pts[1][1]:.1f}" '
                    f'stroke="{el["strokeColor"]}" stroke-width="{el["strokeWidth"]}"{dash}/>')

        elif t == "text":
            ff = el.get("fontFamily", 1)
            if ff == 2:
                font = "Helvetica, Arial, sans-serif"
            else:
                font = "'Segoe Print', 'Comic Sans MS', cursive, sans-serif"

            ang = el.get("angle", 0)
            ang_deg = math.degrees(ang)
            fs = el["fontSize"]
            col = el["strokeColor"]
            txt_lines = el["text"].split("\n")
            cx = el["x"] + el["width"] / 2
            cy = el["y"] + el["height"] / 2
            rot = (f' transform="rotate({ang_deg:.2f} {cx:.1f} {cy:.1f})"'
                   if abs(ang_deg) > 0.1 else "")

            ta = el.get("textAlign", "left")
            if ta == "center":
                anchor = "middle"
                tx = el["x"] + el["width"] / 2
            else:
                anchor = "start"
                tx = el["x"]

            if len(txt_lines) == 1:
                ty = el["y"] + fs * 0.88
                parts.append(
                    f'<text x="{tx:.1f}" y="{ty:.1f}" font-family="{font}" '
                    f'font-size="{fs}" fill="{col}" text-anchor="{anchor}"{rot}>'
                    f'{esc(txt_lines[0])}</text>')
            else:
                parts.append(
                    f'<text font-family="{font}" font-size="{fs}" fill="{col}" '
                    f'text-anchor="{anchor}"{rot}>')
                for i, line in enumerate(txt_lines):
                    ty = el["y"] + fs * 0.88 + i * fs * 1.25
                    parts.append(
                        f'  <tspan x="{tx:.1f}" y="{ty:.1f}">{esc(line)}</tspan>')
                parts.append('</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 excalidraw_to_svg.py input.excalidraw")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found")
        sys.exit(1)

    with open(input_path) as f:
        doc = json.load(f)

    elements = doc.get("elements", [])
    # Filter out deleted elements
    elements = [el for el in elements if not el.get("isDeleted", False)]

    if not elements:
        print("No elements found in the file.")
        sys.exit(1)

    print(f"Loaded {len(elements)} elements from {input_path}")

    # Generate SVG
    svg_content = to_svg(elements)
    base = os.path.splitext(input_path)[0]
    svg_path = base + ".svg"
    with open(svg_path, "w") as f:
        f.write(svg_content)
    print(f"SVG: {svg_path}")

    # Convert to PNG via rsvg-convert
    png_path = base + ".png"
    if shutil.which("rsvg-convert"):
        try:
            subprocess.run(
                ["rsvg-convert", "-w", "2400", "-o", png_path, svg_path],
                check=True)
            print(f"PNG: {png_path}")
        except subprocess.CalledProcessError as e:
            print(f"PNG conversion failed: {e}")
    else:
        print("PNG: skipped (install rsvg-convert: brew install librsvg)")


if __name__ == "__main__":
    main()
