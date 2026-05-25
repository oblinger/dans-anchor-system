#!/usr/bin/env python3
"""audit-q.py — Q.md constraint validator with mechanical-fix mode (F076, B16, F089).

Reusable primitives (importable by other tools):
  - links_in_file(path, vault_index) → list[LinkEntry]   (wiki + markdown links)
  - backlog_entries(path) → list[BacklogEntry]            (structured backlog rows)
  - extract_q_entries(path, container_id) → list[QEntry]  (B16 ask-format)

Checks applied to Q.md, each anchor's backlog, and each feature/Questions doc:
  C1:  every Q.md link resolves (file + optional heading/block-id).
  C2:  brackets `[N Questions]` / `[Questions]` target files containing at least
       one Q-marker (existence-check only; exact count NOT required).
  C4:  stale `[Done]` rows in horizon H2s get moved to `## Done`.
  C6:  every `**Q<n> —` bullet ends with `^<container>-Q<n>` block-ID  (auto-fix).
  C7:  external Q references use block-ID link form `[[X#^X-Q<n>|...]]` (report).
  C8:  no embedded prose alternatives (`"Either (a) X or (b) Y"`)      (report).
  C9:  every Q has a sibling **Recommendation** with Strong/Lean/None  (report).
  C10: **Recommendation** bullet at same indent as the Q header        (auto-fix).
  C12: every `[Verify-by YYYY-MM-DD]` row body includes
       "Naturally exercised by: …"                                     (report).
  C13: `## Ready` H2 contains only `[Ready]` rows.
       Pure-state mismatches (Watching/Waiting/Blocked) auto-move      (hybrid).
  C14: `## Active` H2 contains only `[Active]` rows.
       Pure-state mismatches (Watching/Waiting/Blocked) auto-move      (hybrid).
  C15: `[Watching]/[Waiting]` rows must be in `## Later`               (auto-fix).
  C16: `[Blocked]/[Blocked F<n>]` rows must be in `## Later`           (auto-fix).
  C18: `[Verify-by YYYY-MM-DD]` past expiry → auto-move to `## Done`   (auto-fix).
  D1:  Q.md per-anchor banners derived from each anchor's backlog
       (not validated — overwritten on every run).

Usage:
  python audit-q.py              # report-only (script default; clean primitive)
  python audit-q.py --fix        # apply mechanical repairs to Q.md + backlogs
  python audit-q.py --dry        # report-only AND refuse to write (no side effects)

Design: F076 — `audit q` — Q.md constraint validator with mechanical-fix mode.
       B16  — ask-format rules C6–C12.
       F089 — bracket↔H2 consistency rules C13–C18.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional
import argparse
import re
import sys

# ============================================================
# Configuration
# ============================================================
#
# VAULT_ROOT is the global `vault_root` parameter documented in
# [[SKA System Design]] § Per-user parameters. Audit / hygiene scripts ALWAYS
# default to vault-wide scope — Obsidian operates on the vault, audits follow
# the same scope; single-anchor scoping defeats the purpose of cross-cutting
# drift detection. Per F080, the value comes from
# ~/.config/ob-skills/global.yaml; fallback to ~/ob/kmr if config missing.
# Do NOT add a --project flag that narrows scope by default; if a narrowing
# flag is wanted, make it explicit opt-in.


def _resolve_vault_root() -> Path:
    """Read vault_root from F080 config (~/.config/ob-skills/global.yaml),
    falling back to ~/ob/kmr if the config file or key is missing."""
    config_path = Path.home() / ".config" / "ob-skills" / "global.yaml"
    if config_path.is_file():
        try:
            import yaml
            with config_path.open() as f:
                data = yaml.safe_load(f) or {}
            raw = data.get("vault_root")
            if raw:
                return Path(str(raw).replace("~", str(Path.home())))
        except (ImportError, Exception):
            pass
    return Path.home() / "ob" / "kmr"


VAULT_ROOT = _resolve_vault_root()
Q_MD = VAULT_ROOT / "Q.md"

# Filesystem-walk exclusions when building the vault index.
EXCLUDED_PATH_FRAGMENTS = (".trash", "Closet", "Yore", "worktrees", ".claude")

# Horizon H2s in a per-anchor backlog. `## Done` is the archive surface for
# C4's stale-Done migration; everything else is a "live" horizon.
LIVE_HORIZON_H2S = {"Active", "Ready", "Now", "Next", "Later", "Legwork"}
ALL_KNOWN_H2S = LIVE_HORIZON_H2S | {"Done", "Icebox", "Notes"}

# ============================================================
# Regexes
# ============================================================

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BLOCK_ID_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
# Markdown link: [text](path) — but NOT [[wiki]]. Negative lookbehind for `[`.
MARKDOWN_LINK_RE = re.compile(r"(?<!\[)\[([^\[\]]+)\]\(([^)]+)\)")
# Backlog row: starts with `- **<identifier>` or `- **[[<identifier>` (wiki-link
# identifier form used by some anchors, e.g. MUX). Identifier is F<n> or B-<name>.
ROW_OPENER_RE = re.compile(r"^- \*\*(?:\[\[)?([A-Za-z][A-Za-z0-9_\-]*)\b")
# Status bracket: `[Ready]`, `[3 Questions]`, `[Blocked F123]`, etc.
BRACKET_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9 ]*?)\]")
# Q-marker: `**Q<n> —`. Used by C2 for existence-check at link targets.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Q.md per-anchor section H1 banner.
QMD_BANNER_RE = re.compile(
    r"^# \[(?P<tag>[^\]]+)\]\s+\[\[Q#(?P<name>[^\|\]]+) Triage(?:\|[^\]]+)?\]\]\s+-\s+"
    r"(?P<rest>.+)$"
)

# B16 (ask-format) — Q-header bullet: `- **Q<n> — ...`
Q_HEADER_RE = re.compile(r"^(\s*)- \*\*Q(\d+)\b")
# B16 — block-ID at end of Q header line: `^F089-Q3`
Q_BLOCK_ID_TRAILING_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*-Q\d+)\s*$")
# B16 — Recommendation bullet: `- **Recommendation:** Strong (B). reason.`
RECOMMENDATION_RE = re.compile(
    r"^(\s*)- \*\*Recommendation:\*\*\s*(Strong|Lean|None)?\b",
    re.IGNORECASE,
)
# B16 (C8) — embedded prose alternatives heuristic: "(a) X or (b) Y" inline
# Matches `(a)` or `(A)` followed within ~80 chars by `(b)` or `(B)`
INLINE_ALTERNATIVES_RE = re.compile(r"\([aAbBcDdD]\)[^\n]{0,80}\([aAbBcDdD]\)")
# B16 (C7) — Q reference in display text: `\bQ\d+\b` outside the basename
Q_REF_IN_DISPLAY_RE = re.compile(r"\bQ\d+\b")
# B16 (C12) — Verify-by bracket
VERIFY_BY_BRACKET_RE = re.compile(r"\[Verify-by\s+(\d{4}-\d{2}-\d{2})\]")
# B16 (C12) — "Naturally exercised by" rationale text
NATURALLY_EXERCISED_RE = re.compile(r"[Nn]aturally exercised by\b")
# B16 — F-number extraction from feature-doc stems: `F089 — Title` → `F089`
F_NUMBER_PREFIX_RE = re.compile(r"^(F\d+)\s+—")
# F089 (C18) — Verify-by bracket date extraction (parses the date for expiry check)
VERIFY_BY_DATE_RE = re.compile(r"^Verify-by\s+(\d{4})-(\d{2})-(\d{2})\b")

# ============================================================
# Dataclasses
# ============================================================


@dataclass
class LinkEntry:
    source_file: Path
    source_line: int
    source_col_start: int
    source_col_end: int
    raw: str
    kind: str  # 'wiki' or 'markdown'
    target_basename: str
    target_heading: Optional[str] = None
    target_block_id: Optional[str] = None
    display_text: Optional[str] = None
    target_file_path: Optional[Path] = None
    target_line: int = 0
    target_resolves: bool = False
    target_anchor_resolves: Optional[bool] = None


@dataclass
class BacklogEntry:
    source_file: Path
    source_line: int
    identifier: str
    horizon: str
    status: str
    link: Optional[LinkEntry]
    raw_body: str


@dataclass
class Finding:
    severity: str  # 'error' or 'warning'
    surface_file: Path
    surface_line: int
    code: str  # 'C1' / 'C2' / 'C4' / 'D1' / 'stale-Q-marker' / etc.
    message: str
    mechanically_fixable: bool


@dataclass
class QEntry:
    """B16 — a single Q-header bullet inside a ## Open Questions block."""
    source_file: Path
    source_line: int            # 1-indexed Q header line
    indent: str                 # leading whitespace on the Q header line
    q_num: int
    container_id: str           # e.g., 'F089', 'SKA', 'QFix' (B-row)
    has_block_id: bool
    block_id_value: Optional[str] = None
    inline_alternatives: bool = False
    recommendation_line: int = 0           # 0 = missing
    recommendation_indent: Optional[str] = None
    recommendation_strength: Optional[str] = None  # 'Strong' / 'Lean' / 'None'


