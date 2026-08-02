#!/usr/bin/env python3
"""T074 — the four `svg_*` geometry rules actually run.

`R-svg-jiggle-02..05` declared `check:: svg_label_over_box` and friends, and
nothing registered those names. That failed **silently**, which is why it was a
tracked task and not a chore: the engine decides mechanical-vs-agent by a
registry membership test, so an unregistered name simply misses, the rule is
promoted to a billed agent-judgment task, and `run_checker`'s `unknown checker`
error never runs because the rule never reaches it. Four rules looked enforced
and reported nothing, in either direction, ever.

**The assertion that matters is `test_the_ruleset_reaches_its_own_checkers`.**
Every other check here would pass just as well with the four functions dumped
into `audit-plan.py`. That one asserts they resolve through the ruleset's own
`import:: skills/viz/svg-jiggle.py` (F289) — checkers living beside the geometry
they check, rather than a second copy of `text_bbox` / `rect_overlap` / edge
association in the audit engine.

The `good` fixture is load-bearing in the other direction: a detector that fires
on everything is as useless as one that never fires, and each bad fixture below
is the good one with ONE thing changed, so a fired verdict is attributable.

    python3 test-t074-svg-geometry-checkers.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


# Registration goes through the real corpus, so these tests exercise the same
# path a live audit does — including R-svg-jiggle's import:: line.
_rulesets, _seen = [], set()
for _rs in ap.all_corpus_rulesets():
    if _rs["name"] not in _seen:
        _seen.add(_rs["name"])
        _rulesets.append(_rs)
ap.register_imports(_rulesets)

SVG_RULESET = next(r for r in _rulesets if r["name"] == "R-svg-jiggle")

# Two boxes, one long arrow between them, one edge label sitting clear above it.
# Node labels ('alpha', 'beta') are ≥70% inside their boxes, so R-svg-jiggle-01
# exempts them — without that exemption every diagram would report every node.
GOOD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400">
<defs><marker id="a" markerWidth="8" markerHeight="8"><path d="M0,0 L8,4 L0,8 z"/></marker></defs>
<rect x="20" y="40" width="120" height="60" fill="none" stroke="#333"/>
<rect x="400" y="40" width="120" height="60" fill="none" stroke="#333"/>
<text x="80" y="75" text-anchor="middle" font-size="12">alpha</text>
<text x="460" y="75" text-anchor="middle" font-size="12">beta</text>
<line x1="140" y1="70" x2="400" y2="70" stroke="#333" marker-end="url(#a)"/>
<text x="270" y="55" text-anchor="middle" font-size="11">sends</text>
</svg>"""

# The edge label moved onto the right-hand box's LEFT EDGE, so it straddles:
# ~50% coverage (R-svg-jiggle-02, hard). Centring it on the box instead would
# put it ≥70% inside, and R-svg-jiggle-01 would correctly read it as that box's
# node label and exempt it — the first draft of this fixture made exactly that
# mistake and reported `pass`, which is the exemption working, not a miss.
LABEL_ON_BOX = GOOD.replace('<text x="270" y="55"', '<text x="400" y="55"')

# A second (red) arrow crossing the label's bbox. The label stays nearer its own
# horizontal edge, so association is unchanged and the foreign line is genuinely
# foreign — the label must be over a line it does NOT annotate, which means the
# fixture has to control association, not merely add a line under the text.
LABEL_ON_WRONG_LINE = GOOD.replace(
    '<text x="270" y="55" text-anchor="middle" font-size="11">sends</text>',
    '<line x1="285" y1="150" x2="285" y2="20" stroke="#a00" marker-end="url(#a)"/>\n'
    '<text x="270" y="62" text-anchor="middle" font-size="11">sends</text>')

# Boxes pulled together so the arrow between them is 14px and the head is 8
# (R-svg-jiggle-04, soft) — and, being under the 24px visibility floor, the
# band is crowded too (R-svg-jiggle-05).
SHORT_ARROW = GOOD.replace('<rect x="400"', '<rect x="154"').replace(
    '<text x="460"', '<text x="214"').replace(
    '<line x1="140" y1="70" x2="400" y2="70"', '<line x1="140" y1="70" x2="154" y2="70"').replace(
    '<text x="270" y="55"', '<text x="300" y="300"')

CASES = {"good": GOOD, "label_on_box": LABEL_ON_BOX,
         "label_on_wrong_line": LABEL_ON_WRONG_LINE, "short_arrow": SHORT_ARROW}
FILES = {}
_tmp = tempfile.TemporaryDirectory()
_root = Path(_tmp.name)
for _k, _v in CASES.items():
    _p = _root / f"{_k}.svg"
    _p.write_text(_v, encoding="utf-8")
    FILES[_k] = _p


def verdict(checker, case):
    return ap.run_checker(checker, FILES[case], _root)


print("A clean diagram reports nothing — the detectors are not trigger-happy")

for _c in ("svg_label_over_box", "svg_label_over_wrong_line",
           "svg_overweighted_head", "svg_crowded_band"):
    check(f"{_c} passes the clean fixture", verdict(_c, "good")[0], "pass")


print("\nEach rule fires on the one thing its fixture changed")

check("R-svg-jiggle-02 — a label printed across a box",
      verdict("svg_label_over_box", "label_on_box")[0], "fail")
check("...and names the label, so the finding is actionable",
      "'sends'" in verdict("svg_label_over_box", "label_on_box")[1], True)
