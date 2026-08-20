#!/usr/bin/env python3
"""T559 — a checker and its rule text may not name different fields.

A ruleset is the one copy nothing verifies. [[ATT|Atticus]], generalizing from
T552: *"a grep for the behaviour would have found the three sites; only a grep
for the rule ID finds the fourth. If R-backlog-04's text is the source the
checkers are meant to implement, it might be worth a test that fails when a
checker and its ruleset disagree."*

**What this checks, and it is deliberately the narrow half.** For every rule
carrying a bare `check:: <fn>`, every FIELD NAME the checker matches on — a
`**Verify:**`-shaped bold-colon field, or a `probe::`-shaped declared key — must
appear somewhere in that rule's prose. Nothing here understands English; both
halves are greppable, which is the property that keeps a test alive. T552's own
`test-t552-watching-accepts-probe.py` §4 asserts exactly this for one rule; this
is that assertion run over the whole corpus.

**What it deliberately does NOT check, measured rather than assumed.**

  - **Rule ↔ checker registration was already built** and is not repeated here.
    `verify_registrations` (F289) checks both directions — a `check::` naming no
    registered checker, and a registered checker no rule invokes — and
    `test-f289-checker-registration.py` pins it. T559's Next named this as the
    first tractable core; the honest finding is that it exists.

  - **Whether the prose is TRUE is not mechanically reachable, and the
    counterexample is a day old.** R-spine-09's scope read *"an anchor entry
    page, read from `.anchor`"*, and T556 assumed from that a notebook with no
    `.anchor` would fall outside the rule. It does not: `entry_names` is a union
    seeded unconditionally with the folder basename, so any `X/X.md` fronts its
    folder with no `.anchor` anywhere. The prose named the right field and
    described its semantics wrongly — every field-parity check in this file
    passes on it, and only running a fixture both ways caught it. That is the
    ceiling on this approach, and it is worth writing down next to the check so
    a future reader does not mistake a green run for a verified ruleset.

  - **Parameterized checkers are out of scope by construction**, not skipped
    quietly. 18 of 170 pairs spell `check:: regex_present ^# [^-]` or
    `check:: frontmatter_has description` — the argument IS the contract, it is
    already in the ruleset where a reader sees it, and there is no per-rule
    Python to disagree with. The count is printed on every run.

**The zero this reports is an earned one.** Injecting the T552 drift — deleting
`Probe` from R-backlog-04's prose while its checker still matches
`- **Probe:**` — makes it fire; `test-t559-ruleset-parity.py` §3 pins that, so
a green run cannot come from a detector that sees nothing.

    python3 ruleset-parity.py            # check
    python3 ruleset-parity.py --report   # show every measured pair's tokens
"""
import ast
import importlib.util
import inspect
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_ap_parity", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["_ap_parity"] = ap
_spec.loader.exec_module(ap)

# A bold-colon field, as a rule's prose and a checker's literal both spell it:
# `- **Verify:**`, `**Probe:**`. The colon is REQUIRED — without it the pattern
# swallows ordinary emphasis (`**Warden rule**`, `**Every one of them
# resolves**`) and reports five prose fragments as missing fields.
_BOLD_FIELD = re.compile(r"\\?\*\\?\*([A-Z][A-Za-z][A-Za-z /-]{0,24}?):\\?\*\\?\*")

_DECLARED_KEY = re.compile(r"\b([a-z][a-z_-]{2,24})::")

# Keys that belong to RULESET GRAMMAR rather than to any one rule's vocabulary.
# A checker that parses ruleset syntax — `all_rules_have_tier`, `h1_present`,
# `exceptions_table_wellformed` — matches these generically, in every set it
# reads, so requiring each rule's prose to name them asks the wrong question and
# produced seven of the eight findings in the first cut.
_GRAMMAR_KEYS = {
    "where", "check", "fix", "confirm", "mend", "include", "import",
    "group", "description", "requires", "subsystem", "selector-note", "assoc",
}


def field_tokens(text: str) -> set[str]:
    """The vocabulary a piece of text names — bold-colon fields and non-grammar
    declared keys."""
    out = {m.group(1).strip() for m in _BOLD_FIELD.finditer(text)}
    for m in _DECLARED_KEY.finditer(text):
        if m.group(1) not in _GRAMMAR_KEYS:
            out.add(m.group(1) + "::")
    return out


def checker_tokens(src: str) -> set[str]:
    """The fields a checker MATCHES on — string literals only.

    Docstrings are excluded by the same walk that finds them: a docstring IS an
    `ast.Constant`, so it would count, and a checker that merely discusses a
    field in prose would then oblige its rule to name it. Stripped explicitly
    below rather than left to chance.
    """
    try:
        tree = ast.parse(src.lstrip())
    except SyntaxError:
        return set()
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            d = ast.get_docstring(node, clean=False)
            if d:
                docstrings.add(d)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in docstrings:
                continue
            out |= field_tokens(node.value)
    return out


def rule_prose(rs: dict, rule_id: str) -> str:
    try:
        text = (ap.REPO_ROOT / rs["source"]).read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(rf"^#+\s*RULE {re.escape(rule_id)}\b.*?(?=^#+\s*RULE |\Z)",
                  text, re.S | re.M)
    return m.group(0) if m else ""


def scan():
    """[(rule_id, checker, missing_tokens)] plus the population counts."""
    rulesets = ap.all_corpus_rulesets()
    ap.register_imports(rulesets)
    reg = ap.registry()
    findings, parameterized, unresolved, measured = [], 0, [], 0
    for rs in rulesets:
        for r in rs["rules"]:
            fn = r.get("check")
            if not fn:
                continue
            if " " in fn:
                parameterized += 1
                continue
            impl = reg.get(fn)
            try:
                src = inspect.getsource(impl)
            except Exception:
                unresolved.append((r["id"], fn))
                continue
            measured += 1
            prose = rule_prose(rs, r["id"])
            if not prose:
                continue
            gone = sorted(
                t for t in checker_tokens(src)
                if (t[:-2] if t.endswith("::") else t) not in prose
            )
            if gone:
                findings.append((r["id"], fn, gone))
    return findings, {"parameterized": parameterized,
                      "unresolved": unresolved, "measured": measured}


def main():
    findings, counts = scan()
    n = counts["measured"]
    if "--report" in sys.argv:
        by_fn = defaultdict(list)
        for rid, fn, gone in findings:
            by_fn[fn].append((rid, gone))
        for fn in sorted(by_fn):
            for rid, gone in by_fn[fn]:
                print(f"  {rid:26s} {fn:34s} {', '.join(gone)}")
    tail = (f"{n} rule/checker pairs measured, "
            f"{counts['parameterized']} parameterized (out of scope), "
            f"{len(counts['unresolved'])} unresolvable")
    if not findings:
        print(f"ruleset-parity: clean — {tail}.")
        return 0
    print("ruleset-parity: a checker matches on a field its rule text never names.\n")
    for rid, fn, gone in findings:
        print(f"  {rid} — {fn} matches {', '.join(repr(g) for g in gone)}, "
              f"and the rule's prose says nothing about it")
    print(f"\n{tail}.\n"
          "The ruleset is the authority the checker implements. Either the "
          "prose is stale — say what the checker now accepts — or the checker "
          "drifted, in which case fix the code, not the text.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
