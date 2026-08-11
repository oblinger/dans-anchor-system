#!/usr/bin/env python3
"""test-f319-labelled-heart.py — a heart under a heading is still a heart.

`heart_candidate`'s zone used to end at the FIRST H2, so a page that gave its
heart a heading — `## The map — what flows into what` over the table — read as
having no heart at all. Dan put [[Stones]] forward on 2026-08-10 as the exemplar
of what a page with a heart should look like; the detector returned None on it,
and on 39 other pages vault-wide.

Invisibility was the cost, and it is not cosmetic. H01 fires when a heart sits
buried under prose, so a heart the detector cannot see has no protection against
being buried later — verified by pushing prose above Stones' map table and
watching H01 stay silent.

Two directions, because the first two attempts at this fix each got one of them
backwards:
  * a labelled heart at the top is FOUND but must NOT be reported (it is placed
    correctly — nothing to nominate);
  * the same heart with prose shoved above it MUST be reported, since that is
    precisely what H01 exists for. An early cut gated the labelled-heart branch
    on "no prose seen yet", which made the buried case invisible again.

Usage: python3 test-f319-labelled-heart.py
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


HEAD = """---
description: x
---

| -[[Demo]]- | : a demo page.<br>→ [[kmr]] → [Demo](hook://p/Demo) |
| --- | --- |
| Related | [[Other]],   |
| --- | |

# Demo
One line of orientation under the H1.
"""

TABLE = """
| Node | Feeds | Curated with |
|---|---|---|
| **A** | B | C |
| B | C | D |
| C | D | E |
| D | E | F |
"""

# Long enough on purpose: H01's condition 4 is `body_weight() >= 200`, so a page
# with only a line or two of prose is never nominated however its heart sits. A
# short fixture here silently tests nothing — the first draft of this file did
# exactly that and read as two failures in the code rather than in itself.
PROSE = ("\nSome preamble that accumulated over time, of the kind that arrives one\n"
         "sentence at a time and is never removed, until the thing the page exists\n"
         "to show has been pushed well below where a reader starts looking for it.\n"
         "A second paragraph nobody meant to add, saying very little at some length.\n")


def codes(m, body, name="Demo.md"):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(body, encoding="utf-8")
        return [c for c, _, _ in m.check(p)], m.Page(p).heart_candidate()


def main():
    m = _load()

    # 1 — bare heart at the top: found, not reported. (The pre-existing case.)
    c, hc = codes(m, HEAD + TABLE)
    check(hc is not None and "H01" not in c,
          "bare heart at the top → found, no H01")

    # 2 — LABELLED heart at the top: the Stones shape. Must be found, not reported.
    c, hc = codes(m, HEAD + "\n## The map — what flows into what\n" + TABLE)
    check(hc is not None and "H01" not in c,
          "labelled heart at the top → found, no H01 (the Stones shape)")

    # 3 — labelled heart BURIED under prose: must be reported. This is the one an
    #     early cut got wrong by gating the labelled branch on "no prose yet".
    c, hc = codes(m, HEAD + PROSE + "\n## The map — what flows into what\n" + TABLE)
    check(hc is not None and "H01" in c,
          "labelled heart buried under prose → H01 fires")

    # 4 — bare heart buried under prose: the original H01 case, unchanged.
    c, hc = codes(m, HEAD + PROSE + TABLE)
    check(hc is not None and "H01" in c,
          "bare heart buried under prose → H01 fires (unchanged)")

    # 5 — a heading that opens a PROSE section still ends the zone. This is the
    #     F319 M2 calibration that took the check from 100 hits to the genuine
    #     few; widening the zone must not undo it.
    c, hc = codes(m, HEAD + "\n## Discussion\nSome prose here, not a table.\n" + TABLE)
    check(hc is None,
          "heading opening a prose section still ends the heart zone")

    # 6 — a heading with nothing after it must not walk off the end of the file.
    #     `_next_content` returns len(lines) there, which indexed out of range and
    #     crashed the whole vault sweep.
    try:
        c, hc = codes(m, HEAD + "\n## Trailing heading with no body\n")
        ok = hc is None
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"      raised {type(e).__name__}: {e}")
    check(ok, "heading at end of file → no crash, no candidate")

    # 7 — ANY second H1 ends the zone, not only `# BRIEF` / `# Log`. Those two
    #     were hardcoded, so a table under any other top-level section read as
    #     this page's buried heart. Found 2026-08-11 on [[DAS Disciplines]],
    #     whose `# What the classification found` verdict table was nominated.
    #     Named-instance lists are the shape that manufactures an invisible
    #     miss; the corpus also carries `# MEETINGS`, `# Quotes`, `# TOPICS`.
    for h1 in ("# BRIEF", "# Log", "# What the classification found", "# MEETINGS"):
        c, hc = codes(m, HEAD + PROSE + f"\n{h1}\nintro prose under it.\n" + TABLE)
        check(hc is None, f"a table under a second H1 ({h1!r}) is that section's, not the heart")

    # 8 — and the control: the SAME table with no second H1 above it is still
    #     nominated, so test 7 cannot pass by having broken the detector.
    c, hc = codes(m, HEAD + PROSE + TABLE)
    check(hc is not None and "H01" in c,
          "control — remove the second H1 and the buried heart is found again")

    print("-" * 40)
    print(f"F319 labelled-heart test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
