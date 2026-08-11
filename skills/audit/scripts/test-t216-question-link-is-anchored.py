#!/usr/bin/env python3
"""T216 — a rendered question link must LAND on the question.

The sequel to T211, and the same complaint reported a second time. T211 made a
promoted `[Questions]` row show its question text in the queue; it did, and Dan
still could not reach it:

  *"It says F312, one question. But when I click on it, it doesn't go to the
  questions. There's no open questions in F312."*  — 2026-08-11

Both halves were separately correct and the composition was not. The queue
printed `(1Q)` and the question's own sentence, so every counting surface was
right — but the handle it printed them beside was `[[TINK312 - …|F312]]`, an
**unanchored** link, which lands at the top of the feature doc. F312's
`## Open Questions` is 33 lines down behind a 28-row table of contents, so the
first screen at the destination is entirely TOC and the question is invisible
*at the place the link delivers you to*. F317 and F318 draw no such complaint
because their block sits at line 8.

What makes this a bug rather than a limitation: the render already **holds** the
anchor. It reads the doc's `## Open Questions` to print the question text beside
the link, so it knows the heading is there and knows the `^F312-Q6` block id —
it simply never put either into the href.

The rule this file pins: **if the render can show a question, it can aim at it.**

Run: python3 test-t216-question-link-is-anchored.py
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

# A feature doc shaped like F312: the questions block sits well below a table of
# contents, which is the whole reason an unanchored link fails here.
ONE_Q_DOC = """---
description: a doc whose questions are below the fold
---

# [[X]] · F900 — Feed
One-line orientation.

