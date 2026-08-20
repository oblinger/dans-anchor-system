#!/usr/bin/env python3
"""test-renumber-rows.py — the renumber may only move ids it can PROVE are ours.

THE DEFECT THIS PINS, observed live 2026-08-19. The first draft collected its
rewrite scope as "the anchor's own subtree, plus every file containing a
qualified `ABIO Backlog#^T002` link" and then applied *unqualified* patterns
(`^T002`, `**T002 —`) to all of them. Applied to ABIO's single T002 it
renumbered **ATT's own T002 rows** and **ten unrelated block anchors in the
shared `Q.md`** — 33 edits where 3 were wanted, in two anchors owned by other
agents. Caught by reading the diff, not by the run, which reported success.

The rule the fix encodes: a bare `^T002` is meaningless out of context — 22
anchors have one — so it may be rewritten ONLY inside the two files that own the
id (the anchor's backlog and the row's own document). Outside those, only forms
that name the anchor explicitly (`[[ABIO Backlog#^T002|T002]]`, or a link to the
renamed doc) may move, and each is matched as a WHOLE LINK so an alias can never
be rewritten out from under a sibling link in the same file.

  A. plan       — F stays, colliding T moves, B/Q become T; new ids clear high-water
  B. padding    — the literal spelling is quoted, not guessed (`T002`, not `T2`)
  C. local      — the backlog's own row header + block anchors move
  D. qualified  — a `SLUG Backlog#^id` link moves, target and alias together
  E. isolation  — THE REGRESSION: a foreign anchor's identical id never moves
  F. mixed file — in one file holding both anchors' links, only ours moves
  G. sub-Qs     — a hosted `^T002-Q1` rides along with its host
  H. dry-run    — a dry run writes nothing at all

Self-contained: builds a miniature two-anchor vault in a tmpdir and points the
script at it with RENUMBER_VAULT. Never touches the real vault.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TMP = Path(tempfile.mkdtemp())
os.environ["RENUMBER_VAULT"] = str(TMP)

_loader = importlib.machinery.SourceFileLoader("rn", str(HERE / "renumber-rows.py"))
_spec = importlib.util.spec_from_loader("rn", _loader)
rn = importlib.util.module_from_spec(_spec)
sys.modules["rn"] = rn
_loader.exec_module(rn)

PASS = FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


AAA_BACKLOG = """---
description: fixture
---
# AAA Backlog

## Now

- **F002 — a feature that already owns the number 2** [Ready] — body. ^F002
- **T002 — the colliding task** [Ready] — → [[AAA T002 - The Colliding Task|T002]] — body. ^T002
  - **Q1 — a hosted question** (resolved) ^T002-Q1
