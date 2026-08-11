#!/usr/bin/env python3
"""test-t207-batch-run-executes.py — `--batch DIR --run` must actually run.

Reported by ATT 2026-08-11. The `if args.batch:` branch built a plan per anchor,
printed the recipe, printed a cache footer, and `return 0`'d — **before** control
reached `if args.run:`. So `--run`, `--judge` and `--report` were accepted by
argparse, silently discarded, and never warned about.

The failure is in the direction that manufactures confidence. A `--batch --run`
emits thousands of plausible rule listings and a tidy footer, so it *reads* like
a corpus sweep that found nothing:

    audit-plan.py --batch "Topic/MED" --run --no-cache | grep -cE "✓|✗"   → 0
    audit-plan.py         "Topic/MED" --run --no-cache | grep -cE "✓|✗"   → 576

Same tree, same flag, and the zero was a property of the harness rather than of
the corpus — [[project_clean_scan_is_a_claim_about_the_scanner]]. It had already
produced one published wrong measurement: [[DAS Stone]] recorded that a batch
sweep "emits 13 `R-rocks` verdicts" and concluded the folder-facet selector
worked. Those 13 were **recipe lines**. The conclusion was right; the evidence
was not, and nothing in the output distinguished them.

`test-t098-batch-harness.py` is the sibling that makes this sting: it exists
because `--batch ~/ob/kmr --run` "had never once completed", fixed the decode
crash that stopped it, and left the early return in place — so the vault-wide
harness T098 was built to enable still executed nothing.

Case 3 is the one to keep: the fixture is built so a rule genuinely FAILS on it.
A batch sweep that reports only passes cannot be told apart from one that reports
nothing, which is the whole bug one level up.

Usage: python3 test-t207-batch-run-executes.py
"""
import importlib.util
import io
import contextlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0

_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def run(*argv):
    """(rc, stdout) for one audit-plan invocation."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = ap.main(list(argv))
    return rc, out.getvalue()


# A two-anchor tree. `GOOD` is well-formed; `BAD` is missing the description its
# anchor page needs, so at least one mechanical rule has something to fail on.
td = Path(tempfile.mkdtemp())
for slug, desc in (("GOOD", "description: a well-formed anchor\n"), ("BAD", "")):
    d = td / slug
    d.mkdir(parents=True)
    (d / ".anchor").write_text(f"slug: {slug}\n{desc}", encoding="utf-8")
    (d / f"{slug}.md").write_text(
        ("---\ndescription: a well-formed anchor\n---\n\n" if desc else "")
        + f"# {slug}\nAn anchor.\n", encoding="utf-8")

rc, text = run("--batch", str(td), "--run", "--no-cache")
verdicts = sum(text.count(c) for c in "✓✗")

# 1 — the flag is honoured at all. This is the whole bug.
check(verdicts > 0, "`--batch --run` emits mechanical verdicts")
check("batch total:" in text, "...and a corpus TOTAL, which is the point of a sweep")

# 2 — the recipe path is untouched when no execution flag is given.
rc_recipe, recipe = run("--batch", str(td), "--no-cache")
check(sum(recipe.count(c) for c in "✓✗") == 0,
      "a bare `--batch` still prints the recipe and runs nothing")
check(rc_recipe == 0, "...and exits 0")

# 3 — the sweep can FAIL. A harness that only ever reports passes is
#     indistinguishable from one that reports nothing.
rc_json, js = run("--batch", str(td), "--run", "--json", "--no-cache")
data = json.loads(js)
tot = data["totals"]
check(tot["fail"] > 0, "the sweep reports real FAILURES, not only passes")
check(rc_json != 0, "...and a sweep with failures exits non-zero, so a caller can gate on it")

# 4 — the total is the sum of the parts, not a separately-computed number that
#     could drift away from the per-anchor blocks a reader is checking it against.
summed = sum(a["mechanical"]["counts"]["fail"] for a in data["anchors"])
check(summed == tot["fail"], "the corpus total equals the sum of the per-anchor counts")
check(len(data["anchors"]) == 2, "...over every anchor found under the root")

# 5 — `--judge` and `--report` were dropped by the same early return and must
#     not be left behind now that `--run` works.
_, judged = run("--batch", str(td), "--judge", "--no-cache")
check(sum(judged.count(c) for c in "✓✗") == 0 and judged.strip(),
      "`--batch --judge` emits a manifest rather than nothing")
_, reported = run("--batch", str(td), "--report", "--no-cache")
check(reported.strip() and "batch total:" in reported,
      "`--batch --report` emits the unified view and the total")

print(f"\nT207 batch --run executes: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
