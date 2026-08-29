#!/usr/bin/env python3
"""F291 — the Open Questions block's whole life, driven through `state` alone.

The lifecycle this pins down replaces the Phase 1/2/3 dance in which the block
was DELETED when its last question resolved and RECREATED when a new one
arrived — each recreation an opportunity to write the format wrong. There are
now two states: block exists with N unresolved, and block migrated.

Assertions, in the order the fixture exercises them:

  1. Three questions mint into one block, numbered Q1..Q3.
  2. Resolving out of order re-zones the block rather than emptying it: the
     resolved question moves below a `### Resolved` H3 and the remaining ones
     stay above it, in order.
  3. A resolve naming an option letter that is not listed is REFUSED, and
     refused without touching the file.
  4. `--choice none` is legal and records `none of the above` — the outcome
     that the old required-letter form could not express (it produced
     `**Choice:** (A)` above a body explaining that nothing was decided).
  5. The last resolve migrates: the block disappears and every entry lands at
     the TOP of the bottom `## Resolved`, newest-batch-first, keeping its
     `^F<n>-Q<n>` block-ID.
  6. A fourth question minted afterwards is numbered Q4, not Q1 — monotonic
     per document, because a recycled number would put the same block-ID in
     the file twice and nothing in audit would catch it.

Run: python3 test-f291-question-lifecycle.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("state_mod", str(HERE / "state"))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)
be = st.be

# The post-write chain (audit-q over the vault, Q.md refresh, warden self-fire)
# is out of scope here and needs a real anchor; stub it.
st._post_conditions_and_print = lambda slug, path, summary: None
st._selffire = lambda path: None
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}\n          got  {got!r}\n          want {want!r}")


def ok(name, cond, detail=""):
    check(name, bool(cond) or detail, True)


DOC = """---
description: "fixture"
---

# [[ZZ]] · F001 — Fixture feature

One-line orientation.

## Summary

