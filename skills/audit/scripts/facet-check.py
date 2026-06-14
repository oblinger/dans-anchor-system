#!/usr/bin/env python3
"""facet-check.py — run the R-facet-spec mechanical checkers on a single facet spec.

Usage:  facet-check.py "<path to FCT <Name>.md>"

Prints PASS/FAIL per mechanical rule and exits non-zero if any fail. Thin wrapper
around the checker library in audit-plan.py (the F161 engine), so the rules stay in
one place. Used by /audit and by humans to spot-check one facet at a time."""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)

CHECKS = [
    ("R-facet-spec-02 H1 form", "facet_h1_form"),
    ("R-facet-spec-03 registered", "facet_registered"),
    ("R-facet-spec-04 frontmatter description", "frontmatter_has description"),
    ("R-facet-spec-05 masthead", "facet_dispatch_top"),
    ("R-facet-spec-07 TLDR if substantial", "facet_tldr_if_substantial"),
    ("R-facet-spec-10 cardinality declared", "facet_cardinality_declared"),
    ("R-facet-spec-15 triggers section", "triggers_section_iff_declared"),
    ("R-facet-spec-18 has ruleset", "facet_has_ruleset"),
    ("R-facet-spec-22 has BRIEF", "regex_present ^#+\\s*BRIEF"),
]


def main():
    if len(sys.argv) < 2:
        print("usage: facet-check.py <path to FCT <Name>.md>", file=sys.stderr)
        sys.exit(2)
    p = pathlib.Path(sys.argv[1]).resolve()
    if not p.is_file():
        print(f"facet-check: not a file: {p}", file=sys.stderr)
        sys.exit(2)
    nfail = 0
    for label, chk in CHECKS:
        status, detail = ap.run_checker(chk, p, ap.REPO_ROOT)
        if status != "pass":
            nfail += 1
        mark = "PASS" if status == "pass" else "FAIL"
        print(f"  {mark}  {label}" + (f"  — {detail}" if status != "pass" else ""))
    print(f"{p.name}: {len(CHECKS) - nfail}/{len(CHECKS)} pass")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
