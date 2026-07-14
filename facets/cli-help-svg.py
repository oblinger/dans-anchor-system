#!/usr/bin/env python3
"""Render a CLI `--help` text block to a content-sized, terminal-styled SVG.

Why an SVG and not a markdown code fence: a fence re-wraps long lines at the
render width, which destroys the column-aligned `# comment` layout of a help
screen. An SVG fixes the geometry, so the help reads exactly as authored at any
display width.

Usage:  cli-help-svg.py "<name> Help.txt"   ->  writes "<name> Help.svg" alongside

The .txt source is the single source of truth; regenerate the .svg after editing
it. Lines are `command ...   # comment`; the first whitespace-run before a `#`
splits code from comment. The first token of each line is treated as the tool
name and tinted. Font size is fixed and the canvas is sized to the content, so
text stays readable at natural width — embed at roughly the SVG's own px width
(~1000–1300), never a 3000px canvas scaled down to unreadable type.
"""
import re, sys, html, pathlib

FONT = 15                                   # px, in SVG user units
CHAR_W = FONT * 0.60                         # monospace advance
LINE_H = round(FONT * 1.55, 2)
PAD_X, PAD_Y = 24, 20
BG, FG, COMMENT, TOOL = "#0d1117", "#c9d1d9", "#8b949e", "#79c0ff"


def esc(s):
    return html.escape(s, quote=False)


def render(text):
    lines = text.rstrip("\n").split("\n")
    maxlen = max((len(l) for l in lines), default=1)
    w = round(PAD_X * 2 + maxlen * CHAR_W)
    h = round(PAD_Y * 2 + len(lines) * LINE_H)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
        f'font-size="{FONT}">',
        f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>',
    ]
    y = PAD_Y + FONT
    for ln in lines:
        # Force each line onto an exact char grid so the layout is deterministic
        # regardless of the viewer's monospace fallback (no overflow, columns stay aligned).
        tl = round(len(ln) * CHAR_W, 1)
        out.append(
            f'<text x="{PAD_X}" y="{round(y, 1)}" xml:space="preserve" '
            f'textLength="{tl}" lengthAdjust="spacingAndGlyphs">'
        )
        m = re.match(r'^(\S*)(.*?)(\s+)(#.*)$', ln)
        if m:
            tool, rest, gap, comment = m.groups()
            out.append(
                f'<tspan fill="{TOOL}">{esc(tool)}</tspan>'
                f'<tspan fill="{FG}">{esc(rest + gap)}</tspan>'
                f'<tspan fill="{COMMENT}">{esc(comment)}</tspan>'
            )
        elif ln.strip():
            tool, _, rest = ln.partition(" ")
            out.append(
                f'<tspan fill="{TOOL}">{esc(tool)}</tspan>'
                f'<tspan fill="{FG}">{esc((" " + rest) if rest else "")}</tspan>'
            )
        out.append('</text>')
        y += LINE_H
    out.append('</svg>')
    return "\n".join(out), w


def main():
    src = pathlib.Path(sys.argv[1])
    svg, w = render(src.read_text())
    dst = src.with_suffix(".svg")
    dst.write_text(svg)
    print(f"wrote {dst.name}  ({w}px wide — embed near ![[{dst.stem}.svg|{w}]])")


if __name__ == "__main__":
    main()
