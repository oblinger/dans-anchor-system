#!/usr/bin/env python3
"""T102 — the table class: three fixers that corrupted files, and one that crashed.

Fifth Fable scan under F296, on the two structure classes the T099 census left
measured but untouched (table 33 sites / 25 defs, wiki-link 25 / 22). Every finding
below was re-verified here by execution before it was fixed — the reports named
inputs, and the inputs were re-run against the live module rather than taken on
trust. One reported def list was wrong (10 names that do not exist in the file);
those were dropped and the census re-read.

The three write-path findings are the serious ones, and they share a signature:
**the paired check agreed with the corrupted file**, so nothing in any surface ever
pointed at the bytes the fixer had just written.

    python3 test-t102-table-class.py
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
(ROOT / ".anchor").write_text("slug: T\n", encoding="utf-8")
F = "```"


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def write(text, name="d.md"):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def after(p, fixer):
    getattr(ap, fixer)(p, ROOT, "")
    return p.read_text(encoding="utf-8")


print("fix_md_table_pipe_escape — must not edit through a code span or a typo")

# F296 cured the FENCE half of this fixer and left the INLINE-SPAN half. The row is
# a real table row, so the row-ness test is right; the `re.sub` then ran over the
# whole raw line and rewrote the literal the row exists to display.
p = write(f"# T\n\n| Form | Meaning |\n| --- | --- |\n| `[[A|B]]` | shown as code |\n")
check("a backticked literal inside a LIVE table row is left alone",
      after(p, "fix_md_table_pipe_escape").splitlines()[4],
      "| `[[A|B]]` | shown as code |")

# An unclosed `[[` is an ordinary typo. `\[\[[^\]]*?\]\]` ran from it to the next
# `]]` — across the cell delimiter — and escaping THAT merged two cells. The check
# went fail -> pass, so the driver reported the row "fixed".
p = write("# T\n\n| a | b |\n| --- | --- |\n| [[broken | [[Good]] |\n")
check("an unclosed `[[` does not let the escape span the cell boundary",
      after(p, "fix_md_table_pipe_escape").splitlines()[4],
      "| [[broken | [[Good]] |")
# The checker shares the span, so it stops claiming this row has an unescaped
# link-pipe — which it never did. The `|` after `[[broken` is a CELL DELIMITER, and
# there is no wiki-link containing a pipe anywhere on the line. The pre-fix `fail`
# was itself a false finding, and the fixer then "repaired" it by merging the cells.
# The unclosed `[[` is a real defect, but it belongs to a link-wellformedness rule
# that does not exist yet, not to the pipe-escape rule.
check("...and the checker stops reporting a link-pipe that was never there",
      ap.chk_md_table_pipe_escape(p, ROOT, ""), ("pass", ""))

# Positive control: masking must not become suppression.
p = write("# T\n\n| a | b |\n| --- | --- |\n| [[Target|Label]] | x |\n")
check("a genuinely unescaped alias pipe is still repaired",
      after(p, "fix_md_table_pipe_escape").splitlines()[4],
      "| [[Target\\|Label]] | x |")
p = write("# T\n\n| a | b |\n| --- | --- |\n| [[One]] | [[Two]] |\n")
check("two well-formed links in one row are not cross-captured",
      ap.fix_md_table_pipe_escape(p, ROOT, ""), (False, ""))

print("\nfix_md_trailing_ws — the F278 re-pad respects the same exclusions as its siblings")

p = write("---\nup: [[Parent Page]]\n---\n# T\n\ntrigger line   \n\n"
          f"{F}python\nsub = grid[[0, 1]]\n{F}\n")
out = after(p, "fix_md_trailing_ws").split("\n")
check("no pad is added inside a fence — `grid[[0, 1]]` is code, not a link",
      out[8], "sub = grid[[0, 1]]")
check("...nor to a frontmatter value that happens to end in `]]`",
      out[1], "up: [[Parent Page]]")
check("...and real trailing whitespace on a prose line is still stripped",
      out[5], "trigger line")
p = write("# T\n\nsee [[Somewhere]]\n")
check("a genuine prose terminal link still gets exactly one pad",
      after(p, "fix_md_trailing_ws").split("\n")[2], "see [[Somewhere]] ")

print("\nfix_md_svg_embed_width — the width hint is a pipe, so in a cell it must escape")

p = write("# T\n\n| a | b |\n| --- | --- |\n| ![[diagram.svg]] | the arch |\n")
txt = after(p, "fix_md_svg_embed_width")
check("the hint is escaped inside a table cell",
      txt.splitlines()[4], "| ![[diagram.svg\\|3000]] | the arch |")
check("...so the pipe-escape check does not fail the file this fixer just wrote",
      ap.chk_md_table_pipe_escape(p, ROOT, ""), ("pass", ""))
p = write("# T\n\n![[diagram.svg]]\n")
check("outside a table the hint stays unescaped",
      after(p, "fix_md_svg_embed_width").splitlines()[2], "![[diagram.svg|3000]]")
p = write(f"# T\n\n{F}\n![[diagram.svg]]\n{F}\n")
check("a fenced embed example is not rewritten",
      after(p, "fix_md_svg_embed_width").splitlines()[3], "![[diagram.svg]]")

print("\n_section_body — a document that ends inside a fence is not an error")

# `_strip_fenced` blanks fenced lines and `"\n".join().splitlines()` drops the
# trailing empties, so `marks` came back shorter than `lines` and the scan indexed
# past its end. The checker returned ('error', 'IndexError: ...') — a fail-open on
# a very common doc shape.
doc = (f"# T Architecture\n\n## Subsystems\n\n| Subsystem | Role |\n| --- | --- |\n"
       f"| [[T-core]] | real |\n\n{F}\n| example |\n{F}\n")
p = write(doc, "arch.md")
check("the checker returns a verdict instead of an IndexError",
      ap.run_checker("subsystems_section_present", p, ROOT), ("pass", ""))
check("...and the fenced example row is NOT harvested as a subsystem",
      ap._subsystems_table_rows(doc.splitlines()), ["| [[T-core]] | real |"])

print("\n_row_cells — the escaped pipe the vault mandates is not a cell boundary")

check("an aliased link stays whole", ap._row_cells(r"| [[A\|B]] | second |"),
      [r"[[A\|B]]", "second"])
check("an ordinary row splits normally", ap._row_cells("| a | b |"), ["a", "b"])
check("a row with no trailing pipe keeps its last cell — `[1:-1]` lost it",
      ap._row_cells("| a | b"), ["a", "b"])
check("a genuinely empty final cell survives", ap._row_cells("| a |  |"), ["a", ""])
check("a non-row yields nothing", ap._row_cells("just prose"), [])
# The quiet one: an aliased subsystem row was DROPPED, so kebab-naming and
# link-resolution silently stopped checking any subsystem that used an alias.
check("an aliased subsystem row is read, not dropped",
      ap._subsystem_names([r"| [[not kebab at all\|Core]] | desc |"]),
      [("not kebab at all", True)])

print("\nchk_file_association_folder_structure — targets reduce to a BASENAME")

d = ROOT / "Notes"
write("| Items | [[Notes/Item One]] |\n", "Notes/Notes.md")
write("# Item One\n", "Notes/Item One.md")
check("a folder-qualified link resolves by its last segment, not its first",
      ap.chk_file_association_folder_structure(d, ROOT, "")[0], "pass")
d2 = ROOT / "Feats"
write(r"| Features | [[F001 — Thing\|F001]] |" + "\n", "Feats/Feats.md")
write("# F001\n", "Feats/F001 — Thing.md")
check("...and the mandated in-table escape does not leave a trailing backslash",
      ap.chk_file_association_folder_structure(d2, ROOT, "")[0], "pass")

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
