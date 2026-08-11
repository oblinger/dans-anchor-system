#!/usr/bin/env python3
"""F319 — the spine rules must reach the agent AT WRITE TIME, and heal the page.

[[Stones]] was created 2026-08-10 with its H1 above the spine and a
breadcrumb-first identity cell, and the write hook said nothing. Four failures
were stacked, each on its own sufficient to keep the writer in the dark:

  1. Warden had never been recompiled, so R-spine-04..08 were not in the
     compiled set at all — `warden mend R-spine-04` said "no such rule" while
     the remediation text sat finished on disk.
  2. Four of five `check::` names were never added to `CHECKERS`, so those
     rules reported `error` — which the write hook deliberately never shows.
  3. The one registered checker graded `warn`, and only `fail` surfaces.
  4. No rule asked the blunt question: is there a spine at all.

This file pins all four shut, plus the floor change they needed. Run:
    python3 test-f319-spine-on-write.py
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _load(name, path):
    ldr = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, ldr)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    ldr.exec_module(mod)
    return mod


ap = _load("ap", HERE / "audit-plan.py")

PASS = 0
FAIL = 0


def chk(m, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {m}")
    else:
        FAIL += 1
        print(f"  FAIL: {m}")


BAD = """\
---
---
# Stones
Where the user's work-in-flight is ranked.

