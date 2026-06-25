#!/usr/bin/env python3
"""audit-roadmap.py — Roadmap constraint validator (F145).

Enforces the three named-milestone-era rules introduced by F144 and codified
in [[FCT Roadmap]] / [[FCT Completed Roadmap]]:

  R09: top-level milestones use named form `M-<Name>` (not pure-numbered M1/M2).
       Pure-numbered roadmaps are accepted only if the file carries the marker
       comment `<!-- legacy-numbered-milestones -->`.
  R10: feature docs commissioned from a roadmap milestone encode the M-position
       in their title: `F<NNN> — M-<Name>.<position>: <Title>`. Also: every
       roadmap sub-item carrying a `[F<NNN>]` marker resolves to a feature doc.
  R11: future-only invariant — a roadmap should not accumulate `[x]`-complete
       top-level milestones; they migrate to the Completed Roadmap. At most one
       or two awaiting-migration `[x]` milestones are tolerated.

Reuses the audit-q primitives (build_vault_index / links_in_file / headings_in)
via importlib, mirroring the house style of the other audit sub-scripts.

Usage:
  audit-roadmap                          # vault-wide: every `* Roadmap.md`
  audit-roadmap --anchor SKA             # one anchor's roadmap (by slug)
  audit-roadmap --file PATH              # one specific roadmap file
  audit-roadmap --dry                    # report-only (default; never writes)

Exit code: 1 if any error-severity finding, else 0. Report-only — audit-roadmap
never mutates files (fixing is downstream work, per the audit governing
principle). Milestone migration / checkbox flips live in `state roadmap`.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ============================================================
# Reuse audit-q primitives via importlib (house style)
# ============================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
_AQ_PATH = _SCRIPT_DIR / "audit-q.py"
_spec = importlib.util.spec_from_file_location("audit_q", _AQ_PATH)
if _spec is None or _spec.loader is None:
    print(f"audit-roadmap: cannot load {_AQ_PATH}", file=sys.stderr)
    sys.exit(2)
aq = importlib.util.module_from_spec(_spec)
sys.modules["audit_q"] = aq
_spec.loader.exec_module(aq)

VAULT_ROOT = aq.VAULT_ROOT
EXCLUDED_PATH_FRAGMENTS = aq.EXCLUDED_PATH_FRAGMENTS

# ============================================================
# Regexes
# ============================================================

# A milestone heading: `## [x] M-Store — Persistence Layer` (H2) or
# `### [ ] M-Store.1 — SQLite schema  [F050]` (H3 sub-point). Captures the
# checkbox char, the milestone identifier, and the trailing text.
MILESTONE_HEADING_RE = re.compile(
    r"^(?P<hashes>#{1,3})\s+"
    r"\[(?P<box>[ x~])\]\s+"
    r"(?P<ident>M[-\w.]*)"          # M-Store, M-Store.1, M1, M1.8a, …
    r"(?P<rest>.*)$"
)
# Named-milestone form for the *top-level* identifier (before any dot):
#   M-<Name> where Name is alnum, >= 2 chars after the leading letter,
#   then optional dotted/hyphenated sub-positions.
NAMED_MILESTONE_RE = re.compile(
    r"^M-[A-Za-z][A-Za-z0-9]{1,}(\.[0-9]+)*(-\w+)?$"
)
# Pure-numbered legacy form: M1, M2.3, M1.8a, M1.8a.1, M1.8-tests
LEGACY_NUMBERED_RE = re.compile(r"^M\d")
# Legacy-roadmap escape-hatch marker comment.
LEGACY_MARKER_RE = re.compile(r"<!--\s*legacy-numbered-milestones\s*-->")
# `[F123]` marker on a roadmap sub-item (the pointer to its feature doc).
F_MARKER_RE = re.compile(r"\[F(\d+)\]")
# Feature-doc filename that encodes an M-position (R10 title format).
FEATURE_MPOS_FILENAME_RE = re.compile(
    r"^F\d+\s+—\s+M-[A-Za-z][A-Za-z0-9]+(\.\d+)*:\s+.+$"
)
# Any `F<NNN> — M-` filename prefix (used to detect the encode-attempt).
FEATURE_MPOS_PREFIX_RE = re.compile(r"^F\d+\s+—\s+M-")


# ============================================================
# Finding
# ============================================================


@dataclass
class Finding:
    severity: str  # 'error' or 'warning'
    surface_file: Path
    surface_line: int
    code: str      # 'R09' / 'R10' / 'R11'
    message: str


# ============================================================
# Roadmap discovery
# ============================================================


def find_roadmaps(vault_root: Path) -> list[Path]:
    """Every `* Roadmap.md` (excluding `* Completed Roadmap.md`) under vault."""
    out: list[Path] = []
    for path in vault_root.rglob("* Roadmap.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        if path.name.endswith("Completed Roadmap.md"):
            continue
        out.append(path)
    return out


def _feature_dirs_for(roadmap_path: Path) -> list[Path]:
    """Candidate `{NAME} Features/` dirs for a roadmap at `{NAME} Design/`.

    Roadmap lives at `{NAME} Design/{NAME} Roadmap.md`; feature docs live in
    `{NAME} Design/{NAME} Features/` (new canonical) or legacy siblings. We
    derive the slug from the roadmap stem (`SKA Roadmap` → `SKA`).
    """
    stem = roadmap_path.stem  # e.g. "SKA Roadmap"
    slug = stem[: -len(" Roadmap")] if stem.endswith(" Roadmap") else stem
    design_dir = roadmap_path.parent             # {NAME} Design/
    anchor_root = design_dir.parent
    return [
        design_dir / f"{slug} Features",
        anchor_root / f"{slug} Track" / f"{slug} Features",
        anchor_root / f"{slug} Features",
    ]


# ============================================================
# Parsing — milestones in a roadmap
# ============================================================


@dataclass
class Milestone:
    line: int            # 1-indexed heading line
    level: int           # 1, 2, or 3
    box: str             # ' ', 'x', or '~'
    ident: str           # 'M-Store', 'M-Store.1', 'M1', …
    f_markers: list[int]  # F-numbers referenced via [F123] on the heading line


def parse_milestones(text: str) -> list[Milestone]:
    """Parse every milestone heading (H1/H2/H3 carrying a checkbox)."""
    out: list[Milestone] = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = MILESTONE_HEADING_RE.match(line)
        if not m:
            continue
        f_markers = [int(g) for g in F_MARKER_RE.findall(m.group("rest"))]
        out.append(Milestone(
            line=i,
            level=len(m.group("hashes")),
            box=m.group("box"),
            ident=m.group("ident"),
            f_markers=f_markers,
        ))
    return out


def _top_level_ident(ident: str) -> str:
    """The top-level milestone id (before the first dot): 'M-Store.1' → 'M-Store'."""
    return ident.split(".", 1)[0]


# ============================================================
# R09 — named-milestone convention
# ============================================================


def check_r09(roadmap_path: Path, text: str,
              milestones: list[Milestone]) -> list[Finding]:
    """Top-level milestones must use `M-<Name>` named form unless the file
    carries the `<!-- legacy-numbered-milestones -->` escape marker."""
    findings: list[Finding] = []
    legacy_ok = LEGACY_MARKER_RE.search(text) is not None
    seen_top: set[str] = set()
    for ms in milestones:
        top = _top_level_ident(ms.ident)
        if top in seen_top:
            continue
        seen_top.add(top)
        if NAMED_MILESTONE_RE.match(ms.ident):
            continue
        if LEGACY_NUMBERED_RE.match(ms.ident):
            if legacy_ok:
                continue
            findings.append(Finding(
                severity="error",
                surface_file=roadmap_path,
                surface_line=ms.line,
                code="R09",
                message=(
                    f"milestone '{ms.ident}' uses legacy pure-numbered form; "
                    f"new roadmaps use named `M-<Name>` (or add a "
                    f"`<!-- legacy-numbered-milestones -->` marker to opt out)"
                ),
            ))
            continue
        # Neither named nor recognizably legacy — malformed identifier.
        findings.append(Finding(
            severity="error",
            surface_file=roadmap_path,
            surface_line=ms.line,
            code="R09",
            message=(
                f"milestone '{ms.ident}' is not a valid `M-<Name>` identifier "
                f"(expected e.g. M-Auth, M-WAL, M-Core)"
            ),
        ))
    return findings


# ============================================================
# R10 — feature title encodes M-position; [F<n>] markers resolve
# ============================================================


def check_r10(roadmap_path: Path,
              milestones: list[Milestone],
              vault_index: dict) -> list[Finding]:
    """Two halves:

    (a) Every roadmap sub-item with a `[F<NNN>]` marker must resolve to a
        feature doc on disk.
    (b) Any feature doc whose filename starts with `F<NNN> — M-` must match the
        full R10 title format `F<NNN> — M-<Name>.<position>: <Title>`.
    """
    findings: list[Finding] = []
    feature_dirs = [d for d in _feature_dirs_for(roadmap_path) if d.is_dir()]

    # (a) [F<n>] markers resolve to a feature doc. F-numbers are canonically
    # zero-padded triple-digit (F050), so `[F50]`, `[F050]`, and `[F0050]`
    # should all resolve to a `F050 — *.md`. Match on the integer value,
    # ignoring leading zeros on both the marker and the filename.
    def _feature_doc_exists(fnum: int) -> bool:
        pad = re.compile(rf"^F0*{fnum} — ")
        for stem in vault_index:
            if pad.match(stem):
                return True
        for d in feature_dirs:
            for fpath in d.glob("F*.md"):
                if pad.match(fpath.stem):
                    return True
        return False

    for ms in milestones:
        for fnum in ms.f_markers:
            if not _feature_doc_exists(fnum):
                findings.append(Finding(
                    severity="warning",
                    surface_file=roadmap_path,
                    surface_line=ms.line,
                    code="R10",
                    message=(
                        f"sub-item marker [F{fnum:03d}] has no matching feature "
                        f"doc ('F{fnum:03d} — *.md' not found in vault or Features/)"
                    ),
                ))

    # (b) Feature docs that attempt the M-position encoding must be well-formed.
    for d in feature_dirs:
        for fpath in sorted(d.glob("F*.md")):
            stem = fpath.stem
            if FEATURE_MPOS_PREFIX_RE.match(stem) and not \
                    FEATURE_MPOS_FILENAME_RE.match(stem):
                findings.append(Finding(
                    severity="warning",
                    surface_file=fpath,
                    surface_line=1,
                    code="R10",
                    message=(
                        f"feature title '{stem}' encodes an M-position but "
                        f"breaks the R10 format "
                        f"`F<NNN> — M-<Name>.<position>: <Title>`"
                    ),
                ))
    return findings


# ============================================================
# R11 — future-only invariant
# ============================================================

# At most this many `[x]` top-level milestones may linger in a roadmap before
# the accumulation is flagged as migration-drift.
R11_AWAITING_MIGRATION_TOLERANCE = 2


def check_r11(roadmap_path: Path,
              milestones: list[Milestone]) -> list[Finding]:
    """A roadmap should be future + present. Completed (`[x]`) top-level
    milestones await migration to the Completed Roadmap; more than a couple
    lingering is drift."""
    findings: list[Finding] = []
    # Only top-level milestones (the migration unit). A top-level milestone is
    # the highest heading level present; collapse by top-level identifier and
    # track whether the *heading that names the top id* is [x].
    top_box: dict[str, tuple[str, int]] = {}  # top-ident → (box, line)
    for ms in milestones:
        top = _top_level_ident(ms.ident)
        if ms.ident == top:  # this heading names the top-level milestone itself
            top_box[top] = (ms.box, ms.line)
    completed = [(t, line) for t, (box, line) in top_box.items() if box == "x"]
    if len(completed) > R11_AWAITING_MIGRATION_TOLERANCE:
        for top, line in completed:
            findings.append(Finding(
                severity="warning",
                surface_file=roadmap_path,
                surface_line=line,
                code="R11",
                message=(
                    f"completed milestone '{top}' [x] lingering in roadmap "
                    f"({len(completed)} complete milestones — exceeds tolerance "
                    f"of {R11_AWAITING_MIGRATION_TOLERANCE}); migrate to "
                    f"Completed Roadmap (`state roadmap migrate {top}`)"
                ),
            ))
    return findings


# ============================================================
# Per-file audit
# ============================================================


def audit_roadmap_file(roadmap_path: Path, vault_index: dict) -> list[Finding]:
    try:
        text = roadmap_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    milestones = parse_milestones(text)
    findings: list[Finding] = []
    findings.extend(check_r09(roadmap_path, text, milestones))
    findings.extend(check_r10(roadmap_path, milestones, vault_index))
    findings.extend(check_r11(roadmap_path, milestones))
    return findings


# ============================================================
# Main + CLI
# ============================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Roadmap constraint validator (R-roadmap-09/10/11)."
    )
    parser.add_argument("--anchor", type=str, default=None,
                        help="audit one anchor's roadmap (by slug, e.g. SKA)")
    parser.add_argument("--file", type=str, default=None,
                        help="audit one specific roadmap file (path)")
    parser.add_argument("--dry", action="store_true",
                        help="report-only (default — audit-roadmap never writes)")
    args = parser.parse_args()

    if args.file:
        targets = [Path(args.file).expanduser().resolve()]
        for t in targets:
            if not t.is_file():
                print(f"error: roadmap file not found: {t}", file=sys.stderr)
                return 2
    elif args.anchor:
        cand = VAULT_ROOT.rglob(f"{args.anchor} Roadmap.md")
        targets = [p for p in cand
                   if not any(f in p.parts for f in EXCLUDED_PATH_FRAGMENTS)
                   and not p.name.endswith("Completed Roadmap.md")]
        if not targets:
            print(f"error: no '{args.anchor} Roadmap.md' under {VAULT_ROOT}",
                  file=sys.stderr)
            return 2
    else:
        targets = find_roadmaps(VAULT_ROOT)

    print(f"audit-roadmap: building vault index from {VAULT_ROOT}...",
          file=sys.stderr)
    vault_index = aq.build_vault_index(VAULT_ROOT)

    findings: list[Finding] = []
    for roadmap_path in targets:
        findings.extend(audit_roadmap_file(roadmap_path, vault_index))

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print(f"\naudit-roadmap: {len(findings)} findings "
          f"({len(errors)} errors, {len(warnings)} warnings) "
          f"across {len(targets)} roadmap(s)", file=sys.stderr)
    for f in findings:
        try:
            rel = f.surface_file.relative_to(VAULT_ROOT)
        except ValueError:
            rel = f.surface_file
        print(f"  [{f.severity}] {f.code} {rel}:{f.surface_line} — {f.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
