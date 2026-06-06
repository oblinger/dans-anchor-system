#!/usr/bin/env python3
"""audit-api-doc.py — CAB API Doc facet conformance checker (F119).

Validates a target Markdown file against the [[CAB API Doc]] facet rules.
Mirrors audit-q.py + audit-architecture.py patterns. Emits warnings with
line numbers and rule references (C1..C26). --fix flag auto-repairs the
mechanical checks (C3, C21, C22, C23, C24).

Usage:
  audit-api-doc <path>                   # report-only
  audit-api-doc <path> --fix             # apply mechanical fixes
  audit-api-doc <path> --dry             # report-only AND refuse to write

Per F119 v1: standard check set (26 checks across top-of-doc, figure, SECTIONS,
per-class blocks, Class Method Details zone, spacing, method body, linking).
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import argparse
import re
import sys


# ============================================================
# Findings
# ============================================================

@dataclass
class Finding:
    rule: str            # e.g. "C1"
    line: int            # 1-based line number; 0 = file-level
    message: str
    fixable: bool = False

    def fmt(self, path: Path) -> str:
        loc = f"{path}:{self.line}" if self.line else f"{path}"
        return f"  [{self.rule}] {loc}: {self.message}"


# ============================================================
# Parsing primitives
# ============================================================

H2_PATTERN = re.compile(r'^## +(.+?)\s*$')
H1_PATTERN = re.compile(r'^# +(.+?)\s*$')
H3_PATTERN = re.compile(r'^### +(.+?)\s*$')
BLOCK_ID_PATTERN = re.compile(r'\^([A-Za-z0-9_\-]+)\b')
WIKI_EMBED_SVG_PATTERN = re.compile(r'!\[\[([^\]\|]+\.svg)(?:\|\d+)?\]\]')
SECTIONS_HEADER_PATTERN = re.compile(r'^\|\s*SECTIONS\s*\|\s*Role\s*\|', re.IGNORECASE)
SECTIONS_ROW_PATTERN = re.compile(
    r'^\|\s*\[\[#\^([A-Za-z0-9_\-]+)(?:\\?\|([^\]]+))?\]\]\s*([A-Za-z\-]*)\s*\|'
)
CLASS_TABLE_HEADER_PATTERN = re.compile(r'^\|\s*([A-Z][A-Z0-9 \-]+)\s*\|\s*Description\s*\|')
FIELD_ROW_PATTERN = re.compile(r'^\|\s*\*\*`([^`]+)`\*\*`([^`]*)`')
METHOD_ROW_PATTERN = re.compile(
    r'^\|\s*\*\*\[\[#\^([A-Za-z0-9_\-]+)\\?\|([^\]]+)\]\]\*\*`([^`]*)`'
)
METHODS_DIVIDER_PATTERN = re.compile(r'^\|\s*\*\*Methods\*\*\s*\|\s*\|?\s*$')
METHOD_H3_PATTERN = re.compile(r'^### +`([^`]+)`(?:\s+\^([A-Za-z0-9_\-]+))?')
TOPIC_BULLET_PATTERN = re.compile(r'^- +\*\*[^*]+\*\*\s*[—-]\s*')


def parse_lines(text: str) -> list[str]:
    """Split text into lines, preserving line numbers."""
    return text.splitlines()


def find_h1s(lines: list[str]) -> list[tuple[int, str]]:
    return [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := H1_PATTERN.match(line))]


def find_h2s(lines: list[str]) -> list[tuple[int, str]]:
    return [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := H2_PATTERN.match(line))]


def find_h3s(lines: list[str]) -> list[tuple[int, str]]:
    return [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := H3_PATTERN.match(line))]


def find_all_block_ids(text: str) -> set[str]:
    """Every ^block-id reference in the doc."""
    return set(BLOCK_ID_PATTERN.findall(text))


# ============================================================
# Checks
# ============================================================

def check_top_of_doc(lines: list[str], text: str) -> list[Finding]:
    findings = []
    # C1: YAML frontmatter present with description:
    if not text.startswith('---'):
        findings.append(Finding("C1", 1, "missing YAML frontmatter (expected `---` opener)"))
    else:
        end = text.find('\n---', 4)
        if end < 0:
            findings.append(Finding("C1", 1, "YAML frontmatter not closed (missing `---` terminator)"))
        else:
            fm = text[4:end]
            if not re.search(r'^description\s*:', fm, re.MULTILINE):
                findings.append(Finding("C1", 1, "frontmatter missing `description:` field"))

    # C2: H1 matches `# {NAME} {ModuleName}` form (basic — first H1 exists)
    h1s = find_h1s(lines)
    if not h1s:
        findings.append(Finding("C2", 0, "no H1 found; expected `# {NAME} {ModuleName}`"))
    elif len(h1s) > 2:
        # Allow 2 H1s: file H1 + "Class Method Details"
        findings.append(Finding("C2", h1s[2][0], f"unexpected third H1 `{h1s[2][1]}`; spec allows file H1 + Class Method Details only"))

    # C3: No blank line between H1 and file overview prose (compact rule)
    if h1s:
        h1_line = h1s[0][0]  # 1-based
        if h1_line < len(lines):
            next_line = lines[h1_line]  # 0-based index = 1-based line
            if next_line.strip() == '':
                findings.append(Finding("C3", h1_line + 1, "blank line after H1; spec says H1+overview is compact (no blank)", fixable=True))

    # C4: breadcrumb `:>>` line present (optional; warn if absent — informational)
    has_breadcrumb = any(line.startswith(':>>') for line in lines)
    if not has_breadcrumb:
        findings.append(Finding("C4", 0, "no `:>>` breadcrumb line found (optional but recommended)"))

    return findings


def check_figure(lines: list[str], doc_path: Path) -> list[Finding]:
    findings = []
    # C5: Figure reference present
    embed_match = None
    embed_line = 0
    for i, line in enumerate(lines):
        m = WIKI_EMBED_SVG_PATTERN.search(line)
        if m:
            embed_match = m
            embed_line = i + 1
            break
    if not embed_match:
        findings.append(Finding("C5", 0, "no SVG figure embed found; spec requires `![[file.svg]]` near top"))
        return findings

    svg_basename = embed_match.group(1)
    # C6: Referenced SVG file exists on disk (look in same folder as the .md)
    svg_path = doc_path.parent / svg_basename
    if not svg_path.is_file():
        findings.append(Finding("C6", embed_line, f"referenced SVG `{svg_basename}` not found at `{svg_path}`"))

    # C7: Excalidraw source `.excalidraw` exists alongside
    excal_path = svg_path.with_suffix('.excalidraw')
    if not excal_path.is_file():
        findings.append(Finding("C7", embed_line, f"Excalidraw source `{excal_path.name}` not found alongside SVG"))

    return findings


def check_sections_table(lines: list[str], text: str) -> tuple[list[Finding], list[tuple[str, str, str]]]:
    """C8-C10. Returns findings + list of (block_id, name, type) parsed from SECTIONS rows."""
    findings = []
    sections_rows: list[tuple[str, str, str]] = []

    # C8: SECTIONS header present
    header_line = None
    for i, line in enumerate(lines):
        if SECTIONS_HEADER_PATTERN.match(line):
            header_line = i + 1
            break
    if header_line is None:
        findings.append(Finding("C8", 0, "no `| SECTIONS | Role |` header row found"))
        return findings, sections_rows

    # Walk subsequent rows until we hit a non-table line
    i = header_line  # next index in 0-based
    # Skip separator row
    if i < len(lines) and lines[i].lstrip().startswith('|') and '---' in lines[i]:
        i += 1
    while i < len(lines):
        line = lines[i]
        if not line.lstrip().startswith('|'):
            break
        m = SECTIONS_ROW_PATTERN.match(line)
        if m:
            block_id = m.group(1)
            name = m.group(2) or m.group(1)
            type_word = m.group(3).strip()
            sections_rows.append((block_id, name, type_word))
            # C9: row has form `[[#^anchor|Name]] type` — type lowercase after the link
            if not type_word:
                findings.append(Finding("C9", i + 1, f"SECTIONS row for `{name}` missing type word (class/topic/enum/struct/etc.)"))
            elif type_word != type_word.lower():
                findings.append(Finding("C9", i + 1, f"SECTIONS row type word `{type_word}` should be lowercase"))
        else:
            # Looks like a table row but doesn't match the expected SECTIONS pattern
            if line.strip().startswith('|') and not line.strip().startswith('| ---'):
                # Try to detect rows that lack block-ID link
                if '[[#' not in line:
                    findings.append(Finding("C9", i + 1, f"SECTIONS row missing `[[#^...]]` block-ID link"))
        i += 1

    # C10: Every SECTIONS row's block-ID target exists somewhere in the doc
    all_block_ids = find_all_block_ids(text)
    for bid, name, _ in sections_rows:
        # Each block-ID should appear at least TWICE — once in SECTIONS row, once as the target
        if list(BLOCK_ID_PATTERN.findall(text)).count(bid) < 2:
            findings.append(Finding("C10", 0, f"SECTIONS row for `{name}` references `^{bid}` but no target block-ID found in doc"))

    return findings, sections_rows


def check_overview_h2s(lines: list[str], text: str, sections_rows: list[tuple[str, str, str]]) -> tuple[list[Finding], int]:
    """C11-C17. Walks overview-zone H2s (everything before `# Class Method Details` H1).
    Returns findings + line number where overview zone ends (or len(lines) if no details zone)."""
    findings = []

    # Find Class Method Details H1
    details_h1_line = None
    for i, line in enumerate(lines):
        if H1_PATTERN.match(line) and 'Class Method Details' in line:
            details_h1_line = i + 1
            break
    overview_end = details_h1_line if details_h1_line else len(lines) + 1

    # Walk H2s in overview zone
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        m = H2_PATTERN.match(line)
        if not m:
            continue
        h2_name = m.group(1)
        # Skip See Also and other meta H2s
        if h2_name.lower() in ('see also', 'related'):
            continue
        # C11: H2 matches "Name Type" form (Type capitalized)
        # Parse: split on space, last word should be capitalized type keyword
        parts = h2_name.rsplit(' ', 1)
        if len(parts) < 2 or parts[1] not in ('Class', 'Enum', 'Struct', 'Topic', 'Protocol', 'Interface', 'Trait', 'Record'):
            findings.append(Finding("C11", i + 1, f"H2 `{h2_name}` should end with a Type qualifier (Class/Enum/Topic/Struct/Protocol/Interface/Trait/Record)"))

        # C12: H2 followed by description prose with block-ID inline at end
        # Look at next non-blank line within ~3 lines
        for j in range(i + 1, min(i + 5, overview_end - 1)):
            nl = lines[j]
            if nl.strip() == '':
                continue
            if nl.startswith('#'):
                findings.append(Finding("C12", i + 1, f"H2 `{h2_name}` not followed by description prose"))
                break
            # Description line — check for block-ID at end
            if '^' not in nl:
                findings.append(Finding("C12", j + 1, f"H2 `{h2_name}` description missing inline block-ID at end (`...text.^Name`)"))
            break

    # C13-C17: Walk class tables in overview zone
    in_class_table = False
    table_header_line = 0
    saw_methods_divider = False
    has_methods = False
    has_fields = False
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        # Detect class table header
        m = CLASS_TABLE_HEADER_PATTERN.match(line)
        if m:
            in_class_table = True
            table_header_line = i + 1
            saw_methods_divider = False
            has_methods = False
            has_fields = False
            continue
        if not in_class_table:
            continue
        # Exit on non-table line
        if not line.lstrip().startswith('|'):
            in_class_table = False
            continue
        # Skip separator row
        if '---' in line:
            continue
        # C14: field row form
        field_m = FIELD_ROW_PATTERN.match(line)
        if field_m:
            has_fields = True
            continue
        # Methods divider
        if METHODS_DIVIDER_PATTERN.match(line):
            saw_methods_divider = True
            continue
        # C15: method row form (backticks NOT inside the wiki-link alias)
        method_m = METHOD_ROW_PATTERN.match(line)
        if method_m:
            has_methods = True
            continue
        # If we see a row that has bold-link-inside-alias form (broken), flag
        if re.search(r'\[\[#\^[^\]]+\\?\|\*\*`[^`]+`\*\*\]\]', line):
            findings.append(Finding("C15", i + 1, "method row has backticks INSIDE wiki-link alias — Obsidian won't render. Use `**[[#^anchor|name]]**` outside, `` `(args)` `` outside."))
            continue
        # If looks like a method row but doesn't match expected pattern
        if line.lstrip().startswith('| **') and '**`' in line and not field_m and not METHODS_DIVIDER_PATTERN.match(line):
            # Probably a method row in some non-canonical form
            findings.append(Finding("C14", i + 1, "row form unclear — expected `**`name`**`: Type`` (field) or `**[[#^anchor|name]]**`(args) -> R`` (method)"))

    # Build list of method block-IDs referenced in overview-zone class tables
    method_link_refs: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        for m in re.finditer(r'\*\*\[\[#\^([A-Za-z0-9_\-]+)\\?\|', line):
            method_link_refs.append((i + 1, m.group(1)))

    # C17: each method link's block-ID target exists as an H3 in Class Method Details
    if details_h1_line:
        details_block_ids = set()
        for i, line in enumerate(lines):
            if i + 1 < details_h1_line:
                continue
            m = METHOD_H3_PATTERN.match(line)
            if m and m.group(2):
                details_block_ids.add(m.group(2))
            for bm in BLOCK_ID_PATTERN.findall(line):
                details_block_ids.add(bm)
        for line_no, bid in method_link_refs:
            if bid not in details_block_ids:
                findings.append(Finding("C17", line_no, f"method link `^{bid}` has no matching H3 block-ID in Class Method Details"))
    elif method_link_refs:
        findings.append(Finding("C18", 0, "method links exist but no `# Class Method Details` H1 found"))

    return findings, overview_end


def check_class_method_details(lines: list[str], overview_end: int) -> list[Finding]:
    """C18-C20, C24. Walk Class Method Details zone."""
    findings = []
    if overview_end > len(lines):
        return findings

    # C18: details H1 exists (handled above; check here that we have at least one H3 with block-ID)
    seen_method_h3 = False
    for i in range(overview_end - 1, len(lines)):
        line = lines[i]
        m = METHOD_H3_PATTERN.match(line)
        if m and m.group(2):
            seen_method_h3 = True
            # C20: block-ID format `^ClassName-methodname` — at least one hyphen between class and method
            bid = m.group(2)
            if '-' not in bid:
                findings.append(Finding("C20", i + 1, f"method block-ID `^{bid}` should follow `^ClassName-methodname` form (with hyphen)"))

    # C19: each per-class H2 in details zone matches a class in overview (heuristic — just check H2s exist)
    detail_h2s = []
    for i in range(overview_end - 1, len(lines)):
        m = H2_PATTERN.match(lines[i])
        if m:
            detail_h2s.append((i + 1, m.group(1)))

    # C24: method body uses italic *Args:* + merged bullet list. Heuristic: look for old-style **Args:** bold heading
    for i in range(overview_end - 1, len(lines)):
        line = lines[i]
        if re.match(r'^\*\*Args:\*\*\s*$', line):
            findings.append(Finding("C24", i + 1, "use italic `*Args:*` heading (merged bullet form), not bold `**Args:**`", fixable=True))
        if re.match(r'^\*\*Returns:\*\*', line):
            findings.append(Finding("C24", i + 1, "Returns should be a bullet within the Args list with italic label: `- *Returns:* **type** — ...`", fixable=False))
        if re.match(r'^\*\*Raises:\*\*\s*$', line):
            findings.append(Finding("C24", i + 1, "Raises should be a bullet within the Args list with italic label: `- *Raises:* **type** if ...`", fixable=False))

    return findings


def check_spacing(lines: list[str]) -> list[Finding]:
    """C21-C23. Spacing rules."""
    findings = []

    # C22: 2 blank lines before each H2 (overview zone)
    # Find the Class Method Details H1 line
    details_h1_idx = None
    for i, line in enumerate(lines):
        if H1_PATTERN.match(line) and 'Class Method Details' in line:
            details_h1_idx = i
            break

    for i, line in enumerate(lines):
        if not H2_PATTERN.match(line):
            continue
        # Skip the first H2 if very close to the start (right after SECTIONS table is OK)
        # Compute blank lines immediately before
        blanks = 0
        j = i - 1
        while j >= 0 and lines[j].strip() == '':
            blanks += 1
            j -= 1
        # Don't enforce on very first H2 or H2 right after Class Method Details H1
        if j < 0:
            continue
        if details_h1_idx is not None and j == details_h1_idx:
            continue
        if blanks != 2 and blanks > 0:  # 0 means no blank at all (different bug); 1 or 3+ is the spacing issue
            findings.append(Finding("C22", i + 1, f"expected 2 blank lines before H2, found {blanks}", fixable=True))

    # C23: 7 blank lines before `# Class Method Details` H1
    if details_h1_idx is not None and details_h1_idx > 0:
        blanks = 0
        j = details_h1_idx - 1
        while j >= 0 and lines[j].strip() == '':
            blanks += 1
            j -= 1
        if blanks != 7:
            findings.append(Finding("C23", details_h1_idx + 1, f"expected 7 blank lines before `# Class Method Details`, found {blanks}", fixable=True))

    # C21: 0 blank lines after H1 and after every overview-zone H2 (compact rule)
    for i, line in enumerate(lines):
        if H1_PATTERN.match(line) or H2_PATTERN.match(line):
            # Skip if this H2 is "See Also" or "Related"
            m = H2_PATTERN.match(line)
            if m and m.group(1).lower() in ('see also', 'related'):
                continue
            # Skip the Class Method Details H1
            if H1_PATTERN.match(line) and 'Class Method Details' in line:
                continue
            # Check next line is non-blank
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                findings.append(Finding("C21", i + 2, f"blank line after `{line.strip()}`; spec says compact (no blank between heading and prose)", fixable=True))

    return findings


def check_linking(lines: list[str], doc_path: Path) -> list[Finding]:
    """C25-C26. Doc is referenced from Dev.md and appears in Files.md."""
    findings = []
    # Heuristic: walk up to find a `{NAME} Dev.md` and `{NAME} Files.md` and check if our basename appears
    basename = doc_path.stem
    parent = doc_path.parent

    # Look for {NAME} Dev.md in parent or grandparent
    dev_md = None
    files_md = None
    for ancestor in [parent, parent.parent, parent.parent.parent]:
        if not ancestor.exists():
            continue
        for f in ancestor.glob('* Dev.md'):
            dev_md = f
            break
        for f in ancestor.glob('* Files.md'):
            files_md = f
            break
        if dev_md and files_md:
            break

    if dev_md:
        try:
            if basename not in dev_md.read_text():
                findings.append(Finding("C25", 0, f"doc `{basename}` not referenced in `{dev_md.name}` dispatch table"))
        except OSError:
            pass

    if files_md:
        try:
            if basename not in files_md.read_text():
                findings.append(Finding("C26", 0, f"doc `{basename}` not referenced in `{files_md.name}` Files tree"))
        except OSError:
            pass

    return findings


# ============================================================
# Auto-fix
# ============================================================

def apply_fixes(text: str) -> str:
    """Apply mechanical fixes for C3, C21, C22, C23, C24."""
    lines = text.splitlines(keepends=False)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        # C3 / C21: collapse blank line right after H1/H2 (compact rule), except "See Also"-style H2s and Class Method Details H1
        if (H1_PATTERN.match(line) or H2_PATTERN.match(line)):
            m2 = H2_PATTERN.match(line)
            is_meta = m2 and m2.group(1).lower() in ('see also', 'related')
            is_details = H1_PATTERN.match(line) and 'Class Method Details' in line
            if not is_meta and not is_details:
                # Skip exactly one blank if present
                if i + 1 < len(lines) and lines[i + 1].strip() == '':
                    i += 2
                    continue
        i += 1

    text = '\n'.join(out)

    # C24: convert old-style **Args:** to *Args:*
    text = re.sub(r'^\*\*Args:\*\*\s*$', '*Args:*', text, flags=re.MULTILINE)

    # C22 / C23: normalize blank-line runs before H2s and the Class Method Details H1
    # Strategy: walk through text, when we see N blank lines followed by an H2/H1, normalize N
    lines = text.splitlines(keepends=False)
    out = []
    i = 0
    while i < len(lines):
        # Detect run of blank lines
        if lines[i].strip() == '':
            # Find end of blank run
            j = i
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            # What follows?
            if j < len(lines):
                next_line = lines[j]
                if H1_PATTERN.match(next_line) and 'Class Method Details' in next_line:
                    # Normalize to exactly 7 blank lines
                    out.extend([''] * 7)
                    i = j
                    continue
                elif H2_PATTERN.match(next_line):
                    m2 = H2_PATTERN.match(next_line)
                    is_meta = m2.group(1).lower() in ('see also', 'related')
                    # Skip normalization for See Also (let it follow whatever spacing the user has)
                    if not is_meta:
                        out.extend([''] * 2)
                        i = j
                        continue
            # No special case — preserve as-is
            out.extend(lines[i:j])
            i = j
            continue
        out.append(lines[i])
        i += 1

    return '\n'.join(out) + ('\n' if text.endswith('\n') else '')


# ============================================================
# Driver
# ============================================================

def audit_file(path: Path, fix: bool = False) -> tuple[list[Finding], bool]:
    """Returns (findings, file_was_written)."""
    text = path.read_text()
    lines = parse_lines(text)

    findings: list[Finding] = []
    findings.extend(check_top_of_doc(lines, text))
    findings.extend(check_figure(lines, path))
    sec_findings, sections_rows = check_sections_table(lines, text)
    findings.extend(sec_findings)
    h2_findings, overview_end = check_overview_h2s(lines, text, sections_rows)
    findings.extend(h2_findings)
    findings.extend(check_class_method_details(lines, overview_end))
    findings.extend(check_spacing(lines))
    findings.extend(check_linking(lines, path))

    file_written = False
    if fix:
        fixed_text = apply_fixes(text)
        if fixed_text != text:
            path.write_text(fixed_text)
            file_written = True

    return findings, file_written


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit-api-doc",
        description="CAB API Doc facet conformance checker (F119).",
    )
    parser.add_argument("path", type=Path, help="Path to the API doc .md file to audit.")
    parser.add_argument("--fix", action="store_true",
                        help="Apply mechanical fixes (C3, C21, C22, C23, C24).")
    parser.add_argument("--dry", action="store_true",
                        help="Report-only AND refuse to write (overrides --fix).")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"audit-api-doc: file not found: {args.path}", file=sys.stderr)
        return 2

    do_fix = args.fix and not args.dry
    findings, written = audit_file(args.path, fix=do_fix)

    if findings:
        print(f"audit-api-doc: {args.path}")
        for f in findings:
            tag = " (auto-fix available)" if f.fixable and not do_fix else ""
            print(f.fmt(args.path) + tag)
        print()
        n_fixable = sum(1 for f in findings if f.fixable)
        print(f"  {len(findings)} findings ({n_fixable} fixable mechanically)")
        if written:
            print("  --fix applied; re-run to see remaining findings.")
        return 1 if not written else 0
    else:
        print(f"audit-api-doc: {args.path}: 0 findings — conforms to [[CAB API Doc]] facet.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
