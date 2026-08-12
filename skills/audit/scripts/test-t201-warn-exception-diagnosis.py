#!/usr/bin/env python3
"""test-t201-warn-exception-diagnosis.py — a graded warning is suppressed; an error never is.

**History matters here, because the first version of this file asserted the
opposite of what it asserts now, and both versions were correct at the time.**

`execute_plan` used to rewrite only `fail` → `except`. A `warn` verdict was never
consulted against the grade table, so a well-formed `A` row aimed at a warning
fell through to `stale_exceptions` and was reported as *"exception(s) that did no
work this run (stale, or the rule was out of scope)"* — false in both clauses.
[[ATT|Atticus]] hit that on `R-spine-07` / `Staff/Atticus/Atticus.md`, a deviation
Dan had personally graded `A` (ATT Q002); they wrote the row, watched it report
stale, and **withdrew it**, so the acceptance survived only in that file's Log
where no instrument reads it. The first cut of this test locked in the fixed
*diagnosis* while explicitly leaving the *semantics* to Dan.

Dan answered on 2026-08-11 (T201 Q1 (A)): *"audit grades A through C should
suppress warnings, because we've already decided that that exception is okay."*
So `warn` now suppresses, and the assertions below moved with it.

**What did NOT move is the shape of the guarantee**, and that is what this file
is really protecting:

- a graded A–C row rewrites its verdict to `except` — now for `fail` and `warn`;
- an `error` is never rewritten, because a crashed checker is a bug and a table
  that could hide one is a way to make bugs invisible by hand;
- a row that fired-but-could-not-be-suppressed is reported as exactly that, never
  as stale — the misdiagnosis this file was born to prevent, now living at the
  `error` tier;
- a row whose rule genuinely PASSES is still stale, so widening suppression has
  not traded one misdiagnosis for its opposite.

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


EXC_TMPL = """| Handle | Rule | Target | Grade | Why |
|---|---|---|---|---|
| EX001 | R-demo-07 | Demo.md | {grade} | the children are listed once already |
"""


def run(m, verdict, grade="A"):
    """Build a one-anchor, one-rule plan and run it with `verdict` forced."""
    td = tempfile.mkdtemp()
    root = Path(td) / "Demo"
    (root / "Demo Track").mkdir(parents=True)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    (root / "Demo Track" / "Demo Exceptions.md").write_text(
        EXC_TMPL.format(grade=grade), encoding="utf-8")
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
    #     vacuous. `fail` has been suppressible since F314.
    rep = run(m, "fail")
    check(rep["counts"]["except"] == 1,
          "fixture reaches the table — a `fail` is excepted (control)")
    check(not rep["stale_exceptions"],
          "an excepted fail leaves no stale row (control)")

    # 1 — THE T201 CHANGE. A graded warn is now suppressed, exactly like a fail.
    rep = run(m, "warn")
    check(rep["counts"]["except"] == 1,
          "a graded A row rewrites `warn` → `except` (T201 Q1 (A))")
    check(rep["counts"]["warn"] == 0,
          "the warning is gone from the warn count, not double-counted")
    check(not rep["stale_exceptions"],
          "an excepted warn leaves no stale row")
    check(not rep.get("unsuppressable_exceptions"),
          "an excepted warn is not ALSO reported as unsuppressable")

    # 2 — the grade is still a scale. `D` is a recorded refusal (-08), so it must
    #     suppress neither severity. Without this, widening the severity set
    #     could silently have widened the grade set too.
    rep = run(m, "warn", grade="D")
    check(rep["counts"]["warn"] == 1 and rep["counts"]["except"] == 0,
          "a `D` row suppresses a warn no more than it suppresses a fail")
    rep = run(m, "warn", grade="?")
    check(rep["counts"]["warn"] == 1 and rep["counts"]["except"] == 0,
          "an ungraded `?` row suppresses nothing (R-exception-discipline-06)")

    # 3 — `error` is the line that does not move. A crashed checker is a bug; a
    #     table that could bury one would make bugs invisible by hand.
    rep = run(m, "error")
    check(rep["counts"]["error"] == 1 and rep["counts"]["except"] == 0,
          "an `error` is NEVER excepted, whatever the grade")
    check("EX001" not in rep["stale_exceptions"],
          "a row aimed at an errored rule is NOT reported as stale")
    check("EX001" in rep.get("unsuppressable_exceptions", []),
          "it is reported as fired-but-unsuppressable instead")

    # 4 — a genuinely stale row still reads as stale. Without this the change
    #     would have traded one misdiagnosis for the opposite one.
    rep = run(m, "pass")
    check("EX001" in rep["stale_exceptions"],
          "a row whose rule PASSES is still stale (no over-correction)")
    check(not rep.get("unsuppressable_exceptions"),
          "a passing rule produces no unsuppressable row")

    # 5 — the renderers actually say it. A diagnosis computed and never printed
    #     is the same silence it replaced.
    text = m.render_verdicts(run(m, "error"))
    check("ERRORED" in text and "EX001" in text,
          "render_verdicts names the errored case")
    check("did no work" not in text,
          "render_verdicts does NOT also call it stale")
    text = m.render_verdicts(run(m, "warn"))
    check("EX001" in text and "did no work" not in text,
          "an excepted warn renders as a suppression, not as stale")

    # 6 — the severity set is a named constant, not a literal spelled out at the
    #     one call site. A future widening has to go through it.
    check(m._EXC_SUPPRESSIBLE == frozenset({"fail", "warn"}),
          "_EXC_SUPPRESSIBLE is exactly {fail, warn}")
    check("error" not in m._EXC_SUPPRESSIBLE,
          "`error` is not in the suppressible set")

    print("-" * 40)
    print(f"T201 warn-exception suppression: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