- **T007 — a task that collides with nothing** [Ready] — body. ^T007
- **B18 — an old B row** [Done] — body. ^B18
- **F003 — untouched** [Ready] — body. ^F003
- **T009 — cites a foreign row** [Ready] — see [[BBB Backlog#^T002|T002]] for the parallel case. ^T009
"""

BBB_BACKLOG = """---
description: fixture
---
# BBB Backlog

## Now

- **T002 — a DIFFERENT anchor's T002, which must not move** [Ready] — body. ^T002
- **F050 — bbb feature** [Ready] — body. ^F050
"""

SHARED_Q = """# Q

- [[AAA Backlog#^T002|T002]] — ours, must move.
- [[BBB Backlog#^T002|T002]] — theirs, must not.
- [[AAA Backlog#^T007|T007]] — ours but not colliding, must not move.
- [[AAA Backlog#^T002|AAA T002]] — the cross-anchor display form C37 asks for.
- [[AAA Backlog#^T002|T002 — the colliding task]] — alias carries a title too.

Re-homed from AAA T002 last week; see also BBB T002, which is a different row.
The doc link [[AAA T002 - The Colliding Task]] is the rename's business, not the
prose rule's. Routed per [[AAA Backlog|AAA T002]] — a page link whose display
text names the row, and [[BBB Backlog|BBB T002]] which is not ours.
Gating rows: TINK T148, AAA T002 — none of those are blocked (em-dash after).

| where | row |
|---|---|
| table cell | [[AAA Backlog#^T002\|AAA T002]] |
| theirs | [[BBB Backlog#^T002\|BBB T002]] |

Inbox trail: `MOVED -> AAA Backlog#^T002` and `MOVED -> BBB Backlog#^T002`.
Suffix trap: [[XAAA Backlog#^T002|XAAA T002]] belongs to XAAA, not to AAA.
"""

try:
    aaa = TMP / "AAA"
    (aaa / "AAA Track" / "AAA Backlog").mkdir(parents=True)
    (aaa / ".anchor").write_text("slug: AAA\ndescription: fixture\n", encoding="utf-8")
    (aaa / "AAA Track" / ".anchor").write_text("description: work tracking\n",
                                               encoding="utf-8")
    bl = aaa / "AAA Track" / "AAA Backlog" / "AAA Backlog.md"
    bl.write_text(AAA_BACKLOG, encoding="utf-8")
    doc = aaa / "AAA Track" / "AAA Backlog" / "AAA T002 - The Colliding Task.md"
    doc.write_text("---\ndescription: fixture\n---\n\n"
                   "# [[AAA]] · T002 — The Colliding Task\nintro.\n\n"
                   "## Status\n\n**Ready** — body. ^T002-note\n", encoding="utf-8")

    bbb = TMP / "BBB"
    (bbb / "BBB Track").mkdir(parents=True)
    (bbb / ".anchor").write_text("slug: BBB\ndescription: fixture\n", encoding="utf-8")
    bbl = bbb / "BBB Track" / "BBB Backlog.md"
    bbl.write_text(BBB_BACKLOG, encoding="utf-8")

    qmd = TMP / "Q.md"
    qmd.write_text(SHARED_Q, encoding="utf-8")

    # ---- A: the plan ------------------------------------------------------
    print("== A: F holds its numbers; only the genuine conflicts move ==")
    rows = rn.scan_rows(bl)
    plan = rn.build_plan(rows)
    got = [(o, n) for o, n, _t in plan]
    # High-water across every kind in this fixture is 18 (the B row), so the
    # first fresh number is 19. B18 does NOT need a fresh one — 18 is unclaimed
    # in the merged space once B collapses into T, so only its letter changes.
    if got == [("T002", "T019"), ("B18", "T018")]:
        ok("T002 (collides with F002) → T019, above high-water; B18 → T018; "
           "T007 and T009 untouched")
    else:
        no(f"unexpected plan: {got}")
    if all(int(n[1:]) > 18 or int(n[1:]) == int(o.lstrip("TBQ")) for o, n in got):
        ok("every new id is either above high-water or the row's own free number")
    else:
        no(f"a new id landed inside the live range: {got}")
    if not any(o.startswith("F") for o, _n in got):
        ok("no F row is in the plan")
    else:
        no("an F row was scheduled to move")

    # ---- B: literal spelling ---------------------------------------------
    print("== B: the OLD id is quoted from the file, never reconstructed ==")
    if ("T002", "002") == (f"{rows[1][0]}{rows[1][1]}", rows[1][1]):
        ok("scan_rows kept the zero-padded literal `002`")
    else:
        no(f"padding lost: {rows[1]!r}")
    if got[1][0] == "B18":
        ok("the unpadded `B18` was kept unpadded")
    else:
        no(f"B18 was reformatted to {got[1][0]!r}")

    # ---- doc lookup: the fused form belongs to F, and must not be taken ----
    print("== doc lookup refuses the F-doc that shares the number ==")
    feat = aaa / "AAA Design" / "AAA Features"
    feat.mkdir(parents=True)
    (feat / "AAA002 - A Feature Doc.md").write_text(
        "# [[AAA]] \u00b7 F002 — A Feature Doc\nintro.\n", encoding="utf-8")
    if rn.find_doc(aaa, "AAA", "T002") == doc:
        ok("T002 resolves to its own lettered doc, not `AAA002 - A Feature Doc`")
    else:
        no(f"find_doc returned {rn.find_doc(aaa, 'AAA', 'T002')}")
    if rn.find_doc(aaa, "AAA", "T007") is None:
        ok("a row with no lettered doc resolves to None, not the F-doc")
    else:
        no(f"T007 wrongly matched {rn.find_doc(aaa, 'AAA', 'T007')}")

    root = rn.anchor_root(bl, "AAA")
    if root == aaa:
        ok("anchor_root skipped the slug-less `AAA Track/.anchor`")
    else:
        no(f"anchor_root returned {root}")

    # ---- H: dry-run writes nothing ---------------------------------------
    print("== H: a dry run leaves every byte in place ==")
    before = {p: p.read_bytes() for p in TMP.rglob("*.md")}
    rn.rewrite_local(bl, doc, "T002", "T019", apply=False)
    rn.rewrite_qualified("AAA", "T002", "T019", None, apply=False)
    if all(p.read_bytes() == b for p, b in before.items()):
        ok("dry run changed no file")
    else:
        no("a dry run wrote to disk")

    # ---- C/G: the local rewrite ------------------------------------------
    print("== C: the owning backlog + doc move, sub-question anchors included ==")
    rn.rewrite_local(bl, doc, "T002", "T019", apply=True)
    txt = bl.read_text(encoding="utf-8")
    if "- **T019 — the colliding task**" in txt and "**T002 —" not in txt:
        ok("the row header moved")
    else:
        no("row header not rewritten")
    if " ^T019\n" in txt and " ^T002\n" not in txt:
        ok("the row's block anchor moved")
    else:
        no("block anchor not rewritten")
    if "^T019-Q1" in txt:
        ok("the hosted `^T002-Q1` rode along as `^T019-Q1`")
    else:
        no("hosted sub-question anchor was left behind")
    if "[[BBB Backlog#^T002|T002]]" in txt:
        ok("a FOREIGN block link inside our own backlog was left alone")
    else:
        no("the local pass corrupted a foreign block link in our backlog")
    if "· T019 — The Colliding Task" in doc.read_text(encoding="utf-8"):
        ok("the doc's H1 breadcrumb moved")
    else:
        no("doc H1 not rewritten")

    # ---- D/E/F: the qualified rewrite ------------------------------------
    print("== D/E: qualified links move; the foreign anchor's T002 does not ==")
    rn.rewrite_qualified("AAA", "T002", "T019", None, apply=True)
    q = qmd.read_text(encoding="utf-8")
    if "[[AAA Backlog#^T019|T019]]" in q:
        ok("our qualified link moved — target AND alias together")
    else:
        no(f"our qualified link did not move:\n{q}")
    if "[[BBB Backlog#^T002|T002]]" in q:
        ok("THE REGRESSION: the sibling link in the same file was untouched")
    else:
        no(f"a foreign link in the same file was rewritten:\n{q}")
    if "[[AAA Backlog#^T007|T007]]" in q:
        ok("our own non-colliding T007 was untouched")
    else:
        no("an unrelated row of ours was rewritten")
    if "[[AAA Backlog#^T019|AAA T019]]" in q:
        ok("the slug-prefixed cross-anchor alias moved with its target")
    else:
        no(f"`|AAA T002` was left pointing at a dead id:\n{q}")
    if "[[AAA Backlog#^T019|T019 — the colliding task]]" in q:
        ok("an alias carrying a title keeps the title and moves the id")
    else:
        no(f"the titled alias was mangled:\n{q}")
    if "Re-homed from AAA T019 last week" in q:
        ok("slug-prefixed PROSE moved — the slug qualifies it as ours")
    else:
        no(f"a qualified prose mention was left stale:\n{q}")
    if "see also BBB T002" in q:
        ok("the foreign anchor's slug-prefixed prose was left alone")
    else:
        no("the prose rule crossed into another anchor")
    if "[[AAA T002 - The Colliding Task]]" in q:
        ok("the prose rule stayed out of a fused-filename wiki-link")
    else:
        no(f"the prose rule reached inside a wiki-link:\n{q}")
    if "[[AAA Backlog|AAA T019]]" in q:
        ok("a page link whose alias names the row moved too")
    else:
        no(f"`[[AAA Backlog|AAA T002]]` was left stale:\n{q}")
    if "[[BBB Backlog|BBB T002]]" in q:
        ok("the same shape pointing at another anchor was left alone")
    else:
        no("the page-link alias rule crossed anchors")
    if "[[AAA Backlog#^T019\\|AAA T019]]" in q:
        ok("an ESCAPED-pipe alias inside a markdown table moved too")
    else:
        no(f"the table-cell form `\\|` was skipped:\n{q}")
    if "[[BBB Backlog#^T002\\|BBB T002]]" in q:
        ok("the foreign table-cell link was left alone")
    else:
        no("the escaped-pipe rule crossed anchors")
    if "[[XAAA Backlog#^T002\\|XAAA T002]]" in q or "[[XAAA Backlog#^T002|XAAA T002]]" in q:
        ok("a slug that ENDS with ours (XAAA vs AAA) was not matched")
    else:
        no(f"the slug matched inside a longer slug — the SV/TSV bug:\n{q}")
    if "`MOVED -> AAA Backlog#^T019`" in q:
        ok("a BARE `SLUG Backlog#^id` in a code span moved")
    else:
        no(f"the unbracketed block reference was skipped:\n{q}")
    if "`MOVED -> BBB Backlog#^T002`" in q:
        ok("the foreign bare reference was left alone")
    else:
        no("the bare-reference rule crossed anchors")
    if "TINK T148, AAA T019 — none of those" in q:
        ok("prose followed by an em-dash still moves (it is a list, not a title)")
    else:
        no(f"an em-dash after the id wrongly blocked the rewrite:\n{q}")
    if bbl.read_text(encoding="utf-8") == BBB_BACKLOG:
        ok("the foreign anchor's backlog is byte-identical")
    else:
        no("the foreign anchor's backlog was modified")

    # ---- residual report --------------------------------------------------
    print("== residuals are reported, not silently rewritten ==")
    (aaa / "AAA Track" / "AAA Messages.md").write_text(
        "[INFO] AAA: added T002 in Now [Ready]\n", encoding="utf-8")
    left = rn.residual_prose(root, "T002")
    if any("Messages" in str(f) for f, _i, _l in left):
        ok("a bare prose mention in the log is surfaced for review")
    else:
        no(f"the residual scan missed the log line: {left}")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
