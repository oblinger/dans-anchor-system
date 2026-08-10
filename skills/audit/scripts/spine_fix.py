#!/usr/bin/env python3
"""spine fix — the three mechanical spine rearrangements, self-verified per file.

Reached as `spine fix <paths|--vault> [--dry-run]`. Fixes exactly the codes
that are pure rearrangement, and nothing else:

    S03  move the masthead above the H1
    S04  flip the identity cell to description-first
    S05  delete the blank line between the H1 and its orientation line

**It never touches the heart, and never a code that needs judgement.** S02
(both a breadcrumb and a masthead) is a choice about what the page IS; S07 and
S08 are choices about a folder's régime; S01's scope is unsettled. A script
that guessed at any of them would leave the page *looking* migrated, which is
the one failure that cannot be detected afterwards.

Every write is gated on a per-file proof rather than on trust:

  * the multiset of link targets is unchanged,
  * the H1 text is unchanged,
  * the multiset of table rows is unchanged, comparing the identity row by its
    `<br>` segments as a SET so the flip itself is allowed and nothing else is,
  * the identity cell's description TEXT is unchanged — load-bearing, because
    HookAnchor harvests that text into the sibling `.anchor`, so altering it
    would silently rewrite a second file this script never opened,
  * no non-blank line is lost.

On any mismatch the file is left alone and the reason is printed. Three
measurements during F308 were wrong from regex-splitting table cells, so cells
are split by `spine.split_cells`, a character scanner — never a regex.

Discipline: [[DAS spine]]. Rules: [[R-spine]]. Roadmap: TINK319 Spine Agenda.
"""

import re
import sys
from collections import Counter
from pathlib import Path

from spine import Spine, split_cells, expand, walk, VAULT

LINK = re.compile(r"\[\[([^\]]+?)\]\]|\]\(([^)]+)\)")


def link_bag(text: str) -> Counter:
    """Every link target in the file, however written. Display text is dropped
    so that a cell reflowed from `[[A\\|B]]` to `[[A\\|B]]` still compares
    equal on what it POINTS AT, which is what must not change."""
    out = Counter()
    for m in LINK.finditer(text):
        t = m.group(1) or m.group(2) or ""
        out[t.split("\\|")[0].split("|")[0].strip()] += 1
    return out


def segments(cell_text: str) -> list[str]:
    return [s.strip() for s in cell_text.split("<br>") if s.strip()]


def desc_segment(cell_text: str) -> str | None:
    for s in segments(cell_text):
        if s.startswith(":"):
            return s[1:].strip()
    return None


def row_bag(lines: list[str], identity_idx: int | None) -> Counter:
    """Table rows as a multiset. The identity row is reduced to its sorted
    segment set, so reordering it is permitted and editing it is not."""
    out = Counter()
    for i, l in enumerate(lines):
        s = l.strip()
        if not s.startswith("|"):
            continue
        if i == identity_idx:
            cs = split_cells(l)
            right = cs[2] if len(cs) > 2 else ""
            key = "IDENTITY:" + "␟".join(sorted(segments(right)))
            out[key] += 1
        else:
            out[re.sub(r"\s+", " ", s)] += 1
    return out


# --------------------------------------------------------------------------
# the three rearrangements
# --------------------------------------------------------------------------
def fix_s04(lines: list[str], sp: Spine) -> bool:
    """Identity cell -> description first, breadcrumb beneath."""
    if sp.table_start is None:
        return False
    cs = split_cells(lines[sp.table_start])
    if len(cs) < 3:
        return False
    segs = segments(cs[2])
    desc = [s for s in segs if s.startswith(":")]
    rest = [s for s in segs if not s.startswith(":")]
    if not desc or segs[0].startswith(":"):
        return False                       # nothing to flip, or already flipped
    cs[2] = " " + "<br>".join(desc + rest) + " "
    lines[sp.table_start] = "|".join(cs)
    return True


def fix_s05(lines: list[str], sp: Spine) -> bool:
    """Delete the blank line between the H1 and its orientation line."""
    h = sp.h1
    if h is None or h + 2 >= len(lines):
        return False
    if lines[h + 1].strip():
        return False
    nxt = lines[h + 2].strip()
    if not nxt or nxt.startswith(("|", "#")):
        return False
    del lines[h + 1]
    return True


