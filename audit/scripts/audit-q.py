#!/usr/bin/env python3
"""audit-q.py — Q.md constraint validator with mechanical-fix mode (F076).

Reusable primitives (importable by other tools):
  - links_in_file(path, vault_index) → list[LinkEntry]   (wiki + markdown links)
  - backlog_entries(path) → list[BacklogEntry]            (structured backlog rows)

Four checks applied to Q.md + every anchor backlog:
  C1: every Q.md link resolves (file + optional heading/block-id).
  C2: brackets `[N Questions]` / `[Questions]` target files containing at least
      one Q-marker (existence-check only; exact count NOT required).
  C4: stale `[Done]` rows in horizon H2s get moved to `## Done`.
  D1: Q.md per-anchor banners derived from each anchor's backlog
      (not validated — overwritten on every run).

Usage:
  python audit-q.py              # report-only (script default; clean primitive)
  python audit-q.py --fix        # apply mechanical repairs to Q.md + backlogs
  python audit-q.py --dry        # report-only AND refuse to write (no side effects)

Design: F076 — `audit q` — Q.md constraint validator with mechanical-fix mode.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import argparse
import re
import sys

# ============================================================
# Configuration
# ============================================================

VAULT_ROOT = Path("/Users/oblinger/ob/kmr")
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
# Backlog row: starts with `- **<identifier>`. Identifier is F<n> or B-<name>.
ROW_OPENER_RE = re.compile(r"^- \*\*([A-Za-z][A-Za-z0-9_\-]*)\b")
# Status bracket: `[Ready]`, `[3 Questions]`, `[Blocked F123]`, etc.
BRACKET_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9 ]*?)\]")
# Q-marker: `**Q<n> —`. Used by C2 for existence-check at link targets.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Q.md per-anchor section H1 banner.
QMD_BANNER_RE = re.compile(
    r"^# \[(?P<tag>[^\]]+)\]\s+\[\[Q#(?P<name>[^\|\]]+) Triage(?:\|[^\]]+)?\]\]\s+-\s+"
    r"(?P<rest>.+)$"
)

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
