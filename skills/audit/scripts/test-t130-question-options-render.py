#!/usr/bin/env python3
"""T130 — the queue showed a Lean for an option it had truncated away.

`queries-render` emitted a `## Questions` entry as the question stem plus the
Recommendation, each truncated, and dropped the `- **(A)**` option bullets
entirely. For a question whose content IS its options that renders as a stem, an
ellipsis, and a bare `Lean **(B)**` naming a choice the reader cannot see — a
verdict about nothing. Dan, 2026-08-05 on F305 Q1: *"you're telling me you lean
B on what? … I have no idea what you're talking about."*

The fix carries the option LABELS inline and suppresses the Recommendation when
they are absent, so the lean always has a referent.

Reading option bullets also exposed a latent scanner bug it had been safe to
ignore: the resolved zone was recognized only as a bottom `## Resolved` H2, never
as the in-block `### Resolved` (F241's two-zone shape). On a doc using the
in-block form the scanner never left the pending zone, so a resolved question's
option bullets accreted onto the last pending question — F303's Q1 rendered
seven options, its own three plus resolved Q2's four.

    python3 test-t130-question-options-render.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "queries-render.py").resolve()
_spec = importlib.util.spec_from_file_location("qr", _S)
qr = importlib.util.module_from_spec(_spec)
sys.modules["qr"] = qr
_spec.loader.exec_module(qr)

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def write(name, text):
    p = ROOT / name
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------- the gloss

print("\n_option_gloss — the shortest phrase that says what an option IS")

check("a bolded option name is the gloss",
      qr._option_gloss("**Bracket becomes DERIVED** — computed from the open "
                       "items as the most-blocking kind, with a precedence."),
      "Bracket becomes DERIVED")
check("a trailing period on the bolded name is dropped",
      qr._option_gloss("**Extend the Warden DSL.** Templates become another "
                       "Warden construct alongside rules."),
      "Extend the Warden DSL")
check("unbolded prose is cut at the clause break, not mid-word",
      qr._option_gloss("Split by direction — the match half joins Warden."),
      "Split by direction")
check("unbolded prose with no clause break is cut at the sentence",
      qr._option_gloss("Keep it as it is. Cheapest by a wide margin."),
      "Keep it as it is")
# The cap exists because three options plus the question stem share one rendered
# line; an option nobody finishes reading is no better than one never printed.
long_gloss = qr._option_gloss(
    "**Keep brackets as they are and let a row carry only one kind at a "
    "time, refusing to mint a verification on a feature with open questions**")
check("an over-long gloss is capped", len(long_gloss) <= 60, True)
check("...on a word boundary, with an ellipsis",
      long_gloss.endswith("…") and " " in long_gloss, True)
check("...and never mid-word",
      long_gloss[:-1].rstrip().split()[-1] in
      "Keep brackets as they are and let a row carry only one kind at a time",
      True)


# ------------------------------------------------- options reach the render

print("\n_read_open_questions — option bullets are captured with the question")

DOC = write("F900 - shape.md", """---
description: x
---

# [[TINK]] · F900 — Shape

## Open Questions
<!-- state:q aa -->

- **Q1 — What does the bracket MEAN?** — the load-bearing decision. ^F900-Q1
  - **(A)** **Bracket becomes DERIVED** — computed from the open items.
  - **(B)** **Bracket stays about the WORK** — a separate count rides along.
  - **(C)** **Keep brackets as they are** — cheapest, re-imposes the split.
- **Recommendation:** Lean **(B)**, and it is closer than it looks. · *why-ask:
  architecture lock-in on the core work-item model*
  - **Damage:** locking — every consumer of the bracket is rewritten.

## Summary

Body.
""")

entries = qr._read_open_questions(DOC)
check("one pending question", len(entries), 1)
qid, qtext, qrec, qopts = entries[0]
check("the question keeps its id", qid, "Q1")
check("all three options are captured",
      [lab for lab, _ in qopts], ["A", "B", "C"])
check("each carries its authored name",
      [g for _, g in qopts],
      ["Bracket becomes DERIVED", "Bracket stays about the WORK",
       "Keep brackets as they are"])
# The lean is what the options exist to make legible — losing it would trade one
# unreadable entry for another.
check("the recommendation survives, without its why-ask tail",
      qrec.startswith("Lean **(B)**") and "why-ask" not in qrec, True)
# `- **Damage:**` is a sibling sub-bullet, not an option; a bracket-shaped
# reference inside the Recommendation's own prose is not one either.
check("no non-option sub-bullet is mistaken for an option",
      any(g.startswith("Damage") or g.startswith("locking") for _, g in qopts),
      False)


# ------------------------------------------- the in-block resolved zone (H3)

print("\n_read_open_questions — a resolved question's options stay with it")

TWO_ZONE = write("F901 - two zone.md", """---
description: x
---