| Table of Contents |  |
|---|---|
| **[[#Summary]]** |  |
| **[[#Design]]** |  |

## Open Questions
<!-- state:q ab -->

- **Q6 — Which write model governs?** — context. ^F900-Q6
  - **(A)** single owner
  - **(B)** last writer wins
  - **Recommendation:** Lean **(B)** · *why-ask: irreversible*

## Summary

Body.
"""

TWO_Q_DOC = ONE_Q_DOC.replace(
    "## Summary\n\nBody.\n",
    "- **Q7 — And the second?** — context. ^F900-Q7\n\n## Summary\n\nBody.\n")

# A doc with questions but NO block ids — the anchor must degrade to the
# heading rather than inventing an id that would land the reader nowhere.
NO_BLOCKID_DOC = ONE_Q_DOC.replace(" ^F900-Q6", "")

BACKLOG = """# X Backlog

## Now

- **F900 — Feed** [Questions] — → [[F900 — Feed]] · a second DAG. ^F900
- **T901 — waits on F900** [Blocked F900] — cannot start. ^T901
"""

# Same doc, same questions, but nothing gates the row — so it renders under
# `## Questions` instead of `## Blockers`. The anchor must not depend on which
# section won: that coupling is exactly what produced T211.
BACKLOG_FREE = """# X Backlog

## Now

- **F900 — Feed** [Questions] — → [[F900 — Feed]] · a second DAG. ^F900
- **T902 — unrelated** [Ready] — nothing waits on this. ^T902
"""

# A `[Ready]` row whose doc holds pending Qs (the T213 shape) — its link must be
# aimed too, or the question it now prints is unreachable for the same reason.
BACKLOG_READY = """# X Backlog

## Now

- **F900 — Feed** [Ready] — → [[F900 — Feed]] · a second DAG. ^F900
  - **Next:** land the first half.
"""


def render(backlog_text, doc_text):
    """Render with a real feature doc on disk, indexed as the vault would."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        f = root / "X Backlog.md"
        f.write_text(backlog_text, encoding="utf-8")
        doc = root / "F900 — Feed.md"
        doc.write_text(doc_text, encoding="utf-8")
        index = {"f900 — feed": [doc], "f900 — feed.md": [doc]}
        rows = qr.parse_backlog(f)
        nexts = qr.collect_next_actions(f) if hasattr(qr, "collect_next_actions") else {}
        body = qr.build_queries_body("X", BANNER, rows, index, nexts, {}, f)
    return body or []


def bullet(body, needle="a second DAG"):
    """The one top-level bullet carrying the F900 row's own body text.

    Matched on the body rather than on `F900`, because the handle also appears
    in T901's `[Blocked F900]` bracket and in the `gates` clause — the same
    trap T211's test documents.
    """
    hits = [ln for ln in body if ln.startswith("- ") and needle in ln]
    return hits[0] if len(hits) == 1 else f"<{len(hits)} matches>"


def main():
    # --- the reported case: one pending Q, promoted into ## Blockers ------
    b = render(BACKLOG, ONE_Q_DOC)
    row = bullet(b)
    check("blocker — the question text still renders (T211 holds)",
          any("Which write model governs" in ln for ln in b), True)
    check("blocker — the (1Q) badge still renders",
          "**(1Q)**" in row, True)
    # The assertion this file exists for. The display text is whatever the link
    # builder chose; only the TARGET is under test, so match up to the pipe.
    check("blocker — the link is no longer bare",
          "[[F900 — Feed|" in row, False)
    check("blocker — one pending Q aims at that Q's block id",
          "[[F900 — Feed#^F900-Q6|" in row, True)

    # --- two pending Qs: no single block to aim at, so aim at the heading --
    b2 = render(BACKLOG, TWO_Q_DOC)
    row2 = bullet(b2)
    check("two Qs — aims at the Open Questions heading",
          "[[F900 — Feed#Open Questions|" in row2, True)
    check("two Qs — badge agrees with the anchor choice",
          "**(2Q)**" in row2, True)

    # --- degradation: a doc with no block ids must not invent one ---------
    b3 = render(BACKLOG, NO_BLOCKID_DOC)
    row3 = bullet(b3)
    check("no block id — falls back to the heading",
          "[[F900 — Feed#Open Questions|" in row3, True)
    check("no block id — does not fabricate a ^F900-Q6 target",
          "^F900-Q6" in row3, False)

    # --- the anchor does not depend on which section won ------------------
    bq = render(BACKLOG_FREE, ONE_Q_DOC)
    rowq = bullet(bq)
    check("unpromoted — renders under ## Questions",
          "## Questions" in bq, True)
    check("unpromoted — the doc link is anchored the same way",
          "[[F900 — Feed#^F900-Q6|" in rowq, True)
    # The `(…)` pointer beside it is the *other* click path, and it must stay
    # unanchored: it aims at a row, and a row has no `## Open Questions` on it.
    # Anchoring it would send the reader somewhere the anchor does not resolve.
    check("unpromoted — exactly one anchored target in the bullet",
          rowq.count("#^F900-Q6"), 1)

    # --- a [Ready] row whose doc has questions (the T213 shape) -----------
    br = render(BACKLOG_READY, ONE_Q_DOC)
    # A Ready bullet prints its `Next:` rather than the row body, so match the
    # badge instead — the body needle every other case uses is absent by design.
    rowr = bullet(br, "**(1Q)**")
    check("ready row — renders under ## Ready", "## Ready" in br, True)
    check("ready row — its link is aimed at the question too",
          "[[F900 — Feed#^F900-Q6|" in rowr, True)

    # --- the splice itself, at the unit level -----------------------------
    check("splice — piped link keeps its display text",
          qr._with_anchor("[[Doc|F1]]", "#Open Questions"),
          "[[Doc#Open Questions|F1]]")
    check("splice — bare link gains a pipe so the anchor stays out of the text",
          qr._with_anchor("[[Doc]]", "#^F1-Q2"), "[[Doc#^F1-Q2|Doc]]")
    check("splice — an already-anchored link is left alone",
          qr._with_anchor("[[Doc#Design|F1]]", "#Open Questions"),
          "[[Doc#Design|F1]]")
    check("splice — a plain-text fallback is never turned into a link",
          qr._with_anchor("F1", "#Open Questions"), "F1")
    check("splice — no anchor means no change",
          qr._with_anchor("[[Doc|F1]]", None), "[[Doc|F1]]")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILING: {', '.join(FAILURES)}")
        return 1
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
