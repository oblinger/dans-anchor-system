#!/usr/bin/env python3
"""test-t201-warn-exception-diagnosis.py — an accepted warning is not a stale row.

`execute_plan` rewrites `fail` → `except`; a `warn` verdict is never consulted
against the grade table. Whether that should change is Dan's call on his own
table and is NOT decided here. What *was* wrong regardless of that call is the
**diagnosis**: a row aimed at a warning fell through to `stale_exceptions` and
was reported as *"exception(s) that did no work this run (stale, or the rule was
out of scope)"* — which is false in both clauses. The rule is in scope, the row
is well-formed, the target is right, and the rule really did fire.

[[ATT|Atticus]] hit this on `R-spine-07` / `Staff/Atticus/Atticus.md`, a
deviation Dan had personally graded `A` (ATT Q002). They wrote the row, watched
it report stale, and **withdrew it** — a row that reads as coverage while
suppressing nothing is the failure the whole family exists to prevent. The
acceptance now survives only in that file's Log, where no instrument reads it.

The warning tier is where the judgment calls live (`R-rocks-05`, `R-spine-07`,
`R-rocks-04`'s expansion half), so it is exactly where accepted deviations
cluster — which is why the misdiagnosis bites harder than the count suggests.

Usage: python3 test-t201-warn-exception-diagnosis.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ap"] = m
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


EXC = """| Handle | Rule | Target | Grade | Why |
|---|---|---|---|---|
| EX001 | R-demo-07 | Demo.md | A | the children are listed once already |
"""


def run(m, verdict):
    """Build a one-anchor, one-rule plan and run it with `verdict` forced."""
    td = tempfile.mkdtemp()
    root = Path(td) / "Demo"
    (root / "Demo Track").mkdir(parents=True)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    (root / "Demo Track" / "Demo Exceptions.md").write_text(EXC, encoding="utf-8")
    tgt = root / "Demo.md"
    tgt.write_text("# Demo\nbody.\n", encoding="utf-8")
    plan = {"anchor_root": str(root),
            "groupings": [{"rules": [{"id": "R-demo-07", "check": "noop",
                                      "targets": ["Demo.md"],
                                      "_target_paths": [str(tgt)]}]}]}
    orig = m.run_checker
    m.run_checker = lambda check_, target, anchor_root: (verdict, "the detail")
    try:
        return m.execute_plan(plan, None)
    finally:
        m.run_checker = orig


def main():
    m = _load()

    # 0 — the fixture must actually reach the row, or every assertion below is
    #     vacuous. A `fail` is the case the engine DOES suppress.
    rep = run(m, "fail")
    check(rep["counts"]["except"] == 1,
          "fixture reaches the table — a `fail` is excepted (control)")
    check(not rep["stale_exceptions"],
          "an excepted fail leaves no stale row (control)")

    # 1 — THE DEFECT. A warn is not suppressed, and must not be called stale.
    rep = run(m, "warn")
    check(rep["counts"]["warn"] == 1,
          "a warn stays a warn — this change suppresses nothing new")
    check("EX001" not in rep["stale_exceptions"],
          "the row is NOT reported as stale (the misdiagnosis)")
    check("EX001" in rep.get("unsuppressable_exceptions", []),
          "the row is reported as fired-but-unsuppressable instead")

    # 2 — a genuinely stale row still reads as stale. Without this the fix would
    #     have traded one misdiagnosis for the opposite one.
    rep = run(m, "pass")
    check("EX001" in rep["stale_exceptions"],
          "a row whose rule PASSES is still stale (no over-correction)")
    check(not rep.get("unsuppressable_exceptions"),
          "a passing rule produces no unsuppressable row")

    # 3 — the renderers actually say it. A diagnosis computed and never printed
    #     is the same silence it replaced.
    rep = run(m, "warn")
    text = m.render_verdicts(rep)
    check("cannot suppress" in text and "EX001" in text,
          "render_verdicts names the case")
    check("did no work" not in text,
          "render_verdicts does NOT also call it stale")

    print("-" * 40)
    print(f"T201 warn-exception diagnosis: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