# [[TINK]] · F901 — Two zone

## Open Questions
<!-- state:q bb -->

- **Q1 — Where does the DSL live?** — Dan is genuinely unsure. ^F901-Q1
  - **(A)** **Notation in DAS, executor in Warden.** Part of the standard.
  - **(B)** **Extend the Warden DSL.** Another Warden construct.
- **Recommendation:** Lean **(A)**.

### Resolved

### Q2 — What is the language called? (resolved 2026-08-04)

**Resolved:** (A) — **Stencil** for the language.

- **(A)** **Stencil** for the language, **"anchor template"** for artifacts.
- **(B)** **Anchor Template** as the language's name too.
- **(C)** **Do not name the language yet.**
- **(D)** **Warden Templating** — weaker than it looked.

## Summary

Body.
""")

two = qr._read_open_questions(TWO_ZONE)
check("only the pending question surfaces", [e[0] for e in two], ["Q1"])
check("it carries only its OWN options",
      [lab for lab, _ in two[0][3]], ["A", "B"])

# An H3 must not be treated as an exit from the resolved zone: an archived
# question whose heading lacks a `(resolved …)` marker would be re-admitted as
# pending, which is a worse failure than the one being fixed.
UNMARKED = write("F902 - unmarked.md", """# [[TINK]] · F902 — Unmarked

## Open Questions
<!-- state:q cc -->

- **Q1 — Still open?** — yes. ^F902-Q1
  - **(A)** **Yes.** Keep it.

### Resolved

### Q2 — An archived question with no marker

- **(A)** **Whatever.** It was decided.

## Summary
""")
check("an unmarked H3 inside the resolved zone stays resolved",
      [e[0] for e in qr._read_open_questions(UNMARKED)], ["Q1"])

# ...but an H3-form question BEFORE any resolved zone is still pending, which is
# the shape `_read_open_questions` was taught to read in the first place.
H3_FORM = write("F903 - h3.md", """# [[TINK]] · F903 — H3 form

## Open Questions
<!-- state:q dd -->

### Q1 — Does the H3 form still parse?

- **(A)** **Yes.** It must.

## Summary
""")
h3 = qr._read_open_questions(H3_FORM)
check("an H3-form pending question still parses", [e[0] for e in h3], ["Q1"])
check("...with its options", [lab for lab, _ in h3[0][3]], ["A"])


# ------------------------------------------------------ the inline row twin

print("\n_read_row_inline_questions — same 4-shape, options already in the text")

BACKLOG = write("TINK Backlog.md", """# Tink Backlog

## Now

- **T900 — a row that hosts its own question** [Questions] — context. ^T900
  - **Q1 — Land the fix?** **(A)** land it now **(B)** wait. \
**Recommendation:** Lean **(A)**. ^T900-Q1
- **T901 — the next row** [Ready] — unrelated. ^T901
""")


class _R:
    # `Row.line_num` is 1-indexed, so `lines[line_num:]` starts on the line
    # AFTER the opener — which is what the sub-bullet scan wants.
    line_num = 5


inline = qr._read_row_inline_questions(BACKLOG, _R())
check("the inline row's question is read", [e[0] for e in inline], ["Q1"])
check("it returns the same 4-shape", len(inline[0]), 4)
# An inline Q packs its options onto the question line, so they are already in
# the text and get the wider 420-char budget; a separate option line would print
# them twice.
check("its options list is empty by construction", inline[0][3], [])
check("...because they are still in the text",
      "**(A)**" in inline[0][1] and "**(B)**" in inline[0][1], True)
check("the recommendation is split out",
      inline[0][2].startswith("Lean **(A)**"), True)
check("the scan stops at the next row",
      any("T901" in e[1] for e in inline), False)


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
