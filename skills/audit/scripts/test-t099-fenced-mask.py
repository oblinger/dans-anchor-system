#!/usr/bin/env python3
"""T099 — one fence primitive, seven consumers.

Seven places in `audit-plan.py` answered "is this line inside a code fence?" with
a private `in_fence` toggle. F296 fixed the toggle in `_strip_fenced`, found the
identical one still standing in `chk_md_fence_no_markdown` a press later, and
found a third in `chk_progressive_disclosure_layout` — on a rule scoped
`where:: always` — the press after that. Three finds, three presses, one defect;
this consolidates all seven onto `_fenced_mask` so there is no fourth.

The toggles were wrong in three separable ways, and each gets an assertion here
against the CONSUMER, not just the helper — a shared primitive that no caller
reaches is the failure mode this replaced.

    python3 test-t099-fenced-mask.py
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
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


def write(text, name="d.md"):
    p = ROOT / name
    p.write_text(text, encoding="utf-8")
    return p


print("The primitive")

check("marker lines read as fenced — every consumer skips them",
      ap._fenced_mask("a\n```\nb\n```\nc\n"), [False, True, True, True, False])
check("a `~~~` fence is a fence — the toggles knew only ```",
      ap._fenced_mask("a\n~~~\nb\n~~~\nc\n"), [False, True, True, True, False])
check("a ``` inside a `~~~` block does not invert membership below it",
      ap._fenced_mask("~~~\n```\n~~~\nlive\n"), [True, True, True, False])
# The case that actually moved a verdict.
check("an unclosed fence runs to end-of-document, CommonMark-style",
      ap._fenced_mask("a\n```\nb\nc\n"), [False, True, True, True])
check("...so the NEXT opener is not mistaken for its closer",
      ap._fenced_mask("```\nx\n```py\ny\n")[3], True)
check("mask length always equals splitlines() length",
      len(ap._fenced_mask("a\n```\nb\n")), 3)

print("\nThe consumers")

# chk_progressive_disclosure_layout — R-progressive is `where:: always`, so this
# toggle ran over every doc in the vault. `F113 — Decisions facet…md` is the real
# instance: a ```markdown fence opened at line 54 and never closed, so the toggle
# read the next opener as a closer and judged a `## ` heading inside a code sample
# to be a live H2 glued to the prose above it.
f = write("# T\nWhat this is.\n\n```markdown\nunclosed sample\n"
          "```markdown\nprose line\n## md-formatting\n")
check("layout: an H2 inside an unclosed fence is not a live H2",
      ap.chk_progressive_disclosure_layout(f, ROOT, "")[0], "pass")
f = write("# T\nWhat this is.\n\nprose line\n## Real\n")
check("...but a REAL glued H2 still fails",
      ap.chk_progressive_disclosure_layout(f, ROOT, "")[0], "fail")

# chk_md_table_blank_lines — R-markdown is `where:: **/*.md`.
f = write("# T\nWhat this is.\n\n~~~\nintro\n| a | b |\n|---|---|\n~~~\n")
check("tables: rows in a `~~~` fence are not a live table",
      ap.chk_md_table_blank_lines(f, ROOT, "")[0], "pass")
# T099's second half: CommonMark measures a fence's three-space allowance from the
# containing block's content column, so a fence in a list item legally carries the
# list's indent. `HA F008 — Electric Anchor.md` documents a table that way.
f = write("# T\nWhat this is.\n\n- item\n\n    ```\n    | a | b |\n"
          "    |---|---|\n    ```\n")
check("...and a fence indented 4 inside a list item is still a fence",
      ap.chk_md_table_blank_lines(f, ROOT, "")[0], "pass")
f = write("# T\nWhat this is.\n\nintro\n| a | b |\n|---|---|\n")
check("...but a REAL glued table still fails",
      ap.chk_md_table_blank_lines(f, ROOT, "")[0], "fail")

# _backlog_rows — a fenced example row must not be harvested as a real row.
rows = ap._backlog_rows("## Ready\n\n- **T1 — real** [Ready] — body ^T1\n\n"
                        "~~~\n- **T9 — example** [Ready] — shown, not filed\n~~~\n")
check("rows: a `~~~`-fenced example row is not harvested",
      [r[2].split("—")[0].strip() for r in rows], ["- **T1"])

# _agenda_h2s — same shape, different primitive.
check("agenda: a fenced `## ` sample is not an agenda section",
      ap._agenda_h2s("## Real\n\n~~~\n## Sample\n~~~\n"), ["Real"])

# fix_table_blank_lines WRITES the file. It shares its fence judgement with the
# check it is paired to; the two disagreeing is how a fixer re-inserts a blank
# that the check flags again on the next run.
p = write("# T\nWhat this is.\n\n~~~\nintro\n| a | b |\n|---|---|\n~~~\n", "fx.md")
before = p.read_text()
changed, _ = ap.fix_table_blank_lines(p, ROOT, "")
check("fixer: leaves a fenced table alone", (changed, p.read_text()), (False, before))
p = write("# T\nWhat this is.\n\nintro\n| a | b |\n|---|---|\n", "fx2.md")
ap.fix_table_blank_lines(p, ROOT, "")
check("...but still spaces a REAL glued table",
      "intro\n\n| a | b |" in p.read_text(), True)

print("\nNo eighth toggle")

# Whatever else changes, a NEW private fence toggle should not appear. Read off
# the AST rather than grepped: review is what missed the second and third copies,
# and a text scan cannot tell a live `in_fence = not in_fence` from the docstrings
# that now explain why the toggles are gone.
import ast  # noqa: E402 — local to this assertion

names = {n.id for n in ast.walk(ast.parse(_S.read_text(encoding="utf-8")))
         if isinstance(n, ast.Name)}
check("no `in_fence` variable survives anywhere in the module",
      sorted(n for n in names if "in_fence" in n or "infence" in n), [])

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
