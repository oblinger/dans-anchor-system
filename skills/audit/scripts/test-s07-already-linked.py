#!/usr/bin/env python3
"""test-s07-already-linked.py — S07 counts HIDDEN children, not folder size.

`S07` fired on `marker is None and fronts_folder and children > 0` and reported
`({children} hidden)` — folder SIZE, dressed up as a count of what the page was
concealing. S08, eleven lines below it in the same function, already filtered to
members the page does not link; S07 never got the same treatment.

Measured vault-wide 2026-08-11 (by [[ATT|Atticus]], then independently again):

  * S07 as written ......... 39 pages, 242 children
  * S07 + already-linked ... 18 pages,  51 children
  * pages hiding nothing ... 21

Both worked examples in [[DAS spine]] § The catchall is not optional were among
the false ones — `ASIO` 33 members / 0 unlinked, `META` 14 / 0. Each hand-writes
one masthead row per child, which is a curated spine doing its job. Worse, the
remedy the rule demands could not have helped them: F081 body-mention
suppression omits every child the page already links, so the `...` they were
told to add would have rendered an empty zone.

Both directions are asserted, because a filter is equally wrong if it silences
the real case: a page with genuinely unlinked members MUST still fire.

Usage: python3 test-s07-already-linked.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("sc", HERE / "spine_check.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["sc"] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def page(rows):
    """A masthead page with no marker, fronting a folder — the S07 shape."""
    return ("---\ndescription: x\n---\n\n"
            "| -[[Demo]]- | : a demo.<br>→ [[kmr]] → [Demo](hook://p/Demo) |\n"
            "| --- | --- |\n"
            + rows +
            "\n# Demo\nOne line of orientation under the H1.\n")


def run(m, body, children):
    """Write Demo.md into a folder holding `children`, return S07 findings."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "Demo"
        d.mkdir()
        (d / ".anchor").write_text("", encoding="utf-8")
        for c in children:
            (d / f"{c}.md").write_text("# x\n", encoding="utf-8")
        p = d / "Demo.md"
        p.write_text(body, encoding="utf-8")
        return [(c, msg) for c, _, msg in m.check(p) if c == "S07"]


def main():
    m = _load()
    KIDS = ["Alpha", "Beta", "Gamma"]

    # 1 — nothing linked: the genuine case. Must fire, and count all three.
    f = run(m, page(""), KIDS)
    check(len(f) == 1 and "3 hidden" in f[0][1],
          "no child linked → S07 fires, counts 3")

    # 2 — every child hand-linked in the masthead: the ASIO / META shape.
    #     Must be SILENT. This is the whole defect.
    rows = "".join(f"| [[{c}]] | a row |\n" for c in KIDS)
    f = run(m, page(rows), KIDS)
    check(not f, "every child linked in masthead → S07 silent (the ASIO/META shape)")

    # 3 — partial: two linked, one not. Must fire, and count ONE, not three.
    #     Reporting folder size here is the exact bug — the old code said 3.
    rows = "".join(f"| [[{c}]] | a row |\n" for c in KIDS[:2])
    f = run(m, page(rows), KIDS)
    check(len(f) == 1 and "1 hidden" in f[0][1] and "Gamma" in f[0][1],
          "two of three linked → S07 fires, counts 1 and names Gamma")

    # 4 — linked in PROSE below the H1, not in the masthead. F081 suppression
    #     keys on a body mention anywhere, so the catchall would omit these too;
    #     the checker must agree with what the remedy would actually render.
    body = page("") + "\nThe three parts are [[Alpha]], [[Beta]] and [[Gamma]].\n"
    f = run(m, body, KIDS)
    check(not f, "children linked in prose → S07 silent (agrees with F081 suppression)")

    # 5 — an empty folder never fires, filter or no filter.
    f = run(m, page(""), [])
    check(not f, "no children → S07 silent")

    # 6 — regression guard on the OLD predicate: a page linking every child
    #     still has children > 0, so anything keying on `p.children` alone
    #     fires here. If this ever passes-by-firing again, the filter was lost.
    rows = "".join(f"| [[{c}]] | a row |\n" for c in KIDS)
    f = run(m, page(rows), KIDS)
    check(not any("3 hidden" in msg for _, msg in f),
          "regression — folder SIZE is never reported as the hidden count")

    print("-" * 40)
    print(f"S07 already-linked test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
