#!/usr/bin/env python3
"""T556 — R-spine-03 and R-spine-09 exempt a notebook narrative, and only that.

Both rules fired on **every `nb append`**. [[A2X]] reported it from A2X013 at
16 cells — 16 identical warnings — and declined to fix it locally, correctly:
restructuring a notebook index is a facet decision, and guessing would put a
masthead on every notebook in the vault. Same cost as T363: a rule that is
correct, unactionable and permanent trains agents to skim the warning tier.

[[DAS Notebook]] had already ruled it, which is why this row is an
implementation and not a decision: *"a notebook folder is NOT a sub-anchor — it
takes no functional `.anchor` and no dispatch table; the `<!-- notebook -->`
marker on the namesake is the machine-readable discriminator."*

**Why the exemption has to be written rather than falling out of the scope**,
asserted in §3 because it is the half that would have been assumed wrong:

  1. `R-spine-09`'s scope reads "an anchor entry page, read from `.anchor`",
     which suggests declaring no `.anchor` keeps a notebook outside it. It does
     not — `entry_names` is a UNION seeded unconditionally with the folder's
     basename, and `.anchor` only ADDS a declared slug/title. Any `X/X.md`
     fronts its folder on basename alone.
  2. `.anchor` is not the facet's to withhold anyway: HookAnchor's scanner
     auto-mints a zero-byte one in every namesake folder on its 10-minute
     rescan, and the live A2X013 folder duly has one.

So the facet's "no" survives only in the marker, and the checker has to read it.

§5 pins both checkers against the ruleset text — the T552 lesson, that a rule
relaxed in code and not in its prose has one uncheckable copy that has drifted.

Run: python3 test-t556-notebook-narrative-exempt.py
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

_sspec = importlib.util.spec_from_file_location("sp", _HERE / "spine.py")
sp = importlib.util.module_from_spec(_sspec)
sys.modules["sp"] = sp
_sspec.loader.exec_module(sp)

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-spine.md"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


# The shape `nb` writes: no spine above the H1, marker directly under it, one
# H2 per cell each linking that cell's own doc.
MARKED = """---
description: "Notebook — ZZ013 - A Notebook. Appended by nb ([[DAS Notebook]])."
---

# ZZ013 - A Notebook
<!-- notebook -->

## ZZ013-001 A cell

[[ZZ013-001 A cell]] — what it showed.
"""

UNMARKED = MARKED.replace("<!-- notebook -->\n", "")

FOLDER = "ZZ013 - A Notebook"


def build(root, text, *, folder_name=FOLDER, index_name=None,
          with_anchor=True, extra_member=True):
    folder = root / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    if with_anchor:
        # HookAnchor's scanner mints this whether the facet wants it or not.
        (folder / ".anchor").write_text("")
    f = folder / f"{index_name or folder_name}.md"
    f.write_text(text)
    if extra_member:
        (folder / "ZZ013-001 A cell.md").write_text("# ZZ013-001 A cell\nbody\n")
    return f


def r03(text, **kw):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        return ap.chk_summary_present_iff_complex(build(root, text, **kw), root, [])[0]


def r09(text, **kw):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        return ap.chk_valid_spine(build(root, text, **kw), root, [])[0]


print("1. Both rules exempt a marked notebook narrative")
check("R-spine-03 passes a marked narrative", r03(MARKED), "pass")
check("R-spine-09 passes a marked narrative", r09(MARKED), "pass")

print("2. ...and the SAME file without the marker still fails both")
# This is the assertion that makes §1 mean something: the fixture is a genuine
# violation of both rules, so a pass there is the exemption firing and not a
# fixture that was never in scope.
check("R-spine-03 fails an unmarked namesake", r03(UNMARKED), "fail")
check("R-spine-09 fails an unmarked namesake", r09(UNMARKED), "fail")

print("3. The exemption is load-bearing — the scope alone does NOT excuse it")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    with_a = build(root, MARKED, with_anchor=True)
    check("a namesake fronts its folder WITH an .anchor",
          sp.Spine(with_a).fronts_folder, True)
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    without_a = build(root, MARKED, with_anchor=False)
    check("...and equally WITHOUT one — entry_names is seeded with the basename",
          sp.Spine(without_a).fronts_folder, True)
    check("the narrative genuinely has no spine to be graded",
          sp.Spine(without_a).has_spine, False)
    check("R-spine-09 still exempts it with no .anchor present",
          r09(MARKED, with_anchor=False), "pass")

print("4. `_is_notebook_namesake` is narrow")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    good = build(root, MARKED)
    check("namesake + marker", ap._is_notebook_namesake(good), True)
    bad_name = build(root, MARKED, index_name="Not The Namesake")
    check("marker but not the namesake", ap._is_notebook_namesake(bad_name), False)
    bad_marker = build(root, UNMARKED)
    check("namesake but no marker", ap._is_notebook_namesake(bad_marker), False)
    check("a file that does not exist",
          ap._is_notebook_namesake(root / "nope" / "nope.md"), False)
# The live narrowness case: F334's own feature doc QUOTES the marker, and sits
# in `Tink Features/`, so it is not a namesake. A predicate keyed on the marker
# alone would exempt the doc that documents the marker.
F334 = (Path.home() / "ob/kmr/SYS/Staff/Tink/Tink Design/TINK Features"
        / "Tink334 - Notebook facet - append-only experiment notebooks.md")
if F334.is_file():
    check("F334's own doc quotes the marker and is still refused",
          ap._is_notebook_namesake(F334), False)

print("5. The ruleset text says what the checkers do (the T552 lesson)")
text = RULESET.read_text(encoding="utf-8")
for rule_id, extra in (("R-spine-03", "state:backlog"), ("R-spine-09", None)):
    m = re.search(rf"### RULE {rule_id}\b.*?(?=\n### RULE )", text, re.S)
    check(f"{rule_id} is present", bool(m), True)
    if not m:
        continue
    body = m.group(0)
    check(f"{rule_id} names the notebook marker as the key",
          "<!-- notebook -->" in body, True)
    check(f"{rule_id} names DAS Notebook as the facet that ruled it",
          "DAS Notebook" in body, True)
    check(f"{rule_id} cites T556", "T556" in body, True)
    if extra:
        check(f"{rule_id} still names its FIRST exemption's key",
              extra in body, True)
# R-spine-03 came with a residual for each exemption; the notebook one is the
# unlinked cell doc, and it is stated rather than left to be discovered.
m03 = re.search(r"### RULE R-spine-03\b.*?(?=\n### RULE )", text, re.S)
check("R-spine-03 states the notebook exemption's residual",
      bool(m03) and "cell doc" in m03.group(0), True)

print("6. The three live notebooks pass both rules")
LIVE = Path.home() / "ob/kmr/SV/ww/svar-docs/alg2-experimental/A2X Notebook"
if LIVE.is_dir():
    seen = 0
    for folder in sorted(LIVE.iterdir()):
        f = folder / f"{folder.name}.md"
        if not f.is_file() or "<!-- notebook" not in f.read_text(encoding="utf-8")[:2000]:
            continue
        seen += 1
        check(f"{folder.name} — R-spine-03",
              ap.chk_summary_present_iff_complex(f, LIVE.parent, [])[0], "pass")
        check(f"{folder.name} — R-spine-09",
              ap.chk_valid_spine(f, LIVE.parent, [])[0], "pass")
    check("live notebooks were actually found", seen > 0, True)

print()
if FAILURES:
    print(f"test-t556-notebook-narrative-exempt: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t556-notebook-narrative-exempt: all checks pass")
