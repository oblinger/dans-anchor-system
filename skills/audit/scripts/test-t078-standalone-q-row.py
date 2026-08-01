#!/usr/bin/env python3
"""T078 — R-backlog-05 must exempt an F275 standalone `Q<n>` row.

The rule is implemented twice with different semantics. The writer,
`backlog-edit.check_questions_promise`, exempts a standalone Q-row explicitly:

    if row_id and re.match(r"^Q\\d+$", row_id):
        return  # F275 — a standalone Q-row is its own question

The audit checker had no such branch, so every Q-row `state Backlog Q+ define`
minted was flagged the instant it existed — the writer creating a shape the
auditor calls broken. Same defect family as T066 and T075: the system declares
a shape legal in one place and illegal in another.

The exemption must stay narrow. A standalone Q-row is self-backing because its
number is in the *row header*; an ordinary T-/F-row bracketed `[Questions]`
still owes either an inline `- **Q<n>` sub-bullet or a `→ [[Doc]]` link, and
those are the assertions that would catch an over-broad fix.

Run: python3 test-t078-standalone-q-row.py
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


BACKLOG = """# ZZ Backlog

## Now

- **Q001 — a standalone question row** [Questions] — the row IS the question. ^Q001
    - **(A)** one
    - **(B)** two
  - **Recommendation:** Lean (A).

- **Q7 — an unpadded standalone row** [Questions] — also self-backing. ^Q7
    - **(A)** one
    - **(B)** two

- **T9 — promises Qs it does not have** [Questions] — no sub-bullet, no link. ^T9

- **T8 — honors the promise inline** [Questions] — body. ^T8
  - **Q1 — a real inline question** — context.

- **F5 — honors the promise by link** [Questions] — → [[F5 — Something]] — body. ^F5

- **T7 — a count bracket, still owes a Q** [3 Questions] — nothing here. ^T7
"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    f = root / "ZZ Backlog.md"
    f.write_text(BACKLOG)
    verdict, msg = ap.CHECKERS["backlog_questions_have_numbered_q"](f, root, [])

    print("1. Standalone Q-rows are exempt (F275)")
    check("zero-padded Q001 not flagged", "line 5" in msg, False)
    check("unpadded Q7 not flagged", "line 10" in msg, False)

    print("2. Ordinary rows still owe their promise")
    check("verdict is fail", verdict, "fail")
    check("T9 (no Q, no link) flagged", "line 14" in msg, True)
    check("T7 ([3 Questions], no Q) flagged", "line 21" in msg, True)

    print("3. Rows that honor the promise stay quiet")
    check("T8 (inline Q) not flagged", "line 16" in msg, False)
    check("F5 (doc link) not flagged", "line 19" in msg, False)

print("4. A conforming backlog passes outright")
CLEAN = """# ZZ Backlog

## Now

- **Q001 — a standalone question row** [Questions] — self-backing. ^Q001
    - **(A)** one
    - **(B)** two
"""
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    f = root / "ZZ Backlog.md"
    f.write_text(CLEAN)
    check("Q-row-only backlog passes",
          ap.CHECKERS["backlog_questions_have_numbered_q"](f, root, [])[0], "pass")

print()
if FAILURES:
    print(f"test-t078-standalone-q-row: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t078-standalone-q-row: all checks pass")
