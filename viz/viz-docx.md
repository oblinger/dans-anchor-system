# /viz docx — Markdown to DOCX via pandoc

Convert a markdown file to an editable Word document (`.docx`) using pandoc with a reference template for controlled styling. Use when you want to **polish in Word/Pages** before final delivery — tweak fonts, page breaks, image positioning, then export PDF yourself when satisfied.

For quick md → PDF without polishing, use `/viz pdf` instead.

## Tool

`pandoc` — install via `brew install pandoc`. Verify with `pandoc --version`.

## Usage

```
/viz docx <input.md> [--template <path>] [--output <path>]
```

- **input.md** — source markdown file (required).
- **--template** — path to a reference `.docx` that defines styles (fonts, headings, margins). Default: `~/.claude/skills/viz/template.docx`.
- **--output** — output path. Default: `~/ob/data/MyDesk/<slug>-<YYYY-MM-DD-HHMM>.docx` per the Viz default-output convention.

## Command

```bash
pandoc <input.md> -o <output.docx> --reference-doc=<template.docx>
```

If the input contains Obsidian-style wiki-links (`[[X]]`), preprocess first — see § Wiki-link handling.

## Reference-doc — the styling-control surface

The `--reference-doc` flag is the heart of controlled output. The template `.docx` defines:

- Fonts (Heading 1 / Heading 2 / Heading 3 / Normal body)
- Font sizes and weights
- Margins, page size, line spacing
- Default colors

A starter template ships at `~/.claude/skills/viz/template.docx` with sensible defaults (Inter headings, Charter body, 1" margins, US Letter). To customize:

1. Copy: `cp ~/.claude/skills/viz/template.docx ~/my-template.docx`
2. Open in Word or Pages.
3. Modify styles (Format → Styles, or right-click a style → Modify Style).
4. Save.
5. Use: `/viz docx report.md --template ~/my-template.docx`

You can also keep multiple templates (one per use case: memo, report, paper) and pass the right one per invocation.

## Wiki-link handling

Obsidian wiki-links aren't standard markdown. Pandoc renders `[[X]]` as literal text. To convert to readable form, preprocess with sed before invoking pandoc:

```bash
# Convert [[Name|Display]] → Display
# Convert [[Name]] → Name
sed -E 's/\[\[([^|]+)\|([^]]+)\]\]/\2/g; s/\[\[([^]]+)\]\]/\1/g' input.md > /tmp/input-clean.md
pandoc /tmp/input-clean.md -o output.docx --reference-doc=template.docx
```

For wiki-links → actual hyperlinks (pointing at relative file paths), use a pandoc lua filter — beyond the default workflow but available if needed.

## Workflow

1. **Compute output path** — slug from input filename + timestamp, under MyDesk (unless `--output` specified).
2. **Preprocess wiki-links** if any `[[X]]` appears in the input.
3. **Run pandoc** with the template.
4. **Print output path** so the user can `open <output.docx>`.

## When to use

- You want to **polish before delivering** — fonts, page breaks, image positioning, manual restructuring.
- Final delivery is PDF: use `/viz docx` → polish → export PDF from Word/Pages.
- Final delivery is DOCX: ship the file directly (clients/colleagues who expect Word).
- Iterating: edit markdown, regenerate docx, repolish minor diffs.

For quick md → PDF with no polishing, use `/viz pdf` instead.

## Verification

```bash
printf '# Smoke test\n\nBody text. **Bold** and *italic*. A [[wiki-link]] here.\n' > /tmp/smoke.md
sed -E 's/\[\[([^|]+)\|([^]]+)\]\]/\2/g; s/\[\[([^]]+)\]\]/\1/g' /tmp/smoke.md > /tmp/smoke-clean.md
pandoc /tmp/smoke-clean.md -o /tmp/smoke.docx --reference-doc=~/.claude/skills/viz/template.docx
open /tmp/smoke.docx
```

Expected: `/tmp/smoke.docx` opens in Word/Pages with the template's heading + body fonts applied; the wiki-link renders as the plain word "wiki-link."
