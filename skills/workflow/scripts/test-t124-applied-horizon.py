#!/usr/bin/env python3
"""T124 — `--horizon` was silently ignored for `[Waiting]` rows, and reported success.

`state set <anchor> Backlog <row> --horizon Now` on a `[Waiting]` row printed
`updated <row> in Now [Waiting]` and exited 0, while the row stayed physically
under `## Later`. Reproduced three times by ATT; the same command on the same row
after its bracket changed to `[Questions]` moved it correctly.

**The mechanism is not in `state`'s write path.** `perform_edit` moves a
`[Waiting]` row exactly like any other. What moves it back is `refresh_q_md` →
`audit-q --fix` → **C15**, which parks `[Watching]`/`[Waiting]` rows in `##
Later` by policy. `perform_edit` builds the summary line before any of that runs,
so it could only ever report the horizon that was *requested*.

**The policy stays.** 109 Later Waiting/Blocked rows exist vault-wide and are
correctly quiet, and Dan already ruled on this axis — *"a blocker for something
parked in Later is not a blocker, it is a note"* (queries-render.py, 2026-07-30).
Admitting them to `## Blocked` would put 27 rows on TINK's daily surface alone.

**What was actually missing** is that nothing told the author their row had just
gone silent: under `## Later`, `_row_should_render` admits only
`Questions`/`Verify*`, so a parked `[Waiting]` row renders in no section of
queries.md at all. That is what stranded two live ATT rows.

    python3 test-t124-applied-horizon.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

# `state` carries no `.py`, so it needs an explicit source loader — same shape
# test-f259 and test-f293 use.
_HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("state_mod", str(_HERE / "state"))
_spec = importlib.util.spec_from_loader("state_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["state_mod"] = st
_loader.exec_module(st)
be = st.be

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


print("_renders_under_later — which brackets survive the parking")

# Mirrors `_row_should_render`'s Later arm. These four are the whole point: a
# parked Waiting/Blocked row is invisible, a parked Questions/Verify row is not.
for bracket, visible in (("Questions", True), ("4 Questions", True),
                         ("Verify", True), ("Verify-by 2026-09-01", True),
                         ("Waiting", False), ("Waiting 7d", False),
                         ("Blocked F230", False), ("Watching", False),
                         ("Ready", False), ("", False)):
    check(f"[{bracket or '—'}] renders under Later: {visible}",
          st._renders_under_later(bracket), visible)


print("\n_row_horizon_on_disk — what the FILE says, not what the writer meant")

_td = tempfile.TemporaryDirectory()
bl = Path(_td.name) / "T Backlog.md"
bl.write_text(
    "# T Backlog\n\n## Now\n\n"
    "- **T900 — an active row** [Ready] — body. ^T900\n"
    "\n## Later\n\n"
    "- **T901 — a parked row** [Waiting] — waiting on an event. ^T901\n",
    encoding="utf-8")

check("a Now row reports Now", st._row_horizon_on_disk(bl, "T900"), "Now")
check("a Later row reports Later", st._row_horizon_on_disk(bl, "T901"), "Later")
check("an absent row reports nothing",
      st._row_horizon_on_disk(bl, "T999"), None)
# The reporter must never be the thing that raises on a file the writer already
# damaged — it runs on the failure path.
check("an unreadable path reports nothing rather than raising",
      st._row_horizon_on_disk(Path(_td.name) / "no-such.md", "T900"), None)


print("\nThe write path itself was never the bug — perform_edit moves it")

_td2 = tempfile.TemporaryDirectory()
bl2 = Path(_td2.name) / "T Backlog.md"
bl2.write_text(
    "# T Backlog\n\n## Now\n\n## Later\n\n"
    "- **T900 — a parked row** [Waiting] — waiting on an event. ^T900\n",
    encoding="utf-8")
res = be.perform_edit(bl2, "Now", "T900", "same", None, None, False, False)
check("perform_edit honours --horizon on a [Waiting] row",
      st._row_horizon_on_disk(bl2, "T900"), "Now")
check("...and its summary names that horizon",
      "in Now" in res["summary"], True)
# ...which is exactly why the summary alone cannot be trusted: it is built here,
# before audit-q C15 has had its say.
check("the summary is built before any post-edit pass",
      res["h2_name"], "Now")


print("\nA terminal row moving to `## Done` is not a surprise")

# The note exists to catch a row that went somewhere the caller did not ask for.
# `## Done` is where a Done row belongs, so reporting that move would cry wolf on
# the commonest write there is — and a note that fires when nothing is wrong is
# how a true one gets ignored.
src = (_HERE / "state").read_text(encoding="utf-8")
blk = src.split("summary = result[\"summary\"]", 1)[1].split("print(f\"{slug}: {summary}\")", 1)[0]
check("the note is suppressed for a terminal row",
      'startswith("Done")' in blk and "not terminal" in blk, True)
check("...and still fires for every non-terminal status",
      'status != "delete" and not terminal' in blk, True)


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
