#!/usr/bin/env python3
"""T217 — a selector hidden in YAML frontmatter, and the guard that exempted it.

`rulesets/R-dispatch-table.md` opened with a YAML block carrying
`where: "file: {anchor}/**/*.md"`. `parse_ruleset_block` reads only body
`field::` lines, so both engines — `audit-plan` and `warden compile` — carried
all 15 of its rules as `where=None`, which falls through to the `always` default.

Two independent defects met in that one file, and both are pinned here.

**The selector.** Moving it into the body is a rescope, so the delta was measured
first rather than assumed. For markdown it is zero, and the reason is structural:
`enumerate_scope` in anchor mode enumerates `*.md` only, so `always` and
`{anchor}/**/*.md` select the identical 905 files in this repo; and on the write
path F297's `rows_for` sends every non-markdown kind to its anchor's declared
trait rules, never to the `R-doc` umbrella these live under. The one path where
it bit is `/audit doc` named at a non-markdown file — there all 15 masthead rules
were in play, 15 of the 31 rule-target pairs, and the three carrying a `check::`
each answered a green verdict about a Python file's masthead.

**The guard.** `R-ruleset-11` forbids exactly this shape, and its Check pattern
was unsatisfiable as written: *"if the file's first non-blank line is `# RULESET`,
assert no `---` frontmatter precedes it"* — nothing can precede a first non-blank
line, so the entry condition excluded every violation. `chk_ruleset_no_frontmatter`
implemented it literally and answered `('pass', 'not a standalone ruleset file')`
about files named `R-*.md` living in `rulesets/`. The violation was its own
exemption. It now decides kind on the body, below any frontmatter.

The corrected guard was measured before landing: across all 122 vault files
carrying a `# RULESET R-` block, exactly one verdict changed —
`examples/FEX Repo/R-fex-manifest.md`, the worked example of the ruleset format,
carrying frontmatter that duplicated its own `description::`. That file is fixed,
so this test asserts the rule is at zero findings *honestly* — the two halves
are separable, and asserting only "no findings" would pass on the broken guard.

Run: python3 test-t217-dispatch-table-selector.py
"""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_t217", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


def guard(body, name="R-fixture.md"):
    """Run chk_ruleset_no_frontmatter over a temp file."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(body, encoding="utf-8")
        return ap.CHECKERS["ruleset_no_frontmatter"](p, p.parent, [])


BODY_ONLY = """# RULESET R-fixture
include::
where:: `file:{anchor}/**/*.md`
description:: a fixture

### RULE R-fixture-01 — something (stated)
**Why:** because.
"""

WITH_FRONTMATTER = """---
description: a fixture
where: "file: {anchor}/**/*.md"
---

""" + BODY_ONLY

# The false-positive class the old whole-file `---` scan produced. Frontmatter is
# leading by definition, so a thematic break in the body is not frontmatter.
THEMATIC_BREAK = BODY_ONLY + """
Some prose.

---

More prose after a horizontal rule.
"""

# An embedded ruleset — a facet page that may legitimately carry frontmatter and
# happens to hold a `# RULESET` block further down. This is the case the rule's
# parenthetical explicitly exempts, and it must stay exempt.
EMBEDDED = """---
description: a facet spec
---

# DAS Fixture

Prose about the facet.

# RULESET R-fixture
include::

