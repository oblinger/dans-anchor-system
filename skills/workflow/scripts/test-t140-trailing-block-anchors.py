#!/usr/bin/env python3
"""T140 — a stale block-ID in an incoming body was never stripped.

`render_row` appends ` ^{anchor}` unconditionally. It never checked whether the
body already carried one, so a body arriving with an anchor ended up with two —
and `ROW_FULL_RE` then absorbed the stale one **into `body`**, where it is
permanent. `_format_q_bullet` had the same defect with a weaker guard: it asked
whether the *correct* anchor was present and never removed a wrong one.

**Why nothing caught it: the `+`.** Every block-ID pattern in `backlog-edit.py`
is `\\^[\\w-]+` — `_q_header_line`, `_append_why_ask_annotation`, `ROW_FULL_RE`.
`+` is outside `[\\w-]`, so the mint placeholder `^T+` could not be matched by
any cleanup path that existed. It survived every pass, silently.

**The damage reached the user.** SONAR Backlog:64 read
`**Q1 — …** ^T+-Q1 ^T017-Q1`; because the stale anchor sits FIRST,
queries-render took it, and `Q.md:124` — the vault-root page Dan answers from —
offered the handle `^T+-Q1`, which resolves to no row. Ten rows across six
anchors carried the row-level form, MED T002 having accumulated three
(`^T+ ^T002 ^T002`).

    python3 test-t140-trailing-block-anchors.py
"""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).parent


