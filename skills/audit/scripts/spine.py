#!/usr/bin/env python3
"""spine: every operation on a page's spine, behind one verb.

The shape is never declared — not in `.anchor`, not in frontmatter, not in a
trait. A spine states its own kind by its geometry: whether it is a `:>>`
breadcrumb or a masthead table, which marker row that table carries, and how
its rows are laid out. Anything that wants to know asks this module, so the
classification lives in one place and cannot drift between callers.

    spine shape <file> ...        name each file's shape
    spine census [--vault]        shape counts
    spine list --shape list       every page of one shape
    spine check ...               the full spine + heart checks (spine_check)

A verb is required. This file holds only the parse-and-classify core that every
verb needs; each verb imports its own machinery when it runs, so the cheap verbs
stay cheap — `spine` sits on a hot path and must not pay for `check`.

Shapes, and what each says about the page's children:

    breadcrumb   `:>>`     there are none — this page is a leaf
    curated      `...`     listed by hand, one row each; the catchall is a valve
    grouped      `...`     curated, but the rows form cohesive named groups
    two-level    `...` `+` grouped, but each label is a page with its own spine
    list         `---`     the machine writes one row each, alphabetical
    stream       `^^^`     the same, reversed, so dated children read newest-first
    external     none      they are not in this folder at all
    none                   no spine yet

Discipline: [[DAS spine]]. Rules: [[R-spine]]. Roadmap: TINK319 Spine Agenda.
"""

import argparse
import re
import sys
from pathlib import Path

VAULT = Path.home() / "ob" / "kmr"
SKIP_DIRS = {".git", ".obsidian", "node_modules", ".trash", "Yore",
             ".stversions", "__pycache__"}

MARKERS = {"...", "+++", "^^^", "!!!"}
# Rows below the marker are machine-written; nothing here may judge their content.

IDENTITY = re.compile(r"^\s*-\s*\[\[.+?\]\]\s*-\s*$")
BREADCRUMB = re.compile(r"^\s*:>>")

_ANCHOR_KEY = re.compile(r"^\s*(slug|title)\s*:\s*(.+?)\s*$")
_entry_names: dict[Path, set[str]] = {}

_ap_mod = None


def _head_h1(text: str):
    """The document's HEAD H1 line index, via the ONE definition of that (F296).

    This used to be `l.startswith("# ")` scanned from the body start, which is
    the pattern F296 replaced everywhere else and T093 renamed off `_first_h1`
    for the reason that bites here: `# BRIEF` / `# LOG` / `# MEETINGS` opening a
    body section below an earlier `##` is a widespread user convention, not a
    head. Scanning for the first `# ` hands back a "head" hundreds of lines into
    the body, and every check anchored on it then reports a real line number for
    a defect that is not there. Measured 2026-08-11: **215** in-scope pages were
    handed a head H1 the primitive says does not exist, and 3 more had a legally
    indented one missed because the hand-spelled pattern demanded column zero.

    Loaded lazily and short-circuited to an already-live module, per the same
    reasoning as `_load_checker_module`: `audit-plan` loads `spine` through
    `_spine_sibling`, so re-executing it from disk here would give this module a
    second, divergent copy of 7,000 lines the rest of the process is not using.
    """
    global _ap_mod
    if _ap_mod is None:
        here = Path(__file__).resolve().parent
        target = here / "audit-plan.py"
        for m in list(sys.modules.values()):
            f = getattr(m, "__file__", None)
            if f and Path(f).resolve() == target and hasattr(m, "_head_h1"):
                _ap_mod = m
                break
        else:
            import importlib.util
            spec = importlib.util.spec_from_file_location("_spine_ap", target)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"cannot load audit-plan.py beside {here}")
            _ap_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_ap_mod)
    return _ap_mod._head_h1(text)[0]


