#!/usr/bin/env python3
"""audit-dispatch.py — build / repair one anchor's dispatch table to the
Masthead + Member-zone shape spec'd in [[FCT Dispatch Table]].

The engine behind the `/audit dispatch` runbook. Given an anchor (path or
name) it:

  1. Locates the anchor's page (the `<Name>.md` in the folder marked with
     `.anchor`).
  2. Parses the *current* dispatch table — the contiguous block of table
     rows anchored by the breadcrumb row (first cell `-[[Name]]-`, second
     cell carrying the `hook://` path), plus any member-zone rows that hang
     off it without intervening prose.
  3. Rebuilds it to the spec shape:
       - breadcrumb row preserved verbatim (its parent chain is the curated
         up-edge of the anchor DAG — never recomputed, only the title cell
         is corrected if the name drifted);
       - the standard / structural rows that have *real targets*; rows that
         point at nothing (no links) are dropped — "omit rows pointing at
         nothing";
       - the member zone preserved; if it ends in an electric marker
         (`...`, a trailing `| --- | |`, or `+` group rows) the table is a
         container, so on-disk child docs not yet listed are surfaced for
         auto-fill.

  4. THE LOAD-BEARING SAFETY INVARIANT: never silently drop a hand-pinned
     curated link. Every link in the *old* table that the rebuild does not
     otherwise place is carried forward into a Related row, and reported
     loudly. A correct rebuild carries forward nothing; a non-empty
     carry-forward is a bug to flag, not ship.

  5. DRY by default — prints the proposed table + a proposed-vs-current
     summary + the curated-link-preservation check, and writes nothing.
     `--fix` writes the rebuilt table back to the page.

Usage:
    audit-dispatch.py <anchor-path-or-name> [dry] [--fix] [--json]

`dry` is the default; pass it explicitly to match the `/audit dispatch
<anchor> dry` runbook spelling. `--fix` is the only thing that writes.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Link extraction / classification
# ---------------------------------------------------------------------------

# wiki-link: [[Target]] or [[Target|Display]] (pipe may be escaped as \|)
WIKI_RE = re.compile(r"\[\[([^\]|]+?)(?:\\?\|[^\]]*)?\]\]")
# markdown link: [text](href)
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def link_keys(cell_text: str) -> list[str]:
    """All link identities in a cell — wiki targets + markdown hrefs.

    Identities are normalized for set comparison: wiki targets keep their
    name (trimmed); markdown hrefs keep the raw href. `hook://` links (the
    breadcrumb's own identity link) are excluded — they are never curated
    member content.
    """
    keys: list[str] = []
    for m in WIKI_RE.finditer(cell_text):
        keys.append("wiki:" + m.group(1).strip())
    for m in MDLINK_RE.finditer(cell_text):
        href = m.group(1).strip()
        if href.startswith("hook://"):
            continue
        keys.append("href:" + href)
    return keys


DASH_CELL_RE = re.compile(r"^:?-{2,}:?$")


def split_cells(line: str) -> list[str]:
    """Split a markdown table row into cells on unescaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    # split on pipes that are NOT escaped (\|)
    parts = re.split(r"(?<!\\)\|", body)
    return [p.strip() for p in parts]


def is_table_line(line: str) -> bool:
    return line.lstrip().startswith("|")


def is_separator_row(cells: list[str]) -> bool:
    """A header/structural separator: every cell is dashes or empty."""
    seen_dash = False
    for c in cells:
        if c == "":
            continue
        if DASH_CELL_RE.match(c):
            seen_dash = True
            continue
        return False
    return seen_dash


def is_breadcrumb_row(cells: list[str]) -> bool:
    if not cells:
        return False
    first = cells[0]
    rest = " ".join(cells[1:])
    looks_like_title = bool(re.match(r"^-?\s*\[\[.+\]\]\s*-?$", first))
    has_nav = ("hook://" in rest) or ("→" in rest)
    return looks_like_title and has_nav


def is_electric_marker(cells: list[str]) -> bool:
    """A member-zone auto-fill marker: a `...` row, or a trailing dash-sep
    row used as an auto-list line."""
    nonempty = [c for c in cells if c != ""]
    if nonempty == ["..."]:
        return True
    return False


# ---------------------------------------------------------------------------
# Anchor / page resolution
# ---------------------------------------------------------------------------

def resolve_anchor_folder(arg: str) -> Path:
    """Resolve the anchor folder (a dir containing `.anchor`) from a path or
    a name. Walks up from a path; falls back to `ha -p` for a bare name."""
    p = Path(arg).expanduser()
    if p.exists():
        d = p if p.is_dir() else p.parent
        cur = d.resolve()
        while True:
            if (cur / ".anchor").exists():
                return cur
            if cur.parent == cur:
                break
            cur = cur.parent
        # no .anchor up-chain — treat the given dir as the anchor folder
        return d.resolve()
    # bare name → ha -p
    try:
        out = subprocess.run(
            ["ha", "-p", arg], capture_output=True, text=True, timeout=15
        )
        cand = out.stdout.strip()
        if cand:
            cp = Path(cand)
            return cp if cp.is_dir() else cp.parent
    except Exception:
        pass
    raise SystemExit(f"audit-dispatch: cannot resolve anchor: {arg!r}")


def find_anchor_page(folder: Path) -> Path:
    """The anchor's page: `<FolderName>.md`, else the first .md with a
    breadcrumb row, else the first .md."""
    primary = folder / f"{folder.name}.md"
    if primary.exists():
        return primary
    mds = sorted(folder.glob("*.md"))
    for m in mds:
        for line in m.read_text(errors="replace").splitlines():
            if is_table_line(line) and is_breadcrumb_row(split_cells(line)):
                return m
    if mds:
        return mds[0]
    raise SystemExit(f"audit-dispatch: no markdown page in {folder}")


def on_disk_children(folder: Path, page: Path) -> list[str]:
    """Child docs + sub-anchors that could be members — as wiki targets
    (filename stems / sub-anchor folder names)."""
    out: list[str] = []
    for entry in sorted(folder.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if (entry / ".anchor").exists():
                out.append(entry.name)
        elif entry.suffix == ".md" and entry.resolve() != page.resolve():
            out.append(entry.stem)
    return out


# ---------------------------------------------------------------------------
# Dispatch-region parsing
# ---------------------------------------------------------------------------

class Row:
    __slots__ = ("raw", "cells", "links")

    def __init__(self, raw: str):
        self.raw = raw.rstrip("\n")
        self.cells = split_cells(raw)
        self.links = link_keys(raw)

    @property
    def label(self) -> str:
        return self.cells[0] if self.cells else ""

    @property
    def has_links(self) -> bool:
        return bool(self.links)


def extract_region(lines: list[str]):
    """Return (start, end, rows) for the dispatch region, or None.

    The region begins at the breadcrumb row and extends over the contiguous
    block of table lines, tolerating blank lines *between* table blocks but
    stopping at the first prose / heading line. `start`/`end` are 0-based
    inclusive line indices into `lines`.
    """
    bc = None
    for i, line in enumerate(lines):
        if is_table_line(line) and is_breadcrumb_row(split_cells(line)):
            bc = i
            break
    if bc is None:
        return None

    end = bc
    i = bc
    n = len(lines)
    while i < n:
        line = lines[i]
        if is_table_line(line):
            end = i
            i += 1
            continue
        if line.strip() == "":
            # tolerate blank lines only if another table block follows
            j = i
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and is_table_line(lines[j]):
                i = j
                continue
            break
        break  # prose / heading ends the region

    rows = [Row(lines[k]) for k in range(bc, end + 1) if is_table_line(lines[k])]
    return bc, end, rows


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------

STANDARD_LABELS = {"anchor", "design", "related", "examples", "external",
                   "members", "member", "spec", "builder"}


def rebuild(rows: list[Row], folder: Path, page: Path, anchor_name: str):
    """Return (new_lines, report) where report records every decision."""
    report = {
        "breadcrumb_title_fixed": False,
        "dropped_empty_rows": [],      # list of raw lines dropped
        "kept_rows": 0,
        "auto_filled_children": [],    # wiki targets injected
        "carried_forward": [],         # link keys rescued into Related
    }

    if not rows or not is_breadcrumb_row(rows[0].cells):
        raise SystemExit("audit-dispatch: no breadcrumb row found in table")

    breadcrumb = rows[0]
    # --- fix the breadcrumb title cell if the name drifted -------------
    new_bc_raw = breadcrumb.raw
    want_title = f"-[[{anchor_name}]]-"
    cur_title = breadcrumb.cells[0]
    cur_target_m = WIKI_RE.search(cur_title)
    cur_target = cur_target_m.group(1).strip() if cur_target_m else None
    if cur_target != anchor_name:
        # replace only the first cell, preserving the rest verbatim
        body = breadcrumb.raw.strip()
        inner = body[1:] if body.startswith("|") else body
        parts = re.split(r"(?<!\\)\|", inner)
        if parts:
            parts[0] = f" {want_title} "
        new_bc_raw = "|" + "|".join(parts)
        report["breadcrumb_title_fixed"] = True

    out: list[str] = [new_bc_raw]

    # --- header separator (mandatory for the table to render) ---------
    # find the first separator row directly after the breadcrumb; reuse it,
    # else synthesize the standard 2-col separator.
    body_rows = rows[1:]
    header_sep = "| --- | --- |"
    if body_rows and is_separator_row(body_rows[0].cells):
        header_sep = body_rows[0].raw
        body_rows = body_rows[1:]
    out.append(header_sep)

    # --- collect the OLD link universe (everything except breadcrumb) --
    old_links: set[str] = set()
    for r in rows[1:]:
        old_links.update(r.links)

    # --- walk remaining rows: keep those with links / electric markers;
    #     drop empty (no-link, non-marker) rows -------------------------
    electric_indices: list[int] = []
    for r in body_rows:
        if is_separator_row(r.cells):
            # a later dash-row = electric auto-list marker → keep
            out.append(r.raw)
            electric_indices.append(len(out) - 1)
            report["kept_rows"] += 1
            continue
        if is_electric_marker(r.cells):
            out.append(r.raw)
            electric_indices.append(len(out) - 1)
            report["kept_rows"] += 1
            continue
        if r.has_links:
            out.append(r.raw)
            report["kept_rows"] += 1
        else:
            report["dropped_empty_rows"].append(r.raw.strip())

    # --- container auto-fill: surface unlisted on-disk children --------
    if electric_indices:
        referenced = {k[len("wiki:"):] for k in old_links if k.startswith("wiki:")}
        unlisted = [c for c in on_disk_children(folder, page) if c not in referenced]
        if unlisted:
            report["auto_filled_children"] = unlisted
            inject = " | ".join(f"[[{c}]]" for c in unlisted)
            # place just above the (last) electric marker
            idx = electric_indices[-1]
            out.insert(idx, f"| {inject} |  |")

    # --- SAFETY: carry forward any old link the rebuild dropped --------
    new_links: set[str] = set()
    for line in out[1:]:  # exclude breadcrumb (preserved verbatim)
        new_links.update(link_keys(line))
    # auto-filled children are also "new"; they were not in old anyway
    missing = sorted(old_links - new_links)
    if missing:
        report["carried_forward"] = missing
        rescued = []
        for k in missing:
            if k.startswith("wiki:"):
                rescued.append(f"[[{k[len('wiki:'):]}]]")
            elif k.startswith("href:"):
                rescued.append(f"[link]({k[len('href:'):]})")
        out.append("| Related | " + ",  ".join(rescued) + " |")

    return out, report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(name, page, old_rows, new_lines, report, applied):
    old_raw = [r.raw for r in old_rows]
    print(f"/audit dispatch — {name}")
    print(f"  page: {page}")
    print(f"  mode: {'APPLIED (--fix)' if applied else 'DRY (no write)'}")
    print()
    print("── current table ──")
    for r in old_raw:
        print("  " + r)
    print()
    print("── proposed table ──")
    for line in new_lines:
        print("  " + line)
    print()
    print("── summary ──")
    if report["breadcrumb_title_fixed"]:
        print("  • breadcrumb title cell corrected")
    if report["dropped_empty_rows"]:
        print(f"  • dropped {len(report['dropped_empty_rows'])} empty row(s) (no link targets):")
        for d in report["dropped_empty_rows"]:
            print(f"      {d}")
    if report["auto_filled_children"]:
        print(f"  • auto-filled {len(report['auto_filled_children'])} unlisted child(ren) into the container: "
              + ", ".join(report["auto_filled_children"]))
    if not (report["breadcrumb_title_fixed"] or report["dropped_empty_rows"]
            or report["auto_filled_children"]):
        print("  • no structural changes (table already in good form)")
    print()
    print("── curated-link preservation ──")
    if report["carried_forward"]:
        print(f"  ⚠️  {len(report['carried_forward'])} curated link(s) would have been DROPPED by the")
        print("      rebuild and were rescued into a Related row. THIS IS A BUG — do not")
        print("      ship until the rebuild places these correctly:")
        for k in report["carried_forward"]:
            print(f"        {k}")
    else:
        print("  ✓ zero curated links dropped — every link in the old table is")
        print("    present in the proposed table.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv):
    p = argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("anchor", help="anchor path or name")
    p.add_argument("dry", nargs="?", default=None,
                   help="explicit 'dry' token (default behaviour anyway)")
    p.add_argument("--fix", action="store_true",
                   help="write the rebuilt table back (default: dry, write nothing)")
    p.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = p.parse_args(argv[1:])

    applied = args.fix and (args.dry != "dry")
    if args.dry == "dry":
        applied = False  # explicit dry overrides --fix

    folder = resolve_anchor_folder(args.anchor)
    page = find_anchor_page(folder)
    name = page.stem
    text = page.read_text(errors="replace")
    lines = text.splitlines()

    region = extract_region(lines)
    if region is None:
        raise SystemExit(f"audit-dispatch: no dispatch table found on {page}")
    start, end, rows = region

    new_lines, report = rebuild(rows, folder, page, name)

    if applied:
        # replace the dispatch region (start..end inclusive) with new_lines
        new_file = lines[:start] + new_lines + lines[end + 1:]
        trailing_nl = "\n" if text.endswith("\n") else ""
        page.write_text("\n".join(new_file) + trailing_nl)

    if args.json:
        print(json.dumps({
            "anchor": name,
            "page": str(page),
            "applied": applied,
            "report": report,
            "proposed": new_lines,
        }, indent=2, ensure_ascii=False))
    else:
        print_report(name, page, rows, new_lines, report, applied)

    # non-zero exit ONLY when the safety invariant fired (a drop was caught)
    return 1 if report["carried_forward"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
