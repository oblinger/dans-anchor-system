#!/usr/bin/env python3
"""test-t067-eof-newline.py — T067: `state`'s own writes end in ONE newline.

Every Q/V verb inserts around blank-line separators, so the line list routinely
ends in empty strings. Joining those verbatim — the old
`"\\n".join(lines) + ("\\n" if text.endswith("\\n") else "")` idiom — left
trailing blank lines at EOF, and the on-write hook then fired R-progressive-02
on a file `state` had just written (reproduced 3/3 on real feature docs).

Two assertions, because the fix has two halves:

  1. `_write_feature_lines` normalizes: any number of trailing blanks → one \\n.
  2. No write site still uses the old idiom. This is the half that matters
     long-term — the bug was a copy-pasted line in 13 places, so a source-level
     guard is what stops the 14th from reintroducing it.

Self-contained: imports backlog-edit.py in-process, writes only to a tmpdir."""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
BE = HERE / "backlog-edit.py"
loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0


def ok(m):
    globals().__setitem__("PASS", PASS + 1)
    print(f"  PASS: {m}")


def no(m):
    globals().__setitem__("FAIL", FAIL + 1)
    print(f"  FAIL: {m}")


print("1. _write_feature_lines normalizes the EOF")

CASES = [
    ("three trailing blanks", ["# Doc", "", "body.", "", "", ""], "# Doc\n\nbody.\n"),
    ("one trailing blank", ["# Doc", "", "body.", ""], "# Doc\n\nbody.\n"),
    ("no trailing blank", ["# Doc", "", "body."], "# Doc\n\nbody.\n"),
    ("whitespace-only tail", ["# Doc", "body.", "   ", "\t"], "# Doc\nbody.\n"),
]

with tempfile.TemporaryDirectory() as td:
    for label, lines, want in CASES:
        p = Path(td) / "doc.md"
        be._write_feature_lines(p, list(lines))
        got = p.read_text(encoding="utf-8")
        if got == want:
            ok(f"{label} → exactly one terminating newline")
        else:
            no(f"{label}: wrote {got!r}, wanted {want!r}")

print("2. No write site still uses the conditional-newline idiom")

# The idiom, tolerant of the three formattings it appeared in.
OLD = re.compile(r'\.write_text\(\s*\n?\s*"\\n"\.join\([a-z_]+\)\s*\+\s*'
                 r'\(\s*"\\n"\s+if\s+\w+\.endswith\("\\n"\)\s+else\s+""\s*\)')

for name in ("backlog-edit.py", "state"):
    src = (HERE / name).read_text(encoding="utf-8")
    hits = OLD.findall(src)
    if hits:
        no(f"{name} still has {len(hits)} conditional-newline write site(s)")
    else:
        ok(f"{name} has no conditional-newline write sites")

print("3. T080 — the BACKLOG write path normalizes too")

# T067's source-level guard passed while the bug survived on the file `state`
# touches most: backlog writers join a `splitlines(keepends=True)` list with
# `""`, a different construction the idiom regex above cannot see. Assert on
# behaviour, not on source text.

KEEPENDS_CASES = [
    ("trailing blank line", ["# ZZ Backlog\n", "\n", "- **T1 — x** [Ready]\n", "\n"],
     "# ZZ Backlog\n\n- **T1 — x** [Ready]\n"),
    ("two trailing blanks", ["# ZZ Backlog\n", "\n", "- **T1 — x** [Ready]\n", "\n", "\n"],
     "# ZZ Backlog\n\n- **T1 — x** [Ready]\n"),
    ("already correct", ["# ZZ Backlog\n", "\n", "- **T1 — x** [Ready]\n"],
     "# ZZ Backlog\n\n- **T1 — x** [Ready]\n"),
    ("no final newline", ["# ZZ Backlog\n", "\n", "- **T1 — x** [Ready]"],
     "# ZZ Backlog\n\n- **T1 — x** [Ready]\n"),
]

with tempfile.TemporaryDirectory() as td:
    for label, lines, want in KEEPENDS_CASES:
        p = Path(td) / "ZZ Backlog.md"
        be.write_backlog_lines(p, list(lines))
        got = p.read_text(encoding="utf-8")
        if got == want:
            ok(f"backlog {label} → exactly one terminating newline")
        else:
            no(f"backlog {label}: wrote {got!r}, wanted {want!r}")

# And no backlog writer may bypass it — the failure mode was a raw write_text,
# not the T067 idiom, so guard the shape that actually broke.
RAW_BACKLOG_WRITE = re.compile(r'backlog_path\.write_text\(\s*"" ?\.join')
for name in ("backlog-edit.py", "state"):
    src = (HERE / name).read_text(encoding="utf-8")
    if RAW_BACKLOG_WRITE.search(src):
        no(f"{name} still writes a backlog without the normalizer")
    else:
        ok(f"{name} routes every backlog write through write_backlog_lines")

print(f"\ntest-t067-eof-newline: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