def entry_names(folder: Path) -> set[str]:
    """The stems that would name this folder's anchor entry page.

    An anchor's entry page is `{slug}.md`, and `slug` falls back to the folder
    basename when `.anchor` does not declare one ([[DAS Dot Anchor]]) — but a
    declared `slug` or `title` renames it, so `dans-anchor-system/` is fronted
    by `DAS.md` and `skills/` by `DAS Skills.md`. Testing basename equality
    alone misses 45 anchor pages vault-wide and calls each one a page that
    sweeps its siblings. Cached: this is asked once per scanned file.
    """
    hit = _entry_names.get(folder)
    if hit is not None:
        return hit
    names = {folder.name}
    a = folder / ".anchor"
    if a.is_file():
        try:
            for ln in a.read_text(encoding="utf-8", errors="replace").split("\n"):
                m = _ANCHOR_KEY.match(ln)
                if m:
                    names.add(m.group(2).strip().strip('"').strip("'"))
        except OSError:
            pass
    _entry_names[folder] = names
    return names

# Which shapes can host a table of contents.
#
# A dispatch spine that ENUMERATES its folder has already answered "what is
# here and where do I go" — for the folder. A TOC answers it for the page. On
# `list`, `stream` and `external` the answer is the page's whole job: their
# sections are entries, not sections, so a TOC over them is a list of dates or
# a second copy of the index. The shapes that keep a real document in the body
# — a leaf under a breadcrumb, or an anchor page whose rows are hand-curated —
# stay eligible, and the size floor decides from there. Ruled 2026-08-10.
TOC_ELIGIBLE = {"breadcrumb", "curated", "grouped", "two-level", "none"}
TOC_INELIGIBLE = {"list", "stream", "external"}


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


_in_anchor: dict[Path, bool] = {}


def in_anchor(path: Path) -> bool:
    """Is this file inside an anchor — the scope the spine rule applies to?

    F308 Q3, ruled by the user 2026-08-06: *"the spine only applies to files,
    markdown files inside of an anchor."* Loose material outside every anchor
    is out of scope until it is filed, at which point it inherits the rule.
    The walk stops at the vault root, so a file above every anchor is out.
    """
    d = Path(path).parent
    seen = []
    while True:
        hit = _in_anchor.get(d)
        if hit is not None:
            break
        seen.append(d)
        if (d / ".anchor").exists():
            hit = True
            break
        if d == VAULT or d.parent == d:
            hit = False
            break
        d = d.parent
    for s in seen:
        _in_anchor[s] = hit
    return hit


class Spine:
    """A page's spine, parsed once."""

    def __init__(self, path: Path, lines: list[str] | None = None):
        self.path = Path(path)
        if lines is None:
            lines = self.path.read_text(encoding="utf-8",
                                        errors="replace").split("\n")
        self.lines = lines
        self.fenced = self._fenced()
        self.body_start = self._after_frontmatter()
        self.h1 = _head_h1("\n".join(lines))
        self.breadcrumb = self._find(lambda l: BREADCRUMB.match(l), self.body_start)
        self.table_start = self._find_identity()
        self.table_end = self._table_end()
        self.marker_idx, self.marker = self._find_marker()
        self.fronts_folder = self.path.stem in entry_names(self.path.parent)
        self.children = self._children()

    def _fenced(self) -> list[bool]:
        """Which lines sit inside a code fence.

        A spec page shows the house head as a fenced TEMPLATE — frontmatter,
        a `:>>` breadcrumb, an H1 — and without this every such page reads as
        carrying a real breadcrumb on top of its real masthead. Fences open
        with three-or-more backticks and close on a run at least as long, so
        a ````markdown block containing ``` is handled.
        """
        out, depth = [], 0
        for l in self.lines:
            s = l.lstrip()
            m = re.match(r"^(`{3,}|~{3,})", s)
            if m:
                tick = m.group(1)
                if depth == 0:
                    depth = len(tick)
                    out.append(True)
                    continue
                if len(tick) >= depth and not s[len(tick):].strip():
                    depth = 0
                    out.append(True)
                    continue
            out.append(depth > 0)
        return out

    def _after_frontmatter(self) -> int:
        if self.lines and self.lines[0].strip() == "---":
            for j in range(1, min(len(self.lines), 80)):
                if self.lines[j].strip() == "---":
                    return j + 1
        return 0

    def _find(self, pred, start=0, stop=None):
        stop = len(self.lines) if stop is None else stop
        for j in range(start, stop):
            if self.fenced[j]:
                continue
            if pred(self.lines[j]):
                return j
        return None

    def _find_identity(self):
        for j in range(self.body_start, len(self.lines)):
            if self.fenced[j]:
                continue
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

    def child_names(self) -> list[str]:
        """The folder members a catchall would sweep, by the name a wiki-link
        would use — the stem for a page, the directory name for a folder."""
        if not self.fronts_folder:
            return []
        try:
            return sorted(
                (p.stem if p.suffix == ".md" else p.name)
                for p in self.path.parent.iterdir()
                if not p.name.startswith(".") and p.name not in SKIP_DIRS
                and (p.is_dir() or p.suffix == ".md") and p != self.path
            )
        except OSError:
            return []

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
                if len(re.findall(r"\[\[", cell(self.lines[j], 2))) >= 2
                and cell(self.lines[j], 1)
            )
            return "grouped" if labelled else "curated"
        return "external"      # a masthead with no marker at all

    def toc_eligible(self) -> bool:
        return self.shape() in TOC_ELIGIBLE


