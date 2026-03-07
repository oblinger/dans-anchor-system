#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# ///
"""cab-toc: Generate a table of contents from markdown headings.

Reads a markdown file, extracts H2 and H3 headings, and generates a TOC
in the CAB TOC Format (Form 3: Table). Replaces the existing TOC table
in the file.

Usage:
    cab-toc.py <file.md>

The TOC is identified as the first markdown table whose header row contains
"Table of Contents". If no such table exists, the TOC is printed to stdout.

When replacing an existing TOC, the script preserves content from columns
beyond the first (descriptions, notes, etc.) by matching on the heading title.
The number of columns is preserved from the existing table.

Links are Obsidian wiki-links: [[#heading text]].

See: CAB TOC Format (Common Anchor Form > CAB Markdown)
"""

import argparse
import re
import sys
from pathlib import Path

FIG_SPACE = '\u2007'  # figure space — does not collapse in markdown renderers


def extract_headings(text: str) -> list[dict]:
    """Extract H2 and H3 headings from markdown text, skipping code blocks."""
    headings = []
    in_code_block = False
    for line in text.split('\n'):
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = re.match(r'^(#{2,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))  # 2 or 3
            title = m.group(2).strip()
            headings.append({
                'level': level,
                'title': title,
            })
    return headings


def parse_table_row(line: str) -> list[str]:
    """Split a markdown table row into cell contents.

    '| foo | bar | baz |' -> ['foo', 'bar', 'baz']
    """
    stripped = line.strip().strip('|')
    return [cell.strip() for cell in stripped.split('|')]


def extract_title_from_cell(cell: str) -> str | None:
    """Extract the heading title from a TOC cell.

    Handles both wiki-links and markdown links:
      '**[[#1.4.3 Roadmap]]**' -> '1.4.3 Roadmap'
      '[[#1.4.3 Roadmap|Roadmap]]' -> '1.4.3 Roadmap'
      '**[1.4.3 Roadmap](#1-4-3-roadmap)**' -> '1.4.3 Roadmap'
    """
    # Wiki-link: [[#title]] or [[#title|display]]
    m = re.search(r'\[\[#([^|\]]+)', cell)
    if m:
        return m.group(1)
    # Markdown link: [title](#anchor)
    m = re.search(r'\[([^\]]+)\]\(#', cell)
    if m:
        return m.group(1)
    return None


def parse_existing_toc(text: str) -> tuple[dict[str, list[str]], int]:
    """Parse the existing TOC table and extract extra-column data.

    Returns:
        - dict mapping heading title -> list of strings (one per extra column)
        - number of columns in the existing table
    """
    extra = {}
    num_cols = 2  # default
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        if re.match(r'^\|.*Table of Contents.*\|', lines[i], re.IGNORECASE):
            cells = parse_table_row(lines[i])
            num_cols = len(cells)
            i += 2  # skip separator row
            while i < len(lines) and lines[i].startswith('|'):
                cells = parse_table_row(lines[i])
                title = extract_title_from_cell(cells[0]) if cells else None
                if title and len(cells) > 1:
                    extra[title] = cells[1:]
                i += 1
            break
        i += 1
    return extra, num_cols


def generate_toc_table(headings: list[dict], existing: dict[str, list[str]] = None,
                       num_cols: int = 2) -> str:
    """Generate a TOC in CAB TOC Format (Form 3: Table)."""
    if existing is None:
        existing = {}
    extra_cols = num_cols - 1

    # Header row
    header_cells = ['Table of Contents'] + [''] * extra_cols
    header = '| ' + ' | '.join(header_cells) + ' |'

    # Separator row
    sep = '|' + '|'.join(['---'] * num_cols) + '|'

    lines = [header, sep]
    for h in headings:
        indent = FIG_SPACE * 3 if h['level'] == 3 else ''
        bold_start = '**' if h['level'] == 2 else ''
        bold_end = '**' if h['level'] == 2 else ''
        link = f'[[#{h["title"]}]]'
        first_cell = f'{indent}{bold_start}{link}{bold_end}'

        # Reuse existing extra-column content if available
        prev = existing.get(h['title'], [])
        extra = []
        for c in range(extra_cols):
            if c < len(prev):
                extra.append(prev[c])
            else:
                extra.append('')

        row = '| ' + first_cell + ' | ' + ' | '.join(extra) + ' |'
        lines.append(row)
    return '\n'.join(lines)


def find_toc_table(text: str) -> tuple[int, int] | None:
    """Find the first markdown table whose header contains 'Table of Contents'.

    Returns (start, end) character offsets, or None if not found.
    """
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\|.*Table of Contents.*\|', line, re.IGNORECASE):
            if i + 1 < len(lines) and re.match(r'^\|[-| :]+\|', lines[i + 1]):
                table_start = sum(len(l) + 1 for l in lines[:i])
                j = i + 2
                while j < len(lines) and lines[j].startswith('|'):
                    j += 1
                table_end = sum(len(l) + 1 for l in lines[:j])
                if table_end > 0:
                    table_end -= 1
                return (table_start, table_end)
        i += 1
    return None


def update_file(path: Path, headings: list[dict]) -> bool:
    """Replace the TOC table in the file, preserving extra columns.

    Returns True if updated.
    """
    text = path.read_text()
    span = find_toc_table(text)
    if span:
        start, end = span
        existing_table_text = text[start:end]
        existing, num_cols = parse_existing_toc(existing_table_text)
        toc = generate_toc_table(headings, existing, num_cols)
        new_text = text[:start] + toc + text[end:]
        path.write_text(new_text)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate a table of contents from markdown headings.'
    )
    parser.add_argument('file', type=Path, help='Markdown file to process')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print TOC to stdout without modifying the file')
    args = parser.parse_args()

    if not args.file.exists():
        print(f'Error: {args.file} not found', file=sys.stderr)
        sys.exit(1)

    text = args.file.read_text()
    headings = extract_headings(text)

    if not headings:
        print('No H2/H3 headings found.', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        existing, num_cols = parse_existing_toc(text)
        toc = generate_toc_table(headings, existing, num_cols)
        print(toc)
        return

    if update_file(args.file, headings):
        print(f'Updated TOC in {args.file} ({len(headings)} entries)')
    else:
        toc = generate_toc_table(headings)
        print('No TOC table found (header must contain "Table of Contents").')
        print('Printing to stdout:\n')
        print(toc)


if __name__ == '__main__':
    main()
