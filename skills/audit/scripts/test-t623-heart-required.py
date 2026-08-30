#!/usr/bin/env python3
"""test-t623-heart-required.py — R-spine-12 / H02 (Dan, 2026-08-29): a long
authored page has a heart under its one-liner. Presence only; genre-gated;
never fires beside H01."""
import importlib.util, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("sc", HERE / "spine_check.py")
sc = importlib.util.module_from_spec(spec); sys.modules["sc"] = sc; spec.loader.exec_module(sc)
PASS = FAIL = 0
def check(cond, label):
    global PASS, FAIL
    if cond: PASS += 1; print("PASS ", label)
    else: FAIL += 1; print("FAIL ", label)
PROSE = ("Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor. " * 12 + "\n\n") * 8   # ~800 words
HEAD = ":>> [[kmr]] → [Page](hook://p/Page) \n# Page\nA page that is one thing.\n\n"
TABLE = "| A | B |\n|---|---|\n| 1 | x |\n| 2 | y |\n| 3 | z |\n| 4 | w |\n\n"
DEFL = "- **First** — one.\n- **Second** — two.\n- **Third** — three.\n\n"
TOC = "| Table of Contents |  |\n|---|---|\n| [[#One]] |  |\n| [[#Two]] |  |\n| [[#Three]] |  |\n| [[#Four]] |  |\n\n"
def codes(text, name="Page.md", sub=""):
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "FIX" / sub if sub else Path(td) / "FIX"
        d.mkdir(parents=True, exist_ok=True)
        (Path(td) / "FIX" / ".anchor").write_text("slug: FIX\n")
        f = d / name; f.write_text(text, encoding="utf-8")
        return [c for c, _, _ in sc.check(f)]
check("H02" in codes(HEAD + PROSE), "long prose page with nothing under the one-liner fires H02")
check("H02" not in codes(HEAD + TABLE + PROSE), "a fact-card table under the one-liner satisfies it")
check("H02" not in codes(HEAD + DEFL + PROSE), "a definition list under the one-liner satisfies it")
check("H02" not in codes(HEAD + TOC + PROSE), "a TOC under the one-liner satisfies it (at warn)")
check("H02" not in codes(HEAD + "![[fig.svg]]\n\n" + PROSE), "a figure satisfies it")
check("H02" not in codes(HEAD + PROSE[:400]), "a short page never fires")
check("H02" not in codes(HEAD + PROSE, name="FIX Inbox.md"), "an inbox is genre-exempt")
check("H02" not in codes(HEAD + PROSE, name="FIX Backlog.md"), "a backlog is genre-exempt")
buried = codes(HEAD + PROSE[:300] + "\n\n" + PROSE[:300] + "\n\n" + TABLE + PROSE)
check("H01" in buried and "H02" not in buried, "a buried table is H01's finding and suppresses H02")
print(f"\n{PASS} passed, {FAIL} failed"); sys.exit(1 if FAIL else 0)
