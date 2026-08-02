#!/usr/bin/env python3
"""T106 — what the geometry parser was failing to see.

T074 registered the four `svg_*` checkers; T106 was supposed to be the small
follow-on that declares the trait on a pilot anchor. Reading the findings against
the actual diagrams first — which is what the row gated on — showed the findings
were not trustworthy yet, for three reasons that all live in `parse_svg`:

1. **Stylesheets were never read.** A hand-authored diagram styles itself with
   `<defs><style>.sub{font-size:12.5px}</style>` and `<text class="sub">`, and the
   parser only ever looked at presentation attributes. Every label fell back to
   the 16px default, and a 12px label rendered 33% too wide is enough to push a
   node label under the 70% containment bar — so it stops being exempt and gets
   reported as spilling the box NEXT DOOR. Three of the four hard findings on the
   vault's authored diagrams were this, not a layout defect.
2. **The same blindness hid whole documents.** `.core{stroke:#1565c0}` is how a
   class-styled diagram strokes its boxes, and an unstroked `<rect>` is skipped —
   so `05-svg.svg` in the Viz Bench parsed to **1 box out of 15**, and the repair
   loop had nothing to collide and nothing to move. The tool was a silent no-op
   on that entire class of document.
3. **`markerUnits` was ignored.** `head_len` multiplied `markerWidth` by
   stroke-width unconditionally, which is the `strokeWidth` rule; under an
   explicit `userSpaceOnUse` a 12-unit head was reported as 42.

Each test below is the *shape* that misled, not the vault file it was found in —
the fixtures are self-contained so they keep meaning when the diagrams change.

    python3 test-t106-svg-parser-fidelity.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_ap_spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_ap_spec)
sys.modules["ap"] = ap
_ap_spec.loader.exec_module(ap)

_sj_path = ap.REPO_ROOT / "skills" / "viz" / "svg-jiggle.py"
_sj_spec = importlib.util.spec_from_file_location("sj", _sj_path)
sj = importlib.util.module_from_spec(_sj_spec)
sys.modules["sj"] = sj
_sj_spec.loader.exec_module(sj)

# Registration runs through the real corpus, so `run_checker` below resolves the
# `svg_*` names exactly as a live audit does — via R-svg-jiggle's `import::`.
_rulesets, _seen = [], set()
for _rs in ap.all_corpus_rulesets():
    if _rs["name"] not in _seen:
        _seen.add(_rs["name"])
        _rulesets.append(_rs)
ap.register_imports(_rulesets)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


print("A stylesheet is read like the presentation attributes it stands in for")


def test_class_font_size_is_resolved():
    """The defect that produced the false hard findings, in miniature.

    Two boxes side by side and one long label centred on the RIGHT one. At its
    declared 12px the label is 87% inside that box — its node label, exempt. At
    the 16px default it swells past the left box's edge, drops to 65% coverage,
    loses the exemption, and is reported as spilling a box it never touches."""
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 740">'
           '<defs><style>.feat{font-size:12px;}</style></defs>'
           '<rect x="90" y="142" width="630" height="80" stroke="#5b6b7a" fill="none"/>'
           '<rect x="760" y="142" width="350" height="80" stroke="#5b6b7a" fill="none"/>'
           f'<text class="feat" x="935" y="217" text-anchor="middle">{"x" * 58}</text>'
           '</svg>')
    m = sj.parse_svg(doc)
    check("the label carries its stylesheet size, not the 16px fallback",
          [l.fs for l in m.labels], [12.0])
    check("...so it reads as the right-hand box's node label",
          [l.is_node for l in m.labels], [True])
    check("...and nothing is reported as spilling the box next door",
          sj.detect_label_over_box(m), [])

    # Same document with the class stripped — the pre-fix reading, kept as the
    # control so this test fails loudly if the fallback ever silently returns.
    m16 = sj.parse_svg(doc.replace(' class="feat"', ''))
    check("with no size to read, the 16px fallback still fires the false finding",
          len(sj.detect_label_over_box(m16)), 1)


def test_a_class_stroked_rect_is_a_box():
    """Why a whole document could parse to almost no boxes: `.core{stroke:…}` is
    how a class-styled diagram strokes its entities, and an unstroked `<rect>` is
    skipped as the canvas background. No boxes means no collisions to detect and
    nothing for the repair loop to move — the tool reported a clean diagram
    because it could not see the diagram."""
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
           '<defs><style>.core{fill:#e3f2fd;stroke:#1565c0;}</style></defs>'
           '<rect class="core" x="20" y="20" width="120" height="60"/>'
           '<rect x="200" y="20" width="120" height="60" fill="#eee"/>'
           '</svg>')
    m = sj.parse_svg(doc)
    check("the class-stroked rect is a box", len(m.boxes), 1)
    check("...and the genuinely unstroked one is still not",
          [(b.x, b.y) for b in m.boxes], [(20.0, 20.0)])


def test_a_class_supplied_marker_is_seen():
    """`.arr{marker-end:url(#a)}` is the ordinary way to give every edge a head.
    Missing it meant `head_len()` returned 0 for the whole document, so
    `svg_overweighted_head` could not fire even on an arrow whose head was
    longer than the arrow."""
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
           '<defs><marker id="a" markerWidth="9" markerHeight="9">'
           '<path d="M0,0 L9,4 L0,8 z"/></marker>'
           '<style>.arr{stroke:#555;stroke-width:1.6;marker-end:url(#a);}</style></defs>'
           '<line class="arr" x1="100" y1="70" x2="130" y2="70"/>'
           '</svg>')
    m = sj.parse_svg(doc)
    check("the edge picks up its class's marker", m.edges[0].marker_id, "a")
    check("...and its class's stroke-width", m.edges[0].stroke_w, 1.6)
    check("...so an oversized head is now weighable at all",
          len(sj.detect_overweighted_head(m)), 1)


def test_the_cascade_order_is_css_then_attribute_then_inherited():
    """SVG puts a stylesheet rule above a presentation attribute (which carries
    specificity 0), and both above an inherited value. Getting this backwards
    would have swapped one wrong size for another."""
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" font-size="40">'
           '<defs><style>.s{font-size:11px;}</style></defs>'
           '<text class="s" x="10" y="50" font-size="22">css wins</text>'
           '<text x="10" y="90" font-size="22">attribute wins</text>'
           '<text x="10" y="130">inherited</text>'
           '</svg>')
    m = sj.parse_svg(doc)
    check("css > attribute > inherited", [l.fs for l in m.labels], [11.0, 22.0, 40.0])


def test_css_units_parse_and_relative_ones_decline():
    """`float("12.5px")` raises, and CSS is where units actually show up. A
    relative unit must return None so the caller's default applies rather than a
    number that means something else entirely."""
    check("a plain number", sj.fnum("12.5"), 12.5)
    check("an explicit px", sj.fnum("12.5px"), 12.5)
    check("a bare int", sj.fnum(15), 15.0)
    check("em declines rather than reading as 2 user units", sj.fnum("2em"), None)
    check("...and so does a percentage", sj.fnum("50%"), None)


print("\nAn arrowhead is measured in the units its marker declares")


def test_marker_units_decide_whether_stroke_width_scales_the_head():
    def doc(units, sw):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
                f'<defs><marker id="a" markerUnits="{units}" markerWidth="12" '
                'markerHeight="12"><path d="M0,0 L12,4 L0,8 z"/></marker></defs>'
                f'<line x1="100" y1="70" x2="300" y2="70" stroke="#333" '
                f'stroke-width="{sw}" marker-end="url(#a)"/></svg>')
    usr = sj.parse_svg(doc("userSpaceOnUse", 3.5)).edges[0]
    stw = sj.parse_svg(doc("strokeWidth", 3.5)).edges[0]
    check("a userSpaceOnUse head is markerWidth, full stop", usr.head_len(), 12.0)
    check("...not the 42 that multiplying by stroke-width produced",
          usr.head_len() != 42.0, True)
    check("a strokeWidth head does scale with the line", stw.head_len(), 42.0)

    default = sj.parse_svg(doc("userSpaceOnUse", 3.5).replace(
        'markerUnits="userSpaceOnUse" ', '')).edges[0]
    check("...and strokeWidth is what an absent markerUnits means",
          default.head_len(), 42.0)


def test_the_repair_aims_in_the_same_units_it_measures():
    """`shrink_arrowhead` solves for a `markerWidth` that lands `head_len()` on
    the 20% target. If it divides by stroke-width while `head_len()` no longer
    multiplies by it, the repair overshoots by that factor and the issue it was
    called on survives — the loop then cannot retire it."""
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
           '<defs><marker id="a" markerUnits="userSpaceOnUse" markerWidth="40" '
           'markerHeight="8"><path d="M0,0 L40,4 L0,8 z"/></marker></defs>'
           '<line x1="100" y1="70" x2="200" y2="70" stroke="#333" '
           'stroke-width="4" marker-end="url(#a)"/></svg>')
    m = sj.parse_svg(doc)
    check("the head starts over the 20% bar", len(sj.detect_overweighted_head(m)), 1)
    e = m.edges[0]
    e.marker_scale = sj.HEAD_FRAC * e.length() / max(e.head_unit, 0.01)
    check("...and the markerWidth the repair solves for lands ON the target",
          round(e.head_len(), 6), round(sj.HEAD_FRAC * e.length(), 6))
    check("...which the detector then reads as clean",
          sj.detect_overweighted_head(m), [])


print("\nAn exported diagram is not this ruleset's to repair")

_tmp = tempfile.TemporaryDirectory()
_root = Path(_tmp.name)

# A label straddling a box's left edge — a genuine finding, so the only thing
# that can silence it below is the exemption itself.
_BAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400">'
        '<defs><marker id="a" markerWidth="8" markerHeight="8">'
        '<path d="M0,0 L8,4 L0,8 z"/></marker></defs>'
        '<rect x="20" y="40" width="120" height="60" fill="none" stroke="#333"/>'
        '<rect x="400" y="40" width="120" height="60" fill="none" stroke="#333"/>'
        '<text x="80" y="75" text-anchor="middle" font-size="12">alpha</text>'
        '<text x="460" y="75" text-anchor="middle" font-size="12">beta</text>'
        '<line x1="140" y1="70" x2="400" y2="70" stroke="#333" marker-end="url(#a)"/>'
        '<text x="400" y="55" text-anchor="middle" font-size="11">sends</text>'
        '</svg>')


def test_a_generated_svg_is_exempt_from_the_audit():
    """R-svg-jiggle owns the SVG track — the case where the agent controls every
    coordinate, so a resolution rewrites geometry in place. On an export that
    premise fails in both directions: the repair dies at the next export, and for
    `.d2` the ruleset says outright that those moves belong to the deferred D2
    Jiggle as ELK directives. A finding here would be true and unactionable, and
    88% of the vault's SVGs are exports — so left unscoped this rule was mostly
    reporting other tools' layout decisions."""
    authored = _root / "authored.svg"
    authored.write_text(_BAD, encoding="utf-8")
    check("an authored diagram is audited",
          ap.run_checker("svg_label_over_box", authored, _root)[0], "fail")

    exported = _root / "exported.svg"
    exported.write_text(_BAD, encoding="utf-8")
    (_root / "exported.d2").write_text("a -> b", encoding="utf-8")
    st, det = ap.run_checker("svg_label_over_box", exported, _root)
    check("...the same bytes beside a .d2 source are not", st, "pass")
    check("...and the verdict says which source owns the layout",
          "exported.d2" in det, True)

    # A signature in the file's own bytes is proof; a sibling filename is only
    # the vault's convention, and Viz Bench holds files where the convention
    # lies. The reason string has to distinguish them or a reader cannot tell
    # which files rest on the weaker evidence.
    stamped = _root / "stamped.svg"
    stamped.write_text(_BAD.replace('<svg ', '<svg data-d2-version="0.7.1" ', 1),
                       encoding="utf-8")
    st2, det2 = ap.run_checker("svg_label_over_box", stamped, _root)
    check("a generator's own stamp exempts it with no sibling at all", st2, "pass")
    check("...and is reported as proof, not as the convention",
          det2.startswith("generated by d2"), True)