def is_fixture(p: Path) -> bool:
    """A deliberate-violation corpus specimen, which no checker may grade.

    Warden's corpus holds cases like `progressive-001-both-forms/fixture/` —
    files authored to BREAK a rule so the engine can be tested against them.
    Reporting a finding there is reporting that the test data is test data.
    """
    parts = p.parts
    return "fixture" in parts and any("Corpus" in d for d in parts)


def walk(root: Path):
    for p in sorted(root.rglob("*.md")):
        if not p.is_file() or any(d in SKIP_DIRS for d in p.parts):
            continue
        if is_fixture(p):
            continue
        yield p


def expand(paths) -> list[Path]:
    """Resolve a mixed list of files and directories to markdown files.

    A directory expands to every `.md` beneath it. A path that yields nothing
    is an error, never a silent skip: a scan that quietly drops its argument
    reports a clean zero that is a claim about the scanner, not the corpus.
    """
    out, empty = [], []
    for p in (Path(x).resolve() for x in paths):
        if p.is_dir():
            found = list(walk(p))
            (out.extend(found) if found else empty.append(p))
        elif p.suffix == ".md":
            out.append(p)
        else:
            empty.append(p)
    if empty:
        raise ValueError("no markdown found under: "
                         + ", ".join(str(p) for p in empty))
    return out


def _targets(args, ap):
    if args.vault:
        return list(walk(VAULT))
    if args.file:
        try:
            return expand(args.file)
        except ValueError as e:
            ap.error(str(e))
    ap.error("give files, a directory, or --vault")


def v_shape(args, ap) -> int:
    for p in _targets(args, ap):
        try:
            s = Spine(p)
        except OSError:
            continue
        shape = s.shape()
        if args.shape and shape != args.shape:
            continue
        toc = "toc-ok" if s.toc_eligible() else "no-toc"
        print(f"{shape:11} {s.marker or '-':4} {toc:7} children={s.children:<4} {p}")
    return 0


def v_census(args, ap) -> int:
    from collections import Counter          # verb-local: the core never needs it
    counts = Counter()
    for p in _targets(args, ap):
        try:
            counts[Spine(p).shape()] += 1
        except OSError:
            continue
    for shape, n in counts.most_common():
        flag = "" if shape in TOC_ELIGIBLE else "   (never a TOC)"
        print(f"  {shape:11} {n:6}{flag}")
    return 0


VERBS = {
    "shape": (v_shape, "name each file's spine shape"),
    "list": (v_shape, "every page of one shape (alias of shape --shape)"),
    "census": (v_census, "shape counts"),
}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "check":
        # Hand the tail straight over: `check` owns a rich flag set of its own
        # (--summary, --code, --sample) and this parser must not eat any of it.
        import spine_check
        return spine_check.main(argv[1:])
    if argv and argv[0] == "fix":
        import spine_fix
        return spine_fix.main(argv[1:])

    ap = argparse.ArgumentParser(
        prog="spine", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=sorted(VERBS) + ["check", "fix"],
                    help="; ".join(f"{k} — {d}" for k, (_, d) in sorted(VERBS.items()))
                         + "; check — the full spine + heart checks")
    ap.add_argument("file", type=Path, nargs="*", default=[])
    ap.add_argument("--vault", action="store_true", help="scan the whole vault")
    ap.add_argument("--shape", help="restrict to this shape")
    args = ap.parse_args(argv)
    return VERBS[args.verb][0](args, ap)


if __name__ == "__main__":
    sys.exit(main())
