#!/usr/bin/env python3
"""spine_check — validate a page's spine and heart against [[DAS spine]] + [[DAS heart]].

Two specs, one checker, on purpose: a page's opening is graded once, not twice,
so [[R-spine]] owns both zones and the heart never got an R-heart of its own.
Both are slot facets (a region inside a file) rather than disciplines — see
[[DAS Facet]] § Facet groups; they live under `disciplines/` because the folder
predates the taxonomy, not because it decides it.

This is F319 M2's detector, brought forward. It reports; it never edits.

Two jobs:
  1. Classify the spine into one of the seven shapes and flag what is wrong with it.
  2. NOMINATE a heart where one looks buried — never move it. Nominating is a
     question a reader can answer; moving is a silent assertion that the guess
     was right, and a wrong move is invisible forever because the page then
     looks migrated. That asymmetry is why the migration script will never
     touch hearts (F319 § The detector nominates a heart; it never moves one).

Usage
  spine check <path> [<path> ...]           check specific files
  spine check --vault                       check the whole vault
  spine check --vault --summary             counts only
  spine check --vault --code S04            only that finding
  spine check --vault --sample 8            print 8 spread-out examples per code,
                                            with context, for eyeballing

Exit status is 0 always: this is a lens, not a gate. It becomes a gate at F319 M5.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The spine classifier itself lives in spine.py, so this checker and md-toc.py
# read shape from ONE implementation. Adding a second copy here is how the two
# would drift into disagreeing about what a page is.
from spine import (  # noqa: E402
    VAULT, SKIP_DIRS, MARKERS, IDENTITY, BREADCRUMB,
    split_cells, cell, Spine, expand, in_anchor,
)

def disp(p: Path) -> str:
    """Vault-relative when it can be, absolute otherwise — a path outside the
    vault (a repo checked out elsewhere) must still print, not raise."""
    try:
        return str(p.relative_to(VAULT))
    except ValueError:
        return str(p)


FIGURE = re.compile(r"!\[\[[^\]]+\]\]|<img\s|\.svg\)|\.png\)")
TOC = re.compile(r"^\|\s*(\*\*)?Table of Contents", re.I)


class Page(Spine):
    """A spine, plus the heart analysis only this checker needs."""

    def orientation_line(self):
        """The one sentence under the H1, if present."""
        if self.h1 is None:
            return None
        j = self.h1 + 1
        if j < len(self.lines) and self.lines[j].strip() and not self.lines[j].startswith("#"):
            return j
        return None

    def _heart_element(self, j: int):
        """`(line, why)` if line `j` opens a heart-worthy element, else None.

        A non-trivial table (>=4 body rows) or a figure — never the masthead,
        never a TOC. Returns the line it starts on so the caller can report it.
        """
        if j >= len(self.lines):        # a heading with nothing after it
            return None
        l = self.lines[j]
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
        return None

    def _next_content(self, j: int) -> int:
        """Index of the next non-blank line at or after `j` (len(lines) if none)."""
        while j < len(self.lines) and not self.lines[j].strip():
            j += 1
        return j

    def heart_candidate(self):
        """(line, why) of the element that looks like this page's heart, or None.

        Condition 1 of F319's four: a non-trivial table (>=4 body rows) or a
        figure, below the H1, that is not the masthead and not a TOC.

        The heart zone runs from the H1 to the first H2 that opens a real
        SECTION — not merely to the first H2. A heading whose section begins
        immediately with a table or figure, before any prose has intervened, is
        a *labelled heart*: the author named their heart instead of leaving it
        bare, which is better writing, not a different structure. Treating every
        heading as the end of the zone made those hearts invisible — 40 pages
        vault-wide, [[Stones]] among them, which Dan put forward on 2026-08-10 as
        the exemplar of what a page with a heart should look like. The detector
        returned None on it.

        Invisibility was the real cost, and it is not cosmetic: H01 fires when a
        heart sits buried under prose, so a page whose heart the detector cannot
        see has no protection against its heart being buried later. Verified by
        pushing four prose lines above [[Stones]]'s map table on a scratch copy —
        H01 stayed silent, because the zone had already ended at the heading.
        """
        if self.h1 is None:
            return None
        start = max(self.h1, self.table_end or 0)
        j = start - 1
        while j + 1 < len(self.lines):
            j += 1
            l = self.lines[j]
            # ANY second level-1 heading ends the heart zone, not just the two
            # that used to be named here. The heart is what sits directly below
            # THE H1; a further `# ` opens a new top-level section, and anything
            # under it is that section's content by definition. `# BRIEF` and
            # `# Log` were only the two instances someone happened to hit, and a
            # two-name list is the shape that manufactures an invisible miss —
            # the corpus also carries `# MEETINGS`, `# Quotes`, `# TOPICS` and,
            # on this very repo, `# What the classification found`, whose verdict
            # table was nominated as the page's buried heart (2026-08-11).
            if j > self.h1 and re.match(r"#\s", l):
                break
            if re.match(r"#{2,}\s", l) and j > start:
                # A heading that leads STRAIGHT into a table/figure labels the
                # heart rather than ending the zone — and this must not depend on
                # whether prose appeared above it, because "prose above the heart"
                # is the very thing H01 reports. Gating on that made a buried
                # labelled heart invisible, i.e. silent in exactly the case the
                # check exists for.
                #
                # Only the FIRST heading below the H1 gets this reading, since the
                # loop breaks either way: a table under a later heading is still
                # that section's content, which is the F319 M2 calibration that
                # took this check from 100 hits to the genuine few.
                hit = self._heart_element(self._next_content(j + 1))
                if hit:
                    return hit
                break
            hit = self._heart_element(j)
            if hit:
                return hit
            if l.strip().startswith("|"):
                k = j
                while k < len(self.lines) and self.lines[k].strip().startswith("|"):
                    k += 1
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
        # Scoped to markdown inside an anchor, per F308 Q3 (B). A spine's whole
        # content is a path THROUGH the anchor tree, so a file outside every
        # anchor has no such path to state and is out of scope until it is filed.
        if in_anchor(path):
            out.append(("S01", (p.h1 or 0) + 1, CODES["S01"]))
        return out

    if p.table_start is not None and p.breadcrumb is not None:
        out.append(("S02", p.breadcrumb + 1, CODES["S02"]))

    if p.table_start is not None and p.h1 is not None and p.h1 < p.table_start:
        out.append(("S03", p.h1 + 1, CODES["S03"]))

    if p.table_start is not None:
        # Compare SEGMENTS, not character offsets. `c.find(":")` matches the
        # colon inside `hook://p/Name`, so a breadcrumb-only cell — one with no
        # description at all, and therefore nothing to lead with — scored as
        # breadcrumb-first. That over-count was the whole of this code's
        # population on inspection (measured 2026-08-10).
        body = split_cells(p.lines[p.table_start])
        segs = [s.strip() for s in (body[2] if len(body) > 2 else "").split("<br>") if s.strip()]
        d = next((i for i, s in enumerate(segs) if s.startswith(":")), None)
        b = next((i for i, s in enumerate(segs) if "→" in s), None)
        if d is not None and b is not None and b < d:
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
            # Count only members the page does not ALREADY link, exactly as S08
            # does eleven lines below. Without the filter this reported folder
            # SIZE and called it hidden: 39 pages / 242 children vault-wide, of
            # which 21 pages hid nothing at all and the true count was 18 / 51
            # (measured 2026-08-11, twice — [[ATT|Atticus]] and again here).
            # Both worked examples in [[DAS spine]] § The catchall is not
            # optional were among the false ones: `ASIO` 33 members / 0
            # unlinked, `META` 14 / 0. Their mastheads are one hand-written row
            # per child — a curated spine doing its job, not a page hiding
            # anything, and adding the `...` they were told to add would have
            # surfaced nothing, because F081 body-mention suppression omits
            # every child the page already links. A message asserting "children
            # are invisible" about children linked three rows above the marker
            # it demands is the shape that trains readers to discount the
            # checker.
            body = "\n".join(p.lines)
            hidden = [c for c in p.child_names() if f"[[{c}" not in body]
            if hidden:
                out.append(("S07", (p.table_end or 1),
                            f"{CODES['S07']} ({len(hidden)} hidden, "
                            f"e.g. {hidden[0]})"))
        mi = p.marker_idx if p.marker_idx is not None else 0
        # Degenerate means the machine SHOULD have written rows and did not —
        # so the folder has to exist and hold members. A `---` over an empty
        # folder, or on a page that fronts no folder at all (which is S09's
        # business), is at its correct resting state. Without this the code was
        # 43/44 false positive in-repo, measured 2026-08-10.
        if (p.marker in {"---", "^^^"} and p.rows_below_marker == 0
                and p.fronts_folder and p.children > 0):
            # ...and only for members the page does not ALREADY link. An empty
            # electric zone under a marker is the correct state when every
            # child is linked above it by hand (F081 body-mention suppression)
            # — the zone is empty because suppression worked, not because the
            # index is stale. [[HBR Log]] is exactly that page.
            body = "\n".join(p.lines)
            unlisted = [c for c in p.child_names() if f"[[{c}" not in body]
            if unlisted:
                out.append(("S08", mi + 1,
                            f"{CODES['S08']} ({len(unlisted)} member(s) unlisted, "
                            f"e.g. {unlisted[0]})"))
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--vault", action="store_true", help="check the whole vault")
    ap.add_argument("--summary", action="store_true", help="counts only")
    ap.add_argument("--code", action="append", help="restrict to these finding codes")
    ap.add_argument("--sample", type=int, metavar="N", help="print N spread-out examples per code")
    ap.add_argument("--shapes", action="store_true", help="tally spine shapes instead of findings")
    a = ap.parse_args(argv)

    if a.vault:
        files = list(walk(VAULT))
    elif a.paths:
        try:
            files = expand(a.paths)
        except ValueError as e:
            ap.error(str(e))
    else:
        ap.error("give paths, a directory, or --vault")

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
                print(f"\n  {disp(f)}:{line}")
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
                print(f"  [{code}] {disp(f)}:{line} — {msg}")
        print()
    print(f"spine check: {total} finding(s) across {len(files)} file(s)")
    for code in sorted(found):
        print(f"  {len(found[code]):6}  {code}  {CODES.get(code, '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
