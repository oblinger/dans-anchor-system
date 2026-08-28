#!/usr/bin/env python3
"""T604 — R-markdown-05 must not rewrite ` -- ` inside a LINK TARGET.

A wiki-link target is a filename. Converting a spaced double-hyphen there points
the link at a file that does not exist, and every channel that would normally
surface that is closed: Obsidian renders a dead link as ordinary prose, the fixer
reports success, and the write that triggered the pass was elsewhere in the file.
The rule's own text scopes it to "a definition-list bullet (or prose)"; a
filename was never in scope.

The display half of a piped link IS prose, so it stays in scope — the pipe is the
boundary. These cases pin both sides of that boundary, because a fix that simply
skipped every line holding a link would silently blind the rule across most of
the corpus, which is the worse failure direction.
"""
import importlib.util, pathlib, sys, tempfile

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

PASSED = FAILED = 0


def case(name, src, want_verdict, want_after):
    global PASSED, FAILED
    d = pathlib.Path(tempfile.mkdtemp()) / "t.md"
    d.write_text(src, encoding="utf-8")
    verdict, _ = ap.chk_md_em_dash(d, d.parent, None)
    ap.fix_md_em_dash(d, d.parent, None)
    after = d.read_text(encoding="utf-8")
    ok = verdict == want_verdict and after == want_after
    print(f"  {'ok  ' if ok else 'FAIL'}    {name}")
    if not ok:
        print(f"          verdict {verdict!r} want {want_verdict!r}")
        print(f"          after   {after!r}")
        print(f"          want    {want_after!r}")
    PASSED += ok
    FAILED += not ok


# --- targets are protected -------------------------------------------------
case("bare wiki-link target",
     "See [[Foo -- Bar]] here.", "pass", "See [[Foo -- Bar]] here.")
case("piped wiki-link target",
     "See [[Foo -- Bar|the doc]] here.", "pass", "See [[Foo -- Bar|the doc]] here.")
case("table-escaped pipe (R-markdown-01 form)",
     "| [[Foo -- Bar\\|the doc]] | x |", "pass", "| [[Foo -- Bar\\|the doc]] | x |")
case("embed with width hint",
     "See ![[Foo -- Bar.svg|3000]] here.", "pass", "See ![[Foo -- Bar.svg|3000]] here.")
case("heading-anchored target",
     "See [[Foo -- Bar#Sec|x]] here.", "pass", "See [[Foo -- Bar#Sec|x]] here.")
case("markdown link url",
     "See [text](hook://p/Foo%20--%20Bar) here.", "pass",
     "See [text](hook://p/Foo%20--%20Bar) here.")

# --- prose is STILL in scope: the fix must not blind the rule ---------------
case("plain prose", "one -- two", "fail", "one — two")
case("display half of a piped link is prose",
     "See [[Foo Bar|one -- two]] here.", "fail", "See [[Foo Bar|one — two]] here.")
case("link text of a markdown link is prose",
     "See [one -- two](hook://p/Foo) here.", "fail", "See [one — two](hook://p/Foo) here.")
case("prose on the same line as a protected target",
     "See [[Foo -- Bar]] and one -- two.", "fail",
     "See [[Foo -- Bar]] and one — two.")

# --- interaction with the code masking T375 fixed --------------------------
case("target inside a code span stays put",
     "Write `[[Foo -- Bar]]` like so.", "pass", "Write `[[Foo -- Bar]]` like so.")
case("unpaired-backtick refusal still fires",
     "a ` b -- c", "fail", "a ` b -- c")

# --- idempotence -----------------------------------------------------------
d = pathlib.Path(tempfile.mkdtemp()) / "t.md"
d.write_text("See [[Foo -- Bar|one -- two]] here.", encoding="utf-8")
ap.fix_md_em_dash(d, d.parent, None)
first = d.read_text(encoding="utf-8")
ap.fix_md_em_dash(d, d.parent, None)
ok = d.read_text(encoding="utf-8") == first == "See [[Foo -- Bar|one — two]] here."
print(f"  {'ok  ' if ok else 'FAIL'}    fix is a fixpoint, target and display resolved differently")
PASSED += ok
FAILED += not ok

print(f"\n{PASSED}/{PASSED + FAILED} passed")
sys.exit(1 if FAILED else 0)
