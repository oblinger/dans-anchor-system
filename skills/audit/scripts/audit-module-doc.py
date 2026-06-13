#!/usr/bin/env python3
"""audit-module-doc.py — Module Doc facet conformance checker (F119).

Validates a target Markdown file against the [[FCT Module Doc]] facet rules.
Emits findings with line numbers, rule references (C1..C30), and (where
applicable) suggested fixes. --fix flag auto-repairs the mechanical
spacing checks (C3, C21, C22, C23, C24/C28).

Usage:
  audit-module-doc <path>                   # report-only
  audit-module-doc <path> --fix             # apply mechanical fixes
  audit-module-doc <path> --dry             # report-only AND refuse to write
  audit-module-doc <path> --verbose         # include per-check rule references

Per F119 v1: standard check set across top-of-doc, figure, SECTIONS table,
per-class blocks, Class Method Details zone, spacing, method body, dispatch
linking, topic format.

C convention: each Cn is one independent check, stable across versions.
Numbering matches the inventory in F119 § Design § Mechanical check inventory.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================
# Findings
# ============================================================

@dataclass
class Finding:
    """One conformance issue. `suggest` is the concrete fix the agent should apply."""
    rule: str            # e.g. "C1"
    line: int            # 1-based line number; 0 = file-level
    message: str
    suggest: str = ""
    fixable: bool = False

    def fmt(self, rel_path: str, verbose: bool = False) -> str:
        loc = f"{rel_path}:{self.line}" if self.line else rel_path
        head = f"  [{self.rule}] {loc}: {self.message}"
        if self.suggest:
            head += f"\n          fix: {self.suggest}"
        return head


# ============================================================
# Parsing primitives
# ============================================================

H1_PATTERN = re.compile(r'^# +(.+?)\s*$')
H2_PATTERN = re.compile(r'^## +(.+?)\s*$')
H3_PATTERN = re.compile(r'^### +(.+?)\s*$')

# Block-ID forms (in declarations and references)
BLOCK_ID_DECLARATION_PATTERN = re.compile(r'\^([A-Za-z0-9_\-]+)\s*$')  # end-of-line declaration
BLOCK_ID_INLINE_DECLARATION_PATTERN = re.compile(r'\^([A-Za-z0-9_\-]+)(?:\s|$)')  # inline declaration
BLOCK_ID_REFERENCE_PATTERN = re.compile(r'\[\[#\^([A-Za-z0-9_\-]+)(?:\\?\|[^\]]*)?\]\]')  # wiki-link ref

WIKI_EMBED_SVG_PATTERN = re.compile(r'!\[\[([^\]\|]+\.svg)(?:\|\d+)?\]\]')
SECTIONS_HEADER_PATTERN = re.compile(r'^\|\s*SECTIONS\s*\|\s*Role\s*\|', re.IGNORECASE)
SECTIONS_ROW_PATTERN = re.compile(
    r'^\|\s*\[\[#\^([A-Za-z0-9_\-]+)(?:\\?\|([^\]]+))?\]\]\s*([A-Za-z\-]*)\s*\|'
)

# Class table: first column header all-caps "NAME TYPE" form
# Accept: TASK SCHEDULER CLASS, PRIORITY AND STARVATION TOPIC, etc.
CLASS_TABLE_HEADER_PATTERN = re.compile(
    r'^\|\s*([A-Z][A-Z0-9 \-]+(?:\s+(CLASS|ENUM|STRUCT|TOPIC|PROTOCOL|INTERFACE|TRAIT|RECORD)))\s*\|\s*Description\s*\|',
    re.IGNORECASE
)

# Field row: bold-name-only + plain-code tail
# **`name`**`: Type`  OR  **`name`**`(args) -> Return`  OR  **`name`**  (no tail)
FIELD_ROW_PATTERN = re.compile(r'^\|\s*\*\*`([^`]+)`\*\*(`[^`]*`)?\s*\|')
# Method row: link wraps bold-name; code-tail outside link
METHOD_ROW_PATTERN = re.compile(
    r'^\|\s*\*\*\[\[#\^([A-Za-z0-9_\-]+)\\?\|([^\]]+)\]\]\*\*`([^`]*)`'
)
# Anti-pattern: backticks INSIDE the wiki-link alias
BROKEN_METHOD_PATTERN = re.compile(r'\[\[#\^[^\]]+\\?\|\*\*`[^`]+`\*\*\]\]')
METHODS_DIVIDER_PATTERN = re.compile(r'^\|\s*\*\*Methods\*\*\s*\|\s*\|?\s*$')

METHOD_H3_PATTERN = re.compile(r'^### +`([^`]+)`(?:\s+\^([A-Za-z0-9_\-]+))?')

# Topic content shape: bulleted concept list with `- **Label** — description`
TOPIC_BULLET_PATTERN = re.compile(r'^- +\*\*[^*]+\*\*\s*[—-]\s+')

# Method body italic-Args heading vs old bold-Args
ITALIC_ARGS_PATTERN = re.compile(r'^\*Args:\*\s*$')
BOLD_ARGS_PATTERN = re.compile(r'^\*\*Args:\*\*\s*$')


def parse_lines(text: str) -> list[str]:
    return text.splitlines()


def find_h1s(lines: list[str]) -> list[tuple[int, str]]:
    return [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := H1_PATTERN.match(line))]


def find_h2s(lines: list[str]) -> list[tuple[int, str]]:
    return [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := H2_PATTERN.match(line))]


def find_block_id_declarations(text: str) -> dict[str, int]:
    """Map block-ID → 1-based line where it's declared.

    A declaration is either:
      - end-of-line `^id` (most common — after a prose paragraph or table)
      - inline `^id` at end of a heading line (e.g. `### `name(...)` ^id`)
    """
    decls: dict[str, int] = {}
    for i, line in enumerate(text.splitlines()):
        # End-of-line declaration
        m = BLOCK_ID_DECLARATION_PATTERN.search(line)
        if m:
            bid = m.group(1)
            # Make sure it's not inside a wiki-link reference (those use [[#^id|...]])
            # The simplest disambiguation: if the line contains [[#^id|, the ^id is a reference, not a declaration
            ref_pattern = re.compile(rf'\[\[#\^{re.escape(bid)}(?:\\?\|[^\]]*)?\]\]')
            if not ref_pattern.search(line):
                decls.setdefault(bid, i + 1)
    return decls


def find_block_id_references(text: str) -> list[tuple[int, str]]:
    """List of (1-based line, block-ID) for every `[[#^id|...]]` reference."""
    refs = []
    for i, line in enumerate(text.splitlines()):
        for m in BLOCK_ID_REFERENCE_PATTERN.finditer(line):
            refs.append((i + 1, m.group(1)))
    return refs


# ============================================================
# Checks
# ============================================================

def check_top_of_doc(lines: list[str], text: str) -> list[Finding]:
    findings = []
    # C1: YAML frontmatter present
    if not text.startswith('---'):
        findings.append(Finding(
            "C1", 1,
            "missing YAML frontmatter (expected `---` opener)",
            suggest="Add `---\\ndescription: <one-line module summary>\\n---` at the top of the file.",
        ))
    else:
        end = text.find('\n---', 4)
        if end < 0:
            findings.append(Finding(
                "C1", 1,
                "YAML frontmatter not closed (missing `---` terminator)",
                suggest="Add a closing `---` line after the frontmatter fields.",
            ))
        else:
            fm = text[4:end]
            # C29: description field non-empty
            desc_match = re.search(r'^description\s*:\s*(.*)$', fm, re.MULTILINE)
            if not desc_match:
                findings.append(Finding(
                    "C1", 1,
                    "frontmatter missing `description:` field",
                    suggest='Add `description: "<one-line module summary>"` to the frontmatter.',
                ))
            else:
                desc_val = desc_match.group(1).strip().strip('"').strip("'")
                if not desc_val:
                    findings.append(Finding(
                        "C29", 1,
                        "frontmatter `description:` field is empty",
                        suggest='Fill in a one-line summary of the module, e.g. `description: "priority queue engine and worker pool"`.',
                    ))

    # C2: H1 present
    h1s = find_h1s(lines)
    if not h1s:
        findings.append(Finding(
            "C2", 0,
            "no H1 found; expected `# {NAME} {ModuleName}`",
            suggest="Add `# {NAME} {ModuleName}` as the first non-frontmatter, non-breadcrumb heading.",
        ))
    elif len(h1s) > 2:
        findings.append(Finding(
            "C2", h1s[2][0],
            f"unexpected third H1 `{h1s[2][1]}`; spec allows file H1 + Class Method Details only",
            suggest="Demote the extra H1 to H2 or merge into an existing section.",
        ))

    # C3: No blank line between H1 and file overview prose
    if h1s:
        h1_line = h1s[0][0]
        if h1_line < len(lines):
            next_line = lines[h1_line]
            if next_line.strip() == '':
                findings.append(Finding(
                    "C3", h1_line + 1,
                    "blank line after H1; spec says H1+overview is compact (no blank)",
                    suggest="Delete the blank line — H1 is immediately followed by overview prose.",
                    fixable=True,
                ))

    # C4: breadcrumb (informational only)
    has_breadcrumb = any(line.startswith(':>>') for line in lines)
    if not has_breadcrumb:
        findings.append(Finding(
            "C4", 0,
            "no `:>>` breadcrumb line found (optional but recommended)",
            suggest="Add `:>> [[anchor]] → [[Docs]] → [[Dev]] → [[Architecture]]` line above the H1.",
        ))

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
        findings.append(Finding(
            "C5", 0,
            "no SVG figure embed found; spec requires `![[file.svg]]` near top",
            suggest=f"Author a `.excalidraw` figure, convert with `excalidraw_to_svg.py`, and embed via `![[{doc_path.stem}.svg]]` after the file overview prose.",
        ))
        return findings

    svg_basename = embed_match.group(1)
    svg_path = doc_path.parent / svg_basename
    excal_path = svg_path.with_suffix('.excalidraw')

    # C6: Referenced SVG file exists
    if not svg_path.is_file():
        findings.append(Finding(
            "C6", embed_line,
            f"referenced SVG `{svg_basename}` not found at `{svg_path.parent}/`",
            suggest=f"Generate the SVG: `python3 ~/.claude/skills/viz/excalidraw_to_svg.py '{excal_path}'`",
        ))

    # C7: Excalidraw source exists alongside
    if not excal_path.is_file():
        findings.append(Finding(
            "C7", embed_line,
            f"Excalidraw source `{excal_path.name}` not found alongside SVG",
            suggest="Author the `.excalidraw` source first (see `~/.claude/skills/viz/excalidraw-examples.md`), then convert to SVG.",
        ))

    # C30: SVG should be ≥ excalidraw mtime (catches forgot-to-re-convert)
    if svg_path.is_file() and excal_path.is_file():
        if svg_path.stat().st_mtime < excal_path.stat().st_mtime:
            findings.append(Finding(
                "C30", embed_line,
                f"SVG older than its `.excalidraw` source — needs regeneration",
                suggest=f"Re-run: `python3 ~/.claude/skills/viz/excalidraw_to_svg.py '{excal_path}'`",
            ))

    return findings


def check_sections_table(lines: list[str], text: str) -> tuple[list[Finding], list[tuple[str, str, str]]]:
    """C8-C10. Returns findings + list of (block_id, name, type) parsed from SECTIONS rows."""
    findings: list[Finding] = []
    sections_rows: list[tuple[str, str, str]] = []

    header_line = None
    for i, line in enumerate(lines):
        if SECTIONS_HEADER_PATTERN.match(line):
            header_line = i + 1
            break
    if header_line is None:
        findings.append(Finding(
            "C8", 0,
            "no `| SECTIONS | Role |` header row found",
            suggest="Add a SECTIONS table after the file overview prose, with one row per major section in the doc.",
        ))
        return findings, sections_rows

    # Walk subsequent rows
    i = header_line
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
            # C9: if type word present, must be lowercase. If absent, OK — section is a topic.
            valid_types = {'class', 'enum', 'struct', 'protocol', 'interface', 'trait', 'record'}
            if type_word:
                if type_word != type_word.lower():
                    findings.append(Finding(
                        "C9", i + 1,
                        f"SECTIONS row type word `{type_word}` should be lowercase",
                        suggest=f"Change `{type_word}` to `{type_word.lower()}` (type word is lowercase in SECTIONS).",
                    ))
                elif type_word not in valid_types:
                    findings.append(Finding(
                        "C9", i + 1,
                        f"SECTIONS row type word `{type_word}` not in recognized vocabulary",
                        suggest=f"Use one of: class / enum / struct / protocol / interface / trait / record. If the section is a topic, drop the type word entirely.",
                    ))
            # If type_word is empty, section is a topic — no warning (per facet 2026-06-06 update)
        else:
            if line.strip().startswith('|') and '---' not in line:
                if '[[#' not in line:
                    findings.append(Finding(
                        "C9", i + 1,
                        f"SECTIONS row missing `[[#^...]]` block-ID link",
                        suggest="SECTIONS rows must use block-ID links: `[[#^anchor|Name]] type | Role description`.",
                    ))
        i += 1

    return findings, sections_rows


def check_block_id_resolution(lines: list[str], text: str, sections_rows: list[tuple[str, str, str]]) -> list[Finding]:
    """C10, C17. Proper declare-vs-reference tracking."""
    findings: list[Finding] = []

    declarations = find_block_id_declarations(text)
    references = find_block_id_references(text)

    # C10: Every SECTIONS-row reference resolves to a declaration
    for bid, name, _ in sections_rows:
        if bid not in declarations:
            findings.append(Finding(
                "C10", 0,
                f"SECTIONS row for `{name}` references `^{bid}` but no declaration found",
                suggest=f"Add `^{bid}` at the end of the section's description paragraph (concatenated, no space): `...prose.^{bid}`",
            ))

    # C17: Every method-link reference resolves
    section_bids = {bid for bid, _, _ in sections_rows}
    for line_no, bid in references:
        if bid in section_bids:
            continue  # already checked above
        if bid not in declarations:
            findings.append(Finding(
                "C17", line_no,
                f"reference `^{bid}` has no matching declaration in the doc",
                suggest=f"Either fix the reference (typo in `^{bid}`?), or add `^{bid}` at the end of the target H3 — e.g. `### \\`method(args) -> R\\` ^{bid}`",
            ))

    return findings


def check_overview_h2s(lines: list[str], text: str, sections_rows: list[tuple[str, str, str]]) -> tuple[list[Finding], int, list[str]]:
    """C11-C16. Walk overview-zone H2s. Returns findings, overview_end (line), overview_class_names."""
    findings = []
    overview_classes: list[str] = []

    details_h1_line = None
    for i, line in enumerate(lines):
        if H1_PATTERN.match(line) and 'Class Method Details' in line:
            details_h1_line = i + 1
            break
    overview_end = details_h1_line if details_h1_line else len(lines) + 1

    type_keywords = {'Class', 'Enum', 'Struct', 'Topic', 'Protocol', 'Interface', 'Trait', 'Record'}

    # Walk H2s
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        m = H2_PATTERN.match(line)
        if not m:
            continue
        h2_name = m.group(1)
        if h2_name.lower() in ('see also', 'related'):
            continue

        # C11: H2 with type qualifier → code section; without → topic (no warning, both are valid)
        parts = h2_name.rsplit(' ', 1)
        if len(parts) >= 2 and parts[1] in type_keywords:
            # Code-typed section — record the name (without qualifier) for C19
            overview_classes.append(parts[0])
        # else: bare name = topic. No warning per facet 2026-06-06 update — "Topic" sentinel dropped

        # C12: description prose with inline block-ID
        for j in range(i + 1, min(i + 5, overview_end - 1)):
            nl = lines[j]
            if nl.strip() == '':
                continue
            if nl.startswith('#') or nl.lstrip().startswith('|'):
                _type_kw = {'Class', 'Enum', 'Struct', 'Topic', 'Protocol', 'Interface', 'Trait', 'Record'}
                _parts = h2_name.split()
                if _parts and _parts[-1] in _type_kw:
                    _parts = _parts[:-1]
                _bid = ''.join(w[0].upper() + w[1:] if w else '' for w in _parts) if _parts else 'Section'
                findings.append(Finding(
                    "C12", i + 1,
                    f"H2 `{h2_name}` not followed by description prose",
                    suggest=f"Add a 1-3 sentence description immediately after the H2 (no blank line), ending with `^{_bid}` block-ID inline.",
                ))
                break
            if '^' not in nl:
                # Strip the type qualifier (Class/Enum/etc.) and PascalCase the remaining words
                _type_kw = {'Class', 'Enum', 'Struct', 'Topic', 'Protocol', 'Interface', 'Trait', 'Record'}
                _parts = h2_name.split()
                if _parts and _parts[-1] in _type_kw:
                    _parts = _parts[:-1]
                expected_bid = ''.join(w[0].upper() + w[1:] if w else '' for w in _parts) if _parts else 'Section'
                findings.append(Finding(
                    "C12", j + 1,
                    f"H2 `{h2_name}` description missing inline block-ID at end",
                    suggest=f"Append `^{expected_bid}` to the end of the description line (no space): `...flows through it.^{expected_bid}`",
                ))
            break

    # C13-C16: Walk class tables in overview zone
    in_class_table = False
    saw_methods_divider = False
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        m = CLASS_TABLE_HEADER_PATTERN.match(line)
        if m:
            in_class_table = True
            saw_methods_divider = False
            continue
        # Detect ALL CAPS header without matching the type-qualifier pattern
        if not in_class_table and re.match(r'^\|\s*[A-Z][A-Z0-9 \-]+\s*\|\s*Description\s*\|', line):
            hdr_match = re.match(r'^\|\s*([A-Z][A-Z0-9 \-]+)\s*\|', line)
            if not hdr_match:
                continue
            header = hdr_match.group(1).strip()
            if not any(header.endswith(' ' + tk.upper()) for tk in type_keywords):
                findings.append(Finding(
                    "C13", i + 1,
                    f"class table header `{header}` missing TYPE qualifier in ALL CAPS",
                    suggest=f"Append the type word: `{header} CLASS` (or ENUM / TOPIC / etc., ALL CAPS to match the table-header convention).",
                ))
            in_class_table = True
            saw_methods_divider = False
            continue
        if not in_class_table:
            continue
        if not line.lstrip().startswith('|'):
            in_class_table = False
            saw_methods_divider = False
            continue
        if '---' in line:
            continue

        # C15: detect broken method-row form (backticks INSIDE wiki-link alias)
        if BROKEN_METHOD_PATTERN.search(line):
            findings.append(Finding(
                "C15", i + 1,
                "method row has backticks INSIDE wiki-link alias — Obsidian won't render correctly",
                suggest="Move bold and backticks OUTSIDE the link: `**[[#^anchor|name]]**`(args) -> R`` (link alias is plain text; backticks wrap separate code spans).",
            ))
            continue

        if METHODS_DIVIDER_PATTERN.match(line):
            saw_methods_divider = True
            continue

        # C14: field row or method row
        is_field = bool(FIELD_ROW_PATTERN.match(line))
        is_method = bool(METHOD_ROW_PATTERN.match(line))

        if not is_field and not is_method:
            # Check for plausible row shape (starts with `| **`)
            if line.lstrip().startswith('| **') and '**`' in line:
                # Could be valid but not matching tight regex; loosen with informational
                findings.append(Finding(
                    "C14", i + 1,
                    "row form unclear — expected bold-identifier-only form",
                    suggest=("Fields: `| **`name`**`: Type` | description |`  "
                             "Methods: `| **[[#^anchor|name]]**`(args) -> R` | description |`"),
                ))

    return findings, overview_end, overview_classes


def check_h2_content_consistency(lines: list[str], overview_end: int) -> list[Finding]:
    """C31: H2 form should match the content shape inside its section.
    - H2 with type qualifier (`## Name Class`) → expect a class table.
    - H2 without type qualifier (`## Name`) → expect bulleted content (topic).
    Mismatch means the author intended one thing but authored content for the other."""
    findings: list[Finding] = []

    type_keywords = {'Class', 'Enum', 'Struct', 'Topic', 'Protocol', 'Interface', 'Trait', 'Record'}

    # Walk overview zone; for each H2 boundary, classify expected shape and observed shape
    sections: list[tuple[int, str, bool]] = []  # (line, h2_name, expects_class_table)
    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        m = H2_PATTERN.match(line)
        if not m:
            continue
        name = m.group(1)
        if name.lower() in ('see also', 'related'):
            continue
        parts = name.rsplit(' ', 1)
        expects_class_table = len(parts) >= 2 and parts[1] in type_keywords
        sections.append((i + 1, name, expects_class_table))

    # For each section, check if it has a class table or bullets before the next H2
    for idx, (h2_line, name, expects_table) in enumerate(sections):
        end_line = sections[idx + 1][0] if idx + 1 < len(sections) else overview_end
        has_class_table = False
        has_bullets = False
        for j in range(h2_line, min(end_line, len(lines) + 1) - 1):
            ln = lines[j]
            if CLASS_TABLE_HEADER_PATTERN.match(ln):
                has_class_table = True
            if TOPIC_BULLET_PATTERN.match(ln):
                has_bullets = True
        if expects_table and not has_class_table and has_bullets:
            findings.append(Finding(
                "C31", h2_line,
                f"H2 `{name}` has a type qualifier (code-typed section) but content is a bulleted list, not a class table",
                suggest=f"Either author a class table (`| {name.rsplit(' ', 1)[0].upper()} {name.rsplit(' ', 1)[1].upper()} | Description |` with field/method rows), or drop the type qualifier from the H2 to make it a bare topic.",
            ))
        elif not expects_table and has_class_table:
            findings.append(Finding(
                "C31", h2_line,
                f"H2 `{name}` is bare (looks like a topic) but the section contains a class table — types disagree",
                suggest=f"Either append a type qualifier to the H2 (e.g. `## {name} Class`) to match the class table, or replace the class table with a bulleted concept list if this is genuinely a topic.",
            ))

    return findings


def check_class_method_details(lines: list[str], text: str, overview_end: int, overview_classes: list[str]) -> list[Finding]:
    """C18-C20, C24, C28. Class Method Details zone."""
    findings: list[Finding] = []

    # C18: details H1 exists if there are method H3s with block-IDs in overview-zone refs
    if overview_end > len(lines):
        # No details zone — that's fine for classes with no methods
        return findings

    # Walk details zone
    detail_h2_names: list[str] = []
    seen_block_ids: set[str] = set()
    for i in range(overview_end - 1, len(lines)):
        line = lines[i]
        h2_m = H2_PATTERN.match(line)
        if h2_m:
            detail_h2_names.append(h2_m.group(1))
            continue
        method_m = METHOD_H3_PATTERN.match(line)
        if method_m and method_m.group(2):
            bid = method_m.group(2)
            seen_block_ids.add(bid)
            # C20: block-ID `^ClassName-methodname` form (must contain a hyphen)
            if '-' not in bid:
                findings.append(Finding(
                    "C20", i + 1,
                    f"method block-ID `^{bid}` should follow `^ClassName-methodname` form",
                    suggest=f"Use `^ClassName-{bid}` (e.g. `^TaskScheduler-submit`) — class prefix prevents collisions across classes.",
                ))

    # C19: detail H2 names should match overview class names
    if overview_classes:
        for h2_name in detail_h2_names:
            if h2_name not in overview_classes:
                # Tolerate "Class Method Details" itself if it's an H2 in the details zone heuristic
                continue  # h2_name is in details zone; only enforce if name doesn't appear in overview at all
        for cls in overview_classes:
            if cls not in detail_h2_names and detail_h2_names:
                # Cls has details H2? Only flag if methods reference it
                pass  # soft check, no warning for now

    # C24 / C28: method body uses italic *Args:*, not bold **Args:**
    for i in range(overview_end - 1, len(lines)):
        line = lines[i]
        if BOLD_ARGS_PATTERN.match(line):
            findings.append(Finding(
                "C24", i + 1,
                "use italic `*Args:*` heading, not bold `**Args:**` — merged-bullet form per facet",
                suggest="Change `**Args:**` to `*Args:*`, and merge Returns/Raises into the bullet list as `- *Returns:* **`type`** — ...` / `- *Raises:* **`Error`** if ...`.",
                fixable=True,
            ))
        # C28 supplementary: Returns/Raises on their own as separate sections
        if re.match(r'^\*\*Returns:\*\*', line):
            findings.append(Finding(
                "C28", i + 1,
                "Returns should be a bullet within the Args list, not a separate bold section",
                suggest="Convert to: `- *Returns:* **`<type>`** — <description>` as a bullet item under `*Args:*`.",
            ))
        if BOLD_ARGS_PATTERN.match(line):
            continue
        if re.match(r'^\*\*Raises:\*\*\s*$', line):
            findings.append(Finding(
                "C28", i + 1,
                "Raises should be a bullet within the Args list, not a separate bold section",
                suggest="Convert each Raises entry to: `- *Raises:* **`<ErrorType>`** if <condition>.` as a bullet item.",
            ))

    return findings


def check_spacing(lines: list[str]) -> list[Finding]:
    """C21-C23."""
    findings: list[Finding] = []

    details_h1_idx = None
    for i, line in enumerate(lines):
        if H1_PATTERN.match(line) and 'Class Method Details' in line:
            details_h1_idx = i
            break

    # C22: 2 blank lines before each H2 (overview zone)
    for i, line in enumerate(lines):
        if not H2_PATTERN.match(line):
            continue
        blanks = 0
        j = i - 1
        while j >= 0 and lines[j].strip() == '':
            blanks += 1
            j -= 1
        if j < 0:
            continue
        if details_h1_idx is not None and j == details_h1_idx:
            continue
        if blanks not in (0, 2):
            findings.append(Finding(
                "C22", i + 1,
                f"expected 2 blank lines before H2, found {blanks}",
                suggest=f"{'Add' if blanks < 2 else 'Remove'} {abs(2 - blanks)} blank line(s) before this H2 to match the 2-blank-line separator rule.",
                fixable=True,
            ))

    # C23: 7 blank lines before `# Class Method Details`
    if details_h1_idx is not None and details_h1_idx > 0:
        blanks = 0
        j = details_h1_idx - 1
        while j >= 0 and lines[j].strip() == '':
            blanks += 1
            j -= 1
        if blanks != 7:
            findings.append(Finding(
                "C23", details_h1_idx + 1,
                f"expected 7 blank lines before `# Class Method Details`, found {blanks}",
                suggest=f"{'Add' if blanks < 7 else 'Remove'} {abs(7 - blanks)} blank line(s) before `# Class Method Details` to match the zone-separator rule.",
                fixable=True,
            ))

    # C21: 0 blank lines after H1/H2 (compact rule), except See Also / Related
    for i, line in enumerate(lines):
        h1_m = H1_PATTERN.match(line)
        h2_m = H2_PATTERN.match(line)
        if not h1_m and not h2_m:
            continue
        if h2_m and h2_m.group(1).lower() in ('see also', 'related'):
            continue
        if h1_m and 'Class Method Details' in line:
            continue
        if i + 1 < len(lines) and lines[i + 1].strip() == '':
            findings.append(Finding(
                "C21", i + 2,
                f"blank line after `{line.strip()}`; spec says compact (no blank between heading and prose)",
                suggest="Delete the blank line — heading is immediately followed by content.",
                fixable=True,
            ))

    return findings


def check_topic_format(lines: list[str], overview_end: int) -> list[Finding]:
    """C27: topic sections use bulleted concept-label list (or table when tabular)."""
    findings: list[Finding] = []

    in_topic_section = False
    topic_h2_line = 0
    topic_name = ""
    has_table = False
    has_bullets = False

    for i, line in enumerate(lines):
        if i + 1 >= overview_end:
            break
        m = H2_PATTERN.match(line)
        if m:
            # Closing the previous topic section
            if in_topic_section and not has_bullets and not has_table:
                findings.append(Finding(
                    "C27", topic_h2_line,
                    f"topic `{topic_name}` has no concept content (bulleted list or table)",
                    suggest=("Add a bulleted concept-label list: `- **Concept name** — one-sentence explanation.`  "
                             "Use a table instead only when the topic has genuinely tabular structure (state-transition matrix, etc.)."),
                ))
            # Reset for new section — a topic is any H2 that doesn't end with a code-type qualifier
            _type_kw = {'Class', 'Enum', 'Struct', 'Protocol', 'Interface', 'Trait', 'Record'}
            _parts = m.group(1).rsplit(' ', 1)
            in_topic_section = not (len(_parts) >= 2 and _parts[1] in _type_kw)
            # Skip See Also / Related — those are file-level meta, not topics
            if m.group(1).lower() in ('see also', 'related'):
                in_topic_section = False
            topic_h2_line = i + 1
            topic_name = m.group(1)
            has_table = False
            has_bullets = False
            continue
        if not in_topic_section:
            continue
        # Detect table inside topic section
        if line.lstrip().startswith('|'):
            has_table = True
        # Detect topic-style bullet
        if TOPIC_BULLET_PATTERN.match(line):
            has_bullets = True

    # Close at overview_end
    if in_topic_section and not has_bullets and not has_table:
        findings.append(Finding(
            "C27", topic_h2_line,
            f"topic `{topic_name}` has no concept content",
            suggest="Add a bulleted concept-label list under the topic description.",
        ))

    return findings


def check_linking(doc_path: Path) -> list[Finding]:
    """C25-C26. Doc is referenced from Dev.md and Files.md."""
    findings: list[Finding] = []
    basename = doc_path.stem
    parent = doc_path.parent

    dev_md = None
    files_md = None
    for ancestor in (parent, parent.parent, parent.parent.parent):
        try:
            if not ancestor.exists():
                continue
        except OSError:
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
                findings.append(Finding(
                    "C25", 0,
                    f"doc `{basename}` not referenced in `{dev_md.name}` dispatch table",
                    suggest=f"Add a row to `{dev_md.name}` linking the new doc: `| [[{basename}]] | <one-line description> |`",
                ))
        except OSError:
            pass

    if files_md:
        try:
            if basename not in files_md.read_text():
                findings.append(Finding(
                    "C26", 0,
                    f"doc `{basename}` not referenced in `{files_md.name}` Files tree",
                    suggest=f"Add the file to `{files_md.name}` Files tree at the appropriate node, with a wiki-link.",
                ))
        except OSError:
            pass

    return findings


# ============================================================
# Auto-fix
# ============================================================

def apply_fixes(text: str) -> str:
    """Apply mechanical fixes for C3, C21, C22, C23, C24."""
    lines = text.splitlines(keepends=False)

    # Strip blank lines immediately after H1 (non-Class-Method-Details) and H2 (non-See-Also)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        h1_m = H1_PATTERN.match(line)
        h2_m = H2_PATTERN.match(line)
        skip_compact = False
        if h2_m and h2_m.group(1).lower() in ('see also', 'related'):
            skip_compact = True
        if h1_m and 'Class Method Details' in line:
            skip_compact = True
        if (h1_m or h2_m) and not skip_compact:
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                i += 2
                continue
        i += 1
    text = '\n'.join(out)

    # C24: bold **Args:** → italic *Args:*
    text = re.sub(r'^\*\*Args:\*\*\s*$', '*Args:*', text, flags=re.MULTILINE)

    # C22 / C23: normalize blank-line runs before headings
    lines = text.splitlines(keepends=False)
    out = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == '':
            j = i
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                nl = lines[j]
                if H1_PATTERN.match(nl) and 'Class Method Details' in nl:
                    out.extend([''] * 7)
                    i = j
                    continue
                h2_m = H2_PATTERN.match(nl)
                if h2_m and h2_m.group(1).lower() not in ('see also', 'related'):
                    out.extend([''] * 2)
                    i = j
                    continue
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
    findings.extend(check_block_id_resolution(lines, text, sections_rows))
    h2_findings, overview_end, overview_classes = check_overview_h2s(lines, text, sections_rows)
    findings.extend(h2_findings)
    findings.extend(check_topic_format(lines, overview_end))
    findings.extend(check_h2_content_consistency(lines, overview_end))
    findings.extend(check_class_method_details(lines, text, overview_end, overview_classes))
    findings.extend(check_spacing(lines))
    findings.extend(check_linking(path))

    # Sort findings by line, then rule
    findings.sort(key=lambda f: (f.line, f.rule))

    file_written = False
    if fix:
        fixed = apply_fixes(text)
        if fixed != text:
            path.write_text(fixed)
            file_written = True

    return findings, file_written


def relpath_from_cwd(path: Path) -> str:
    """Best-effort relative path; fall back to absolute if elsewhere."""
    try:
        from os import getcwd
        return str(path.resolve().relative_to(Path(getcwd()).resolve()))
    except (ValueError, OSError):
        return str(path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="audit-module-doc",
        description="Module Doc facet conformance checker (F119).",
    )
    parser.add_argument("path", type=Path, help="Path to the module doc .md file to audit.")
    parser.add_argument("--fix", action="store_true",
                        help="Apply mechanical fixes (C3, C21, C22, C23, C24).")
    parser.add_argument("--dry", action="store_true",
                        help="Report-only AND refuse to write (overrides --fix).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print rule descriptions inline with findings.")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"audit-module-doc: file not found: {args.path}", file=sys.stderr)
        return 2

    do_fix = args.fix and not args.dry
    findings, written = audit_file(args.path, fix=do_fix)

    rel = relpath_from_cwd(args.path)

    if findings:
        print(f"audit-module-doc: {rel}")
        # Group by severity (just by line for now)
        for f in findings:
            print(f.fmt(rel, verbose=args.verbose))
        print()
        n_fixable = sum(1 for f in findings if f.fixable)
        msg = f"  {len(findings)} findings"
        if n_fixable:
            msg += f" ({n_fixable} fixable via --fix)"
        print(msg)
        if written:
            print("  --fix applied; re-run to see remaining findings.")
        return 1 if not written else 0
    else:
        print(f"audit-module-doc: {rel}: 0 findings — conforms to [[FCT Module Doc]] facet.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
