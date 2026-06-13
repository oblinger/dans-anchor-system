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
  C19: option sub-bullets each on own line, labeled `(A)/(B)/...`      (report).
  C20: blank line after Recommendation separating Q groups             (report).
  C21: `## Open Questions` H2 with zero pending Qs (Phase 2 missed)    (report).
  C22: link existence in feature docs / backlogs                       (report).
  C23: `[Designing]` brackets must resolve to `[N Questions]` (if
       linked doc has pending Qs) or `[Ready]` (if none) — `[Designing]`
       alone is a turn-ownership deadlock                              (auto-fix).
  C24: `[Questions]` / `[N Questions]` bracket count must match the
       linked feature doc's actual pending-Q count. Bare `[Questions]`
       on a row whose linked doc has 7 Qs is stale (should be
       `[7 Questions]`); `[3 Questions]` on a doc with 0 Qs is also stale. (report).
  D1:  Q.md per-anchor banners derived from each anchor's backlog
       (not validated — overwritten on every run).

Usage (per F076 v2, 2026-05-26 — scope-aware audit):
  audit-q                                  # default --scope q: Q.md + linked backlogs + linked feature docs
  audit-q --fix                            # apply mechanical repairs
  audit-q --dry                            # report-only AND refuse to write
  audit-q --scope all                      # vault-wide (every Features/F*.md, ignoring backlog reachability)
  audit-q --scope backlog --anchor SKA     # one anchor's backlog + its linked feature docs
  audit-q --scope feature-doc --feature-doc PATH    # one feature doc only

Wrapper scripts at ~/bin/audit-backlog and ~/bin/audit-feature-doc invoke the
scoped modes with terser CLI: `audit-backlog SKA`, `audit-feature-doc PATH`.

Design: F076 v2 — scoped audits (q / backlog / feature-doc / all) chained by
       reachability per user direction 2026-05-26: only audit feature docs
       the user can click into via Q.md → backlog → linked F-doc.
       F076 v1 — Q.md constraint validator with mechanical-fix mode.
       B16    — ask-format rules C6–C12.
       F089   — bracket↔H2 consistency rules C13–C18.
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
LIVE_HORIZON_H2S = {"Active", "Ready", "Now", "Next", "Later", "Verify", "Legwork"}
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
ROW_OPENER_RE = re.compile(
    r"^- \*\*"
    r"(?:\[\[)?"                     # optional `[[` (wiki-link form)
    r"(?:\[[A-Z]+\]\s+)?"            # optional `[TYPE] ` prefix (e.g., `[BUG] `)
    r"([A-Za-z][A-Za-z0-9_\-]*)\b"   # group(1) = identifier
)
# Status bracket: `[Ready]`, `[3 Questions]`, `[Blocked F123]`, etc.
BRACKET_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9 \-]*?)\]")
# Q-marker: `**Q<n> —`. Used by C2 for existence-check at link targets.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Q.md per-anchor section H1 banner.
QMD_BANNER_RE = re.compile(
    # Match both the new format `[[X ask|X]]` and the legacy
    # `[[Q#X Triage|X Triage]]` form so banner-rewrite works either way.
    r"^# \[(?P<tag>[^\]]*)\]\s+"
    r"\[\[(?:Q#)?(?P<name>[^\|\]]+?)(?:\s+(?:Triage|ask))?(?:\|[^\]]+)?\]\]"
    r"\s+-\s+(?P<rest>.+)$"
)

# B16 (ask-format) — Q-header bullet: `- **Q<n> — ...`
Q_HEADER_RE = re.compile(r"^(\s*)- \*\*Q(\d+)\b")
# F123 — Q-header H3 form: `### Q<n> — ...` (used by DKT and possibly others)
Q_HEADER_H3_RE = re.compile(r"^### Q(\d+)\b")
# B16 — block-ID at end of Q header line: `^F089-Q3`
Q_BLOCK_ID_TRAILING_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*-Q\d+)\s*$")
# B16 — Recommendation bullet: `- **Recommendation:** Strong (B). reason.`
RECOMMENDATION_RE = re.compile(
    r"^(\s*)- \*\*Recommendation:\*\*\s*(Strong|Lean|None)?\b",
    re.IGNORECASE,
)
# F123 — Recommendation paragraph form (H3-shape Qs): `Recommendation: **None** ...`
# Accepts strength inside or outside the bold-asterisks. Anchors `\b` *after*
# the strength capture (before any closing `**`) so `**None**` matches.
RECOMMENDATION_PARA_RE = re.compile(
    r"^Recommendation:\s*\*{0,2}(Strong|Lean|None)\b\*{0,2}",
    re.IGNORECASE,
)
# B16 (C8) — embedded prose alternatives heuristic: "(a) X or (b) Y" inline
# Matches `(a)` or `(A)` followed within ~80 chars by `(b)` or `(B)`
INLINE_ALTERNATIVES_RE = re.compile(r"\([aAbBcDdD]\)[^\n]{0,80}\([aAbBcDdD]\)")
# B16 (C7) — Q reference in display text: `\bQ\d+\b` outside the basename
# Bare `Q<n>` in display text means the link should point to that Q via block-ID.
# Whereas `F<n> Q<m>` (an F-number immediately preceding Q<m>) means Q<m>
# references THAT F<n>, not the link's target — those are descriptive phrases,
# not Q-pointer links, and shouldn't trigger C7.
Q_REF_IN_DISPLAY_RE = re.compile(r"\bQ\d+\b")
F_REF_BEFORE_Q_RE = re.compile(r"\bF\d+\s+Q\d+\b")
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
    """B16 — a single Q-header inside a ## Open Questions block.

    F123: `shape` distinguishes the two valid Q-header forms:
      - "bullet" — `- **Q<n> — ...` (canonical / ask-format default)
      - "h3"     — `### Q<n> — ...` (DKT and possibly other anchors)
    Most checks apply uniformly; per-shape divergences are documented at
    each check (C10 N/A for h3; C19 looks at top-level bullets; C20 N/A
    when shape==h3 and recommendation is paragraph-form).
    """
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
    shape: str = "bullet"                  # F123: "bullet" | "h3"
    recommendation_is_paragraph: bool = False  # F123: paragraph-form Rec (h3 only)


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
    """Return dict heading-text → 1-indexed line. First occurrence wins.

    Stores TWO keys per heading: (1) the raw heading text, (2) the
    code-span-stripped form. Wiki-links pointing to a heading get their
    inner backticks blanked by `_strip_code_spans` during `links_in_file`,
    so the lookup may use either form. Storing both makes the comparison
    survive backticks inside heading text like H3 'move' (in code-span form)
    followed by em-dash and prose.
    """
    if not file_path.is_file():
        return {}
    headings: dict[str, int] = {}
    try:
        with file_path.open() as f:
            for i, line in enumerate(f, start=1):
                m = HEADING_RE.match(line)
                if m:
                    raw = m.group(2)
                    headings.setdefault(raw, i)
                    stripped = _strip_code_spans(raw)
                    if stripped != raw:
                        headings.setdefault(stripped, i)
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


def _is_placeholder_basename(basename: str) -> bool:
    """Heuristically detect 'placeholder' wiki-links that shouldn't be flagged:
    template-prose `[[<expected_anchor>]]`, `[[NAME]]`, `[[...]]`, `[[{x}]]`,
    `[[filename.ext]]`, etc. — these aren't real links, they're spec examples.

    Returns True if the basename looks like a placeholder."""
    if not basename:
        return True
    # Angle-bracket placeholders: <expected_anchor>, <Name>, etc.
    if "<" in basename or ">" in basename:
        return True
    # Curly-brace placeholders: {x}, {NAME}, {}, etc.
    if "{" in basename or "}" in basename:
        return True
    # Ellipsis placeholders: `...`, `name...`, etc.
    if "..." in basename:
        return True
    # Generic-shaped placeholders: bare lowercase metavariable like `name`,
    # `filename.ext` (contains a dot suggesting a filename example).
    if basename in {"name", "NAME", "filename.ext", "RID", "TID", "SLUG", "Name", "id"}:
        return True
    return False


# Memory-file prefixes (live in ~/.claude/projects/.../memory/, OUTSIDE the
# kmr vault). Wiki-links to them are valid but the audit can't see them.
_MEMORY_PREFIXES = ("feedback_", "user_", "project_", "reference_")


def _is_out_of_vault_wiki_link(basename: str) -> bool:
    """Detect wiki-link basenames that legitimately target content the audit
    cannot see in the kmr vault:

    - Path-style refs (`../../../foo`, `A2X Skills/A2X remote`) — these are
      filesystem-relative or sub-folder refs, not basename lookups.
    - Memory-file refs (`feedback_*`, `user_*`, `project_*`, `reference_*`) —
      live in ~/.claude/projects/<proj>/memory/, outside the kmr vault.

    Returns True if the basename should be silently skipped by C22."""
    if not basename:
        return False
    # Path-style: contains a slash (forward or back) or path traversal.
    if "/" in basename or "\\" in basename or ".." in basename:
        return True
    # Memory-file prefixes.
    if basename.startswith(_MEMORY_PREFIXES):
        return True
    return False


# Markdown links with a URL scheme are external — not audit's concern.
_URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _is_url_markdown_link(path: str) -> bool:
    """True if a markdown link's path is a URL (http://, https://, hook://,
    mailto:, etc.) rather than a filesystem path."""
    return bool(_URL_SCHEME_RE.match(path))


def _strip_code_spans(line: str) -> str:
    """Remove inline-code spans (` ` `) from a line so wiki-links inside them
    don't get parsed. Replaces each code span with same-length whitespace to
    preserve column offsets."""
    out_chars = list(line)
    in_code = False
    i = 0
    while i < len(out_chars):
        if out_chars[i] == "`":
            in_code = not in_code
        elif in_code:
            out_chars[i] = " "
        i += 1
    return "".join(out_chars)