### RULE R-fixture-01 — something (stated)
"""


print("The guard — kind is decided on the body, not on line 1")

check("a body-only standalone ruleset passes",
      guard(BODY_ONLY), ("pass", ""))
check("the SAME file with frontmatter above it now FAILS — the case the rule "
      "exists for, and the one the old first-non-blank-line test exempted",
      guard(WITH_FRONTMATTER),
      ("fail", "standalone ruleset file has YAML frontmatter"))
check("...and it fails for the frontmatter, not for any later `---`: a thematic "
      "break in the body of a frontmatter-free file still passes",
      guard(THEMATIC_BREAK), ("pass", ""))
check("an EMBEDDED ruleset inside a frontmatter-bearing host page stays exempt "
      "— the rule's own parenthetical",
      guard(EMBEDDED), ("pass", "not a standalone ruleset file"))
check("an empty file is not a ruleset",
      guard("\n\n"), ("pass", "empty file"))

print("\nThe corpus — the rule is at zero findings honestly, not vacuously")

_repo_rulesets = sorted((ap.REPO_ROOT / "rulesets").glob("*.md"))
check("every file in rulesets/ passes the guard",
      [str(p.relative_to(ap.REPO_ROOT))
       for p in _repo_rulesets
       if ap.CHECKERS["ruleset_no_frontmatter"](p, ap.REPO_ROOT, [])[0] != "pass"],
      [])

# The one file the corrected predicate newly caught. Asserting it is CLEAN would
# also pass if someone reverted the guard, so assert the property that separates
# the two: the file is judged a standalone ruleset at all.
_fex = ap.REPO_ROOT / "examples" / "FEX Repo" / "R-fex-manifest.md"
check("the FEX worked example is judged a standalone ruleset — not skipped, "
      "which is what the old guard did to it",
      ap.CHECKERS["ruleset_no_frontmatter"](_fex, ap.REPO_ROOT, []), ("pass", ""))
check("...and it no longer opens with a `---` block",
      _fex.read_text(encoding="utf-8").splitlines()[0], "# RULESET R-fex-manifest")

print("\nThe selector — R-dispatch-table declares it where the parser reads")

_dt = ap.REPO_ROOT / "rulesets" / "R-dispatch-table.md"
_dt_text = _dt.read_text(encoding="utf-8")
_dt_parsed = ap.parse_ruleset_block(
    ap.extract_ruleset_block(_dt_text, "R-dispatch-table")[0], _dt)

check("the set parses a real selector — `where=None` was the whole defect",
      _dt_parsed.get("where"), "file:{anchor}/**/*.md")

# Read it back the way the ENGINE does, `or "always"` and all (plan_one,
# warden_docfire.fire_audit). Two reasons: a re-hidden selector then produces a
# failing assertion here instead of an AttributeError three lines down, and the
# measurement block below measures what would actually run rather than what the
# file happens to say.
_where = _dt_parsed.get("where") or "always"

# Not a restatement of the line above: this reads the spelling off two OTHER
# sets, so a corpus-wide convention change is caught here rather than silently
# leaving this one set behind in an abandoned form.
_sibling_prefixes = set()
for _name in ("R-backlog", "R-query"):
    _p = ap.REPO_ROOT / "rulesets" / f"{_name}.md"
    _w = ap.parse_ruleset_block(
        ap.extract_ruleset_block(_p.read_text(encoding="utf-8"), _name)[0], _p)["where"]
    _sibling_prefixes.add(_w.split("{anchor}")[0])
check("...spelled the way its `{anchor}`-rooted siblings spell it (R-backlog / "
      "R-query), read off those files rather than restated here",
      {_where.split("{anchor}")[0]}, _sibling_prefixes)
check("...and all 15 rules are still there, so the move rescoped nothing away",
      len(_dt_parsed["rules"]), 15)
check("no rule overrides it with a narrower own `where::`",
      [r["id"] for r in _dt_parsed["rules"] if r.get("where")], [])
check("the file no longer opens with frontmatter",
      _dt_text.splitlines()[0], "# RULESET R-dispatch-table")

print("\nThe measurement — markdown is untouched, non-markdown is dropped")

_, _scope = ap.enumerate_scope(ap.REPO_ROOT, "anchor")
_kind, _arg = ap.parse_selector(_where)
_glob_targets = ap.match_targets(_kind, _arg, _scope, ap.REPO_ROOT)
_always_targets = ap.match_targets(*ap.parse_selector("always"), _scope, ap.REPO_ROOT)

check("anchor-mode scope is markdown-only, so the declared glob and the `always` "
      "default select the identical set — this is why the move cost nothing",
      len(_glob_targets), len(_always_targets))
check("...and that set is every markdown file in the scope, none excluded",
      len(_glob_targets), len(_scope))

# Doc mode is the path where the two differ: `enumerate_scope` returns whatever
# single file was named, whatever its suffix.
_py = ap.REPO_ROOT / "skills" / "audit" / "scripts" / "queries-render.py"
_root, _one = ap.enumerate_scope(_py, "doc")
check("named at a Python file, the declared glob selects nothing",
      ap.match_targets(_kind, _arg, _one, _root), [])
check("...where `always` would have selected it — the 15 masthead rules that "
      "used to run there, three of them returning a green check:: verdict",
      len(ap.match_targets(*ap.parse_selector("always"), _one, _root)), 1)

_md = ap.REPO_ROOT / "DAS.md"
_mroot, _mone = ap.enumerate_scope(_md, "doc")
check("while a markdown doc-fire still selects the file, unchanged",
      len(ap.match_targets(_kind, _arg, _mone, _mroot)), 1)

print("\nThe rule text — the unsatisfiable Check pattern is replaced")

_rs = ap.REPO_ROOT / "rulesets" / "R-ruleset.md"
_rs_text = _rs.read_text(encoding="utf-8")
_rs_parsed = ap.parse_ruleset_block(
    ap.extract_ruleset_block(_rs_text, "R-ruleset")[0], _rs)
_rs_rules = {r["id"]: r for r in _rs_parsed["rules"]}
_r11 = _rs_rules["R-ruleset-11"]

check("R-ruleset-11 still wires the guard",
      _r11.get("check"), "ruleset_no_frontmatter")
check("...and no longer asks for something that precedes a first non-blank line",
      bool(re.search(r"precedes it", _r11.get("check_pattern") or "")), False)
check("...but describes the strip-then-decide order the checker implements",
      bool(re.search(r"strip.*frontmatter", _r11.get("check_pattern") or "",
                     re.I)), True)

print(f"\n{passed}/{passed + failed} passed")
sys.exit(0 if failed == 0 else 1)
