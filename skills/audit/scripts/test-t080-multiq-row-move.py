#!/usr/bin/env python3
"""test-t080-multiq-row-move.py — a row's blank lines must not split it in a move.

MUX T080, 2026-08-08. `apply_placement_fixes` (C15/C16 parking) and
`apply_c4_fix` (C4 stale-[Done] sweep) both extracted a row by walking forward
while the line was indented, then swallowing one blank. That reads a row as
ending at its first blank line — but a blank line is legal INSIDE a row, and
audit-q's own **C20 requires** one between consecutive Q groups. So the two
movers split exactly the rows that were correctly formatted.

Live damage: MUX T073 sat in `## Now` with Q1 and Q2 separated by the C20 blank.
Parking it to `## Later` moved the header and Q1; Q2's five lines stayed behind
under `## Now`, orphaned from any row, and the run reported success. It was
caught only because C34 happens to inspect that horizon — under a horizon C34
skips, the question would have vanished silently.

Both directions are asserted, because "Q2 survived" and "nothing was left
behind" are different failures: a mover could copy the whole row and still
under-delete, leaving a duplicate.

Self-contained: imports audit-q.py, builds fixtures in a tmpdir, cleans up.
Never touches the real vault (warden self-fire disabled)."""
import datetime as dt
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

AQ = Path(__file__).parent / "audit-q.py"
spec = importlib.util.spec_from_file_location("audit_q", AQ)
aq = importlib.util.module_from_spec(spec)
sys.modules["audit_q"] = aq
spec.loader.exec_module(aq)
aq._warden_selffire = None  # disable warden self-fire for fixture writes

PASS = 0
FAIL = 0


def ok(m):
    globals().__setitem__("PASS", PASS + 1)
    print(f"  PASS: {m}")


def no(m, detail=""):
    globals().__setitem__("FAIL", FAIL + 1)
    print(f"  FAIL: {m}")
    if detail:
        print("\n".join("        " + l for l in detail.splitlines()[:24]))


TWO_Q_ROW = (
    "- **T001 — a two-question row** [{status}] — body text. ^T001\n"
    "  - **Next:** do the thing.\n"
    "  - **Q1 — first question?** ^T001-Q1\n"
    "    - **(A)** first option.\n"
    "    - **(B)** second option.\n"
    "  - **Recommendation:** None — no lean.\n"
    "\n"                                   # <- the C20 separator; the whole point
    "  - **Q2 — second question?** ^T001-Q2\n"
    "    - **(A)** first option.\n"
    "    - **(B)** second option.\n"
    "  - **Recommendation:** None — no lean.\n"
)


def section_of(text, h2):
    """Body of `## <h2>` up to the next H2 — where a stranded orphan would sit."""
    lines = text.splitlines()
    try:
        i = next(k for k, l in enumerate(lines) if l.strip() == f"## {h2}")
    except StopIteration:
        return ""
    out = []
    for l in lines[i + 1:]:
        if l.startswith("## "):
            break
        out.append(l)
    return "\n".join(out)


TMP = Path(tempfile.mkdtemp())
try:
    # ---- C15/C16 park: [Waiting] row must travel WHOLE to ## Later ----------
    print("== C15/C16 parking moves an entire multi-Q row ==")
    bl = TMP / "ZZA Track" / "ZZA Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text(
        "# ZZA Backlog\n\n"
        "## Now\n\n"
        + TWO_Q_ROW.format(status="Waiting 2026-08-09")
        + "\n## Next\n\n## Later\n\n## Done\n",
        encoding="utf-8",
    )
    entries = aq.backlog_entries(bl, {})
    aq.apply_placement_fixes(bl, entries, dt.date(2026, 8, 8))
    after = bl.read_text(encoding="utf-8")
    later, now = section_of(after, "Later"), section_of(after, "Now")

    if "Q2 — second question?" in later:
        ok("Q2 travelled to ## Later with the rest of the row")
    else:
        no("Q2 did NOT travel — the row split at its C20 blank line", after)
    if "Q1 — first question?" in later and "**Next:**" in later:
        ok("Q1 and the Next: sub-bullet travelled too")
    else:
        no("part of the row above the blank line failed to travel", after)
    if "Q2" not in now and "Q1" not in now:
        ok("nothing was left behind under ## Now")
    else:
        no("orphaned sub-bullets stranded under ## Now", now)
    if after.count("Q2 — second question?") == 1:
        ok("Q2 appears exactly once (moved, not copied)")
    else:
        no(f"Q2 appears {after.count('Q2 — second question?')} times", after)

    # ---- C4 sweep: a stale [Done] row must travel whole to ## Done ----------
    print("== C4 stale-[Done] sweep moves an entire multi-Q row ==")
    bl2 = TMP / "ZZB Track" / "ZZB Backlog.md"
    bl2.parent.mkdir(parents=True, exist_ok=True)
    bl2.write_text(
        "# ZZB Backlog\n\n"
        "## Now\n\n"
        + TWO_Q_ROW.format(status="Done 2026-08-01")
        + "\n## Later\n\n## Done\n",
        encoding="utf-8",
    )
    entries2 = aq.backlog_entries(bl2, {})
    aq.apply_c4_fix(bl2, entries2)
    after2 = bl2.read_text(encoding="utf-8")
    done2, now2 = section_of(after2, "Done"), section_of(after2, "Now")

    if "Q2 — second question?" in done2:
        ok("Q2 travelled to ## Done with the rest of the row")
    else:
        no("C4 sweep split the row at its blank line", after2)
    if "Q1" not in now2 and "Q2" not in now2:
        ok("nothing was left behind under ## Now")
    else:
        no("orphaned sub-bullets stranded under ## Now", now2)

    # ---- the row boundary is still a row boundary ---------------------------
    # The fix widens what counts as "inside a row"; assert it did not widen so
    # far that the NEXT row gets dragged along with the one being moved.
    print("== a following top-level row is NOT absorbed into the moved row ==")
    bl3 = TMP / "ZZC Track" / "ZZC Backlog.md"
    bl3.parent.mkdir(parents=True, exist_ok=True)
    bl3.write_text(
        "# ZZC Backlog\n\n"
        "## Now\n\n"
        + TWO_Q_ROW.format(status="Waiting 2026-08-09")
        + "\n- **T002 — a neighbour that must stay put** [Ready] — body. ^T002\n"
        "  - **Next:** stay here.\n\n"
        "## Later\n\n## Done\n",
        encoding="utf-8",
    )
    entries3 = aq.backlog_entries(bl3, {})
    aq.apply_placement_fixes(bl3, entries3, dt.date(2026, 8, 8))
    after3 = bl3.read_text(encoding="utf-8")
    now3, later3 = section_of(after3, "Now"), section_of(after3, "Later")
    if "T002" in now3 and "T002" not in later3:
        ok("the neighbouring [Ready] row stayed under ## Now")
    else:
        no("the mover dragged the following row along", after3)
    if "Q2 — second question?" in later3:
        ok("the parked row still travelled whole")
    else:
        no("row split with a neighbour present", after3)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
