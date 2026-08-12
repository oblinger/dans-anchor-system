#!/usr/bin/env python3
"""spine fix — the three mechanical spine rearrangements, self-verified per file.

Reached as `spine fix <paths> [--dry-run]` or `spine fix --vault [--write]`.
**`--vault` reports and does not write unless `--write` is given** (T231); a
path argument writes unless `--dry-run` is given. The two defaults differ on
purpose — one file is inspectable, 1,296 are not.

Fixes exactly the codes
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
  * no non-blank line is lost,
  * and the sibling `.anchor` ALREADY AGREES with that description. Leaving the
    description alone is not enough: the harvest fires on the touch, not on the
    edit, so a page whose `.anchor` already disagrees has its `.anchor`
    rewritten by the mere act of saving it — and reverting the page does not
    undo it, because the page still says something different. That second file
    would change while every assertion above passed.

On any mismatch the file is left alone and the reason is printed. Three
measurements during F308 were wrong from regex-splitting table cells, so cells
are split by `spine.split_cells`, a character scanner — never a regex.

Discipline: [[DAS spine]]. Rules: [[R-spine]]. Roadmap: TINK319 Spine Agenda.
"""

import re
import sys
from collections import Counter
from pathlib import Path

from spine import (Spine, split_cells, expand, walk, entry_names,
                   is_description_home, VAULT)

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


_ANCHOR_DESC = re.compile(r"^\s*description\s*:\s*(.*?)\s*$")


def _unquote(v: str) -> str:
    """A YAML scalar, read the way a YAML parser reads it.

    Only a value that opens AND closes with the same quote is quoted; then its
    `\\"` and `\\\\` escapes are real escapes. Naive `.strip('"')` is what a
    first draft does, and it is wrong in both directions here: it ate the
    closing quote of `… sections A, B, C in order"` (an UNquoted value whose
    text merely ends in a quotation mark) and left `Personal \\"Quick\\"
    Projects` half-escaped. Both then read as divergences that do not exist.
    """
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        if v[0] == '"':
            return inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner.replace("''", "'")
    return v


def anchor_desc(folder: Path) -> str | None:
    """The sibling `.anchor`'s declared description, or None if it declares
    none (536 of them do vault-wide; the rest have nothing to diverge from)."""
    a = folder / ".anchor"
    if not a.is_file():
        return None
    try:
        for ln in a.read_text(encoding="utf-8", errors="replace").split("\n"):
            m = _ANCHOR_DESC.match(ln)
            if m:
                return _unquote(m.group(1)) or None
    except OSError:
        return None
    return None


def norm(s: str) -> str:
    """Compare descriptions on their meaning, not their punctuation.

    Three folds, each because the difference it hides cannot carry information:

    * **whitespace** — the harvest round-trips text through a table cell, so a
      run of spaces on one side and a single space on the other is not a
      divergence, and treating it as one refuses pages that are in fact in sync.
    * **a trailing full stop** — some descriptions end in a period and some do
      not, and no reader learns anything from which. Measured 2026-08-12: of the
      30 divergences the guard reported, **four differed by nothing else** —
      `Roots`, `SV Features`, `_` and `DKT System Design` — so a fifth of the
      list was punctuation the operator had to read and dismiss one page at a
      time. A guard that refuses on nothing teaches its operator to wave
      refusals through, which is how the one real divergence gets written.
    * **the case of the first character only** — sentence-casing an opening word
      is a house style, not a claim. Deliberately *only* the first character:
      folding case throughout would hide `DKT` against `dkt`, and a slug's case
      is meaning.
    """
    t = re.sub(r"\s+", " ", s).strip().rstrip(".")
    return t[:1].lower() + t[1:]


# What the harvest ACTUALLY stores, mirrored from HookAnchor rather than
# guessed. The first draft of this check compared the raw cell text and refused
# 107 files where the true count of at-risk pages is 55 — the two normalisations
# below are the whole of that gap, and both were read out of the Rust before
# being written here (`sections.rs`, `extract_dispatch_descriptions` +
# `strip_own_name_prefixes`). A mover that refuses twice as often as it must
# teaches its operator to wave refusals through, so over-refusing is not the
# safe direction it looks like.
OWN_NAME_DELIM = " — "                       # space EM-DASH space


def _unescape_pipes(s: str) -> str:
    """`\\|` inside a cell is emit-side escaping; the store holds the raw `|`."""
    return s.replace("\\|", "|")


def _strip_own_name_prefixes(raw: str, folder: Path, stem: str) -> str:
    """Drop the leading `{own name} — ` the masthead prepends.

    `build_desc_with_name` puts the anchor's display name in front of its own
    description for the `: ` line, and the harvest strips it symmetrically, so
    `MUX.md` reading `MuxUX — Tauri GUI overlay…` against an `.anchor` reading
    `Tauri GUI overlay…` is a round-trip, not drift. Only names this script can
    read locally are stripped — folder, stem, `slug:`, `title:`. HookAnchor also
    strips ALIASES, which need the command store; a page whose prefix is a prior
    name therefore still refuses here, which is the correct direction for the
    one case that stays uncertain.
    """
    names = {folder.name, stem} | entry_names(folder)
    s = raw.strip()
    while OWN_NAME_DELIM in s:
        prefix, rest = s.split(OWN_NAME_DELIM, 1)
        if prefix.strip() in names:
            s = rest.strip()
        else:
            break
    return s