check("...while the OTHER three stay silent on that same file — a hard issue "
      "must not be reported four times over",
      [verdict(c, "label_on_box")[0] for c in
       ("svg_label_over_wrong_line", "svg_overweighted_head", "svg_crowded_band")],
      ["pass", "pass", "pass"])

check("R-svg-jiggle-03 — a label sitting on an edge it does not annotate",
      verdict("svg_label_over_wrong_line", "label_on_wrong_line")[0], "fail")
check("...and it is not also a label-over-box (the label is over no box)",
      verdict("svg_label_over_box", "label_on_wrong_line")[0], "pass")

check("R-svg-jiggle-04 — an arrowhead longer than 20% of its segment",
      verdict("svg_overweighted_head", "short_arrow")[0], "fail")
check("R-svg-jiggle-05 — a band of sub-visibility arrows",
      verdict("svg_crowded_band", "short_arrow")[0], "fail")


def test_node_labels_are_exempt():
    """R-svg-jiggle-01: a `<text>` ≥70% inside a box is that box's node label
    and is never a finding. Without the exemption the hard rule would fire on
    every labelled node in every diagram — the checker would be pure noise and
    would read as catastrophic on a perfectly good file."""
    sj_path = ap.REPO_ROOT / "skills" / "viz" / "svg-jiggle.py"
    spec = importlib.util.spec_from_file_location("sj_probe", sj_path)
    sj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sj)
    model = sj.parse_svg(GOOD)
    check("the two texts inside boxes are classified as node labels",
          sorted(l.content for l in model.labels if l.is_node), ["alpha", "beta"])
    check("...and the edge label is not",
          [l.content for l in model.labels if not l.is_node], ["sends"])


def test_the_ruleset_reaches_its_own_checkers():
    """The registration assertion — everything else here would pass with the
    four functions dumped into audit-plan.py instead.

    R-svg-jiggle names the geometry module, not the audit engine, so the
    checkers sit beside the `text_bbox` / `rect_overlap` / edge-association code
    they depend on. Wiring them into audit-plan would have meant a second
    implementation of all of it."""
    check("R-svg-jiggle declares the geometry module",
          SVG_RULESET["imports"], ["skills/viz/svg-jiggle.py"])
    owner = {n: ap._REGISTRY_OWNER.get(n) for n in
             ("svg_label_over_box", "svg_label_over_wrong_line",
              "svg_overweighted_head", "svg_crowded_band")}
    check("...and all four checkers are registered BY that module, not the engine",
          set(owner.values()), {"skills/viz/svg-jiggle.py"})
    check("...so none of them is a ghost any more",
          [g for g in ap.verify_registrations(_rulesets)["ghosts"] if "svg_" in g], [])
    check("...and the rules are mechanical rather than agent-judgment",
          [ap._needs_judgment({"tier": "checked", "check": c}) for c in owner],
          [False] * 4)


def test_a_head_at_exactly_the_threshold_is_not_a_finding():
    """Found by wiring the checker and running it over the vault (2026-08-02).

    `shrink_arrowhead` drives the head to EXACTLY 20% of the segment, and the
    marker size is re-read from the rewritten file, so it comes back a whisker
    high — 6.80001 against a 6.8 target. Under a strict `>` the detector
    re-flagged the very edge its own repair had just fixed: the repair loop
    could never retire the issue, and a fully-jiggled diagram still reported it.
    A `.jiggled.svg` failing `svg_overweighted_head` is the one thing a jiggled
    file must not do."""
    sj_path = ap.REPO_ROOT / "skills" / "viz" / "svg-jiggle.py"
    spec = importlib.util.spec_from_file_location("sj_eps", sj_path)
    sj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sj)

    def head_case(seg_len, head):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400">'
                f'<defs><marker id="a" markerWidth="{head}" markerHeight="{head}">'
                f'<path d="M0,0 L{head},4 L0,8 z"/></marker></defs>'
                f'<line x1="100" y1="70" x2="{100 + seg_len}" y2="70" stroke="#333" '
                f'marker-end="url(#a)"/></svg>')

    at = sj.parse_svg(head_case(34, 6.8))
    over = sj.parse_svg(head_case(34, 9.0))
    check("a head at exactly the 20% target is clean",
          sj.detect_overweighted_head(at), [])
    check("...and one genuinely over it still fires",
          len(sj.detect_overweighted_head(over)), 1)
    check("...with the tolerance small enough to stay a rounding allowance",
          sj.HEAD_EPS < 0.01, True)


def test_a_malformed_svg_errors_rather_than_fails():
    """Reporting `fail` here would say the geometry is bad when the file never
    parsed — and it would restate the same parse failure once per geometry rule.
    `svg_validates_xml` is the rule that owns malformed XML."""
    bad = _root / "broken.svg"
    bad.write_text("<svg><rect x='1'</svg>", encoding="utf-8")
    for c in ("svg_label_over_box", "svg_crowded_band"):
        st, det = ap.run_checker(c, bad, _root)
        check(f"{c} reports error, not fail, on unparseable XML", st, "error")
        check(f"...and {c} says why", "unparseable SVG" in det, True)


test_node_labels_are_exempt()
test_the_ruleset_reaches_its_own_checkers()
test_a_head_at_exactly_the_threshold_is_not_a_finding()
test_a_malformed_svg_errors_rather_than_fails()

print(f"\n{sum(results)}/{len(results)} passed")
_tmp.cleanup()
raise SystemExit(0 if all(results) else 1)