def links_in_file(file_path: Path,
                  vault_index: dict[str, list[Path]]) -> list[LinkEntry]:
    """Parse all wiki + markdown links in file_path; return ordered list.

    Skips: (a) lines inside fenced code blocks (``` ... ```), (b) wiki-links
    inside inline code spans (`...`), (c) wiki-links whose basename looks like
    a template placeholder (`<x>`, `{x}`, `...`, etc.). Per user direction
    2026-05-26 — these are spec-prose examples, not real links."""
    entries: list[LinkEntry] = []
    if not file_path.is_file():
        return entries
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return entries
    in_fence = False
    for line_num, line in enumerate(lines, start=1):
        # Track fenced-code-block state. Lines starting with ``` toggle.
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Strip inline-code spans before scanning links.
        scan_line = _strip_code_spans(line)
        for m in WIKI_LINK_RE.finditer(scan_line):
            parsed = _parse_wiki_inner(m.group(1))
            # Skip template-prose placeholders.
            if _is_placeholder_basename(parsed["basename"]):
                continue
            # Skip path-style refs and memory-file refs the audit can't see.
            if _is_out_of_vault_wiki_link(parsed["basename"]):
                continue
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
        for m in MARKDOWN_LINK_RE.finditer(scan_line):
            # Skip URL-scheme links (http://, https://, hook://, mailto:, ...).
            if _is_url_markdown_link(m.group(2)):
                continue
            parsed = _parse_markdown(m.group(1), m.group(2), file_path)
            # Skip template-prose placeholders.
            if _is_placeholder_basename(parsed["basename"] or ""):
                continue
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
    Only the FIRST bracket — and only when it sits in the row's *head*
    region (before the first ` — ` separator). Brackets buried in the row's
    body description (e.g., `(Phases 0 + 1 + 2a [Done] 2026-05-20)`) are NOT
    workflow-state markers and must be ignored.

    Strips `[[wiki-links]]` and inline code spans first so the inner brackets
    of `[[CAE System Design]]` or backticked code-span brackets don't get misread.
    """
    cleaned = _strip_code_spans(line)
    # Replace each `[[...]]` with same-length spaces to preserve column offsets
    # while making BRACKET_RE blind to wiki-link inner text.
    cleaned = re.sub(r"\[\[[^\[\]]*\]\]", lambda m: " " * len(m.group(0)), cleaned)
    # Restrict the scan to the head region: from the end of the row's `**title**`
    # bolded title up to the first ` — ` (em-dash separator) or ` - ` after it.
    # This isolates the workflow-state bracket position (e.g., `[Ready]`) and
    # ignores both em-dashes inside the title and bracketed prose in the body.
    title_match = re.match(r"^- \*\*[^*]+\*\*", cleaned)
    if title_match:
        post_title = cleaned[title_match.end():]
        sep_match = re.search(r"\s[—-]\s", post_title)
        head = post_title[: sep_match.start()] if sep_match else post_title
    else:
        head = cleaned
    m = BRACKET_RE.search(head)
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


def _scope_to_block_id_region(text: str, block_id: str) -> str:
    """Return the lines from `^<block_id>`-bearing row up to the next
    bullet-row or H2. Used by C2 (and backlog-edit's Q-marker check) to
    scope the Q-marker search to a specific row's region when the link
    carries a `#^<block-id>` anchor.

    A row's region:
      - starts at the line containing `^<block_id>` (case-sensitive)
      - includes any indented sub-bullets immediately after it
      - ends at the next top-level bullet, the next H2, or EOF
    """
    lines = text.splitlines()
    marker = f"^{block_id}"
    start = None
    for i, line in enumerate(lines):
        if marker in line:
            start = i
            break
    if start is None:
        return ""  # block-id not found; no scope to check
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("## "):
            end = j
            break
        # Top-level bullet (no leading whitespace) starting with `- **`
        if re.match(r"^- \*\*", s):
            end = j
            break
        # H3 row (HA-style)
        if s.startswith("### "):
            end = j
            break
    return "\n".join(lines[start:end])


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
        if not primary_link:
            # F103 — Q.md row carries [Questions] bracket but has NO non-Q-internal
            # wiki-link. The promise cannot be satisfied; that is an error.
            findings.append(Finding(
                severity="error",
                surface_file=Q_MD,
                surface_line=line_num,
                code="C2",
                message=(
                    f"[Questions] bracket at line {line_num} but row has no "
                    f"wiki-link to a Q-marker target"
                ),
                mechanically_fixable=False,
            ))
            continue
        if not primary_link.target_resolves:
            # F103 — Q.md row's link target does not resolve. Was previously
            # silently skipped (the B-roots-reconcile failure 2026-06-02).
            # Per user direction: any failure to find the questions is an error.
            findings.append(Finding(
                severity="error",
                surface_file=Q_MD,
                surface_line=line_num,
                code="C2",
                message=(
                    f"[Questions] bracket at line {line_num} but linked target "
                    f"[[{primary_link.target_basename}]] does not resolve "
                    f"(broken link = broken promise)"
                ),
                mechanically_fixable=False,
            ))
            continue
        target_file = primary_link.target_file_path
        assert target_file is not None  # target_resolves implies this
        try:
            target_text = target_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # F103 — scope to the row's region when the link uses a block-id.
        # `[[<file>#^<row-id>|...]]` is a promise that the Q-markers live IN
        # that row, not somewhere else in the same file. Without scoping,
        # a row with zero inline Qs passes because the file has Q-markers
        # elsewhere (the B-roots-reconcile failure 2026-06-02).
        if primary_link.target_block_id:
            target_text = _scope_to_block_id_region(
                target_text, primary_link.target_block_id
            )
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
# C19: option sub-bullets each on own line, labeled (A)/(B)/...  (report only)
# C20: blank line after Recommendation, separating Q groups      (report only)
# C21: ## Open Questions H2 with zero pending Qs (Phase 2 missed) (report only)
# C22: link existence in feature docs / backlogs (extends C1's Q.md scope) (report only)
# C23: [Designing] must resolve to [N Questions] or [Ready] — never [Designing] alone (auto-fix)
# (C11 — Verify 4-piece layout — deferred; too heuristic for v1.)


def find_ask_format_files(
    anchor_backlogs: dict[str, Path],
    vault_index: Optional[dict[str, list[Path]]] = None,
    reachable_only: bool = True,
) -> list[tuple[str, Path]]:
    """For each anchor, yield (container_id, file_path) pairs for every file
    that might contain ask-format Qs.

    Container IDs:
    - Feature doc F089-...md → 'F089'
    - Anchor ask file '<NAME> ask.md' → '<NAME>' (authored anchor-level Qs)

    By default (`reachable_only=True`, per user direction 2026-05-26): only
    audit feature docs that are *linked from the anchor's backlog*. Orphan
    feature docs in `Features/` but not reachable via backlog wiki-links are
    skipped — they aren't navigable from Q.md, so the user can't click into
    them, and their drift doesn't matter to the dashboard. Requires `vault_index`
    to resolve wiki-link basenames.

    With `reachable_only=False`, falls back to the original behavior: glob every
    `Features/F*.md`. Used by `--scope all` for vault-wide cleanup sweeps.
    """
    out: list[tuple[str, Path]] = []
    for name, backlog_file in anchor_backlogs.items():
        if reachable_only and vault_index is not None:
            # Reachability-limited: walk backlog wiki-links, pick out F<n> targets.
            # Each reachable feature doc audited once.
            seen_paths: set[Path] = set()
            for link in links_in_file(backlog_file, vault_index):
                if not link.target_resolves or link.target_file_path is None:
                    continue
                stem = link.target_file_path.stem
                # Feature doc: stem starts with `F<NNN> — `
                m = F_NUMBER_PREFIX_RE.match(stem)
                if m:
                    if link.target_file_path not in seen_paths:
                        seen_paths.add(link.target_file_path)
                        out.append((m.group(1), link.target_file_path))
                    continue
            # Always include `{NAME} ask.md` if it exists — anchor-level Qs are
            # authored directly there (there is no `{NAME} Questions.md`).
            # extract_q_entries picks up only the authored `**Q<n>` bullets in
            # `## Questions`; rendered pointer lines and resolutions are ignored.
            ask_file = backlog_file.parent / f"{name} ask.md"
            if ask_file.is_file() and ask_file not in seen_paths:
                out.append((name, ask_file))
        else:
            # Vault-wide: every F<n>.md in the anchor's Features/ folder.
            features_dir = backlog_file.parent / f"{name} Features"
            if features_dir.is_dir():
                for feature_file in sorted(features_dir.glob("F*.md")):
                    m = F_NUMBER_PREFIX_RE.match(feature_file.stem)
                    if m:
                        out.append((m.group(1), feature_file))
            ask_file = backlog_file.parent / f"{name} ask.md"
            if ask_file.is_file():
                out.append((name, ask_file))
    return out


def extract_q_entries(file_path: Path, container_id: str) -> list[QEntry]:
    """Parse file_path; return one QEntry per pending `**Q<n>` bullet anywhere in the file.

    **Loose detection** — a Q-bullet is "pending" unless it appears inside a
    Resolved section (`## Resolved` H2 or `### Resolved` H3, case-insensitive).
    No gating on `## Open Questions` H2 spelling: the principle is "if the file
    contains `**Q<n> —` bullets in a non-Resolved area, treat them as the
    pending questions for this file." This catches lowercase `## Open questions`
    and any other H2 variant without playing whack-a-mole on titles.

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
    in_h2_resolved = False  # inside `## Resolved` H2 (case-insensitive)
    in_h3_resolved = False  # inside `### Resolved` H3 (case-insensitive)
    in_fence = False        # inside ``` ... ``` (or ~~~) fenced code block
    pending_q: Optional[QEntry] = None

    def flush():
        nonlocal pending_q
        if pending_q is not None:
            out.append(pending_q)
            pending_q = None

    # Local heading regex — tolerates up to 3 leading spaces per CommonMark
    # ATX-heading rules. The global HEADING_RE anchors at line-start without
    # leading whitespace, which is intentional for some callers but causes
    # false negatives here for inline B-row `### Resolved` subsections nested
    # under bullet rows (visually indented with 2 spaces).
    _local_heading_re = re.compile(r"^( {0,3})(#{1,6})\s+(.+?)\s*$")
    for line_num, line in enumerate(lines, start=1):
        # Track fenced-code-block state. Format-spec docs (F068, F025, F026)
        # show `**Q1 — ...**` bullets as illustrations inside ``` fences — they
        # are examples, not real pending questions. Same fence-tracking pattern
        # as link-resolution and module-doc scans elsewhere in this file.
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Track Resolved-section state via H2/H3. Any new H2 resets H3 context.
        # A line is in a Resolved area iff in_h2_resolved OR in_h3_resolved.
        heading_m = _local_heading_re.match(line)
        if heading_m:
            level = len(heading_m.group(2))
            heading_text = heading_m.group(3).strip()
            if level == 2:
                flush()
                in_h2_resolved = (heading_text.lower() == "resolved")
                in_h3_resolved = False
                continue
            if level == 3:
                flush()
                # F123: detect H3-form Q-header. If matched, start a new
                # pending H3-form Q (only when not in `## Resolved` H2);
                # in_h3_resolved is set False because the Q header replaces
                # any prior `### Resolved` context.
                h3_q_m = Q_HEADER_H3_RE.match(line)
                if h3_q_m and not in_h2_resolved:
                    q_num = int(h3_q_m.group(1))
                    block_id_match = Q_BLOCK_ID_TRAILING_RE.search(line)
                    has_block_id = block_id_match is not None
                    block_id_value = block_id_match.group(1) if block_id_match else None
                    inline_alt = INLINE_ALTERNATIVES_RE.search(
                        _strip_code_spans(line)
                    ) is not None
                    pending_q = QEntry(
                        source_file=file_path,
                        source_line=line_num,
                        indent="",
                        q_num=q_num,
                        container_id=container_id,
                        has_block_id=has_block_id,
                        block_id_value=block_id_value,
                        inline_alternatives=inline_alt,
                        shape="h3",
                    )
                    in_h3_resolved = False
                    continue
                in_h3_resolved = (heading_text.lower() == "resolved")
                continue
            # Level 1 or 4+: leave state alone (rare in feature docs)
        if in_h2_resolved or in_h3_resolved:
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
            # Strip inline code spans before checking for prose-alternatives.
            # `(A)/(B)/(C)` inside backticks is *describing* the format, not
            # an actual inline alternative — common in feature docs that
            # discuss the ask-format spec itself.
            inline_alt = INLINE_ALTERNATIVES_RE.search(
                _strip_code_spans(line)
            ) is not None
            pending_q = QEntry(
                source_file=file_path,
                source_line=line_num,
                indent=indent,
                q_num=q_num,
                container_id=container_id,
                has_block_id=has_block_id,
                block_id_value=block_id_value,
                inline_alternatives=inline_alt,
                shape="bullet",
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
                continue
            # F123: H3-form Qs may use paragraph-form Recommendation
            if pending_q.shape == "h3":
                rm_para = RECOMMENDATION_PARA_RE.match(line)
                if rm_para:
                    pending_q.recommendation_line = line_num
                    pending_q.recommendation_indent = ""
                    pending_q.recommendation_strength = rm_para.group(1).capitalize()
                    pending_q.recommendation_is_paragraph = True
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
            # Skip when every Q-ref in the display is already attached to an
            # F-number (`F074 Q4`) — those are descriptive phrases that name a
            # Q in a DIFFERENT feature, not pointers to a Q in the link target.
            q_count = len(Q_REF_IN_DISPLAY_RE.findall(display))
            fq_count = len(F_REF_BEFORE_Q_RE.findall(display))
            if q_count > 0 and q_count == fq_count:
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
    """C10: Recommendation bullet at same indent as Q header (not nested).

    F123: N/A for H3-form Qs — there is no indent semantics to enforce
    (H3 + top-level Recommendation are both at column 0).
    """
    findings: list[Finding] = []
    for q in q_entries:
        if q.shape == "h3":
            continue
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
        if q.shape == "h3":
            continue  # F123: C10 N/A for H3-form Qs
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


# C19: each Q's option sub-bullet on its own line, labeled (A)/(B)/...
# C20: blank line after Recommendation separating Q groups

# Accepts any of these option-label conventions at the start of a sub-bullet:
#   - **(A)** text   ← canonical (Ask skill spec, uppercase parens, bold)
#   - (A) text       ← uppercase parens, unbolded
#   - **A)** text    ← bold A)
#   - A) text        ← uppercase A) form (common in legacy docs)
#   - **A.** text    ← bold A.
#   - A. text        ← uppercase A. form
#   - (a) text       ← lowercase parens variants (also seen in legacy)
#   - a) text
#   - **(a)** text
# The audit's intent is "alternatives are labeled and live on their own line."
# All variants above meet that bar; the canonical form `- **(A)** ...` is
# encouraged elsewhere (Ask skill spec) but the audit no longer flags
# well-formed legacy variants. Case (upper/lower) is accepted equally.
OPTION_BULLET_RE = re.compile(
    r"^(\s+)-\s+\*{0,2}"             # bullet, then optional opening bold
    r"(?:"
    r"\(([A-Za-z][0-9]*)\)"          # (X) — paren-wrapped
    r"|([A-Za-z][0-9]*)[.)]"         # X. / X)
    r")"
    r"\*{0,2}"                       # optional closing bold
    r"(?:\s|$)"
)
SUB_BULLET_RE = re.compile(r"^(\s+)-\s+")
# Two option labels on the same line — only the bolded canonical form counts
# as evidence of an attempted (and malformed) option list. Bare parens like
# `(no)` and `(yes)` in prose would over-match the loosened form, so DOUBLE
# stays strict on `**(X)**` ... `**(X)**` per F076 original intent.
DOUBLE_OPTION_INLINE_RE = re.compile(
    r"\*\*\([A-Za-z][0-9]*\)\*\*.*?\*\*\([A-Za-z][0-9]*\)\*\*"
)


def check_c19_option_bullets(q_entries: list[QEntry]) -> list[Finding]:
    """C19: every option sub-bullet between Q header and Recommendation must
    be a labeled bullet `- **(A)** ...` on its own line.

    Catches:
    - Two option labels on the same line: `- **(A)** X. **(B)** Y.` → split needed.
    - Unlabeled sub-bullets that look like alternatives but lack a `(A)` label.

    Continuation lines (further indent) are skipped — they belong to the
    enclosing option."""
    findings: list[Finding] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        qs_sorted = sorted(qs, key=lambda x: x.source_line)
        for i, q in enumerate(qs_sorted):
            start_line = q.source_line
            # End of this Q's options block: the Recommendation line (1-indexed),
            # or the next Q in the same file, or EOF.
            end_line = q.recommendation_line if q.recommendation_line else (
                qs_sorted[i + 1].source_line if i + 1 < len(qs_sorted) else len(lines) + 1
            )
            q_indent_len = len(q.indent)
            # F123: for H3-form Qs, options live at top-level (indent 0)
            # rather than nested. Use indent==0 (TOP_BULLET_RE) for option
            # detection; the unlabeled-sub-bullet flag fires when a
            # top-level bullet inside the H3 body lacks an `(X)` label
            # and the body is not a known annotation.
            is_h3 = (q.shape == "h3")
            for line_num in range(start_line + 1, end_line):
                line = lines[line_num - 1]
                # Two option labels on same line:
                if DOUBLE_OPTION_INLINE_RE.search(line):
                    findings.append(Finding(
                        severity="warning",
                        surface_file=file_path,
                        surface_line=line_num,
                        code="C19",
                        message=(
                            f"Q{q.q_num} options must each be on their own labeled "
                            f"sub-bullet; two `(X)` labels found on one line"
                        ),
                        mechanically_fixable=False,
                    ))
                    continue
                if is_h3:
                    # Top-level bullet detection inside H3 body
                    m_top = re.match(r"^-\s+", line)
                    if not m_top:
                        continue
                    # Inline Recommendation bullet inside H3 body — not an option
                    if RECOMMENDATION_RE.match(line):
                        continue
                    if not OPTION_BULLET_RE.match("  " + line):
                        # Reuse OPTION_BULLET_RE (it expects leading whitespace);
                        # prepend two spaces to satisfy its leading-indent group.
                        body = line.lstrip("- *").strip()
                        if body.startswith((
                            "Note:", "Context:", "Constraint:", "Background:",
                            "Recommendation",
                        )):
                            continue
                        findings.append(Finding(
                            severity="warning",
                            surface_file=file_path,
                            surface_line=line_num,
                            code="C19",
                            message=(
                                f"Q{q.q_num} top-level bullet not labeled as option "
                                f"`- **(A)** ...`; H3-form alternatives must be "
                                f"labeled (A)/(B)/... on their own lines"
                            ),
                            mechanically_fixable=False,
                        ))
                    continue
                # Sub-bullet at Q's option indent level but not labeled
                sub_m = SUB_BULLET_RE.match(line)
                if not sub_m:
                    continue
                sub_indent = len(sub_m.group(1))
                # Must be more-indented than the Q header (a true sub-bullet)
                if sub_indent <= q_indent_len:
                    continue
                # First option-line indent sets the "alternative-row" indent;
                # only flag at that indent (deeper sub-bullets are continuations).
                # Simplification: flag any sub-bullet exactly q_indent_len+2 that
                # lacks the `(LABEL)` shape and contains words suggesting it's
                # being attempted as an alternative.
                if sub_indent == q_indent_len + 2:
                    if not OPTION_BULLET_RE.match(line):
                        # Skip if it's clearly a non-alternative annotation
                        # (e.g., starts with a known prefix like `- **Note:**`).
                        body = line.lstrip("- *").strip()
                        if body.startswith((
                            "Note:", "Context:", "Constraint:", "Background:",
                            # Inline Recommendation lines are NOT options.
                            # Legacy docs sometimes have a rich inline Rec
                            # alongside the stub-Rec terminator; skip those.
                            "Recommendation",
                        )):
                            continue
                        findings.append(Finding(
                            severity="warning",
                            surface_file=file_path,
                            surface_line=line_num,
                            code="C19",
                            message=(
                                f"Q{q.q_num} sub-bullet not labeled as option `- **(A)** ...`; "
                                f"alternatives must be labeled (A)/(B)/... on their own lines"
                            ),
                            mechanically_fixable=False,
                        ))
    return findings


def check_c20_blank_after_recommendation(q_entries: list[QEntry]) -> list[Finding]:
    """C20: every Recommendation line must be followed by a blank line (or end-of-block),
    separating one Q group from the next."""
    findings: list[Finding] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        qs_sorted = sorted(qs, key=lambda x: x.source_line)
        for q in qs_sorted:
            if q.recommendation_line == 0:
                continue
            # F123: H3-form Qs with paragraph-form Recommendation have no
            # indent semantics — continuation lines are at column 0 like
            # the Rec line itself; the strict outdent rule would false-fire.
            # The H2/H3 boundary between Qs is enforced separately by C21
            # and standard markdown structure.
            if q.shape == "h3" and q.recommendation_is_paragraph:
                continue
            # The Recommendation itself may span continuation lines (more-indented).
            # Find the end of the Recommendation block: walk forward while we see
            # blank lines OR lines indented more than the Recommendation.
            rec_line_num = q.recommendation_line
            rec_indent_len = len(q.recommendation_indent or "")
            # Compute the line after the Recommendation block ends.
            j = rec_line_num  # 1-indexed; next line is lines[j]
            while j < len(lines):
                nxt = lines[j]
                if nxt == "":
                    break  # blank line — required separator present
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent > rec_indent_len:
                    j += 1
                    continue
                # A non-blank, non-continuation line at same-or-less indent
                # immediately following the Recommendation block — flag it.
                findings.append(Finding(
                    severity="warning",
                    surface_file=file_path,
                    surface_line=j + 1,
                    code="C20",
                    message=(
                        f"Q{q.q_num} Recommendation must be followed by a blank line "
                        f"before the next Q group / non-continuation content"
                    ),
                    mechanically_fixable=False,
                ))
                break
    return findings


def check_c21_empty_open_questions(
    ask_format_files: list[tuple[str, Path]],
    q_entries: list[QEntry],
) -> list[Finding]:
    """C21: a `## Open Questions` H2 with zero top-level pending Q bullets is
    a Phase-2-transition-missed bug. All Qs resolved → the H2 should be deleted
    and resolutions migrated to a bottom `## Resolved` H2.

    Detected: file has `## Open Questions` heading but `extract_q_entries`
    found zero Q bullets in it (because all Qs are inside `### Resolved`)."""
    findings: list[Finding] = []
    q_entries_by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        q_entries_by_file.setdefault(q.source_file, []).append(q)
    for _, file_path in ask_format_files:
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        oq_line = 0
        in_fence = False
        for line_num, line in enumerate(lines, start=1):
            # Skip code-fenced content — feature-doc-template illustrations
            # (e.g., F015) show `## Open Questions` inside ``` blocks as the
            # canonical template; those are not real Open Questions sections.
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if line.strip() == "## Open Questions":
                oq_line = line_num
                break
        if oq_line == 0:
            continue
        # H2 exists. Did we find any pending Q bullets under it?
        if q_entries_by_file.get(file_path):
            continue
        # H2 with zero pending Qs → Phase 2 missed.
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=oq_line,
            code="C21",
            message=(
                "`## Open Questions` H2 has zero pending Qs (all in ### Resolved). "
                "Phase 2 transition missed — delete this H2 and migrate Resolved "
                "to a bottom `## Resolved` H2."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c22_link_existence_extended(
    scope_files: list[Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C22: extend C1's link-existence check beyond Q.md to feature docs +
    backlogs. C1 covers Q.md; C22 covers everything else where broken
    wiki-links are user-visible (feature docs, backlogs, ask.md files)."""
    findings: list[Finding] = []
    for file_path in scope_files:
        for link in links_in_file(file_path, vault_index):
            if not link.target_resolves:
                findings.append(Finding(
                    severity="error",
                    surface_file=link.source_file,
                    surface_line=link.source_line,
                    code="C22",
                    message=(
                        f"link {link.raw} does not resolve "
                        f"(basename '{link.target_basename}' not in vault)"
                    ),
                    mechanically_fixable=False,
                ))
            elif link.target_anchor_resolves is False:
                anchor_kind = "heading" if link.target_heading else "block-id"
                anchor_val = link.target_heading or link.target_block_id
                findings.append(Finding(
                    severity="error",
                    surface_file=link.source_file,
                    surface_line=link.source_line,
                    code="C22",
                    message=(
                        f"link {link.raw} resolves to file but {anchor_kind} "
                        f"'{anchor_val}' missing in target"
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
    """Pure-state brackets unambiguously belong in a park horizon (per F089 Q1
    hybrid + F100 Verify-horizon split):
    - Watching, Watching Nd/Nh -> ## Verify (passive observation)
    - Verify, Verify-by YYYY-MM-DD -> ## Verify
    - Waiting, Waiting Nd/Nh -> ## Later (awaiting external event)
    - Blocked, Blocked F<n> -> ## Later (external dependency)

    Ambiguous brackets (Questions / Designing) are NOT auto-fixable — they
    need /groom body-reading to decide.
    """
    s = status.strip()
    return (
        s.startswith("Watching")
        or s.startswith("Waiting")
        or s.startswith("Blocked")
        or s.startswith("Verify")  # Verify, Verify-by -> ## Verify horizon
    )


def _park_bracket_target_h2(status: str) -> str:
    """Return the canonical target H2 name for a pure-state park bracket.

    Per F100: Watching/Verify* go to `## Verify`; Waiting/Blocked stay in
    `## Later`. The split surfaces passive-observation rows separately from
    awaiting-event rows in triage.
    """
    s = status.strip()
    if s.startswith("Watching") or s.startswith("Verify"):
        return "Verify"
    return "Later"  # Waiting, Blocked


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
        if auto_fix:
            target_h2 = _park_bracket_target_h2(e.status)
            suffix = f"; auto-moving to ## {target_h2}"
        else:
            suffix = "; needs /groom body-reading"
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
        if auto_fix:
            target_h2 = _park_bracket_target_h2(e.status)
            suffix = f"; auto-moving to ## {target_h2}"
        else:
            suffix = "; needs /groom body-reading"
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
    """C15: [Watching]/[Verify*] rows belong in ## Verify; [Waiting] in ## Later."""
    findings: list[Finding] = []
    for e in entries:
        s = e.status.strip()
        # Watching* and Verify* (Verify, Verify-by) → ## Verify horizon
        if s.startswith("Watching") or s.startswith("Verify"):
            if e.horizon == "Verify":
                continue
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C15",
                message=(
                    f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                    f"— Watching/Verify belongs in ## Verify (passive observation)"
                ),
                mechanically_fixable=True,
            ))
            continue
        # Waiting* → ## Later horizon (separate behavior — awaiting an event)
        if s.startswith("Waiting"):
            if e.horizon == "Later":
                continue
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C15",
                message=(
                    f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                    f"— Waiting belongs in ## Later (awaiting external event)"
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


# ============================================================
# C23 — [Designing] is not a valid terminal bracket
# ============================================================
# Per user direction 2026-05-26 — [Designing] alone creates a deadlock:
# nobody knows whose turn it is. Force every [Designing] row to resolve
# to one of two honest forms:
#   - linked feature doc has N pending Qs → bracket must be [N Questions]
#     (or [Questions] for N=1) — names the user as the next-action owner.
#   - linked feature doc has zero pending Qs → bracket must be [Ready] —
#     the agent can pick it up. Designing is over.


def check_c23_designing_resolves(entries: list[BacklogEntry]) -> list[Finding]:
    """C23: every [Designing] row must resolve to [N Questions] (if its
    linked feature doc has pending Qs) or [Ready] (if not). Designing alone
    creates a turn-ownership deadlock.

    Walks each [Designing] row, finds its linked feature doc, counts pending
    Qs in that doc's `## Open Questions` H2 via `extract_q_entries`, and
    emits a finding that names the correct bracket.

    Rows without a linked feature doc (B-rows with inline Qs in the backlog
    itself) are handled by extracting Qs from the backlog file scoped to the
    row's identifier as the container_id.
    """
    findings: list[Finding] = []
    for e in entries:
        if e.status != "Designing":
            continue
        # Resolve where to count pending Qs.
        target_file: Optional[Path] = None
        container_id = e.identifier
        if e.link is not None and e.link.target_file_path is not None:
            target_file = e.link.target_file_path
            # Container_id for feature-doc Qs is the F-number from the doc stem.
            stem_m = F_NUMBER_PREFIX_RE.match(target_file.stem)
            if stem_m:
                container_id = stem_m.group(1)
        else:
            # No feature-doc link: inline Qs would live in the backlog file
            # itself, under this row. extract_q_entries scopes by container_id
            # via block-ID prefix `^<container>-Q<n>` — match the row's id.
            target_file = e.source_file
        if target_file is None or not target_file.is_file():
            # Can't count Qs — flag as ambiguous; needs user attention.
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] but has no linked "
                    f"feature doc to count Qs against — bracket must be "
                    f"[N Questions] or [Ready], not [Designing] alone"
                ),
                mechanically_fixable=False,
            ))
            continue
        q_entries = extract_q_entries(target_file, container_id)
        # Filter to pending (no Recommendation:Strong/Lean/None — just pending).
        # extract_q_entries returns all Q-headers below ## Open Questions H2
        # before the Resolved sub-section, which IS the pending set.
        pending = len(q_entries)
        if pending > 0:
            correct = f"[{pending} Questions]" if pending > 1 else "[Questions]"
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] but linked doc has "
                    f"{pending} pending Q{'s' if pending != 1 else ''} — "
                    f"bracket must be {correct}, not [Designing] (so the "
                    f"user can see the open questions from the banner)"
                ),
                mechanically_fixable=True,
            ))
        else:
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] with zero pending "
                    f"Qs in its linked doc — bracket must be [Ready], not "
                    f"[Designing] (designing is over; the agent can pick it up)"
                ),
                mechanically_fixable=True,
            ))
    return findings


