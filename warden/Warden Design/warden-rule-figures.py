#!/usr/bin/env python3
"""Render the example rule + example ruleset as SVG code-cards.

These figures let Warden Rule SHOW a literal markdown rule/ruleset without
embedding live markdown (which would create real headings) or fencing it
(forbidden). Regenerate:  python3 warden-rule-figures.py
"""
import re
from pathlib import Path

CHAR_W = 9.6      # px per monospace char at 15px (generous, avoids right-clip)
LINE_H = 23
PAD = 18
FONT = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

SENTINEL = re.compile(r"\b(RULE|RULESET)\b")
FIELD = re.compile(r"^(include|where|when|description|check)::")
BOLDFIELD = re.compile(r"^\*\*[^*]+:\*\*")  # **Check pattern:** / **Why:**


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_color(line: str) -> str:
    if line.lstrip().startswith("#"):
        return "#7b2d52"          # heading / sentinel line
    if FIELD.match(line):
        return "#2d5b7b"          # :: field line
    if BOLDFIELD.match(line):
        return "#555555"          # **Label:** prose
    return "#1a1a2e"              # default


def line_weight(line: str) -> str:
    return "bold" if line.lstrip().startswith("#") else "normal"


def render(lines, out_path: Path):
    width = int(max(len(l) for l in lines) * CHAR_W) + 2 * PAD
    height = len(lines) * LINE_H + 2 * PAD
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="15">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="10" '
        f'fill="#f8f9fb" stroke="#c9cde0" stroke-width="1.5"/>',
    ]
    y = PAD + 16
    for line in lines:
        if line.strip():
            parts.append(
                f'<text x="{PAD}" y="{y}" fill="{line_color(line)}" '
                f'font-weight="{line_weight(line)}" xml:space="preserve">{esc(line)}</text>'
            )
        y += LINE_H
    parts.append("</svg>")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out_path.name}  ({width}x{height})")


RULE = [
    "### RULE R-diagram-04 — Text fits its container (checked)",
    "where:: {ANCHOR}/**/*.svg",
    "",
    "Every text element sits fully within the shape it labels —",
    "no overflow past the container edge.",
    "",
    "**Check pattern:** for each <text>, assert its bbox is inside",
    "the parent shape's bbox.",
    "",
    "**Why:** overflowing labels are the commonest hand-SVG defect.",
]

RULESET = [
    "# RULESET R-backlog",
    "include::",
    "where:: {ANCHOR}/**/{NAME} Backlog.md",
    "description:: Structure every {NAME} Backlog.md obeys.",
    "",
    "### RULE R-backlog-01 — Rows carry a status bracket (checked)",
    "**Check pattern:** every item under a horizon H2 ends with a",
    "[Ready] / [Questions] / … bracket.",
    "",
    "### RULE R-backlog-07 — Anchor has exactly one backlog (checked)",
    "where:: anchor",
    "**Check pattern:** exactly one \"* Backlog.md\" under the root.",
]

EXAMPLES = [
    "# RULESET R-warden-examples",
    "include::",
    "description:: worked examples of Warden's rule-execution modes",
    "",
    "### RULE R-ex-01 — Ruleset has a description (checked · script)",
    "check:: regex_present ^description::",
    "**Check pattern:** a header line matches ^description::",
    "",
    "### RULE R-ex-02 — Summary matches the body (stated · LLM)",
    "where:: {ANCHOR}/**/F[0-9][0-9][0-9] — *.md",
    "The ## Summary faithfully reflects ## Design — no drift, no",
    "promises the design abandoned.   (the LLM reads + judges)",
    "",
    "### RULE R-ex-03 — Open Questions still open (stated · script-assisted)",
    "check:: extract_section \"## Open Questions\"",
    "Judge each extracted item: still unresolved given the rest of",
    "the doc? Flag the stale ones.   (script narrows the LLM's input)",
    "",
    "### RULE R-ex-04 — Diagram matches prose (stated · LLM, gated)",
    "where:: {ANCHOR}/**/*Architecture*.md",
    "when:: write:markdown",
    "rerun:: significant         # skip re-eval for typo-scale edits",
    "The figure reflects the components in the prose; flag drift.",
]

here = Path(__file__).parent
render(RULE, here / "Warden Rule Example.svg")
render(RULESET, here / "Warden Ruleset Example.svg")
render(EXAMPLES, here.parent / "Warden User Docs" / "Warden Examples Ruleset.svg")
