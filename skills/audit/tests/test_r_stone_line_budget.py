"""R-stone-13 — a stone `line::` or control-file stone line that renders over
`stone_line_max` is a finding; links collapse to their alias before measuring;
the display regex restates stone's own and must stay byte-equal."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
STONE = HERE.parent.parent / "workflow" / "scripts" / "stone"


def _ap():
    spec = importlib.util.spec_from_file_location("audit_plan_slb", SCRIPTS / "audit-plan.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_plan_slb"] = mod
    spec.loader.exec_module(mod)
    return mod


def _stone():
    loader = importlib.machinery.SourceFileLoader("stone_slb", str(STONE))
    spec = importlib.util.spec_from_loader("stone_slb", loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["stone_slb"] = mod
    loader.exec_module(mod)
    return mod


def test_budget_from_config_and_regex_agrees_with_stone():
    ap, st = _ap(), _stone()
    assert ap.stone_line_max() == 84
    assert ap._STONE_LINK_DISPLAY_RE.pattern == st._LINK_DISPLAY_RE.pattern
    assert ap._stone_display("a [[X|b]] c [[Y]]") == st.display_text("a [[X|b]] c [[Y]]")


def test_stone_file_line_key_over_budget(tmp_path):
    ap = _ap()
    long = "security model — access doctrine + enclave + ingestion front door, drawn then audited — [[Atticus P0004|Security Model]]"
    p = tmp_path / "Atticus P0004.md"
    p.write_text(f"line:: {long}\ntempo:: waiting\n\nbody with a very long prose line " + "x" * 200 + "\n")
    verdict, detail = ap.chk_stone_line_budget(p, tmp_path, None)
    assert verdict == "fail" and "104" in detail and "line(s) 1" in detail
    short = tmp_path / "Atticus P0005.md"
    short.write_text("line:: short and sweet — [[Atticus P0005|Sweet]]\n\nbody\n")
    assert ap.chk_stone_line_budget(short, tmp_path, None)[0] == "pass"


def test_control_file_stone_line_and_prose_exempt(tmp_path):
    ap = _ap()
    p = tmp_path / "Atticus Pebbles.md"
    p.write_text("---\ndescription: x\n---\n\nLATER:\n"
                 "[[Atticus P0004|-]] " + "w" * 90 + "\n"
                 "[[Atticus P0005|-]] fits\n"
                 "a plain prose line that is very long " + "y" * 120 + "\n")
    verdict, detail = ap.chk_stone_line_budget(p, tmp_path, None)
    assert verdict == "fail" and "line(s) 6" in detail and "line(s) 6," not in detail


def test_registered():
    ap = _ap()
    assert ap.CHECKERS["stone_line_budget"] is ap.chk_stone_line_budget
