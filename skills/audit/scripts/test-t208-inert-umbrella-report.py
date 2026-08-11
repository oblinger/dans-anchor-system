#!/usr/bin/env python3
"""T208 — an umbrella that arms nothing must be REPORTED, not discovered.

`audit-plan.py` resolves a fixed umbrella — `R-doc` in doc mode, `R-anchor` in
anchor mode — and nothing reads a per-anchor ruleset declaration. So an
`include::` in any other umbrella is an instruction to do nothing, while looking
exactly like adoption: the recipe lists the rules, the tier reads `(checked)`,
and the sweep runs green because no rule ran. `R-facet` documented itself as the
thing an anchor "adopts" for its whole life; three separate defects (T164, the
`R-stone` arming, T208) each began with someone believing it.

The measure is not "is this umbrella reachable" — a catalog whose members are all
armed elsewhere is harmless and must not nag, or the report becomes furniture
nobody reads. The measure is **how many rulesets the umbrella is the sole route
to**, since those are armed by nothing at all, and that count falls to zero as
sets get named in `R-doc`/`R-anchor`.

Run: python3 test-t208-inert-umbrella-report.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "ap", Path(__file__).resolve().parent / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def ruleset(name, includes=None, rules=1):
    """A minimal but real RULESET block — the parser needs a tier-suffixed RULE
    heading to count a rule, which is what makes a set a leaf rather than a
    pure umbrella."""
    out = [f"# RULESET {name}"]
    if includes:
        out.append("include:: " + ", ".join(f"[[{i}]]" for i in includes))
    out.append(f"description:: fixture {name}")
    out.append("")
    for i in range(1, rules + 1):
        out.append(f"### RULE {name}-0{i} — fixture rule (stated)")
        out.append("")
        out.append("**Why:** fixture.")
        out.append("")
    return "\n".join(out) + "\n"


CORPUS = {
    # The two roots. Between them they reach R-live and nothing else.
    "R-doc": ruleset("R-doc", ["R-live"], rules=0),
    "R-anchor": ruleset("R-anchor", ["R-live"], rules=0),
    "R-live": ruleset("R-live"),
    # The defect shape: an umbrella outside the closure, sole route to R-orphan.
    "R-inert": ruleset("R-inert", ["R-orphan"], rules=0),
    "R-orphan": ruleset("R-orphan"),
    # The benign shape: outside the closure, but everything it names is armed.
    "R-catalog": ruleset("R-catalog", ["R-live"], rules=0),
    # Outside the closure with rules but NO include:: — not an umbrella at all.
    "R-leaf": ruleset("R-leaf"),
}


def report():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, text in CORPUS.items():
            (root / f"{name}.md").write_text(text, encoding="utf-8")
        saved_root, saved_idx = ap.REPO_ROOT, ap._MD_INDEX
        ap.REPO_ROOT, ap._MD_INDEX = root, None
        try:
            warns = []
            reachable = set()
            for u in ("R-doc", "R-anchor"):
                reachable |= {r["name"] for r in ap.flatten_umbrella(u, warns)}
            lines = ap.inert_umbrellas(reachable, ("R-doc", "R-anchor"))
        finally:
            ap.REPO_ROOT, ap._MD_INDEX = saved_root, saved_idx
    return reachable, lines


def main():
    reachable, lines = report()
    named = {ln.split(" — ", 1)[0] for ln in lines}

    # The fixture only means anything if the closure came out as designed.
    check("fixture control — the closure reaches exactly R-live",
          reachable, {"R-live"})

    check("the inert umbrella is reported", "R-inert" in named, True)
    check("it says how many sets it is the sole route to",
          any(ln.startswith("R-inert") and "SOLE route to 1" in ln for ln in lines), True)
    check("and names them, so the reader can act without a second query",
          any(ln.startswith("R-inert") and "R-orphan" in ln for ln in lines), True)

    # Each of these is a way the report could become noise and stop being read.
    check("a root umbrella is never reported against itself",
          {"R-doc", "R-anchor"} & named, set())
    check("a leaf outside the closure is not reported — it is not an umbrella",
          "R-leaf" in named, False)
    check("a catalog whose members are all armed is reported as costing nothing",
          any(ln.startswith("R-catalog") and "costing nothing" in ln for ln in lines), True)
    check("that catalog is NOT described as the sole route to anything",
          any(ln.startswith("R-catalog") and "SOLE route" in ln for ln in lines), False)

    # The whole point: reporting converges. Arming R-orphan must silence R-inert.
    CORPUS["R-doc"] = ruleset("R-doc", ["R-live", "R-orphan"], rules=0)
    try:
        reachable2, lines2 = report()
        check("arming the orphan widens the closure",
              reachable2, {"R-live", "R-orphan"})
        check("arming the orphan drops R-inert to a costs-nothing catalog",
              any(ln.startswith("R-inert") and "costing nothing" in ln for ln in lines2), True)
        check("and no umbrella is left claiming a sole route",
              any("SOLE route" in ln for ln in lines2), False)
    finally:
        CORPUS["R-doc"] = ruleset("R-doc", ["R-live"], rules=0)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILING: {', '.join(FAILURES)}")
        return 1
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