Body prose.
"""


import re as _re


def _lean_letter(rec, first="A"):
    """T160 — the option letter a Lean/Strong recommendation names, else the
    first listed option; None when the recommendation is `None`, which T160
    never gates."""
    if not _re.search(r"\b(Lean|Strong)\b", rec, _re.IGNORECASE):
        return None
    m = _re.search(r"\(([A-Za-z]\w*)\)", rec)
    return m.group(1) if m else first


def q_body(n, title, opts, lean, damage="taste — no mechanical check settles it",
           risk="file — the fixture doc is rewritten in place"):
    lines = [f"- **Q{n} — {title}** — context for {title}."]
    for letter, text in opts:
        lines.append(f"    - **({letter})** {text}")
    # Outdented to the Q header level — DAS ask-format § 3 / audit-q C10; the
    # define gate enforces the same indent since T621 (2026-08-29).
    lines.append(f"- **Recommendation:** {lean}")
    # T160 — a Lean/Strong Q must state the risk OF ITS LEAN; carried here so
    # this test keeps exercising the lifecycle rather than that gate.
    letter = _lean_letter(lean, first=(opts[0][0] if opts else "A"))
    if letter and risk is not None:
        lines.append(f"    - **Risk of ({letter}):** {risk}")
    lines.append(f"    - **Damage:** {damage}")
    return "\n".join(lines)


def zones(text):
    """(unresolved Q-numbers, resolved-entry Q-numbers) inside the block."""
    lines = text.splitlines()
    rng = be._open_questions_range(lines)
    if rng is None:
        return (None, None)
    start, end = rng
    unresolved, resolved, in_h3 = [], [], False
    for k in range(start + 1, end):
        if lines[k].strip() in ("### Resolved", "### Removed"):
            in_h3 = True          # the zone heading — everything below is archived
            continue
        m = (be._Q_HEADER_BULLET_RE.match(lines[k])
             or be._Q_HEADER_H3_RE.match(lines[k]))
        if m:
            (resolved if in_h3 else unresolved).append(int(m.group(2)))
    return (unresolved, resolved)


def archived(text):
    """Q-numbers of `### Q<n>` entries under the bottom `## Resolved`, in order."""
    lines = text.splitlines()
    found = be._find_h2(lines, "Resolved")
    if found is None:
        return None
    start, end = found
    return [int(m.group(2)) for m in
            (be._Q_HEADER_H3_RE.match(lines[k]) for k in range(start + 1, end)) if m]


with tempfile.TemporaryDirectory() as td:
    doc = Path(td) / "F001 — Fixture feature.md"
    doc.write_text(DOC, encoding="utf-8")

    print("1. Three questions mint into one block")
    specs = [
        ("should the widget spin?", [("A", "spin it"), ("B", "leave it still")],
         "Lean (B). Stillness is the cheaper default."),
        ("where does the cache live?", [("A", "in memory"), ("B", "on disk"),
                                        ("C", "both, tiered")],
         "Lean (A). The working set is small."),
        ("what names the export?", [("A", "the slug"), ("B", "the title")],
         "None"),
    ]
    for i, (title, opts, lean) in enumerate(specs, start=1):
        n = be._next_q_number(doc.read_text(encoding="utf-8"))
        check(f"Q{i} mints as Q{i}", n, i)
        st._q_define_core("ZZ", doc, n, q_body(n, title, opts, lean),
                          why_ask="taste — no mechanical check settles it")
    check("all three pending, none resolved", zones(doc.read_text()), ([1, 2, 3], []))

    print("2. Resolving out of order re-zones rather than empties")
    st._q_answer_core("ZZ", doc, 2, None, "(C)",
                      "Tiering won because the cold half is never touched.")
    check("Q2 moved to the resolved zone", zones(doc.read_text()), ([1, 3], [2]))
    text = doc.read_text()
    ok("entry leads with the question, not the choice",
       re.search(r"### Q2 — where does the cache live\? \(resolved \d{4}-\d\d-\d\d\)\n"
                 r"context for where does the cache live\?\. \^F001-Q2\n\n"
                 r"\*\*Resolved:\*\* \(C\) — both, tiered\n", text),
       "entry layout is question → resolution")
    ok("rejected options survive, one line each",
       "- **(A)** in memory" in text and "- **(B)** on disk" in text,
       "rejected options kept")
    ok("lean is recorded separately from the outcome",
       "**Lean:** Lean (A). The working set is small." in text,
       "Lean line present")
    ok("no `> Original Q context:` quote block", "> Original Q context:" not in text,
       "old quote-block layout is gone")

    print("3. An unlisted option letter is refused, and changes nothing")
    before = doc.read_text()
    try:
        st._q_answer_core("ZZ", doc, 1, None, "(D)", "note")
        check("refused (D)", "no error raised", "BacklogEditError")
    except be.BacklogEditError as err:
        ok("refusal names the listed options", "(A), (B)" in str(err), str(err))
        ok("refusal points at --choice none", "none" in str(err), str(err))
    check("file untouched by the refusal", doc.read_text(), before)

    print("4. `--choice none` is legal")
    st._q_answer_core("ZZ", doc, 1, None, "none — superseded by the F002 rewrite",
                      "The widget was deleted, so the question dissolved.")
    text = doc.read_text()
    ok("records `none of the above` plus what happened",
       "**Resolved:** none of the above — superseded by the F002 rewrite" in text,
       "none-of-the-above line")
    check("Q3 alone still pending", zones(doc.read_text()), ([3], [2, 1]))

    print("5. The last resolve migrates the whole block")
    st._q_answer_core("ZZ", doc, 3, None, "B", "The title reads better in a file list.")
    text = doc.read_text()
    check("block is gone", be._open_questions_range(text.splitlines()), None)
    check("every entry archived", sorted(archived(text)), [1, 2, 3])
    ok("block-IDs survive migration",
       all(f"^F001-Q{n}" in text for n in (1, 2, 3)), "all three anchors present")
    ok("archive sits at the bottom of the doc",
       text.index("## Resolved") > text.index("## Summary"), "Resolved is last H2")
    ok("no stamp left behind", "state:q" not in text, "integrity stamp removed")

    print("6. A later question is numbered above the high-water mark")
    n = be._next_q_number(doc.read_text(encoding="utf-8"))
    check("next Q is Q4, not a recycled Q1", n, 4)
    st._q_define_core("ZZ", doc, n, q_body(n, "does the export sort?",
                                           [("A", "yes"), ("B", "no")], "Lean (A)."),
                      why_ask="taste — no mechanical check settles it")
    check("Q4 opens a fresh block above the archive", zones(doc.read_text()), ([4], []))
    check("archive untouched by the new round", sorted(archived(doc.read_text())),
          [1, 2, 3])

    print("7. Newest batch migrates ABOVE the earlier archive")
    st._q_answer_core("ZZ", doc, 4, None, "(A)", "Sorted output diffs cleanly.")
    check("newest entry first", archived(doc.read_text())[0], 4)

    print("8. A hand-authored H3-form block resolves the same way")
    # The shape audit-q F012 taught the checkers to read, and the shape every
    # question on F294 uses. `### Q<n> — …` must read as a QUESTION, while
    # `### Resolved` reads as the ZONE boundary — the two are one character
    # apart in the naive test ("does the line start with `### `?").
    h3doc = Path(td) / "F002 — Hand authored.md"
    h3doc.write_text(
        "# [[ZZ]] · F002 — Hand authored\n"
        "Orientation.\n\n"
        "## Open Questions\n\n"
        "### Q1 — what does the command get called? — RESOLVED 2026-08-01 ^F002-Q1\n\n"
        "Prose stating the question.\n\n"
        "- **(A)** a short word\n"
        "- **(B)** a self-documenting name\n"
        "- **Recommendation:** Lean (A). House style is terse.\n\n"
        "### Q2 — does it block or warn? ^F002-Q2\n\n"
        "- **(A)** block\n"
        "- **(B)** warn\n"
        "- **Recommendation:** None\n\n"
        "## Summary\n\nBody.\n", encoding="utf-8")
    check("both H3 questions read as pending", zones(h3doc.read_text()), ([1, 2], []))
    st._q_answer_core("ZZ", h3doc, 1, None, "none — a third name won on other grounds",
                      "Agent-facing names optimize for recall, not typing.")
    check("H3 Q1 re-zones, Q2 stays open", zones(h3doc.read_text()), ([2], [1]))
    t = h3doc.read_text()
    ok("the H3 body prose is carried into the entry",
       "Prose stating the question." in t, "prose preserved")
    ok("a prose `— RESOLVED <date>` marker is not stuttered into the title",
       re.search(r"### Q1 — what does the command get called\? \(resolved ", t)
       and "RESOLVED 2026-08-01 (resolved" not in t, "title normalized")
    ok("the recorded outcome contradicts the lean, and both survive",
       "**Resolved:** none of the above — a third name won on other grounds" in t
       and "**Lean:** Lean (A). House style is terse." in t,
       "lean/outcome delta preserved")
    st._q_answer_core("ZZ", h3doc, 2, None, "(B)", "Warning first; measure before blocking.")
    check("block migrates once the H3 round empties",
          be._open_questions_range(h3doc.read_text().splitlines()), None)
    check("both archived", sorted(archived(h3doc.read_text())), [1, 2])

    print("9. T085 — a pre-written ## Resolved entry is merged, not duplicated")
    # F291 released R-pathguard's deny on `## Resolved`, so an agent can now
    # write a `### Q<n>` entry there itself — typically while the decision is
    # still fresh, before it gets around to calling resolve. Without a merge,
    # migration writes a SECOND entry for the same Q and the file ends up
    # carrying `^F<n>-Q<n>` twice: a duplicate block-ID, which is the F281
    # collision class at document scale, and which no audit check looks for.
    race = Path(td) / "F003 — Pre-written.md"
    race.write_text(
        "# [[ZZ]] · F003 — Pre-written\n"
        "Orientation.\n\n"
        "## Summary\n\nBody.\n\n"
        "## Resolved\n\n"
        "### Q1 — the one the agent wrote up first\n"
        "the question as the agent phrased it ^F003-Q1\n\n"
        "**Resolved:** (B) — with the reasoning the agent had in hand\n\n"
        "A paragraph of context only the agent could write.\n",
        encoding="utf-8")
    n = be._next_q_number(race.read_text(encoding="utf-8"))
    check("minting respects the pre-written entry's number", n, 2)
    # Re-open Q1 as a pending question — the shape the race produces.
    st._q_define_core("ZZ", race, 1,
                      q_body(1, "the one the agent wrote up first",
                             [("A", "no"), ("B", "yes")], "Lean (B)."),
                      why_ask="taste — no mechanical check settles it")
    st._q_answer_core("ZZ", race, 1, None, "(B)", "generated stub note")
    t = race.read_text()
    check("exactly one ### Q1 entry survives",
          len([l for l in t.splitlines() if l.startswith("### Q1")]), 1)
    check("exactly one ^F003-Q1 block-ID survives", t.count("^F003-Q1"), 1)
    ok("the agent's prose is the one kept",
       "A paragraph of context only the agent could write." in t
       and "generated stub note" not in t, "agent text won")
    ok("the agent's own Resolved line is untouched",
       "**Resolved:** (B) — with the reasoning the agent had in hand" in t,
       "no second Resolved line grafted")
    check("the block is gone either way",
          be._open_questions_range(t.splitlines()), None)

    print("10. A pre-written entry MISSING the machine-critical line gets it")
    bare = Path(td) / "F004 — Bare.md"
    bare.write_text(
        "# [[ZZ]] · F004 — Bare\n"
        "Orientation.\n\n"
        "## Summary\n\nBody.\n\n"
        "## Resolved\n\n"
        "### Q1 — written up without the resolution line\n"
        "the question ^F004-Q1\n\n"
        "Reasoning, but no **Resolved** line anywhere.\n",
        encoding="utf-8")
    st._q_define_core("ZZ", bare, 1,
                      q_body(1, "written up without the resolution line",
                             [("A", "no"), ("B", "yes")], "Lean (A)."),
                      why_ask="taste — no mechanical check settles it")
    st._q_answer_core("ZZ", bare, 1, None, "(A)", "note")
    t = bare.read_text()
    check("still exactly one entry",
          len([l for l in t.splitlines() if l.startswith("### Q1")]), 1)
    ok("the agent's reasoning survives",
       "Reasoning, but no **Resolved** line anywhere." in t, "prose kept")
    ok("the missing **Resolved:** line was grafted on",
       "**Resolved:** (A) — no" in t, t[-400:])

with tempfile.TemporaryDirectory() as td:
    print("11. F305 D1 — the block is `## Open Items`; legacy docs rename on touch")
    # 11a. A freshly-created block carries the canonical heading.
    fresh = Path(td) / "F005 — Fresh.md"
    fresh.write_text(DOC.replace("F001 — Fixture feature", "F005 — Fresh"),
                     encoding="utf-8")
    st._q_define_core("ZZ", fresh, 1,
                      q_body(1, "does the new block get the new name?",
                             [("A", "yes"), ("B", "no")], "None"))
    t = fresh.read_text()
    ok("new block minted as ## Open Items", "## Open Items" in t, t[:300])
    ok("no legacy heading in a fresh doc", "## Open Questions" not in t, t[:300])
    check("the block reads back", zones(t), ([1], []))

    # 11b. A doc already carrying `## Open Items` round-trips the lifecycle.
    st._q_answer_core("ZZ", fresh, 1, None, "(A)", "The creator writes the new name.")
    check("Open Items block migrates when its round empties",
          be._open_questions_range(fresh.read_text().splitlines()), None)
    check("entry archived from an Open Items block",
          sorted(archived(fresh.read_text())), [1])

    # 11c. A legacy `## Open Questions` doc is renamed by its FIRST managed
    # write — and the integrity stamp is computed over the migrated block.
    legacy = Path(td) / "F006 — Legacy.md"
    legacy.write_text(
        "# [[ZZ]] · F006 — Legacy\n"
        "Orientation.\n\n"
        "## Open Questions\n\n"
        "- **Q1 — stays pending** — context. ^F006-Q1\n"
        "    - **(A)** yes\n"
        "    - **(B)** no\n"
        "    - **Recommendation:** None\n\n"
        "## Summary\n\nBody.\n", encoding="utf-8")
    st._q_define_core("ZZ", legacy, 2,
                      q_body(2, "arrives via a managed write",
                             [("A", "yes"), ("B", "no")], "None"))
    t = legacy.read_text()
    ok("legacy heading renamed on touch", "## Open Items" in t, t[:400])
    ok("old heading gone after the touch", "## Open Questions" not in t, t[:400])
    check("both questions pending after the rename", zones(t), ([1, 2], []))
    ok("Q1's block-ID survives the rename", "^F006-Q1" in t, "anchor kept")
    lines = t.splitlines()
    rng = be._open_questions_range(lines)
    check("stamp matches the migrated block",
          be.read_q_stamp(lines, *rng), be.compute_q_stamp(lines, *rng))

    # 11d. An untouched legacy doc is NOT migrated — reads work, file unchanged.
    untouched = Path(td) / "F007 — Untouched.md"
    untouched_text = (
        "# [[ZZ]] · F007 — Untouched\n"
        "Orientation.\n\n"
        "## Open Questions\n\n"
        "- **Q1 — read but never written** — context. ^F007-Q1\n"
        "    - **(A)** yes\n"
        "    - **(B)** no\n"
        "    - **Recommendation:** None\n\n"
        "## Summary\n\nBody.\n")
    untouched.write_text(untouched_text, encoding="utf-8")
    check("legacy block reads under the old name",
          zones(untouched.read_text()), ([1], []))
    check("reading migrated nothing", untouched.read_text(), untouched_text)

    print("12. F305 D2 — `set` edits a doc-hosted item; define creates")
    import types
    setdoc = Path(td) / "F008 — Setdoc.md"
    setdoc.write_text(DOC.replace("F001 — Fixture feature", "F008 — Setdoc"),
                      encoding="utf-8")
    st._q_define_core("ZZ", setdoc, 1,
                      q_body(1, "the original question",
                             [("A", "yes"), ("B", "no")], "None"))
    args = types.SimpleNamespace(
        inline=q_body(1, "the rewritten question",
                      [("A", "spin"), ("B", "still")], "None"),
        from_file=None, why_ask=None)
    st._query_verb("ZZ", setdoc, 1, "set", args)
    t = setdoc.read_text()
    ok("set replaced the bullet wholesale",
       "the rewritten question" in t and "the original question" not in t,
       t[:600])
    ok("set replaced the options too",
       "**(A)** spin" in t and "**(A)** yes" not in t, "options replaced")
    check("still exactly one Q1", zones(t), ([1], []))

    # set never creates — a missing item is refused, file untouched.
    before = setdoc.read_text()
    args_missing = types.SimpleNamespace(
        inline=q_body(3, "does not exist",
                      [("A", "yes"), ("B", "no")], "None"),
        from_file=None, why_ask=None)
    try:
        st._query_verb("ZZ", setdoc, 3, "set", args_missing)
        check("set on a missing item is refused", "no error raised",
              "BacklogEditError")
    except be.BacklogEditError as err:
        ok("refusal points at define", "define" in str(err), str(err))
    check("file untouched by the refusal", setdoc.read_text(), before)

print(f"\ntest-f291-question-lifecycle: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
