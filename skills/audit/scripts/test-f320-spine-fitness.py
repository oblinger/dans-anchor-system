#!/usr/bin/env python3
"""test-f320-spine-fitness.py — S10 asks whether this is the RIGHT spine.

Every other code in `spine_check` is CONFORMANCE: given that the page took form
X, is X well-formed. S10 asks the prior question — a page that fronts a folder
with children is a hub, and a breadcrumb says "there are none below me". The
inputs sit on disk beside the file, not in it.

The load-bearing assertion is the SILENT direction. Naive `breadcrumb + has
children` fires on 206 in-scope pages; 29 of those hand-link every child in
prose, so "the children are invisible" is simply false on them and the masthead
S10 asks for would render an EMPTY electric zone (F081 body-mention
suppression). The qualifier is S07's, not a new one: count the members the page
does NOT link and require two. 206 -> 84.

Case 3 is why this file exists. F320's design named a different qualifier —
"links NONE of its children", scoring 37 — and writing the partial case down as
a fixture is what showed it wrong at both tails: `Corp.md` hides 114 of 132 and
links 18, so zero-linked missed the most obvious hub-in-denial in the vault,
while a some-unlinked rule would have fired on a page linking 5 of 6. Counting
hidden members lands both ends against the >=2 floor the design already had.

Usage: python3 test-f320-spine-fitness.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load(name, fname=None):
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(name, HERE / (fname or f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


sc = _load("spine_check")

BREADCRUMB = ":>> [[kmr]] → [[Demo]] → [Hub](hook://p/Hub)"
MASTHEAD = (
    "| -[[Hub]]- | : a hub.<br>→ [[kmr]] → [Hub](hook://p/Hub) |\n"
    "| --- | --- |\n"
)


def build(td, spine, body="", children=("Alpha", "Beta"), name="Hub"):
    """A folder fronted by its own index page, with `children` beside it."""
    root = Path(td)
    (root / ".anchor").write_text("", encoding="utf-8")     # in_anchor -> True
    folder = root / name
    folder.mkdir(exist_ok=True)
    page = folder / f"{name}.md"
    page.write_text(f"{spine}\n\n# {name}\nWhat this is.\n{body}", encoding="utf-8")
    for c in children:
        (folder / f"{c}.md").write_text(f"# {c}\n", encoding="utf-8")
    return page


def codes(page):
    return [c for c, _, _ in sc.check(page)]


# 1 — fires: a breadcrumb over a folder whose children the page never names.
with tempfile.TemporaryDirectory() as td:
    p = build(td, BREADCRUMB)
    check("S10" in codes(p), "breadcrumb + 2 unlinked children fires S10")
    msg = next(m for c, _, m in sc.check(p) if c == "S10")
    check("2 of 2 hidden" in msg, "...and the message carries the hidden count")

# 2 — SILENT: the same page, routing its children by hand. This is the 29-page
#     population, and it is silent for the reason S07/S08 are — the children are
#     not invisible, and the masthead would render nothing.
with tempfile.TemporaryDirectory() as td:
    p = build(td, BREADCRUMB, body="\nSee [[Alpha]] and [[Beta]] for the parts.\n")
    check("S10" not in codes(p), "children linked in prose -> silent")

# 3 — PARTIAL: the floor counts HIDDEN members, not total ones, so the same page
#     answers both tails. Linking one of three still hides two -> fires; linking
#     two of three hides one -> silent, because a page routing all but one of
#     its members by hand is doing the hub's job, not denying it.
with tempfile.TemporaryDirectory() as td:
    p = build(td, BREADCRUMB, body="\nSee [[Alpha]].\n",
              children=("Alpha", "Beta", "Gamma"))
    check("S10" in codes(p), "one of three linked (two hidden) fires")
with tempfile.TemporaryDirectory() as td:
    p = build(td, BREADCRUMB, body="\nSee [[Alpha]] and [[Beta]].\n",
              children=("Alpha", "Beta", "Gamma"))
    check("S10" not in codes(p), "two of three linked (one hidden) is silent")

# 4 — the >=2 floor. One hidden member is not a hub in denial; this is what
#     keeps the code off a page that merely forgot one link.
with tempfile.TemporaryDirectory() as td:
    p = build(td, BREADCRUMB, children=("Alpha",))
    check("S10" not in codes(p), "a lone hidden child does not make a hub")

# 5 — fronts no folder. The page is a leaf beside its siblings; nothing below it.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("", encoding="utf-8")
    (root / "Leaf.md").write_text(f"{BREADCRUMB}\n\n# Leaf\nWhat this is.\n",
                                  encoding="utf-8")
    (root / "Alpha.md").write_text("# Alpha\n", encoding="utf-8")
    (root / "Beta.md").write_text("# Beta\n", encoding="utf-8")
    check("S10" not in codes(root / "Leaf.md"), "a page fronting no folder is silent")

# 6 — already a masthead: this is conformance's business (S07), not fitness's.
#     The two must not double-report the same folder.
with tempfile.TemporaryDirectory() as td:
    p = build(td, MASTHEAD)
    c = codes(p)
    check("S10" not in c, "a masthead page is never an S10")
    check("S07" in c, "...it is S07's, and S07 still sees it")

# 7 — no spine at all is S01's population, explicitly excluded by the
#     measurement (109 of the 315). A page with neither opening must not be
#     charged with wearing the wrong one.
with tempfile.TemporaryDirectory() as td:
    p = build(td, "")
    c = codes(p)
    check("S10" not in c, "a page with no spine is not an S10")
    check("S01" in c, "...it is S01's")

# 8 — outside every anchor: out of scope, per F308 Q3. Same tree, no `.anchor`.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    folder = root / "Hub"
    folder.mkdir()
    (folder / "Hub.md").write_text(f"{BREADCRUMB}\n\n# Hub\nWhat this is.\n",
                                   encoding="utf-8")
    for c in ("Alpha", "Beta"):
        (folder / f"{c}.md").write_text(f"# {c}\n", encoding="utf-8")
    check("S10" not in codes(folder / "Hub.md"), "outside an anchor is out of scope")

# 9 — the suppression question, settled by construction rather than by taste
#     (F320 § Why one command, not two). Every form-specific code is gated on a
#     masthead, so on a breadcrumb page there is nothing for a fitness finding
#     to suppress: the only code that co-occurs vault-wide is S05, and S05 is
#     the H1/orientation gap, which survives the repair unchanged.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("", encoding="utf-8")
    folder = root / "Hub"
    folder.mkdir()
    (folder / "Hub.md").write_text(
        f"{BREADCRUMB}\n\n# Hub\n\nWhat this is.\n", encoding="utf-8")   # blank -> S05
    for c in ("Alpha", "Beta"):
        (folder / f"{c}.md").write_text(f"# {c}\n", encoding="utf-8")
    c = codes(folder / "Hub.md")
    check("S10" in c and "S05" in c, "S10 and S05 co-report; S05 is not suppressed")

print(f"\nF320 spine fitness: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