def test_a_dotted_basename_finds_its_own_source():
    """`with_suffix` on `Foo.bar.svg` asks for `Foo.d2`, which is a different
    figure — and would exempt or fail the wrong file."""
    f = _root / "Diagram.v2.svg"
    f.write_text(_BAD, encoding="utf-8")
    (_root / "Diagram.d2").write_text("decoy", encoding="utf-8")
    check("a same-stem-prefix decoy does not exempt it",
          ap.run_checker("svg_label_over_box", f, _root)[0], "fail")
    (_root / "Diagram.v2.d2").write_text("a -> b", encoding="utf-8")
    check("...its actual source does",
          ap.run_checker("svg_label_over_box", f, _root)[0], "pass")


def test_the_exemption_is_the_audit_adapter_not_the_detector():
    """Pointing `svg-jiggle.py --issues` at an export is a deliberate act and
    must still answer. What the exemption governs is the *audit*, which fires
    unbidden across a whole anchor — so it lives in the adapter, and the geometry
    layer stays willing to analyse anything it is handed."""
    m = sj.parse_svg(_BAD)
    check("the detector reports on the same bytes an audit exempts",
          len(sj.detect_label_over_box(m)), 1)
    check("...and the exemption is a property of the file's neighbours",
          sj.generator_source(_root / "exported.svg"), "exported from exported.d2")
    check("...which an authored file simply does not have",
          sj.generator_source(_root / "authored.svg"), None)


test_class_font_size_is_resolved()
test_a_class_stroked_rect_is_a_box()
test_a_class_supplied_marker_is_seen()
test_the_cascade_order_is_css_then_attribute_then_inherited()
test_css_units_parse_and_relative_ones_decline()
test_marker_units_decide_whether_stroke_width_scales_the_head()
test_the_repair_aims_in_the_same_units_it_measures()
test_a_generated_svg_is_exempt_from_the_audit()
test_a_dotted_basename_finds_its_own_source()
test_the_exemption_is_the_audit_adapter_not_the_detector()

print(f"\n{sum(results)}/{len(results)} passed")
_tmp.cleanup()
raise SystemExit(0 if all(results) else 1)
