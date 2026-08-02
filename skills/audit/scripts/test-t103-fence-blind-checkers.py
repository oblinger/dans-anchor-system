#!/usr/bin/env python3
"""T103 class (a) — seven checkers read raw text and judged fenced examples as live.

Sibling of `test-f296-fence-blind-fixers.py`: same disease, on the CHECK path rather
than the FIX path. Each of these read `_read(f)` directly, so a structure shown as a
fenced EXAMPLE was indistinguishable from a live one. The docs most likely to carry
such an example are precisely the docs these rules govern — a page explaining what a
masthead looks like shows a masthead; a page explaining why skill anchors carry no
Track row shows a Track row.

The worst shape is `chk_no_dispatch_table`, whose remediation text is "remove it":
on a fenced sample it tells the author to delete their own documentation.

**Measured, and the honest result is zero.** Back-to-back over the vault at each
rule's own `where::` — 155,684 verdicts, **0 status moves**. Every one of these
defects is real and reproduces on demand (below), but none fires on the corpus today,
because each rule's `where::` is narrow enough to miss the docs that carry fenced
structure. The latent exposure is not zero and not small: **17 vault docs carry a
fenced masthead row, 79 carry a fenced table row**, 8 a fenced dated link, and 2 each
a fenced Design row, Track row, and `## Questions`. So this is a trap one scope
widening away from firing, not a live fault — recorded that way rather than dressed
up as findings removed.

    python3 test-t103-fence-blind-checkers.py
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
FENCE = "```markdown\n"


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


def anchor(name, dot=""):
    d = ROOT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(dot, encoding="utf-8")
    return d


print("A fenced example is never live structure")

# The fenced sample must NOT itself look like a valid breadcrumb, or the checker
# would pass for the wrong reason — matching the SAMPLE and never reaching the real
# masthead below it. That is how the first cut of this fixture failed to reproduce.
a1 = anchor("Doc1")
p1 = doc("Doc1/Doc1.md",
         "# Doc1\nHow to write a masthead.\n\n" + FENCE
         + "| Field | Value |\n| --- | --- |\n```\n\n"
           "| -[[Doc1]]- | → [[kmr]] → [Doc1](hook://p/Doc1) |\n| --- | --- |\n")
check("chk_breadcrumb_row reaches the REAL masthead below the sample",
      ap.chk_breadcrumb_row(p1, a1, []), ("pass", ""))

MAST = "| -[[Sample]]- | → [[kmr]] → [Sample](hook://p/Sample) |\n| --- | --- |\n"
p2 = doc("story.md", "# Story\nA story file, correctly tableless.\n\n" + FENCE + MAST + "```\n")
# This rule says "remove it" — the one place a false positive damages the document.
check("chk_no_dispatch_table does not tell the author to delete their example",
      ap.chk_no_dispatch_table(p2, ROOT, []), ("pass", "no dispatch table"))

a3 = anchor("Doc3")
p3 = doc("Doc3/Doc3.md", "# Doc3\nExplains the Design row.\n\n" + FENCE
         + "| Design | [[X Design|Design]] |\n```\n")
check("a fenced Design row is not a Design row",
      ap.chk_design_row_iff_folder(p3, a3, []), ("pass", "neither (no design facet)"))

p4 = doc("log.md", "# Log\nHow a log dispatch reads.\n\n" + FENCE
         + "| [[2024-01-01 old]] | [[2026-01-01 new]] |\n```\n\n"
           "| [[2026-08-01 newest]] |\n| [[2026-07-01 older]] |\n")
check("fenced dated links do not interleave with the live ordering",
      ap.chk_log_dispatch_newest_first(p4, ROOT, []), ("pass", ""))

p5 = doc("q.md", "# Q\nExplains the Questions section.\n\n" + FENCE
         + "## Questions\n\n- a free-text bullet with no handle\n```\n")
check("a fenced `## Questions` does not open the live section",
      ap.chk_queries_catchall_links(p5, ROOT, []), ("pass", ""))

a6 = anchor("HBR")
p6 = doc("HBR/HBR PRD.md", "# HBR PRD\nShows a masthead, then carries one.\n\n" + FENCE
         + "| Related | [[Other]] |\n```\n\n"
           "| -[[HBR PRD]]- | → [[kmr]] |\n| Stories | [[HBR Stories]] |\n")
# "The dispatch table" is the first contiguous run of table rows; a fenced sample
# above it used to claim that title and the real Stories row was never inspected.
check("the first FENCED table is not 'the dispatch table'",
      ap.chk_dispatch_table_stories_row(p6, a6, []), ("pass", ""))

a7 = anchor("Skl", "traits: [skill]\n")
p7 = doc("Skl/Skl.md", "# Skl\nWhy skill anchors carry no Track row.\n\n" + FENCE
         + "| Track | [[Skl Track]] |\n```\n")
check("a fenced Track row is not a Track row",
      ap.chk_no_track_row_if_ecosystem_traits(p7, a7, []), ("pass", ""))

print("\n...and the live structure is still seen — the fix must not blind them")

a8 = anchor("Skl2", "traits: [skill]\n")
p8 = doc("Skl2/Skl2.md", "# Skl2\nOrientation.\n\n| Track | [[Skl2 Track]] |\n")
check("a REAL Track row on an ecosystem anchor still fails",
      ap.chk_no_track_row_if_ecosystem_traits(p8, a8, []),
      ("fail", "Track row present on ecosystem anchor"))
p9 = doc("story2.md", "# Story2\nOrientation.\n\n" + MAST)
check("a REAL masthead on a story file still fails",
      ap.chk_no_dispatch_table(p9, ROOT, [])[0], "fail")
a10 = anchor("Doc10")
(a10 / "Doc10 Design").mkdir()
p10 = doc("Doc10/Doc10.md", "# Doc10\nOrientation.\n\n| Design | [[Doc10 Design|Design]] |\n")
check("a REAL Design row still pairs with its folder",
      ap.chk_design_row_iff_folder(p10, a10, []), ("pass", "both present"))

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
