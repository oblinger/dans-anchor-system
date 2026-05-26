#!/usr/bin/env python3
"""audit-architecture.py — Architecture doc shape + link-integrity validator (F092).

Two rules over the vault's Architecture docs, reachable from each anchor's
main `<NAME> Architecture.md`:

  A1: every reachable Arch doc has a block diagram within the first 30 lines
      after H1. Mermaid code fence OR image embed (svg/png/excalidraw).
  A2: the block diagram is followed within 5 lines by a markdown table.
  A3: every cell in that component table that names a vault file (basename
      match) is a wiki-link `[[X]]`, not plain text. Auto-fix wraps the
      unambiguous matches; ambiguous matches (multi-anchor basenames) are
      report-only. Cells tagged `[ext: <name>]` opt out of the check.
  A4: an Arch doc has EITHER a diagram OR a table but not both in order —
      one half of the shape contract is missing.

Reuses audit-q.py primitives (build_vault_index, links_in_file, headings_in)
via Python import. CLI is shaped like audit-q.py:

  audit-architecture [--scope reach|anchor|file|all] [--anchor NAME]
                     [--file PATH] [--fix] [--dry]

Default --scope reach walks each anchor's main Arch doc → transitively
linked Arch docs (basename matches `<X> Architecture` or `<X> Arch`).
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ============================================================
# Import audit-q.py as a module to reuse its primitives.
# ============================================================

_AUDIT_Q_PATH = Path(__file__).parent / "audit-q.py"


def _load_audit_q():
    """Load audit-q.py as a Python module (its filename has a hyphen so we
    can't `import audit-q`; use importlib instead). audit-q.py registers
    itself in sys.modules so its @dataclass declarations work."""
    spec = importlib.util.spec_from_file_location("audit_q", _AUDIT_Q_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load audit-q.py from {_AUDIT_Q_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_q"] = mod
    spec.loader.exec_module(mod)
    return mod


_aq = _load_audit_q()
VAULT_ROOT: Path = _aq.VAULT_ROOT
build_vault_index = _aq.build_vault_index
links_in_file = _aq.links_in_file
headings_in = _aq.headings_in


# ============================================================
# Dataclasses
# ============================================================


@dataclass
class Finding:
    severity: str   # 'error' or 'warning'
    surface_file: Path
    surface_line: int
    code: str       # 'A1' / 'A2' / 'A3' / 'A4'
    message: str
    mechanically_fixable: bool = False


# ============================================================
# Reachability — find Arch docs starting from each anchor's main Arch doc
# ============================================================

# Matches stems like `SKA Architecture`, `MUX Frontend Arch`, `HA Interface Arch`,
# `<NAME> Architecture`. Excludes versioned snapshots inside Versions/ folders
# (those mirror the spec but aren't live-audit targets).
ARCH_STEM_RE = re.compile(r"^(.+?)\s+(?:Architecture|Arch)$")

# Path segments that mark a file as out-of-scope for the live-audit:
# - Versions/ — `/architect`-managed snapshot archive of an Arch doc
# - .history/ — md_history watcher's daily backup snapshots (B15)
# - worktrees/ — Claude Code agent worktrees (transient working copies)
# - .anchor.d/ — HA's internal cache
# - .build/, .cache/, target/, node_modules/ — build artifacts
_OUT_OF_SCOPE_SEGMENTS = frozenset([
    "Versions", ".history", "worktrees", ".anchor.d",
    ".build", ".cache", "target", "node_modules",
])


def is_in_scope(path: Path) -> bool:
    """True if `path` is a live-audit target (not in a snapshot/backup tree)."""
    return not (_OUT_OF_SCOPE_SEGMENTS & set(path.parts))


def is_arch_doc_basename(basename: str) -> bool:
    """True if `basename` (filename without `.md` extension) matches the
    Arch-doc pattern: `<X> Architecture` or `<X> Arch`."""
    return ARCH_STEM_RE.match(basename) is not None


def find_main_arch_docs(vault_index: dict[str, list[Path]]) -> list[Path]:
    """Return the list of main `<NAME> Architecture.md` files in the vault.

    Main = the Architecture doc that lives at the top of an anchor (i.e., one
    level under the anchor's User/ or Docs/ folder, not nested in a per-
    subsystem Architecture/ folder). Detected heuristically: stem matches
    `<NAME> Architecture` AND path does NOT include a `Versions/` segment.
    """
    mains: list[Path] = []
    for basename, paths in vault_index.items():
        if not basename.endswith(" Architecture"):
            continue
        for p in paths:
            if not is_in_scope(p):
                continue
            mains.append(p)
    # Deterministic ordering for stable reports.
    return sorted(mains)


def walk_reachable_arch_docs(
    start: Path,
    vault_index: dict[str, list[Path]],
) -> list[Path]:
    """Walk wiki-links from `start` (a main Arch doc) to every other Arch doc
    reachable transitively. Returns the closure including `start` itself,
    ordered by discovery (BFS)."""
    seen: dict[Path, None] = {}  # ordered set
    queue: list[Path] = [start]
    while queue:
        cur = queue.pop(0)
        if cur in seen or not cur.is_file():
            continue
        seen[cur] = None
        for link in links_in_file(cur, vault_index):
            if not link.target_resolves:
                continue
            tgt = link.target_file_path
            if tgt is None:
                continue
            if not is_arch_doc_basename(tgt.stem):
                continue
            if not is_in_scope(tgt):
                continue
            if tgt not in seen:
                queue.append(tgt)
    return list(seen.keys())


# ============================================================
# Diagram + table detection
# ============================================================

MERMAID_FENCE_OPEN_RE = re.compile(r"^\s*```\s*mermaid\s*$", re.IGNORECASE)
# Wiki-link image embed: `![[name.svg]]`, `![[name.png]]`, etc.
IMAGE_WIKI_EMBED_RE = re.compile(
    r"!\[\[[^\]]+\.(?:svg|png|jpe?g|gif|webp|excalidraw|drawio)\]\]",
    re.IGNORECASE,
)
# Markdown image link: `![alt text](path.svg)`. URL-encoded paths and external
# image URLs both count (the diagram is still embedded as an image).
IMAGE_MD_RE = re.compile(
    r"!\[[^\]]*\]\([^)]+?\.(?:svg|png|jpe?g|gif|webp|excalidraw|drawio)\)",
    re.IGNORECASE,
)


def is_image_embed_line(line: str) -> bool:
    """True if `line` contains an image embed in either form (wiki-link or
    markdown image syntax)."""
    return bool(IMAGE_WIKI_EMBED_RE.search(line) or IMAGE_MD_RE.search(line))
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]+.*\|?\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
H1_RE = re.compile(r"^# .+$")
FRONTMATTER_DELIM = "---"

DIAGRAM_WINDOW = 30   # lines after H1 where diagram must appear (A1)
TABLE_WINDOW = 5      # lines after diagram-end where table must start (A2)


@dataclass
class DiagramHit:
    kind: str        # 'mermaid' or 'image'
    start_line: int  # 1-indexed
    end_line: int    # 1-indexed; inclusive


@dataclass
class TableHit:
    start_line: int  # 1-indexed (header row)
    end_line: int    # 1-indexed (last row); inclusive


def _h1_line(lines: list[str]) -> Optional[int]:
    """Return 1-indexed line of the first H1, skipping YAML frontmatter."""
    i = 0
    if lines and lines[0].strip() == FRONTMATTER_DELIM:
        i = 1
        while i < len(lines) and lines[i].strip() != FRONTMATTER_DELIM:
            i += 1
        i += 1  # past the closing ---
    while i < len(lines):
        if H1_RE.match(lines[i]):
            return i + 1
        i += 1
    return None


def find_diagram(lines: list[str], h1_line: int) -> Optional[DiagramHit]:
    """Search for a block diagram in the first DIAGRAM_WINDOW lines after
    the H1 (exclusive). Returns the diagram's start/end lines, or None."""
    start_idx = h1_line  # 1-indexed line AFTER H1
    end_idx = min(start_idx + DIAGRAM_WINDOW, len(lines))
    i = start_idx
    while i < end_idx:
        line = lines[i]
        if MERMAID_FENCE_OPEN_RE.match(line):
            # Walk to closing fence.
            j = i + 1
            while j < len(lines) and not re.match(r"^\s*```\s*$", lines[j]):
                j += 1
            return DiagramHit(kind="mermaid", start_line=i + 1, end_line=j + 1)
        if is_image_embed_line(line):
            return DiagramHit(kind="image", start_line=i + 1, end_line=i + 1)
        i += 1
    return None


def find_table_after(lines: list[str], after_line: int) -> Optional[TableHit]:
    """Search for a markdown table starting within TABLE_WINDOW lines after
    `after_line` (1-indexed). A table = header row + separator row + ≥1 data
    row. Returns start/end lines or None."""
    start_idx = after_line  # search starts AT line after_line+1 (0-indexed: after_line)
    end_idx = min(start_idx + TABLE_WINDOW, len(lines))
    i = start_idx
    while i < end_idx:
        line = lines[i]
        # Skip blank lines.
        if not line.strip():
            i += 1
            continue
        # Need: header row (i) + separator row (i+1) + data row (i+2).
        if TABLE_ROW_RE.match(line):
            if i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
                # Find end of table.
                j = i + 2
                while j < len(lines) and TABLE_ROW_RE.match(lines[j]):
                    j += 1
                if j > i + 2:  # at least one data row
                    return TableHit(start_line=i + 1, end_line=j)
        # Non-blank, non-table line in the window — table-not-found.
        break
    return None


# ============================================================
# Wiki-link integrity in table cells
# ============================================================

WIKI_LINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
EXT_TAG_RE = re.compile(r"\[ext:\s*([^\]]+)\]")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def split_table_row(row: str) -> list[str]:
    """Split a `| a | b | c |` row into cells. Returns trimmed cell texts."""
    # Strip leading/trailing pipes + whitespace.
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _strip_links_and_code(cell: str) -> str:
    """Remove `[[wiki-links]]`, `[ext: ...]` tags, and `` `code spans` ``
    from a cell so what remains is the prose-only fragment to scan for
    plain-text basenames."""
    s = WIKI_LINK_RE.sub(" ", cell)
    s = EXT_TAG_RE.sub(" ", s)
    s = INLINE_CODE_RE.sub(" ", s)
    return s


# Token characters allowed in vault basenames: letters, digits, space,
# hyphen, underscore. Punctuation (commas, parens, slashes, em-dashes)
# terminates a token.
TOKEN_BREAK_RE = re.compile(r"[^A-Za-z0-9 _\-]+")


def find_plain_text_basenames(
    cell: str,
    vault_index: dict[str, list[Path]],
) -> list[tuple[str, bool]]:
    """In a table cell, find substrings that match a vault basename exactly
    AND aren't already wiki-linked, code-spanned, or marked `[ext: ...]`.

    Returns list of (basename, ambiguous) tuples where `ambiguous` is True
    when the basename matches >1 file in the vault (auto-fix not safe)."""
    cleaned = _strip_links_and_code(cell)
    # Split into candidate phrases at punctuation boundaries.
    phrases = [p.strip() for p in TOKEN_BREAK_RE.split(cleaned) if p.strip()]
    hits: list[tuple[str, bool]] = []
    seen: set[str] = set()
    # For each phrase, try the whole phrase as a basename. Also try ascending
    # multi-word prefixes (e.g., "SKA Triage subsystem" → try "SKA Triage",
    # then "SKA").  Prefer the longest match.
    for phrase in phrases:
        words = phrase.split()
        if not words:
            continue
        matched = False
        # Longest-prefix-first lookup.
        for n in range(len(words), 0, -1):
            candidate = " ".join(words[:n])
            if candidate in vault_index:
                if candidate not in seen:
                    seen.add(candidate)
                    ambiguous = len(vault_index[candidate]) > 1
                    hits.append((candidate, ambiguous))
                matched = True
                break
        # Single-word fall-through already handled by n=1 in loop above.
        # If no prefix matched, skip; tokens that aren't basenames are fine.
        _ = matched
    return hits


# ============================================================
# Audit one Arch doc
# ============================================================


@dataclass
class A3Edit:
    """A pending wrap-basename-in-brackets edit on a specific line."""
    file: Path
    line_num: int      # 1-indexed
    basename: str


def audit_arch_doc(
    file_path: Path,
    vault_index: dict[str, list[Path]],
) -> tuple[list[Finding], list[A3Edit]]:
    """Run A1-A4 against one Arch doc. Returns (findings, edits)."""
    findings: list[Finding] = []
    edits: list[A3Edit] = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        findings.append(Finding(
            severity="error",
            surface_file=file_path,
            surface_line=0,
            code="A1",
            message=f"could not read: {e}",
        ))
        return findings, edits
    lines = text.splitlines()
    h1 = _h1_line(lines)
    if h1 is None:
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=1,
            code="A1",
            message="no H1 found — cannot evaluate diagram-at-top rule",
        ))
        return findings, edits
    diagram = find_diagram(lines, h1)
    if diagram is None:
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=h1,
            code="A1",
            message=(
                f"no block diagram in the first {DIAGRAM_WINDOW} lines after "
                f"H1 (expected ```mermaid``` fence or `![[X.svg]]`/`.png`/"
                f"`.excalidraw` image embed)"
            ),
        ))
        # Without a diagram, A2 can't reach a verdict — A4 covers the shape gap.
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=h1,
            code="A4",
            message="diagram+table shape contract broken: no diagram → no table either",
        ))
        return findings, edits
    table = find_table_after(lines, diagram.end_line)
    if table is None:
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=diagram.end_line,
            code="A2",
            message=(
                f"no markdown table within {TABLE_WINDOW} lines after the "
                f"diagram (expected component table immediately after)"
            ),
        ))
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=diagram.end_line,
            code="A4",
            message="diagram+table shape contract broken: diagram present but no table",
        ))
        return findings, edits
    # A3: wiki-link integrity in the table.
    for line_num in range(table.start_line, table.end_line + 1):
        line = lines[line_num - 1]
        if TABLE_SEP_RE.match(line):
            continue  # separator row
        for cell in split_table_row(line):
            for basename, ambiguous in find_plain_text_basenames(cell, vault_index):
                if ambiguous:
                    findings.append(Finding(
                        severity="warning",
                        surface_file=file_path,
                        surface_line=line_num,
                        code="A3",
                        message=(
                            f"plain-text basename '{basename}' in component table "
                            f"matches multiple vault files — wrap in `[[...]]` "
                            f"with the disambiguating path (auto-fix unsafe)"
                        ),
                        mechanically_fixable=False,
                    ))
                else:
                    findings.append(Finding(
                        severity="warning",
                        surface_file=file_path,
                        surface_line=line_num,
                        code="A3",
                        message=(
                            f"plain-text basename '{basename}' in component "
                            f"table should be `[[{basename}]]`"
                        ),
                        mechanically_fixable=True,
                    ))
                    edits.append(A3Edit(
                        file=file_path, line_num=line_num, basename=basename,
                    ))
    return findings, edits