# ============================================================
# Vault index (basename → list of paths; Obsidian path-proximity resolution)
# ============================================================


def build_vault_index(vault_root: Path) -> dict[str, list[Path]]:
    """Walk vault_root for *.md files; return basename → list of paths."""
    index: dict[str, list[Path]] = {}
    for path in vault_root.rglob("*.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        stem = path.stem
        index.setdefault(stem, []).append(path)
    return index


def resolve_target(basename: str, source_file: Path,
                   vault_index: dict[str, list[Path]]) -> Optional[Path]:
    """Obsidian path-proximity resolution: closest match wins."""
    basename = basename.strip()
    if not basename:
        return None
    # Strip `.md` extension if explicitly written
    if basename.endswith(".md"):
        basename = basename[:-3]
    candidates = vault_index.get(basename, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    def shared_depth(p: Path) -> int:
        a = source_file.parts
        b = p.parts
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i
    return max(candidates, key=shared_depth)


# ============================================================
# File scanning primitives (read once per call; no caching of contents)
# ============================================================


def headings_in(file_path: Path) -> dict[str, int]:
    """Return dict heading-text → 1-indexed line. First occurrence wins."""
    if not file_path.is_file():
        return {}
    headings: dict[str, int] = {}
    try:
        with file_path.open() as f:
            for i, line in enumerate(f, start=1):
                m = HEADING_RE.match(line)
                if m:
                    headings.setdefault(m.group(2), i)
    except (OSError, UnicodeDecodeError):
        pass
    return headings


def block_ids_in(file_path: Path) -> dict[str, int]:
    """Return dict block-id → 1-indexed line. First occurrence wins."""
    if not file_path.is_file():
        return {}
    ids: dict[str, int] = {}
    try:
        with file_path.open() as f:
            for i, line in enumerate(f, start=1):
                for m in BLOCK_ID_RE.finditer(line):
                    ids.setdefault(m.group(1), i)
    except (OSError, UnicodeDecodeError):
        pass
    return ids


# ============================================================
# Link parsing — wiki + markdown
# ============================================================


def _parse_wiki_inner(inner: str) -> dict:
    """Parse the inside of a [[wiki-link]] (between [[ and ]])."""
    if "|" in inner:
        target_part, alias = inner.split("|", 1)
    else:
        target_part, alias = inner, None
    target_heading = None
    target_block_id = None
    if "#" in target_part:
        basename, anchor = target_part.split("#", 1)
        if anchor.startswith("^"):
            target_block_id = anchor[1:]
        else:
            target_heading = anchor
    else:
        basename = target_part
    return {
        "basename": basename.strip(),
        "target_heading": target_heading,
        "target_block_id": target_block_id,
        "display_text": alias,
    }


def _resolve_wiki(parsed: dict, source_file: Path,
                  vault_index: dict[str, list[Path]]) -> dict:
    """Given parsed wiki components, resolve target file + anchor + line."""
    target_file = resolve_target(parsed["basename"], source_file, vault_index)
    target_resolves = target_file is not None
    target_anchor_resolves: Optional[bool] = None
    target_line = 0
    if target_file and parsed["target_heading"]:
        line_num = headings_in(target_file).get(parsed["target_heading"], 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    elif target_file and parsed["target_block_id"]:
        line_num = block_ids_in(target_file).get(parsed["target_block_id"], 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    return {
        "target_file_path": target_file,
        "target_line": target_line,
        "target_resolves": target_resolves,
        "target_anchor_resolves": target_anchor_resolves,
    }


def _parse_markdown(text: str, path: str, source_file: Path) -> dict:
    """Parse markdown link [text](path). Resolve path relative to source_file."""
    target_heading = None
    if "#" in path:
        path_part, anchor = path.split("#", 1)
        if not anchor.startswith("^"):
            target_heading = anchor
    else:
        path_part = path
    target_file: Optional[Path] = None
    if path_part:
        if path_part.startswith("/"):
            candidate = Path(path_part)
        elif path_part.startswith("~"):
            candidate = Path(path_part).expanduser()
        else:
            candidate = (source_file.parent / path_part).resolve()
        if candidate.is_file():
            target_file = candidate
    target_resolves = target_file is not None
    target_anchor_resolves: Optional[bool] = None
    target_line = 0
    if target_file and target_heading:
        line_num = headings_in(target_file).get(target_heading, 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    return {
        "basename": Path(path_part).stem if path_part else "",
        "target_heading": target_heading,
        "target_block_id": None,
        "display_text": text,
        "target_file_path": target_file,
        "target_line": target_line,
        "target_resolves": target_resolves,
        "target_anchor_resolves": target_anchor_resolves,
    }


def links_in_file(file_path: Path,
                  vault_index: dict[str, list[Path]]) -> list[LinkEntry]:
    """Parse all wiki + markdown links in file_path; return ordered list."""
    entries: list[LinkEntry] = []
    if not file_path.is_file():
        return entries
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return entries
    for line_num, line in enumerate(lines, start=1):
        # Skip wiki-link matches that are inside markdown links (rare).
        for m in WIKI_LINK_RE.finditer(line):
            parsed = _parse_wiki_inner(m.group(1))
            resolved = _resolve_wiki(parsed, file_path, vault_index)
            entries.append(LinkEntry(
                source_file=file_path,
                source_line=line_num,
                source_col_start=m.start() + 1,
                source_col_end=m.end(),
                raw=m.group(0),
                kind="wiki",
                target_basename=parsed["basename"],
                target_heading=parsed["target_heading"],
                target_block_id=parsed["target_block_id"],
                display_text=parsed["display_text"],
                target_file_path=resolved["target_file_path"],
                target_line=resolved["target_line"],
                target_resolves=resolved["target_resolves"],
                target_anchor_resolves=resolved["target_anchor_resolves"],
            ))
        for m in MARKDOWN_LINK_RE.finditer(line):
            parsed = _parse_markdown(m.group(1), m.group(2), file_path)
            entries.append(LinkEntry(
                source_file=file_path,
                source_line=line_num,
                source_col_start=m.start() + 1,
                source_col_end=m.end(),
                raw=m.group(0),
                kind="markdown",
                target_basename=parsed["basename"],
                target_heading=parsed["target_heading"],
                target_block_id=parsed["target_block_id"],
                display_text=parsed["display_text"],
                target_file_path=parsed["target_file_path"],
                target_line=parsed["target_line"],
                target_resolves=parsed["target_resolves"],
                target_anchor_resolves=parsed["target_anchor_resolves"],
            ))
    return entries


# ============================================================
# Backlog parsing — structured BacklogEntry list
# ============================================================


def _detect_status(line: str) -> str:
    """Extract the workflow-state bracket from a row's main line.

    Returns the bracket text without brackets (e.g., 'Ready', '3 Questions',
    'Blocked F123', 'Done', 'Done 2026-05-19', or '' if no bracket found).
    Returns the FIRST bracket — the workflow-state one.
    """
    m = BRACKET_RE.search(line)
    if not m:
        return ""
    return m.group(1).strip()


def backlog_entries(backlog_file: Path,
                    vault_index: dict[str, list[Path]]) -> list[BacklogEntry]:
    """Parse {NAME} Backlog.md; return list of BacklogEntry in source order."""
    if not backlog_file.is_file():
        return []
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    entries: list[BacklogEntry] = []
    current_horizon = ""
    # Pre-compute all links in the file for efficient lookup by line.
    file_links = links_in_file(backlog_file, vault_index)
    links_by_line: dict[int, list[LinkEntry]] = {}
    for link in file_links:
        links_by_line.setdefault(link.source_line, []).append(link)
    for line_num, line in enumerate(lines, start=1):
        m = HEADING_RE.match(line)
        if m and m.group(1) == "##":
            current_horizon = m.group(2)
            continue
        opener = ROW_OPENER_RE.match(line)
        if opener and current_horizon:
            identifier = opener.group(1)
            status = _detect_status(line)
            link = None
            row_links = links_by_line.get(line_num, [])
            if row_links:
                link = row_links[0]
            entries.append(BacklogEntry(
                source_file=backlog_file,
                source_line=line_num,
                identifier=identifier,
                horizon=current_horizon,
                status=status,
                link=link,
                raw_body=line,
            ))
    return entries


# ============================================================
# Check C1 — link existence (against Q.md)
# ============================================================


def check_c1_link_existence(qmd_links: list[LinkEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for link in qmd_links:
        if not link.target_resolves:
            findings.append(Finding(
                severity="error",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C1",
                message=f"link {link.raw} does not resolve "
                        f"(basename '{link.target_basename}' not in vault)",
                mechanically_fixable=False,
            ))
        elif link.target_anchor_resolves is False:
            anchor_kind = "heading" if link.target_heading else "block-id"
            anchor_val = link.target_heading or link.target_block_id
            findings.append(Finding(
                severity="error",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C1",
                message=f"link {link.raw} resolves to file but {anchor_kind} "
                        f"'{anchor_val}' missing in target",
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# Check C2 — Q-marker existence at target (for `[Questions]` brackets)
# ============================================================


def check_c2_q_marker_existence(qmd_links: list[LinkEntry],
                                qmd_text: str) -> list[Finding]:
    """For every Q.md line carrying `[N Questions]` bracket, verify the link
    target contains at least one Q-marker."""
    findings: list[Finding] = []
    lines = qmd_text.splitlines()
    links_by_line: dict[int, list[LinkEntry]] = {}
    for link in qmd_links:
        links_by_line.setdefault(link.source_line, []).append(link)
    for line_num, line in enumerate(lines, start=1):
        if "Questions" not in line:
            continue
        # Match bracket containing "Questions"
        m = re.search(r"\[(\d*\s*)Questions?\]", line)
        if not m:
            continue
        row_links = links_by_line.get(line_num, [])
        if not row_links:
            continue
        # Use the first link as the target (skip Q.md-internal heading-anchor refs)
        primary_link = None
        for link in row_links:
            if not (link.kind == "wiki" and link.target_basename == "Q"):
                primary_link = link
                break
        if not primary_link or not primary_link.target_resolves:
            continue
        target_file = primary_link.target_file_path
        assert target_file is not None  # target_resolves implies this
        try:
            target_text = target_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # Existence-check only — count NOT required to match
        if not Q_MARKER_RE.search(target_text):
            findings.append(Finding(
                severity="error",
                surface_file=primary_link.source_file,
                surface_line=line_num,
                code="C2",
                message=f"[Questions] bracket at line {line_num} but target "
                        f"{target_file.name} contains no Q<n> markers",
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# Check C4 — stale `[Done]` rows in horizon H2s → auto-move to `## Done`
# ============================================================


def check_c4_stale_done(entries: list[BacklogEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for entry in entries:
        if entry.horizon not in LIVE_HORIZON_H2S:
            continue
        # Bracket starts with 'Done' → stale
        if entry.status.startswith("Done"):
            findings.append(Finding(
                severity="warning",
                surface_file=entry.source_file,
                surface_line=entry.source_line,
                code="C4",
                message=f"row '{entry.identifier}' has [Done] bracket in "
                        f"## {entry.horizon} (stale; should be in ## Done)",
                mechanically_fixable=True,
            ))
    return findings


def apply_c4_fix(backlog_file: Path,
                 entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Move stale [Done] rows to top of ## Done. Returns (changed, log)."""
    stale = [e for e in entries
             if e.horizon in LIVE_HORIZON_H2S and e.status.startswith("Done")]
    if not stale:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    # Sort stale rows by source line descending so removing doesn't shift indices
    stale_sorted = sorted(stale, key=lambda e: e.source_line, reverse=True)
    extracted_rows: list[str] = []
    # Extract each stale row (and any continuation indented sub-bullets / blank-prefix-of-next)
    for entry in stale_sorted:
        idx = entry.source_line - 1
        if idx >= len(lines):
            continue
        row_lines: list[str] = [lines[idx]]
        # Pull subsequent indented lines (sub-bullets)
        j = idx + 1
        while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
            row_lines.append(lines[j])
            j += 1
        # If next line is blank, include it (preserves row separation)
        if j < len(lines) and lines[j] == "":
            row_lines.append(lines[j])
            j += 1
        # Remove the extracted lines
        del lines[idx:j]
        extracted_rows.insert(0, "\n".join(row_lines).rstrip("\n"))
    # Find ## Done H2 line
    done_h2_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Done":
            done_h2_idx = i
            break
    if done_h2_idx is None:
        # No ## Done — append one at the end
        lines.extend(["", "", "## Done", ""])
        done_h2_idx = len(lines) - 2
    # Insert extracted rows at top of ## Done (just after the H2 line + blank)
    insert_at = done_h2_idx + 1
    # Skip one blank line if present
    while insert_at < len(lines) and lines[insert_at] == "":
        insert_at += 1
    log = []
    for row_block in extracted_rows:
        # Prepend the row + a trailing blank line
        for offset, row_line in enumerate(row_block.split("\n")):
            lines.insert(insert_at + offset, row_line)
        lines.insert(insert_at + len(row_block.split("\n")), "")
        log.append(f"moved to ## Done: {row_block.splitlines()[0][:80]}")
    new_text = "\n".join(lines)
    # Preserve trailing newline if original had one
    if not new_text.endswith("\n"):
        new_text += "\n"
    backlog_file.write_text(new_text, encoding="utf-8")
    return True, log


# ============================================================
# Checks C6–C12 — ask-format compliance (B16)
# ============================================================
# C6: every Q has block-ID ^<container>-Q<n>           (auto-fix)
# C7: external Q references use block-ID link form     (report only)
# C8: no embedded prose alternatives in Q line          (report only)
# C9: every Q has Recommendation with Strong/Lean/None  (report only)
# C10: Recommendation outdented to Q's indent level     (auto-fix)
# C12: [Verify-by] rows include "Naturally exercised by:" (report only)
# (C11 — Verify 4-piece layout — deferred; too heuristic for v1.)


def find_ask_format_files(
    anchor_backlogs: dict[str, Path],
) -> list[tuple[str, Path]]:
    """For each anchor, yield (container_id, file_path) pairs for every file
    that might contain ask-format Qs.

    Container IDs:
    - Feature doc F089-...md → 'F089'
    - À la carte '<NAME> Questions.md' → '<NAME>'
    """
    out: list[tuple[str, Path]] = []
    for name, backlog_file in anchor_backlogs.items():
        features_dir = backlog_file.parent / f"{name} Features"
        if features_dir.is_dir():
            for feature_file in sorted(features_dir.glob("F*.md")):
                m = F_NUMBER_PREFIX_RE.match(feature_file.stem)
                if m:
                    out.append((m.group(1), feature_file))
        questions_file = backlog_file.parent / f"{name} Questions.md"
        if questions_file.is_file():
            out.append((name, questions_file))
    return out


def extract_q_entries(file_path: Path, container_id: str) -> list[QEntry]:
    """Parse file_path; return one QEntry per Q-header inside `## Open Questions`.

    Recommendation matching: the first bullet line whose body starts with
    `**Recommendation:**` after a Q-header and before the next Q-header is the
    Recommendation for that Q.
    """
    if not file_path.is_file():
        return []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[QEntry] = []
    in_open_questions = False
    pending_q: Optional[QEntry] = None

    def flush():
        nonlocal pending_q
        if pending_q is not None:
            out.append(pending_q)
            pending_q = None

    for line_num, line in enumerate(lines, start=1):
        # Track section state via H2 headings; H3 ### Resolved closes Q tracking
        heading_m = HEADING_RE.match(line)
        if heading_m:
            level = len(heading_m.group(1))
            heading_text = heading_m.group(2).strip()
            if level == 2:
                flush()
                in_open_questions = (heading_text == "Open Questions")
                continue
            if level == 3 and heading_text == "Resolved" and in_open_questions:
                # Resolved subsection — pending Qs above the heading get flushed
                flush()
                in_open_questions = False
                continue
        if not in_open_questions:
            continue
        # Q-header bullet
        qm = Q_HEADER_RE.match(line)
        if qm:
            flush()
            indent = qm.group(1)
            q_num = int(qm.group(2))
            block_id_match = Q_BLOCK_ID_TRAILING_RE.search(line)
            has_block_id = block_id_match is not None
            block_id_value = block_id_match.group(1) if block_id_match else None
            inline_alt = INLINE_ALTERNATIVES_RE.search(line) is not None
            pending_q = QEntry(
                source_file=file_path,
                source_line=line_num,
                indent=indent,
                q_num=q_num,
                container_id=container_id,
                has_block_id=has_block_id,
                block_id_value=block_id_value,
                inline_alternatives=inline_alt,
            )
            continue
        # Recommendation bullet (first match wins)
        if pending_q is not None and pending_q.recommendation_line == 0:
            rm = RECOMMENDATION_RE.match(line)
            if rm:
                pending_q.recommendation_line = line_num
                pending_q.recommendation_indent = rm.group(1)
                pending_q.recommendation_strength = (
                    rm.group(2).capitalize() if rm.group(2) else None
                )
    flush()
    return out


def check_c6_block_id_present(q_entries: list[QEntry]) -> list[Finding]:
    """C6: every Q has block-ID ^<container>-Q<n>."""
    findings: list[Finding] = []
    for q in q_entries:
        expected = f"{q.container_id}-Q{q.q_num}"
        if not q.has_block_id:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C6",
                message=f"Q{q.q_num} missing block-ID; expected ^{expected}",
                mechanically_fixable=True,
            ))
        elif q.block_id_value != expected:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C6",
                message=f"Q{q.q_num} block-ID '^{q.block_id_value}' should be '^{expected}'",
                mechanically_fixable=True,
            ))
    return findings


def apply_c6_fix(q_entries: list[QEntry]) -> list[str]:
    """Append / replace block-IDs for all C6-flagged Qs. Returns log."""
    log: list[str] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        expected = f"{q.container_id}-Q{q.q_num}"
        if q.has_block_id and q.block_id_value == expected:
            continue
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        changed = False
        for q in qs:
            idx = q.source_line - 1
            if idx >= len(lines):
                continue
            line = lines[idx]
            expected = f"{q.container_id}-Q{q.q_num}"
            # Strip any existing trailing ^... block-ID (right form or wrong)
            stripped = Q_BLOCK_ID_TRAILING_RE.sub("", line).rstrip()
            new_line = f"{stripped} ^{expected}"
            if new_line != line:
                lines[idx] = new_line
                changed = True
                log.append(
                    f"  {file_path.name}:{q.source_line} — set ^{expected} (Q{q.q_num})"
                )
        if changed:
            new_text = "\n".join(lines)
            if not new_text.endswith("\n"):
                new_text += "\n"
            file_path.write_text(new_text, encoding="utf-8")
    return log


def check_c7_link_form(
    files_to_scan: list[Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C7: external Q refs use block-ID link form.

    Heuristic: any link whose display text contains 'Q<n>' but whose link target
    has no block-ID component is a violation. Report-only (rewriting requires
    reading destination to find the matching Q — agent task).
    """
    findings: list[Finding] = []
    for file_path in files_to_scan:
        links = links_in_file(file_path, vault_index)
        for link in links:
            display = link.display_text or ""
            if not Q_REF_IN_DISPLAY_RE.search(display):
                continue
            if link.target_block_id is not None:
                continue  # already block-ID form
            findings.append(Finding(
                severity="warning",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C7",
                message=(
                    f"link {link.raw} references Q<n> in display but lacks "
                    f"block-ID form (expected [[<file>#^<container>-Q<n>|...]])"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c8_inline_alternatives(q_entries: list[QEntry]) -> list[Finding]:
    """C8: Q header should not embed prose alternatives like '(a) X or (b) Y'."""
    findings: list[Finding] = []
    for q in q_entries:
        if q.inline_alternatives:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C8",
                message=(
                    f"Q{q.q_num} has inline prose alternatives; hoist to labeled "
                    f"sub-bullets (A) / (B) / (C) on their own lines"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c9_recommendation_present(q_entries: list[QEntry]) -> list[Finding]:
    """C9: every Q has a Recommendation bullet with Strong/Lean/None."""
    findings: list[Finding] = []
    for q in q_entries:
        if q.recommendation_line == 0:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C9",
                message=(
                    f"Q{q.q_num} missing Recommendation bullet "
                    f"(expected '- **Recommendation:** Strong|Lean|None ...')"
                ),
                mechanically_fixable=False,
            ))
        elif q.recommendation_strength is None:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.recommendation_line,
                code="C9",
                message=(
                    f"Q{q.q_num} Recommendation lacks strength label "
                    f"(must be Strong / Lean / None)"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c10_recommendation_outdent(q_entries: list[QEntry]) -> list[Finding]:
    """C10: Recommendation bullet at same indent as Q header (not nested)."""
    findings: list[Finding] = []
    for q in q_entries:
        if q.recommendation_line == 0 or q.recommendation_indent is None:
            continue
        if len(q.recommendation_indent) > len(q.indent):
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.recommendation_line,
                code="C10",
                message=(
                    f"Q{q.q_num} Recommendation nested "
                    f"(indent {len(q.recommendation_indent)}) — outdent to Q "
                    f"header level (indent {len(q.indent)})"
                ),
                mechanically_fixable=True,
            ))
    return findings


def apply_c10_fix(q_entries: list[QEntry]) -> list[str]:
    """Rewrite indent of nested Recommendation bullets to match Q indent."""
    log: list[str] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        if q.recommendation_line == 0 or q.recommendation_indent is None:
            continue
        if len(q.recommendation_indent) > len(q.indent):
            by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        changed = False
        for q in qs:
            idx = q.recommendation_line - 1
            if idx >= len(lines):
                continue
            line = lines[idx]
            stripped = line.lstrip()
            new_line = q.indent + stripped
            if new_line != line:
                lines[idx] = new_line
                changed = True
                log.append(
                    f"  {file_path.name}:{q.recommendation_line} — outdented "
                    f"Recommendation for Q{q.q_num}"
                )
        if changed:
            new_text = "\n".join(lines)
            if not new_text.endswith("\n"):
                new_text += "\n"
            file_path.write_text(new_text, encoding="utf-8")
    return log


def check_c12_verify_by_rationale(
    anchor_backlogs: dict[str, Path],
) -> list[Finding]:
    """C12: every `[Verify-by YYYY-MM-DD]` row body includes 'Naturally exercised by:'."""
    findings: list[Finding] = []
    for backlog_file in anchor_backlogs.values():
        try:
            lines = backlog_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_num, line in enumerate(lines, start=1):
            if not VERIFY_BY_BRACKET_RE.search(line):
                continue
            # Body = the row line + any subsequent indented continuation lines
            body_text = line
            j = line_num  # next-line index (1-based line_num == 0-based j)
            while j < len(lines):
                nxt = lines[j]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    body_text += "\n" + nxt
                    j += 1
                elif nxt == "":
                    j += 1
                    continue
                else:
                    break
            if not NATURALLY_EXERCISED_RE.search(body_text):
                findings.append(Finding(
                    severity="warning",
                    surface_file=backlog_file,
                    surface_line=line_num,
                    code="C12",
                    message=(
                        "[Verify-by] row body missing 'Naturally exercised by: …' "
                        "rationale (required per ask-format § Deferred-by-use Verify)"
                    ),
                    mechanically_fixable=False,
                ))
    return findings


# ============================================================
# Checks C13–C18 — bracket↔H2 consistency (F089)
# ============================================================
# C13: `## Ready` H2 only contains [Ready] rows  (auto-fix pure-state only)
# C14: `## Active` H2 only contains [Active] rows (auto-fix pure-state only)
# C15: [Watching]/[Waiting] rows belong in `## Later`     (auto-fix)
# C16: [Blocked]/[Blocked F<n>] rows belong in `## Later` (auto-fix)
# C18: [Verify-by YYYY-MM-DD] past-expiry → `## Done`     (auto-fix)
# (C17 — stale [Done] in horizon H2s — covered by existing C4.)


def _is_pure_state_park_bracket(status: str) -> bool:
    """Pure-state brackets unambiguously belong in ## Later (per F089 Q1 hybrid):
    Watching, Waiting, Watching Nd/Nh, Waiting Nd/Nh, Blocked, Blocked F<n>.

    Ambiguous brackets (Questions / Designing / Verify / Verify-by) are NOT
    auto-fixable — they need /groom body-reading to decide.
    """
    s = status.strip()
    return (
        s.startswith("Watching")
        or s.startswith("Waiting")
        or s.startswith("Blocked")
    )


def _is_verify_by_expired(status: str, today: date) -> bool:
    """Does this status bracket match `Verify-by YYYY-MM-DD` past today?"""
    m = VERIFY_BY_DATE_RE.match(status.strip())
    if not m:
        return False
    try:
        verify_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    return verify_date < today


def check_c13_ready_h2_purity(entries: list[BacklogEntry]) -> list[Finding]:
    """C13: every row under ## Ready H2 must have [Ready] bracket."""
    findings: list[Finding] = []
    for e in entries:
        if e.horizon != "Ready":
            continue
        if e.status == "Ready":
            continue
        # Don't double-report [Done] (C4 owns it)
        if e.status.startswith("Done"):
            continue
        auto_fix = _is_pure_state_park_bracket(e.status)
        suffix = (
            "; auto-moving to ## Later" if auto_fix
            else "; needs /groom body-reading"
        )
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C13",
            message=(
                f"row '{e.identifier}' has [{e.status}] bracket under ## Ready H2 "
                f"— workflow-state H2 must match bracket{suffix}"
            ),
            mechanically_fixable=auto_fix,
        ))
    return findings


def check_c14_active_h2_purity(entries: list[BacklogEntry]) -> list[Finding]:
    """C14: every row under ## Active H2 must have [Active] bracket."""
    findings: list[Finding] = []
    for e in entries:
        if e.horizon != "Active":
            continue
        if e.status == "Active":
            continue
        if e.status.startswith("Done"):
            continue  # C4 owns
        auto_fix = _is_pure_state_park_bracket(e.status)
        suffix = (
            "; auto-moving to ## Later" if auto_fix
            else "; needs /groom body-reading"
        )
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C14",
            message=(
                f"row '{e.identifier}' has [{e.status}] bracket under ## Active H2 "
                f"— workflow-state H2 must match bracket{suffix}"
            ),
            mechanically_fixable=auto_fix,
        ))
    return findings


def check_c15_watching_waiting_in_later(
    entries: list[BacklogEntry],
) -> list[Finding]:
    """C15: [Watching]/[Waiting] rows must be in ## Later."""
    findings: list[Finding] = []
    for e in entries:
        s = e.status.strip()
        if not (s.startswith("Watching") or s.startswith("Waiting")):
            continue
        if e.horizon == "Later":
            continue
        # Skip if already counted by C13/C14 (same row, same auto-fix target)
        # We still flag separately to make the bracket-based rule visible.
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C15",
            message=(
                f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                f"— Watching/Waiting belongs in ## Later (not actionable now)"
            ),
            mechanically_fixable=True,
        ))
    return findings


def check_c16_blocked_in_later(entries: list[BacklogEntry]) -> list[Finding]:
    """C16: [Blocked]/[Blocked F<n>] rows must be in ## Later."""
    findings: list[Finding] = []
    for e in entries:
        s = e.status.strip()
        if not s.startswith("Blocked"):
            continue
        if e.horizon == "Later":
            continue
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C16",
            message=(
                f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                f"— Blocked belongs in ## Later (external dependency)"
            ),
            mechanically_fixable=True,
        ))
    return findings


def check_c18_verify_by_expired(
    entries: list[BacklogEntry], today: date,
) -> list[Finding]:
    """C18: [Verify-by YYYY-MM-DD] past expiry → auto-move to ## Done."""
    findings: list[Finding] = []
    for e in entries:
        if not _is_verify_by_expired(e.status, today):
            continue
        if e.horizon == "Done":
            continue
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C18",
            message=(
                f"row '{e.identifier}' has [{e.status}] window expired "
                f"(today={today.isoformat()}); auto-Done per Verify-by deferred-by-use"
            ),
            mechanically_fixable=True,
        ))
    return findings


def _find_or_create_h2(lines: list[str], h2_name: str) -> int:
    """Return index of `## <h2_name>` line; append (and return new index) if absent."""
    target = f"## {h2_name}"
    for i, line in enumerate(lines):
        if line.strip() == target:
            return i
    # Append at end with leading blank-separation
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(target)
    lines.append("")
    return len(lines) - 2


def apply_placement_fixes(
    backlog_file: Path,
    entries: list[BacklogEntry],
    today: date,
) -> list[str]:
    """F089 — apply C13/C14/C15/C16/C18 mechanical moves on this backlog.

    Conservative: only moves rows whose bracket has an unambiguous canonical
    target H2 (pure-state Watching/Waiting/Blocked → Later; Verify-by expired
    → Done). Ambiguous cases (Questions/Designing/Verify in wrong H2) are
    flagged by the C13/C14 checks but NOT moved here — /groom handles those
    with body-reading judgment.
    """
    # Decide moves
    moves: list[tuple[BacklogEntry, str]] = []  # (entry, target_h2_name)
    for e in entries:
        s = e.status.strip()
        # C18 first — Verify-by expired wins over any other classification
        if _is_verify_by_expired(s, today):
            if e.horizon != "Done":
                moves.append((e, "Done"))
            continue
        # C15/C16 — pure-state park brackets not in Later
        if _is_pure_state_park_bracket(s):
            if e.horizon != "Later":
                moves.append((e, "Later"))
            continue
    if not moves:
        return []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    # Sort by source_line DESC so deletions don't shift earlier line numbers
    moves_sorted = sorted(moves, key=lambda x: x[0].source_line, reverse=True)
    # Extract each row block (the bullet line + any indented sub-bullets + 1 blank)
    extracted: list[tuple[str, str, str]] = []  # (target_h2, block_text, identifier)
    for entry, target in moves_sorted:
        idx = entry.source_line - 1
        if idx >= len(lines):
            continue
        row_lines: list[str] = [lines[idx]]
        j = idx + 1
        while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
            row_lines.append(lines[j])
            j += 1
        if j < len(lines) and lines[j] == "":
            row_lines.append(lines[j])
            j += 1
        del lines[idx:j]
        extracted.append((target, "\n".join(row_lines).rstrip("\n"), entry.identifier))
    # Group by target H2
    by_target: dict[str, list[tuple[str, str]]] = {}
    for target, block, identifier in extracted:
        by_target.setdefault(target, []).append((block, identifier))
    log: list[str] = []
    # For each target H2, find or create, insert rows at top
    for target_h2_name, row_blocks in by_target.items():
        h2_idx = _find_or_create_h2(lines, target_h2_name)
        insert_at = h2_idx + 1
        # Skip one blank line below the H2 header if present
        while insert_at < len(lines) and lines[insert_at] == "":
            insert_at += 1
        # row_blocks are in source-line-descending order; insert each at insert_at
        # (so the relative ordering within the target H2 ends up matching the
        # original source order from bottom-up, which after multiple inserts at
        # the same position yields top-of-section in original-order).
        for row_block, identifier in row_blocks:
            block_lines = row_block.split("\n")
            for offset, row_line in enumerate(block_lines):
                lines.insert(insert_at + offset, row_line)
            # Trailing blank for separation
            lines.insert(insert_at + len(block_lines), "")
            log.append(f"  moved to ## {target_h2_name}: {block_lines[0][:80]}")
    new_text = "\n".join(lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    backlog_file.write_text(new_text, encoding="utf-8")
    return log


# ============================================================
# D1 — Banner derivation
# ============================================================


def find_anchor_backlogs(vault_root: Path) -> dict[str, Path]:
    """Find every {NAME} Backlog.md in the vault. Return name → path."""
    out: dict[str, Path] = {}
    for path in vault_root.rglob("* Backlog.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        if path.parent.name.endswith("Plan") or path.parent.name.endswith("Plan"):
            name = path.stem.replace(" Backlog", "")
            out[name] = path
    return out


def derive_anchor_banner(name: str, backlog_file: Path,
                         vault_index: dict[str, list[Path]]) -> Optional[str]:
    """Return the H1 banner line for an anchor's Q.md section.

    Returns None if the anchor has no items in any active horizon (TAG `[]`)."""
    entries = backlog_entries(backlog_file, vault_index)
    if not entries:
        return None
    # Filter out [Done]-bracketed rows from active horizons (stale; C4 may not
    # have run yet, but we don't want them counted toward live state).
    live = [e for e in entries
            if e.horizon in LIVE_HORIZON_H2S
            and not e.status.startswith("Done")]
    # Compute counts by bracket
    active_n = sum(1 for e in live if e.status == "Active")
    ready_n = sum(1 for e in live if e.status == "Ready")
    verify_n = sum(1 for e in live if e.status == "Verify")
    # Questions count = sum of Q-markers across linked targets for each
    # [N Questions]/[Questions] row.
    questions_n = 0
    for e in live:
        if "Questions" not in e.status:
            continue
        if not e.link or not e.link.target_resolves:
            continue
        target_path = e.link.target_file_path
        assert target_path is not None
        try:
            target_text = target_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # Count Q-markers
        q_count = len(Q_MARKER_RE.findall(target_text))
        if q_count == 0:
            # Bracket-claim but no markers: count as 1 anyway (don't lose the row)
            q_count = 1
        questions_n += q_count
    # Per-horizon counts (every entry, even with [Done] would count toward Now
    # in original spec, but C4 will move them out; here we count live only).
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Icebox")}
    for e in entries:  # all entries including potentially-stale-Done
        if e.horizon in horizon_counts and not e.status.startswith("Done"):
            horizon_counts[e.horizon] += 1
    # Icebox count: from {NAME} Icebox.md if it exists
    icebox_file = backlog_file.parent / f"{name} Icebox.md"
    if icebox_file.is_file():
        try:
            icebox_text = icebox_file.read_text(encoding="utf-8")
            horizon_counts["Icebox"] = sum(
                1 for line in icebox_text.splitlines() if ROW_OPENER_RE.match(line)
            )
        except (OSError, UnicodeDecodeError):
            pass
    # TAG cascade
    has_u = questions_n > 0 or verify_n > 0
    has_a = active_n > 0 or ready_n > 0
    has_g = (horizon_counts["Now"] > 0 or horizon_counts["Next"] > 0)
    has_later = horizon_counts["Later"] > 0
    if has_u and has_a:
        tag = "U+A"
    elif has_u:
        tag = "U"
    elif has_a:
        tag = "A"
    elif has_g:
        tag = "G"
    elif has_later:
        tag = "?"
    else:
        tag = ""
    if not tag and horizon_counts["Icebox"] == 0:
        return None
    banner = (
        f"# [{tag}]  [[Q#{name} Triage|{name} Triage]]  -  "
        f"Questions {questions_n}    Verify {verify_n}   |   "
        f"Active {active_n}    Ready {ready_n}   |   "
        f"Now {horizon_counts['Now']}    Next {horizon_counts['Next']}    "
        f"Later {horizon_counts['Later']}    Icebox {horizon_counts['Icebox']}"
    )
    return banner


# ============================================================
# Main + CLI
# ============================================================


def main() -> int:
    desc = (__doc__ or "").split("\n")[0]
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--fix", action="store_true",
                        help="apply mechanical repairs to Q.md + backlogs")
    parser.add_argument("--dry", action="store_true",
                        help="report-only AND refuse to write anywhere")
    args = parser.parse_args()
    if args.fix and args.dry:
        print("error: --fix and --dry are mutually exclusive", file=sys.stderr)
        return 2
    if not Q_MD.is_file():
        print(f"error: {Q_MD} not found", file=sys.stderr)
        return 2
    print(f"audit-q: building vault index from {VAULT_ROOT}...", file=sys.stderr)
    vault_index = build_vault_index(VAULT_ROOT)
    print(f"  vault index: {sum(len(v) for v in vault_index.values())} files, "
          f"{len(vault_index)} unique basenames", file=sys.stderr)
    # C1 + C2 on Q.md
    qmd_links = links_in_file(Q_MD, vault_index)
    qmd_text = Q_MD.read_text(encoding="utf-8")
    findings: list[Finding] = []
    findings.extend(check_c1_link_existence(qmd_links))
    findings.extend(check_c2_q_marker_existence(qmd_links, qmd_text))
    # C4 + D1 require walking each anchor's backlog
    anchor_backlogs = find_anchor_backlogs(VAULT_ROOT)
    c4_fixes_applied: list[str] = []
    derived_banners: dict[str, str] = {}
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        findings.extend(check_c4_stale_done(entries))
        if args.fix:
            changed, fix_log = apply_c4_fix(backlog_file, entries)
            if changed:
                c4_fixes_applied.extend(f"  {name}: {msg}" for msg in fix_log)
        banner = derive_anchor_banner(name, backlog_file, vault_index)
        if banner:
            derived_banners[name] = banner
    # B16 — C6 / C8 / C9 / C10 walk feature docs + Questions.md per anchor
    ask_format_files = find_ask_format_files(anchor_backlogs)
    all_q_entries: list[QEntry] = []
    for container_id, file_path in ask_format_files:
        all_q_entries.extend(extract_q_entries(file_path, container_id))
    findings.extend(check_c6_block_id_present(all_q_entries))
    findings.extend(check_c8_inline_alternatives(all_q_entries))
    findings.extend(check_c9_recommendation_present(all_q_entries))
    findings.extend(check_c10_recommendation_outdent(all_q_entries))
    # B16 — C7 walks the same ask-format files + backlogs + Q.md
    c7_scope = [Q_MD]
    c7_scope.extend(p for _, p in ask_format_files)
    c7_scope.extend(anchor_backlogs.values())
    findings.extend(check_c7_link_form(c7_scope, vault_index))
    # B16 — C12 walks anchor backlogs only (Verify-by lives on backlog rows)
    findings.extend(check_c12_verify_by_rationale(anchor_backlogs))
    # F089 — C13/C14/C15/C16/C18 walk each anchor's backlog entries
    today = date.today()
    f089_fixes_applied: list[str] = []
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        findings.extend(check_c13_ready_h2_purity(entries))
        findings.extend(check_c14_active_h2_purity(entries))
        findings.extend(check_c15_watching_waiting_in_later(entries))
        findings.extend(check_c16_blocked_in_later(entries))
        findings.extend(check_c18_verify_by_expired(entries, today))
        if args.fix:
            fix_log = apply_placement_fixes(backlog_file, entries, today)
            if fix_log:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in fix_log)
    # B16 — apply mechanical fixes for C6 + C10 if --fix
    c6_fixes_applied: list[str] = []
    c10_fixes_applied: list[str] = []
    if args.fix:
        c6_fixes_applied = apply_c6_fix(all_q_entries)
        c10_fixes_applied = apply_c10_fix(all_q_entries)
    # Print findings + summary
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print(f"\naudit-q: {len(findings)} findings ({len(errors)} errors, "
          f"{len(warnings)} warnings)", file=sys.stderr)
    for f in findings:
        rel = f.surface_file.relative_to(VAULT_ROOT) if VAULT_ROOT in f.surface_file.parents else f.surface_file
        print(f"  [{f.severity}] {f.code} {rel}:{f.surface_line} — {f.message}")
    if c4_fixes_applied:
        print(f"\naudit-q: C4 mechanical moves applied:")
        for line in c4_fixes_applied:
            print(line)
    if c6_fixes_applied:
        print(f"\naudit-q: C6 block-IDs appended:")
        for line in c6_fixes_applied:
            print(line)
    if c10_fixes_applied:
        print(f"\naudit-q: C10 Recommendations outdented:")
        for line in c10_fixes_applied:
            print(line)
    if f089_fixes_applied:
        print(f"\naudit-q: F089 placement fixes (C15/C16/C18 auto-moves):")
        for line in f089_fixes_applied:
            print(line)
    print(f"\naudit-q: derived banners for {len(derived_banners)} anchors")
    if args.fix and not args.dry:
        # D1: write derived banners back to Q.md (replace H1 lines for each
        # existing per-anchor section). New-anchor section creation is deferred
        # to /audit q-fix in v1; only existing sections get their banner updated.
        d1_changes = apply_d1_banner_write(Q_MD, derived_banners)
        if d1_changes:
            print(f"\naudit-q: D1 — {d1_changes} per-anchor banner(s) rewritten in Q.md")
    return 1 if errors else 0


def apply_d1_banner_write(qmd_file: Path, derived_banners: dict[str, str]) -> int:
    """Replace existing per-anchor H1 banner lines in Q.md with derived banners.
    Returns the count of banners replaced."""
    try:
        lines = qmd_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    changed = 0
    for i, line in enumerate(lines):
        m = QMD_BANNER_RE.match(line)
        if not m:
            continue
        name = m.group("name")
        derived = derived_banners.get(name)
        if derived and derived != line:
            lines[i] = derived
            changed += 1
    if changed:
        qmd_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    sys.exit(main())
