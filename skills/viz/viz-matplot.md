# /viz matplot — Matplotlib chart generation via vizcharts.py

Generate Tufte-grade static charts using `vizcharts.py`, a 1,162-line matplotlib chart tool. Output is `.png` suitable for PM artifacts, reports, and slide decks.

## Tool

`vizcharts.py` ships with this skill at `~/.claude/skills/viz/vizcharts.py`.

## Available chart types

| Type | Use when |
|---|---|
| `timeline` | Sequential events / project milestones along a time axis |
| `multi_line` | Multiple time-series on shared axes (e.g., metrics over time) |
| `quadrant` | 2×2 categorization of items (e.g., effort × impact) |
| `scatter` | Bivariate point cloud, optionally with regression |
| `rankings` | Ordered list with bar magnitudes (e.g., team velocity ranking) |
| `comparison` | Side-by-side comparison of categories (e.g., before/after) |
| `stacked_bar` | Composition of categories across groups |
| `donut` | Composition of one whole (use sparingly per Tufte) |
| `waterfall` | Sequential additive/subtractive contributions to a total |
| `hex_shot` | Hex-grid heatmap (originally for shot-location density; reusable) |

## Usage

```bash
python3 ~/.claude/skills/viz/vizcharts.py <chart_type> <input.json> --output <output.png> [--theme <theme>]
```

Themes (after F034): `light` (default), `dark`, `neutral`.

## Workflow

1. **Determine chart type** from user intent. If ambiguous, ask which of the 10 types fits — naming the closest 2–3 candidates.
2. **Prepare input data** as JSON in the schema vizcharts.py expects (per chart type — see vizcharts.py docstrings or `examples/` if present).
3. **Run the tool** to produce the .png.
4. **Show the output** — `open <output.png>` so the user can review.
5. **Iterate** — if styling needs adjustment, tweak input or call options and re-run.

## Status / known issues

- **Font fallback** — vizcharts.py hard-codes Sean O'Connor's `Roobert` font path. On other machines, matplotlib falls back to DejaVu Sans (visible in 2026-05-08 demo at `/tmp/vizcharts-demo-arr.png`).
- **Northwind brand leak** — accent color `#FF4C57` (brand red) appears in milestone markers and some chart elements; F034 introduces a `neutral` theme that strips brand colors.

See [[2026-05-08 Professionalize vizcharts]] for the active work to address these.

## Driving feature

[[F020 — Take-Home Velocity Tooling]] in [[LRN TPM]] — Anthropic Alignment Special Ops TPM take-home; vizcharts.py provides the chart layer for that submission.
