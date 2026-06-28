#!/usr/bin/env python3
"""Render Warden rule/ruleset examples as SVG code-cards.

Clean-viewer look: literal rule syntax (`###` headings, `key::` fields,
backticked globs) is shown as-is, but **bold** markdown is RENDERED bold
(asterisks stripped) — so the card reads like a rendered doc, not raw
markdown. Regenerate:  python3 warden-rule-figures.py
"""
import re
from pathlib import Path

CHAR_W = 8.0      # px per monospace char at 13px
LINE_H = 20
PAD = 16
FONT = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
FSIZE = 13

FIELD = re.compile(r"^(include|where|when|if|rerun|description|check)::")
PYLINE = re.compile(r"^(```|def |    |\treturn)")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_style(line: str):
    s = line.lstrip()
    if re.match(r"^#{1,6}\s+(RULE|RULESET)\b", s):
        return "#7b2d52", "bold"      # markdown heading sentinel (### RULE / # RULESET)
    if FIELD.match(line):
        return "#2d5b7b", "normal"    # :: field
    if s.startswith("`"):
        return "#2f7d4f", "normal"    # inline-backtick one-liner = python body
    if PYLINE.match(line) or s.startswith("#"):
        return "#2f7d4f", "normal"    # embedded python (incl. # comments)
    return "#1a1a2e", "normal"        # default


def tspans(line, color, weight):
    segs, pos = [], 0
    for m in BOLD.finditer(line):
        if m.start() > pos:
            segs.append((line[pos:m.start()], weight))
        segs.append((m.group(1), "bold"))   # **x** -> bold, asterisks dropped
        pos = m.end()
    if pos < len(line):
        segs.append((line[pos:], weight))
    if not segs:
        segs = [(line, weight)]
    return "".join(
        f'<tspan font-weight="{w}" fill="{color}">{esc(t)}</tspan>'
        for t, w in segs if t != ""
    )


def disp_len(line):
    return len(BOLD.sub(r"\1", line))


def render(lines, out_path: Path):
    width = int(max((disp_len(l) for l in lines), default=10) * CHAR_W) + 2 * PAD
    height = len(lines) * LINE_H + 2 * PAD
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FSIZE}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="9" '
        f'fill="#f8f9fb" stroke="#c9cde0" stroke-width="1.3"/>',
    ]
    y = PAD + 13
    in_fence = False
    for line in lines:
        if line.strip():
            if line.lstrip().startswith("```"):
                c, w = "#2f7d4f", "normal"
                in_fence = not in_fence
            elif in_fence:
                c, w = "#2f7d4f", "normal"   # everything inside a fence is python
            else:
                c, w = line_style(line)
            parts.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">{tspans(line, c, w)}</text>')
        y += LINE_H
    parts.append("</svg>")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out_path.name}  ({width}x{height})")


# ── the rule/ruleset format figures (for Warden Rule) ──────────────────
RULE = [
    "### RULE R-diagram-04 — Text fits its container (checked)",
    "where:: `{ANCHOR}/**/*.svg`",
    "",
    "Every text element sits fully within the shape it labels —",
    "no overflow past the container edge.",
    "",
    "**Check pattern:** for each text element, assert its bbox is",
    "inside the parent shape's bbox.",
    "",
    "**Why:** overflowing labels are the commonest hand-SVG defect.",
]
RULESET = [
    "# RULESET R-backlog",
    "include::",
    "where:: `{ANCHOR}/**/{NAME} Backlog.md`",
    "description:: Structure every {NAME} Backlog.md obeys.",
    "",
    "### RULE R-backlog-01 — Rows carry a status bracket (checked)",
    "**Check pattern:** every item under a horizon H2 ends with a",
    "[Ready] / [Questions] bracket.",
    "",
    "### RULE R-backlog-07 — Anchor has exactly one backlog (checked)",
    "where:: anchor",
    "**Check pattern:** exactly one Backlog.md under the anchor root.",
]

