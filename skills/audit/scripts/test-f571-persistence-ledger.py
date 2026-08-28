#!/usr/bin/env python3
"""T571 — a finding that survives a sweep unchanged must say so.

Routing a finding to another anchor reported success and then graded nothing.
Measured 2026-08-20 and re-probed 2026-08-27: of six findings routed on
2026-08-09, four were still byte-identical eleven and eighteen days later, and
no surface anywhere said so. Each sweep re-found them and reported them exactly
as it reports a finding seen for the first time, because nothing anywhere held
a first-seen date — and without one, "still broken" and "broken again" are
indistinguishable observations.

C59 is that memory. `update_persistence_ledger` records every finding's
first-seen date, forgets the ones that are gone, and returns whatever has been
open PERSIST_DAYS or more; `check_c59_persistent_findings` turns that into
exactly one finding on the sweeping anchor's backlog.

The two assertions the row asked for are the two halves of the same claim:
a routed-and-unfixed finding yields exactly one TINK finding, and a
routed-and-fixed one yields zero.

    python3 test-f571-persistence-ledger.py
"""
import importlib.util
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

_S = (Path(__file__).parent / "audit-q.py").resolve()
_spec = importlib.util.spec_from_file_location("aq", _S)
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


_td = tempfile.TemporaryDirectory()
TMP = Path(_td.name)
LEDGER = TMP / "seen.json"

# A TINK backlog for the finding to land on, and an EMBER tree for it to be
# found in — the shape of the live case, where the sweep is TINK's and the
# unfixed finding is someone else's.
for owner in ("TINK", "EMBER"):
    trk = TMP / owner / f"{owner} Track"
    trk.mkdir(parents=True)
    (trk / f"{owner} Backlog.md").write_text("# Backlog\n", encoding="utf-8")
BACKLOGS = {o: TMP / o / f"{o} Track" / f"{o} Backlog.md" for o in ("TINK", "EMBER")}

aq.VAULT_ROOT = TMP


def finding(rel, code="C19", msg="option bullets missing"):
    return aq.Finding(severity="error", surface_file=TMP / rel, surface_line=7,
                      code=code, message=msg, mechanically_fixable=False)


TODAY = date.today()
OLD = (TODAY - timedelta(days=11)).isoformat()
NOW = TODAY.isoformat()

f_stale = finding("EMBER/EMBER Design/EMBER Features/EMBER007 - a.md")
f_fresh = finding("EMBER/EMBER Design/EMBER Features/EMBER009 - b.md")

print("A first sight is not yet a persistence")

out = aq.update_persistence_ledger([f_stale, f_fresh], today=NOW, path=LEDGER)
check("nothing is persistent on the first run", out, [])
check("...but both were recorded", len(json.loads(LEDGER.read_text())), 2)
check("and no finding is raised", aq.check_c59_persistent_findings(out, BACKLOGS), [])

print("\nThe same finding, eleven days later — the live T571 shape")

# Rewind both first-seen dates: the same two findings reproduce unchanged.
LEDGER.write_text(json.dumps({k: OLD for k in json.loads(LEDGER.read_text())}),
                  encoding="utf-8")
out = aq.update_persistence_ledger([f_stale, f_fresh], today=NOW, path=LEDGER)
check("both are reported as persistent", len(out), 2)
check("...with their true age, not the age of this run",
      sorted({age for _k, _f, age in out}), [11])

found = aq.check_c59_persistent_findings(out, BACKLOGS)
check("a routed-and-unfixed finding yields exactly ONE finding", len(found), 1)
check("...on the sweeping anchor's backlog, not the target's",
      found[0].surface_file, BACKLOGS["TINK"])
check("...coded C59", found[0].code, "C59")
check("...and it names how many and how old",
      ("2 finding(s)" in found[0].message and "oldest 11d" in found[0].message),
      True)

print("\nFixing the finding clears it — and leaves no residue")

# EMBER007 is fixed; only EMBER009 still reproduces. It is still 11 days old,
# so exactly one persistent item should remain.
out = aq.update_persistence_ledger([f_fresh], today=NOW, path=LEDGER)
check("the fixed finding is no longer persistent", len(out), 1)
check("...and is forgotten by the ledger rather than kept as its own stale row",
      sorted(json.loads(LEDGER.read_text())),
      [aq._persist_key(f_fresh)])

out = aq.update_persistence_ledger([], today=NOW, path=LEDGER)
check("with everything fixed, nothing is persistent", out, [])
check("a routed-and-fixed finding yields ZERO findings",
      aq.check_c59_persistent_findings(out, BACKLOGS), [])
check("...and the ledger is empty, not merely quiet",
      json.loads(LEDGER.read_text()), {})

print("\nThe clock does not restart when a finding moves down its file")

LEDGER.write_text(json.dumps({aq._persist_key(f_stale): OLD}), encoding="utf-8")
moved = finding("EMBER/EMBER Design/EMBER Features/EMBER007 - a.md")
moved.surface_line = 412            # the whole reason line is not in the key
out = aq.update_persistence_ledger([moved], today=NOW, path=LEDGER)
check("a shifted line number keeps the original first-seen date",
      [(f, a) for _k, f, a in out], [(OLD, 11)])

print("\nA read-only pass reports without recording")

before = LEDGER.read_text()
out = aq.update_persistence_ledger([f_fresh], today=NOW, write=False, path=LEDGER)
check("--dry leaves the ledger byte-identical", LEDGER.read_text(), before)

# `--scope all` sees a different, wider population than `--scope q` (204
# findings against 14 on the same vault). If both wrote, each pass would prune
# the other's keys and alternating between them would reset every clock.
wider = [f_stale] + [finding(f"EMBER/unreached-{i}.md") for i in range(5)]
out = aq.update_persistence_ledger(wider, today=NOW, write=False, path=LEDGER)
check("a wider read-only scope prunes nothing", LEDGER.read_text(), before)
check("...and still reports what the narrow ledger already knew",
      [(k.split("|")[0].rsplit("/", 1)[-1], a) for k, _f, a in out],
      [("EMBER007 - a.md", 11)])

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