| -[[Stones]]- | → [[kmr]] → [[SYS]] → [Stones](hook://p/Stones)<br>: Stones — The stone feed graph. |
| --- | --- |
| Mechanism | [[DAS Stone]],   |
| ... |  |

## What travels
Body text.
"""


def anchor(page_name="Stones", desc="The stone feed graph.", body=BAD):
    d = Path(tempfile.mkdtemp()) / page_name
    d.mkdir()
    (d / ".anchor").write_text(f"slug: STONE\ntitle: {page_name}\ndescription: {desc}\n")
    (d / f"{page_name}.md").write_text(body)
    (d / "Child.md").write_text("# Child\nA member so the folder is not empty.\n")
    return d, d / f"{page_name}.md"


# ---- A: every check:: name resolves to a registered checker -----------------
print("== A: registration — four of five were defined and never registered ==")
for name in ("spine_above_h1", "identity_cell_description_first",
             "orientation_line_adjoins_h1", "masthead_over_folder_has_marker",
             "marker_has_rows_below", "valid_spine"):
    chk(f"`{name}` is in CHECKERS", name in ap.CHECKERS)
chk("`spine_position` is in FIXERS", "spine_position" in ap.FIXERS)

# ---- B: the grades — only a `fail` reaches the writer -----------------------
print("== B: grade — `warn` is invisible on write, so the fixable ones are `fail` ==")
d, page = anchor()
for rule, want in (("spine_above_h1", "fail"),
                   ("identity_cell_description_first", "fail")):
    st, _ = ap.run_checker(rule, page, d)
    chk(f"`{rule}` grades {want} on a broken page", st == want)
# the two with no safe repair stay advisory until the corpus is clean
st, _ = ap.run_checker("marker_has_rows_below", page, d)
chk("`marker_has_rows_below` is never `fail` (no safe auto-repair)", st != "fail")

# ---- C: valid_spine — the blunt question -----------------------------------
print("== C: valid_spine — is there a spine AT ALL ==")
d2, p2 = anchor(body="# Stones\nNo spine at all, anywhere above this H1.\n\n## Body\nx\n")
st, detail = ap.run_checker("valid_spine", p2, d2)
chk("an entry page with no spine fails", st == "fail")
chk("and the message says what to add",
    "breadcrumb" in detail and "identity row" in detail)
st, _ = ap.run_checker("valid_spine", page, d)
chk("an entry page WITH a spine passes", st == "pass")
# scope: a non-entry page is out of scope while F308 Q6 is open
loose = d / "Child.md"
st, detail = ap.run_checker("valid_spine", loose, d)
chk("a non-entry page is out of scope, not a failure", st == "pass" and "Q6" in detail)

# 46 anchor folders hold both `{slug}.md` and `{title}.md`; one is the anchor
# page and the other a pointer. Which one varies by folder, so the test is
# structural. Telling a three-line pointer to grow a spine is how a live rule
# teaches agents to ignore it.
d5, p5 = anchor(page_name="ESP",
                body="---\ndescription: Slug marker for ESP.\n---\n\n"
                     "# ESP\n(See Anchor [[Espresso]])\n")
st, detail = ap.run_checker("valid_spine", p5, d5)
chk("a pointer stub is not told to grow a spine", st == "pass")
chk("and it is excluded for the RIGHT reason", "pointer stub" in detail)
# ...but has_spine is asked FIRST, so a breadcrumb-only page — which also matches
# the stub shape — passes on its spine, not on a reason that is not true of it.
d6, p6 = anchor(page_name="Leaf",
                body=":>> [[kmr]] → [[SYS]] → [Leaf](hook://p/Leaf)\n")
st, detail = ap.run_checker("valid_spine", p6, d6)
chk("a breadcrumb-only page passes on its SPINE, not as a stub",
    st == "pass" and "pointer stub" not in detail)
# and a page with real content is never a stub, however short
d7, p7 = anchor(page_name="Real",
                body="# Real\nOne real sentence of content that is not a link.\n")
chk("a short page with real content is NOT treated as a stub",
    ap.run_checker("valid_spine", p7, d7)[0] == "fail")

# ---- D: the floor — a rearranging fixer needs an order-FREE floor ----------
print("== D: the never-delete floor, and why `spine_position` needs its own ==")
a, b = "alpha bravo", "bravo alpha"
chk("the ordered floor REJECTS a pure rearrangement (this is the bug)",
    not ap._alnum_subseq(a, b))
chk("the multiset floor ACCEPTS it", ap._alnum_multiset(a, b))
chk("...and still REJECTS a deletion", not ap._alnum_multiset("alpha bravo", "bravo"))
chk("...and still REJECTS an insertion", not ap._alnum_multiset("bravo", "alpha bravo"))
chk("`spine_position` is routed to the multiset floor",
    ap._content_floor_holds("spine_position", a, b))
chk("every OTHER fixer keeps the ordered floor — not weakened globally",
    not ap._content_floor_holds("md_trailing_ws", a, b))
for other in ap.FIXERS:
    if other != "spine_position":
        chk(f"`{other}` is not exempted", other not in ap._REARRANGING_FIXERS)

# ---- E: end to end — the write heals the page ------------------------------
print("== E: end to end — a broken page is repaired, not merely reported ==")
d3, p3 = anchor()
before = p3.read_text()
ok, note = ap.run_fixer("spine_position", p3, d3)
after = p3.read_text()
chk("the fixer reports a change", ok and "S03" in note and "S04" in note)
chk("the masthead now sits above the H1",
    after.index("| -[[Stones]]-") < after.index("# Stones"))
chk("the identity cell now leads with its description",
    "| -[[Stones]]- | : Stones —" in after)
chk("no alphanumeric content was lost or invented",
    ap._alnum_multiset(before, after))
chk("the electric marker row survived the move", "| ... |" in after)
st, _ = ap.run_checker("spine_above_h1", p3, d3)
chk("and the check that fired now passes", st == "pass")

# The fixer must REFUSE — not half-fix — when the sibling `.anchor` disagrees,
# because the write would silently rewrite that second file.
d4, p4 = anchor(desc="a completely different description nobody harvested")
snapshot = p4.read_text()
ok, note = ap.run_fixer("spine_position", p4, d4)
chk("a diverging `.anchor` makes the fixer decline", not ok)
chk("and the page is left byte-identical", p4.read_text() == snapshot)
chk("and the reason is reported, not swallowed", "anchor" in (note or "").lower())

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
