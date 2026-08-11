#!/usr/bin/env python3
"""test-t155-resolved-collision.py — TINK T155: the last `resolve` of a round
must not let a hand-written `## Resolved` H3 shadow the entry it merely names.

The defect, hit live on TINK311 2026-08-08. `_merge_prewritten` matched a
pre-existing entry against a migrating one with `^\\s*### Q(\\d+)\\b`. An
apostrophe is a word boundary, so the H3

    ### Q1's answer is superseded — Feed dissolves the ownership question

matched as the entry that IS Q1 — and a supersession is *supposed* to name the
question it supersedes, so that heading is the normal authoring pattern, not an
edge case. The migration then dropped the machine entry in its favour, taking
the question text, the three labeled options, the `**Lean:**` line, and the
`^F311-Q1` block-ID with it, under a message that read as a courteous merge
(`kept yours`). Second-order: it appended `**Resolved:** (A)` to an entry whose
own `**Choice:**` said (C), so the surviving record contradicted itself.

The fix matches on the BLOCK-ID, which is the address every inbound link
resolves through, and keeps both entries when only the heading looks alike.

  A. the T155 regression — a supersession H3 naming Q1 does not shadow Q1
  B. the block-ID survives migration, exactly once
  C. options and Lean survive — the machine entry is their only carrier
  D. T085 still holds — a TRUE collision (same block-ID) merges, not duplicates
  E. the graft is lossless — a merged entry gains what it was missing

Self-contained: loads `state` in-process and stubs the two seams that reach the
real vault. Never touches the real vault."""
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

ST = Path(__file__).parent / "state"
_loader = importlib.machinery.SourceFileLoader("state_mod", str(ST))
_spec = importlib.util.spec_from_loader("state_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["state_mod"] = st
_loader.exec_module(st)
st._selffire = lambda *a, **k: None
st._post_conditions_and_print = lambda slug, path, summary: None

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


DOC = """---
description: fixture
---
# [[ZZT]] · F001 — Fixture feature
One-line orientation.

## Open Questions
<!-- state:q 00 -->

- **Q1 — Who owns the register** — if many agents write to it the home is wrong. ^F001-Q1
  - **(A)** Vault-level surface, Lumen as reader-of-record
  - **(B)** Stays under Lumen, others write as guests
  - **(C)** Per-anchor facets compiling upward
  - **Recommendation:** Lean (A) — it mirrors the federated shape already proven.

- **Q2 — Where does it present** — the surface question. ^F001-Q2
  - **(A)** an existing dashboard pane
  - **(B)** a purpose-built view
  - **Recommendation:** None

## Summary

Body.

## Status

**Designing** — fixture.
"""

SUPERSESSION = """
### Q1's answer is superseded — Feed dissolves the ownership question

**Choice:** (C), not (A). Per-anchor folders propagating upward into one
regenerated roster. **Supersedes the (A) resolution, the same day.**

The (A) reasoning was wrong on its own terms.
"""


def resolve(doc, n, choice, body=""):
    return st._q_answer_core("ZZT", doc, n, None, choice, body)


def append_under_bottom_h2(doc, block):
    """Hand-write `block` under the doc's bottom `## Resolved`, creating that H2
    if the doc has none. Matched on the whole line: the in-block `### Resolved`
    staging zone contains `## Resolved` as a substring."""
    lines = doc.read_text(encoding="utf-8").splitlines()
    if not any(l.strip() == "## Resolved" for l in lines):
        lines += ["", "## Resolved", ""]
    doc.write_text("\n".join(lines).rstrip("\n") + "\n" + block,
                   encoding="utf-8")


def bottom_resolved(doc):
    lines = doc.read_text(encoding="utf-8").splitlines()
    s = next(i for i, l in enumerate(lines) if l.strip() == "## Resolved")
    return "\n".join(lines[s:])


TMP = Path(tempfile.mkdtemp())
try:
    # ---- A/B/C: the regression -------------------------------------------
    print("== A: a supersession H3 naming Q1 must not shadow the Q1 entry ==")
    doc = TMP / "ZZT001 - Fixture feature.md"
    doc.write_text(DOC, encoding="utf-8")

    resolve(doc, 1, "(A)", "Decided from the federated precedent.")
    # The agent then hand-writes a supersession into the bottom ## Resolved,
    # exactly as F311 did an hour before its last resolve.
    append_under_bottom_h2(doc, SUPERSESSION)

    resolve(doc, 2, "(A)", "The surface already exists.")   # last of the round

    text = doc.read_text(encoding="utf-8")
    if "## Open Questions" not in text:
        ok("the spent block retired (migration ran — the path under test)")
    else:
        no("migration did not run; the rest of this test proves nothing")

    if "Q1's answer is superseded" in text:
        ok("the hand-written supersession H3 survives")
    else:
        no("the hand-written supersession H3 was destroyed")

    print("== B: the block-ID survives, exactly once ==")
    n = text.count("^F001-Q1")
    if n == 1:
        ok("^F001-Q1 present exactly once")
    elif n == 0:
        no("^F001-Q1 was DESTROYED — T155 has regressed")
    else:
        no(f"^F001-Q1 appears {n} times — duplicate block-ID (the T085 hazard)")

    print("== C: the machine entry's unique content survives ==")
    body = bottom_resolved(doc)
    missing = [s for s in ("Vault-level surface", "write as guests",
                           "Per-anchor facets", "**Lean:**")
               if s not in body]
    if not missing:
        ok("question text, all three options, and Lean all survive")
    else:
        no(f"lost from the archive: {missing}")

    # The second-order damage: a `**Resolved:**` line landing under a heading
    # whose own `**Choice:**` says something else.
    sup = body.split("### Q1's answer is superseded", 1)[1]
    sup = sup.split("\n### ", 1)[0]
    if "**Resolved:**" not in sup:
        ok("no stray **Resolved:** grafted onto the supersession entry")
    else:
        no("a **Resolved:** line was grafted onto the supersession entry, "
           "which already carries a contradicting **Choice:**")

    # ---- D/E: T085 still holds -------------------------------------------
    print("== D: a TRUE collision (same block-ID) still merges, not duplicates ==")
    doc2 = TMP / "ZZT002 - Fixture two.md"
    doc2.write_text(DOC, encoding="utf-8")
    resolve(doc2, 1, "(A)", "note one")
    # A genuine pre-written record: it carries the block-ID, so it IS the entry.
    append_under_bottom_h2(doc2, "\n### Q2 — Where does it present\n\n"
                                 "The surface question. ^F001-Q2\n\n"
                                 "Hand-written ahead of the resolve.\n")
    resolve(doc2, 2, "(B)", "note two")
    t2 = doc2.read_text(encoding="utf-8")
    if t2.count("^F001-Q2") == 1:
        ok("^F001-Q2 present exactly once — merged, not duplicated")
    else:
        no(f"^F001-Q2 appears {t2.count('^F001-Q2')} times — T085 regressed")
    if "Hand-written ahead of the resolve." in t2:
        ok("the agent's text won, as T085 rules")
    else:
        no("the agent's pre-written text was clobbered")

    print("== E: the merge grafts what the agent's entry was missing ==")
    if "**Resolved:**" in t2:
        ok("the machine's **Resolved:** line was grafted on")
    else:
        no("the **Resolved:** line is missing from the merged entry")
    if "a purpose-built view" in t2:
        ok("the option list was grafted on (the machine is its only carrier)")
    else:
        no("the option list was lost in the merge")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
