#!/usr/bin/env python3
"""T213 — a `[Ready]` row with pending questions must SHOW them too.

T211's sibling, reached from the other side. There a `[Questions]` row was
promoted into `## Blockers` and lost its questions on the way; here the row is
in the right section already and its BRACKET is something else. A row can
honestly be both — its agent work runnable, its doc waiting on an answer, which
is the normal state of a feature mid-flight — but the bracket is a set while the
render picks one section, so a question on any row not bracketed `[Questions]`
reached no surface at all.

Found 2026-08-11 by filing F303 Q3 and Q5 and then reading the queue file: F303
rendered under `## Ready` with its `**Next:**` and nothing else. No badge, no
question text. `audit-q --scope backlog --anchor TINK` reported **0 findings**
at that moment — every surface that COUNTS questions was right, and only the
surface that DISPLAYS them was wrong, which is precisely why neither defect in
this family is ever caught by an audit.

The 2026-07-18 rule both violated: *the queue must SHOW the questions, not just
a (NQ) badge.*

Run: python3 test-t213-ready-row-shows-its-questions.py
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


BANNER = ("# [T]  [[X|X]]  -  Ready 1    User 0   |   "
          "Now 1    Next 0    Later 0   |   Parked 0    Waiting 0    Icebox 0")


def render(backlog_text):
    # `next_actions` is supplied the way the real caller supplies it — a Ready
    # bullet renders its Next, not the row body, so an empty map would put the
    # ⚠-none-declared placeholder in every bullet and the control would be
    # testing the placeholder rather than the row.
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "X Backlog.md"
        f.write_text(backlog_text, encoding="utf-8")
        rows = qr.parse_backlog(f)
        nexts = {"T900": "run the sweep and commit it."}
        body = qr.build_queries_body("X", BANNER, rows, {}, nexts, {}, f)
    return body or []


def section(body, h2):
    i = body.index(h2)
    out = []
    for ln in body[i + 1:]:
        if ln.startswith("## "):
            break
        if ln.strip():
            out.append(ln)
    return out


# A genuinely runnable row that is ALSO waiting on an answer. The inline (F233)
# Q form is used deliberately: with an empty vault index there is no feature doc
# to resolve, so this exercises the same path a doc-less row takes in production.
READY_WITH_Q = """# X Backlog

## Now

- **T900 — runnable and also asking** [Ready] — context for the work. ^T900
  - **Next:** run the sweep and commit it.
  - **Q1 — Land the fix?** **(A)** land it now **(B)** wait. \
**Recommendation:** Lean **(A)**. ^T900-Q1
"""

# The control: same row, no question. Nothing about it may change.
READY_NO_Q = """# X Backlog

## Now

- **T900 — just runnable** [Ready] — context for the work. ^T900
  - **Next:** run the sweep and commit it.
"""


def main():
    rs = section(render(READY_WITH_Q), "## Ready")

    check("the row renders under Ready", any("T900" in ln for ln in rs), True)
    check("its Next survives — the row is still runnable work",
          any("run the sweep" in ln for ln in rs), True)
    # The two assertions this file exists for.
    check("it carries the (1Q) badge", any("**(1Q)**" in ln for ln in rs), True)
    check("and THE QUESTION TEXT, not just the badge",
          any("Land the fix?" in ln for ln in rs), True)
    # An inline Q has no feature doc to click through to, so this render is the
    # only place its options will ever be read.
    check("an inline Q brings its options (no doc to click to)",
          any("**(A)**" in ln and "**(B)**" in ln for ln in rs), True)

    body = render(READY_WITH_Q)
    check("the question is not double-printed across sections",
          sum("Land the fix?" in ln for ln in body), 1)
    check("the row itself still appears exactly once",
          sum(ln.startswith("- ") and "T900" in ln for ln in body), 1)

    # The affordance must stay keyed on HAVING a question, not on the section.
    ctl = section(render(READY_NO_Q), "## Ready")
    check("a Ready row with no question gets no badge",
          any("Q)**" in ln for ln in ctl), False)
    check("and no stray preview lines under it",
          len(ctl), 1)
    check("that control row still renders its Next",
          any("run the sweep" in ln for ln in ctl), True)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILING: {', '.join(FAILURES)}")
        return 1
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
