#!/usr/bin/env python3
"""T211 — a promoted `[Questions]` row must still SHOW its questions.

`## Blockers` is computed: any row some *other* row names in its
`[Blocked <handle>]` is promoted out of whatever section would otherwise hold
it (F283), and the render is total — one row, exactly one section (F284). Those
two rules composed into a defect nobody had reason to look for: a `[Questions]`
row that gates other work leaves `## Questions`, and the Blockers bullet emitted
the bracket and the waiters but **no `(NQ)` badge and no question text**. So the
one kind of question that is provably holding work up was the one kind the user
could not read anywhere in the queue file.

Dan, 2026-08-11, on F312: *"you list 312 as a blocker with questions. But if I
click on 312, I don't see a question there."* Two live rows were affected — F312
and F316 — and the bracket, the audit and the banner all agreed a question
existed, which is precisely why nothing flagged it: every surface that COUNTS
questions was right, and only the surface that DISPLAYS them was wrong.

The 2026-07-18 rule the promotion was silently exempting: *the queue must SHOW
the questions, not just a (NQ) badge.*

Run: python3 test-t211-blocker-shows-its-questions.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "qr", Path(__file__).resolve().parent / "queries-render.py")
qr = importlib.util.module_from_spec(_spec)
sys.modules["qr"] = qr
_spec.loader.exec_module(qr)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


BANNER = ("# [T]  [[X|X]]  -  Ready 0    User 1   |   "
          "Now 2    Next 0    Later 0   |   Parked 0    Waiting 0    Icebox 0")


def render(backlog_text):
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "X Backlog.md"
        f.write_text(backlog_text, encoding="utf-8")
        rows = qr.parse_backlog(f)
        body = qr.build_queries_body("X", BANNER, rows, {}, {}, {}, f)
    return body or []


def section(body, h2):
    """The bullet lines of one H2, including indented sub-bullets."""
    i = body.index(h2)
    out = []
    for ln in body[i + 1:]:
        if ln.startswith("## "):
            break
        if ln.strip():
            out.append(ln)
    return out


# T900 carries its own question inline (F233 form) and nothing depends on it —
# the control. The fixture uses the inline shape deliberately: with an empty
# vault index there is no feature doc to resolve, so this exercises the same
# path a doc-less T-row takes in production.
FREE = """# X Backlog

## Now

- **T900 — needs an answer** [Questions] — context for the ask. ^T900
  - **Q1 — Land the fix?** **(A)** land it now **(B)** wait. \
**Recommendation:** Lean **(A)**. ^T900-Q1
- **T902 — unrelated** [Ready] — nothing waits on this. ^T902
"""

# Identical, except T901 now names T900 — which promotes T900 into Blockers.
# The question did not change; only who is waiting on it did.
GATING = """# X Backlog

## Now

- **T900 — needs an answer** [Questions] — context for the ask. ^T900
  - **Q1 — Land the fix?** **(A)** land it now **(B)** wait. \
**Recommendation:** Lean **(A)**. ^T900-Q1
- **T901 — waits on T900** [Blocked T900] — cannot start. ^T901
"""

# A blocker that is NOT a questions row must gain nothing: the affordance is
# keyed on the bracket, not on being promoted.
VERIFY_BLOCKER = """# X Backlog

## Now

- **T900 — a check** [Verify] — did it hold? ^T900
  - **Verify:** did the thing hold? *why-user: taste*
- **T901 — waits on T900** [Blocked T900] — cannot start. ^T901
"""


def main():
    # --- control: unpromoted, the question is visible in ## Questions -----
    free = render(FREE)
    qsec = section(free, "## Questions")
    check("control — the row renders under Questions",
          any("T900" in ln for ln in qsec), True)
    check("control — it carries the (1Q) badge",
          any("**(1Q)**" in ln for ln in qsec), True)
    check("control — and the question TEXT, not just the badge",
          any("Land the fix?" in ln for ln in qsec), True)

    # --- the regression: promotion must not cost the question ------------
    gat = render(GATING)
    check("promoted — the row left ## Questions entirely",
          "## Questions" in gat, False)
    bsec = section(gat, "## Blockers")
    check("promoted — it renders under Blockers",
          any("T900" in ln for ln in bsec), True)
    check("promoted — the bullet still says it is a questions row",
          any("[Questions]" in ln for ln in bsec), True)
    check("promoted — it says what it gates",
          any("gates" in ln and "T901" in ln for ln in bsec), True)
    # The two assertions this file exists for.
    check("promoted — the (1Q) badge survives promotion",
          any("**(1Q)**" in ln for ln in bsec), True)
    check("promoted — THE QUESTION TEXT survives promotion",
          any("Land the fix?" in ln for ln in bsec), True)
    # An inline Q has no feature doc to click through to, so this render is the
    # only place the reader will ever see its options — they must come too.
    check("promoted — an inline Q brings its options (no doc to click to)",
          any("**(A)**" in ln and "**(B)**" in ln for ln in bsec), True)

    # --- the question is not double-printed ------------------------------
    check("promoted — the question appears exactly once in the whole body",
          sum("Land the fix?" in ln for ln in gat), 1)
    # Totality (F284) still holds: promotion MOVES the row, it does not copy it.
    # Matched on the row's body text rather than its handle — the rendered link
    # is `[[X Backlog#^T900|T900]]`, so a handle match would also catch T901's
    # `[Blocked T900]` bracket and the `gates` clause.
    check("promoted — the row itself appears exactly once",
          sum(ln.startswith("- ") and "context for the ask" in ln for ln in gat), 1)

    # --- the affordance is keyed on the bracket, not on promotion --------
    vb = section(render(VERIFY_BLOCKER), "## Blockers")
    check("a non-questions blocker gets no badge",
          any("Q)**" in ln for ln in vb), False)
    check("a non-questions blocker still renders",
          any("T900" in ln for ln in vb), True)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILING: {', '.join(FAILURES)}")
        return 1
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
