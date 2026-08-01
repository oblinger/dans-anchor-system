#!/usr/bin/env python3
"""T075 — a backlog row title may contain a literal `*`.

`_row_bracket` matched the title run as `[^*]*`, which cannot cross an
asterisk. A row like

    - **T074 — Wire the 4 `svg_*` checkers** [Ready] — …

therefore matched nothing and read as *bracketless*. The visible symptom was
R-backlog-03 calling a plainly-`[Ready]` row ungroomed frontier, but that is
the harmless half. The damage runs the other way: R-backlog-02/-04/-05 all
gate on `_row_bracket(row)` being truthy, so a starred row was silently
SKIPPED by the planned-step and Verify-question checks — under-enforcement,
which is the failure mode this engine treats as worst because nothing
announces it.

Both halves are pinned below: the bracket parses, AND the bracket-keyed
checkers actually fire on a starred row that violates them. The second half
is the one that matters — a fix that only silenced R-backlog-03 would leave
the exemption in place and look green.

Run: python3 test-t075-row-bracket-star.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "ap", Path(__file__).resolve().parent / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


print("1. _row_bracket reads a bracket past an asterisk in the title")

ROWS = [
    ("glob in backticks",
     "- **T074 — Wire the 4 `svg_*` checkers on R-svg-jiggle** [Ready] — body", "Ready"),
    ("bare asterisk",
     "- **T1 — match * against everything** [Questions] — body", "Questions"),
    ("several asterisks",
     "- **T2 — `* Agenda.md`, `F*`, `svg_*`** [Blocked F123] — body", "Blocked F123"),
    ("asterisk adjacent to the closing bold",
     "- **T3 — trailing glob `F*`** [Active] — body", "Active"),
    # Regressions: the shapes that already worked must keep working.
    ("no asterisk", "- **F286 — Chokepoint interfaces** [Questions] — body", "Questions"),
    ("leading-bold bracket form", "- **[Ready]** an unnamed row", "Ready"),
    ("no bracket at all", "- **T4 — nothing here** — body", None),
    ("bracket only later in prose", "- **T5 — a row** — mentions [Ready] in passing", None),
]

for label, row, want in ROWS:
    check(label, ap._row_bracket(row), want)

print("2. The bracket-keyed checkers stop skipping starred rows")

# Each row below is starred AND violates the rule that keys on its bracket.
# Pre-fix every one of these returned a clean pass, because the row was
# invisible rather than compliant.
BACKLOG = """# ZZT Backlog

## Now

- **T1 — a `svg_*` row with no next step** [Ready] — body. ^T1

- **T2 — a `svg_*` row needing a question** [Verify] — body. ^T2

- **T3 — a `svg_*` row, unbracketed** — body. ^T3
"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZT\n")
    f = root / "ZZT Backlog.md"
    f.write_text(BACKLOG)

    verdict, msg = ap.CHECKERS["backlog_frontier_planned"](f, root, [])
    check("R-backlog-02 fires on the starred [Ready] row", verdict, "fail")
    check("  …and names T1's line", "line 5" in msg, True)

    verdict, msg = ap.CHECKERS["backlog_verify_concrete"](f, root, [])
    check("R-backlog-04 fires on the starred [Verify] row", verdict, "fail")

    verdict, msg = ap.CHECKERS["backlog_frontier_bracketed"](f, root, [])
    check("R-backlog-03 still catches a genuinely bracketless starred row",
          verdict, "fail")
    check("  …and names T3, not T1 or T2", "line 9" in msg and "line 5" not in msg, True)

print("3. A conforming starred row is silent on all three")

CLEAN = """# ZZT Backlog

## Now

- **T1 — a `svg_*` row, properly groomed** [Ready] — body. ^T1
  - **Next:** do the thing.

- **T2 — a `svg_*` row awaiting a check** [Verify] — body. ^T2
  - **Verify:** did the thing happen?
"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZT\n")
    f = root / "ZZT Backlog.md"
    f.write_text(CLEAN)
    for c in ("backlog_frontier_planned", "backlog_verify_concrete",
              "backlog_frontier_bracketed"):
        check(c, ap.CHECKERS[c](f, root, [])[0], "pass")

print()
if FAILURES:
    print(f"test-t075-row-bracket-star: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t075-row-bracket-star: all checks pass")