# ── the execution-mode examples (for Warden Examples) ──────────────────
HEADER = [
    "# RULESET R-warden-examples",
    "include::",
    "description:: worked examples of Warden's rule-execution modes",
]
RULES = {
    # body scope: file / anchor / event (the matched sub-objects) + bare verbs
    # tell / deny / judge. bare prose body = the tell; backticks = python.
    "prose": [
        "### RULE R-ex-01 — Ruleset has a description",
        "where:: `**/R-*.md`",
        "if:: `'description' not in file.frontmatter`",
        "Every ruleset needs a `description::` line — add one.",
    ],
    "python": [
        "### RULE R-ex-02 — No empty sections",
        "description:: Every H2 section needs a body; an empty heading is a stub.",
        "where:: `**/*.md`",
        "```",
        "for s in file.sections(level=2):",
        "    if not s.body.strip():",
        "        tell(f\"'{s.title}' is empty — add a body or drop it\")",
        "```",
    ],
    "judgment": [
        "### RULE R-ex-03 — Summary matches the body",
        "where:: `**/F[0-9][0-9][0-9] — *.md`",
        "The `## Summary` should faithfully reflect `## Design`.",
        "If it has drifted, say what no longer matches.",
    ],
    "script-assisted": [
        "### RULE R-ex-04 — Open Questions still open",
        "where:: `**/*.md`",
        "```",
        "# narrow to just this slice, merged into the prompt; the oracle replies in prose",
        "q = file.section('## Open Questions')",
        "tell(ask_oracle(f'Which of these are already resolved elsewhere?\\n\\n{q}'))",
        "```",
    ],
    "edit": [
        "### RULE R-ex-05 — Stamp the reviewed-date",
        "where:: `**/*Architecture*.md`",
        "when:: write:markdown",
        "`file.set_frontmatter('reviewed', today)`",
    ],
    "deny": [
        "### RULE R-ex-06 — No force-push to main",
        "when:: tool:pre:Bash",
        "```",
        "# the pending command — not yet run; we inspect it",
        "if 'git push' in event.command and git.branch == 'main':",
        "    deny('never force-push main — open a PR instead')",
        "```",
    ],
}

def render_annotated(lines, annots, out_path: Path):
    """annots: list of (start_idx, end_idx, label, color) — labeled brackets in a right gutter."""
    content_w = int(max((disp_len(l) for l in lines), default=10) * CHAR_W) + 2 * PAD
    gutter = 168
    width = content_w + gutter
    height = len(lines) * LINE_H + 2 * PAD
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FSIZE}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="9" '
        f'fill="#f8f9fb" stroke="#c9cde0" stroke-width="1.3"/>',
    ]
    y = PAD + 13
    line_y = []
    for line in lines:
        line_y.append(y)
        if line.strip():
            c, w = line_style(line)
            parts.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">{tspans(line, c, w)}</text>')
        y += LINE_H
    gx = content_w + 4
    for (s, e, label, color) in annots:
        yt, yb = line_y[s] - 12, line_y[e] + 4
        parts.append(f'<path d="M{gx+5},{yt} H{gx} V{yb} H{gx+5}" fill="none" stroke="{color}" stroke-width="1.6"/>')
        parts.append(
            f'<text x="{gx+13}" y="{(yt+yb)//2+4}" fill="{color}" font-size="12" '
            f'font-weight="bold">{esc(label)}</text>'
        )
    parts.append("</svg>")
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out_path.name}  ({width}x{height})")


ANATOMY = [
    "### RULE R-ex — Title present",
    "where:: `*.md`",
    "when:: write:markdown",
    "if:: `not file.title`",
    "Add a top-level title.",
]
ANATOMY_ANNOTS = [
    (0, 0, "name", "#7b2d52"),
    (1, 3, "IF — condition", "#2d5b7b"),
    (4, 4, "THEN — the tell (just prose)", "#2f7d4f"),
]

here = Path(__file__).parent
udocs = here.parent / "Warden User Docs"
render_annotated(ANATOMY, ANATOMY_ANNOTS, here / "Warden Rule Anatomy.svg")
render(RULE, here / "Warden Rule Example.svg")
render(RULESET, here / "Warden Ruleset Example.svg")

# combined overview (header + every rule, blank-separated)
combined = list(HEADER)
for r in RULES.values():
    combined += [""] + r
render(combined, udocs / "Warden Examples Ruleset.svg")

# one snippet per rule
for slug, lines in RULES.items():
    render(lines, udocs / f"Warden Example {slug}.svg")
