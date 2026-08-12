#!/usr/bin/env python3
"""T212 — the last three orphan checkers, which were the SVG ones.

`--verify-registry` listed `svg_no_orphan_defs`, `svg_validates_xml` and
`svg_title_or_legend` as registered-and-called-by-nothing. Two were wired and one
refused, and the split was decided by measurement over all 127 vault SVGs:

  * `svg_no_orphan_defs` -> R-svg-hygiene-02 — 2 findings (`arrowhead`/`arrowthin`
    in an SV streaming diagram, `arr-leaf` in a Viz Bench render).
  * `svg_validates_xml`  -> R-svg-hygiene-03 — 1 finding (`ANC API.svg`, which
    xmllint rejects at line 21).
  * `svg_title_or_legend` — REFUSED. 104 of 127 fail (82%). Its rule is R-c4-02,
    not R-svg-hygiene; the refusal and its measurement live in R-c4.md.

Two things beyond the wiring are pinned here.

**The set had no `where::`, and that is what made wiring unsafe** rather than
anything about the checkers. With no selector a ruleset inherits `always`, so
both rules would have run on every markdown file in the vault and answered
`error` — *the checker malfunctioned* — on each. The set now carries the `.svg`
selector its siblings use.

**`-02` no longer reports `-03`'s finding in the error voice.** An unparseable
file has no `<defs>` to audit; it used to come back `error`, so one broken file
produced two findings, one of them claiming the checker itself had failed. This
is the same fault T212 fixed in `no_track_row_if_ecosystem_traits` the same day,
which is why it is asserted rather than just corrected.

Run: python3 test-t212-svg-orphan-wiring.py
"""
import importlib.machinery
import importlib.util
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


ap = _load("audit_plan_t212_svg", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


def svg(checker, body, name="fig.svg"):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(body, encoding="utf-8")
        return ap.CHECKERS[checker](p, p.parent, [])


HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480">'

USED = HEAD + """
  <defs><marker id="arrow"><path d="M0,0 L6,3 L0,6"/></marker></defs>
  <line x1="0" y1="0" x2="9" y2="9" marker-end="url(#arrow)"/>
</svg>"""

ORPHAN = HEAD + """
  <defs>
    <marker id="arrow"><path d="M0,0 L6,3 L0,6"/></marker>
    <marker id="arrowthin"><path d="M0,0 L4,2 L0,4"/></marker>
  </defs>
  <line x1="0" y1="0" x2="9" y2="9" marker-end="url(#arrow)"/>
</svg>"""

MALFORMED = HEAD + """
  <defs><marker id="arrow"><path d="M0,0"/></marker></defs>
  <line x1="0" y1="0" x2="9" y2="9"
</svg>"""


print("R-svg-hygiene-02 — orphan <defs> entries")

check("a marker referenced by marker-end passes",
      svg("svg_no_orphan_defs", USED)[0], "pass")
check("an unreferenced marker fails",
      svg("svg_no_orphan_defs", ORPHAN)[0], "fail")
check("...and the verdict names the orphan id, so the fix is one edit",
      "arrowthin" in svg("svg_no_orphan_defs", ORPHAN)[1], True)
check("a file with no <defs> at all passes rather than erroring",
      svg("svg_no_orphan_defs", HEAD + "<line x1='0' y1='0' x2='9' y2='9'/></svg>")[0],
      "pass")

# The defect this half exists to freeze: `error` means the checker malfunctioned,
# and an unparseable file is R-svg-hygiene-03's finding, not this rule's.
_v, _m = svg("svg_no_orphan_defs", MALFORMED)
check("an UNPARSEABLE file is not this rule's finding — it passes here",
      _v, "pass")
check("...and says which rule does own it, so the pointer survives the handoff",
      "R-svg-hygiene-03" in _m, True)
check("...and it is emphatically not `error`, which claims the checker broke",
      _v == "error", False)

print("\nR-svg-hygiene-03 — well-formed XML")

check("a well-formed file passes", svg("svg_validates_xml", USED)[0], "pass")
check("a malformed file fails", svg("svg_validates_xml", MALFORMED)[0], "fail")
check("so ONE broken file yields exactly one finding across the two rules",
      [svg(c, MALFORMED)[0] for c in ("svg_no_orphan_defs", "svg_validates_xml")],
      ["pass", "fail"])

print("\nThe selector the set was missing (R-ruleset-10)")

_src = ap.REPO_ROOT / "rulesets" / "R-svg-hygiene.md"
_text = _src.read_text(encoding="utf-8")
_block, _ = ap.extract_ruleset_block(_text, "R-svg-hygiene")
_parsed = ap.parse_ruleset_block(_block, _src)

_where = _parsed.get("where") or ""
check("the set declares a where:: at all — without one it inherits `always` "
      "and both rules answer `error` on every non-SVG file in the vault",
      bool(_where), True)
check("...and that selector is scoped to .svg",
      _where.endswith("*.svg"), True)
check("...in the majority spelling its siblings use "
      "(R-svg-jiggle / R-diagram-geometry / R-c4)",
      _where.strip("`"), "{anchor}/**/*.svg")

# A non-SVG target still answers `error` — that is correct and is precisely why
# the selector is load-bearing. The guard is not redundant with the where::;
# it is what makes a mis-scoped set loud instead of silently green.
check("a non-SVG target is still refused by the checker itself",
      svg("svg_no_orphan_defs", "# not a diagram\n", name="doc.md")[0], "error")

print("\nThe wiring itself")

_rules = {r["id"]: r for r in _parsed["rules"]}
check("R-svg-hygiene-02 carries its check::",
      _rules["R-svg-hygiene-02"].get("check"), "svg_no_orphan_defs")
check("R-svg-hygiene-03 carries its check::",
      _rules["R-svg-hygiene-03"].get("check"), "svg_validates_xml")
check("-01 stays unwired — it is (sampled) and has no implementation",
      _rules["R-svg-hygiene-01"].get("check"), None)

print("\nThe refusal — svg_title_or_legend belongs to R-c4-02 and stays orphan")

_c4 = ap.REPO_ROOT / "rulesets" / "R-c4.md"
_c4_text = _c4.read_text(encoding="utf-8")
_c4_parsed = ap.parse_ruleset_block(ap.extract_ruleset_block(_c4_text, "R-c4")[0], _c4)
_c4_rules = {r["id"]: r for r in _c4_parsed["rules"]}

check("R-c4-02 carries no check:: — the refusal is real, not a stale note",
      _c4_rules["R-c4-02"].get("check"), None)
check("...and no rule anywhere in the corpus wires it, so it is still reported "
      "as an orphan rather than quietly disappearing from the walk",
      "svg_title_or_legend" in ap.CHECKERS, True)
check("...while the refusal itself is written down where the rule is",
      "svg_title_or_legend" in _c4_text and "104" in _c4_text, True)

# The rescued-by-proportional-threshold hypothesis was tested and falsified (2 of
# 104). It is recorded so the next author does not re-run it as a fix.
check("...including the divergence that was tested and did NOT explain it",
      "proportional" in _c4_text, True)

print(f"\n{passed}/{passed + failed} passed")
sys.exit(0 if failed == 0 else 1)
