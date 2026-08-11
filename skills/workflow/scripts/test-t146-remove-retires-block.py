#!/usr/bin/env python3
"""test-t146-remove-retires-block.py — TINK T146: `state remove` must retire a
spent `## Open Questions` block, exactly as `state resolve` does.

The defect: `remove` archived the removed Q to a `### Removed` H3 *inside*
`## Open Questions` — and re-created that H2 if the removal had just emptied it.
`open_questions_is_empty` counts any `### ` as content (correctly: a holding pen
may carry unmigrated decisions), and `remove` never called
`drop_open_questions_if_empty`. So removing the LAST pending Q left an
`## Open Questions` H2 with zero pending questions that no sanctioned verb could
clear — audit-q C21 (empty H2) and C35/C46 (stale pending entry) all fired on it.
Hit live on TINK309, 2026-08-06, and hand-repaired with Python.

The fix archives to the bottom `## Resolved` H2 and fires phase 2, which is what
F127/F128 already ruled for `resolve` ("the in-block ### Resolved staging is a
historical artifact"). The audit trail is strengthened, not weakened: the bottom
H2 is the doc's permanent decision record; `## Open Questions` is transient.

  A. remove a NON-last Q  → block survives with the remaining pending Q
  B. remove the LAST Q    → block is GONE, entries are in the bottom ## Resolved
  C. the audit trail      → the original Q body and the reason are preserved
  D. resolve-then-remove  → a mixed round still retires cleanly

Self-contained: imports backlog-edit.py in-process and stubs the two seams that
reach the real vault (`_find_feature_doc`, `_post_conditions`, `_selffire`), so
fixtures live in a tmpdir. Never touches the real vault."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)
# Never touch the real vault.
be._selffire = lambda *a, **k: None
be._post_conditions = lambda *a, **k: []   # returns the warnings list main_q iterates

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

DOC = """---
description: fixture
---
# [[ZZT]] · F001 — Fixture feature
One-line orientation.

## Open Questions
<!-- state:q 00 -->

- **Q1 — First question** — context for the first.
  - **(A)** do it this way
  - **(B)** do it that way
  - **Recommendation:** None

- **Q2 — Second question** — context for the second.
  - **(A)** left
  - **(B)** right
  - **Recommendation:** None

## Summary

Body.

## Status

**Designing** — fixture.
"""


def drive(path, *argv):
    """Run a -Q verb against `path`, with doc resolution pinned to the fixture."""
    be._find_feature_doc = lambda slug, row_id: path
    return be.main_q(["backlog-edit.py", "ZZT", "F001", *argv])


def oq_present(path):
    return "## Open Questions" in path.read_text(encoding="utf-8")


def pending_qs(path):
    """Pending Q-header bullets inside the Open Questions block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        s = next(i for i, l in enumerate(lines) if l.strip() == "## Open Questions")
    except StopIteration:
        return []
    e = next((i for i in range(s + 1, len(lines)) if lines[i].startswith("## ")),
             len(lines))
    return [l for l in lines[s + 1:e] if l.lstrip().startswith("- **Q")]


TMP = Path(tempfile.mkdtemp())
try:
    # ---- A: removing a non-last Q leaves the block standing ----------------
    print("== A: removing one of two Qs keeps the block (one still pending) ==")
    doc = TMP / "F001 — Fixture feature.md"
    doc.write_text(DOC, encoding="utf-8")
    drive(doc, "-Q", "remove", "-n", "1", "--reason", "fixture removal")
    if oq_present(doc):
        ok("## Open Questions survives while Q2 is pending")
    else:
        no("block was dropped while a pending Q remained")
    n = len(pending_qs(doc))
    if n == 1:
        ok("exactly one pending Q remains")
    else:
        no(f"expected 1 pending Q, found {n}")

    # ---- B: removing the LAST Q retires the block -------------------------
    print("== B: removing the last Q retires the block (the T146 defect) ==")
    drive(doc, "-Q", "remove", "-n", "2", "--reason", "fixture removal")
    if not oq_present(doc):
        ok("## Open Questions is gone once nothing is pending")
    else:
        no("spent ## Open Questions block survived — T146 has regressed")
    text = doc.read_text(encoding="utf-8")
    if "## Resolved" in text:
        ok("bottom ## Resolved H2 exists")
    else:
        no("no bottom ## Resolved H2 was created")
    if "### Q1 —" in text and "### Q2 —" in text:
        ok("both removed Qs archived to the bottom H2")
    else:
        no("removed Q entries are missing from the archive")

    # ---- C: the audit trail is preserved ----------------------------------
    print("== C: the original Q body and reason survive the move ==")
    if "do it this way" in text and "left" in text:
        ok("original Q context preserved for both entries")
    else:
        no("original Q context was lost")
    if "**Removed:** fixture removal" in text:
        ok("removal reason recorded")
    else:
        no("removal reason missing")

    # ---- D: a mixed resolve-then-remove round still retires ---------------
    print("== D: resolve one, remove the other — block still retires ==")
    doc2 = TMP / "F002 — Mixed round.md"
    doc2.write_text(DOC.replace("F001", "F002"), encoding="utf-8")
    drive(doc2, "-Q", "resolve", "-n", "1", "--choice", "(A)", "-m", "went with A")
    drive(doc2, "-Q", "remove", "-n", "2", "--reason", "obsoleted by Q1")
    if not oq_present(doc2):
        ok("mixed round retires the block")
    else:
        no("mixed round left a spent block behind")
    t2 = doc2.read_text(encoding="utf-8")
    if "**Choice:** (A)" in t2 and "**Removed:** obsoleted by Q1" in t2:
        ok("a resolved and a removed entry land in the same archive")
    else:
        no("mixed archive is incomplete")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\ntest-t146-remove-retires-block: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
