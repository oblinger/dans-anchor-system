#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# ///
"""md-toc: keep a markdown document's table of contents correct, or absent.

One idempotent pass decides all three questions the TOC discipline asks, so a
document only ever has the TOC it is entitled to:

  WHETHER  a doc at or above the size floor (default 3 pages, 500 words/page)
           and carrying at least two sections gets a TOC; anything smaller has
           its TOC removed.
  WHAT     top-level sections only when the full outline would be too long to
           scan (default > 25 entries), otherwise both levels.
  WHERE    directly below the H1's orientation line and directly above the
           heart — never above the H1, and never fused into the spine.

Run it as often as you like: same input, same output, no drift.

    md-toc.py <file.md> [--dry-run] [--pages 3] [--max-entries 25]

A TOC is recognized as the first markdown table whose header row contains
"Table of Contents". Content in columns beyond the first is preserved across
regeneration by matching on the heading title, so hand-written descriptions
survive. Links are Obsidian wiki-links: [[#heading text]].

See: [[DAS spine]] (the TOC is document content, not spine), CAB TOC Format.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

# --- Warden self-fire (fork 9 option A, 2026-07-13) -------------------------
# Script-written files bypass Warden's PostToolUse hook (agent tool calls
# only), so writer scripts report their own writes through the same dispatch
# path. Best-effort: Warden off/uninstalled means silence; never raises.
try:
    import importlib.util as _wsf_il
    _WSF_PATH = ((Path.home() / ".claude" / "skills").resolve().parent
                 / "warden" / "engine" / "warden_selffire.py")
    _wsf_spec = _wsf_il.spec_from_file_location("warden_selffire", _WSF_PATH)
    _warden_selffire = _wsf_il.module_from_spec(_wsf_spec)
    _wsf_spec.loader.exec_module(_warden_selffire)
except Exception:
    _warden_selffire = None


def _selffire(path):
    """Report a just-written markdown file to Warden (best-effort)."""
    if _warden_selffire is not None:
        _warden_selffire.fire_write(path)
# ---------------------------------------------------------------------------


# The spine shape decides whether a TOC is even a question. A list, stream or
# external spine IS an index: its rows already answer "what is here", and its
# H2s are entries rather than sections, so a TOC over one restates the page or
# lists dates. That classification has exactly one implementation — spine.py in
# the audit scripts — and a missing one is a hard error, never a quiet default.
_SPINE_PATH = Path.home() / '.claude' / 'skills' / 'audit' / 'scripts' / 'spine.py'
try:
    _spec = importlib.util.spec_from_file_location('spine', _SPINE_PATH)
    spine = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(spine)
except Exception as _e:                                   # pragma: no cover
    sys.exit(f'md-toc: cannot load the spine classifier at {_SPINE_PATH}: {_e}')


FIG_SPACE = ' '   # figure space — does not collapse in markdown renderers
PAGE_WORDS = 500       # one "page" of prose
DEFAULT_PAGES = 3      # size floor below which a doc gets no TOC
MAX_ENTRIES = 25       # full outline longer than this drops to top level only


# --- reading the document ---------------------------------------------------

def split_frontmatter(lines: list[str]) -> int:
    """Return the index of the first body line, skipping YAML frontmatter."""
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return i + 1
    return 0


def extract_headings(text: str, max_level: int = 3) -> list[dict]:
    """Extract H2..H{max_level} headings, skipping fenced code blocks."""
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
            level = len(m.group(1))
            if level <= max_level:
                headings.append({'level': level, 'title': m.group(2).strip()})
    return headings


def find_h1(lines: list[str]) -> int | None:
    """Index of the document's H1, outside frontmatter and fences."""
    in_code_block = False
    for i in range(split_frontmatter(lines), len(lines)):
        line = lines[i]
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r'^# \S', line):
            return i
    return None


def is_masthead_row(line: str) -> bool:
    """A dispatch masthead's identity row: '| -[[Name]]- | ... |'."""
    return bool(re.match(r'^\|\s*-\[\[', line))


def insertion_point(lines: list[str], h1: int) -> int:
    """Index where the TOC belongs: after the orientation line, before the heart.

    Skips `key:: value` inline fields (skill pages carry `requires::` there) and
    steps over a masthead table still sitting below the H1 — the pre-migration
    position — so the TOC never lands between a spine and the page it labels.
    """
    i = h1 + 1
    while i < len(lines) and (not lines[i].strip()
                              or re.match(r'^\w[\w-]*::', lines[i])):
        i += 1
    if i < len(lines) and not lines[i].startswith('|'):
        i += 1                                    # consume the orientation line
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and is_masthead_row(lines[i]):
        while i < len(lines) and lines[i].startswith('|'):
            i += 1
    return i


