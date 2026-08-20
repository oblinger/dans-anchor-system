#!/usr/bin/env python3
"""T551 — `remove <anchor> Backlog <row>.Q<n>`: F329's missing other half.

F329 retired inline row questions and told the existing ones to "migrate on
touch, never by sweep". `define … Q+` performs the first half — the question
lands in the row's doc. Nothing performed the second: `remove` refused a
row-scoped address outright, so every migration stalled with the question
stored twice and C57 still flagging the row. `resolve` is not a substitute; it
writes an answer, and these questions are open.

The load-bearing property is the guard, not the deletion. Removal is refused
unless the row's arrow-linked doc already carries a PENDING `^<row>-Q<n>`, so
the verb can stop a duplicate but cannot lose a question. The three refusals
below are the test: no doc, doc without the block-ID, and doc where the
block-ID sits under `## Resolved` (rehomed to a question nobody can answer).

    python3 test-t551-row-q-remove.py
"""
# T170 — several scripts here are extensionless, so the import machinery caches
# them under a mangled name and has been seen serving code no longer on disk.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

# `state` is extensionless, so the ordinary path-based finder returns a spec
# with no loader — T086 hit this first and the SourceFileLoader form is what
# every test here uses.
_S = (Path(__file__).parent / "state").resolve()
_loader = importlib.machinery.SourceFileLoader("state_mod", str(_S))
st = importlib.util.module_from_spec(
    importlib.util.spec_from_loader("state_mod", _loader))
sys.modules["state_mod"] = st
_loader.exec_module(st)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


ROW = """- **T001 — A row with two legacy inline questions** [2 Questions] \
— → [[XX001 - A row|T001]] — body. ^T001
  - **Next:** do the thing.
  - **Q1 — first?** — context. ^T001-Q1
    - **(A)** yes
    - **(B)** no
  - **Q2 — second?** — context. ^T001-Q2
    - **(A)** yes
    - **(B)** no
"""

DOC_PENDING = """# [[XX]] · T001 — A row

## Open Items
<!-- state:q aa -->

- **Q1 — first?** — context. ^T001-Q1
  - **(A)** yes
  - **(B)** no
"""

DOC_RESOLVED = """# [[XX]] · T001 — A row

## Resolved

### Q1 — first? (resolved 2026-08-19) ^T001-Q1
**Resolved:** (A)
"""


def scratch(doc_text=None, arrow=True):
    d = Path(tempfile.mkdtemp())
    row = ROW if arrow else ROW.replace("— → [[XX001 - A row|T001]] ", "")
    bl = d / "XX Backlog.md"
    bl.write_text(f"# XX Backlog\n\n## Now\n\n{row}\n## Later\n\n## Done\n")
    if doc_text is not None:
        (d / "XX001 - A row.md").write_text(doc_text)
    return bl


def q_span_present(bl, n):
    return f"^T001-Q{n}" in bl.read_text()


print("_row_q_rehomed_in_doc — the guard, in isolation")

for name, doc_text, arrow, want in [
    ("doc carries a pending ^T001-Q1        → rehomed", DOC_PENDING, True, True),
    ("no doc on disk                        → NOT rehomed", None, True, False),
    ("row has no arrow pointer              → NOT rehomed", DOC_PENDING, False, False),
    ("doc exists, block-ID absent           → NOT rehomed",
     "# [[XX]] · T001\n\nprose that mentions T001 but hosts nothing.\n", True, False),
    ("block-ID only under ## Resolved       → NOT rehomed", DOC_RESOLVED, True, False),
]:
    bl = scratch(doc_text, arrow)
    lines = bl.read_text().splitlines()
    row_start, _ = st._row_span(lines, "T001")
    got = st._row_q_rehomed_in_doc(bl, lines, row_start, "T001", 1) is not None
    check(name, got, want)

print()
print("_extend_over_q_furniture — the question's tail travels with it")

# `- **Recommendation:**` is a SIBLING of the Q header by C9/C19 convention, so
# the span ends above it and removing the question alone strands it. Nothing
# catches that: every check that reads a recommendation starts from a question.
FURN = [
    "  - **Q1 — first?** — context. ^T001-Q1",       # 0  q_start
    "    - **(A)** yes",                              # 1
    "  - **Recommendation:** None — open.",           # 2  furniture
    "    - continuation of the recommendation",       # 3  its child
    "  - **Q2 — second?** — context. ^T001-Q2",       # 4  neighbour: STOP here
    "    - **(B)** no",                               # 5
    "  - **Recommendation:** Lean (B).",              # 6  Q2's, not Q1's
    "  - **Next:** do the thing.",                    # 7
]
check("furniture after Q1 is consumed, Q2 is not",
      st._extend_over_q_furniture(FURN, 2, len(FURN), 2), 4)
check("a companion sub-bullet stops the scan",
      st._extend_over_q_furniture(FURN, 7, len(FURN), 2), 7)
check("an unrecognised label is left alone",
      st._extend_over_q_furniture(
          ["  - **Parked:** since 2026-08-02."], 0, 1, 2), 0)
check("furniture at a DEEPER indent is not a sibling and is skipped",
      st._extend_over_q_furniture(
          ["      - **Recommendation:** nested under an option."], 0, 1, 2), 0)

print()
print("dispatch — remove now accepts a row-scoped address")

check("remove is routed, not refused",
      "remove" in _S.read_text().split("does not take a row-scoped")[0][-600:],
      True)

print()
print("the refusal names the sanctioned recovery, not just the failure")

bl = scratch(None)
lines = bl.read_text().splitlines()
row_start, _ = st._row_span(lines, "T001")
# The message is built where the guard returns None; assert the two escapes it
# must name, because an agent that hits this refusal with no route out will
# reach for `resolve` and fabricate an answer — the exact harm being prevented.
src = _S.read_text()
msg = src.split("is not hosted anywhere else", 1)[1][:900]
check("points at `define … Q+` to rehome first", "define {slug} <doc> Q+" in msg, True)
check("points at `resolve` to retire outright", "state resolve {slug} Backlog" in msg, True)
check("tells the caller to keep the block-ID", "block-ID" in msg, True)

print()
print(f"{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
