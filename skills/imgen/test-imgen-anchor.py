#!/usr/bin/env python3
"""test-imgen-anchor.py — the anchor bookkeeping in imgen-gen.py.

Everything here runs against a throwaway tree, so the only untested thing left
in the skill is the network call itself. What is asserted is the set of
properties the IMGEN anchor's `# BRIEF` promises, because those are what every
derived view reads back:

  - a new shoot takes the next free number and gets its namesake page
  - a new prompt group lands ABOVE the older ones (newest-first is load-bearing;
    the gallery and the masthead both trust the order)
  - the prompt is the LAST thing in its group — nothing may come between it and
    the end of the section, or a copy picks up trailing junk
  - the seeds line therefore sits above the images, not under the prompt
  - grids wrap 3-across and pad the short final row
  - a fresh shoot registers in the masthead member zone and at the top of the
    gallery
"""
import importlib.util
import pathlib
import re
import shutil
import sys
import tempfile

spec = importlib.util.spec_from_file_location(
    "imgen_gen", pathlib.Path(__file__).with_name("imgen-gen.py"))
assert spec and spec.loader
ig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ig)

PASS = FAIL = 0


def check(label, got, want):
    global PASS, FAIL
    if got == want:
        print(f"  ok   {label}")
        PASS += 1
    else:
        print(f"  FAIL {label}: got {got!r}, want {want!r}")
        FAIL += 1


def main():
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        ig.ANCHOR = tmp
        (tmp / "IMGEN.md").write_text("# IMGEN\nx\n\n| ^^^ | |\n", encoding="utf-8")
        (tmp / "IMGEN Gallery.md").write_text(
            "# IMGEN Gallery\nx\n\n## [[old]]\n\n![[o.png|500]]\n", encoding="utf-8")

        n, d = ig.new_shoot("Kitchen concepts")
        check("new shoot takes the next number", (n, d.name),
              (1, "IMGEN001 — Kitchen concepts"))
        check("namesake page written", (d / f"{d.name}.md").exists(), True)

        files = []
        for letter in "ABCD":
            f = d / f"IMGEN001-1{letter}.png"
            f.write_bytes(b"x")
            files.append(f)
        ig.record_prompt(d, 1, 1, "Kitchen concepts", "a bright kitchen", files,
                         "model · seed 7")
        ig.add_member_row(d)
        ig.add_to_gallery(d, files[0])
        check("prompt index advances", ig.next_prompt_index(d), 2)

        f2 = d / "IMGEN001-2A.png"
        f2.write_bytes(b"x")
        ig.record_prompt(d, 1, 2, "darker", "make it darker", [f2], "model · seed 9")
        page = (d / f"{d.name}.md").read_text(encoding="utf-8")

        check("newest group is above the older one",
              page.index("IMGEN001-2 —") < page.index("IMGEN001-1 —"), True)

        groups = re.split(r"^## (?=IMGEN)", page, flags=re.M)[1:]
        check("newest group ends with its own prompt",
              groups[0].strip().endswith("make it darker"), True)
        check("older group ends with its own prompt",
              groups[1].strip().endswith("a bright kitchen"), True)
        check("seeds line sits above the images",
              page.index("seed 9") < page.index("IMGEN001-2A.png"), True)

        check("grid wraps 3-across",
              "| ![[IMGEN001-1A.png\\|500]] | ![[IMGEN001-1B.png\\|500]] "
              "| ![[IMGEN001-1C.png\\|500]] |" in page, True)
        check("short final row is padded",
              "| ![[IMGEN001-1D.png\\|500]] |  |  |" in page, True)

        check("shoot registered in the masthead",
              "[[IMGEN001 — Kitchen concepts]]" in
              (tmp / "IMGEN.md").read_text(encoding="utf-8"), True)
        gallery = (tmp / "IMGEN Gallery.md").read_text(encoding="utf-8")
        check("gallery entry goes on top",
              gallery.index("Kitchen concepts") < gallery.index("[[old]]"), True)

        # A second shoot must not disturb the first, and must sort after it.
        n2, d2 = ig.new_shoot("Rooftop")
        check("second shoot takes 002", (n2, d2.name), (2, "IMGEN002 — Rooftop"))
        check("both shoots are seen", [b[0] for b in ig.shoots()], [1, 2])
    finally:
        shutil.rmtree(tmp)

    print()
    print(f"imgen anchor bookkeeping: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
