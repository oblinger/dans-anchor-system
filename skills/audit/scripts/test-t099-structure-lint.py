#!/usr/bin/env python3
"""T099 — the ratchet that makes a 130th private structure spelling loud.

`audit-plan.py` is ~5,000 lines in which checkers kept re-deciding what a heading
is, what a fence is, what a table row is; an AST census found 129 such spellings
across 67 defs, and nearly every F296/T102/T103 finding turned out to be a checker
that did not call the shared helper. Three classes have since had their DEFECT
converted — fence, heading, table — but 67 defs is too diffuse to consolidate in
one refactor, so the durable close is a guard, not a finish.

**The assertion that matters is the falsification.** A lint that never fires is
indistinguishable from no lint, and this one is a ratchet over a baseline file, so
it can fail silently in the worst way: by having a baseline so loose that nothing
trips it. `test_lint_fires_on_a_new_spelling` therefore injects each of the four
classes into a copy of the real module and asserts the lint FAILS on every one.

`structure-lint.py` reads the AST rather than grepping, for the reason the fence
assertion in `test-t099-fenced-mask.py` gives: review is what missed the second and
third copies of the fence toggle. Two whole categories are excluded by that
choice, and both are asserted below — an f-string EMITTER (`f"# {name}"` writes a
heading, it does not recognise one; counting these is what made the census's first
cut report heading at 55) and a cell SPLIT (`line.split("|")` divides a row already
known to be one).

    python3 test-t099-structure-lint.py
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
LINT = HERE / "structure-lint.py"
TARGET = HERE / "audit-plan.py"

_spec = importlib.util.spec_from_file_location("slint", LINT)
sl = importlib.util.module_from_spec(_spec)
sys.modules["slint"] = sl
_spec.loader.exec_module(sl)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def classes_of(src: str):
    """The lint's verdict on a synthetic module: {class: n} outside the primitives."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(src)
        p = Path(fh.name)
    try:
        out = {}
        for d, cls, _, _ in sl.sites(p):
            if d in sl.PRIMITIVES:
                continue
            out[cls] = out.get(cls, 0) + 1
        return out
    finally:
        p.unlink()


print("The classifier counts recognisers, not emitters or parsers")

check("an anchored heading regex is a heading recogniser",
      classes_of('import re\ndef chk_x(t):\n    return re.match(r"^ {0,3}## Foo", t)\n'),
      {"heading": 1})
check("an f-string EMITTER is not — `f\"# {name}\"` writes a heading",
      classes_of('def chk_x(n):\n    return f"# {n}\\n## {n}"\n'), {})
check("a cell SPLIT is not — it divides a row already known to be one",
      classes_of('def chk_x(ln):\n    return [c.strip() for c in ln.split("|")]\n'), {})
check("a `#` that does not anchor is not a heading — the SVG `url(#id)` case "
      "that was the census's one false positive",
      classes_of('import re\ndef chk_x(t):\n    return re.findall(r"url\\(#([\\w-]+)\\)", t)\n'), {})
check("`startswith(\"|\")` IS a table-row recogniser",
      classes_of('def chk_x(ln):\n    return ln.lstrip().startswith("|")\n'), {"table": 1})
check("a multi-class `startswith` tuple counts once per class — the `_prose` shape",
      classes_of('def chk_x(s):\n    return s.startswith(("|", "# ", "```"))\n'),
      {"table": 1, "heading": 1, "fence": 1})

print("\nPrimitives are exempt — they ARE the definition")

prim = 'import re\n_TABLE_ROW_RE = re.compile(r"^ {0,3}\\|")\ndef _is_table_row(l):\n    return re.match(r"^ {0,3}\\|", l)\n'
check("the module-level constant and the primitive def are both exempt",
      classes_of(prim), {})
check("...but the same spelling in an ordinary checker is not",
      classes_of(prim + 'def chk_y(l):\n    return re.match(r"^ {0,3}\\|", l)\n'), {"table": 1})


def test_lint_fires_on_a_new_spelling():
    """A ratchet that never fires is indistinguishable from no ratchet.

    Injected into a COPY of the real module — not a toy — so the baseline under
    test is the committed one, at its real size. Each class is asserted
    separately: a guard that catches three of four classes would otherwise pass
    while leaving the fourth open, which is exactly the shape of the gap this
    whole line of work keeps finding.
    """
    src = TARGET.read_text(encoding="utf-8")
    base = sl.tally(sl.sites(TARGET))
    for cls, line in (
        ("heading",   'return re.match(r"^ {0,3}### Widgets\\b", ln)'),
        ("fence",     'return ln.strip().startswith("```")'),
        ("table",     'return re.match(r"^\\|\\s*Widget\\s*\\|", ln)'),
        ("wiki-link", 'return re.findall(r"\\[\\[([^\\]|]+)", ln)'),
    ):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "audit-plan.py").write_text(
                src + f"\n\ndef chk_brand_new_widget_rule(ln):\n    {line}\n", encoding="utf-8")
            (d / "structure-lint-baseline.json").write_text(
                sl.BASELINE.read_text(encoding="utf-8"), encoding="utf-8")
            (d / "structure-lint.py").write_text(
                LINT.read_text(encoding="utf-8"), encoding="utf-8")
            r = subprocess.run([sys.executable, str(d / "structure-lint.py")],
                               capture_output=True, text=True)
            check(f"a new {cls} spelling in a new def FAILS the lint", r.returncode, 1)
            check(f"...and the {cls} failure names the def and the class",
                  ("chk_brand_new_widget_rule" in r.stdout and cls in r.stdout), True)
            # The new def must be the ONLY thing that moved — if injecting one
            # spelling perturbs the tally elsewhere, the ratchet is not stable and
            # its clean runs mean nothing.
            now = sl.tally(sl.sites(d / "audit-plan.py"))
            check(f"...and nothing else in the module moved ({cls})",
                  {k: v for k, v in now.items() if k != "chk_brand_new_widget_rule"}, base)


test_lint_fires_on_a_new_spelling()

print("\nThe committed baseline is honest")

r = subprocess.run([sys.executable, str(LINT)], capture_output=True, text=True)
check("the module as committed is clean against its baseline", r.returncode, 0)
check("the baseline is not vacuous — it freezes a real population",
      sum(sum(c.values()) for c in sl.tally(sl.sites(TARGET)).values()) > 50, True)

# A ratchet only tightens. If a class is converted and the baseline is not
# reshrunk, the lint must SAY so rather than silently bank the slack — otherwise
# the baseline drifts permanently looser than the module and every later clean run
# is worth less than it looks.
import json  # noqa: E402 — local to this assertion

with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    (d / "audit-plan.py").write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")
    (d / "structure-lint.py").write_text(LINT.read_text(encoding="utf-8"), encoding="utf-8")
    loose = json.loads(sl.BASELINE.read_text(encoding="utf-8"))
    loose["chk_retired_checker_that_no_longer_exists"] = {"heading": 3}
    (d / "structure-lint-baseline.json").write_text(json.dumps(loose), encoding="utf-8")
    r = subprocess.run([sys.executable, str(d / "structure-lint.py")],
                       capture_output=True, text=True)
    check("a baseline LOOSER than the module fails rather than banking the slack",
          r.returncode, 1)
    check("...and it says the ratchet can tighten, naming the converted site",
          ("can tighten" in r.stdout
           and "chk_retired_checker_that_no_longer_exists" in r.stdout), True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
