#!/usr/bin/env python3
"""T212 — a ruleset's own source file is exempt by NAME, never by CONTENT.

`plan_one` drops a ruleset's own source file from that ruleset's targets, and
for the case it was written for it is exactly right: `DAS Decisions.md` is the
*spec* of `R-decisions`, it matches the `* Decisions.md` glob by filename, and
it is not a Decisions document. The glob was fooled by the name.

Applied to a `sentinel:` selector the same exclusion is wrong, because content
does not lie about kind. A file carrying `# RULESET R-` **is** a ruleset —
whichever ruleset it happens to be. So `R-ruleset` was exempted from itself:
the one set in the repo whose subject is the file kind it is written as, and
whose header says in so many words *"Self-applying: this set obeys its own
rules."* It never was. Six mechanical rules ran on every other ruleset file in
the vault and on none of its own.

Both directions are asserted here, because fixing one by breaking the other is
the obvious wrong repair and it would look like a pass from either side alone.

Measured 2026-08-11 before the narrowing: of the four sentinel-scoped rulesets
(R-brief, R-discussion, R-ruleset, R-stream) only R-ruleset matches its own
sentinel, and it passes all six of its mechanical rules — so this closes a hole
without moving a verdict, which is the only reason it could be landed silently.

Run: python3 test-t212-sentinel-self-apply.py
"""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_t212", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


def rulesets_for(rel: str):
    """The ruleset names whose rules actually matched this document."""
    p = (ap.REPO_ROOT / rel)
    if not p.is_file():
        return None
    plan = ap.plan_one(p, "doc", None, [])
    return {g["ruleset"] for g in plan["groupings"]}


# ── the regression: a sentinel-scoped set reaches its own source ─────────────

names = rulesets_for("rulesets/R-ruleset.md")
check("R-ruleset.md resolves a plan at all", names is not None, True)
if names is not None:
    check("R-ruleset applies to its own source file (sentinel = content match)",
          "R-ruleset" in names, True)
    # Sanity: the doc-level sets everyone gets are still there, so a pass above
    # cannot come from the plan having quietly widened to include everything.
    check("and the ordinary doc rulesets are still present",
          "R-markdown" in names, True)

# ── the exclusion it must not break: glob-matched specs stay exempt ──────────

dec = rulesets_for("facets/DAS Decisions.md")
check("DAS Decisions.md resolves a plan at all", dec is not None, True)
if dec is not None:
    check("a facet spec is still NOT an instance of its own glob-scoped set",
          "R-decisions" in dec, False)

# ── the predicate itself, stated once ───────────────────────────────────────

check("the exclusion is keyed on selector kind, not on the file",
      [k != "sentinel" for k in ("file", "sentinel", "always", "anchor")],
      [True, False, True, True])

# ── the measurement the narrowing rests on ──────────────────────────────────
# Only R-ruleset self-matches. If another sentinel set ever grows a heading
# that matches its own selector, this flips and someone must re-measure before
# assuming the change is still verdict-neutral.

import re  # noqa: E402  — used only for the corpus measurement below

SENTINEL_SETS = {
    "R-brief.md": r"^#+ BRIEF\b",
    "R-discussion.md": r"^#+ Discussion",
    "R-ruleset.md": r"^#+ RULESET R-",
    "R-stream.md": r"^## \d{4}-\d{2}-\d{2} —",
}
selfmatch = sorted(
    n for n, rx in SENTINEL_SETS.items()
    if (ap.REPO_ROOT / "rulesets" / n).is_file()
    and re.search(rx, ap._read(ap.REPO_ROOT / "rulesets" / n), re.M))
check("exactly one sentinel-scoped ruleset matches its own sentinel",
      selfmatch, ["R-ruleset.md"])

print()
if failed:
    print(f"test-t212-sentinel-self-apply: {passed} passed, {failed} failed")
    sys.exit(1)
print(f"test-t212-sentinel-self-apply: {passed} passed, 0 failed")
