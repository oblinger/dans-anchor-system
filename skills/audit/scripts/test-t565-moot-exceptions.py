#!/usr/bin/env python3
"""T565 — R-exception-discipline-13: a row whose rule now PASSES is moot.

Dan, 2026-08-20: *"How come we haven't graded the exceptions for Eli. And I
wonder if we shouldn't be grading the exceptions for everybody."*

The answer turned out to be that grading was the wrong act. Of the vault's four
exception tables, **six of the fourteen rows named a finding that no longer
existed** — [[Eli Exceptions]]'s five, all repaired upstream by TINK T561, and
[[TINK Exceptions]]'s one, repaired by an exemption the checker grew itself.
Grading any of them `A` would have converted a working rule into a permanently
blindfolded one, and nothing would ever have fired again to reveal it.

The engine could not say so. Two separate messages hid the state:

  - a **proposed** (`?`) row read *"ungraded — suppresses nothing until you
    grade it"*, which asks for precisely the harmful action; and
  - a **graded** row was folded into *"stale, or the rule was out of scope"*,
    honest but discarding a distinction the engine can actually make — a `pass`
    is a verdict, and only "the rule never ran here" is undecidable.

§5 is the case the fix must NOT swallow, and it is why `stale` survives at all:
[[Warden Exceptions]]'s eight graded rows also did no work that run, but their
rules never ran at that scope, so calling them moot would be a fabricated
verdict. Measured against the live vault the day this landed: Eli 5 moot, TINK
1 moot, ATT 3 genuinely live, Warden 8 correctly undecidable.

Run: python3 test-t565-moot-exceptions.py
"""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
RULESET = HERE.parent.parent.parent / "rulesets" / "R-exception-discipline.md"


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_t565", HERE / "audit-plan.py")

FAILURES = []
HEADER = "| EX | Rule | Target | Grade | Justification |\n|---|---|---|---|---|\n"


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def build(td, rows, *, passing):
    """An anchor whose doc PASSES or FAILS `regex_present`, plus a table."""
    root = Path(td)
    (root / ".anchor").write_text("slug: FIX\n", encoding="utf-8")
    doc = root / "FIX Thing.md"
    doc.write_text("# FIX Thing\n" + ("SENTINEL\n" if passing else "nope.\n"),
                   encoding="utf-8")
    trk = root / "FIX Track"
    trk.mkdir(exist_ok=True)
    (trk / "FIX Exceptions.md").write_text(
        "# FIX Exceptions\nAccepted deviations.\n\n" + HEADER + rows,
        encoding="utf-8")
    return root, doc


def plan_for(root, targets, rule="R-spine-02"):
    return {"anchor_root": str(root),
            "groupings": [{"rules": [{
                "id": rule,
                "check": "regex_present ^SENTINEL$",
                "targets": [p.name for p in targets],
                "_target_paths": [str(p) for p in targets]}]}]}


print("1. A PROPOSED row whose rule now passes is moot, not awaiting a grade")
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-spine-02 | FIX Thing.md | ? | proposed. |\n",
                      passing=True)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("the rule passes", [r["status"] for r in rep["results"]], ["pass"])
    check("the row is reported moot", rep.get("moot_exceptions"), ["EX001"])
    txt = ap.render_verdicts(rep)
    check("...and the render says MOOT", "MOOT" in txt, True)
    check("...and asks for RETIREMENT", "Retire the row" in txt, True)
    check("...and names the harm of doing the other thing",
          "suppress a rule that is working" in txt, True)
    check("...and no longer says 'until you grade it'",
          "until you grade it" in txt, False)

print("2. A proposed row whose rule still FAILS is untouched — this is the gate")
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-spine-02 | FIX Thing.md | ? | proposed. |\n",
                      passing=False)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("the finding still fails", [r["status"] for r in rep["results"]], ["fail"])
    check("nothing is moot", rep.get("moot_exceptions"), [])
    check("...and the old message is intact",
          "until you grade it" in ap.render_verdicts(rep), True)

print("3. A GRADED row whose rule now passes is moot, and leaves `stale`")
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-spine-02 | FIX Thing.md | A | accepted. |\n",
                      passing=True)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("the row is moot", rep.get("moot_exceptions"), ["EX001"])
    # The whole point of the split: `stale` must stop claiming this one, or the
    # answerable case stays buried in the unanswerable bucket.
    check("...and is NOT also reported stale", rep.get("stale_exceptions"), [])
    txt = ap.render_verdicts(rep)
    check("...the render names it as covering a passing rule",
          "now PASSES on their own target" in txt, True)
    check("...and does not call it stale", "did no work this run" in txt, False)

print("4. A graded row that IS doing work stays untouched")
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-spine-02 | FIX Thing.md | A | accepted. |\n",
                      passing=False)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("the finding is suppressed", [r["status"] for r in rep["results"]], ["except"])
    check("nothing is moot", rep.get("moot_exceptions"), [])
    check("nothing is stale", rep.get("stale_exceptions"), [])

print("5. A row whose rule NEVER RAN here stays `stale`, never moot")
# Warden's eight. Calling these moot would be a fabricated verdict: no run
# produced a pass on their target, so the engine genuinely cannot tell a
# repaired deviation from a rule that is out of scope. `stale` exists for
# exactly this remainder and must keep it.
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-naming-01 | FIX Thing.md | A | accepted. |\n",
                      passing=True)
    rep = ap.execute_plan(plan_for(root, [doc], rule="R-spine-02"), None)
    check("the out-of-scope row is stale", rep.get("stale_exceptions"), ["EX001"])
    check("...and is NOT moot", rep.get("moot_exceptions"), [])
    check("...and the render still hedges honestly",
          "stale, or the rule was out of scope" in ap.render_verdicts(rep), True)

print("6. Target scoping still holds — a pass elsewhere does not make a row moot")
with tempfile.TemporaryDirectory() as td:
    root, doc = build(td, "| EX001 | R-spine-02 | FIX Other.md | ? | proposed. |\n",
                      passing=True)
    check("the row's target is a different file", (root / "FIX Other.md").exists(), False)
    rep = ap.execute_plan(plan_for(root, [doc]), None)
    check("a pass on FIX Thing.md does not moot a row aimed at FIX Other.md",
          rep.get("moot_exceptions"), [])

print("7. The ruleset states it (the T552 parity discipline)")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-exception-discipline-13\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-exception-discipline-13 exists", bool(m), True)
if m:
    body = m.group(0)
    check("...covers proposed AND graded rows", "proposed (`?`) or graded" in body, True)
    check("...names the retire action", "retired" in body, True)
    check("...carries the measured six-of-fourteen", "six of the fourteen" in body, True)
    check("...keeps `stale` for the undecidable remainder",
          "never ran here" in body, True)
    check("...names its guard test", "test-t565-moot-exceptions.py" in body, True)

print()
if FAILURES:
    print(f"test-t565-moot-exceptions: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t565-moot-exceptions: all checks pass")
