#!/usr/bin/env python3
"""audit-dispatch.py — build / repair one anchor's dispatch table to the
Masthead + Member-zone shape spec'd in [[DAS Dispatch Table]].

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


STRUCK_RE = re.compile(r"~~.+?~~", re.DOTALL)

VAULT_ROOT = Path.home() / "ob" / "kmr"
# `/Yore/` is load-bearing here, not incidental: archiving to Yore is HOW a doc
# is retired, so a link into Yore is a link to something deliberately gone.
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/",
                       "/Closet/")

_BASENAME_INDEX: set[str] | None = None


def vault_basenames() -> set[str]:
    """Every live filename in the vault, indexed both ways — built once per run.

    EVERY file, not just `.md`. A wiki-link may name a PDF, a spreadsheet, an
    image, a `.txt` — those are ordinary Obsidian links and their targets are
    ordinary files. Indexing only `.md` made 417 rows across 121 anchors look
    dead on the first vault-wide dry sweep of this check, nearly all of them
    perfectly good links to `.pdf` / `.xlsx` / `.ppt` attachments. That sweep
    is why this function walks everything: the drop is destructive and its
    input is a resolver, so the resolver's blind spots ARE the damage.

    Each file is indexed under both its full name (`Foo.pdf`, how an
    attachment is linked) and its stem (`Foo`, how a note is linked).
    """
    global _BASENAME_INDEX
    if _BASENAME_INDEX is None:
        import os
        found: set[str] = set()
        for root, dirs, files in os.walk(VAULT_ROOT, followlinks=False):
            if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            # Folders count. `[[SVAI Design]]` naming a folder that holds docs
            # but no `SVAI Design.md` is an unresolved link Obsidian would
            # flag, yet the row is pointing at something real and the repair is
            # to give the folder an index page — not to delete the row.
            found.update(dirs)
            for f in files:
                if f.startswith("."):
                    continue
                found.add(f)
                stem = f.rsplit(".", 1)[0]
                if stem:
                    found.add(stem)
        _BASENAME_INDEX = found
    return _BASENAME_INDEX


_HA_COMMANDS: set[str] | None = None
_HA_AVAILABLE = True


def ha_command_names() -> set[str]:
    """Every HookAnchor command name, lowercased — built once per run.

    A wiki-link in a dispatch table does not always name a file. Catalog pages
    (`DIR`, `AGENT`) put their content INSIDE the dispatch table by design, and
    their links are HookAnchor command names — `[[grove]]`, `[[Public Gdrive
    Page]]`, `[[qball]]`. Some bind to paths outside the vault, some to URLs
    and so have no path at all. Judging those by vault residency marks live
    catalog rows dead; the vault-wide dry sweep put 20-odd such rows on the
    chopping block, which is how this was caught before it ran with `--fix`.

    If `ha` cannot be reached, `_HA_AVAILABLE` goes false and the dead-row drop
    disables itself. A resolver that failed to load is not evidence of absence,
    and this check deletes rows — the fail-safe direction is to keep them.
    """
    global _HA_COMMANDS, _HA_AVAILABLE
    if _HA_COMMANDS is None:
        try:
            out = subprocess.run(["ha", "--dump", "--format=name"],
                                 capture_output=True, text=True, timeout=60)
            names = {l.strip().lower() for l in out.stdout.splitlines() if l.strip()}
            if not names:
                raise RuntimeError("empty dump")
            _HA_COMMANDS = names
        except Exception:
            _HA_AVAILABLE = False
            _HA_COMMANDS = set()
    return _HA_COMMANDS


def wiki_target_resolves(target: str) -> bool:
    """Does `[[target]]` name something that still exists?

    The target is stripped of any `#heading` / `#^block` before lookup — those
    live or die with their file. A target carrying a path (`Folder/Doc`) is
    matched on its last segment, the same way Obsidian resolves one.
    """
    base = target.split("#", 1)[0].strip().rstrip("/")
    base = base.rsplit("/", 1)[-1].strip()
    if not base:
        return False
    return base in vault_basenames() or base.lower() in ha_command_names()


def live_link_keys(cell_text: str) -> list[str]:
    """`link_keys`, minus every link whose target is gone.

    T088 — the runbook lists "remove rows pointing at deleted children" among
    the fixes this tool applies mechanically without asking. It never applied
    that one, because the keep/drop test only asked whether a row contained
    link *syntax*, never whether the link had a *target*. Found 2026-08-01
    finishing T087: after `SKA Audit Design/` was archived to Yore, `SKA
    audit.md` kept `| [[SKA Audit Design|Design]] | [[SKA Audit PRD|PRD]], |`,
    a row whose two links both pointed at nothing, and the tool reported the
    table "already in good form" on two consecutive runs. Dropping it by hand
    is exactly what the never-hand-author-a-dispatch-table rule exists to
    prevent, so the tool has to be the one that does it.

    A link is dead two ways, and both answer the same question — is there
    anything at the other end?

      * its target does not resolve to a live `.md` in the vault; or
      * it is struck through (`~~[[X|Design]]~~`), which is the maintenance
        pass declaring the target gone by hand. Honoring the strikethrough is
        a short-circuit of the resolution check, not a second rule.

    Only wiki-links are resolution-checked. A markdown href (`file://`,
    `https://`, a relative path) is treated as live-unknown and keeps its row:
    this tool cannot see the other end of those, and a row it cannot judge is
    a row it must not delete.
    """
    spans = [(m.start(), m.end()) for m in STRUCK_RE.finditer(cell_text)]

    def struck(pos: int) -> bool:
        return any(s <= pos < e for s, e in spans)

    keys: list[str] = []
    for m in WIKI_RE.finditer(cell_text):
        target = m.group(1).strip()
        if struck(m.start()) or not wiki_target_resolves(target):
            continue
        keys.append("wiki:" + target)
    for m in MDLINK_RE.finditer(cell_text):
        href = m.group(1).strip()
        if href.startswith("hook://") or struck(m.start()):
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
    __slots__ = ("raw", "cells", "links", "live_links")

    def __init__(self, raw: str):
        self.raw = raw.rstrip("\n")
        self.cells = split_cells(raw)
        self.links = link_keys(raw)
        self.live_links = live_link_keys(raw)

    @property
    def label(self) -> str:
        return self.cells[0] if self.cells else ""

    @property
    def has_links(self) -> bool:
        return bool(self.live_links)

    @property
    def is_dead(self) -> bool:
        """The row has links, and every one of them points at nothing.

        A row mixing live and dead links is NOT dead: the live link is the
        reason the row is still there, and the dead one is a note beside it.
        Nor is a row that merely has no links — that one never had a target,
        and `dropped_empty_rows` already covers it.

        A `hook://` link keeps a row alive too. `link_keys` drops those from
        the link universe on purpose (they are the breadcrumb's own identity
        and must not be carried forward), but "not curated member content" and
        "not a target" are different claims — outside the breadcrumb a
        `hook://` link points at something this tool cannot follow, and an
        unfollowable target is unjudgeable, not absent."""
        if "hook://" in self.raw and not is_breadcrumb_row(self.cells):
            return False
        if not self.live_links and not _HA_AVAILABLE:
            return False  # resolver did not load — never delete on a guess
        return bool(self.links) and not self.live_links


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
        "dropped_dead_rows": [],       # T088 — every link struck through
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
    # Dead links are excluded here as well as at the drop test — otherwise the
    # carry-forward net below rescues the dead link into a Related row and
    # silently undoes the drop in the same pass (T088).
    old_links: set[str] = set()
    for r in rows[1:]:
        old_links.update(r.live_links)

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
        if r.is_dead:
            # Tested before has_links so a wholly-dead row cannot reach the
            # keep branch; it is reported separately from an empty row because
            # the two say different things — one row never had a target, this
            # one outlived its target.
            report["dropped_dead_rows"].append(r.raw.strip())
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
        new_links.update(live_link_keys(line))
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
    if report["dropped_dead_rows"]:
        print(f"  • dropped {len(report['dropped_dead_rows'])} dead row(s) (every link points at nothing):")
        for d in report["dropped_dead_rows"]:
            print(f"      {d}")
    if report["auto_filled_children"]:
        print(f"  • auto-filled {len(report['auto_filled_children'])} unlisted child(ren) into the container: "
              + ", ".join(report["auto_filled_children"]))
    if not (report["breadcrumb_title_fixed"] or report["dropped_empty_rows"]
            or report["dropped_dead_rows"] or report["auto_filled_children"]):
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