# ============================================================
# Apply A3 auto-fixes
# ============================================================


def apply_a3_edits(edits: list[A3Edit]) -> dict[Path, int]:
    """Apply A3 wrap-in-brackets edits, grouped by file. Returns dict of
    file → edits-applied count.

    Per-file: read once, apply all edits, write once. Edits are line-scoped;
    within a line, replace each unwrapped basename occurrence with the
    bracketed form using a precise regex (negative lookbehind for `[[` and
    negative lookahead for `]]` already inside).
    """
    counts: dict[Path, int] = {}
    by_file: dict[Path, list[A3Edit]] = {}
    for e in edits:
        by_file.setdefault(e.file, []).append(e)
    for file_path, file_edits in by_file.items():
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        # De-dup by (line, basename) pair — a basename can be flagged once
        # per cell, but we wrap line-by-line.
        seen: set[tuple[int, str]] = set()
        applied = 0
        for e in file_edits:
            key = (e.line_num, e.basename)
            if key in seen:
                continue
            seen.add(key)
            idx = e.line_num - 1
            if idx < 0 or idx >= len(lines):
                continue
            line = lines[idx]
            # Wrap occurrences not already inside `[[...]]` or `[ext: ...]`.
            new_line = _wrap_basename_on_line(line, e.basename)
            if new_line != line:
                lines[idx] = new_line
                applied += 1
        if applied:
            file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            counts[file_path] = applied
    return counts