def find_toc_span(lines: list[str]) -> tuple[int, int] | None:
    """Line span [start, end) of the first 'Table of Contents' table."""
    for i, line in enumerate(lines):
        if re.match(r'^\|.*Table of Contents.*\|', line, re.IGNORECASE):
            if i + 1 < len(lines) and re.match(r'^\|[-| :]+\|', lines[i + 1]):
                j = i + 2
                while j < len(lines) and lines[j].startswith('|'):
                    j += 1
                return (i, j)
    return None


def parse_table_row(line: str) -> list[str]:
    """Split a markdown table row into cell contents, honoring escaped pipes.

    A character scanner, not a regex: TOC cells hold wiki-links whose display
    form is `[[Target\\|Display]]`, and every `[^|]*`-style pattern either stops
    at that escaped pipe or captures the backslash. Three separate vault
    measurements were wrong before this was written as a scanner (F319).
    """
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    cells, buf, k = [], [], 0
    while k < len(s):
        c = s[k]
        if c == '\\' and k + 1 < len(s):
            buf.append(s[k:k + 2])
            k += 2
            continue
        if c == '|':
            cells.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(c)
        k += 1
    cells.append(''.join(buf).strip())
    return cells


def extract_title_from_cell(cell: str) -> str | None:
    """Recover the heading title from a TOC cell (wiki-link or markdown link)."""
    m = re.search(r'\[\[#([^|\]]+)', cell)
    if m:
        return m.group(1)
    m = re.search(r'\[([^\]]+)\]\(#', cell)
    if m:
        return m.group(1)
    return None


def parse_existing_toc(lines: list[str], span) -> tuple[dict, int]:
    """Extra-column content keyed by heading title, plus the column count."""
    extra, num_cols = {}, 2
    if not span:
        return extra, num_cols
    start, end = span
    num_cols = len(parse_table_row(lines[start]))
    for k in range(start + 2, end):
        cells = parse_table_row(lines[k])
        title = extract_title_from_cell(cells[0]) if cells else None
        if title and len(cells) > 1:
            extra[title] = cells[1:]
    return extra, num_cols


# --- writing the table ------------------------------------------------------

def unlinkable(title: str) -> str | None:
    """Why `[[#title]]` cannot address this heading, or None if it can.

    Obsidian's heading link ends at the first `]]`, so a heading containing a
    wiki-link or a bare `]` is permanently untargetable — no escaping rescues
    it, and the fix is to rewrite the heading.
    """
    if '[[' in title:
        return 'contains a wiki-link'
    if ']' in title:
        return 'contains a `]`'
    if '#' in title:
        return 'contains a `#`'
    return None


def escape_cell(s: str) -> str:
    """Escape bare pipes so a heading with a `|` cannot split the table row."""
    return re.sub(r'(?<!\\)\|', r'\\|', s)


def generate_toc_table(headings, extra=None, num_cols=2) -> list[str]:
    """Build the TOC table (CAB TOC Format, Form 3)."""
    extra = extra or {}
    n_extra = num_cols - 1
    out = ['| ' + ' | '.join(['Table of Contents'] + [''] * n_extra) + ' |',
           '|' + '|'.join(['---'] * num_cols) + '|']
    for h in headings:
        indent = FIG_SPACE * 3 if h['level'] == 3 else ''
        bold = '**' if h['level'] == 2 else ''
        cell = f'{indent}{bold}[[#{escape_cell(h["title"])}]]{bold}'
        prev = extra.get(h['title'], [])
        tail = [prev[c] if c < len(prev) else '' for c in range(n_extra)]
        out.append('| ' + cell + ' | ' + ' | '.join(tail) + ' |')
    return out


# --- the decision -----------------------------------------------------------

def body_words(lines: list[str], toc_span) -> int:
    """Words in the document body, excluding frontmatter and the TOC itself."""
    start = split_frontmatter(lines)
    skip = set(range(*toc_span)) if toc_span else set()
    return sum(len(lines[i].split())
               for i in range(start, len(lines)) if i not in skip)


