#!/usr/bin/env python3
"""spine-check.py — validate a page's spine and heart against [[DAS spine]].

This is F319 M2's detector, brought forward. It reports; it never edits.

Two jobs:
  1. Classify the spine into one of the seven shapes and flag what is wrong with it.
  2. NOMINATE a heart where one looks buried — never move it. Nominating is a
     question a reader can answer; moving is a silent assertion that the guess
     was right, and a wrong move is invisible forever because the page then
     looks migrated. That asymmetry is why the migration script will never
     touch hearts (F319 § The detector nominates a heart; it never moves one).

Usage
  spine-check.py <path> [<path> ...]        check specific files
  spine-check.py --vault                    check the whole vault
  spine-check.py --vault --summary          counts only
  spine-check.py --vault --code S04         only that finding
  spine-check.py --vault --sample 8         print 8 spread-out examples per code,
                                            with context, for eyeballing

Exit status is 0 always: this is a lens, not a gate. It becomes a gate at F319 M5.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VAULT = Path.home() / "ob" / "kmr"
SKIP_DIRS = {".git", ".obsidian", "node_modules", ".trash", "Yore", ".stversions", "__pycache__"}

MARKERS = {"...", "+++", "^^^", "!!!"}
# Rows below the marker are machine-written; nothing here may judge their content.

IDENTITY = re.compile(r"^\s*-\s*\[\[.+?\]\]\s*-\s*$")
BREADCRUMB = re.compile(r"^\s*:>>")
FIGURE = re.compile(r"!\[\[[^\]]+\]\]|<img\s|\.svg\)|\.png\)")
TOC = re.compile(r"^\|\s*(\*\*)?Table of Contents", re.I)


# --------------------------------------------------------------------------
# Cell splitting. MUST be a character scanner, never a regex.
#
# A table cell is delimited by an UNESCAPED '|', but wiki-links inside cells are
# written [[Target\|Display]]. Every regex of the form [^|]* or \[\[([^\]\|#]+?)
# either stops early or captures the trailing backslash. Three separate
# measurements during F308 were wrong for exactly this reason, one of them
# silently skipping 17 files. Test any replacement against [[A\|B]] first.
# --------------------------------------------------------------------------
def split_cells(line: str) -> list[str]:
    out, cur, i = [], "", 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            cur += line[i:i + 2]
            i += 2
            continue
        if c == "|":
            out.append(cur)
            cur = ""
            i += 1
            continue
        cur += c
        i += 1
    out.append(cur)
    return out


def cell(line: str, n: int) -> str:
    cs = split_cells(line)
    return cs[n].strip() if len(cs) > n else ""


class Page:
    """Everything the checks need, parsed once."""

    def __init__(self, path: Path):
        self.path = path
        self.lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
        self.body_start = self._after_frontmatter()
        self.h1 = self._find(lambda l: l.startswith("# "), self.body_start)
        self.breadcrumb = self._find(lambda l: BREADCRUMB.match(l), self.body_start)
        self.table_start = self._find_identity()
        self.table_end = self._table_end()
        self.marker_idx, self.marker = self._find_marker()
        self.fronts_folder = path.parent.name == path.stem
        self.children = self._children()

    def _after_frontmatter(self) -> int:
        if self.lines and self.lines[0].strip() == "---":
            for j in range(1, min(len(self.lines), 80)):
                if self.lines[j].strip() == "---":
                    return j + 1
        return 0

    def _find(self, pred, start=0, stop=None):
        stop = len(self.lines) if stop is None else stop
        for j in range(start, stop):
            if pred(self.lines[j]):
                return j
        return None

    def _find_identity(self):
        for j in range(self.body_start, len(self.lines)):
            l = self.lines[j]
            if l.strip().startswith("|") and IDENTITY.match(cell(l, 1)):
                return j
            if l.startswith("# BRIEF") or l.startswith("# Log"):
                break
        return None

    def _table_end(self):
        if self.table_start is None:
            return None
        j = self.table_start
        while j < len(self.lines) and self.lines[j].strip().startswith("|"):
            j += 1
        return j

    def _find_marker(self):
        if self.table_start is None:
            return None, None
        for j in range(self.table_start + 2, self.table_end):
            c0 = cell(self.lines[j], 1)
            if c0 in MARKERS:
                return j, c0
            if re.fullmatch(r"-{3,}", c0) and not cell(self.lines[j], 2):
                return j, "---"
        return None, None

    def _children(self) -> int:
        if not self.fronts_folder:
            return 0
        try:
            return sum(
                1 for p in self.path.parent.iterdir()
                if not p.name.startswith(".") and p.name not in SKIP_DIRS
                and (p.is_dir() or p.suffix == ".md") and p != self.path
            )
        except OSError:
            return 0

    # -- derived -----------------------------------------------------------
    @property
    def has_spine(self) -> bool:
        return self.table_start is not None or self.breadcrumb is not None

    @property
    def rows_below_marker(self) -> int:
        if self.marker_idx is None or self.table_end is None:
            return 0
        return max(0, self.table_end - self.marker_idx - 1)

    def shape(self) -> str:
        stop = self.marker_idx if self.marker_idx is not None else (self.table_end or 0)
        if self.table_start is None:
            return "breadcrumb" if self.breadcrumb is not None else "none"
        if self.marker == "^^^":
            return "stream"
        if self.marker == "---":
            return "list"
        if self.marker == "...":
            for j in range(self.table_start + 2, stop):
                if re.search(r"\[\[.+?\]\][^|]*\+\s*$", cell(self.lines[j], 1)):
                    return "two-level"
            labelled = sum(
                1 for j in range(self.table_start + 2, stop)
                if len(re.findall(r"\[\[", cell(self.lines[j], 2))) >= 2 and cell(self.lines[j], 1)
            )
            return "grouped" if labelled else "curated"
        return "external"      # a masthead with no marker at all

    def orientation_line(self):
        """The one sentence under the H1, if present."""
        if self.h1 is None:
            return None
        j = self.h1 + 1
        if j < len(self.lines) and self.lines[j].strip() and not self.lines[j].startswith("#"):
            return j
        return None

    def heart_candidate(self):
        """(line, why) of the element that looks like this page's heart, or None.

        Condition 1 of F319's four: a non-trivial table (>=4 body rows) or a
        figure, below the H1, that is not the masthead and not a TOC.
        """
        if self.h1 is None:
            return None
        start = max(self.h1, self.table_end or 0)
        j = start - 1
        while j + 1 < len(self.lines):
            j += 1
            l = self.lines[j]
            if l.startswith("# BRIEF") or l.startswith("# Log"):
                break
            # The heart sits above the first H2. A table under a later heading is
            # that section's content, not the page's buried heart — without this,
            # the check fired on every spec table in the corpus (F319 M2 calibration,
            # 2026-08-09: 100 hits -> the genuine ones).
            # Any heading below H1 ends the heart zone — a table under a later
            # heading is that section's content (F319 M2 calibration).
            if re.match(r"#{2,}\s", l) and j > start:
                break
            if FIGURE.search(l):
                return j, "figure"
            if l.strip().startswith("|"):
                k = j
                while k < len(self.lines) and self.lines[k].strip().startswith("|"):
                    k += 1
                is_toc = TOC.match(l.strip()) is not None
                is_masthead = IDENTITY.match(cell(l, 1)) is not None
                if not is_toc and not is_masthead and k - j >= 6:
                    return j, f"table, {k - j - 2} rows"
                j = k - 1                          # skip the WHOLE table, not one row
        return None

    def prose_before(self, upto: int) -> int:
        """Non-empty prose lines between the orientation line and `upto`."""
        o = self.orientation_line()
        if o is None:
            return 0
        return sum(
            1 for j in range(o + 1, upto)
            if self.lines[j].strip()
            and not self.lines[j].strip().startswith("|")
            and not self.lines[j].startswith("#")
            and not self.lines[j].strip().startswith(">")
        )

    def body_weight(self) -> int:
        """Rough prose volume below the spine, excluding BRIEF/Log. Condition 4."""
        start = max(self.h1 or 0, self.table_end or 0)
        n = 0
        for j in range(start, len(self.lines)):
            if self.lines[j].startswith("# BRIEF") or self.lines[j].startswith("# Log"):
                break
            s = self.lines[j].strip()
            if s and not s.startswith("|"):
                n += len(s)
        return n


CODES = {
    "S01": "no spine at all — neither a breadcrumb nor a masthead (the third opening)",
    "S02": "carries BOTH a breadcrumb and a masthead (R-spine-01)",
    "S03": "H1 sits above the spine — the spine is everything above the H1",
    "S04": "identity cell is breadcrumb-first; should lead with `: description`",
    "S05": "blank line between the H1 and its orientation line",
    "S06": "no orientation line under the H1",
    "S07": "fronts a folder with children but carries no marker — children are invisible",
    "S08": "marker present but nothing below it — a degenerate list/stream",
    "S09": "carries a marker but fronts no folder — it can only sweep siblings",
    "H01": "a substantial element sits below prose; it looks like the buried heart",
}


def check(path: Path) -> list[tuple[str, int, str]]:
    try:
        p = Page(path)
    except Exception as e:                                    # unreadable -> say so
        return [("ERR", 1, f"could not parse: {e}")]
    out: list[tuple[str, int, str]] = []

    if not p.has_spine:
        # Only meaningful for pages that are part of the anchor system's world.
        out.append(("S01", (p.h1 or 0) + 1, CODES["S01"]))
        return out

    if p.table_start is not None and p.breadcrumb is not None:
        out.append(("S02", p.breadcrumb + 1, CODES["S02"]))

    if p.table_start is not None and p.h1 is not None and p.h1 < p.table_start:
        out.append(("S03", p.h1 + 1, CODES["S03"]))

    if p.table_start is not None:
        body = split_cells(p.lines[p.table_start])
        c = body[2] if len(body) > 2 else ""
        a, b = c.find(":"), c.find("→")
        if a >= 0 and b >= 0 and b < a:
            out.append(("S04", p.table_start + 1, CODES["S04"]))

    if p.h1 is not None:
        nxt = p.h1 + 1
        if nxt < len(p.lines) and not p.lines[nxt].strip():
            after = p.lines[nxt + 1].strip() if nxt + 1 < len(p.lines) else ""
            if after and not after.startswith("|") and not after.startswith("#"):
                out.append(("S05", p.h1 + 1, CODES["S05"]))
        elif p.orientation_line() is None and p.table_start is not None and p.h1 > p.table_start:
            out.append(("S06", p.h1 + 1, CODES["S06"]))

    if p.table_start is not None:
        if p.marker is None and p.fronts_folder and p.children > 0:
            out.append(("S07", (p.table_end or 1), f"{CODES['S07']} ({p.children} hidden)"))
        mi = p.marker_idx if p.marker_idx is not None else 0
        if p.marker in {"---", "^^^"} and p.rows_below_marker == 0:
            out.append(("S08", mi + 1, CODES["S08"]))
        if p.marker is not None and not p.fronts_folder:
            out.append(("S09", mi + 1, CODES["S09"]))

    # ---- heart: the four conditions, all of which must hold ----------------
    cand = p.heart_candidate()                                   # condition 1
    if cand and p.body_weight() >= 200:                          # condition 4
        line, why = cand
        prose = p.prose_before(line)                             # condition 3
        o = p.orientation_line()
        if o is not None and line > o + 2 and prose >= 2:        # condition 2
            out.append(("H01", line + 1, f"{CODES['H01']} ({why}, {prose} prose lines above it)"))
    return out


def walk(root: Path):
    for p in sorted(root.rglob("*.md")):
        if any(x in SKIP_DIRS for x in p.parts):
            continue
        if not p.is_file():          # this vault has DIRECTORIES named *.md
            continue
        yield p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--vault", action="store_true", help="check the whole vault")
    ap.add_argument("--summary", action="store_true", help="counts only")
    ap.add_argument("--code", action="append", help="restrict to these finding codes")
    ap.add_argument("--sample", type=int, metavar="N", help="print N spread-out examples per code")
    ap.add_argument("--shapes", action="store_true", help="tally spine shapes instead of findings")
    a = ap.parse_args()

    files = list(walk(VAULT)) if a.vault else [p for p in a.paths if p.suffix == ".md"]
    if not files:
        ap.error("give paths or --vault")

    if a.shapes:
        tally: dict[str, int] = {}
        for f in files:
            try:
                s = Page(f).shape()
            except Exception:
                continue
            tally[s] = tally.get(s, 0) + 1
        print(f"{len(files)} files\n")
        for s, n in sorted(tally.items(), key=lambda kv: -kv[1]):
            print(f"  {n:6}  {s}")
        return 0

    found: dict[str, list[tuple[Path, int, str]]] = {}
    for f in files:
        for code, line, msg in check(f):
            if a.code and code not in a.code:
                continue
            found.setdefault(code, []).append((f, line, msg))

    total = sum(len(v) for v in found.values())
    if a.sample:
        for code in sorted(found):
            hits = found[code]
            step = max(1, len(hits) // a.sample)
            print(f"\n{'=' * 78}\n{code} — {CODES.get(code, '')}   [{len(hits)} total]\n{'=' * 78}")
            for f, line, msg in hits[::step][:a.sample]:
                rel = f.relative_to(VAULT)
                print(f"\n  {rel}:{line}")
                try:
                    src = f.read_text(encoding="utf-8", errors="replace").split("\n")
                    lo, hi = max(0, line - 3), min(len(src), line + 2)
                    for k in range(lo, hi):
                        mark = ">" if k == line - 1 else " "
                        print(f"    {mark} {k+1:5} | {src[k][:110]}")
                except OSError:
                    pass
        return 0

    if not a.summary:
        for code in sorted(found):
            for f, line, msg in found[code]:
                print(f"  [{code}] {f.relative_to(VAULT)}:{line} — {msg}")
        print()
    print(f"spine-check: {total} finding(s) across {len(files)} file(s)")
    for code in sorted(found):
        print(f"  {len(found[code]):6}  {code}  {CODES.get(code, '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
