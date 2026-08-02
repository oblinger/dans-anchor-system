#!/usr/bin/env python3
"""test-imgen-anchor.py — the anchor bookkeeping in imgen-gen.py.

Everything here runs against a throwaway tree, so the only untested thing left
in the skill is the network call itself. What is asserted is the page shape
SKILL.md § The roll page promises, because that shape is what every derived view
and every later hand-edit reads back:

  - a new roll takes the next free number and gets its namesake page
  - that page is a REGULAR file — `:>>` breadcrumb, never a dispatch table
  - `## Next render` holds exactly one pending operation: an `#### {command}`
    H4 followed by its prompt
  - `## Batch {n}` sections sit newest-first, each one heading → image grid →
    the `####` command and prompt that produced it
  - a rewritten batch keeps its hand-authored subtitle and lead commentary,
    which are unrecoverable if regenerated away
  - grids wrap 3-across and pad the short final row
  - a fresh roll registers in the masthead member zone and at the top of the
    gallery

Rewritten 2026-08-02: the suite still spoke the skill's pre-redesign vocabulary
(`new_shoot` / `record_prompt` / prompt-groups) and had been failing at import
since the roll/batch redesign landed.

    python3 test-imgen-anchor.py
"""
import importlib.util
import pathlib
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


def images(roll_dir, n, letters):
    """Create batch-n image files and return them in order."""
    out = []
    for letter in letters:
        f = roll_dir / f"IMGEN001-{n}{letter}.png"
        f.write_bytes(b"x")
        out.append(f)
    return out


def main():
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        ig.ANCHOR = tmp
        (tmp / "IMGEN.md").write_text("# IMGEN\nx\n\n| ^^^ | |\n", encoding="utf-8")
        (tmp / "IMGEN Gallery.md").write_text(
            "# IMGEN Gallery\nx\n\n## [[old]]\n\n![[o.png|500]]\n", encoding="utf-8")

        n, d = ig.new_roll("Kitchen concepts", "a bright kitchen",
                           about="Exploring a warm morning kitchen.")
        check("a new roll takes the next number", (n, d.name),
              (1, "IMGEN001 — Kitchen concepts"))
        check("namesake page written", ig.roll_page(d).exists(), True)

        page = ig.roll_page(d).read_text(encoding="utf-8")
        # A roll page is a regular file, so it heads with a breadcrumb. A
        # dispatch table here would misidentify it as an anchor page.
        check("the page heads with a `:>>` breadcrumb, not a dispatch table",
              page.startswith(":>>") and "| ^^^ |" not in page, True)
        check("the about line replaces the bare title when given",
              "Exploring a warm morning kitchen." in page, True)
        check("Next render carries the seeded prompt",
              "## Next render" in page and "a bright kitchen" in page, True)
        check("...under an `####` command H4",
              page.index("####") < page.index("a bright kitchen"), True)

        first = images(d, 1, "ABCD")
        ig.write_batch(d, 1, ig.format_command("create"), "a bright kitchen", first,
                       "flux-dev · seed 7 · $0.10")
        ig.add_member_row(d)
        ig.add_to_gallery(d, first[0])
        check("the batch index advances off the image files on disk",
              ig.next_batch_index(d), 2)

        second = images(d, 2, "A")
        ig.write_batch(d, 2, ig.format_command("create"), "make it darker", second,
                       "flux-dev · seed 9 · $0.03")

        page = ig.roll_page(d).read_text(encoding="utf-8")
        check("the newest batch sits above the older one",
              page.index("## Batch 2") < page.index("## Batch 1"), True)
        check("...and both sit below the pending Next render",
              page.index("## Next render") < page.index("## Batch 2"), True)

        # Within a batch the images come first and the prompt is recorded with
        # them; a batch that lost its prompt is unrecoverable (IMGEN001 is the
        # cautionary example), so the pairing is the property worth pinning.
        b2 = page[page.index("## Batch 2"):page.index("## Batch 1")]
        check("the grid precedes the command that made it",
              b2.index("IMGEN001-2A.png") < b2.index("####"), True)
        check("the prompt follows its own command, inside its own batch",
              b2.index("####") < b2.index("make it darker"), True)
        check("the older batch keeps its own prompt, not the newer one",
              "a bright kitchen" in page[page.index("## Batch 1"):], True)

        check("the grid wraps 3-across",
              "| ![[IMGEN001-1A.png\\|500]] | ![[IMGEN001-1B.png\\|500]] "
              "| ![[IMGEN001-1C.png\\|500]] |" in page, True)
        check("the short final row is padded",
              "| ![[IMGEN001-1D.png\\|500]] |  |  |" in page, True)

        # Rewriting a batch (the append case) must not cost it its identity —
        # a heading subtitle and any commentary above the grid are hand-authored
        # and cannot be regenerated.
        text = ig.roll_page(d).read_text(encoding="utf-8")
        text = text.replace("## Batch 2\n\n",
                            "## Batch 2 — the keeper\n\nThe light finally reads right.\n\n")
        ig.roll_page(d).write_text(text, encoding="utf-8")
        ig.write_batch(d, 2, ig.format_command("create"), "make it darker",
                       second + images(d, 2, "B"), "flux-dev · seed 9 · $0.06")
        page = ig.roll_page(d).read_text(encoding="utf-8")
        check("a rewritten batch keeps its hand-authored subtitle",
              "## Batch 2 — the keeper" in page, True)
        check("...and the commentary written above its grid",
              "The light finally reads right." in page, True)

        check("the roll is registered in the masthead",
              "[[IMGEN001 — Kitchen concepts]]" in
              (tmp / "IMGEN.md").read_text(encoding="utf-8"), True)
        gallery = (tmp / "IMGEN Gallery.md").read_text(encoding="utf-8")
        check("the gallery entry goes on top",
              gallery.index("Kitchen concepts") < gallery.index("[[old]]"), True)

        # A second roll must not disturb the first, and must sort after it.
        n2, d2 = ig.new_roll("Rooftop", "a rooftop at dusk")
        check("the second roll takes 002", (n2, d2.name), (2, "IMGEN002 — Rooftop"))
        check("both rolls are seen", [b[0] for b in ig.rolls()], [1, 2])
        check("the first roll's page is untouched by the second",
              "Kitchen concepts" in ig.roll_page(d).read_text(encoding="utf-8"), True)
    finally:
        shutil.rmtree(tmp)

    print()
    print(f"imgen anchor bookkeeping: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
