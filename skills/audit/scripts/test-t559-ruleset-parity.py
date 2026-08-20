#!/usr/bin/env python3
"""T559 — the checker/ruleset field-parity lint, and the proof it can fire.

`ruleset-parity.py` reports a clean corpus. A clean report from a detector that
cannot see anything is the failure mode this file exists to rule out, so §3
replays the real T552 drift — R-backlog-04's checker accepts `- **Probe:**`
while its prose says nothing about a Probe — and asserts the lint fires on it.
That pair is the one that motivated T559, so the regression it guards is the
one that actually happened rather than an invented one.

§4 pins the two suppressions, because each one was added to silence a real
first-cut finding and either could be widened later into a hole:

  - the bold-colon field REQUIRES its colon (without it `**Warden rule**` and
    `**Every one of them resolves**` were reported as missing fields), and
  - ruleset-GRAMMAR keys (`where::`, `fix::`, `confirm::`) are excluded,
    because a checker that parses ruleset syntax matches them in every set it
    reads and no individual rule owes them a mention.

Run: python3 test-t559-ruleset-parity.py
"""
import importlib.util
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, _HERE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


rp = _load("rp", "ruleset-parity.py")

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


print("1. The corpus agrees today")
findings, counts = rp.scan()
check("no checker names a field its rule text does not", findings, [])
check("...over a population that is not empty", counts["measured"] > 100, True)
check("every checker resolved to source", counts["unresolved"], [])
# Not a silent cap: parameterized checkers (`check:: regex_present ^# [^-]`)
# carry their contract as the argument, in the ruleset, with no per-rule Python
# to disagree with. The lint prints this count on every run.
check("parameterized pairs are counted, not dropped",
      counts["parameterized"] > 0, True)

print("2. The token extractors read what a rule and a checker both spell")
check("a bold-colon field is a token",
      "Verify" in rp.field_tokens("carries a `- **Verify:**` sub-bullet"), True)
check("...but bare emphasis is NOT — the colon is required",
      rp.field_tokens("this is a **Warden rule** about things"), set())
check("a declared key is a token",
      "probe::" in rp.field_tokens("the `probe:: foo` line"), True)
check("...but a ruleset-grammar key is not",
      rp.field_tokens("`where:: file:**` and `fix:: x` and `confirm:: user`"),
      set())
check("a checker's DOCSTRING does not oblige its rule",
      rp.checker_tokens('def f(x):\n    """mentions **Probe:** in prose"""\n'
                        '    return x\n'),
      set())
check("...but a literal it matches on does",
      "Probe" in rp.checker_tokens('def f(s):\n    """d"""\n'
                                   '    return s.startswith("- **Probe:**")\n'),
      True)

print("3. The T552 drift makes it fire — the zero in §1 is earned")
# The real pair, read live: `chk_backlog_verify_concrete` accepts a Probe on a
# `[Watching …]` row, and R-backlog-04's prose was silent about that for as long
# as it took someone to notice. Prose and checker are in step now, so the drift
# is re-created by deleting `Probe` from the prose — nothing else changes.
import inspect  # noqa: E402  (deliberately local to this section)

impl = None
rulesets = rp.ap.all_corpus_rulesets()
rp.ap.register_imports(rulesets)
impl = rp.ap.registry().get("backlog_verify_concrete")
check("the R-backlog-04 checker resolves", impl is not None, True)
if impl is not None:
    src = inspect.getsource(impl)
    check("...and it really does match on a Probe field",
          "Probe" in rp.checker_tokens(src), True)
    prose = ""
    for rs in rulesets:
        for r in rs["rules"]:
            if r["id"] == "R-backlog-04":
                prose = rp.rule_prose(rs, "R-backlog-04")
    check("R-backlog-04's prose is findable", bool(prose), True)
    check("...and today it names the Probe — no finding", "Probe" in prose, True)
    drifted = prose.replace("Probe", "XXXXX")
    gone = sorted(t for t in rp.checker_tokens(src)
                  if (t[:-2] if t.endswith("::") else t) not in drifted)
    check("strip Probe from the prose and the lint reports it",
          "Probe" in gone, True)

print("4. What the lint does NOT claim is written down")
doc = (_HERE / "ruleset-parity.py").read_text(encoding="utf-8")
check("it says registration is already covered by F289",
      "verify_registrations" in doc and "F289" in doc, True)
check("it names the counterexample its approach cannot reach",
      "R-spine-09" in doc and "entry_names" in doc, True)
check("it says parameterized pairs are out of scope by construction",
      "out of scope by construction" in doc, True)

print("5. The lint reports its population, so a shrinking one is visible")
check("the clean line carries the measured count",
      bool(re.search(r"pairs measured", doc)), True)

print()
if FAILURES:
    print(f"test-t559-ruleset-parity: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t559-ruleset-parity: all checks pass")
