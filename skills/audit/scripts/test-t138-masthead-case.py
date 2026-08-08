#!/usr/bin/env python3
"""test-t138-masthead-case.py — TINK T138: masthead links resolve the way
Obsidian resolves them, and case drift is cosmetic rather than broken.

98 masthead wiki-links vault-wide differ from their target's on-disk case,
across ~40 anchors — [[SLUG]] 22, [[TINK]] 9, [[ASG]] 7 — and most have no
rename anywhere in their history (`[[pp]]`→`PP`, `[[SCRatch]]`→`Scratch` are
plain hand-authoring drift). Obsidian resolves a link's FILENAME
case-insensitively through its own index, so every one of them routes a reader
correctly. Matching case-sensitively reported them as MISSING — the phantom
"row is missing" finding that is the half of T136's defect T136 did not reach.

Worse than the phantom: `_has_self_masthead` gated on the same exact match, so
a case-drifted breadcrumb made the doc read as having NO masthead — and every
rule that opens `if not _has_self_masthead(...): return "pass"` then passed it
vacuously. A drifted anchor page was not noisy; it was unchecked.

Ruled 2026-08-08 (T138 Q1 → A): resolve case-insensitively, and list the drift
under its own low-severity rule R-dispatch-table-15.

  A. _has_self_masthead accepts a case-drifted breadcrumb
  B. chk_dispatch_area_row finds a case-drifted Track row
  C. ...and a genuinely absent row still fails
  D. the drift check reports at `warn`, naming both spellings
  E. exact case is silent, and a resolving-but-different NAME is not drift

Self-contained: builds fixture anchors in a tmpdir. Never reads the vault."""
import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

AP = Path(__file__).parent / "audit-plan.py"
_loader = importlib.machinery.SourceFileLoader("audit_plan_mod", str(AP))
_spec = importlib.util.spec_from_loader("audit_plan_mod", _loader)
ap = importlib.util.module_from_spec(_spec)
sys.modules["audit_plan_mod"] = ap
_loader.exec_module(ap)

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")


def masthead(breadcrumb, track_cell):
    return (f"| -[[{breadcrumb}]]- | [[Home]] |\n"
            f"| {track_cell} | [[ZZ Backlog\\|Backlog]] |\n")


TMP = Path(tempfile.mkdtemp())
try:
    # An anchor whose real on-disk names are all-caps, linked in lower/mixed
    # case — TINK's actual shape after `anchor update` rewrote its links.
    root = TMP / "ZZ"
    (root / "ZZ Track").mkdir(parents=True)
    (root / ".anchor").write_text("slug: ZZ\n", encoding="utf-8")
    doc = root / "ZZ.md"

    print("A: _has_self_masthead accepts a case-drifted breadcrumb")
    if ap._has_self_masthead(masthead("Zz", "[[ZZ Track\\|Track]]"), "ZZ"):
        ok("-[[Zz]]- counts as ZZ.md's own masthead")
    else:
        no("a case-drifted breadcrumb read as NO masthead — every masthead "
           "rule then passes the doc vacuously")
    if not ap._has_self_masthead(masthead("Other Page", "[[ZZ Track\\|Track]]"), "ZZ"):
        ok("...while an example masthead for a DIFFERENT page still does not")
    else:
        no("an illustrative masthead was taken as the doc's own")

    print("B: chk_dispatch_area_row finds a case-drifted Track row")
    doc.write_text(masthead("ZZ", "[[Zz Track\\|Track]]"), encoding="utf-8")
    verdict, msg = ap.chk_dispatch_area_row(doc, root, ["Track"])
    if verdict == "pass":
        ok("[[Zz Track|Track]] against ZZ Track/ is a found row")
    else:
        no(f"phantom missing-row finding: {msg}")

    print("C: a genuinely absent row still fails")
    doc.write_text("| -[[ZZ]]- | [[Home]] |\n| [[ZZ Notes\\|Notes]] | x |\n",
                   encoding="utf-8")
    verdict, msg = ap.chk_dispatch_area_row(doc, root, ["Track"])
    if verdict == "fail":
        ok("a masthead with no Track row at all still fails")
    else:
        no(f"case-insensitivity swallowed a real failure: {verdict} {msg}")

    print("D: the drift check reports at warn, naming both spellings")
    doc.write_text(masthead("ZZ", "[[Zz Track\\|Track]]"), encoding="utf-8")
    verdict, msg = ap.chk_dispatch_link_case_drift(doc, root, [])
    if verdict == "warn":
        ok("verdict is `warn` — cosmetic, so it never joins the failure list")
    else:
        no(f"expected warn, got {verdict}: {msg}")
    if "Zz Track" in msg and "ZZ Track" in msg:
        ok("the message names the link and the on-disk truth")
    else:
        no(f"message does not name both spellings: {msg}")

    print("E: exactness and scope")
    doc.write_text(masthead("ZZ", "[[ZZ Track\\|Track]]"), encoding="utf-8")
    if ap.chk_dispatch_link_case_drift(doc, root, [])[0] == "pass":
        ok("exact case is silent")
    else:
        no("an exactly-cased masthead was reported as drift")
    # A link to something that simply is not there is C1/C22's territory, not
    # a case-drift finding — the two must not be conflated.
    doc.write_text(masthead("ZZ", "[[ZZ Somewhere\\|Track]]"), encoding="utf-8")
    if ap.chk_dispatch_link_case_drift(doc, root, [])[0] == "pass":
        ok("a link with no case-variant on disk is not drift")
    else:
        no("a plain unresolved link was mis-reported as case drift")

    print("F: warn is a first-class verdict, not a soft fail")
    rep = {"counts": {"pass": 1, "fail": 0, "warn": 1, "error": 0, "cached": 0},
           "results": [{"rule": "R-dispatch-table-15", "target": "ZZ.md",
                        "status": "warn", "detail": "case drift"},
                       {"rule": "R-dispatch-table-10", "target": "ZZ.md",
                        "status": "pass", "detail": ""}]}
    text = ap.render_verdicts(rep)
    if "warn 1" in text and "~ R-dispatch-table-15" in text:
        ok("render_verdicts counts and marks warn distinctly")
    else:
        no(f"warn is not rendered as its own verdict:\n{text}")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