def _wrap_basename_on_line(line: str, basename: str) -> str:
    """Replace each occurrence of `basename` in `line` with `[[basename]]`,
    skipping occurrences already inside `[[...]]` or `[ext: ...]` and code
    spans. Basename match is whole-word + case-sensitive."""
    # Mask out spans we shouldn't touch.
    mask = [False] * len(line)
    for m in WIKI_LINK_RE.finditer(line):
        for k in range(m.start(), m.end()):
            mask[k] = True
    for m in EXT_TAG_RE.finditer(line):
        for k in range(m.start(), m.end()):
            mask[k] = True
    for m in INLINE_CODE_RE.finditer(line):
        for k in range(m.start(), m.end()):
            mask[k] = True
    # Walk line, find occurrences of basename at word boundaries outside mask.
    pat = re.compile(r"(?<![A-Za-z0-9_\-])" + re.escape(basename) +
                     r"(?![A-Za-z0-9_\-])")
    out: list[str] = []
    pos = 0
    for m in pat.finditer(line):
        # Is the match entirely outside the mask?
        if any(mask[k] for k in range(m.start(), m.end())):
            continue
        out.append(line[pos:m.start()])
        out.append(f"[[{basename}]]")
        pos = m.end()
    if pos == 0:
        return line  # no replacement
    out.append(line[pos:])
    return "".join(out)


