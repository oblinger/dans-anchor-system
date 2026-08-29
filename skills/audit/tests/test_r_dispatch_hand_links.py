"""R-dispatch-table-16 — a hand-row link that resolves nowhere is reported;
links below the electric marker are never judged; a same-page `[[#…]]` link and
a link to a file elsewhere in the vault both pass."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"


def _ap():
    spec = importlib.util.spec_from_file_location("audit_plan_t615", SCRIPTS / "audit-plan.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_plan_t615"] = mod
    spec.loader.exec_module(mod)
    return mod


def _anchor(tmp: Path) -> Path:
    a = tmp / "HX"
    a.mkdir()
    (a / ".anchor").write_text("slug: HX\n", encoding="utf-8")
    (a / "HX Real.md").write_text("# HX Real\nexists.\n", encoding="utf-8")
    (a / "HX Help.txt").write_text("help\n", encoding="utf-8")
    return a


def _page(a: Path, rows: str) -> Path:
    p = a / "HX.md"
    p.write_text(
        "---\ndescription: x\n---\n\n"
        "| -[[HX]]- | : x<br>→ [[kmr]] → [HX](hook://p/HX)  |\n"
        "| --- | --- |\n" + rows +
        "| ... | [[HX Ghost Below]],  |\n\n# HX\nThe page.\n", encoding="utf-8")
    return p


def test_dead_hand_link_warns_and_electric_zone_is_ignored(tmp_path):
    ap = _ap()
    a = _anchor(tmp_path)
    p = _page(a, "| [[HX Real\\|Real]]+ | [[HX Ghost]],  [[HX Help.txt\\|help]],  [[#Body]],  |\n")
    status, detail = ap.chk_dispatch_hand_link_resolves(p, a, [])
    assert status == "warn", detail
    assert "[[HX Ghost]]" in detail and "Ghost Below" not in detail, detail
    assert "HX Real" not in detail and "Help.txt" not in detail, detail


def test_clean_masthead_passes(tmp_path):
    ap = _ap()
    a = _anchor(tmp_path)
    p = _page(a, "| [[HX Real\\|Real]] | [[HX Help.txt]],  [[DAS Dispatch Table]],  |\n")
    status, detail = ap.chk_dispatch_hand_link_resolves(p, a, [])
    assert status == "pass", detail


def test_bare_marker_row_stops_the_walk(tmp_path):
    ap = _ap()
    a = _anchor(tmp_path)
    p = a / "HX.md"
    p.write_text(
        "| -[[HX]]- | : x<br>→ [[kmr]] → [HX](hook://p/HX)  |\n"
        "| --- | --- |\n"
        "| --- | |\n"
        "| [[HX Nope]] | machine row |\n\n# HX\nThe page.\n", encoding="utf-8")
    status, detail = ap.chk_dispatch_hand_link_resolves(p, a, [])
    assert status == "pass", detail