def check_c24_questions_count_match(entries: list[BacklogEntry]) -> list[Finding]:
    """C24: every `[Questions]` / `[N Questions]` row's bracket count must
    match the linked feature doc's actual pending-Q count.

    Per CAB Backlog discipline (`[N Questions]` when N > 1, bare `[Questions]`
    when N = 1, no bracket at all when N = 0), the bracket must stay in sync
    with the doc state. Observed 2026-06-04 on MUX F037: row was bracketed
    `[Questions]` (bare) but linked doc had 7 pending Qs — should have been
    `[7 Questions]`. The audit banner-Q count was right (7); the row bracket
    was lying about the count. Both forms (under-claiming and over-claiming)
    are flagged.

    Reuses C23's pending-Q-counting logic. Rows with no resolvable target are
    skipped (they'd be reported by C1/C22 link-resolution checks).
    """
    findings: list[Finding] = []
    for e in entries:
        # Match brackets of the form "Questions" (bare) or "N Questions"
        m = re.match(r"^\s*(\d+)\s+Questions?\s*$|^\s*Questions?\s*$", e.status or "")
        if not m:
            continue
        claimed = int(m.group(1)) if m.group(1) else 1
        # Resolve linked feature doc (same approach as C23)
        target_file: Optional[Path] = None
        container_id = e.identifier
        if e.link is not None and e.link.target_file_path is not None:
            target_file = e.link.target_file_path
            stem_m = F_NUMBER_PREFIX_RE.match(target_file.stem)
            if stem_m:
                container_id = stem_m.group(1)
        else:
            target_file = e.source_file
        if target_file is None or not target_file.is_file():
            continue  # link-resolution issue belongs to C1/C22, not here
        actual = len(extract_q_entries(target_file, container_id))
        if actual == claimed:
            continue  # in sync
        if actual == 0:
            # Bracket claims questions but linked doc has none. The bracket is
            # stale — likely all Qs got resolved without the bracket being
            # updated. Most common case after Phase 2 transition.
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C24",
                message=(
                    f"row '{e.identifier}' is [{e.status}] but linked doc has "
                    f"zero pending Qs — bracket is stale (Qs likely all "
                    f"resolved; bracket should be [Ready] or [Done])"
                ),
                mechanically_fixable=True,
            ))
        else:
            correct = f"[{actual} Questions]" if actual > 1 else "[Questions]"
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C24",
                message=(
                    f"row '{e.identifier}' is [{e.status}] (claims {claimed}) "
                    f"but linked doc has {actual} pending Q"
                    f"{'s' if actual != 1 else ''} — bracket must be {correct}"
                ),
                mechanically_fixable=True,
            ))
    return findings


