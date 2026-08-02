#!/usr/bin/env python3
"""T103 class (b) — "a table row" is one definition, and a table is a block.

Five sites in `audit-plan.py` each decided what a table row is, and they disagreed
in both directions. Every lead below was REPRODUCED BY EXECUTION before anything
was touched — T103's own instruction, because the T102 scan that produced these
leads also named ten defs that do not exist in the file and one verdict that was a
stateful-registry ghost.

  b1   `chk_breadcrumb_row` (lstrip) and `chk_design_row_iff_folder` (`^\\|`) reach
       OPPOSITE verdicts about the same two-space-indented table — the shape
       `ATT F004` uses for a symlink table continuing a list item.
  b1'  the lstrip form reads a four-space INDENTED CODE BLOCK as the document's
       first table row (`DKT Standard.md` § kv-table) and fails the page for a
       malformed masthead while the real breadcrumb table sits untouched below.
  b2   `chk_tests_table_present` took `rows[2:]` over EVERY pipe-line in its
       section, so a second table's header and separator were judged coverage
       rows missing a wiki-link.
  b3   `_proposed_tests_rows` identified the separator LEXICALLY, so a legitimate
       all-placeholder row `| - | - | - |` was dropped as a separator AND took the
       real row above it out (a separator's predecessor is treated as a header).
       Silent suppression — the worse half.
  b4   `_disclosure_summary` allowed a bold wrapper only on the `[[#…]]` form while
       `_disclosure_descriptive` allowed it on all three, so `| **[[Alpha]]** |`
       was judged to have NO summary and a DESCRIPTIVE one in the same pass.

The bound is CommonMark's `{0,3}`, deliberately NOT the `[ \\t]*` that `_FENCE_RE`
settled on. Both approximate a block parser this file does not have; the trade runs
opposite ways. A fence's contents are literal either way, so over-recognising costs
nothing there. A table row over-recognised becomes live structure that checkers
then demand the author repair — which is exactly b1'.

Measured at each rule's real `where::` over the whole vault: 155,684 verdicts,
**2 status moves, both fail->pass**, both false findings on ASCII art read as a
masthead (`Log/Idea/2006-00 Nanofabrication`, `Topic/Doc/DocApplescript`). A third
apparent move on `Topic/Career/Career.md` was R-progressive-05's registry state,
not this change: re-run with an identical baseline `~/.warden/disclosure.json` on
both sides, 36,870 R-progressive verdicts moved zero.

    python3 test-t103-table-row.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def doc(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


print("One definition of a table row — CommonMark's three-space bound")

check("column zero is a row", ap._is_table_row("| a | b |"), True)
check("three spaces is still a row (a list item's continuation)",
      ap._is_table_row("   | a | b |"), True)
check("four spaces is an indented code block, not a row",
      ap._is_table_row("    | a | b |"), False)
check("a tab indents four columns, so it is not a row either",
      ap._is_table_row("\t| a | b |"), False)
check("prose containing a pipe is not a row", ap._is_table_row("x | y"), False)
# `_row_cells` is the file's table primitive and must answer to the same predicate,
# or a line can be "not a row" to one caller and splittable by another.
check("_row_cells agrees — it splits a 3-indent row",
      ap._row_cells("   | a | b |"), ["a", "b"])
check("...and refuses a 4-indent code line",
      ap._row_cells("    | a | b |"), [])

print("\nb1 — the same indented table, two checkers, one verdict now")

a = ROOT / "Harbor"
(a / "Harbor Design").mkdir(parents=True)
(a / ".anchor").write_text("", encoding="utf-8")
page = doc("Harbor/Harbor.md",
           "# Harbor\nOrientation.\n\n- a bullet\n\n"
           "  | -[[Harbor]]- | → [[kmr]] → [Harbor](hook://p/Harbor) |\n"
           "  | --- | --- |\n  | Design | [[Harbor Design\\|Design]] |\n")
check("chk_breadcrumb_row sees the 2-indent masthead",
      ap.chk_breadcrumb_row(page, a, []), ("pass", ""))
check("chk_design_row_iff_folder sees the SAME table (was: 'no Design row')",
      ap.chk_design_row_iff_folder(page, a, []), ("pass", "both present"))

print("\nb1' — a fenceless indented code sample is not the document's masthead")

b = ROOT / "Bay"
b.mkdir()
(b / ".anchor").write_text("", encoding="utf-8")
page2 = doc("Bay/Bay.md",
            "# Bay\nOrientation.\n\n### kv-table\n\n"
            "    | Field | Value |\n    |-------|-------|\n    | Status | open |\n\n"
            "| -[[Bay]]- | → [[kmr]] → [Bay](hook://p/Bay) |\n| --- | --- |\n")
check("the real breadcrumb below the sample is the first ROW",
      ap.chk_breadcrumb_row(page2, b, []), ("pass", ""))

print("\nb2/b3 — a table is a block: header, optional separator, data")

blocks = ap._table_blocks(["| a |", "|---|", "| 1 |", "", "text", "| b |", "| 2 |"])
check("two tables separated by prose are two blocks", len(blocks), 2)
check("a block with a separator drops header AND separator",
      ap._table_data_rows(blocks[0]), ["| 1 |"])
check("a block without one drops only the header",
      ap._table_data_rows(blocks[1]), ["| 2 |"])
# `| | |` has no dash: an empty row is not a delimiter row.
check("an empty row is not a separator", bool(ap._TABLE_SEP_RE.match("| | |")), False)
check("...but `|---|---|` is", bool(ap._TABLE_SEP_RE.match("|---|---|")), True)

page3 = doc("tests.md",
            "# T\nOrientation.\n\n## Tests\n\n"
            "| Kind | Where |\n|---|---|\n| [[unit]] | tests/ |\n\n"
            "| Note | Detail |\n|---|---|\n| [[x]] | y |\n\n## Overview\n\nBody.\n")
check("a second table in ## Tests is not judged as coverage rows",
      ap.chk_tests_table_present(page3, ROOT, []), ("pass", ""))

rows = ap._proposed_tests_rows(
    ("# T\n\n## Proposed Tests\n\n"
     "| Kind | Target | Spec |\n|---|---|---|\n"
     "| [[unit]] | parser | [[S1]] |\n| - | - | - |\n").splitlines())
check("an all-placeholder row no longer eats the real row above it",
      rows, ["| [[unit]] | parser | [[S1]] |", "| - | - | - |"])
# The placeholder row is data now, so the Spec-cell rule can finally see it.
check("...and the empty-Spec rule reaches it",
      ap.chk_proposed_tests_rows_have_spec(
          doc("pt.md", "# T\n\n## Proposed Tests\n\n"
                       "| Kind | Target | Spec |\n|---|---|---|\n"
                       "| [[unit]] | parser | [[S1]] |\n| - | - | - |\n"), ROOT, [])[0],
      "fail")

print("\nb4 — bold is presentation; it applies to every summary-row form")

page4 = doc("bold.md", "# B\nOrientation.\n\n"
                       "| **[[Alpha]]** | the first unit, described here |\n"
                       "| **[[Beta]]** | the second unit, described here |\n")
check("a bold-lead masthead HAS a summary", ap._disclosure_summary(page4)[0], True)
check("...and the two functions agree it is descriptive",
      ap._disclosure_descriptive(page4), True)
plain = doc("plain.md", "# P\nOrientation.\n\n"
                        "| [[Alpha]] | the first unit, described here |\n")
check("the unbolded form is unchanged", ap._disclosure_summary(plain)[0], True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