def choose_depth(text: str, max_entries: int) -> tuple[int, list[dict]]:
    """Both levels when the full outline is scannable; top level when it isn't.

    A doc with fewer than two top-level sections keeps both levels regardless —
    a one-row TOC is not a table of contents.
    """
    full = extract_headings(text, 3)
    tops = [h for h in full if h['level'] == 2]
    if len(full) <= max_entries or len(tops) < 2:
        return 3, full
    return 2, tops


def plan(path: Path, pages: int, page_words: int, max_entries: int):
    """Decide what this file's TOC should be. Returns (action, new_lines, note)."""
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        # Never rewrite a file we cannot read losslessly — a replacement-char
        # round-trip would silently corrupt whatever bytes we failed to decode.
        return 'skip', None, 'not valid UTF-8', []
    lines = text.split('\n')
    span = find_toc_span(lines)
    words = body_words(lines, span)
    floor = pages * page_words
    h1 = find_h1(lines)

    depth, headings = choose_depth(text, max_entries)
    warnings = [f'{h["title"][:60]} — {why}'
                for h in extract_headings(text, 3)
                if (why := unlinkable(h['title']))]

    shape = spine.Spine(path, list(lines)).shape()
    eligible = shape in spine.TOC_ELIGIBLE
    wants = eligible and words >= floor and len(headings) >= 2
    note = f'{shape} spine, {words} words ({words / page_words:.1f} pages), floor {floor}'
    why = (f'{shape} spine is an index — never a TOC' if not eligible
           else 'below floor')

    if not wants:
        if span is None:
            return 'none', lines, note + f' — no TOC ({why}), correct', []
        out = lines[:span[0]] + lines[span[1]:]
        while out and span[0] < len(out) and not out[span[0]].strip():
            del out[span[0]]
        return 'delete', out, note + f' — {why}, TOC removed', []

    if h1 is None:
        return 'none', lines, note + ' — no H1, skipped', []

    extra, num_cols = parse_existing_toc(lines, span)
    table = generate_toc_table(headings, extra, num_cols)

    body = lines[:span[0]] + lines[span[1]:] if span else list(lines)
    if span:
        while span[0] < len(body) and not body[span[0]].strip():
            del body[span[0]]
    h1b = find_h1(body)
    at = insertion_point(body, h1b)
    # Absorb the blank lines on both sides of the insertion point rather than
    # adding to them, so the table is always framed by exactly one blank line
    # and a re-run cannot accrete another.
    start = at
    while start > 0 and not body[start - 1].strip():
        start -= 1
    while at < len(body) and not body[at].strip():
        at += 1
    out = body[:start] + [''] + table + [''] + body[at:]

    lvl = 'top level only' if depth == 2 else 'both levels'
    detail = f'{note} — {len(headings)} entries, {lvl}'
    if out == lines:
        return 'ok', lines, detail, warnings
    if span is None:
        return 'insert', out, detail, warnings
    return ('update' if span[0] == start + 1 else 'move'), out, detail, warnings


def main():
    ap = argparse.ArgumentParser(
        description='Create, update, move, or remove a document\'s table of contents.')
    ap.add_argument('file', type=Path, nargs='+', help='Markdown file(s)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Report the decision without writing')
    ap.add_argument('--pages', type=int, default=DEFAULT_PAGES,
                    help=f'Size floor in pages (default {DEFAULT_PAGES})')
    ap.add_argument('--page-words', type=int, default=PAGE_WORDS,
                    help=f'Words per page (default {PAGE_WORDS})')
    ap.add_argument('--max-entries', type=int, default=MAX_ENTRIES,
                    help=f'Above this, top-level only (default {MAX_ENTRIES})')
    args = ap.parse_args()

    rc = 0
    for f in args.file:
        if not f.exists():
            print(f'Error: {f} not found', file=sys.stderr)
            rc = 1
            continue
        result = plan(f, args.pages, args.page_words, args.max_entries)
        action, out, note = result[0], result[1], result[2]
        warnings = result[3] if len(result) > 3 else []
        print(f'{f.name}: {action} — {note}')
        for w in warnings:
            print(f'  ! unlinkable heading: {w}')
        if args.dry_run and action in ('insert', 'update', 'move', 'ok'):
            s = find_toc_span(out)
            if s:
                print('\n'.join(out[s[0]:s[1]]))
        if action not in ('none', 'ok', 'skip') and not args.dry_run:
            f.write_text('\n'.join(out))
            _selffire(f)
    sys.exit(rc)


if __name__ == '__main__':
    main()