def _load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(_HERE / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


be = _load("be", "backlog-edit.py")

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


# ------------------------------------------------- _strip_trailing_anchors

print("_strip_trailing_anchors — the mint placeholder is the case that mattered")

s = be._strip_trailing_anchors
check("a real anchor is stripped", s("body ^T051"), "body")
# The load-bearing one. `[\w-]` cannot match `+`, which is why every pre-T140
# cleanup path walked straight past this and the placeholder became permanent.
check("the mint placeholder is stripped", s("body ^T+"), "body")
check("...which the old [\\w-] pattern could not do",
      __import__("re").sub(r"\s+\^[\w-]+\s*$", "", "body ^T+"), "body ^T+")
check("a whole run collapses", s("body ^T+ ^T002 ^T002"), "body")
check("dotted R-handles are admitted", s("body ^R-Scaffolding.5.2"), "body")
check("a body with no anchor is untouched", s("plain body"), "plain body")
check("empty stays empty", s(""), "")
check("None is tolerated", s(None), "")

# A block *reference* is not a block *anchor* — the pattern needs whitespace
# before the caret, so an inbound link at the end of a body survives. This is
# the one way an over-eager strip would have silently eaten real content.
check("a trailing wiki block-link survives",
      s("see [[TINK Backlog#^T056]]"), "see [[TINK Backlog#^T056]]")
check("a bare block reference survives",
      s("see TINK Backlog#^T056"), "see TINK Backlog#^T056")


# ------------------------------------------------------------- render_row

print("\nrender_row — one anchor, always, whatever the body arrived with")

check("a clean body gets exactly one anchor",
      be.render_row("T051", "Ready", "Title", "body"),
      "- **T051 — Title** [Ready] — body ^T051\n")
check("a body carrying the placeholder does not keep it",
      be.render_row("T051", "Ready", "Title", "body ^T+"),
      "- **T051 — Title** [Ready] — body ^T051\n")
check("a body carrying a real anchor does not double it",
      be.render_row("T002", "Watching", "Title", "body ^T002"),
      "- **T002 — Title** [Watching] — body ^T002\n")
check("the MED T002 shape collapses to one",
      be.render_row("T002", "Watching", "Title", "body ^T+ ^T002 ^T002"),
      "- **T002 — Title** [Watching] — body ^T002\n")
check("an empty body still renders without a stray dash",
      be.render_row("T051", "Ready", "Title", ""),
      "- **T051 — Title** [Ready] ^T051\n")

# The round trip is what makes the fix self-healing: parse a damaged row, render
# it back, and the damage is gone. Every `state set` on an affected row repairs
# it, so the 10 live rows need no separate migration pass.
damaged = "- **T051 — Title** [Ready] — body ^T+ ^T051"
title, body = be.parse_existing_row(damaged)
check("a damaged row round-trips clean",
      be.render_row("T051", "Ready", title, body),
      "- **T051 — Title** [Ready] — body ^T051\n")
# ...and a clean row is a fixed point, so re-rendering never churns the file.
clean = "- **T051 — Title** [Ready] — body ^T051"
t2, b2 = be.parse_existing_row(clean)
check("a clean row is a fixed point",
      be.render_row("T051", "Ready", t2, b2), clean + "\n")


# -------------------------------------------------------- _format_q_bullet

print("\n_format_q_bullet — the stale anchor sat FIRST, so the renderer took it")

f = be._format_q_bullet
check("a plain body is wrapped with one anchor",
      f(1, "T017", "Which relationships carry an ask?"),
      "- **Q1 — Untitled** — Which relationships carry an ask? ^T017-Q1")
check("a pre-formatted Q keeps its title and gains one anchor",
      f(1, "T017", "**Q1 — Which relationships carry an ask?**"),
      "- **Q1 — Which relationships carry an ask?** ^T017-Q1")
# The exact SONAR Backlog:64 shape. The old guard saw `^T017-Q1` was absent,
# appended it, and left `^T+-Q1` in front of it.
check("the SONAR shape drops the placeholder rather than appending beside it",
      f(1, "T017", "- **Q1 — Which relationships carry an ask?** ^T+-Q1"),
      "- **Q1 — Which relationships carry an ask?** ^T017-Q1")
check("re-formatting an already-correct Q is a fixed point",
      f(1, "T017", "- **Q1 — Which relationships carry an ask?** ^T017-Q1"),
      "- **Q1 — Which relationships carry an ask?** ^T017-Q1")

# The second defect this test surfaced, pre-existing and unrelated to anchors:
# the pre-formatted check did not admit a leading `- ` (the form every skill
# template shows) or the `Q+` mint placeholder, so both fell through to the
# plain-body branch and were wrapped a SECOND time. The header then read
# `Untitled` — which is the line queries-render surfaces — while the real
# question sat behind a stray `— - `. Live on SKA F234 Q1/Q2 and HA F112 Q6.
check("a bulleted body is not wrapped a second time as Untitled",
      f(3, "F234", "- **Q1 — Anchor-verb consolidation?** — context here"),
      "- **Q3 — Anchor-verb consolidation?** — context here ^F234-Q3")
check("the Q+ mint placeholder is recognized, not re-wrapped",
      f(3, "F234", "**Q+ — Anchor-verb consolidation?** — context here"),
      "- **Q3 — Anchor-verb consolidation?** — context here ^F234-Q3")
check("a bulleted Q+ body — both shapes at once — still converges",
      f(3, "F234", "- **Q+ — Anchor-verb consolidation?** — context here"),
      "- **Q3 — Anchor-verb consolidation?** — context here ^F234-Q3")
# A genuinely title-less body must still get the Untitled wrapper — the fix
# narrows what counts as pre-formatted, it does not remove the fallback.
check("a body that really has no Q header still gets wrapped",
      f(2, "F234", "just some prose"),
      "- **Q2 — Untitled** — just some prose ^F234-Q2")
# Only the FIRST line carries the anchor; option/Recommendation lines below it
# must come through untouched.
multi = ("- **Q1 — Pick one** ^T+-Q1\n"
         "  - **(A)** first\n"
         "  - **Recommendation:** None")
check("multi-line bodies keep every line below the header",
      f(1, "T017", multi),
      "- **Q1 — Pick one** ^T017-Q1\n"
      "  - **(A)** first\n"
      "  - **Recommendation:** None")


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