def fix_s03(lines: list[str], sp: Spine) -> bool:
    """Move the whole masthead block above the H1.

    The block is moved opaquely — every row including everything below the
    electric marker, which is recomputed by HookAnchor and must never be
    parsed or rewritten here.
    """
    if sp.table_start is None or sp.h1 is None or sp.h1 > sp.table_start:
        return False
    t0, t1 = sp.table_start, sp.table_end
    if t1 is None:
        return False
    block = lines[t0:t1]
    rest = lines[:t0] + lines[t1:]
    # Lifting the table out leaves the blank that preceded it adjacent to the
    # blank that followed it. Collapse that pair, or every moved page ends up
    # with a double blank under its orientation line.
    if 0 < t0 < len(rest) and not rest[t0 - 1].strip() and not rest[t0].strip():
        del rest[t0]
    # re-find the H1 in the remainder, then drop blanks that bracketed the table
    h = next((i for i, l in enumerate(rest) if l.startswith("# ")), None)
    if h is None:
        return False
    while h > 0 and not rest[h - 1].strip():
        del rest[h - 1]
        h -= 1
    out = rest[:h] + block + [""] + rest[h:]
    # The moved block must not butt against the frontmatter fence — the
    # exemplar ([[HBR]]) separates them, and a `---` immediately followed by a
    # `|` row reads as one ambiguous run.
    if h > 0 and out[h - 1].strip() == "---" and h >= 3:
        out.insert(h, "")
    lines[:] = out
    return True


# --------------------------------------------------------------------------
def plan_file(path: Path):
    """Return (action, note, new_text). action in fixed | ok | refused | skip."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return "skip", f"unreadable ({e.__class__.__name__})", None

    lines = text.split("\n")
    before_links = link_bag(text)
    sp0 = Spine(path, list(lines))
    before_rows = row_bag(lines, sp0.table_start)
    before_h1 = lines[sp0.h1] if sp0.h1 is not None else None
    before_desc = None
    if sp0.table_start is not None:
        cs = split_cells(lines[sp0.table_start])
        before_desc = desc_segment(cs[2] if len(cs) > 2 else "")
    # A MULTISET, not a sequence: relocating the masthead is precisely a change
    # of order, so an ordered comparison here refuses every S03 fix. What must
    # hold is that no non-blank line is lost, gained, or altered.
    before_solid = Counter(l for l in lines if l.strip())

    # WHICH codes apply is the checker's call, never re-derived here. Deriving
    # it independently silently widened S05 from 55 files to 300: the checker
    # returns early on a page with no spine at all, and a fixer that did not
    # would have edited 245 files whose scope is still an open question.
    import spine_check
    codes = {c for c, _, _ in spine_check.check(path)}

    done = []
    # Order matters: edit the cell and the head BEFORE relocating the block,
    # so every index computed above is still valid when it is used.
    for name, fn in (("S04", fix_s04), ("S05", fix_s05), ("S03", fix_s03)):
        if name not in codes:
            continue
        sp = Spine(path, list(lines))
        if fn(lines, sp):
            done.append(name)
    if not done:
        return "ok", "already conforming", None

    new = "\n".join(lines)
    sp1 = Spine(path, list(lines))

    # ---- the proof ------------------------------------------------------
    if link_bag(new) != before_links:
        return "refused", "link multiset changed", None
    after_h1 = lines[sp1.h1] if sp1.h1 is not None else None
    if after_h1 != before_h1:
        return "refused", "H1 text changed", None
    if row_bag(lines, sp1.table_start) != before_rows:
        return "refused", "table rows changed beyond the identity flip", None
    after_desc = None
    if sp1.table_start is not None:
        cs = split_cells(lines[sp1.table_start])
        after_desc = desc_segment(cs[2] if len(cs) > 2 else "")
    if after_desc != before_desc:
        return "refused", "identity description text changed (would rewrite .anchor)", None
    after_solid = Counter(l for l in lines if l.strip())
    if after_solid != before_solid:
        # the identity row legitimately changes under S04 — allow exactly that
        delta = (after_solid - before_solid) + (before_solid - after_solid)
        if not (len(delta) == 2 and all(d.strip().startswith("|") for d in delta)):
            return "refused", "a non-blank line was lost or added", None

    return "fixed", "+".join(done), new


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="spine fix", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--vault", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
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

    tally = Counter()
    for f in files:
        action, note, new = plan_file(f)
        tally[action] += 1
        if action == "fixed":
            tally["by:" + note] += 1
            if not a.dry_run:
                f.write_text(new, encoding="utf-8")
        if action in ("refused", "skip"):
            try:
                shown = f.relative_to(VAULT)
            except ValueError:
                shown = f
            print(f"  {action.upper():8} {shown} — {note}")

    verb = "would fix" if a.dry_run else "fixed"
    print(f"\nspine fix: {verb} {tally['fixed']} of {len(files)} file(s); "
          f"{tally['ok']} already conforming, {tally['refused']} refused, "
          f"{tally['skip']} skipped")
    for k in sorted(k for k in tally if k.startswith("by:")):
        print(f"    {tally[k]:5}  {k[3:]}")
    return 1 if tally["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