def check_c25_designing_justification(backlog_files: list[Path],
                                      vault_index: dict[str, list[Path]]) -> list[Finding]:
    """C25 (per F106): every [Designing] row must carry a justification.

    F102 says any row bracketed [Designing] must declare what's next — without
    this, designing-state creates a turn-ownership deadlock. C25 is the
    present-time invariant check (C23 was the auto-rewrite escape; F106 keeps
    [Designing] as a valid state that requires justification rather than
    forcing rewrite).

    For each [Designing] row found in any backlog (bullet or H3 form):

    - **Bullet with resolvable feature-doc link** — the linked doc's ## Status
      H2 must lead with `**Designing**` (bolded token per F102) AND the body
      must contain `next action` or `next step` (case-insensitive). Anything
      missing → finding.
    - **Bullet without resolvable link** — must have an inline sub-bullet
      directly below the row matching `- **Status:** Designing —` with `next`
      in the body. Missing → finding.
    - **H3 row** (HA-style) — must have the same inline sub-bullet anywhere
      between the H3 line and the next H3/H2/EOF. Missing → finding.

    Severity: error. No auto-fix — content gap, not mechanical.
    """
    findings: list[Finding] = []
    designing_bracket_re = re.compile(r"\[Designing\b[^\]]*\]")
    h3_row_opener_re = re.compile(
        r"^### "
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    bullet_row_opener_re = re.compile(
        r"^- \*\*"
        r"(?:\[\[)?"
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    status_subbullet_re = re.compile(
        r"^\s+- \*\*Status:\*\*\s+Designing\s+[—-]\s+(.+)$"
    )
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_horizon = ""
        for i, line in enumerate(lines):
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_horizon = m.group(2)
                continue
            # Skip Done / Icebox; only live horizons.
            if current_horizon in ("Done", "Icebox", ""):
                continue
            if not designing_bracket_re.search(line):
                continue
            # Identify row type.
            mh3 = h3_row_opener_re.match(line)
            mb = bullet_row_opener_re.match(line)
            row_match = mh3 or mb
            if row_match is None:
                # Not a row opener — bracketed text inside a sub-bullet or body.
                continue
            identifier = row_match.group(1)
            is_h3 = bool(mh3)
            # Look for the row's body span (lines until the next row/heading).
            # Track code-fence state so a YAML/Python comment like `# Before`
            # inside a ``` fence isn't mistaken for an H1 heading.
            #
            # H3-style rows (HA convention) can contain `- **Q1 — ...`-style
            # sub-bullets in the body that look like bullet row openers but
            # aren't separate rows. When the current row is H3, break only on
            # the next ##/### heading. When the current row is a bullet,
            # break on the next bullet row opener too (adjacent bullet rows
            # are genuinely separate).
            body_lines: list[str] = []
            j = i + 1
            in_fence = False
            while j < len(lines):
                nxt = lines[j]
                if re.match(r"^\s*```", nxt):
                    in_fence = not in_fence
                    body_lines.append(nxt)
                    j += 1
                    continue
                if not in_fence and HEADING_RE.match(nxt):
                    break
                if not in_fence and h3_row_opener_re.match(nxt):
                    break
                if not is_h3 and not in_fence and bullet_row_opener_re.match(nxt):
                    break
                body_lines.append(nxt)
                j += 1
            # Try inline status sub-bullet first (works for any row class).
            inline_ok = False
            for bl in body_lines:
                sm = status_subbullet_re.match(bl)
                if sm and re.search(r"\bnext\b", sm.group(1), re.IGNORECASE):
                    inline_ok = True
                    break
            if inline_ok:
                continue
            # No inline status — for bullet rows with a feature-doc link, fall
            # back to checking the linked doc's ## Status H2.
            doc_ok = False
            if not is_h3:
                # Resolve the row's primary link via `links_in_file`.
                row_links = [
                    lk for lk in links_in_file(backlog_file, vault_index)
                    if lk.source_line == i + 1
                ]
                # Prefer an arrow-trailing link if present, else last wiki-link.
                arrow_link = None
                for lk in row_links:
                    col_text = line[max(0, lk.source_col_start - 4):lk.source_col_start]
                    if "→" in col_text or "->" in col_text:
                        arrow_link = lk
                        break
                target_link = arrow_link or (row_links[-1] if row_links else None)
                if (target_link is not None
                        and target_link.target_resolves
                        and target_link.target_file_path is not None):
                    try:
                        doc_text = target_link.target_file_path.read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError):
                        doc_text = ""
                    # Find ## Status H2 and read its body until next H2 / EOF.
                    status_match = re.search(
                        r"^## Status\b.*$", doc_text, re.MULTILINE,
                    )
                    if status_match:
                        body_start = status_match.end()
                        next_h2 = re.search(
                            r"^## ", doc_text[body_start:], re.MULTILINE,
                        )
                        status_body = (
                            doc_text[body_start:body_start + next_h2.start()]
                            if next_h2 else doc_text[body_start:]
                        )
                        # Leading bold token must be **Designing**
                        first_nonblank = next(
                            (s.strip() for s in status_body.splitlines() if s.strip()),
                            "",
                        )
                        leads_designing = first_nonblank.startswith("**Designing**")
                        has_next = bool(re.search(
                            r"\bnext (action|step|move)\b",
                            status_body, re.IGNORECASE,
                        ))
                        if leads_designing and has_next:
                            doc_ok = True
            if doc_ok:
                continue
            # Emit the finding.
            row_kind = "H3 row" if is_h3 else "bullet row"
            findings.append(Finding(
                severity="error",
                surface_file=backlog_file,
                surface_line=i + 1,
                code="C25",
                message=(
                    f"{row_kind} '{identifier}' [Designing] has no "
                    f"justification — per F102 every [Designing] row must "
                    f"carry **Designing** + next-action (in linked doc's "
                    f"## Status H2, or inline `- **Status:** Designing — "
                    f"<next-action>` sub-bullet)."
                ),
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# C32 — H3-form rows in backlog horizons are forbidden
# C33 — [Designing] rows must have a → [[F<n>]] link to a feature doc
# C34 — Inline Q<n> bullets in backlog row bodies are forbidden
# All three: severity error, no auto-fix (content judgment required).
# ============================================================


_LIVE_HORIZONS = ("Now", "Next", "Later", "Ready", "Active")


def check_c32_h3_rows_forbidden(backlog_files: list[Path]) -> list[Finding]:
    """C32: H3-form rows in backlog horizon H2s are invalid.

    Backlog rows must be bullets per [[CAB Backlog]]. H3-style rows (e.g.
    `### BUG — Title [Designing]`) sail past most row-based checks because
    the canonical parser (ROW_OPENER_RE) is bullet-only. Forbid the form
    entirely so triage and audit see the same shape.
    """
    findings: list[Finding] = []
    h3_re = re.compile(
        r"^### "
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_h2 = ""
        in_fence = False
        for i, line in enumerate(lines, start=1):
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_h2 = m.group(2).strip()
                continue
            if current_h2 not in _LIVE_HORIZONS:
                continue
            mh3 = h3_re.match(line)
            if mh3:
                identifier = mh3.group(1)
                findings.append(Finding(
                    severity="error",
                    surface_file=backlog_file,
                    surface_line=i,
                    code="C32",
                    message=(
                        f"H3-form row '{identifier}' in `## {current_h2}` H2 — "
                        f"backlog rows must be bullets per [[CAB Backlog]]; "
                        f"rewrite as `- **{identifier} — Title** [Status] — body... "
                        f"→ [[F<n> — Title]]`. H3 form escapes the canonical row "
                        f"parser, so most state-purity checks silently skip it."
                    ),
                    mechanically_fixable=False,
                ))
    return findings


def check_c33_designing_needs_link(entries: list[BacklogEntry]) -> list[Finding]:
    """C33: every [Designing] row must have a `→ [[F<n>]]` link.

    [Designing] implies active design work in a linked feature doc. A row
    bracketed [Designing] with no link is in a self-contradictory state —
    no design doc means there's nothing being designed. Honest brackets:
      - [Waiting]  — parked, awaiting external trigger
      - [Ready]    — design resolved, ready to implement
      - [Questions] — has open Qs (which then live in a feature doc, with a link)
    """
    findings: list[Finding] = []
    for e in entries:
        if e.status != "Designing":
            continue
        if e.link is not None:
            continue
        # Skip Done/Icebox horizons.
        if e.horizon in ("Done", "Icebox"):
            continue
        findings.append(Finding(
            severity="error",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C33",
            message=(
                f"row '{e.identifier}' [Designing] has no `→ [[F<n>]]` link "
                f"to a feature doc — [Designing] implies active design work "
                f"in a linked doc. If parked, use [Waiting]; if ready to "
                f"implement, [Ready]; if Qs remain, [N Questions] + link to "
                f"the feature doc holding them."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c34_inline_q_in_row_body(backlog_files: list[Path]) -> list[Finding]:
    """C34: inline `Q<n>` bullets inside backlog row bodies are forbidden.

    Qs belong in feature docs (`{NAME} Features/F<n> — Title.md` §
    `## Open Questions`) or authored directly in the anchor ask file
    (`{NAME} ask.md` § `## Questions`), per
    [[ask-format]]. Embedding Qs in a backlog row body bypasses /ask's
    surfacing (Q.md banner, /triage) and produces a row that contains
    decision content the rest of the workflow can't see.
    """
    findings: list[Finding] = []
    # Match `- **Q<n> —` or `  - **Q<n> —` (indented or not — any bullet form).
    inline_q_re = re.compile(r"^\s*- \*\*Q\d+\s+[—-]")
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_h2 = ""
        in_fence = False
        for i, line in enumerate(lines, start=1):
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_h2 = m.group(2).strip()
                continue
            # Skip Done/Icebox/Verify (Verify rows reference Qs legitimately).
            if current_h2 in ("Done", "Icebox", "Verify", ""):
                continue
            if inline_q_re.match(line):
                findings.append(Finding(
                    severity="error",
                    surface_file=backlog_file,
                    surface_line=i,
                    code="C34",
                    message=(
                        f"inline `Q<n>` bullet in backlog row body (`## {current_h2}`) "
                        f"— Qs belong in a feature doc's `## Open Questions` H2 or in "
                        f"`{{NAME}} ask.md` § `## Questions` per [[ask-format]]. Move the Q to "
                        f"the appropriate surface and replace this row's body with "
                        f"a `→ [[F<n> — Title]]` link."
                    ),
                    mechanically_fixable=False,
                ))
    return findings


def check_c35_ask_md_drift(
    anchor_backlogs: dict[str, Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C35 (F124): each Q<n> reference in `{NAME} ask.md` § Questions must
    correspond to a pending Q in the linked feature doc.

    Surfacing case (F077 Q7, 2026-06-06): SKA ask.md carried 'F077 ... (Q1, Q7)'
    forward as pending, but F077's doc had Q7 in `### Resolved` (choice A).
    The /ask runbook step 3 requires 'live re-check each carried-forward
    entry' — this check mechanizes it.

    Walks each anchor backlog's sibling `{NAME} ask.md` file, parses the
    `## Questions` H2 region, extracts wiki-linked feature docs + the
    Q-numbers each bullet claims pending, then cross-checks against the
    linked doc's actual pending-Q set via `extract_q_entries` (which is
    now H3-aware thanks to F123).
    """
    findings: list[Finding] = []
    q_ref_re = re.compile(r"\bQ(\d+)\b")
    wiki_link_re = re.compile(r"\[\[([^|\]]+?)(?:\|[^\]]+)?\]\]")
    for name, backlog_file in anchor_backlogs.items():
        ask_file = backlog_file.parent / f"{name} ask.md"
        if not ask_file.is_file():
            continue
        try:
            text = ask_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        # Find ## Questions H2 region
        q_start = -1
        q_end = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == "## Questions":
                q_start = i + 1
            elif q_start >= 0 and re.match(r"^## ", line):
                q_end = i
                break
        if q_start < 0:
            continue
        # Parse bullets in the Questions region
        for line_num in range(q_start, q_end):
            line = lines[line_num]
            if not re.match(r"^\s*-\s+", line):
                continue
            link_m = wiki_link_re.search(line)
            if not link_m:
                continue
            target_name = link_m.group(1).strip()
            # Strip any block-ID fragment from target name
            if "#" in target_name:
                target_name = target_name.split("#", 1)[0]
            target_file = resolve_target(target_name, ask_file, vault_index)
            if target_file is None or not target_file.is_file():
                continue  # link resolution belongs to C1/C22
            # Only feature docs participate (skip non-F<n> targets like
            # `[[CAB ...]]` references inside descriptive text).
            stem_m = F_NUMBER_PREFIX_RE.match(target_file.stem)
            if not stem_m:
                continue
            container_id = stem_m.group(1)
            # Extract claimed Q-numbers from the bullet line (and any
            # immediately-following indented continuation lines).
            bullet_text = line
            j = line_num + 1
            while j < q_end:
                nxt = lines[j]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    bullet_text += " " + nxt
                    j += 1
                elif nxt == "":
                    break
                else:
                    break
            claimed = sorted({int(m.group(1)) for m in q_ref_re.finditer(bullet_text)})
            if not claimed:
                continue
            pending_qs = {q.q_num for q in extract_q_entries(target_file, container_id)}
            stale = [q for q in claimed if q not in pending_qs]
            if not stale:
                continue
            pending_str = (
                ", ".join(f"Q{n}" for n in sorted(pending_qs))
                if pending_qs else "none"
            )
            stale_str = ", ".join(f"Q{n}" for n in stale)
            findings.append(Finding(
                severity="warning",
                surface_file=ask_file,
                surface_line=line_num + 1,
                code="C35",
                message=(
                    f"ask.md claims {stale_str} pending in {container_id} "
                    f"but linked doc has those resolved or absent "
                    f"(actual pending: {pending_str}). /ask runbook step 3 "
                    f"requires live re-check; drift carried forward."
                ),
                mechanically_fixable=False,
            ))
    return findings


################################################################
# C36 (F126) — backtick-quoted file-paths must be links
################################################################

# Recognized file extensions for bare-filename detection
_C36_EXTENSIONS = (
    "md", "py", "sh", "yaml", "yml", "toml", "json", "txt",
    "html", "css", "rs", "ts", "tsx", "js", "jsx",
)
_C36_EXT_RE = re.compile(
    r"\.(" + "|".join(_C36_EXTENSIONS) + r")$"
)

# Capture every backtick-quoted token on a line that doesn't already
# straddle a line boundary. We restrict to single-backtick spans so we
# don't accidentally pick up ``code with `nested` `` fragments.
_BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")

# Inside a backtick token, the path-like content. Either:
#  - starts with `/`, `~/`, `./`, `../`
#  - bare filename ending in a recognized extension
_C36_PATH_LEAD_RE = re.compile(r"^(/|~/|\./|\.\./)")


def _c36_is_path_like(token: str) -> bool:
    """Heuristic: token inside backticks looks like a single file-path.

    Rejects:
    - whitespace (command-line)
    - code shapes (parens, equals, braces)
    - glob/regex metacharacters
    - directory references ending in `/`
    - templated paths containing `<...>` placeholders or `{...}` or YYYY/NNN
      style placeholders
    - slash-commands (single segment after `/`, all lowercase a-z0-9-)
    """
    t = token.strip()
    if not t:
        return False
    # Reject obvious non-path shapes
    if any(c in t for c in " \t"):
        return False  # command-line / multi-word
    if any(c in t for c in "()=<>|&;{}"):
        return False  # code / templated
    if any(c in t for c in "*?"):
        return False  # glob
    if "[" in t or "]" in t:
        return False  # regex/glob class
    # Reject directory references ending in `/`
    if t.endswith("/"):
        return False
    # Reject placeholder paths
    if "YYYY" in t or "MM-DD" in t or "NNN" in t:
        return False
    # Reject bare-extension mentions like `.md` / `.html` (no stem)
    if t.startswith(".") and _C36_EXT_RE.fullmatch(t):
        return False
    # Reject slash-commands: leading `/` followed by a single segment of
    # lowercase letters / digits / hyphens — these are `/ask`, `/groom`,
    # `/audit foo`, etc., NOT file paths.
    if t.startswith("/"):
        rest = t[1:]
        if "/" not in rest and not _C36_EXT_RE.search(rest):
            # single-segment after leading slash, no extension → command
            return False
    # Reject `.app` directory bundles (macOS) — they aren't text files
    if t.endswith(".app"):
        return False
    # Accept absolute / home / relative paths
    if _C36_PATH_LEAD_RE.match(t):
        return True
    # Accept bare basenames ending in a recognized extension
    if _C36_EXT_RE.search(t):
        # But require it look like a filename (no `/` already counted by the
        # absolute case; bare-basename means no `/` at all)
        return "/" not in t
    return False


def _c36_resolve_replacement(
    token: str, vault_index: dict[str, list[Path]]
) -> Optional[str]:
    """Compute the replacement link for a path-like backtick token.

    Returns the replacement string (without surrounding backticks) or
    None if no clean replacement exists — caller leaves the backticks
    intact and routes to QFix for manual review.

    Discipline (post-shipping-bug 2026-06-07): NEVER emit a markdown link
    `[name](path)` whose path doesn't actually resolve. A non-resolving
    link breaks C1/C22 link-existence checks downstream. The valid
    replacements are:
      - `[[stem]]`     — only when stem is in the vault index (.md files)
      - `[name](path)` — only when the path resolves on disk (absolute,
                         `~/`-expanded, or relative-to-vault-root)
      - None           — otherwise; caller leaves the backticks intact
    """
    raw = token.strip()
    name = raw.rsplit("/", 1)[-1]
    if "." in name:
        stem = name.rsplit(".", 1)[0]
        ext = name.rsplit(".", 1)[1].lower()
    else:
        stem = name
        ext = ""
    # Safe automatic replacements (in priority order):
    #
    # 1. Wiki-link `[[stem]]` — when basename is `.md` AND uniquely resolvable
    #    in the vault index. Ambiguous basenames (SKILL.md, README.md, ...)
    #    are skipped: the resulting `[[SKILL]]` would silently resolve
    #    "somewhere" via path-proximity, worse affordance than the backticks.
    if ext == "md" and stem in vault_index and len(vault_index[stem]) == 1:
        return f"[[{stem}]]"
    # 2. Markdown link `[name](path)` — when the path is ABSOLUTE (starts
    #    with `/` or `~/`) AND the file actually exists on disk. Absolute
    #    paths are unambiguous; the existing `_parse_markdown` resolver
    #    accepts them correctly (no C1/C22 false positive). Relative paths
    #    are deliberately skipped — they'd resolve to "source_file/path"
    #    which is almost never what the author meant, and would trigger
    #    C22 link-existence errors downstream.
    if raw.startswith(("/", "~/")):
        expanded = Path(raw).expanduser()
        if expanded.is_file():
            return f"[{name}]({raw})"
    return None


def _c36_is_inside_existing_link(line: str, span_start: int) -> bool:
    """Crude check: is the column inside an existing [..](..) or [[..]]?

    Looks at the prefix of the line. If an unmatched `[` precedes the span
    without a closing `]` between it and the span, we're inside a markdown
    or wiki link target/text and should NOT flag this backtick.
    """
    prefix = line[:span_start]
    # Count unbalanced `[` vs `]` to the left of the span.
    open_brackets = prefix.count("[") - prefix.count("]")
    return open_brackets > 0


def check_c36_backtick_filepath(
    file_path: Path, vault_index: dict[str, list[Path]]
) -> list[Finding]:
    """C36: backtick-quoted file-paths on Q.md / ask.md should be wiki-links
    or markdown-links so they're clickable.

    Surfacing case (F126, 2026-06-07): the user observed that bare backtick
    file-path tokens in `Q.md` / `{NAME} ask.md` aren't navigable from
    Obsidian — they look like links but aren't, forcing the user to manually
    copy the path. C36 forbids them and `--fix` mechanically replaces them.
    """
    findings: list[Finding] = []
    if not file_path.is_file():
        return findings
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return findings
    in_fence = False
    for line_num, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Skip audit-q residual sub-bullets — these are findings rendered as
        # `- **C<NN>** ...` on a B-QFix row; the backticks in their bodies are
        # quoting the original finding's offending token, not a real path the
        # author wrote. Re-flagging them creates a recursion where every audit
        # pass surfaces residuals as new findings.
        if re.match(r"^\s*-\s+\*\*[CD]\d+\*\*\s", line):
            continue
        for m in _BACKTICK_SPAN_RE.finditer(line):
            token = m.group(1)
            if not _c36_is_path_like(token):
                continue
            if _c36_is_inside_existing_link(line, m.start()):
                continue
            replacement = _c36_resolve_replacement(token, vault_index)
            mech_fixable = replacement is not None
            findings.append(Finding(
                severity="warning",
                surface_file=file_path,
                surface_line=line_num,
                code="C36",
                message=(
                    f"backtick file-path `{token}` should be a link — "
                    + (f"suggested: `{replacement}`"
                       if replacement
                       else "basename doesn't resolve in vault index "
                            "(manual review)")
                ),
                mechanically_fixable=mech_fixable,
            ))
    return findings


def apply_c36_fix(
    file_path: Path,
    findings: list[Finding],
    vault_index: dict[str, list[Path]],
) -> int:
    """Apply mechanical replacements for C36 findings on file_path.

    Processes findings descending by (line, span-start) so earlier offsets
    on the same line aren't invalidated by later edits. Idempotent: a
    second pass on the cleaned file produces 0 changes.
    Returns the number of replacements actually applied.
    """
    relevant = [
        f for f in findings
        if f.code == "C36"
        and f.surface_file == file_path
        and f.mechanically_fixable
    ]
    if not relevant:
        return 0
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (OSError, UnicodeDecodeError):
        return 0
    # Re-scan to find exact spans (the original check stored line numbers,
    # not column ranges). For each affected line, replace every path-like
    # backtick span via the regex sub — single-pass per line is correct.
    affected_lines = sorted({f.surface_line for f in relevant})
    applied = 0

    def _sub(m: re.Match) -> str:
        nonlocal applied
        token = m.group(1)
        if not _c36_is_path_like(token):
            return m.group(0)
        # Check column-context guard (existing-link)
        prefix = m.string[:m.start()]
        if (prefix.count("[") - prefix.count("]")) > 0:
            return m.group(0)
        replacement = _c36_resolve_replacement(token, vault_index)
        if replacement is None:
            return m.group(0)
        applied += 1
        return replacement

    in_fence = False
    for idx in range(len(lines)):
        line = lines[idx]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if (idx + 1) not in affected_lines:
            continue
        lines[idx] = _BACKTICK_SPAN_RE.sub(_sub, line)
    if applied:
        file_path.write_text("".join(lines), encoding="utf-8")
    return applied


def apply_c23_fix(backlog_file: Path,
                  entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Rewrite [Designing] brackets to [N Questions] or [Ready] based on
    pending Q-count in linked feature docs. Returns (changed, log)."""
    fix_log: list[str] = []
    designing = [e for e in entries if e.status == "Designing"]
    if not designing:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    changed = False
    for e in designing:
        target_file: Optional[Path] = None
        container_id = e.identifier
        if e.link is not None and e.link.target_file_path is not None:
            target_file = e.link.target_file_path
            stem_m = F_NUMBER_PREFIX_RE.match(target_file.stem)
            if stem_m:
                container_id = stem_m.group(1)
        else:
            target_file = e.source_file
        if target_file is None or not target_file.is_file():
            continue
        q_entries = extract_q_entries(target_file, container_id)
        pending = len(q_entries)
        if pending > 0:
            new_bracket = (
                f"[{pending} Questions]" if pending > 1 else "[Questions]"
            )
        else:
            new_bracket = "[Ready]"
        # 0-indexed line
        line_idx = e.source_line - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        old_line = lines[line_idx]
        # Replace [Designing] with new_bracket on this line. Use BRACKET_RE-style
        # narrow head-region replacement: only the first [Designing] occurrence
        # in the row's head (between **Title** and the first ` — `).
        title_match = re.match(r"^- \*\*[^*]+\*\*", old_line)
        if not title_match:
            continue
        post_title = old_line[title_match.end():]
        sep_match = re.search(r"\s[—-]\s", post_title)
        head_end_in_post = sep_match.start() if sep_match else len(post_title)
        head = post_title[:head_end_in_post]
        rest = post_title[head_end_in_post:]
        new_head = head.replace("[Designing]", new_bracket, 1)
        if new_head == head:
            continue
        new_line = old_line[: title_match.end()] + new_head + rest
        lines[line_idx] = new_line
        changed = True
        fix_log.append(
            f"row '{e.identifier}' [Designing] → {new_bracket} "
            f"(pending Qs: {pending})"
        )
    if changed:
        backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed, fix_log


def apply_c24_fix(backlog_file: Path,
                  entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Rewrite `[Questions]` / `[N Questions]` brackets to match the linked
    feature doc's actual pending-Q count. Mirrors apply_c23_fix's mechanics.
    Returns (changed, log). Bare `[Questions]` on a row whose linked doc has
    7 Qs becomes `[7 Questions]`; `[3 Questions]` on a doc with 0 Qs becomes
    `[Ready]` (the bracket-promise is stale, downstream of all Qs being
    resolved without the bracket being updated)."""
    fix_log: list[str] = []
    questions_rows: list[tuple[BacklogEntry, str]] = []
    for e in entries:
        if not e.status:
            continue
        m = re.match(r"^\s*(\d+)\s+Questions?\s*$|^\s*Questions?\s*$", e.status)
        if m:
            questions_rows.append((e, e.status))
    if not questions_rows:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    changed = False
    for e, old_status in questions_rows:
        target_file: Optional[Path] = None
        container_id = e.identifier
        if e.link is not None and e.link.target_file_path is not None:
            target_file = e.link.target_file_path
            stem_m = F_NUMBER_PREFIX_RE.match(target_file.stem)
            if stem_m:
                container_id = stem_m.group(1)
        else:
            target_file = e.source_file
        if target_file is None or not target_file.is_file():
            continue
        actual = len(extract_q_entries(target_file, container_id))
        m = re.match(r"^\s*(\d+)\s+Questions?\s*$", old_status)
        claimed = int(m.group(1)) if m else 1
        if actual == claimed:
            continue
        if actual == 0:
            new_bracket = "[Ready]"
        else:
            new_bracket = (
                f"[{actual} Questions]" if actual > 1 else "[Questions]"
            )
        old_bracket = f"[{old_status}]"
        line_idx = e.source_line - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        old_line = lines[line_idx]
        # Same head-region replacement as apply_c23_fix.
        title_match = re.match(r"^- \*\*[^*]+\*\*", old_line)
        if not title_match:
            continue
        post_title = old_line[title_match.end():]
        sep_match = re.search(r"\s[—-]\s", post_title)
        head_end_in_post = sep_match.start() if sep_match else len(post_title)
        head = post_title[:head_end_in_post]
        rest = post_title[head_end_in_post:]
        new_head = head.replace(old_bracket, new_bracket, 1)
        if new_head == head:
            continue
        new_line = old_line[: title_match.end()] + new_head + rest
        lines[line_idx] = new_line
        changed = True
        fix_log.append(
            f"row '{e.identifier}' {old_bracket} → {new_bracket} "
            f"(pending Qs: {actual})"
        )
    if changed:
        backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed, fix_log


def _resolve_owning_anchor(
    surface_file: Path, anchor_backlogs: dict[str, Path]
) -> Optional[str]:
    """Return the anchor name whose tree (anchor_root = backlog.parents[2])
    contains surface_file. Sorts anchors by anchor-root path length, longest
    first, so sub-anchors (e.g., A2X inside SVAR's tree) match before
    parents. Returns None when surface_file is outside every anchor tree
    (e.g., Q.md itself, or vault-level files)."""
    candidates: list[tuple[int, str, Path]] = []
    for name, backlog in anchor_backlogs.items():
        try:
            root = backlog.parents[2]
        except IndexError:
            continue
        candidates.append((len(root.parts), name, root))
    # Longest-path first → most-specific anchor wins.
    candidates.sort(key=lambda t: t[0], reverse=True)
    for _, name, root in candidates:
        try:
            surface_file.relative_to(root)
            return name
        except ValueError:
            continue
    return None


def file_qfix_row(
    backlog_file: Path, anchor_name: str, findings: list[Finding]
) -> tuple[bool, str]:
    """Find or create the singleton `B-QFix [Ready]` row in backlog_file,
    then replace its sub-bullets with the current findings list.

    Idempotent: subsequent runs with the same findings produce an identical
    file; new findings replace old sub-bullets; zero findings shouldn't
    happen here (the caller filters empties before calling).

    Returns (changed, summary_msg)."""
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, f"couldn't read {backlog_file.name}"

    lines = text.splitlines()
    # Format new sub-bullets — relative path to VAULT_ROOT for compactness.
    # Wrap any `[[X]]` wiki-link OR `[name](path)` markdown-link patterns in
    # the message text in backticks so `_strip_code_spans` makes them invisible
    # to C1/C22 link-resolution on subsequent runs. Without this guard,
    # sub-bullets containing finding messages with link forms are themselves
    # flagged as broken links → routing-induced cascade (observed 2026-06-04
    # for wiki-links and 2026-06-07 for markdown-links when F126 surfaced
    # markdown-link findings).
    def _backtick_wiki_links(msg: str) -> str:
        # Wrap wiki-links first (so the markdown-link regex doesn't catch the
        # backticked replacement)
        msg = re.sub(r"\[\[([^\[\]]*)\]\]", r"`[[\1]]`", msg)
        # Wrap markdown links: [name](path) — but skip those already inside
        # backticks. The `(?<!\`)` lookbehind would be cleaner but Python's
        # variable-width lookbehind support varies; instead just wrap any
        # remaining unbackticked form.
        msg = re.sub(r"(?<!`)\[([^\[\]]+)\]\(([^)]+)\)(?!`)", r"`[\1](\2)`", msg)
        return msg

    new_subs: list[str] = []
    for f in findings:
        try:
            rel = f.surface_file.relative_to(VAULT_ROOT)
        except ValueError:
            rel = f.surface_file
        safe_msg = _backtick_wiki_links(f.message)
        new_subs.append(
            f"  - **{f.code}** {rel}:{f.surface_line} — {safe_msg}"
        )

    qfix_row_text = (
        f"- **B-QFix — QFix** [Ready] — audit q findings routed by --fix; "
        f"each sub-bullet is a residual on {anchor_name}'s tree needing the "
        f"100%-fix discipline (per the audit skill's Governing principle). "
        f"^B-QFix"
    )

    # Locate existing B-QFix row.
    qfix_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- **B-QFix"):
            qfix_idx = i
            break

    if qfix_idx is not None:
        # Find end of existing sub-bullets (`  - ` indented lines, with
        # optional intervening blank lines that don't terminate the block).
        end = qfix_idx + 1
        while end < len(lines):
            stripped = lines[end]
            if stripped.startswith("  - "):
                end += 1
                continue
            # Blank line — peek next to see if sub-bullets continue.
            if not stripped.strip() and end + 1 < len(lines) \
                    and lines[end + 1].startswith("  - "):
                end += 1
                continue
            break
        lines[qfix_idx] = qfix_row_text
        lines[qfix_idx + 1: end] = new_subs
        result = f"updated B-QFix with {len(new_subs)} sub-bullet(s)"
    else:
        # Create row at the top of `## Ready`. Create the H2 if absent.
        ready_idx: Optional[int] = None
        for i, line in enumerate(lines):
            if line.strip() == "## Ready":
                ready_idx = i
                break
        if ready_idx is None:
            # Insert `## Ready` before the first existing H2, or at end.
            insert_at = len(lines)
            for i, line in enumerate(lines):
                if line.startswith("## "):
                    insert_at = i
                    break
            lines.insert(insert_at, "## Ready")
            lines.insert(insert_at + 1, "")
            ready_idx = insert_at
        insert_at = ready_idx + 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        block = [qfix_row_text] + new_subs + [""]
        for j, ln in enumerate(block):
            lines.insert(insert_at + j, ln)
        result = f"created B-QFix with {len(new_subs)} sub-bullet(s)"

    backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True, result


def clear_qfix_row(backlog_file: Path) -> tuple[bool, str]:
    """Delete an existing singleton `B-QFix` row (and its sub-bullets) from
    backlog_file. No-op if the row doesn't exist. Returns (changed, msg).

    Called when an anchor's residual findings drop to zero so stale captures
    from prior runs don't persist as a phantom Ready row inflating the
    anchor's banner.
    """
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, f"couldn't read {backlog_file.name}"
    lines = text.splitlines()
    qfix_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- **B-QFix"):
            qfix_idx = i
            break
    if qfix_idx is None:
        return False, "no QFix row to clear"
    end = qfix_idx + 1
    while end < len(lines):
        stripped = lines[end]
        if stripped.startswith("  - "):
            end += 1
            continue
        if not stripped.strip() and end + 1 < len(lines) \
                and lines[end + 1].startswith("  - "):
            end += 1
            continue
        break
    del lines[qfix_idx:end]
    while qfix_idx < len(lines) and not lines[qfix_idx].strip():
        del lines[qfix_idx]
        if qfix_idx > 0 and not lines[qfix_idx - 1].strip():
            break
    backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True, "cleared stale B-QFix row"


def route_findings_to_qfix(
    findings: list[Finding], anchor_backlogs: dict[str, Path]
) -> list[str]:
    """For each non-mechanically-fixable finding, file it as a sub-bullet on
    the owning anchor's `B-QFix` `[Ready]` row. Mechanically-fixable findings
    are excluded (they've already been auto-fixed in this run; they won't
    survive to the next audit pass).

    Per audit § Governing principle (2026-06-04): every residual the script
    can't fix gets routed to an anchor-local backlog row where the owning
    Pilot's next /triage or /groom drives it to zero under the 100%-fix rule.

    When residual findings for an anchor drop to zero, the stale B-QFix row
    is deleted so the anchor's banner reflects the current state.

    Returns a per-anchor log of routing actions."""
    residual = [f for f in findings if not f.mechanically_fixable]
    # Build per-anchor groups; every anchor in scope gets an entry (possibly
    # empty) so anchors whose residual dropped to zero get their stale QFix
    # cleared rather than left to inflate the banner.
    groups: dict[str, list[Finding]] = {a: [] for a in anchor_backlogs}
    for f in residual:
        owner = _resolve_owning_anchor(f.surface_file, anchor_backlogs)
        if owner is None:
            continue
        groups[owner].append(f)
    log: list[str] = []
    for anchor in sorted(groups):
        backlog_file = anchor_backlogs[anchor]
        if groups[anchor]:
            changed, msg = file_qfix_row(backlog_file, anchor, groups[anchor])
        else:
            changed, msg = clear_qfix_row(backlog_file)
        if changed:
            log.append(f"  {anchor}: {msg}")
    return log


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
        # C15/C16 — pure-state park brackets in wrong horizon
        if _is_pure_state_park_bracket(s):
            target_h2 = _park_bracket_target_h2(s)
            if e.horizon != target_h2:
                moves.append((e, target_h2))
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
    """Find every {NAME} Backlog.md in the vault. Return name → path.

    Per F107: backlogs nested deeper than SKA's own backlog level inside
    `Skill Agent/` are SKA sub-skill anchors (Triage, Mode, Crank, etc.) —
    SKA's internal organization, not standalone projects. They get filtered
    out of Q.md presence here. Their underlying files keep existing on disk.
    """
    out: dict[str, Path] = {}
    for path in vault_root.rglob("* Backlog.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        # Accept either the legacy `<X> Plan/` form or the F094 four-bucket
        # `<X> Track/` form. Migrated anchors hold the backlog under Track.
        if not (path.parent.name.endswith("Plan") or path.parent.name.endswith("Track")):
            continue
        # F107 — exclude every backlog under `Skill Agent/` except SKA's own.
        # SKA's backlog sits at `Skill Agent/SKA Docs/SKA Track/SKA Backlog.md`
        # (4 parts after `Skill Agent`, inclusive). Anything deeper — CAB, CAE,
        # CSE, SKA skill-trait at the sibling level, plus the sub-skill nesting
        # under Drive Loop / Discipline / Utility / Dev / Doc / skills — is part
        # of SKA and rolls up under SKA's presence in Q.md. Per user direction
        # 2026-06-02 (round 2): "C-A-B and C-A-E are part of SKA, and that's
        # the only backlog we should be looking at."
        if "Skill Agent" in path.parts:
            sa_idx = path.parts.index("Skill Agent")
            if len(path.parts) - sa_idx > 4:
                continue
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
    # User-actionable banner counts (Ready, Questions, Verify-bracket leftover)
    # only count from ACTIVE horizons. Rows parked in ## Later or ## Verify are
    # passive observation, not active questions. Per user direction 2026-06-02
    # after MUX banner showed "Questions 13" with Now/Next at 0.
    ACTIVE_HORIZONS = {"Active", "Ready", "Now", "Next", "Legwork"}
    actionable = [e for e in live if e.horizon in ACTIVE_HORIZONS]
    # Compute counts by bracket
    active_n = sum(1 for e in actionable if e.status == "Active")
    ready_n = sum(1 for e in actionable if e.status == "Ready")
    verify_n = sum(1 for e in actionable if e.status == "Verify")
    # Questions count = sum of Q-markers across linked targets for each
    # [N Questions]/[Questions] row in active horizons only.
    questions_n = 0
    for e in actionable:
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
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Verify", "Icebox")}
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
        f"# [{tag}]  [[{name} ask|{name}]]  -  "
        f"Ready {ready_n}    Questions {questions_n}   |   "
        f"Now {horizon_counts['Now']}    Next {horizon_counts['Next']}    "
        f"Later {horizon_counts['Later']}    Verify {horizon_counts['Verify']}    "
        f"Icebox {horizon_counts['Icebox']}"
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
    parser.add_argument(
        "--scope",
        choices=["q", "backlog", "feature-doc", "all"],
        default="q",
        help=(
            "Audit scope. Default `q` (reachability-limited from Q.md): "
            "audits Q.md + each anchor's backlog listed in Q.md + each feature "
            "doc linked from those backlogs. `backlog` audits one anchor's "
            "backlog + linked feature docs (requires --anchor). `feature-doc` "
            "audits one feature doc (requires --feature-doc). `all` is the "
            "vault-wide pre-2026-05-26 behavior — audits every F<n>.md in every "
            "Features/ folder regardless of reachability."
        ),
    )
    parser.add_argument("--anchor", type=str, default=None,
                        help="(scope=backlog) anchor name, e.g. 'SKA'")
    parser.add_argument("--feature-doc", type=str, default=None,
                        help="(scope=feature-doc) path to a feature doc")
    args = parser.parse_args()
    if args.scope == "backlog" and not args.anchor:
        print("error: --scope backlog requires --anchor NAME", file=sys.stderr)
        return 2
    if args.scope == "feature-doc" and not args.feature_doc:
        print("error: --scope feature-doc requires --feature-doc PATH", file=sys.stderr)
        return 2
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
    findings: list[Finding] = []
    c4_fixes_applied: list[str] = []
    derived_banners: dict[str, str] = {}
    all_backlogs = find_anchor_backlogs(VAULT_ROOT)

    # Compute scoped backlog dict per --scope:
    if args.scope == "feature-doc":
        # Skip Q.md + backlog entirely; audit only the one feature doc.
        anchor_backlogs: dict[str, Path] = {}
    elif args.scope == "backlog":
        if args.anchor not in all_backlogs:
            print(f"error: anchor '{args.anchor}' has no backlog in {VAULT_ROOT}", file=sys.stderr)
            return 2
        anchor_backlogs = {args.anchor: all_backlogs[args.anchor]}
    else:
        # scope=q or scope=all → all anchor backlogs
        anchor_backlogs = all_backlogs

    # C1 + C2 on Q.md — only when auditing Q.md itself (scope=q or scope=all).
    if args.scope in ("q", "all"):
        qmd_links = links_in_file(Q_MD, vault_index)
        qmd_text = Q_MD.read_text(encoding="utf-8")
        findings.extend(check_c1_link_existence(qmd_links))
        findings.extend(check_c2_q_marker_existence(qmd_links, qmd_text))
    # C4 + D1 require walking each anchor's backlog (in the scoped set).
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
    # B16 — C6 / C8 / C9 / C10 walk feature docs + the anchor ask file per anchor.
    # Default (scope=q or scope=backlog): reachability-limited via backlog wiki-links.
    # `--scope all` gives the original vault-wide behavior.
    if args.scope == "feature-doc":
        # Audit just one feature doc.
        fd_path = Path(args.feature_doc).expanduser().resolve()
        if not fd_path.is_file():
            print(f"error: feature doc not found: {fd_path}", file=sys.stderr)
            return 2
        stem_m = F_NUMBER_PREFIX_RE.match(fd_path.stem)
        cid = stem_m.group(1) if stem_m else fd_path.stem
        ask_format_files = [(cid, fd_path)]
    else:
        reachable = args.scope != "all"
        ask_format_files = find_ask_format_files(
            anchor_backlogs, vault_index=vault_index, reachable_only=reachable
        )
    all_q_entries: list[QEntry] = []
    for container_id, file_path in ask_format_files:
        all_q_entries.extend(extract_q_entries(file_path, container_id))
    findings.extend(check_c6_block_id_present(all_q_entries))
    findings.extend(check_c8_inline_alternatives(all_q_entries))
    findings.extend(check_c9_recommendation_present(all_q_entries))
    findings.extend(check_c10_recommendation_outdent(all_q_entries))
    findings.extend(check_c19_option_bullets(all_q_entries))
    findings.extend(check_c20_blank_after_recommendation(all_q_entries))
    findings.extend(check_c21_empty_open_questions(ask_format_files, all_q_entries))
    # C22 — link existence across feature docs + backlogs + ask.md files
    c22_scope: list[Path] = []
    c22_scope.extend(p for _, p in ask_format_files)
    c22_scope.extend(anchor_backlogs.values())
    for backlog_file in anchor_backlogs.values():
        ask_md = backlog_file.parent / f"{backlog_file.stem.replace(' Backlog', ' ask')}.md"
        if ask_md.is_file():
            c22_scope.append(ask_md)
    findings.extend(check_c22_link_existence_extended(c22_scope, vault_index))
    # B16 — C7 walks the same ask-format files + backlogs + Q.md (when in scope)
    c7_scope: list[Path] = []
    if args.scope in ("q", "all"):
        c7_scope.append(Q_MD)
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
        findings.extend(check_c23_designing_resolves(entries))
        findings.extend(check_c24_questions_count_match(entries))
        findings.extend(check_c25_designing_justification([backlog_file], vault_index))
        findings.extend(check_c32_h3_rows_forbidden([backlog_file]))
        findings.extend(check_c33_designing_needs_link(entries))
        findings.extend(check_c34_inline_q_in_row_body([backlog_file]))
    # F124 — C35 ask.md drift check walks every anchor backlog's sibling
    # `{NAME} ask.md`. Runs once after the per-anchor loop (not per anchor),
    # since each ask.md is keyed by its sibling backlog's anchor name.
    findings.extend(check_c35_ask_md_drift(anchor_backlogs, vault_index))
    # F126 — C36 backtick-filepath check. Runs on Q.md (when in scope),
    # every per-anchor `{NAME} ask.md`, AND every anchor backlog —
    # backlog rows are the source content that triage-section.py copies
    # into Q.md, so fixing the surface alone gets overwritten by the
    # next D1 banner-rewrite. Source-fix is durable.
    c36_surfaces: list[Path] = []
    if args.scope in ("q", "all"):
        c36_surfaces.append(Q_MD)
    for name, backlog_file in anchor_backlogs.items():
        c36_surfaces.append(backlog_file)
        ask_md = backlog_file.parent / f"{name} ask.md"
        if ask_md.is_file():
            c36_surfaces.append(ask_md)
    for surface in c36_surfaces:
        findings.extend(check_c36_backtick_filepath(surface, vault_index))
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        if args.fix:
            fix_log = apply_placement_fixes(backlog_file, entries, today)
            if fix_log:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in fix_log)
                # apply_placement_fixes moves rows between H2 sections, which
                # shifts source-line numbers. Re-parse before apply_c23_fix so
                # its in-memory line indices match the on-disk file.
                entries = backlog_entries(backlog_file, vault_index)
            c23_changed, c23_log = apply_c23_fix(backlog_file, entries)
            if c23_changed:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in c23_log)
                # C23 fix rewrites brackets, so re-parse before C24 sees them.
                entries = backlog_entries(backlog_file, vault_index)
            c24_changed, c24_log = apply_c24_fix(backlog_file, entries)
            if c24_changed:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in c24_log)
    # B16 — apply mechanical fixes for C6 + C10 if --fix
    c6_fixes_applied: list[str] = []
    c10_fixes_applied: list[str] = []
    c36_fixes_applied: list[str] = []
    if args.fix:
        c6_fixes_applied = apply_c6_fix(all_q_entries)
        c10_fixes_applied = apply_c10_fix(all_q_entries)
        # F126 C36 — replace backtick file-paths with links on each surface
        for surface in c36_surfaces:
            n = apply_c36_fix(surface, findings, vault_index)
            if n:
                try:
                    rel = surface.relative_to(VAULT_ROOT)
                except ValueError:
                    rel = surface
                c36_fixes_applied.append(f"  {rel}: {n} replacement(s)")
    # QFix routing — file every non-mechanically-fixable residual on the
    # owning anchor's `B-QFix [Ready]` row. Per audit § Governing principle
    # (2026-06-04): every check has an agent-side fix path; routing puts the
    # residual where the owning Pilot's next /triage or /groom will see it
    # and drive it to zero under the 100%-fix rule.
    qfix_routing_log: list[str] = []
    if args.fix:
        qfix_routing_log = route_findings_to_qfix(findings, anchor_backlogs)
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
    if c36_fixes_applied:
        print(f"\naudit-q: C36 backtick file-paths replaced with links:")
        for line in c36_fixes_applied:
            print(line)
    if f089_fixes_applied:
        print(f"\naudit-q: F089 placement fixes (C15/C16/C18 auto-moves):")
        for line in f089_fixes_applied:
            print(line)
    if qfix_routing_log:
        print(f"\naudit-q: QFix routing — non-mechanically-fixable residuals "
              f"filed on owning anchors' B-QFix rows (per 100%-fix discipline):")
        for line in qfix_routing_log:
            print(line)
    print(f"\naudit-q: derived banners for {len(derived_banners)} anchors")
    if args.fix and not args.dry and args.scope in ("q", "all", "backlog"):
        # D1: write derived banners back to Q.md (replace H1 lines for each
        # existing per-anchor section). Runs for backlog scope too so per-anchor
        # invocations (`--scope backlog --anchor X --fix` from backlog-edit.py)
        # actually update the Q.md banner.
        d1_changes = apply_d1_banner_write(Q_MD, derived_banners)
        if d1_changes:
            print(f"\naudit-q: D1 — {d1_changes} per-anchor section(s) regenerated in Q.md (via triage-section.py)")
    # Hard-continuation directive — print whenever ANY anchor has Ready > 0.
    # Per user direction 2026-05-26 — the agent reads audit-q's output at the
    # moment they're tempted to stop; embedding the rule into that output is
    # the structural defense against lazy stops ("loop exited cleanly" with
    # Ready > 0). Phrase-patching the chat-summary loses to paraphrases;
    # status-line embedding doesn't, because it IS the status the agent reads.
    _print_hard_continuation_directive(derived_banners)
    return 1 if errors else 0


# Regex to extract Ready N and Questions N counts from a derived banner line.
_BANNER_COUNTS_RE = re.compile(
    r"Ready\s+(\d+).*?Questions\s+(\d+)"
)


def _print_hard_continuation_directive(derived_banners: dict[str, str]) -> None:
    """When any anchor has Ready > 0, surface the crank hard-rule to the
    agent in audit-q's stderr-style output. The directive cites the rule's
    home, names the failure mode by name, and lists the exit requirement
    (3-gate argument). Silent when every anchor is at Ready 0."""
    actionable: list[tuple[str, int, int]] = []  # (name, ready_n, questions_n)
    for name, banner in derived_banners.items():
        m = _BANNER_COUNTS_RE.search(banner)
        if not m:
            continue
        ready_n = int(m.group(1))
        questions_n = int(m.group(2))
        if ready_n > 0:
            actionable.append((name, ready_n, questions_n))
    if not actionable:
        return
    print()
    print("Agent requirement:  (skills/crank/SKILL.md § Hard continuation rule)")
    print("  Anchors with Ready > 0 — you MUST continue while context > 40%:")
    for name, r, q in sorted(actionable):
        print(f"    - {name}: Ready {r}, Questions {q}")
    print(
        "  To stop, print the 3-gate exit argument in chat:\n"
        "    Gate 1 (uncertain): I'd be guessing from <specific info gap>.\n"
        "    Gate 2 (high downside): wrong choice would <concrete consequence>.\n"
        "    Gate 3 (continuing IS the risk): the specific bad outcome of\n"
        "      continuing is <which file gets corrupted / which interface gets\n"
        "      locked in / which downstream commit becomes load-bearing on a\n"
        "      wrong choice>. Cost of stopping < that risk because <one sentence>.\n"
        "  If you can't fill any blank with concrete content, the rule's\n"
        "  diagnosis is: CONTINUE. 'Loop exited cleanly' / 'natural pause' /\n"
        "  'handoff to user' with Ready > 0 are spec violations — they look\n"
        "  like exit messages but don't satisfy Gate 3.")


def apply_d1_banner_write(qmd_file: Path, derived_banners: dict[str, str]) -> int:
    """Regenerate the per-anchor section in Q.md for each anchor with a derived
    banner — delegates the actual write to `triage-section.py {NAME}` (per F104).

    Each subprocess call rewrites the entire per-anchor section (banner + body
    H2s + bullets) and bubbles it to the top of Q.md. Returns the count of
    sections rewritten.

    Falls back to in-process banner-only rewrite if triage-section.py is
    unreachable — preserves the original D1 behavior so audit-q can still fix
    banner-only drift even if the new script went missing."""
    import subprocess
    triage_script = (Path.home() / ".claude" / "skills" / "triage"
                     / "scripts" / "triage-section.py")
    if not triage_script.is_file():
        # Fallback — original banner-only rewrite (preserves pre-F104 behavior)
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
    rewrites = 0
    for name in derived_banners.keys():
        result = subprocess.run(
            ["python3", str(triage_script), name],
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0:
            rewrites += 1
    return rewrites


if __name__ == "__main__":
    sys.exit(main())