def harvested_desc(page_desc: str | None, folder: Path, stem: str) -> str | None:
    """What HookAnchor would write into `.anchor` from this page's cell.

    None means it would write NOTHING — the harvest is gated on
    `if !text.is_empty()`, so a cell carrying a bare `: ` with no text is not a
    description that overwrites anything. 40-odd `{slug} Track` / `{slug}
    Features` pages are in exactly that state and the first draft refused every
    one of them.
    """
    if page_desc is None:
        return None
    text = _strip_own_name_prefixes(_unescape_pipes(page_desc), folder, stem)
    return text or None


def anchor_would_change(path: Path, page_desc: str | None) -> str | None:
    """The reason writing this page would also rewrite its sibling `.anchor`,
    or None if it would not.

    Bi-directional desc-sync makes the PAGE the harvest authority, so touching
    it propagates its identity-cell description into `{folder}/.anchor`. That
    is by design and is NOT revertible while the two disagree: restoring the
    `.anchor` from git and waiting for the rebuild reproduces the overwrite
    (measured on `examples/HBR/.anchor`, F319 M1 probes). 55 pages vault-wide
    are in that state today. They are a deliberate reconciliation, not a
    side effect of a spine sweep, so this script refuses them.
    """
    declared = anchor_desc(path.parent)
    if declared is None:
        return None                      # nothing on the `.anchor` to overwrite
    would_write = harvested_desc(page_desc, path.parent, path.stem)
    if would_write is None:
        return None                      # the harvest writes nothing at all
    if norm(declared) == norm(would_write):
        return None
    # Two very different things end up here, and lumping them makes the refusal
    # list unactionable. FOSSIL: the `.anchor` carries an own-name prefix the
    # harvest strips symmetrically (`Hook Anchor — universal command launcher`
    # vs `universal command launcher`), so the touch would only heal a
    # round-trip artefact — HookAnchor's own doc calls this healing by design.
    # DIVERGENCE: the two texts genuinely say different things, and one of them
    # is about to win silently. 9 fossils and 50 divergences vault-wide.
    kind = ("fossil own-name prefix on the .anchor — the touch would heal it"
            if norm(_strip_own_name_prefixes(declared, path.parent, path.stem))
            == norm(would_write)
            else "sibling .anchor would be rewritten by the touch")
    # NOT truncated, deliberately. F319 makes "resolve the divergences
    # deliberately rather than letting the sweep absorb them" a prerequisite of
    # the sweep, and both texts were clipped to 48 characters — long enough to
    # see that two descriptions differ, never long enough to see HOW, so on
    # 2026-08-12 the prerequisite could not be performed from the output that
    # names it. Most of the clipped pairs diverge past character 48; several are
    # identical for their whole visible prefix and read as false alarms. The
    # refusal list is 37 lines against 8,043 files scanned, so nothing is being
    # protected by the clip.
    return (f"{kind} (.anchor says {declared!r}, harvest would write "
            f"{would_write!r})")


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
    # The one assertion that reads a file OTHER than the page. Only the page
    # whose description HOME is the `.anchor` can rewrite it — which is the
    # slug-keyed question `is_description_home` asks, NOT the union
    # `fronts_folder` answers. Gating on the union refused three marker stubs
    # (`Atticus.md`, `Munger.md`, `Areas of Thought.md`) that HookAnchor's own
    # T051 routing makes incapable of touching an `.anchor` at all.
    if is_description_home(path):
        why = anchor_would_change(path, before_desc)
        if why:
            return "refused", why, None

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
    ap.add_argument("--vault", action="store_true",
                    help="every markdown file in the vault — REPORTS ONLY unless "
                         "--write is also given")
    ap.add_argument("--write", action="store_true",
                    help="required to make --vault actually write; ignored for "
                         "path arguments, which write by default")
    ap.add_argument("--dry-run", action="store_true",
                    help="report without writing (the default for --vault)")
    a = ap.parse_args(argv)

    # T231 — `--vault` reports unless told otherwise; a path writes unless told
    # otherwise. The blast radii are three orders of magnitude apart and the
    # safe invocation should be the one you get by typing less.
    #
    # This is not hypothetical caution. On 2026-08-11 an agent reading F319 —
    # which calls the vault measurement "the dry run" throughout — ran the
    # command that prose names and wrote **1,296 files**, the single action M5
    # is gated on. The old signal that it had written rather than reported was
    # one word in the summary line (`fixed` versus `would fix`), which is easy
    # to read past, and the second-order damage was worse than the writes:
    # HookAnchor's daemon woke on every touched page and re-harvested 16
    # `.anchor` descriptions, content this script's own guard refuses to touch.
    write = a.write and not a.dry_run if a.vault else not a.dry_run
    if a.vault and a.write and a.dry_run:
        ap.error("--write and --dry-run contradict each other")

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
            if write:
                f.write_text(new, encoding="utf-8")
        if action in ("refused", "skip"):
            try:
                shown = f.relative_to(VAULT)
            except ValueError:
                shown = f
            print(f"  {action.upper():8} {shown} — {note}")

    verb = "fixed" if write else "would fix"
    if a.vault and not write:
        print("\nspine fix: --vault REPORTS ONLY. Re-run with --write to apply.")
    print(f"\nspine fix: {verb} {tally['fixed']} of {len(files)} file(s); "
          f"{tally['ok']} already conforming, {tally['refused']} refused, "
          f"{tally['skip']} skipped")
    for k in sorted(k for k in tally if k.startswith("by:")):
        print(f"    {tally[k]:5}  {k[3:]}")
    return 1 if tally["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