# ============================================================
# Main
# ============================================================


def collect_targets(
    args: argparse.Namespace,
    vault_index: dict[str, list[Path]],
) -> list[Path]:
    """Resolve --scope into a concrete list of Arch doc paths to audit."""
    if args.scope == "file":
        p = Path(args.file).expanduser().resolve()
        if not p.is_file():
            print(f"error: --file not found: {p}", file=sys.stderr)
            sys.exit(2)
        return [p]
    if args.scope == "anchor":
        # Find the anchor's main Arch doc: `<NAME> Architecture.md`.
        anchor = args.anchor
        bn = f"{anchor} Architecture"
        if bn not in vault_index:
            print(f"error: '{bn}.md' not in vault", file=sys.stderr)
            sys.exit(2)
        candidates = [p for p in vault_index[bn] if is_in_scope(p)]
        if not candidates:
            print(f"error: no live `{bn}.md` (all matches under Versions/)",
                  file=sys.stderr)
            sys.exit(2)
        if len(candidates) > 1:
            print(f"warning: multiple `{bn}.md` matches, using first: "
                  f"{candidates[0]}", file=sys.stderr)
        return walk_reachable_arch_docs(candidates[0], vault_index)
    if args.scope == "all":
        # Every Arch-stem file in the vault, not just reachable ones.
        out: list[Path] = []
        for bn, paths in vault_index.items():
            if not is_arch_doc_basename(bn):
                continue
            for p in paths:
                if not is_in_scope(p):
                    continue
                out.append(p)
        return sorted(out)
    # Default scope=reach: every main Arch doc + transitive reach.
    out_seen: dict[Path, None] = {}
    for main in find_main_arch_docs(vault_index):
        for p in walk_reachable_arch_docs(main, vault_index):
            out_seen[p] = None
    return list(out_seen.keys())


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n")[0]
    )
    parser.add_argument(
        "--scope",
        choices=["reach", "anchor", "file", "all"],
        default="reach",
        help=(
            "Audit scope. Default `reach`: every anchor's main "
            "`<NAME> Architecture.md` + transitive Arch docs via wiki-links. "
            "`anchor` requires --anchor NAME. `file` requires --file PATH. "
            "`all` audits every Arch-stem file in the vault (unreachable too)."
        ),
    )
    parser.add_argument("--anchor", type=str, default=None,
                        help="(scope=anchor) anchor name, e.g., 'SKA'")
    parser.add_argument("--file", type=str, default=None,
                        help="(scope=file) path to an Arch doc")
    parser.add_argument("--fix", action="store_true",
                        help="apply mechanical wraps (A3 auto-fixes)")
    parser.add_argument("--dry", action="store_true",
                        help="report-only AND refuse to write")
    args = parser.parse_args()
    if args.scope == "anchor" and not args.anchor:
        print("error: --scope anchor requires --anchor NAME", file=sys.stderr)
        return 2
    if args.scope == "file" and not args.file:
        print("error: --scope file requires --file PATH", file=sys.stderr)
        return 2
    if args.fix and args.dry:
        print("error: --fix and --dry are mutually exclusive", file=sys.stderr)
        return 2
    print(f"audit-architecture: building vault index from {VAULT_ROOT}...",
          file=sys.stderr)
    vault_index = build_vault_index(VAULT_ROOT)
    print(f"  vault index: {sum(len(v) for v in vault_index.values())} files, "
          f"{len(vault_index)} unique basenames", file=sys.stderr)
    targets = collect_targets(args, vault_index)
    print(f"audit-architecture: {len(targets)} Arch doc(s) in scope "
          f"({args.scope})", file=sys.stderr)
    all_findings: list[Finding] = []
    all_edits: list[A3Edit] = []
    for fp in targets:
        findings, edits = audit_arch_doc(fp, vault_index)
        all_findings.extend(findings)
        all_edits.extend(edits)
    # Print findings.
    errors = [f for f in all_findings if f.severity == "error"]
    warnings = [f for f in all_findings if f.severity == "warning"]
    for f in all_findings:
        rel = f.surface_file.relative_to(VAULT_ROOT) if (
            f.surface_file.is_absolute() and VAULT_ROOT in f.surface_file.parents
        ) else f.surface_file
        print(f"  [{f.severity}] {f.code} {rel}:{f.surface_line} — {f.message}")
    print(f"\naudit-architecture: {len(all_findings)} findings "
          f"({len(errors)} errors, {len(warnings)} warnings)")
    # Apply --fix.
    if args.fix and all_edits:
        counts = apply_a3_edits(all_edits)
        if counts:
            print(f"\naudit-architecture: A3 auto-fixes applied:")
            for fp, n in counts.items():
                rel = fp.relative_to(VAULT_ROOT) if (
                    fp.is_absolute() and VAULT_ROOT in fp.parents
                ) else fp
                print(f"  {rel}: {n} basename(s) wrapped in [[...]]")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
