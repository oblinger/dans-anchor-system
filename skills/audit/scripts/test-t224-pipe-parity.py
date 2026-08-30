#!/usr/bin/env python3
"""test-t224-pipe-parity.py — a pipe is escaped by an ODD run of backslashes.

Three call sites each asked "is this pipe escaped?" with the same lookbehind,
`(?<!\\\\)\\|`, which tests for the PRESENCE of a preceding backslash rather than
the PARITY of the run. They therefore all agreed, and all three were wrong on
one form:

    [[Target\\\\|alias]]

`\\\\` is an escaped BACKSLASH. It renders as one literal backslash and leaves the
pipe bare — so markdown ends the cell there and discards the rest of the row.
The lookbehind saw a backslash immediately before the pipe and called it
escaped. Measured on the real checker before the fix:

    [[A\\|b]]     pass / 2 cells   correct
    [[A\\\\|b]]    pass / 3 cells   WRONG — the row is already broken
    [[A|b]]      fail / 3 cells   correct

The wrong row is exactly what a repair pass emits when it escapes an
already-escaped pipe, so `fix_md_table_pipe_escape` could manufacture the defect
`chk_md_table_pipe_escape` was blind to, and `_row_cells` — the shared splitter
five other checks read their cells through — would hand those checks a cell
containing a live delimiter. Found by Lumen 2026-08-10 draining Tink's inbox
drop about six [[Lumen Nudge]] rows losing their tails.

The fix is one shared predicate, `_unescaped_pipe_positions`, which all three
call. The assertions below fail against the pre-T224 code.

    python3 test-t224-pipe-parity.py
"""
import importlib.util
import pathlib
import sys
import tempfile

S = (pathlib.Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def write(body, name="Doc.md"):
    f = pathlib.Path(tempfile.mkdtemp()) / name
    f.write_text(body, encoding="utf-8")
    return f


def row(link):
    return f"# Note\nWhat this is.\n\n| head | h2 |\n|---|---|\n| {link} | tail |\n"


print("The predicate itself — parity, not presence")

check("bare pipe is live", ap._unescaped_pipe_positions("A|b"), [0 + 1])
check("one backslash escapes", ap._unescaped_pipe_positions(r"A\|b"), [])
check("two backslashes do NOT escape — this is the whole bug",
      ap._unescaped_pipe_positions(r"A\\|b"), [3])
check("three backslashes escape", ap._unescaped_pipe_positions(r"A\\\|b"), [])
check("four backslashes do not", ap._unescaped_pipe_positions(r"A\\\\|b"), [5])
check("a leading pipe at index 0 is live",
      ap._unescaped_pipe_positions("|a|"), [0, 2])
check("no pipes, no positions", ap._unescaped_pipe_positions(r"A\\b"), [])


print("\n_row_cells — the splitter five other checks read through")

check("escaped pipe keeps the link in ONE cell",
      ap._row_cells(r"| [[A\|b]] | tail |"), [r"[[A\|b]]", "tail"])
check("doubled backslash SPLITS the link — the row really is broken",
      len(ap._row_cells(r"| [[A\\|b]] | tail |")), 3)
check("escaping backslashes stay with their cell",
      ap._row_cells(r"| [[A\\\|b]] | tail |"), [r"[[A\\\|b]]", "tail"])
check("bare pipe splits", len(ap._row_cells(r"| [[A|b]] | tail |")), 3)


print("\nchk_md_table_pipe_escape — the doubled form is now caught")

check("odd run of 1 passes",
      ap.chk_md_table_pipe_escape(write(row(r"[[A\|b]]")), pathlib.Path("/"), [])[0], "pass")
check("EVEN run of 2 fails — was `pass` before T224",
      ap.chk_md_table_pipe_escape(write(row(r"[[A\\|b]]")), pathlib.Path("/"), [])[0], "fail")
check("odd run of 3 passes — no over-flagging of legitimate literal backslashes",
      ap.chk_md_table_pipe_escape(write(row(r"[[A\\\|b]]")), pathlib.Path("/"), [])[0], "pass")
check("bare pipe still fails",
      ap.chk_md_table_pipe_escape(write(row(r"[[A|b]]")), pathlib.Path("/"), [])[0], "fail")


print("\nfix_md_table_pipe_escape — repairs it, and does not re-break the repaired form")

for src, want in [(r"[[A|b]]", r"[[A\|b]]"),
                  (r"[[A\\|b]]", r"[[A\\\|b]]"),
                  (r"[[A\|b]]", r"[[A\|b]]"),
                  (r"[[A\\\|b]]", r"[[A\\\|b]]")]:
    f = write(row(src))
    ap.fix_md_table_pipe_escape(f, f.parent, [])
    got = f.read_text().splitlines()[-1]
    check(f"fix {src} -> {want}", got, f"| {want} | tail |")
    # A fixer that is not a fixpoint escapes its own output on the next write.
    ap.fix_md_table_pipe_escape(f, f.parent, [])
    check(f"  ...and is a fixpoint", f.read_text().splitlines()[-1], f"| {want} | tail |")
    check(f"  ...and the re-check is clean",
          ap.chk_md_table_pipe_escape(f, f.parent, [])[0], "pass")


print("\nChokepoint — no call site re-derives the predicate")

src = S.read_text(encoding="utf-8")
check("the `(?<!\\\\)\\|` lookbehind appears nowhere in the file",
      src.count(r'(?<!\\)\|'), 0)


print("\nFence blindness stays cured (the F296 property this must not regress)")

fenced = "# Note\nWhat this is.\n\n```\n| [[A\\\\|b]] | tail |\n```\n"
f = write(fenced)
check("a fenced example of the broken form is not a finding",
      ap.chk_md_table_pipe_escape(f, f.parent, [])[0], "pass")
ap.fix_md_table_pipe_escape(f, f.parent, [])
check("...and the fixer leaves it byte-identical", f.read_text(), fenced)


print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
