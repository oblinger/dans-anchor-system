#!/usr/bin/env python3
"""test-t042-phase2.py — retiring a spent ## Open Questions block.

Phase 2 drops the block once nothing pending remains. Two things went wrong
(T042), and a third reported symptom turned out not to be a defect at all:

  * FIRED TOO RARELY — emptiness was "no non-blank lines", so one leftover
    placeholder line kept a spent block alive forever. audit-q C21 then flagged
    it, groom-list counted it, and the stop-gate blocked on it, with no
    sanctioned verb able to clear it (the region is Edit-hook-blocked).
  * NO REPAIR PATH — `revalidate` refreshed the stamp but never transitioned.
  * REPORTED, NOT REPRODUCED — "the drop also deletes an already-migrated
    resolved archive." It cannot: `_find_h2` ends the block at the next H2, so a
    resolved section further down is never inside the removed span. Replayed
    against the real pre-loss file (kmr 542fc5134) the archive survives intact.
    The last two cases below pin that invariant so a future change can't quietly
    introduce the bug everyone believed was already there.

    python3 test-t042-phase2.py
"""
import importlib.util
import pathlib

SCRIPT = pathlib.Path(__file__).parent / "backlog-edit.py"
_spec = importlib.util.spec_from_file_location("backlog_edit", SCRIPT)
be = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(be)

STAMP = "<!-- state:q ab -->"
results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def pending_q(n):
    return [f"- **Q{n} — Something** — body ^F001-Q{n}", "  - **(A)** one",
            "  - **Recommendation:** None"]


print("Phase 2 fires when nothing pending remains")

spent = ["# F001", "", "## Open Questions", "", STAMP, "", "## Summary", "", "prose", ""]
out, dropped = be.drop_open_questions_if_empty(list(spent))
check("a bare spent block is retired", dropped, True)
check("## Summary survives", "## Summary" in out, True)

stale = ["# F001", "", "## Open Questions", "", STAMP, "", "*(none pending)*", "",
         "## Summary", "", "prose", ""]
out, dropped = be.drop_open_questions_if_empty(list(stale))
check("a leftover placeholder no longer blocks the drop", dropped, True)
check("the placeholder goes with the block", any("none pending" in x for x in out), False)

out2, dropped2 = be.drop_open_questions_if_empty(list(out))
check("idempotent — a second call is a no-op", dropped2, False)
check("...and changes nothing", out2, out)

print("Phase 2 stays its hand while anything is pending")

live = ["# F001", "", "## Open Questions", "", STAMP, ""] + pending_q(1) + ["", "## Summary", ""]
out, dropped = be.drop_open_questions_if_empty(list(live))
check("a pending Q keeps the block", dropped, False)
check("the pending Q survives", any("**Q1" in x for x in out), True)

pen = ["# F001", "", "## Open Questions", "", STAMP, "", "### Resolved", "",
       "### Q1 — thing (resolved)", "", "## Summary", ""]
out, dropped = be.drop_open_questions_if_empty(list(pen))
check("an in-block holding pen keeps the block", dropped, False)

print("the drop never reaches a resolved archive (the misdiagnosed defect)")

archived = ["# F001", "", "## Open Questions", "", STAMP, "", "## Summary", "", "prose", "",
            "## Resolved", "", "### Q1 — earlier (resolved)", "**Choice:** (A)", ""]
out, dropped = be.drop_open_questions_if_empty(list(archived))
check("block retired", dropped, True)
check("## Resolved survives", "## Resolved" in out, True)
check("the archived Q body survives", any("**Choice:** (A)" in x for x in out), True)

adjacent = ["# F001", "", "## Open Questions", "", STAMP, "",
            "## Resolved", "", "### Q1 — earlier (resolved)", "**Choice:** (A)", ""]
out, dropped = be.drop_open_questions_if_empty(list(adjacent))
check("archive immediately below the block still survives",
      dropped and "## Resolved" in out and any("**Choice:** (A)" in x for x in out), True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
