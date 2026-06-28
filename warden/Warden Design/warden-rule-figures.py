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
    if s.startswith("#"):
        return "#7b2d52", "bold"      # heading / sentinel
    if FIELD.match(line):
        return "#2d5b7b", "normal"    # :: field
    if PYLINE.match(line):
        return "#2f7d4f", "normal"    # embedded python
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
    for line in lines:
        if line.strip():
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
    # the body shows the kind (check:: / python / prose); no tier needed.
    # passive (no when::) rules run at /audit time; live ones declare when::.
    "primitive": [
        "### RULE R-ex-01 — Has a description",
        "where:: `{ANCHOR}/**/R-*.md`",
        "check:: regex_present `^description::`",
    ],
    "python": [
        "### RULE R-ex-02 — Every H2 section has a body",
        "where:: `{ANCHOR}/**/*.md`",
        "```python",
        "def check(ctx):",
        "    for sec in ctx.sections(level=2):",
        "        if not sec.body.strip():",
        "            ctx.report(f'empty section: {sec.title}')",
        "```",
    ],
    "llm": [
        "### RULE R-ex-03 — Summary matches the body",
        "where:: `{ANCHOR}/**/F[0-9][0-9][0-9] — *.md`",
        "The ## Summary faithfully reflects ## Design — no drift.",
    ],
    "script-assisted": [
        "### RULE R-ex-04 — Open Questions still open",
        "where:: `{ANCHOR}/**/*.md`",
        "```python",
        "def prepare(ctx):     # cheap: hand the LLM only one section",
        "    return ctx.section('## Open Questions')",
        "```",
        "Judge each item prepare() returns: still unresolved? Report stale ones.",
    ],
    "message": [
        "### RULE R-ex-05 — Don't ask whether to commit",
        "when:: skill:audit-q",
        "where:: `{ANCHOR}/**/{NAME} queries.md`",
        "```python",
        "def check(ctx):",
        "    if ctx.has_question('push', 'commit'):",
        "        ctx.report(steer_for(ctx.git_aspect))  # tell the agent, don't ask",
        "```",
    ],
    "gated": [
        "### RULE R-ex-06 — Diagram matches prose",
        "where:: `{ANCHOR}/**/*Architecture*.md`",
        "when:: write:markdown",
        "rerun:: significant",
        "The figure reflects the components in the prose; report drift.",
    ],
}

here = Path(__file__).parent
udocs = here.parent / "Warden User Docs"
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
